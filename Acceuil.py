import json
import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, time
from pathlib import Path
import tempfile

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import io

from auth import auth_interface, check_session, initialize_app, login_form
from tender_processor import create_results_dataframe, get_top_tenders, process_tender_folder
from main import reanalyze_tender_with_feedback  # Import the new function

# Load environment variables - Uncomment this if you have dotenv installed
# from dotenv import load_dotenv
# load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Textra - Plateforme de Tenders",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* Couleur de fond de la sidebar */
    section[data-testid="stSidebar"] {
        background-color: #e0f0ff;
    }

    /* Texte dans la sidebar */
    section[data-testid="stSidebar"] .css-10trblm {
        color: #003366;
    }

    /* Élément actif dans la sidebar */
    .css-1d391kg.e1g8pov64 {
        background-color: #cce5ff !important;
        color: #003366 !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Apply custom CSS from templates
from templates import apply_styles, display_logo
apply_styles()

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'original_results' not in st.session_state:
    st.session_state.original_results = None
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = {}
if 'results' not in st.session_state:
    st.session_state.results = None
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'top_results' not in st.session_state:
    st.session_state.top_results = None
if 'client_requirements' not in st.session_state:
    st.session_state.client_requirements = None
if 'current_tender_id' not in st.session_state:
    st.session_state.current_tender_id = None
if 'current_tender_info' not in st.session_state:
    st.session_state.current_tender_info = None

def home_page():
    display_logo()

    # Description
    st.markdown("""
    <div style='font-size:22px; line-height:1.8; color:#333; text-align:center; margin-bottom:30px;'>
    Une plateforme intelligente pour l'accompagnement de l'analyse des appels d'offre jusqu'à la soumission des candidatures.
    </div>
    """, unsafe_allow_html=True)

    # Créer deux colonnes pour les boutons avec un peu d'espace entre eux
    col1, space, col2 = st.columns([4, 1, 4])
    with col1:
        # Button for Fournisseur (Supplier) - gray
        if st.button("ESPACE FOURNISSEUR", key="fournisseur_btn", use_container_width=True, help="Accédez à l'espace fournisseur"):
            st.session_state.page = 'fournisseur'
            st.rerun()
    with col2:
        # Button for Client - blue
        if st.button("ESPACE CLIENT", key="client_btn", use_container_width=True, help="Accédez à l'espace client"):
            st.session_state.page = 'client'
            st.rerun()

    st.markdown("<hr style='margin-top:40px; margin-bottom:40px;'>", unsafe_allow_html=True)

    # SECTION: Comment ça fonctionne (with custom styling)
    st.markdown("<h2 style='color:#1E88E5; font-size:32px; padding-bottom:10px; border-bottom:2px solid #1E88E5;'>Comment ça fonctionne</h2>", unsafe_allow_html=True)
    
    st.markdown("<div style='padding:20px 0;'></div>", unsafe_allow_html=True)
    
    step1, step2 = st.columns(2)
    with step1:
        st.markdown("""
        <div class="feature-box">
            <h3 style="color:#1E88E5;">Déposez votre appel d'offres</h3>
            <p style="font-size:18px;">Téléversez vos documents sur notre plateforme sécurisée.</p>
        </div>
        """, unsafe_allow_html=True)
    with step2:
        st.markdown("""
        <div class="feature-box">
            <h3 style="color:#1E88E5;">Analyse automatisée</h3>
            <p style="font-size:18px;">Nos modèles analysent vos documents avec précision.</p>
        </div>
        """, unsafe_allow_html=True)

    step3, step4 = st.columns(2)
    with step3:
        st.markdown("""
        <div class="feature-box">
            <h3 style="color:#1E88E5;">Recevez des insights</h3>
            <p style="font-size:18px;">Obtenez des rapports détaillés, clairs et pertinents.</p>
        </div>
        """, unsafe_allow_html=True)
    with step4:
        st.markdown("""
        <div class="feature-box">
            <h3 style="color:#1E88E5;">Décidez en toute confiance</h3>
            <p style="font-size:18px;">Bénéficiez d'analyses stratégiques pour vos décisions.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin-top:40px; margin-bottom:40px;'>", unsafe_allow_html=True)

    # SECTION: Les avantages de Textra Tender (in a different color)
    st.markdown("<h2 style='color:#4CAF50; font-size:32px; padding-bottom:10px; border-bottom:2px solid #4CAF50;'>Les avantages de Textra</h2>", unsafe_allow_html=True)
    
    st.markdown("<div style='padding:20px 0;'></div>", unsafe_allow_html=True)
    
    colA, colB = st.columns(2)
    with colA:
        st.markdown("""
        <div class="advantage-box">
            <h3 style="color:#4CAF50;">Gain de temps</h3>
            <p style="font-size:18px;">Automatisez jusqu'à 80 % du processus d'analyse.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="advantage-box">
            <h3 style="color:#4CAF50;">Économies</h3>
            <p style="font-size:18px;">Ciblez les meilleures opportunités au meilleur coût.</p>
        </div>
        """, unsafe_allow_html=True)
    with colB:
        st.markdown("""
        <div class="advantage-box">
            <h3 style="color:#4CAF50;">Analyse intelligente</h3>
            <p style="font-size:18px;">Profitez de l'IA pour extraire des informations clés.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="advantage-box">
            <h3 style="color:#4CAF50;">Avantage concurrentiel</h3>
            <p style="font-size:18px;">Restez toujours une longueur d'avance.</p>
        </div>
        """, unsafe_allow_html=True)

    # Additional styling for buttons and boxes
    st.markdown("""
    <style>
        /* Styles pour les boutons */
        [data-testid="stButton"] button {
            height: 80px;
            font-size: 24px;
            font-weight: bold;
            color: white !important;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        [data-testid="stButton"] button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
        
        /* Couleurs spécifiques pour chaque bouton */
        button[title="Accédez à l'espace fournisseur"] {
            background-color: #757575 !important; /* Gris */
            border: none;
        }
        
        button[title="Accédez à l'espace client"] {
            background-color: #1E88E5 !important; /* Bleu */
            border: none;
        }
        
        /* Styles pour les boîtes de fonctionnalités et avantages */
        .feature-box, .advantage-box {
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            background-color: #f9f9f9;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .feature-box:hover, .advantage-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .feature-box h3, .advantage-box h3 {
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .main-header {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            background: linear-gradient(45deg, #1E88E5, #4CAF50);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)


def fournisseur_page():
    # Navigation button
    if st.button("← Retour à l'accueil", key="home_return_btn"):
        st.session_state.page = 'home'
        st.rerun()
    
    # Display logo
    display_logo()
    st.markdown('<h1 class="main-header">Analyse des Tenders Fournisseurs</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>Entrez vos <strong>critères</strong> ci-dessous puis cliquez sur <em>Analyser</em> pour trouver les tenders correspondants.</p>", unsafe_allow_html=True)

    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    with st.form("supplier_form"):
        st.markdown('<h3 class="sub-header">Vos critères</h3>', unsafe_allow_html=True)

        st.subheader("Exigences du Fournisseur")
        sector = st.text_input("Secteur", "Technologie")
        deadline = st.date_input("Date Limite", datetime.now())
        location = st.text_input("Localisation", "Paris")

        supplier_type = st.selectbox(
            "Type d'entreprise",
            ["PME", "Startup", "Grande entreprise", "Indépendant", "Organisation publique"]
        )
        legal_form = st.selectbox(
            "Forme juridique",
            ["SARL", "SA", "SAS", "Auto-entrepreneur", "Coopérative", "Association", "Autre"]
        )
        activity_scope = st.selectbox(
            "Zone d'activité principale",
            ["Locale", "Régionale", "Nationale", "Internationale"]
        )

        # Submission button
        submitted = st.form_submit_button("Lancer l'analyse")
        if submitted:
            st.success("Critères soumis avec succès !")
    
    # Folder path input section
    folder_path = "tenders"
    
    
    # Check if folder path exists
    if folder_path and not os.path.isdir(folder_path):
        st.error(f"Le dossier '{folder_path}' n'existe pas. Veuillez vérifier le chemin.")

    # Main content area
    tab1, tab2 = st.tabs(["Résultats", "Détails"])

    # Process the folder files
    if folder_path and submitted and os.path.isdir(folder_path):
        with st.spinner("Traitement des fichiers en cours..."):
            # Create client requirements dictionary
            client_requirements = {
                "Secteur": sector,
                "Date Limite": deadline.strftime("%Y-%m-%d"),
                "Localisation": location
            }
            
            # Process the tenders
            results = process_tender_folder(folder_path, client_requirements)
            
            # Get top results
            top_results = get_top_tenders(results, top_n=5)
            
            # Create DataFrame for display
            results_df = create_results_dataframe(results)
            
            # Store results in session state
            st.session_state.results = results
            st.session_state.results_df = results_df
            st.session_state.top_results = top_results
            st.session_state.original_results = results  # Store original results
            st.session_state.client_requirements = client_requirements  # Store requirements for reanalysis

    # Display results
    with tab1:
        if 'results_df' in st.session_state and st.session_state.results_df is not None and not st.session_state.results_df.empty:
            st.subheader("Top 5 Appels d'Offres")
            
            # Display top results as a table
            st.dataframe(
                st.session_state.results_df.head(5)[['Tender ID', 'Score', 'Sentiment']], 
                use_container_width=True
            )
            
            # Show select box for viewing detailed results
            if not st.session_state.results_df.empty:
                selected_tender_id = st.selectbox(
                    "Sélectionner un appel d'offres pour voir les détails",
                    options=st.session_state.results_df['Tender ID'].tolist(),
                    key="initial_results_selectbox"
                )
                
                # Get selected tender details
                selected_tender = next(
                    (item for item in st.session_state.results if item['tender_id'] == selected_tender_id), 
                    None
                )
                
                if selected_tender:
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader(f"Détails de l'offre: {selected_tender_id}")
                        st.write(f"*Score:* {selected_tender['score']}")
                        
                        # Display sentiment with color
                        sentiment = selected_tender.get('sentiment', 'N/A')
                        sentiment_color = {
                            'positif': 'green',
                            'négatif': 'red',
                            'neutre': 'gray'
                        }.get(sentiment, 'black')
                        
                        st.markdown(f"*Sentiment:* <span style='color:{sentiment_color}'>{sentiment}</span>", 
                                    unsafe_allow_html=True)
                        
                        st.subheader("Justification:")
                        for point in selected_tender['justification']:
                            st.write(point)
                        
                        # Add feedback section with a form
                        st.subheader("Soumettre un Feedback")
                        
                        # Check if feedback was already submitted for this tender
                        already_submitted = selected_tender_id in st.session_state.feedback_submitted
                        
                        if already_submitted:
                            st.success("Votre feedback a été pris en compte et l'offre a été réévaluée.")
                            
                            # Option to submit new feedback
                            if st.button("Soumettre un nouveau feedback", key=f"new_feedback_{selected_tender_id}"):
                                # Reset feedback submitted status for this tender
                                st.session_state.feedback_submitted.pop(selected_tender_id, None)
                                st.rerun()
                        else:
                            # Feedback form
                            with st.form(key=f"feedback_form_{selected_tender_id}"):
                                st.write("Partagez votre feedback sur cette offre :")
                                feedback = st.text_area(
                                    "Décrivez tout problème ou préoccupation concernant cette offre",
                                    placeholder="Exemple: Les délais proposés sont irréalistes pour ce type de projet..."
                                )
                                
                                feedback_submitted = st.form_submit_button("Soumettre le feedback")
                                
                                if feedback_submitted and feedback.strip():
                                    with st.spinner("Analyse du feedback et réévaluation de l'offre..."):
                                        # Re-analyze tender with feedback
                                        updated_tender = reanalyze_tender_with_feedback(
                                            selected_tender,
                                            feedback,
                                            st.session_state.client_requirements
                                        )
                                        
                                        # Update tender in results
                                        for i, tender in enumerate(st.session_state.results):
                                            if tender['tender_id'] == selected_tender_id:
                                                st.session_state.results[i] = updated_tender
                                                break
                                        
                                        # Update dataframe
                                        st.session_state.results_df = create_results_dataframe(st.session_state.results)
                                        
                                        # Get top results again
                                        st.session_state.top_results = get_top_tenders(st.session_state.results, top_n=5)
                                        
                                        # Mark feedback as submitted for this tender
                                        st.session_state.feedback_submitted[selected_tender_id] = True
                                        
                                        st.success("Feedback soumis avec succès! L'offre a été réévaluée.")
                                        st.rerun()
                        
                        # Ajout du bouton "Créer la candidature" en dessous du feedback
                        st.markdown("###  Candidature")
                        if st.button(" Créer la candidature", key=f"create_application_{selected_tender_id}"):
                            # Store the selected tender info in session state
                            st.session_state.current_tender_id = selected_tender_id
                            st.session_state.current_tender_info = selected_tender
                            st.session_state.page = 'candidature'
                            st.rerun()
                    
                    with col2:
                        st.subheader("Document PDF Original")
                        pdf_path = selected_tender.get('pdf_path')
                        if pdf_path and os.path.exists(pdf_path):
                            display_pdf(pdf_path)
                        else:
                            st.error("PDF non disponible pour cette offre")
        else:
            st.info("Téléchargez des fichiers et cliquez sur 'Analyser les Appels d'Offres' pour voir les résultats")

    # Details tab - show all results
    with tab2:
        st.subheader("Tous les Résultats")
        
        if 'results_df' in st.session_state and st.session_state.results_df is not None and not st.session_state.results_df.empty:
            # Add a button to reset feedback and scores
            if st.button("Réinitialiser tous les feedbacks et scores", key="reset_all"):
                if st.session_state.original_results:
                    st.session_state.results = st.session_state.original_results.copy()
                    st.session_state.results_df = create_results_dataframe(st.session_state.results)
                    st.session_state.top_results = get_top_tenders(st.session_state.results, top_n=5)
                    st.session_state.feedback_submitted = {}
                    st.success("Toutes les évaluations ont été réinitialisées.")
                    st.rerun()
            
            st.dataframe(st.session_state.results_df, use_container_width=True)
            
            # Export results option
            csv = st.session_state.results_df.to_csv(index=False)
            st.download_button(
                label="Télécharger les résultats (CSV)",
                data=csv,
                file_name="resultats_appels_offres.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucun résultat disponible")

def client_page():
    # Navigation button
    if st.button("← Retour à l'accueil", key="home_return_client_btn"):
        st.session_state.page = 'home'
        st.rerun()
    
    # Display logo
    display_logo()
    st.markdown('<h1 class="main-header"> Espace Client</h1>', unsafe_allow_html=True)
    
    st.info("L'espace client est en cours de développement. Revenez bientôt pour accéder à cette fonctionnalité.")

# Fonction pour récupérer les documents requis à partir du JSON du tender
def get_required_documents(tender_id, folder_path="C:/Users/PC-1/Desktop/Aya/tenders"):
    json_file = os.path.join(folder_path, f"{tender_id}.json")
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            tender_data = json.load(f)
            return tender_data.get("Documents_requis", []), tender_data
    else:
        return [], {}

# Fonction pour générer un modèle de document
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import io

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import io

   
# Fonction principale pour la page de candidature
   




import json
import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, time
from pathlib import Path
import tempfile
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm, mm, inch

from tender_processor import create_results_dataframe, get_top_tenders, process_tender_folder
from main import reanalyze_tender_with_feedback

def generate_document_template_pdf(doc_type, company_info, output_path=None):
    """
    Génère un modèle de document PDF pour les appels d'offres en utilisant Groq LLM.
    
    Args:
        doc_type (str): Type de document à générer
        company_info (dict): Informations sur l'entreprise
        output_path (str, optional): Chemin de sortie pour le fichier PDF. 
                                    Si None, retourne le contenu en bytes.
    
    Returns:
        bytes ou None: Contenu du document en bytes si output_path est None, sinon None
    """
    # Importer la bibliothèque Groq
    try:
        from groq import Groq
    except ImportError:
        # Si groq n'est pas installé, essayons d'installer
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
        from groq import Groq
    
    # Initialiser le client Groq
    # Utilisez votre propre clé API Groq ici
    groq_api_key = os.environ.get("GROQ_API_KEY", "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")
    if not groq_api_key:
        # Vérifier si la clé d'API est définie - sinon utiliser une simulation
        print("Attention: Clé API Groq non trouvée. Mode simulation activé.")
        
    else:
        # Préparer le client et le prompt pour Groq
        client = Groq(api_key=groq_api_key)
        prompt = create_prompt_for_document(doc_type, company_info)
        
        # Obtenir la réponse de Groq
        try:
            response = client.chat.completions.create(
                model="llama3-70b-8192",  # Ou autre modèle de Groq selon disponibilité
                messages=[
                    {"role": "system", "content": "Vous êtes un expert juridique spécialisé dans les appels d'offres. Vous allez générer un document administratif français en respectant strictement le format et les normes légales."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Valeur basse pour être plus précis et formel
                max_tokens=4096
            )
            content = response.choices[0].message.content
        except Exception as e:
            print(f"Erreur lors de l'appel à Groq API: {e}")
            # En cas d'erreur, utiliser la génération simulée de contenu
            
    
    # Créer un PDF à partir du contenu généré
    buffer = io.BytesIO()
    pdf_path = output_path if output_path else buffer
    
    pdf = create_pdf_from_content(content, doc_type, company_info, pdf_path)
    
    # Si aucun chemin de sortie n'est spécifié, retourner le contenu du buffer
    if not output_path:
        buffer.seek(0)
        return buffer.getvalue()
    return None


def create_prompt_for_document(doc_type, company_info):
    """
    Crée un prompt spécifique pour le type de document demandé.
    """
    today = datetime.now().strftime("%d/%m/%Y")
    
    base_prompt = f"""
    Générez un document administratif français de type "{doc_type}" en utilisant les informations d'entreprise suivantes:
    
    - Nom de l'entreprise: {company_info['name']}
    - Représentant légal: {company_info['representative']}
    - Numéro SIRET: {company_info['siret']}
    - Adresse: {company_info['address']}
    - Forme juridique: {company_info['legal_form']}
    - Capital social: {company_info['capital']} €
    - Date de création: {company_info['creation_date']}
    - Effectif: {company_info['employees']} employés
    - Chiffre d'affaires des 3 dernières années: {company_info['turnover_y1']}, {company_info['turnover_y2']}, {company_info['turnover_y3']}
    
    Date du jour: {today}
    
    Le document doit être complet, structuré et conforme aux normes légales françaises pour les marchés publics.
    """
    
    # Ajouter des informations spécifiques selon le type de document
    if "DC1" in doc_type:
        base_prompt += """
        Pour la Lettre de candidature (DC1), incluez:
        1. Les informations d'identification du pouvoir adjudicateur et du candidat
        2. L'objet de la consultation
        3. L'engagement du candidat
        4. L'identification des membres du groupement (si applicable)
        5. La désignation du mandataire (si applicable)
        6. La signature du représentant habilité
        """
    elif "DC2" in doc_type:
        base_prompt += """
        Pour la Déclaration du candidat (DC2), incluez:
        1. L'identification du candidat
        2. Les renseignements relatifs à la situation financière
        3. Les renseignements relatifs aux moyens et références
        4. Les renseignements relatifs à l'aptitude à exercer l'activité
        5. Les capacités économiques, financières et techniques
        6. La déclaration sur l'honneur
        """
    elif "assurance" in doc_type.lower():
        base_prompt += """
        Pour l'Attestation d'assurance, incluez:
        1. Les informations de l'assureur
        2. La période de validité
        3. Les garanties couvertes
        4. Les montants de couverture
        5. La certification de l'assureur
        """
    elif "kbis" in doc_type.lower():
        base_prompt += """
        Pour l'Extrait Kbis, incluez:
        1. Les informations d'identification de l'entreprise
        2. La date d'immatriculation
        3. Le numéro RCS
        4. Les activités principales
        5. Les mentions légales essentielles
        """
    elif "fiscale" in doc_type.lower():
        base_prompt += """
        Pour l'Attestation fiscale, incluez:
        1. La déclaration de régularité fiscale
        2. Les références aux articles du code général des impôts
        3. L'engagement de paiement des impôts et taxes
        4. La période concernée
        """
    elif "sociale" in doc_type.lower():
        base_prompt += """
        Pour l'Attestation sociale, incluez:
        1. La déclaration de régularité sociale
        2. Les références aux organismes sociaux (URSSAF, etc.)
        3. L'engagement de paiement des cotisations
        4. La période concernée
        """
    elif "référence" in doc_type.lower():
        base_prompt += """
        Pour les Références similaires, incluez:
        1. Un tableau des principales références sur les 3 dernières années
        2. Pour chaque référence: client, période, montant, description
        3. Les coordonnées de contact pour vérification
        4. Les certifications ou qualifications obtenues
        """
    
    base_prompt += """
    Formatez le document de manière professionnelle et prêt à l'emploi. N'incluez pas de notes explicatives ou de commentaires en dehors du contenu du document lui-même.
    """
    
    return base_prompt

def create_pdf_from_content(content, doc_type, company_info, output_path):
    """
    Crée un fichier PDF à partir du contenu généré.
    """
    # Déterminer si output_path est un chemin fichier ou un buffer
    is_buffer = not isinstance(output_path, str)
    
    # Créer le document PDF
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=A4,
        rightMargin=72, 
        leftMargin=72,
        topMargin=72, 
        bottomMargin=72
    )
    
    # Styles pour le document
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        spaceAfter=20,
        fontSize=16,
        textColor=colors.HexColor("#1E88E5")  # Bleu
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        alignment=TA_LEFT,
        spaceAfter=12,
        fontSize=14,
        textColor=colors.HexColor("#4CAF50")  # Vert
    )
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14
    heading_style = styles['Heading2']
    
    # Éléments du document
    elements = []
    
    # En-tête avec informations de l'entreprise
    elements.append(Paragraph(f"{doc_type.upper()}", title_style))
    elements.append(Spacer(1, 20))
    
    # Information sur l'entreprise
    company_info_table_data = [
        [Paragraph(f"<b>{company_info['name']}</b>", normal_style), 
         Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", normal_style)],
        [Paragraph(f"{company_info['address']}", normal_style), ""],
        [Paragraph(f"SIRET: {company_info['siret']}", normal_style), ""],
        [Paragraph(f"Représentant: {company_info['representative']}", normal_style), ""]
    ]
    
    company_info_table = Table(company_info_table_data, colWidths=[300, 150])
    company_info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(company_info_table)
    elements.append(Spacer(1, 20))
    
    # Ajouter une ligne de séparation
    elements.append(Paragraph("<hr width='100%'/>", normal_style))
    elements.append(Spacer(1, 20))
    
    # Contenu principal - diviser en paragraphes
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if para.strip():
            if para.strip().isupper() or para.strip().endswith(':'):
                elements.append(Paragraph(para, subtitle_style))
            else:
                elements.append(Paragraph(para, normal_style))
            elements.append(Spacer(1, 8))
    
    # Ajouter un espace pour la signature si nécessaire
    if "DC1" in doc_type or "DC2" in doc_type or "attestation" in doc_type.lower():
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Fait à _________________, le " + datetime.now().strftime("%d/%m/%Y"), normal_style))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Signature du représentant habilité:", normal_style))
        elements.append(Spacer(1, 60))  # Espace pour la signature
        elements.append(Paragraph(company_info['representative'], normal_style))
    
    # Générer le PDF
    doc.build(elements)
    return doc

def application_page(tender_id, tender_info):
    # Navigation button
    if st.button("← Retour aux résultats", key="home_return_application_btn"):
        st.session_state.page = 'fournisseur'
        st.rerun()
        
    display_logo()
    st.markdown(f'<h1 class="main-header">Préparation de Candidature</h1>', unsafe_allow_html=True)
    
    # Afficher les informations de l'appel d'offres
    
    
    required_docs, tender_json_data = get_required_documents(tender_id)
    
    tender_title = tender_json_data.get('title', tender_info.get('title') if tender_info else 'Inconnu')
    tender_deadline = tender_json_data.get('deadline', tender_info.get('deadline') if tender_info else 'Non spécifiée')
    tender_client = tender_json_data.get('acheteur', tender_info.get('acheteur') if tender_info else 'Non spécifié')
    
   
 
    
    if not required_docs:
        
        required_docs = [
            "Lettre de candidature et d'habilitation (DC1)",
            "Déclaration du candidat (DC2)",
            "Attestation d'assurance",
            "Extrait Kbis",
            "Attestation fiscale",
            "Attestation sociale",
            "Références similaires"
        ]
        st.info("Des documents standard ont été proposés par défaut.")
    
    # Formulaire pour les informations de l'entreprise
    st.markdown("###  Informations sur l'entreprise")
    
    # Utiliser des colonnes pour une mise en page plus compacte
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("Nom de l'entreprise", key="company_name")
        representative = st.text_input("Nom du représentant légal", key="representative")
        siret = st.text_input("Numéro SIRET", key="siret")
        address = st.text_area("Adresse", key="address", height=100)
        
    with col2:
        legal_form = st.selectbox(
            "Forme juridique",
            ["SARL", "SAS", "SA", "EURL", "Auto-entrepreneur", "Autre"],
            key="legal_form"
        )
        capital = st.text_input("Capital social (€)", key="capital")
        creation_date = st.date_input("Date de création de l'entreprise", key="creation_date").strftime("%d/%m/%Y")
        employees = st.text_input("Nombre d'employés", key="Nombre d'employést")
    
    # Informations financières
    st.markdown("###  Informations financières")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        turnover_y1 = st.text_input(f"CA {datetime.now().year - 1} (€)", key="turnover_y1")
    with col2:
        turnover_y2 = st.text_input(f"CA {datetime.now().year - 2} (€)", key="turnover_y2")
    with col3:
        turnover_y3 = st.text_input(f"CA {datetime.now().year - 3} (€)", key="turnover_y3")
    
    # Rassembler toutes les infos de l'entreprise
    company_info = {
        'name': company_name,
        'representative': representative,
        'siret': siret,
        'address': address,
        'legal_form': legal_form,
        'capital': capital,
        'creation_date': creation_date,
        'employees': str(employees),
        'turnover_y1': turnover_y1,
        'turnover_y2': turnover_y2,
        'turnover_y3': turnover_y3,
    }
    
    # Vérifier si tous les champs sont remplis
    all_fields_filled = all(company_info.values())
    
    st.markdown("---")
    
    st.markdown("###  Documents à générer")
    
    # Si tous les champs sont remplis, permettre la génération de documents
    if all_fields_filled:
        # Interface pour la génération et la prévisualisation des documents
        doc_col1, doc_col2 = st.columns([2, 1])
        
        with doc_col1:
            selected_doc = st.selectbox(
                "Choisir un document à générer", 
                required_docs,
                key="selected_doc"
            )
            
            st.markdown("*Cliquez sur le bouton pour générer et prévisualiser le document*")
            
            if st.button(" Générer et prévisualiser", key="preview_btn"):
                with st.spinner("Génération du document en cours..."):
                    # Générer le document sans l'enregistrer
                    pdf_bytes = generate_document_template_pdf(selected_doc, company_info)
                    
                    # Stocker les bytes PDF dans la session state pour prévisualisation et téléchargement
                    st.session_state.preview_pdf = pdf_bytes
                    st.session_state.preview_doc_name = selected_doc
                    
                    st.success(f"Document '{selected_doc}' généré avec succès!")
        
        with doc_col2:
            # Option pour télécharger le document prévisualisé
            if 'preview_pdf' in st.session_state and st.session_state.preview_pdf:
                st.download_button(
                    label="⬇️ Télécharger le PDF",
                    data=st.session_state.preview_pdf,
                    file_name=f"{st.session_state.preview_doc_name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key="download_pdf_btn"
                )
        
        # Prévisualisation du PDF généré
        if 'preview_pdf' in st.session_state and st.session_state.preview_pdf:
            st.markdown("### Prévisualisation du document")
            # Convertir les bytes PDF en base64 pour l'affichage
            base64_pdf = base64.b64encode(st.session_state.preview_pdf).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
              
    else:
        st.warning("🛈 Veuillez remplir toutes les informations de l'entreprise pour générer les documents.")
    
    # Ajouter des styles CSS pour améliorer l'apparence
    st.markdown("""
    <style>
    .main-header {
        color: #1E88E5;
        text-align: center;
        margin-bottom: 30px;
    }
    
    h3 {
        color: #4CAF50;
        margin-top: 30px;
        margin-bottom: 20px;
        padding-bottom: 5px;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .stButton button {
        width: 100%;
        padding: 10px;
        font-weight: bold;
    }
    
    .stTextInput, .stTextArea, .stSelectbox, .stSlider {
        padding: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)
# Function to display PDF
def display_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Main app logic - determine which page to show
def main():
    # Initialize the app
    initialize_app()

    # Check login status
    if not check_session():
        # Show login/signup only if not logged in
        auth_interface()
    else:
        # User is logged in, show appropriate page
        if st.session_state.page == 'home':
            home_page()
        elif st.session_state.page == 'fournisseur':
            fournisseur_page()
        elif st.session_state.page == 'client':
            client_page()
        elif st.session_state.page == 'candidature':
            application_page(st.session_state.current_tender_id, st.session_state.current_tender_info)

   
if __name__ == "__main__":
    main()
