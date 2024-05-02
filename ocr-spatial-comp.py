import json

# Load the JSON data for original and potentially tampered PDFs
with open('spans.json', 'r') as file:
    original_spans = json.load(file)

with open('spans_new.json', 'r') as file:
    tampered_spans = json.load(file)

def calculate_distance(box1, box2):
    # Using center point distance for simplicity
    center1 = ((box1[0] + box1[2]) / 2, (box1[1] + box1[3]) / 2)
    center2 = ((box2[0] + box2[2]) / 2, (box2[1] + box2[3]) / 2)
    return ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5

def extract_key_value_pairs(spans, max_distance=50):
    pairs = []
    keys = [span for span in spans if ":" in span[1] or "Date" in span[1] or "Total" in span[1]]

    for key in keys:
        closest_value = None
        min_distance = float('inf')

        for span in spans:
            if span == key:
                continue
            distance = calculate_distance(key[0], span[0])
            if distance < min_distance and distance < max_distance:
                closest_value = span
                min_distance = distance

        if closest_value:
            pairs.append((key, closest_value))
    return pairs

def compare_structures(original_pairs, tampered_pairs):
    if len(original_pairs) != len(tampered_pairs):
        print("Mismatch in number of key-value pairs.")
        return False

    for orig_pair, tamp_pair in zip(original_pairs, tampered_pairs):
        if orig_pair[0][1] != tamp_pair[0][1]:
            print(f"Mismatch found: Original '{orig_pair[0][1]}' vs. Tampered '{tamp_pair[0][1]}'")
            return False
    return True

original_pairs = extract_key_value_pairs(original_spans)
tampered_pairs = extract_key_value_pairs(tampered_spans)

# Print the extracted key-value pairs
print("Original Key-Value Pairs:")
for key, value in original_pairs:
    print(f"{key[1]}: {value[1]}")

print("\nTampered Key-Value Pairs:")
for key, value in tampered_pairs:
    print(f"{key[1]}: {value[1]}")
    
# Compare the structures of the original and tampered documents
if compare_structures(original_pairs, tampered_pairs):
    print("No structural tampering detected.")
else:
    print("Structural tampering detected.")
