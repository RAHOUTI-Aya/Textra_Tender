import PyPDF2
import io
import json
import os
from typing import Dict, Tuple, Optional

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    text = ""
    try:
        print(f"Extracting text from {pdf_path}...")
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                extracted_page_text = page.extract_text()
                if extracted_page_text:
                    text += extracted_page_text + "\n"
                
        if not text.strip():
            print(f"Warning: No text extracted from {pdf_path}")
        
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        return ""


def create_json_from_pdf(pdf_path: str, output_dir: Optional[str] = None) -> Tuple[str, dict]:
    """
    Create a JSON file from a PDF and return the path and content
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the JSON file (defaults to same directory as PDF)
        
    Returns:
        Tuple of (json_file_path, json_content)
    """
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Create base filename without extension
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Create JSON content
    json_content = {
        "tender_id": base_filename,
        "text": text,
        "feedback": "",  # Empty feedback by default
        "pdf_path": pdf_path
    }
    
    # Save to JSON file
    json_file_path = os.path.join(output_dir, f"{base_filename}.json")
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(json_content, f, ensure_ascii=False, indent=2)
    
    return json_file_path, json_content


def process_pdf_directory(pdf_dir: str, output_dir: Optional[str] = None) -> Dict[str, dict]:
    """
    Process all PDFs in a directory and create JSON files
    
    Args:
        pdf_dir: Directory containing PDF files
        output_dir: Directory to save JSON files (defaults to same as pdf_dir)
        
    Returns:
        Dictionary mapping tender IDs to their JSON content
    """
    if output_dir is None:
        output_dir = pdf_dir
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    # Find all PDF files
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        try:
            # Create JSON from PDF
            json_path, json_content = create_json_from_pdf(pdf_path, output_dir)
            
            # Store result
            tender_id = json_content['tender_id']
            results[tender_id] = json_content
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")
    
    return results