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

    def validate_sequence(headers_and_formats, spans_text):
        header_indices = [spans_text.index(header) for header in headers_and_formats if header in spans_text]
        
        if not header_indices:
            print("No headers found in the document.")
            return False
        
        header_indices.sort()
        
        for index, header in enumerate(headers_and_formats):
            if header not in spans_text:
                print(f"Header '{header}' missing in document.")
                return False
            header_position = spans_text.index(header)
            
            if index < len(header_indices) - 1:
                next_header_position = spans_text.index(list(headers_and_formats.keys())[index + 1])
                # Values should be between current header and next header
                values = spans_text[header_position + 1: next_header_position]
            else:
                # Last header, values should be till the end
                values = spans_text[header_position + 1:]

            if not values:
                print(f"No values found for header '{header}', document is tampered.")
                return False
            
            for value in values:
                if re.match(headers_and_formats[header], value):
                    continue
                else:
                    print(f"Value '{value}' for header '{header}' does not match the expected format.")
                    return False
                
        return True

    return validate_sequence(headers_and_formats, spans_text)

# Run validations
if validate_metadata():
    print("Metadata validation passed")
else:
    print("Metadata validation failed")

if validate_spans(spans_data):
    print("Spans validation passed")
else:
    print("Spans validation failed")
