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
    for i, word in enumerate(data['text']):
        if word.strip():
            features.append([
                int(data['left'][i]),
                int(data['top'][i]),
                int(data['width'][i]),
                int(data['height'][i]),
                len(word),
                int(data['conf'][i])  # OCR confidence as a feature
            ])
    return np.array(features) if features else np.empty((0, 6))

# Evaluate model performance
def evaluate_model(features):
    # Normalize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # Define potential parameter ranges
    n_estimators = [50, 100, 150]
    contamination_levels = np.linspace(0.01, 0.1, 5)  # Dynamic range of contamination
    best_score = np.inf
    best_params = {}
    
    for n in n_estimators:
        for contamination in contamination_levels:
            model = Isolation Forest(n_estimators=n, contamination=contamination, random_state=42)
            model.fit(features_scaled)
            # Calculate anomaly scores
            scores = model.score_samples(features_scaled)
            average_score = np.mean(scores)
            if average_score < best_score:  # Looking for the lowest score as indication of anomalies
                best_score = average_score
                best_params = {'n_estimators': n, 'contamination': contamination}
    
    return best_params, best_score

# Process each page
for page_number, page in enumerate(pdf_document):
    features = extract_text_features(page)
    if features.size > 0:
        best_params, best_score = evaluate_model(features)
        print(f"Best params for page {page_number + 1}: {best_params} with anomaly score {best_score}")
        if best_score < -0.5:  # Example threshold, adjust based on your data
            print(f"Potential tampering detected on page {page_number + 1}")
    else:
        print(f"No features to analyze on page {page_number + 1}")
