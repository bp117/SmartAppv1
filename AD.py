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
    blocks = {}  # Dictionary to hold block positions and text
    for i, word in enumerate(data['text']):
        if word.strip():  # Check non-empty words
            block_num = data['block_num'][i]
            if block_num not in blocks:
                blocks[block_num] = {
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'right': data['left'][i] + data['width'][i],
                    'bottom': data['top'][i] + data['height'][i],
                    'texts': [word]
                }
            else:
                # Update block dimensions to include new word
                blocks[block_num]['right'] = max(blocks[block_num]['right'], data['left'][i] + data['width'][i])
                blocks[block_num]['bottom'] = max(blocks[block_num]['bottom'], data['top'][i] + data['height'][i])
                blocks[block_num]['texts'].append(word)

    # Flatten block data into features and calculate distances
    last_block_position = None
    for block in blocks.values():
        # Calculate horizontal and vertical center of the block
        center_x = (block['left'] + block['right']) / 2
        center_y = (block['top'] + block['bottom']) / 2
        block_feature = [
            block['left'],
            block['top'],
            block['right'] - block['left'],
            block['bottom'] - block['top'],
            len(" ".join(block['texts'])),  # Total length of text in the block
            center_x,
            center_y
        ]
        if last_block_position:
            # Distance to the previous block
            distance = np.sqrt((center_x - last_block_position[0]) ** 2 + (center_y - last_block_position[1]) ** 2)
            block_feature.append(distance)
        else:
            block_feature.append(0)  # No distance for the first block
        features.append(block_feature)
        last_block_position = (center_x, center_y)

    return np.array(features) if features else np.empty((0, 8))

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
    grid_search.fit(features[:, :-1])  # Fit model without distance feature
    best_model = grid_search.best_estimator_
    predictions = best_model.predict(features[:, :-1])
    anomalies = features[predictions == -1]
    return anomalies

# Process each page
for page_number, page in enumerate(pdf_document):
    features = extract_text_features(page)
    anomalies = detect_anomalies(features)
    if anomalies.size > 0:
        print(f"Potential tampering detected on page {page_number + 1} at positions {anomalies[:, :-1]}")  # Exclude distance feature from output
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from sklearn.ensemble import Isolation Forest

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
                len(word)
            ])
    return np.array(features) if features else np.empty((0, 5))

# Evaluate model performance based on silhouette score or other custom criteria
def evaluate_model(features):
    # Define potential parameter ranges
    n_estimators = [50, 100, 150]
    contamination_levels = [0.01, 0.05, 0.1]
    best_score = -np.inf
    best_params = {}
    
    for n in n_estimators:
        for contamination in contamination_levels:
            model = Isolation Forest(n_estimators=n, contamination=contamination, random_state=42)
            model.fit(features)
            # Calculate anomaly scores (negative scores are more anomalous)
            scores = model.decision_function(features)
            average_score = np.mean(scores)
            if average_score > best_score:
                best_score = average_score
                best_params = {'n_estimators': n, 'contamination': contamination}
    
    return best_params, best_score

# Process each page
for page_number, page in enumerate(pdf_document):
    features = extract_text_features(page)
    if features.size > 0:
        best_params, best_score = evaluate_model(features)
        print(f"Best params for page {page_number + 1}: {best_params} with score {best_score}")
    else:
        print(f"No features to analyze on page {page_number + 1}")
    
    else:
        print(f"No tampering detected on page {page_number + 1}")
