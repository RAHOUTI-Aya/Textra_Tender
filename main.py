import json
import requests
import os
import argparse
from typing import Dict, List
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment or use default if not found
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "VVjexrRbRJfxwRxFj8C3jswoaQT8fhAe")  # 🔐 Use env var if possible
HEADERS = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}

# Improved function to analyze feedback with neutral sentiment option
def analyze_feedback_with_mistral(feedback_text: str) -> str:
    if not feedback_text or feedback_text.strip() == "":
        return "neutre"  # Default to neutral for empty feedback

    prompt = (
        "Voici un commentaire laissé par un fournisseur sur un appel d'offres. "
        "Analyse s'il est **positif**, **négatif** ou **neutre**. "
        "Retourne uniquement un mot : 'positif', 'négatif' ou 'neutre'.\n\n"
        f"Commentaire : {feedback_text}"
    )

    payload = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        response = requests.post(MISTRAL_API_URL, headers=HEADERS, json=payload)
        result = response.json()["choices"][0]["message"]["content"].lower().strip()

        # Handle different possible responses
        if "positif" in result:
            return "positif"
        elif "négatif" in result:
            return "négatif"
        else:
            return "neutre"
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return "neutre"  # Default to neutral on error

# Enhanced function to assess if feedback indicates a blocking issue
def assess_feedback_criticality(feedback_text: str) -> dict:
    if not feedback_text or feedback_text.strip() == "":
        return {"is_blocking": False, "reason": "Pas de feedback"}

    prompt = (
        "Voici un commentaire laissé par un fournisseur sur un appel d'offres. "
        "Analyse si ce commentaire indique un problème bloquant qui devrait invalider complètement cette offre "
        "(c'est-à-dire qui justifierait un score de 0/100).\n\n"
        "Un problème bloquant peut être par exemple:\n"
        "- Une impossibilité technique ou légale de répondre\n"
        "- Des exigences contradictoires ou impossibles à satisfaire\n"
        "- Une discrimination ou pratique illégale\n"
        "- Une date limite déjà passée ou impossible à respecter\n\n"
        f"Commentaire: {feedback_text}\n\n"
        "Réponds avec une structure JSON avec deux champs:\n"
        "1. 'is_blocking': boolean (true si le problème est bloquant, false sinon)\n"
        "2. 'reason': courte explication de ta décision"
    )

    payload = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        response = requests.post(MISTRAL_API_URL, headers=HEADERS, json=payload)
        result = response.json()["choices"][0]["message"]["content"].strip()

        import re
        json_match = re.search(r'({.*})', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                result_json = json.loads(json_str)
                return {
                    "is_blocking": result_json.get("is_blocking", False),
                    "reason": result_json.get("reason", "Analyse non concluante")
                }
            except json.JSONDecodeError:
                pass

        return {
            "is_blocking": "true" in result.lower() and "block" in result.lower(),
            "reason": "Analyse basée sur les mots-clés (fallback)"
        }

    except Exception as e:
        print(f"Error in feedback criticality analysis: {str(e)}")
        return {"is_blocking": False, "reason": f"Erreur lors de l'analyse: {str(e)}"}

# Remaining function definitions would go here

# Function to reanalyze tenders with user feedback
def reanalyze_tender_with_feedback(tender_data: dict, feedback_text: str, client_requirements: dict) -> dict:
    text = tender_data.get('content', '')
    if not text and 'json_path' in tender_data:
        try:
            with open(tender_data['json_path'], 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                text = json_data.get('text', '')
        except Exception as e:
            print(f"Error reading JSON file: {str(e)}")

    result = analyze_supplier_submission(text, client_requirements, feedback_text)

    tender_data['score'] = result['Score']
    tender_data['justification'] = result['Justification']
    tender_data['feedback'] = feedback_text
    tender_data['sentiment'] = analyze_feedback_with_mistral(feedback_text)

    return tender_data
def analyze_supplier_submission(text: str, client_requirements: dict, feedback_text: str = None) -> dict:
    # First check if feedback indicates a blocking issue
    if feedback_text and feedback_text.strip() != "":
        criticality = assess_feedback_criticality(feedback_text)
        if criticality["is_blocking"]:
            return {
                "Score": 0, 
                "Justification": [
                    f"- Problème bloquant identifié dans le feedback: {criticality['reason']}",
                    f"- Feedback original: \"{feedback_text}\""
                ]
            }
    
    if not text.strip():
        return {"Score": 0, "Justification": ["- Description vide"]}

    extra_context = ""
    if feedback_text:
        extra_context = f"\n\nLe fournisseur a exprimé ce commentaire :\n\"{feedback_text}\".\nPrends cela en compte pour ajuster l'évaluation si pertinent."

    prompt = (
        f"Analyse ce document d'appel d'offres pour évaluer sa correspondance avec les exigences suivantes :\n"
        f"- Secteur : {client_requirements['Secteur']}\n"
        f"- Date limite souhaitée : {client_requirements['Date Limite']}\n"
        f"- Localisation souhaitée : {client_requirements['Localisation']}\n\n"
        "Critères d'évaluation :\n"
        "-Compare la date limite du tender avec la date indique par le fournisseur. Si la date limite est déjà passée , attribue un score de 0 et marque-le comme 'Expiré'. Exemple: pour un tender avec date limite 03/08/2022, et fournisseur entre: 09/04/2023 score = 0 car expiré; pour un tender avec date limite 23/04/2032, évalue normalement car la date est future."
        "- Si la date est avant ou égale à la date demandée, le score est évalué normalement.\n"
        "- La localisation différente n'est pas éliminatoire, mais une localisation exacte donne un score plus élevé.\n"
        "- Le secteur doit correspondre au mieux, selon les mots-clés et le contexte fourni."
        f"{extra_context}\n\n"
        "Retourne une note entre 0 (pas pertinent) et 100 (parfaitement pertinent), ainsi qu'une justification concise "
        "sous forme de tirets basée sur le texte fourni.\n\n"
        "Format de la réponse en JSON :\n"
        "```json\n"
        "{\n"
        "  \"Score\": note,\n"
        "  \"Justification\": [\n"
        "    \"- Raisons claires qui expliquent la note.\",\n"
        "    \"- Points forts et points faibles selon les exigences.\"\n"
        "  ]\n"
        "}\n"
        "```\n\n"
        f"Voici le texte du document à analyser :\n{text[:2000]}..."
    )

    try:
        payload = {
            "model": "mistral-medium",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.3
        }

        response = requests.post(MISTRAL_API_URL, json=payload, headers=HEADERS)
        raw_response = response.json()["choices"][0]["message"]["content"]

        # Extraction de la partie JSON
        if "```json" in raw_response:
            json_str = raw_response.split("```json")[-1].split("```")[0].strip()
        elif "```" in raw_response:
            json_str = raw_response.split("```")[1].strip()
        else:
            json_str = raw_response.strip()

        # Clean the JSON string
        json_str = json_str.replace("\n", " ").strip()
        
        # Ensure we have a valid JSON object
        if not json_str.startswith('{'):
            json_str = '{' + json_str.split('{', 1)[1]
        if not json_str.endswith('}'):
            json_str = json_str.rsplit('}', 1)[0] + '}'
            
        return json.loads(json_str)

    except Exception as e:
        print(f"Error parsing response: {str(e)}")
        print(f"Raw response: {raw_response}")
        return {"Score": 0, "Justification": [f"- Erreur lors de l'analyse : {str(e)}"]}

# Function to reanalyze tenders with user feedback
def reanalyze_tender_with_feedback(tender_data: dict, feedback_text: str, client_requirements: dict) -> dict:
    """
    Reanalyzes a tender with user feedback.
    Args:
        tender_data: Original tender data dictionary
        feedback_text: User feedback text
        client_requirements: Dictionary with client requirements
    Returns:
        Updated tender data dictionary with new score and justification
    """
    # Get the tender content - either from text or from file
    text = tender_data.get('content', '')
    
    # If no content is available, try to read from file
    if not text and 'json_path' in tender_data:
        try:
            with open(tender_data['json_path'], 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                text = json_data.get('text', '')
        except Exception as e:
            print(f"Error reading JSON file: {str(e)}")
    
    # Analyze the tender with feedback
    result = analyze_supplier_submission(text, client_requirements, feedback_text)
    
    # Update the tender data
    tender_data['score'] = result['Score']
    tender_data['justification'] = result['Justification']
    tender_data['feedback'] = feedback_text
    tender_data['sentiment'] = analyze_feedback_with_mistral(feedback_text)
    
    return tender_data

# New function to run a command-line version of the tender analyzer
def run_cli_analyzer():
    parser = argparse.ArgumentParser(description='Analyze tenders in a directory')
    parser.add_argument('tender_dir', help='Directory containing tender PDFs and their JSON extracts')
    parser.add_argument('--sector', default='Technologie', help='Required sector')
    parser.add_argument('--deadline', default='2025-05-31', help='Required deadline (YYYY-MM-DD)')
    parser.add_argument('--location', default='Paris', help='Required location')
    parser.add_argument('--top', type=int, default=5, help='Show top N results')
    parser.add_argument('--convert-only', action='store_true', help='Only convert PDFs to JSON without analysis')
    parser.add_argument('--feedback', help='Feedback text to include in analysis')
    
    args = parser.parse_args()
    
    # Validate folder path
    if not os.path.isdir(args.tender_dir):
        print(f"Error: '{args.tender_dir}' is not a valid directory")
        sys.exit(1)
    
    # If convert-only mode, just convert PDFs to JSON
    if args.convert_only:
        from pdf_extractor import process_pdf_directory
        print(f"Converting PDFs in {args.tender_dir} to JSON format...")
        results = process_pdf_directory(args.tender_dir)
        print(f"Converted {len(results)} PDF files to JSON format")
        sys.exit(0)
    
    # Create client requirements
    client_requirements = {
        "Secteur": args.sector,
        "Date Limite": args.deadline,
        "Localisation": args.location
    }
    
    # Import needed modules here to avoid circular imports
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from tender_processor import process_tender_folder, get_top_tenders
    except ImportError:
        print("Error importing tender_processor module. Make sure all files are in the same directory.")
        sys.exit(1)
    
    # Process tenders
    print(f"Processing tenders in {args.tender_dir}...")
    results = process_tender_folder(args.tender_dir, client_requirements, feedback_text=args.feedback)
    
    if not results:
        print("No tenders found or all processing failed.")
        sys.exit(1)
    
    # Get top results
    top_results = get_top_tenders(results, top_n=args.top)
    
    # Print results
    print(f"\nTop {min(args.top, len(results))} Tenders:")
    print("=" * 60)
    
    for i, result in enumerate(top_results, 1):
        print(f"{i}. Tender ID: {result['tender_id']}")
        print(f"   Score: {result['score']}")
        print(f"   PDF: {os.path.basename(result['pdf_path']) if result['pdf_path'] else 'N/A'}")
        print(f"   Sentiment: {result['sentiment'] if result['sentiment'] else 'N/A'}")
        print("   Justification:")
        for point in result['justification']:
            print(f"   {point}")
        print("-" * 60)
    
    print(f"\nTotal tenders analyzed: {len(results)}")
    
    # Return code based on whether we found any good matches
    if not results or results[0]['score'] < 50:
        print("No high-scoring tenders found.")
        sys.exit(2)  # Exit with code 2 if no good matches
    
    sys.exit(0)  # Success

if __name__ == "__main__":
    run_cli_analyzer()