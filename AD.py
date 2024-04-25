import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from sklearn.ensemble import Isolation Forest
import numpy as np
from sklearn.model_selection import GridSearchCV

# Load the PDF
pdf_document = fitz.open("/mnt/data/INV-AP-B1-65583719-109634302829-JULY-2022.pdf")

# Extract text and metadata using OCR
def extract_text_features(page):
    image = page.get_pixmap()
    image_pil = Image.frombytes("RGB", [image.width, image.height], image.image)
    data = pytesseract.image_to_data(image_pil, output_type=pytesseract.Output.DICT)
    features = []
    for i, word in enumerate(data['text']):
        if word.strip():  # Check non-empty words
            features.append([
                int(data['left'][i]),
                int(data['top'][i]),
                int(data['width'][i]),
                int(data['height'][i]),
                len(word),
                int(data['conf'][i]),  # Confidence level of OCR
                # Additional features like font size could be estimated from 'height' and specific pattern matching
            ])
    return np.array(features) if features else np.empty((0, 6))

# Parameter tuning and anomaly detection
def detect_anomalies(features):
    if features.size == 0:
        return []
    params = {
        'n_estimators': [50, 100, 150],
        'contamination': [0.01, 0.05, 0.1]
    }
    model = Isolation Forest()
    grid_search = GridSearchCV(model, params, cv=3)
    grid_search.fit(features)
    best_model = grid_search.best_estimator_
    predictions = best_model.predict(features)
    anomalies = features[predictions == -1]
    return anomalies

# Process each page
for page_number, page in enumerate(pdf_document):
    features = extract_text_features(page)
    anomalies = detect_anomalies(features)
    if anomalies.size > 0:
        print(f"Potential tampering detected on page {page_number + 1} at positions {anomalies}")
    else:
        print(f"No tampering detected on page {page_number + 1}")
