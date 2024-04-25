import numpy as np
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from sklearn.ensemble import Isolation Forest
from sklearn.preprocessing import StandardScaler

# Load the PDF
pdf_document = fitz.open("/mnt/data/INV-AP-B1-65583719-109634302829-JULY-2022.pdf")

# Extract text and metadata using OCR
def extract_text_features(page):
    pixmap = page.get_pixmap()
    image_pil = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
    data = pytesseract.image_to_data(image_pil, output_type=pytesseract.Output.DICT)
    features = []
    text_blocks = []
    for i, word in enumerate(data['text']):
        if word.strip():  # Include only non-empty words
            feature = [
                int(data['left'][i]),
                int(data['top'][i]),
                int(data['width'][i]),
                int(data['height'][i]),
                len(word),
                int(data['conf'][i])  # OCR confidence as a feature
            ]
            features.append(feature)
            text_blocks.append(word)  # Keep track of the text corresponding to each feature
    return np.array(features), text_blocks

# Evaluate model performance and detect anomalies
def detect_anomalies(features, text_blocks):
    if features.size == 0:
        return []
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    model = Isolation Forest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(features_scaled)
    predictions = model.predict(features_scaled)

    # Collect anomalous text blocks
    anomalies = []
    for idx, pred in enumerate(predictions):
        if pred == -1:
            anomalies.append(text_blocks[idx])
    return anomalies

# Process each page
for page_number, page in enumerate(pdf_document):
    features, text_blocks = extract_text_features(page)
    anomalies = detect_anomalies(features, text_blocks)
    if anomalies:
        print(f"Potential tampering detected on page {page_number + 1} in the following text blocks: {anomalies}")
    else:
        print(f"No tampering detected on page {page_number + 1}")
