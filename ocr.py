import fitz  # Import PyMuPDF
from PIL import Image
import pytesseract
import re

def extract_text_data(page):
    """Extract text and its bounding boxes from a page using OCR."""
    text_data = []
    image = page.get_pixmap()
    open_cv_image = Image.frombytes("RGB", [image.width, image.height], image.samples)
    ocr_data = pytesseract.image_to_data(open_cv_image, output_type=pytesseract.Output.DICT)
    num_items = len(ocr_data['text'])
    for i in range(num_items):
        if ocr_data['text'][i].strip():  # Ensure text is not empty
            x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
            text_data.append((ocr_data['text'][i], x, y, w, h))
    return text_data

def detect_changes(text_data, expected_patterns):
    """Detect deviations from expected patterns in text data."""
    anomalies = []
    for text, x, y, w, h in text_data:
        for key, pattern in expected_patterns.items():
            if re.match(pattern, text):
                anomalies.append((text, x, y, w, h))
    return anomalies

def annotate_pdf(document, anomalies, page_number):
    """Draw rectangles around detected changes in the PDF."""
    page = document[page_number]
    for text, x, y, w, h in anomalies:
        rect = fitz.Rect(x, y, x + w, y + h)
        page.draw_rect(rect, color=(0, 0, 1), width=1.5)  # Draw a blue rectangle

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
    anomalies = detect_changes(text_data, expected_patterns)
    if anomalies:
        annotate_pdf(pdf_document, anomalies, page_number)

# Save the annotated PDF
output_pdf_path = pdf_path.replace('.pdf', '_annotated.pdf')
pdf_document.save(output_pdf_path)
pdf_document.close()

print(f"Annotated PDF saved as: {output_pdf_path}")
