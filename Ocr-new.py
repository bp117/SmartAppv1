import json
import re
from PyPDF2 import PdfReader

# Load the spans JSON file
with open('/mnt/data/output4_TAMP.json') as json_file:
    spans_data = json.load(json_file)

# Load the PDF file
pdf_path = '/mnt/data/ACT Invoice.pdf'
pdf_reader = PdfReader(pdf_path)

# Validate metadata
def validate_metadata():
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
def validate_spans(spans_data):
    # Define the expected headers and their formats
    headers_and_formats = {
        "Previous Due ₹": r"\d+",
        "Payments Received ₹": r"\d+",
        "Adjustments ₹": r"\d+",
        "Invoice Amount ₹": r"\d{1,3}(,\d{3})*",
        "Balance Amount ₹": r"\d{1,3}(,\d{3})*",
        "Amount Payable ₹": r"\d{1,3}(,\d{3})*",
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

    spans_text = [span[1] for span in spans_data]

    def validate_headers_and_values(spans_text, headers_and_formats):
        header_positions = [i for i, text in enumerate(spans_text) if text in headers_and_formats]
        
        for i in range(len(header_positions) - 1):
            header = spans_text[header_positions[i]]
            next_header = spans_text[header_positions[i + 1]]
            header_index = spans_text.index(header)
            next_header_index = spans_text.index(next_header)

            # Extract values between current header and next header
            values = spans_text[header_index + 1: next_header_index]
            if not values:
                print(f"Validation failed: No values found for header '{header}'")
                return False
            
            # Validate the values with the regex
            regex = headers_and_formats[header]
            for value in values:
                if not re.match(regex, value):
                    print(f"Validation failed for header '{header}': value '{value}' does not match expected format")
                    return False
        
        # Validate the last header values
        last_header = spans_text[header_positions[-1]]
        last_header_index = spans_text.index(last_header)
        values = spans_text[last_header_index + 1:]
        if not values:
            print(f"Validation failed: No values found for header '{last_header}'")
            return False
        
        regex = headers_and_formats[last_header]
        for value in values:
            if not re.match(regex, value):
                print(f"Validation failed for header '{last_header}': value '{value}' does not match expected format")
                return False

        return True

    return validate_headers_and_values(spans_text, headers_and_formats)

# Run validations
if validate_metadata():
    print("Metadata validation passed")
else:
    print("Metadata validation failed")

if validate_spans(spans_data):
    print("Spans validation passed")
else:
    print("Spans validation failed")
