import fitz  # Import PyMuPDF
from PIL import Image
import pytesseract
import re

def extract_text_data(page):
    """Extract text and its bounding boxes from a page using OCR and include font information."""
    text_data = []
    # Use PyMuPDF to extract text with font styles
    for text_instance in page.get_text("dict")["blocks"]:
        for line in text_instance.get("lines", []):
            for span in line.get("spans", []):
                text = span['text'].strip()
                if text:  # Ensure text is not empty
                    x, y, w, h = span['bbox']
                    font_name = span['font']  # Extract the font name
                    font_size = span['size']  # Extract the font size
                    bold = 'Bold' in font_name  # Determine if the font is bold
                    italic = 'Italic' in font_name  # Determine if the font is italic
                    text_data.append((text, x, y, w, h, font_name, font_size, bold, italic))
    return text_data

def annotate_pdf(document, anomalies, page_number):
    """Draw rectangles around detected changes in the PDF."""
    page = document[page_number]
    for text, x, y, w, h, font_name, font_size, bold, italic in anomalies:
        rect = fitz.Rect(x, y, x + w, y + h)
        page.draw_rect(rect, color=(0, 0, 1), width=1.5)  # Draw a blue rectangle
        # Optionally add a note or print text font information
        note = f"{font_name}, {font_size:.2f}pt, {'bold' if bold else ''}{'italic' if italic else ''}"
        page.insert_text((x, y), note, fontsize=8, color=(1, 0, 0))

# Load the PDF document
pdf_path = "INV-AP-B1-65583719-109634302829-JULY-2022.pdf"
pdf_document = fitz.open(pdf_path)

# Define regex patterns for billing amounts and customer details
expected_patterns = {
    'customer_details': r"[A-Z][a-z]+ [A-Z][a-z]+",
    'billing_amounts': r"\d+\.\d{2}"
}

# Process each page
for page_number, page in enumerate(pdf_document):
    text_data = extract_text_data(page)
    # You may want to modify how anomalies are detected if using font information
    anomalies = text_data  # Placeholder, adjust based on your anomaly detection logic
    if anomalies:
        annotate_pdf(pdf_document, anomalies, page_number)

# Save the annotated PDF
output_pdf_path = pdf_path.replace('.pdf', '_annotated.pdf')
pdf_document.save(output_pdf_path)
pdf_document.close()

print(f"Annotated PDF saved as: {output_pdf_path}")
