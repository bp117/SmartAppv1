import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from sklearn.ensemble import Isolation Forest
from sklearn.preprocessing import StandardScaler
import numpy as np

# Load the PDF
pdf_path = "/mnt/data/your_document.pdf"
pdf_document = fitz.open(pdf_path)

# Define regions of interest (ROI) based on your document layout
roi_boxes = {
    'amounts': fitz.Rect(100, 500, 300, 550),
    'names': fitz.Rect(100, 200, 300, 250),
    'addresses': fitz.Rect(100, 300, 300, 350)
}

def extract_roi_features(page):
    features = []
    text_blocks = []
    for key, roi in roi_boxes.items():
        words = page.get_text("words")  # Getting text and bounding boxes
        for word in words:
            word_rect = fitz.Rect(word[:4])
            if word_rect.intersects(roi):
                feature = [word[0], word[1], word[2] - word[0], word[3] - word[1], len(word[4])]
                features.append(feature)
                text_blocks.append({'text': word[4], 'type': key, 'coords': word[:4]})
    return np.array(features), text_blocks

def detect_anomalies(features, text_blocks):
    if features.size == 0:
        return []
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    model = Isolation Forest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(features_scaled)
    predictions = model.predict(features_scaled)
    anomalies = []
    for idx, pred in enumerate(predictions):
        if pred == -1:
            anomalies.append(text_blocks[idx])
    return anomalies

def annotate_pdf(document, anomalies, page_number):
    page = document[page_number]
    for anomaly in anomalies:
        rect = fitz.Rect(anomaly['coords'])
        page.draw_rect(rect, color=(1, 0, 0), width=2)  # Draw a red rectangle

# Process each page
for page_number, page in enumerate(pdf_document):
    features, text_blocks = extract_roi_features(page)
    anomalies = detect_anomalies(features, text_blocks)
    if anomalies:
        annotate_pdf(pdf_document, anomalies, page_number)
        print(f"Tampering detected and marked on page {page_number + 1}.")
    else:
        print(f"No tampering detected on page {page_number + 1}.")

# Save the annotated PDF
output_pdf_path = pdf_path.replace('.pdf', '_annotated.pdf')
pdf_document.save(output_pdf_path)
pdf_document.close()

print(f"Annotated PDF saved as: {output_pdf_path}")
