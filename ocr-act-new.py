import os
import json
import fitz  # PyMuPDF
import pandas as pd
import re

# Directory configuration
pdf_dir = "/Users/binduraj/Documents/Bindu/RAFT_POC_WORK/bills (1)"
output_dir = "/Users/binduraj/Documents/Bindu/RAFT_POC_WORK/processed-new"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Regular expression patterns
date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
currency_pattern = re.compile(r'^\d+\.?\d*')  # Matches numbers with optional decimal part
unicode_currency_pattern = re.compile(r"^₹\s*[\d,]+\.\d+$")# Handles Unicode symbol followed by numbers
name_pattern = re.compile(r'[A-Za-z\s]+')  # Adjust the name pattern as needed

# Invoice fields and their expected patterns
invoice_key_patterns = {
    "Billing Period": re.compile(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec), \d{4}$'),
    "Invoice Date": date_pattern,
    "Amount Payable": currency_pattern,
    "Due Date": date_pattern,
    "Amount After Due Date": currency_pattern
}

def check_invoice_context(spans):
    for i, span in enumerate(spans):
       
        if "Account No" in span[1]:
            print("span: ", span[1])
            return False
        if "TAX INVOICE" in span[1] or "INVOICE" in span[1]:
            
            if i + 1 < len(spans) and "(Original for the Receipient)" in spans[i + 1][1]:
                if i + 2 < len(spans) and name_pattern.match(spans[i + 2][1].strip()):
                    return True
    return False

def validate_invoice_sequence(spans):
    results = {}
    tampered = False
    tax_invoice_present = check_invoice_context(spans)
    print("tax_invoice_present: ", tax_invoice_present)

    for i, (bbox, text) in enumerate(spans):
        text = text.strip()
        if text in invoice_key_patterns:
            pattern = invoice_key_patterns[text]
            next_span = spans[i + 1][1].strip() if i + 1 < len(spans) else ""
            if tax_invoice_present and text.startswith("Amount"):
                print("text: ", text,":",next_span)
                valid = bool(unicode_currency_pattern.match(next_span))
                print("valid: ", valid)
            else:
                print("in else")
                if text.startswith("Amount"):
                    print("in if")
                    # Check if two parts are needed (Unicode and amount)
                    next_next_span = spans[i + 2][1].strip() if i + 2 < len(spans) else ""
                    combined_span = next_span + next_next_span
                    valid = bool(unicode_currency_pattern.match(combined_span))
                    next_span = combined_span
                    #next_next_span = spans[i + 2][1].strip() if i + 2 < len(spans) else ""
                    #valid = bool(re.match(r'^₹$', spans[i + 1][1].strip())) and bool(currency_pattern.match(next_next_span))
                else:
                    print("in else of inner if")
                    valid = bool(pattern.match(next_span))
            results[text] = (next_span, valid)
            if not valid:
                tampered = True

    return results, tampered

def process_pdfs(pdf_dir, output_dir):
    validation_results = []

    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            doc = fitz.open(os.path.join(pdf_dir, filename))
            page = doc[0]
            spans = [(span['bbox'], span['text']) for block in page.get_text("dict")['blocks'] if 'lines' in block for line in block['lines'] for span in line['spans']]
            
            # Save spans to JSON for future reference or checks
            with open(os.path.join(output_dir, filename.replace('.pdf', '_spans.json')), 'w') as file:
                json.dump(spans, file)

            # Validate the document based on defined rules
            results, is_tampered = validate_invoice_sequence(spans)
            validation_results.append({
                'Filename': filename,
                'Results': results,
                'Tampered': is_tampered
            })

    # Save validation results to a CSV file
    df = pd.DataFrame(validation_results)
    df.to_csv(os.path.join(output_dir, 'document_validation_results.csv'), index=False)

# Execute the processing function
process_pdfs(pdf_dir, output_dir)
