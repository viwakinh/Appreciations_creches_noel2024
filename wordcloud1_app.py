import streamlit as st
import io  # Pour manipuler BytesIO
import qrcode
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json  # Pour sauvegarder et charger les mots
import os  # Pour vérifier l'existence du fichier
import time  # Pour le rafraîchissement automatique

# Configuration de la page
st.set_page_config(page_title="Nuage de mots en direct", layout="wide")

# Fichier pour stocker les mots soumis
WORDS_FILE = os.path.join(os.path.dirname(__file__), "words.json")

# Liste de mots présélectionnés
PRESELECTED_WORDS = [
    " ", "Ingénieuse", "Innovante", "Imaginative", 
    "Originale", "Éblouissante", "Impressionnante", "Inspirée"
]

# Fonction pour charger les mots depuis un fichier JSON
def load_words():
    if not os.path.exists(WORDS_FILE):  # Vérifie si le fichier n'existe pas
        with open(WORDS_FILE, "w") as file:
            json.dump([], file)  # Crée un fichier vide avec une liste
    try:
        with open(WORDS_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

# Fonction pour sauvegarder les mots dans un fichier JSON
def save_words(words):
    with open(WORDS_FILE, "w") as file:
        json.dump(words, file)

# Charger les mots au démarrage
if 'word_list' not in st.session_state:
    st.session_state.word_list = load_words()

# Suivi des participants
if 'has_participated' not in st.session_state:
    st.session_state.has_participated = False

# URL de l'application pour les participants
url_wordcloud = "https://vote-reunion.streamlit.app"

# Génération du QR Code pour les participants
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=5,
    border=2
)
qr.add_data(url_wordcloud)
qr.make(fit=True)
qr_image = qr.make_image(fill_color="black", back_color="white")

# Conversion de l'image en BytesIO pour Streamlit
buffer = io.BytesIO()
qr_image.save(buffer, format="PNG")
buffer.seek(0)

# Affichage du QR Code dans Streamlit
st.title("Nuage de mots en direct")
st.subheader("Scannez le QR Code ci-dessous pour accéder au nuage de mots")
st.image(buffer, caption="Scannez et entrez vos mots", width=200)

# Section d'entrée de mots
st.subheader("Partagez un mot pour décrire ce que vous pensez des crèches")

# Ajout de sélection de mots présélectionnés
new_word = st.selectbox(
    "Choisissez un mot dans la liste",
    PRESELECTED_WORDS,
    index=0
)

# Authentification pour affichage du nuage
st.sidebar.subheader("Authentification administrateur")
admin_code = st.sidebar.text_input("Entrez le code administrateur :", type="password")

# Clé administrateur (définissez votre code)
ADMIN_CODE = "2018"  # Remplacez par votre propre code

# Soumission des mots
if st.button("Soumettre"):
    if admin_code == ADMIN_CODE:  # Si c'est l'administrateur, il peut voter plusieurs fois
        if new_word.strip() != "":
            word_list = load_words()
            word_list.append(new_word.lower())
            save_words(word_list)
            st.success("Le mot a été ajouté par l'administrateur.")
        else:
            st.warning("Veuillez sélectionner un mot avant de soumettre.")
    else:  # Si c'est un participant normal
        if st.session_state.has_participated:
            st.warning("Vous avez déjà soumis un mot. Merci de votre participation !")
        else:
            if new_word.strip() != "":
                word_list = load_words()
                word_list.append(new_word.lower())
                save_words(word_list)
                st.success("Merci pour votre mot !")
                st.session_state.has_participated = True  # Marque la participation
            else:
                st.warning("Veuillez sélectionner un mot avant de soumettre.")

# Affichage dynamique du nuage de mots uniquement pour l'administrateur
if admin_code == ADMIN_CODE:  # ADMIN_CODE défini comme 2018
    st.subheader("Nuage de mots en direct")
    word_list = load_words()  # Recharger les mots à chaque rafraîchissement

    if word_list:
        # Créer le texte pour le nuage de mots à partir des mots soumis
        wordcloud_text = " ".join(word_list)
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(wordcloud_text)

        # Afficher le nuage de mots
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.write("Le nuage de mots apparaîtra ici lorsque les participants auront soumis leurs mots.")
else:
    if admin_code:  # Vérifie si un code a été saisi
        st.subheader("Nuage de mots")
        st.write("⚠️ Le nuage de mots est réservé à l'administrateur. Veuillez entrer le code administrateur dans la barre latérale.")

# Fonction pour réinitialiser les mots et l'état des participants
def reset_words():
    # Vider la liste des mots et mettre à jour le fichier
    st.session_state.word_list = []
    save_words([])  # Écrire une liste vide dans le fichier JSON
    # Réinitialiser l'état de participation pour tous
    if 'has_participated' in st.session_state:
        del st.session_state['has_participated']  # Supprimer l'état de participation

# Vérifiez si l'état de rafraîchissement existe dans la session
if "refresh" not in st.session_state:
    st.session_state["refresh"] = False

# Rafraîchissement et réinitialisation manuelle
if admin_code == ADMIN_CODE:
    st.sidebar.success("Code correct. Vous pouvez rafraîchir ou réinitialiser.")
    if st.sidebar.button("Rafraîchir la page"):
        st.session_state["refresh"] = True
    if st.sidebar.button("Réinitialiser les votes"):
        reset_words()
        st.sidebar.success("Tous les mots et états de participation ont été réinitialisés.")
if st.session_state["refresh"]:
    st.session_state["refresh"] = False
    st.query_params = {"refresh": str(time.time())}
