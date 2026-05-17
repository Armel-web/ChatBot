import time
import streamlit as st
import fitz  # PyMuPDF
from groq import Groq

# Configuration de l'interface
st.set_page_config(page_title="Assistant IA", page_icon="📄", layout="centered")

# BARRE LATÉRALE
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key = st.text_input("Clé API Groq:", type="password", help="Récupérez votre clé sur console.groq.com")
    
    st.divider()
    
    st.subheader("Paramètres de réponse")
    mode = st.selectbox("Style de réponse:", ["Expert", "Amical", "Concis"])
    model_choice = st.selectbox("Modèle Llama:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    
    st.divider()
    
    # GESTION DE FICHIERS (PDF)
    st.subheader("📂 Documents de référence")
    uploaded_pdf = st.file_uploader("Analyser un fichier PDF (.pdf)", type=['pdf'])
    pdf_text = ""
    if uploaded_pdf:
        # Lecture du PDF via PyMuPDF
        with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
            pdf_text = ""
            for page in doc:
                pdf_text += page.get_text() # extraction du texte de chaque page
        st.success("Fichier chargé avec succès !")

    st.divider()
    
    # ACTIONS
    if st.button("🗑️ Effacer la discussion"):
        st.session_state.messages = []
        st.rerun()

st.title("💬 Assistant IA")
st.caption("Ce bot lit votre PDF et répond à vos questions en fonction de l'énoncé. Choisissez un mode de réponse et un modèle Llama pour personnaliser l'expérience.")

# Vérification de la clé API
if not api_key:
    st.warning("Veuillez entrer votre clé API Groq dans la barre latérale pour activer l'IA.", icon="⚠️")
    st.stop()

client = Groq(api_key=api_key)

# LOGIQUE DU CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrée utilisateur
if prompt := st.chat_input("Posez votre question ou faites une demande..."):
    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Préparation du prompt système (Mode + Contexte du fichier)
    system_instructions = f"Tu es un assistant {mode}. Réponds en français."
    if pdf_text:
        system_instructions += f"Voici le contenu du document PDF pour t'aider à répondre : {pdf_text}"

    # Appel à l'IA avec mesure du temps
    with st.chat_message("assistant"):
        with st.spinner("Analyse en cours..."):
            start_time = time.time() # Début du chrono
            
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instructions},
                        *st.session_state.messages
                    ],
                    model=model_choice,
                )
                
                end_time = time.time() # Fin du chrono
                response = chat_completion.choices[0].message.content
                
                # Calcul des stats
                duration = round(end_time - start_time, 2)
                word_count = len(response.split())
                
                # Affichage de la réponse
                st.markdown(response)
                
                # AFFICHAGE DES STATISTIQUES (Petit texte discret en dessous)
                st.caption(f"⏱️ Temps de réponse : {duration}s | 📝 Mots : {word_count} | 🧠 Modèle : {model_choice}")
                
                # Ajouter à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")

# OPTION D'EXPORTATION
if st.session_state.messages:
    st.divider()
    # Création du texte pour l'export
    full_chat = ""
    for msg in st.session_state.messages:
        full_chat += f"{msg['role'].upper()}: {msg['content']}\n\n"
    
    st.download_button(
        label="📥 Télécharger la discussion (TXT)",
        data=full_chat,
        file_name="mon_chat_historique.txt",
        mime="text/plain"
    )