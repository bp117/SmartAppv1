import requests
from docx import Document

def fetch_confluence_page(base_url, page_id, token):
    """Fetches a Confluence page content using Confluence REST API."""
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"  # Using Bearer token for authentication
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.json()

def save_as_docx(page_content, file_name):
    """Saves the Confluence page content to a .docx file."""
    doc = Document()
    doc.add_paragraph(page_content)
    doc.save(file_name)

# Configuration
BASE_URL = 'https://your-confluence-site.atlassian.net/wiki'  # Adjust to your Confluence base URL
PAGE_ID = '123456'  # The Confluence page ID you want to save
TOKEN = 'your_personal_access_token'  # Your Confluence Personal Access Token

# Main script
try:
    page_data = fetch_confluence_page(BASE_URL, PAGE_ID, TOKEN)
    page_body = page_data['body']['storage']['value']  # Adjust path based on actual API response structure
    save_as_docx(page_body, f'Confluence_Page_{PAGE_ID}.docx')
    print("Document has been saved successfully.")
except requests.HTTPError as e:
    print("Failed to fetch page:", e)
except Exception as e:
    print("An error occurred:", e)
