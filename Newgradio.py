import gradio as gr
import json
import os
import uuid
import tempfile
import base64
import requests
from PIL import Image
import fitz  # PyMuPDF
import io
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiPDFProcessor:
    def __init__(self):
        """Initialize with API key."""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"
        self.verify_api_key()
        
    def verify_api_key(self):
        """Verify that API key is available."""
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY environment variable not set.")
            self.api_available = False
        else:
            self.api_available = True
    
    def call_gemini_api(self, prompt, image=None):
        """
        Call Gemini API using requests.post
        
        Args:
            prompt: Text prompt for Gemini
            image: Optional PIL Image to include
            
        Returns:
            Response text or None if error
        """
        if not self.api_available:
            return None
            
        try:
            # Prepare request URL with API key
            url = f"{self.api_url}?key={self.api_key}"
            
            # Prepare content parts list
            parts = [{"text": prompt}]
            
            # Add image if provided
            if image:
                # Convert PIL image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # Convert to base64
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                # Add image part
                parts.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": img_b64
                    }
                })
            
            # Prepare request body
            request_body = {
                "contents": [{
                    "parts": parts
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "topK": 32,
                    "topP": 0.95,
                    "maxOutputTokens": 8192,
                }
            }
            
            # Make POST request
            response = requests.post(
                url, 
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
            
            # Handle response
            if response.status_code == 200:
                response_json = response.json()
                
                # Extract text from response
                try:
                    text = response_json["candidates"][0]["content"]["parts"][0]["text"]
                    return text
                except (KeyError, IndexError) as e:
                    print(f"Error parsing Gemini response: {str(e)}")
                    return None
            else:
                print(f"Gemini API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            return None
    
    def extract_pdf_pages(self, pdf_path):
        """Extract pages from PDF as both text and images."""
        result = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get text
                text = page.get_text()
                
                # Render page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better resolution
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                
                result.append({
                    "page_num": page_num + 1,
                    "text": text,
                    "image": img
                })
                
            return result
        except Exception as e:
            print(f"Error extracting PDF pages: {str(e)}")
            return []
    
    def process_page_with_gemini(self, page_info):
        """Process a page with Gemini for enhanced text extraction."""
        try:
            # Skip if API not available
            if not self.api_available:
                return {
                    "page": page_info["page_num"],
                    "extracted_text": page_info["text"],
                    "success": False,
                    "error": "Gemini API not configured"
                }
            
            # Prepare prompt
            prompt = """
            Extract ALL text content from this PDF page image, including any text in 
            tables, charts, headers, footers, and image captions. 
            Format your response as plain text. Include all content exactly as it appears.
            Do not summarize or explain the content. Just extract the raw text.
            """
            
            # Send to Gemini using our requests-based method
            response_text = self.call_gemini_api(prompt, page_info["image"])
            
            if not response_text:
                return {
                    "page": page_info["page_num"],
                    "extracted_text": page_info["text"],  # Fallback to original text
                    "success": False,
                    "error": "No response from Gemini API"
                }
            
            # Return structured response
            return {
                "page": page_info["page_num"],
                "extracted_text": response_text.strip(),
                "original_text": page_info["text"],
                "success": True
            }
        except Exception as e:
            return {
                "page": page_info["page_num"],
                "extracted_text": page_info["text"],  # Fallback to original text
                "success": False,
                "error": str(e)
            }
    
    def create_chunks_with_gemini(self, page_results, filename):
        """Use Gemini to create chunks from extracted text."""
        try:
            # Skip if API not available
            if not self.api_available:
                return self.create_chunks_locally(page_results, filename)
            
            # Combine all pages into one document
            full_text = "\n\n".join([f"PAGE {pr['page']}:\n{pr['extracted_text']}" 
                                     for pr in page_results])
            
            # Prepare chunking prompt
            prompt = f"""
            I have a PDF document with the following text content. Please divide it 
            into logical chunks for processing. Each chunk should be about 500 characters
            and should try to maintain logical boundaries (like paragraphs or sections).

            For each chunk, determine if it's related to banking or financial services.
            
            Format your response as a JSONL string where each line is a JSON object with:
            - "rawContent": The chunk of text
            - "enhancedContent": "I work in Wells Fargo. ABC is a Bank providing financial services."
            - "presentationContext": "I work in Wells Fargo. ABC is a Bank providing financial services."
            - "metadata": An object with "chunkId", "pageNumber", and "fileUrl"
            - "groupNames": An object with a "banking" boolean property
            
            Example format:
            {{"rawContent": "Text content here", "enhancedContent": "I work in Wells Fargo. ABC is a Bank providing financial services.", "presentationContext": "I work in Wells Fargo. ABC is a Bank providing financial services.", "metadata": {{"chunkId": 1, "pageNumber": 1, "fileUrl": "///document.pdf"}}, "groupNames": {{"banking": true}}}}
            
            Here's the document text:
            {full_text[:10000]}  # Limiting to 10K characters to avoid token limits
            """
            
            # Send to Gemini
            response_text = self.call_gemini_api(prompt)
            
            if not response_text:
                return self.create_chunks_locally(page_results, filename)
            
            # Parse response (expected to be JSONL)
            jsonl_text = response_text.strip()
            
            # Process the response
            chunks = []
            chunk_id = 1
            
            for line in jsonl_text.split('\n'):
                line = line.strip()
                if not line or line.startswith('```') or line.startswith('#'):
                    continue
                    
                try:
                    # Clean the line if needed (removing markdown artifacts)
                    if line.endswith('```') or line.endswith('`'):
                        line = line.rstrip('`')
                        
                    chunk = json.loads(line)
                    
                    # Ensure required fields
                    if "metadata" not in chunk:
                        chunk["metadata"] = {}
                    
                    # Set or override metadata
                    chunk["metadata"]["chunkId"] = chunk_id
                    chunk["metadata"]["fileUrl"] = f"///{filename}"
                    
                    # Ensure groupNames
                    if "groupNames" not in chunk:
                        chunk["groupNames"] = {"banking": False}
                        
                    chunks.append(chunk)
                    chunk_id += 1
                except json.JSONDecodeError:
                    # If Gemini didn't return proper JSON, try to extract content
                    # This is a fallback for when the model doesn't follow the format exactly
                    if len(line) > 20:  # Only process substantial lines
                        chunks.append({
                            "rawContent": line,
                            "enhancedContent": "I work in Wells Fargo. ABC is a Bank providing financial services.",
                            "presentationContext": "I work in Wells Fargo. ABC is a Bank providing financial services.",
                            "metadata": {
                                "chunkId": chunk_id,
                                "pageNumber": 1,  # Default
                                "fileUrl": f"///{filename}"
                            },
                            "groupNames": {
                                "banking": "bank" in line.lower() or "financial" in line.lower()
                            }
                        })
                        chunk_id += 1
            
            # If Gemini failed to produce valid chunks, fall back to local chunking
            if not chunks:
                return self.create_chunks_locally(page_results, filename)
                
            return chunks
            
        except Exception as e:
            print(f"Error creating chunks with Gemini: {str(e)}")
            # Fall back to local chunking
            return self.create_chunks_locally(page_results, filename)
    
    def create_chunks_locally(self, page_results, filename, chunk_size=500, overlap=100):
        """Create chunks locally as a fallback."""
        chunks = []
        chunk_id = 1
        
        for page_info in page_results:
            page_num = page_info["page"]
            text = page_info["extracted_text"]
            
            # Skip empty text
            if not text.strip():
                continue
                
            # Simple chunking by characters
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                
                # Try to end at a sentence or paragraph
                for marker in ['. ', '? ', '! ', '\n']:
                    pos = text.rfind(marker, start, end)
                    if pos > start + 100:  # At least 100 chars in the chunk
                        end = pos + 2  # Include the marker
                        break
                
                # If no good break point, try a space
                if end == start + chunk_size and end < len(text):
                    space_pos = text.rfind(' ', start, end)
                    if space_pos > start:
                        end = space_pos + 1
                
                chunk_text = text[start:end].strip()
                
                # Skip empty chunks
                if not chunk_text:
                    start = end
                    continue
                
                # Create chunk in required format
                is_banking = any(term in chunk_text.lower() 
                                for term in ['bank', 'financial', 'credit', 'loan', 'mortgage'])
                
                chunks.append({
                    "rawContent": chunk_text,
                    "enhancedContent": "I work in Wells Fargo. ABC is a Bank providing financial services.",
                    "presentationContext": "I work in Wells Fargo. ABC is a Bank providing financial services.",
                    "metadata": {
                        "chunkId": chunk_id,
                        "pageNumber": page_num,
                        "fileUrl": f"///{filename}"
                    },
                    "groupNames": {
                        "banking": is_banking
                    }
                })
                
                chunk_id += 1
                start = end - overlap if end < len(text) else len(text)
        
        # If still no chunks, create a dummy chunk
        if not chunks:
            chunks = [{
                "rawContent": "No text content could be extracted from this document.",
                "enhancedContent": "I work in Wells Fargo. ABC is a Bank providing financial services.",
                "presentationContext": "I work in Wells Fargo. ABC is a Bank providing financial services.",
                "metadata": {
                    "chunkId": 1,
                    "pageNumber": 1,
                    "fileUrl": f"///{filename}"
                },
                "groupNames": {
                    "banking": False
                }
            }]
            
        return chunks
    
    def process_pdf(self, pdf_file):
        """Main function to process PDF with Gemini."""
        try:
            output_dir = tempfile.mkdtemp()
            status_messages = []
            
            # Handle file input
            if pdf_file is None:
                return None, None, "No file uploaded. Please upload a PDF file."
                
            # Save to temp file if needed
            if not isinstance(pdf_file, str):
                if hasattr(pdf_file, 'name'):
                    filename = os.path.basename(pdf_file.name)
                    temp_path = pdf_file.name
                else:
                    # Create a temporary file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    temp_path = temp_file.name
                    filename = "uploaded_document.pdf"
                    
                    # Write content to the temporary file
                    if hasattr(pdf_file, 'read'):
                        content = pdf_file.read()
                        with open(temp_path, 'wb') as f:
                            if isinstance(content, str):
                                f.write(content.encode('utf-8'))
                            else:
                                f.write(content)
                    else:
                        return None, None, f"Unsupported file type: {type(pdf_file)}"
            else:
                # It's already a path
                temp_path = pdf_file
                filename = os.path.basename(pdf_file)
            
            status_messages.append(f"File '{filename}' uploaded successfully.")
            
            # Extract PDF pages
            status_messages.append("Extracting PDF pages...")
            pdf_pages = self.extract_pdf_pages(temp_path)
            
            if not pdf_pages:
                return None, None, "Failed to extract pages from the PDF."
                
            status_messages.append(f"Extracted {len(pdf_pages)} pages.")
            
            # Process each page with Gemini
            status_messages.append("Processing pages with Gemini API...")
            processed_pages = []
            
            for page_info in pdf_pages:
                result = self.process_page_with_gemini(page_info)
                processed_pages.append(result)
                status_messages.append(f"Processed page {result['page']}" + 
                                      (" successfully" if result['success'] else " with fallback"))
            
            # Create chunks
            status_messages.append("Creating chunks...")
            chunks = self.create_chunks_with_gemini(processed_pages, filename)
            
            status_messages.append(f"Created {len(chunks)} chunks.")
            
            # Generate JSONL output
            output_filename = f"document_chunks_{uuid.uuid4().hex[:8]}.jsonl"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w') as f:
                for chunk in chunks:
                    f.write(json.dumps(chunk) + '\n')
                    
            status_messages.append(f"Created JSONL file: {output_filename}")
            
            # Create preview dataframe
            preview_data = []
            for chunk in chunks[:min(10, len(chunks))]:
                preview_text = chunk["rawContent"]
                if len(preview_text) > 100:
                    preview_text = preview_text[:100] + "..."
                    
                preview_data.append({
                    "chunkId": chunk["metadata"]["chunkId"],
                    "pageNumber": chunk["metadata"].get("pageNumber", 1),
                    "rawContent": preview_text,
                    "banking": chunk["groupNames"].get("banking", False)
                })
                
            preview_df = pd.DataFrame(preview_data)
            
            # Clean up
            if hasattr(pdf_file, 'name') and os.path.exists(temp_path) and temp_path != pdf_file:
                os.unlink(temp_path)
                
            return output_path, preview_df, "\n".join(status_messages)
            
        except Exception as e:
            import traceback
            return None, None, f"Error processing PDF: {str(e)}\n{traceback.format_exc()}"

# Create Gradio interface
def create_interface():
    processor = GeminiPDFProcessor()
    
    with gr.Blocks(title="PDF to JSONL with Gemini") as app:
        gr.Markdown("# PDF to JSONL Chunker with Google Gemini API")
        gr.Markdown("""
        This application processes PDF documents using Google's Gemini API via direct HTTP requests 
        to extract text from both text-based PDFs and image-based PDFs, then generates a JSONL file 
        with chunked content.
        
        **Note**: You need to set the `GOOGLE_API_KEY` environment variable with your 
        Google API key that has access to the Gemini API.
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
                process_button = gr.Button("Process PDF", variant="primary")
            
            with gr.Column(scale=2):
                output_file = gr.File(label="Generated JSONL")
                preview = gr.DataFrame(label="Preview (First 10 chunks)")
                status = gr.Textbox(label="Status", lines
