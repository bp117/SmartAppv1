import json

# Load the JSON data for original and potentially tampered PDFs
with open('spans.json', 'r') as file:
    original_spans = json.load(file)

with open('spans_new.json', 'r') as file:
    tampered_spans = json.load(file)

def extract_key_value_pairs(spans):
    pairs = []
    key_candidate = None

    # Example simplistic pairing based on proximity and sequence
    for span in spans:
        if ":" in span[1] or "Date" in span[1]:
            key_candidate = span
        elif key_candidate:
            # Assuming a key is immediately followed by its value in the JSON structure
            pairs.append((key_candidate, span))
            key_candidate = None  # Reset key candidate after pairing
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
