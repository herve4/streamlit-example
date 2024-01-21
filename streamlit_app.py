import decimal
import os.path
from io import BytesIO
from os import path
from pathlib import Path

import numpy.random
from PIL.ImageFilter import *
from rembg import remove
import streamlit as s
from PIL import Image, ImageColor, ImageFilter
from aspose.imaging import RasterImage
import aspose.pycore as aspycore

s.set_page_config(page_title="BACKGROUND", page_icon=":book:", layout="centered", initial_sidebar_state="auto")
with open("style.css") as file_style:
    s.markdown(f"<style>{file_style.read()}</style>", unsafe_allow_html=True)

s.write("<h1 style='color:yellow;'>UNE NOUVELLE MANIERE DE MANUPULER LES IMAGES</h1>", unsafe_allow_html=True)
s.write("###### Vous avez marre de toujours utiliser Photoshop :dog: ! Mais oui, il fait ramer votre ordinateur. ")
s.write("###### Mais la solution, elle est là ! BACKGROUND vous ouvre ses porte.")
s.write("### Enlever l'arrière-plan de l'image")
s.sidebar.write("# :snake: Background :snake:")

col1, col2 = s.columns(2)

bordure = s.sidebar.number_input("Améliorer la bordure", min_value=0, max_value=400, value=220, step=5)
fond = s.sidebar.slider("Améliorer l'arrière-plan", min_value=0, max_value=100, value=15)
row1 = s.sidebar.container(border=True)
check = row1.checkbox("Activer le masque", value=False)
contoure_leger = row1.checkbox("Contour léger", value=False)
select_img_filtre = row1.selectbox("Filtres", options=(
    "Selectionner un filtre", "Flou panoramic", "Nettété", "Flou Gaussien", "Masquage flou"))

# On charge l'image
image_upload = s.file_uploader("Choississez une image", type=["png", "jpg", "jpeg"], accept_multiple_files=False)


def convert_img(image):
    buf = BytesIO()
    image.save(buf, format="PNG")
    byte_img = buf.getvalue()
    return byte_img


def fix_image(image):
    image = Image.open(image)

    # Ajout des éléments dans la colonne 1
    col1.write("### Image originale")
    col1.image(image)
    # Traiter l'image
    fixed = remove(image, alpha_matting=False, only_mask=check, alpha_matting_background_threshold=fond,
                   alpha_matting_foreground_threshold=bordure, post_process_mask=contoure_leger)

    # Affichage de l'image détourrée
    new_fixed = fixed
    if select_img_filtre != "Selectionner un filtre":

        if select_img_filtre == "Flou panoramic":
            blur_value = row1._number_input("Intensité du flou panaoramic :", min_value=0.0, max_value=100.0,
                                            value=10.0, step=5.0)
            fixed = convert_img(fixed.filter(GaussianBlur(radius=blur_value)))

            print("Blur")

        elif select_img_filtre == "Nettété":
            fixed = convert_img(fixed.filter(DETAIL))
            print("Détail")

        elif select_img_filtre == "Flou Gaussien":
            blur_value = row1._number_input("Intensité du flou gaussien :", min_value=0.0, max_value=100.0,
                                            value=20.0, step=2.0)
            fixed = convert_img(fixed.filter(BoxBlur(radius=blur_value)))



        elif select_img_filtre == "Masquage flou":
            blur_value = row1._number_input("Niveau du flou :", min_value=0, max_value=10,
                                            value=5, step=1)

            # le seuil contrôle le changement de luminosité minimum qui sera accentué
            lumiere_value = row1._number_input("Seuil de la luminosité:", min_value=0, max_value=30,
                                               value=3, step=1)
            # pourcentage de rayon de flou
            per_value = row1._number_input("Pourcentage de l'effet :", min_value=0, max_value=500,
                                           value=100, step=5)

            def hex_to_rgb(hex):
                """
                Utilisez une compréhension de liste en combinaison avec int()une notation de tranche de liste pour obtenir les composants RVB de la chaîne hexadécimale.
                Utilisez tuple()pour convertir la liste résultante en tuple.
                :param hex:
                :return:
                """
                return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))

            fixed = convert_img(
                fixed.filter(UnsharpMask(radius=blur_value, percent=per_value, threshold=lumiere_value)))

    if select_img_filtre == "Flou panoramic":
        col2.write("### Image détourée avec Flou panoramic")

        col2.image(fixed)
        s.sidebar.markdown("\n")
        s.sidebar.download_button("Télécharger l'image", fixed, mime="image/png",
                                  file_name="image.png")

    elif select_img_filtre == "Nettété":
        col2.write("### Image détourée nette")

        col2.image(fixed)
        s.sidebar.markdown("\n")
        s.sidebar.download_button("Télécharger l'image", fixed, mime="image/png",
                                  file_name="image.png")
    elif select_img_filtre == "Flou Gaussien":
        col2.write("### Image détourée avec Flou Gaussien")

        col2.image(fixed)
        s.sidebar.markdown("\n")
        s.sidebar.download_button("Télécharger l'image", fixed, mime="image/png",
                                  file_name="image.png")
    elif select_img_filtre == "Masquage flou":
        col2.write("### Image détourée - Autres Effets")
        col2.image(fixed)
        s.sidebar.markdown("\n")
        s.sidebar.info(
            "Rendre les images plus claires et plus claires et spectaculaires en augmentant le contraste et en réduisant le bruit.")

        s.sidebar.download_button("Télécharger l'image", fixed, mime="image/png",
                                  file_name="image.png")

    else:
        col2.write("### Image détourée")

        col2.image(fixed)
        s.sidebar.markdown("\n")
        s.sidebar.download_button("Télécharger l'image", fixed.tobytes(), mime="image/png",
                                  file_name="image.png")
    # Information sur l'image
    s.markdown(f"#### Informations sur l'image :")
    s.markdown("\n")
    if select_img_filtre == "Selectionner un filtre":
        s.markdown(
            f"<p> Taille de l'image : {image.width} x {image.height}</p> <p>Mode avant : {image.mode} -  Mode après : {image.mode}</p>"
            f"<p>Format de l'image : {image.format}</p>"
            f"<p>Format ISO : {image.format_description}</p>", unsafe_allow_html=True)
        s.markdown(f"<p>Dimension bordure : {fixed.getbbox()}</p>", unsafe_allow_html=True)

    else:
        s.markdown(
            f"<p> Taille de l'image : {image.width} x {image.height}</p> <p>Mode avant : {image.mode}</p>"
            f"<p>Format de l'image : {image.format}</p>"
            f"<p>Format ISO : {image.format_description}</p>", unsafe_allow_html=True)


if image_upload is not None:
    fix_image(image_upload)
else:
    s.write("##### En attente d'une image uploadée !")
