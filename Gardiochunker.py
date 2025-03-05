import gradio as gr
import json
import os
import uuid
import time
import tempfile
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import utility functions
from utils import save_images_from_document, enhance_content, determine_presentation_context, determine_groups

class PDFProcessor:
    def __init__(self):
        """Initialize the PDF processor with Google Document AI configuration."""
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("DOCUMENT_AI_LOCATION", "us")
        self.processor_id = os.getenv("DOCUMENT_AI_PROCESSOR_ID")
        
        if not all([self.project_id, self.processor_id]):
            print("Warning: Missing required environment variables. Set GOOGLE_CLOUD_PROJECT and DOCUMENT_AI_PROCESSOR_ID.")
        
        self.client = None
        self.processor_name = None
        self.output_dir = tempfile.mkdtemp()
        
    def initialize_document_ai(self):
        """Initialize Document AI client."""
        try:
            opts = ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
            self.client = documentai.DocumentProcessorServiceClient(client_options=opts)
            self.processor_name = self.client.processor_path(
                self.project_id, self.location, self.processor_id
            )
            return True
        except Exception as e:
            print(f"Error initializing Document AI: {str(e)}")
            return False
    
    def process_document(self, file_content, mime_type="application/pdf"):
        """Process the document using Document AI."""
        try:
            # Create the document object
            document = {"content": file_content, "mime_type": mime_type}
            
            # Configure the process request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                document=document,
                # Enable image extraction
                process_options=documentai.ProcessOptions(
                    individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
                        pages=[]  # Empty list means all pages
                    ),
                    ocr_config=documentai.ProcessOptions.OcrConfig(
                        enable_image_quality_scores=True,
                        enable_symbol=True
                    )
                )
            )
            
            result = self.client.process_document(request=request)
            return result.document
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return None
    
    def extract_text_and_images(self, document):
        """Extract text and image data from Document AI response."""
        try:
            text = document.text
            pages = document.pages
            
            # Extract text by page
            page_texts = []
            for page in pages:
                page_number = page.page_number + 1  # 1-based page numbers
                page_text = ""
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for line in paragraph.lines:
                            line_text = ""
                            for token in line.tokens:
                                line_text += token.text + " "
                            page_text += line_text.strip() + "\n"
                page_texts.append({
                    "page": page_number, 
                    "text": page_text.strip()
                })
            
            # Extract images
            images = []
            for entity in document.entities:
                if hasattr(entity, 'type_') and entity.type_ == "image":
                    images.append({
                        "page": entity.page_anchor.page_refs[0].page + 1,  # 1-based
                        "confidence": entity.confidence,
                        "image_data": entity.normalized_value.text  # Base64 encoded
                    })
            
            return text, page_texts, images
        except Exception as e:
            print(f"Error extracting text and images: {str(e)}")
            return "", [], []
    
    def chunk_document(self, page_texts, chunk_size=500, overlap=100, filename=""):
        """Chunk document text with overlap, maintaining page boundaries."""
        try:
            chunks = []
            chunk_id = 1
            
            for page_info in page_texts:
                page_number = page_info["page"]
                text = page_info["text"]
                text_length = len(text)
                
                start = 0
                while start < text_length:
                    end = min(start + chunk_size, text_length)
                    if end < text_length and end - start == chunk_size:
                        # Find the last sentence end or space to avoid cutting words
                        sentence_end = max(
                            text.rfind('. ', start, end),
                            text.rfind('? ', start, end),
                            text.rfind('! ', start, end),
                            text.rfind('\n', start, end)
                        )
                        
                        if sentence_end != -1 and sentence_end > start + 50:  # At least 50 chars
                            end = sentence_end + 1
                        else:
                            # Fallback to last space
                            last_space = text.rfind(' ', start, end)
                            if last_space != -1 and last_space > start:
                                end = last_space
                    
                    raw_content = text[start:end].strip()
                    
                    # Skip empty chunks
                    if not raw_content:
                        start = end
                        continue
                    
                    # Create enhanced content and presentation context
                    enhanced = enhance_content(raw_content)
                    context = determine_presentation_context(raw_content)
                    groups = determine_groups(raw_content)
                    
                    chunks.append({
                        "rawContent": raw_content,
                        "enhancedContent": enhanced,
                        "presentationContext": context,
                        "metadata": {
                            "chunkId": chunk_id,
                            "pageNumber": page_number,
                            "fileUrl": f"///GENAI0014_DIV_RAG.pdf" if not filename else f"///{filename}"
                        },
                        "groupNames": groups
                    })
                    
                    chunk_id += 1
                    # Move start position accounting for overlap
                    start = end - overlap if end < text_length else text_length
            
            return chunks
        except Exception as e:
            print(f"Error chunking document: {str(e)}")
            return []
    
    def process_pdf(self, pdf_file):
        """Main function to process uploaded PDF and generate JSONL."""
        try:
            start_time = time.time()
            status_messages = []
            
            # Handle different types of input (file object, file path, etc.)
            if isinstance(pdf_file, str):
                # pdf_file is a file path
                filename = os.path.basename(pdf_file)
                with open(pdf_file, 'rb') as f:
                    file_content = f.read()
            elif hasattr(pdf_file, 'read') and callable(pdf_file.read):
                # pdf_file is a file-like object
                filename = os.path.basename(pdf_file.name) if hasattr(pdf_file, 'name') else "uploaded_document.pdf"
                file_content = pdf_file.read()
            elif hasattr(pdf_file, 'name') and isinstance(pdf_file.name, str):
                # Gradio sometimes passes a NamedTemporaryFile or similar object
                filename = os.path.basename(pdf_file.name)
                with open(pdf_file.name, 'rb') as f:
                    file_content = f.read()
            else:
                return None, None, f"Error: Invalid file input type: {type(pdf_file)}"
                
            status_messages.append(f"File '{filename}' uploaded successfully.")
            
            # Initialize Document AI if not already done
            if not self.client:
                if not self.initialize_document_ai():
                    return None, None, "Failed to initialize Document AI. Check your credentials."
                status_messages.append("Document AI initialized.")
            
            # Process document
            status_messages.append("Processing document with Google Document AI...")
            document = self.process_document(file_content)
            if not document:
                return None, None, "Document processing failed. Check logs for details."
            
            processing_time = time.time() - start_time
            status_messages.append(f"Document processed in {processing_time:.2f} seconds.")
            
            # Extract text and images
            status_messages.append("Extracting text and images...")
            full_text, page_texts, images = self.extract_text_and_images(document)
            
            # Save images if any were found
            if images:
                image_paths = save_images_from_document(images, self.output_dir)
                status_messages.append(f"Extracted {len(images)} images.")
            else:
                status_messages.append("No images found in the document.")
            
            # Chunk the document
            status_messages.append("Chunking document...")
            chunks = self.chunk_document(page_texts, filename=filename)
            
            if not chunks:
                return None, None, "Document chunking failed or produced no chunks."
            
            status_messages.append(f"Generated {len(chunks)} chunks.")
            
            # Generate a unique filename for the JSONL output
            output_filename = f"document_chunks_{uuid.uuid4().hex[:8]}.jsonl"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Write chunks to JSONL file
            with open(output_path, 'w') as f:
                for chunk in chunks:
                    f.write(json.dumps(chunk) + '\n')
            
            status_messages.append(f"JSONL file created: {output_filename}")
            
            # Create a preview dataframe
            preview_data = []
            for chunk in chunks[:10]:  # Show first 10 chunks
                preview_text = chunk["rawContent"]
                if len(preview_text) > 100:
                    preview_text = preview_text[:100] + "..."
                
                preview_data.append({
                    "chunkId": chunk["metadata"]["chunkId"],
                    "pageNumber": chunk["metadata"]["pageNumber"],
                    "rawContent": preview_text,
                    "groupNames": ", ".join([k for k, v in chunk["groupNames"].items() if v])
                })
            
            preview_df = pd.DataFrame(preview_data)
            
            total_time = time.time() - start_time
            status_messages.append(f"Total processing time: {total_time:.2f} seconds.")
            
            return output_path, preview_df, "\n".join(status_messages)
        
        except Exception as e:
            return None, None, f"Error processing PDF: {str(e)}"

# Create Gradio interface
def create_interface():
    processor = PDFProcessor()
    
    with gr.Blocks(title="PDF to JSONL Chunker") as app:
        gr.Markdown("# PDF to JSONL Chunker with Google Document AI")
        gr.Markdown("""
        This application processes PDF documents with Google Document AI and generates a 
        JSONL file with chunked content formatted similar to the example in the image.
        
        ## Features:
        - PDF text extraction with OCR
        - Image extraction
        - Text chunking with configurable size and overlap
        - Content enhancement and categorization
        - JSONL output with metadata
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
                
                with gr.Row():
                    chunk_size = gr.Slider(minimum=100, maximum=1000, value=500, step=50, 
                                          label="Chunk Size (characters)")
                    overlap = gr.Slider(minimum=0, maximum=200, value=100, step=10, 
                                       label="Chunk Overlap (characters)")
                
                process_button = gr.Button("Process PDF", variant="primary")
            
            with gr.Column(scale=2):
                output_file = gr.File(label="Generated JSONL")
                preview = gr.DataFrame(label="Preview (First 10 chunks)")
                status = gr.Textbox(label="Status", lines=10)
        
        def process_wrapper(pdf_file, chunk_size_val, overlap_val):
            # Update processor's chunk parameters
            processor.chunk_size = chunk_size_val
            processor.overlap = overlap_val
            return processor.process_pdf(pdf_file)
        
        process_button.click(
            process_wrapper,
            inputs=[pdf_input, chunk_size, overlap],
            outputs=[output_file, preview, status]
        )
        
        gr.Markdown("""
        ## How to Use:
        1. Upload your PDF file
        2. Adjust chunk size and overlap if needed
        3. Click "Process PDF"
        4. Download the generated JSONL file
        
        **Note:** This application requires Google Cloud credentials with access to Document AI.
        """)
    
    return app

# For local development
if __name__ == "__main__":
    app = create_interface()
    app.launch()
else:
    # For deployment
    app = create_interface()
