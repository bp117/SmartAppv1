import json
import re

# Load the JSON data from the potentially tampered PDF
with open('spans.json', 'r') as file:
    tampered_spans = json.load(file)

key_sequence = ["Plan Name", "From Date", "To Date", "Quantity", "Rental", "Net Amount"]
date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
billing_period_pattern = re.compile(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec), \d{4}$')
currency_pattern = re.compile(r'\d+\.?\d*')
name_pattern = re.compile(r"^[A-Za-z ]+$")
def extract_and_validate_data(spans):
    # Define patterns for specific types of data
    date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
    billing_period_pattern = re.compile(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec), \d{4}$')
    currency_pattern = re.compile(r'\d+\.?\d*')
    name_pattern = re.compile(r"^[A-Za-z ]+$")

    results = {
        'Billing Period': [],
        'Dates': [],
        'Currency Values': [],
        'Names': []
    }

    # Iterate over spans to check each item based on its label
    for i, span in enumerate(spans):
        label = span[1].strip()
        value = spans[i + 1][1].strip() if i + 1 < len(spans) else None

        if "Billing Period" in label:
            print("Billing Period", value)
            results['Billing Period'].append((value, bool(billing_period_pattern.match(value))))
        elif "Date" in label and "Billing Period" not in label:
            results['Dates'].append((value, bool(date_pattern.match(value))))
        elif any(term in label for term in ["Amount", "Total", "Sub Total", "Net Amount"]):
            results['Currency Values'].append((value, bool(currency_pattern.match(value))))
        elif "Name" in label or "Receipient" in label:  # Adjust based on how names are labeled in your data
            results['Names'].append((value, bool(name_pattern.match(value))))
    print("results", results)
    return results

def extract_key_sequence_and_values(spans):
    values_following_keys = []
    keys_found = []

    start_index = next((i for i, span in enumerate(spans) if "Invoice Charges" in span[1]), None)
    if start_index is None:
        return None, None, False

    # Identify and collect the sequence of keys and values
    for i in range(start_index + 1, len(spans)):
        text = spans[i][1].strip()
        if text in key_sequence:
            keys_found.append(text)
        else:
            break

    value_start_index = i
    for j in range(value_start_index, value_start_index + len(keys_found)):
        if j < len(spans):
            values_following_keys.append(spans[j][1].strip())

    return keys_found, values_following_keys, keys_found == key_sequence and len(values_following_keys) == len(keys_found)

# Validate individual values based on their labels
def validate_value(label, value,next_value=None):
    if "Billing Period" in label:
        return bool(billing_period_pattern.match(value))
    elif "Date" in label:
        return bool(date_pattern.match(value))
    elif any(term in label for term in ["Amount Payable",  "Amount After Due Date"]):
       if value == "₹" and next_value and currency_pattern.match(next_value):
            return True
        # Or if the current value is directly a numeric amount
            return bool(currency_pattern.match(value))
    elif "Name" in label or "Receipient" in label:
        return bool(name_pattern.match(value))
    return True
def extract_key_value_pairs(spans):
    pairs = {}
    for i in range(len(spans) - 1):
        key = spans[i][1].strip()
        # Check if it is likely to be a key
        if key in ["Date", "Total", "Invoice No", "Account No", "Sub Total","(Original for the Receipient)"]:
            value_candidate = spans[i + 1][1].strip()

            pairs[key] = value_candidate
    return pairs
# Extract and validate all spans in the document
def extract_and_validate_data(spans):
    results = []
    for i in range(len(spans) - 1):
        key = spans[i][1].strip()
        if key in ["Billing Period","Amount Payable", "Invoice Date", "Due Date", "Amount After Due Date"]:
            value = spans[i + 1][1].strip()
            next_value = spans[i + 2][1].strip() if i + 2 < len(spans) else None
        #value = spans[i + 1][1].strip()
            valid = validate_value(key, value,next_value)
            results.append((key, value, valid))
    return results

def check_name_after_specific_key(spans, key="(Original for the Receipient)", name_pattern=re.compile(r"^[A-Za-z ]+$")):
    for i, span in enumerate(spans):
        if span[1].strip() == key:
            if i + 1 < len(spans):
                match = name_pattern.match(spans[i + 1][1].strip())
                return match is not None, spans[i + 1][1].strip()
    return False, None

keys_found, values_following_keys, sequence_valid = extract_key_sequence_and_values(tampered_spans)
name_valid, actual_name = check_name_after_specific_key(tampered_spans)
#validation_results = validate_value_formats(dict(zip(keys_found, values_following_keys)))
validation_results_keys = extract_and_validate_data(tampered_spans)
print("validation_results_keys", validation_results_keys)
for label, value, valid in validation_results_keys:
        if not valid:
            print(f"Invalid entry for '{label}': '{value}'")
            all_valid = False
if sequence_valid  and name_valid:
    print("No structural tampering detected. Document conforms to expected formats and structure.")
else:
    print("Potential tampering detected in invoice charges section.")
    if not sequence_valid:
        print("Expected keys:", key_sequence)
        print("Actual keys found:", keys_found)
        print("Values found:", values_following_keys)
    if not name_valid:
        print(f"'Original for the Recipient' is expected to be followed by a valid name, found: '{actual_name}'")
    for category, entries in validation_results_keys.items():
        for value, valid in entries:
            if not valid:
                print(f"Invalid {category}: '{value}'")
                all_valid = False
    if all_valid:
        print("All data is valid according to specified formats.")