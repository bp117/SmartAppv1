# .env.example
# Copy this file to .env and fill in your specific values
GOOGLE_CLOUD_PROJECT=your-project-id
DOCUMENT_AI_PROCESSOR_ID=your-processor-id
# Optional: Specify location of Google Cloud services
DOCUMENT_AI_LOCATION=us

# load_env.py
# Helper script to load environment variables
import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    required_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "DOCUMENT_AI_PROCESSOR_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with these variables or set them in your environment.")
        return False
    
    return True

# utils.py
# Utility functions for the PDF processor
import base64
import os
import json
from typing import List, Dict, Any

def save_images_from_document(images: List[Dict[str, Any]], output_dir: str) -> List[str]:
    """
    Save extracted images to disk and return their file paths.
    
    Args:
        images: List of image data dictionaries
        output_dir: Directory to save images
        
    Returns:
        List of saved image file paths
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    image_paths = []
    for idx, img in enumerate(images):
        try:
            # Decode base64 image data
            img_data = base64.b64decode(img.get("image_data", ""))
            
            # Generate filename
            file_path = os.path.join(output_dir, f"image_{idx+1}_page_{img.get('page', 0)}.png")
            
            # Save image
            with open(file_path, "wb") as img_file:
                img_file.write(img_data)
            
            image_paths.append(file_path)
        except Exception as e:
            print(f"Error saving image {idx}: {str(e)}")
    
    return image_paths

def enhance_content(text: str) -> str:
    """
    Apply basic NLP enhancements to the raw text.
    This is a placeholder that could be expanded with actual NLP processing.
    
    Args:
        text: Raw text content
        
    Returns:
        Enhanced text
    """
    # This is where you could integrate with NLP services or libraries
    # For now, just doing basic cleaning
    enhanced = text.strip()
    # Remove excessive whitespace
    enhanced = ' '.join(enhanced.split())
    return enhanced

def determine_presentation_context(text: str) -> str:
    """
    Determine the presentation context based on content.
    This is a placeholder function.
    
    Args:
        text: Text content
        
    Returns:
        Presentation context string
    """
    # This would be where you analyze the content to determine context
    # For demo purposes, returning a generic context
    if "bank" in text.lower() or "financial" in text.lower():
        return "I work in banking. This is financial service content."
    return "This is general document content."

def determine_groups(text: str) -> Dict[str, bool]:
    """
    Determine which groups the content belongs to.
    
    Args:
        text: Text content
        
    Returns:
        Dictionary of group names and boolean values
    """
    groups = {}
    
    # Basic keyword matching - could be replaced with more sophisticated categorization
    keywords = {
        "banking": ["bank", "financial", "credit", "loan", "mortgage"],
        "insurance": ["insurance", "policy", "claim", "premium", "coverage"],
        "investment": ["investment", "stock", "bond", "portfolio", "asset"],
        "compliance": ["compliance", "regulation", "policy", "procedure", "guideline"]
    }
    
    text_lower = text.lower()
    
    for group, words in keywords.items():
        groups[group] = any(word in text_lower for word in words)
    
    return groups
