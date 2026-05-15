import time
import streamlit as st
from groq import Groq

# Configuration de l'interface
st.set_page_config(page_title="Assistant IA", page_icon="🚀", layout="wide")

# BARRE LATÉRALE
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key = st.text_input("Clé API Groq:", type="password", help="Récupérez votre clé sur console.groq.com")
    
    st.divider()
    
    st.subheader("Paramètres de réponse")
    mode = st.selectbox("Style de réponse:", ["Expert", "Amical", "Concis"])
    model_choice = st.selectbox("Modèle Llama:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    
    st.divider()
    
    # GESTION DE FICHIERS
    st.subheader("📂 Documents de référence")
    uploaded_file = st.file_uploader("Analyser un fichier texte (.txt)", type=['txt'])
    file_context = ""
    if uploaded_file:
        file_context = uploaded_file.read().decode("utf-8")
        st.success("Fichier chargé avec succès !")

    st.divider()
    
    # ACTIONS
    if st.button("🗑️ Effacer la discussion"):
        st.session_state.messages = []
        st.rerun()

st.title("💬 Assistant IA")
st.caption("Projet Python | Streamlit | Groq Cloud | Llama 3.3")

# Vérification de la clé API
if not api_key:
    st.warning("Veuillez entrer votre clé API Groq dans la barre latérale pour activer l'IA.", icon="⚠️")
    st.stop()

client = Groq(api_key=api_key)

# LOGIQUE DU CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrée utilisateur
if prompt := st.chat_input("Posez votre question..."):
    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Préparation du prompt système (Mode + Contexte du fichier)
    system_instructions = f"Tu es un assistant {mode}. Réponds en français."
    if file_context:
        system_instructions += f"\nContexte important issu du document fourni : {file_context}"

    # Appel à l'IA avec mesure du temps
    with st.chat_message("assistant"):
        with st.spinner("Réflexion en cours..."):
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