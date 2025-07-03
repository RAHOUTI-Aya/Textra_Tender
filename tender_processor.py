import os
import json
import pandas as pd
from glob import glob
from typing import List, Dict, Any
from main import analyze_supplier_submission, analyze_feedback_with_mistral

def extract_pdf_content(pdf_path: str) -> Dict:
    """
    This function would normally extract text from a PDF.
    Since we're working with a placeholder, it returns a dummy result.
    In a real implementation, you'd use a library like PyPDF2, pdfplumber, etc.
    """
    # In a real implementation, this would extract text from the PDF
    # For demonstration purposes, we'll just return the filename as content
    return {"text": f"Contenu extrait de {os.path.basename(pdf_path)}"}

def process_tender_folder(folder_path: str, client_requirements: Dict, feedback_text: str = None) -> List[Dict]:
    """
    Process all tender files in a folder and analyze them.
    Args:
        folder_path: Path to folder containing tender files
        client_requirements: Dictionary with client requirements
        feedback_text: Optional global feedback text to apply to all tenders
    Returns:
        List of dictionaries with analysis results
    """
    # Find all JSON files in the folder
    json_files = glob(os.path.join(folder_path, "*.json"))
    
    # Find all PDF files in the folder
    pdf_files = glob(os.path.join(folder_path, "*.pdf"))
    
    results = []
    
    # Process each JSON file first (these are already extracted)
    for json_path in json_files:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Get base name without extension
            base_name = os.path.splitext(os.path.basename(json_path))[0]
            
            # Find corresponding PDF if it exists
            pdf_path = next((pdf for pdf in pdf_files if os.path.splitext(os.path.basename(pdf))[0] == base_name), None)
            
            # Get content from JSON
            content = json_data.get('text', '')
            
            # Analyze tender with potential feedback
            analysis = analyze_supplier_submission(content, client_requirements, feedback_text)
            
            # Create result dictionary
            result = {
                'tender_id': base_name,
                'score': analysis['Score'],
                'justification': analysis['Justification'],
                'pdf_path': pdf_path,
                'json_path': json_path,
                'content': content,
                'feedback': feedback_text if feedback_text else '',
                'sentiment': analyze_feedback_with_mistral(feedback_text) if feedback_text else 'neutre'
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"Error processing JSON file {json_path}: {str(e)}")
    
    # Process PDFs that don't have corresponding JSON files
    for pdf_path in pdf_files:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Check if we already processed this file via JSON
        if any(r['tender_id'] == base_name for r in results):
            continue
        
        try:
            # Extract content from PDF
            content_dict = extract_pdf_content(pdf_path)
            content = content_dict.get('text', '')
            
            # Analyze tender with potential feedback
            analysis = analyze_supplier_submission(content, client_requirements, feedback_text)
            
            # Create result dictionary
            result = {
                'tender_id': base_name,
                'score': analysis['Score'],
                'justification': analysis['Justification'],
                'pdf_path': pdf_path,
                'json_path': None,
                'content': content,
                'feedback': feedback_text if feedback_text else '',
                'sentiment': analyze_feedback_with_mistral(feedback_text) if feedback_text else 'neutre'
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"Error processing PDF file {pdf_path}: {str(e)}")
    
    return results

def get_top_tenders(results: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Get top N tenders by score.
    Args:
        results: List of tender results
        top_n: Number of top results to return
    Returns:
        List of top N tender results
    """
    # Sort results by score in descending order
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
    
    # Return top N results
    return sorted_results[:top_n]

def create_results_dataframe(results: List[Dict]) -> pd.DataFrame:
    """
    Create a pandas DataFrame from tender results for display.
    Args:
        results: List of tender results
    Returns:
        Pandas DataFrame
    """
    # Extract relevant columns
    data = []
    for result in results:
        data.append({
            'Tender ID': result['tender_id'],
            'Score': result['score'],
            'PDF Path': os.path.basename(result['pdf_path']) if result['pdf_path'] else 'N/A',
            'Sentiment': result.get('sentiment', 'N/A'),
            'Feedback': result.get('feedback', '')[:50] + '...' if result.get('feedback', '') else 'N/A'
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Sort by score
    df = df.sort_values('Score', ascending=False)
    
    return df