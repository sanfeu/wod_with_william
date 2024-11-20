import math
import os

from PIL import Image, ImageDraw, ImageFont

import streamlit as st
from streamlit_javascript import st_javascript
import numpy as np
import pandas as pd

BAR_WEIGHT = 20

plates = [
    {"weight": 25, "color" : 'red'},
    {"weight": 20, "color" : 'blue'},
    {"weight": 15, "color" : 'yellow'},
    {"weight": 10, "color" : 'black'},
    {"weight": 5, "color": 'black'},
    {"weight": 2.5, "color": 'red'},
    {"weight": 1.25, "color": 'black'}
]
sorted_plates = sorted(plates, key=lambda x: x['weight'], reverse=True)


def decompose_weight(weight):
    added_weight = weight - BAR_WEIGHT # remove the bar weight
    semi_weight = added_weight / 2
    current_weight = 0
    composition = []
    for plate in plates:
        while current_weight + plate["weight"] < semi_weight:
            composition.append(plate)
            current_weight = current_weight + plate["weight"]
    return composition


def make_table(weight):
    percents = [i for i in np.arange(0.8, 1.01, 0.02)]
    perfect_weights = [round(weight * p, 2) for p in percents]
    min_weights = [math.floor(w / 2.5) * 2.5 for w in perfect_weights]
    max_weights = [math.ceil(w / 2.5) * 2.5 for w in perfect_weights]
    actual_weights = list(set(min_weights + max_weights))
    compositions = [decompose_weight(w) for w in actual_weights]

    df1 = pd.DataFrame(data={'percent': percents, 'actual': perfect_weights})
    df2 = pd.DataFrame(data={'actual': actual_weights, 'composition': compositions})

    df = df1.merge(df2, how='outer', on='actual')
    df = df.sort_values(by='actual', ascending=False)

    return df

def make_weight_list(my_plates):

    if not isinstance(my_plates, list):
        return []
    return [p['weight'] for p in my_plates]


def make_bitmap(my_plates):

    if not isinstance(my_plates, list):
        return ""

    total_weight = sum([my_plate['weight'] for my_plate in my_plates])
    image_file = f'plates_for_{total_weight}.png'
    if os.path.exists(image_file):
        return image_file

    RADIUS = 30
    SQUARE = 100

    # Dimensions de l'image
    width = SQUARE * len(my_plates)
    height = SQUARE

    # Créer une nouvelle image blanche
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Police pour le texte (vous pouvez spécifier le chemin vers une police TTF si nécessaire)
    font = ImageFont.load_default()

    # Initial position
    x = SQUARE // 2
    y = SQUARE // 2

    # Dessiner les cercles et ajouter le texte
    for plate in my_plates:
        # Dessiner le cercle
        draw.ellipse((x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS), fill=plate['color'])
        
        # Ajouter le texte (weight) au centre du cercle
        text = str(plate['weight'])
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
        draw.text((x - text_width // 2, y - text_height // 2), text, fill='white', font=font)
        
        # Déplacer la position x pour le prochain cercle
        x += SQUARE

    image.save(image_file)
    return image_file



weight_one_rep = st.number_input("Enter your 1 REP weight (in Kg)"
                                 , value=60.0
                                 ,step=2.5)

#st.divider()

df = make_table(weight_one_rep)
# df['composition2'] = df['composition'].apply(make_bitmap)

df['composition'] = df['composition'].apply(make_weight_list)
df['percent'] = df['percent'].fillna("")


column_config={
        "percent": st.column_config.NumberColumn(format="%.2f")
        , "actual": st.column_config.NumberColumn(format="%.2f")
        , "composition": st.column_config.ListColumn()
#        , "composition2": st.column_config.ImageColumn()
    }

#st.table(df)
st.dataframe(df
              , hide_index=True
              , column_config=column_config
              , width=400, height=600)
