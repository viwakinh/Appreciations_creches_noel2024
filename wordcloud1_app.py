import streamlit as st
import io  # Pour manipuler BytesIO
import qrcode
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json  # Pour sauvegarder et charger les mots
import os  # Pour vérifier l'existence du fichier
from collections import Counter  # Pour compter les occurrences des mots
import datetime  # Pour inclure la date et l'heure dans les fichiers

# Configuration de la page
st.set_page_config(page_title="Nuage de mots en direct", layout="wide")

# Fichier pour stocker les mots soumis
WORDS_FILE = os.path.join(os.path.dirname(__file__), "words.json")

# Liste de mots présélectionnés
PRESELECTED_WORDS = [
    " ", "Ingénieuse", "Innovante", "Imaginative", 
    "Originale", "Éblouissante", "Impressionnante", "Inspirée"
]

# Initialiser le numéro d’appréciation si nécessaire
if 'appreciation_number' not in st.session_state:
    st.session_state.appreciation_number = 1

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

# Fonction pour enregistrer une image combinée du nuage de mots et de l'histogramme
def save_charts_combined(wordcloud, word_counts):
    # Obtenir le numéro d’appréciation actuel
    appreciation_number = st.session_state.appreciation_number

    # Générer l'horodatage
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Créer une figure combinée pour le nuage de mots et l'histogramme
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    # Nuage de mots
    axes[0].imshow(wordcloud, interpolation="bilinear")
    axes[0].axis("off")
    axes[0].set_title("Nuage de mots")

    # Histogramme
    words, counts = zip(*word_counts.items())
    bars = axes[1].barh(words, counts)
    axes[1].set_xlabel("Nombre de votes")
    axes[1].set_ylabel("Mots")
    axes[1].xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    axes[1].set_title("Histogramme des mots")

    # Ajouter le nombre de votes au sommet de chaque barre
    for bar, count in zip(bars, counts):
        axes[1].text(count, bar.get_y() + bar.get_height() / 2, str(count),
                     va='center', ha='left', fontsize=10)

    # Sauvegarder l'image combinée
    combined_filename = f"Appreciations_creches_{appreciation_number}_{timestamp}_combined.png"
    plt.tight_layout()
    plt.savefig(combined_filename)
    plt.close(fig)

    # Incrémenter le numéro d’appréciation pour la prochaine sauvegarde
    st.session_state.appreciation_number += 1

    return combined_filename  # Retourne le nom du fichier pour l'affichage

# Charger les mots au démarrage
if 'word_list' not in st.session_state:
    st.session_state.word_list = load_words()

# Suivi des participants
if 'has_participated' not in st.session_state:
    st.session_state.has_participated = False

# URL de l'application pour les participants
url_wordcloud = "https://appreciationscrechesnoel2024-9cdywr4k2o4kx58pc3cgjv.streamlit.app/"

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

# Bouton Rafraîchir après le bouton Soumettre
if st.button("Rafraîchir la page"):
    st.session_state.word_list = load_words()

# Affichage dynamique du nuage de mots et de l'histogramme
if admin_code == ADMIN_CODE:  # ADMIN_CODE défini comme 2018
    st.subheader("Nuage de mots en direct")
    word_list = load_words()  # Recharger les mots

    if word_list:
        # Créer le texte pour le nuage de mots à partir des mots soumis
        wordcloud_text = " ".join(word_list)
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(wordcloud_text)

        # Compter les occurrences des mots pour l'histogramme
        word_counts = Counter(word_list)
        words, counts = zip(*word_counts.items())

        # Organisation en deux colonnes avec plus d'espace pour le nuage de mots
        col1, col2 = st.columns([2, 1])

        # Afficher le nuage de mots dans la première colonne
        with col1:
            st.write("### Nuage de mots")
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

        # Afficher l'histogramme dans la deuxième colonne avec annotations des nombres de votes
        with col2:
            st.write("### Histogramme des mots")
            fig, ax = plt.subplots(figsize=(5, 3))
            bars = ax.barh(words, counts)
            ax.set_xlabel("Nombre de votes")
            ax.set_ylabel("Mots")
            ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

            # Ajouter le nombre de votes au sommet de chaque barre
            for bar, count in zip(bars, counts):
                ax.text(count, bar.get_y() + bar.get_height() / 2, str(count),
                        va='center', ha='left', fontsize=10)

            st.pyplot(fig)

    else:
        st.write("Le nuage de mots et l'histogramme apparaîtront ici lorsque les participants auront soumis leurs mots.")
else:
    if admin_code:  # Vérifie si un code a été saisi
        st.subheader("Nuage de mots")
        st.write("⚠️ Le nuage de mots est réservé à l'administrateur. Veuillez entrer le code administrateur dans la barre latérale.")

# Fonction pour réinitialiser les mots et l'état des participants
def reset_words():
    word_list = load_words()  # Charger les mots actuels
    if word_list:
        # Créer et sauvegarder les graphiques combinés
        wordcloud_text = " ".join(word_list)
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(wordcloud_text)
        word_counts = Counter(word_list)
        last_saved_file = save_charts_combined(wordcloud, word_counts)

        # Enregistrer le nom du fichier dans la session pour l'historique
        if "saved_files" not in st.session_state:
            st.session_state.saved_files = []
        st.session_state.saved_files.append(last_saved_file)

    st.session_state.word_list = []
    save_words([])  # Écrire une liste vide dans le fichier JSON
    if 'has_participated' in st.session_state:
        del st.session_state['has_participated']  # Supprimer l'état de participation

# Bouton pour réinitialiser - Affiché uniquement pour l'administrateur
if admin_code == ADMIN_CODE:  # ADMIN_CODE défini comme 2018
    if st.sidebar.button("Réinitialiser"):
        reset_words()
        st.success("Les mots et les graphiques ont été sauvegardés et réinitialisés.")

# Affichage de l'historique des images sauvegardées
if admin_code == ADMIN_CODE:  # ADMIN_CODE défini comme 2018
    st.sidebar.subheader("Historique des images sauvegardées")
    if "saved_files" in st.session_state and st.session_state.saved_files:
        for saved_file in st.session_state.saved_files:
            st.sidebar.image(saved_file, caption=saved_file, use_column_width=True)
    else:
        st.sidebar.write("Aucune image sauvegardée pour le moment.")
