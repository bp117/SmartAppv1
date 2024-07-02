import json
import re
from PyPDF2 import PdfReader

# Load the spans JSON file
json_file_path = '/mnt/data/file-c0uCXi0KJGdhhEp3RUyqR0Dc'
with open(json_file_path) as json_file:
    spans_data = json.load(json_file)

# Extract the text spans
spans_text = [span[1] for span in spans_data]

# Define the expected headers and their formats
headers_and_formats = {
    "Previous Due ₹": r"\d+",
    "Payments Received ₹": r"\d+",
    "Adjustments ₹": r"\d+",
    "Invoice Amount ₹": r"\d{1,3}(,\d{3})*",
    "Balance Amount ₹": r"\d{1,3}(,\d{3})*",
    "Amount Payable ₹": r"\d{1,3}(,\d{3})*",
    "If paid after due date": r"\d{1,3}(,\d{3})*",
    "Txn No": r".+",
    "Txn Date": r"\d{2}/\d{2}/\d{4}",
    "Period": r".+ - .+",
    "Description": r".+",
    "HSN Code": r"\d+",
    "Package/Goods Description": r".+",
    "Rate": r"\d{1,3}(,\d{3})*",
    "Unit": r".+",
    "Quantity": r"\d+ days",
    "Discount": r"\d+",
    "Taxable Amount": r"\d{1,3}(,\d{3})*",
    "CGST Rate %": r"\d+",
    "CGST Amount": r"\d{1,3}(,\d{3})*",
    "SGST Rate %": r"\d+",
    "SGST Amount": r"\d{1,3}(,\d{3})*",
    "Amount Incl. Tax": r"\d{1,3}(,\d{3})*",
}

# Validate metadata
def validate_metadata(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    metadata = pdf_reader.metadata
    creation_date = metadata.get('/CreationDate', '')
    modification_date = metadata.get('/ModDate', '')

    if creation_date != '2024-07-02T02:49:14Z' or modification_date != '2024-07-02T02:49:14Z':
        print("Metadata validation failed: Creation or modification date mismatch")
        return False
    
    trailer = pdf_reader.trailer
    if '/Index' in trailer:
        print("Metadata validation failed: /Index found in PDF trailer")
        return False
    
    return True

# Validate the sequence and format of table spans
def validate_spans(spans_text, headers_and_formats):
    header_keys = list(headers_and_formats.keys())
    header_indices = [spans_text.index(header) for header in header_keys if header in spans_text]

    if len(header_indices) != len(header_keys):
        print("Validation failed: Some headers are missing")
        return False

    # Ensure all headers come first in the correct order
    for i in range(1, len(header_indices)):
        if header_indices[i] <= header_indices[i-1]:
            print(f"Validation failed: Header '{header_keys[i]}' is out of order")
            return False

    # Extract the values following the headers
    values_start_index = header_indices[-1] + 1
    values = spans_text[values_start_index:values_start_index + len(header_keys)]

    if len(values) != len(header_keys):
        print("Validation failed: Number of values does not match number of headers")
        return False

    # Validate the values against the formats
    for i, header in enumerate(header_keys):
        value = values[i]
        regex = headers_and_formats[header]
        if not re.match(regex, value):
            print(f"Validation failed for header '{header}': value '{value}' does not match expected format")
            return False

    return True

# Run validations
pdf_path = '/mnt/data/ACT Invoice.pdf'
if validate_metadata(pdf_path):
    print("Metadata validation passed")
else:
    print("Metadata validation failed")

if validate_spans(spans_text, headers_and_formats):
    print("Spans validation passed")
else:
    print("Spans validation failed")
