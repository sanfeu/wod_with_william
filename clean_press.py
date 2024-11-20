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

def decompose_weight(weight, weights_selection):
    added_weight = weight - BAR_WEIGHT # remove the bar weight
    semi_weight = added_weight / 2
    current_weight = 0
    composition = []
    for plate in sorted_plates:
        if weights_selection and not plate['weight'] in weights_selection:
            continue
        while current_weight + plate["weight"] <= semi_weight:
            composition.append(plate)
            current_weight = current_weight + plate["weight"]

    # remaining_weight = semi_weight
    # for plate, next_plate in reversed(plates):
    #     nb_plates = remaining_weight // plate[weight]
    #     nb_to_next_plate = next_plate['weight'] /  = 
    return composition


def make_table(weight, plates_selection):
    percents = [i for i in np.arange(0.8, 1.01, 0.02)]
    perfect_weights = [round(weight * p, 2) for p in percents]
    min_weights = [math.floor(w / 2.5) * 2.5 for w in perfect_weights]
    max_weights = [math.ceil(w / 2.5) * 2.5 for w in perfect_weights]
    actual_weights = list(set(min_weights + max_weights))
    compositions = [decompose_weight(w, plates_selection) for w in actual_weights]

    df1 = pd.DataFrame(data={'percent': percents, 'actual': perfect_weights})
    df2 = pd.DataFrame(data={'actual': actual_weights, 'composition': compositions})

    df = df1.merge(df2, how='outer', on='actual')
    df = df.sort_values(by='actual', ascending=False)

    return df

def make_weight_list(my_plates):

    if not isinstance(my_plates, list):
        return []
    return [p['weight'] for p in my_plates]


options = [plate['weight'] for plate in reversed(sorted_plates)]
plates_selection = st.pills("Choose your plates"
                           , options
                           , default = [w for w in options if w <=10]
                           , selection_mode="multi")


weight_one_rep = st.number_input("Enter your 1 REP weight (in Kg)"
                                 , value=60.0
                                 ,step=2.5)

df = make_table(weight_one_rep, plates_selection)

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
              , width=600, height=600)
