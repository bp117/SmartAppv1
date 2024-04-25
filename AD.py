import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from sklearn.ensemble import Isolation Forest
from sklearn.preprocessing import StandardScaler
import numpy as np

# Load the PDF
pdf_path = "/mnt/data/INV-AP-B1-65583719-109634302829-JULY-2022.pdf"
pdf_document = fitz.open(pdf_path)

# Extract text and metadata using OCR
def extract_text_features(page):
    pixmap = page.get_pixmap()
    image_pil = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
    data = pytesseract.image_to_data(image_pil, output_type=pytesseract.Output.DICT)
    features = []
    text_blocks = []
    block_coords = []
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
            block_coords.append((data['left'][i], data['top'][i], data['left'][i] + data['width'][i], data['top'][i] + data['height'][i]))
    return np.array(features), text_blocks, block_coords

# Evaluate model performance and detect anomalies
def detect_anomalies(features, block_coords):
    if features.size == 0:
        return []
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    model = Isolation Forest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(features_scaled)
    predictions = model.predict(features_scaled)

    # Collect coordinates of anomalous text blocks
    anomalies = []
    for idx, pred in enumerate(predictions):
        if pred == -1:
            anomalies.append(block_coords[idx])
    return anomalies

# Process each page and annotate anomalies
for page_number, page in enumerate(pdf_document):
    features, text_blocks, block_coords = extract_text_features(page)
    anomalies = detect_anomalies(features, block_coords)
    if anomalies:
        for rect in anomalies:
            # Draw a red rectangle around each anomalous block
            page.draw_rect(fitz.Rect(rect), color=(1, 0, 0), width=1.5)
        print(f"Tampering detected and marked on page {page_number + 1}.")
    else:
        print(f"No tampering detected on page {page_number + 1}.")

# Save the annotated PDF
output_pdf_path = pdf_path.replace('.pdf', '_annotated.pdf')
pdf_document.save(output_pdf_path)
pdf_document.close()

print(f"Annotated PDF saved as: {output_pdf_path}")
