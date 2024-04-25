import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from sklearn.ensemble import Isolation Forest
from sklearn.preprocessing import StandardScaler
import numpy as np
import re

# Load the PDF
pdf_path = "/mnt/data/your_document.pdf"
pdf_document = fitz.open(pdf_path)

# Define regions of interest (ROI) based on your document layout
# Example ROI for amounts, customer names, and addresses (x0, y0, x1, y1)
roi_boxes = {
    'amounts': fitz.Rect(100, 500, 300, 550),
    'names': fitz.Rect(100, 200, 300, 250),
    'addresses': fitz.Rect(100, 300, 300, 350)
}

# Extract text within specified regions of interest
def extract_roi_features(page):
    features = []
    text_blocks = []
    for key, roi in roi_boxes.items():
        words = page.get_text("words")  # Gets text as list of words along with their bounding boxes
        for word in words:
            word_rect = fitz.Rect(word[:4])
            if word_rect.intersects(roi):
                feature = [
                    word[0],  # x0
                    word[1],  # y0
                    word[2] - word[0],  # width
                    word[3] - word[1],  # height
                    len(word[4]),  # text length
                    word[4]  # the text itself for further analysis
                ]
                features.append(feature)
                text_blocks.append({'text': word[4], 'type': key, 'coords': word[:4]})
    return np.array(features), text_blocks

# Detect anomalies using Isolation Forest
def detect_anomalies(features, text_blocks):
    if len(features) == 0:
        return []
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features[:,:-1])  # Exclude text for scaling
    model = Isolation Forest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(features_scaled)
    predictions = model.predict(features_scaled)
    anomalies = []
    for idx, pred in enumerate(predictions):
        if pred == -1:
            anomalies.append(text_blocks[idx])
    return anomalies

# Process each page
for page_number, page in enumerate(pdf_document):
    features, text_blocks = extract_roi_features(page)
    anomalies = detect_anomalies(features, text_blocks)
    if anomalies:
        print(f"Potential tampering detected on page {page_number + 1} in the following blocks:")
        for anomaly in anomalies:
            print(f" - {anomaly['type']} at {anomaly['coords']}: {anomaly['text']}")
    else:
        print(f"No tampering detected on page {page_number + 1}")

# Save the annotated PDF
output_pdf_path = pdf_path.replace('.pdf', '_annotated.pdf')
pdf_document.save(output_pdf_path)
pdf_document.close()

print(f"Annotated PDF saved as: {output_pdf_path}")
