import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import re

# Load the PDF
pdf_path = "/path/to/your/document.pdf"
pdf_document = fitz.open(pdf_path)

# Define regex patterns for detecting specific fields
patterns = {
    'amounts': r'(₹\s?\d{1,3}(,\d{3})*(\.\d+)?|Rs\.?\s?\d{1,3}(,\d{3})*(\.\d+)?|\d{1,3}(,\d{3})*(\.\d+)?\s?(Rs|INR))',  # Regex for Indian Rupee amounts
    'names': r'[A-Z][a-z]+ [A-Z][a-z]+',  # Simplistic pattern for names
    'addresses': r'\d+ [\w\s]+ Street',  # Adjusted pattern for Indian addresses
}

# Function to extract text using OCR, find ROIs based on patterns, and mark them
def process_page(page):
    pixmap = page.get_pixmap()
    image_pil = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
    text = pytesseract.image_to_string(image_pil)
    data = pytesseract.image_to_data(image_pil, output_type=pytesseract.Output.DICT)
    for pattern_key, pattern in patterns.items():
        for i, text in enumerate(data['text']):
            if re.match(pattern, text):
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                rect = fitz.Rect(x, y, x + w, y + h)
                # Draw a blue rectangle around the matched text
                page.draw_rect(rect, color=(0, 0, 1), width=1.5, overlay=True)  # Color set to blue

# Process each page
for page_number, page in enumerate(pdf_document):
    process_page(page)
    print(f"Processed page {page_number + 1}")

# Save the annotated PDF
output_pdf_path = pdf_path.replace('.pdf', '_annotated.pdf')
pdf_document.save(output_pdf_path)
pdf_document.close()

print(f"Annotated PDF saved as: {output_pdf_path}")
