import streamlit as st

def apply_styles():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
        .stApp {
            background-color: white;
        }
        .main-header {
            color: #0D47A1 !important;
            font-weight: bold;
            text-align: center;
            margin-top: 20px;
            font-size: 36px;
        }
        .sub-header {
            color: #388E3C !important;
            font-weight: 600;
            font-size: 24px;
        }
        .result-box {
            background-color: #F1F8E9;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #388E3C;
            margin-top: 20px;
        }
        .updated-result-box {
            background-color: #FFF8E1;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #FF9800;
            margin-top: 20px;
        }
        .form-container {
            background-color: #E3F2FD;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .home-button {
            display: block;
            width: 100%;
            font-size: 24px;
            font-weight: bold;
            padding: 30px 20px;
            border-radius: 10px;
            text-align: center;
            margin: 10px 0;
            cursor: pointer;
            border: none;
        }
        .supplier-button {
            background-color: #0D47A1;
            color: #fcfcfc !important;
        }
        .client-button {
            background-color: #57c95c;
            color: #fcfcfc!important;
        }
        .home-button:hover {
            opacity: 0.9;
        }
        .center-block {
            margin-top: 30px;
        }
        .stButton>button {
            background-color: #88ace3;
            color: #fcfcfc !important;
            font-weight: bold;
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
        }
        .logo-container {
            display: flex;
            justify-content: center;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .textra-logo {
            font-size: 50px;
            font-weight: bold;
            text-align: center;
        }
        .textra-blue {
            color: #007BFF !important;
        }
        .textra-green {
            color: #5b6b5c !important;
        }
        .nav-button {
            display: inline-block;
            background-color: #E3F2FD;
            color: #0D47A1 !important;
            padding: 10px 20px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 20px;
            font-weight: bold;
            cursor: pointer;
            border: none;
        }
        p, h1, h2, h3, span, label, div {
            color: #333333 !important;
        }
        .stSuccess {
            color: #1B5E20 !important;
        }
        .stWarning {
            color: #FF6F00 !important;
        }
        .stInfo {
            color: #01579B !important;
        }
        .score-comparison {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        .old-score {
            text-decoration: line-through;
            color: #757575 !important;
        }
        .new-score {
            font-weight: bold;
            color: #FF5722 !important;
        }
        .feedback-sentiment {
            padding: 5px 10px;
            border-radius: 15px;
            display: inline-block;
            font-weight: bold;
            margin-top: 5px;
        }
        .sentiment-negative {
            background-color: #FFEBEE;
            color: #C62828 !important;
        }
        .sentiment-positive {
            background-color: #E8F5E9;
            color: #2E7D32 !important;
        }
        .sentiment-neutral {
            background-color: #ECEFF1;
            color: #455A64 !important;
        }
        /* Style pour la barre de sélection des PDF */
        div[data-baseweb="select"] > div {
            background-color: white !important;
            color: #333333 !important;
        }
        div[data-baseweb="select"] span {
            color: #333333 !important;
        }
        div[data-baseweb="select"] svg {
            color: #333333 !important;
        }
        div[data-baseweb="popover"] div {
            background-color: white !important;
            color: #333333 !important;
        }
        div[data-baseweb="select-option"] {
            background-color: white !important;
        }
        div[data-baseweb="select-option"]:hover {
            background-color: #E3F2FD !important;
        }
    </style>
    """, unsafe_allow_html=True)

def display_logo():
    """Display the Textra logo"""
    st.markdown(
        """
        <div class="logo-container">
            <h1 class="textra-logo">
                <span class="textra-blue">Textra</span>
                <span class="textra-green">Tender</span>
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )