# -*- coding: utf-8 -*-
"""
Bases de datos disponibles

Autor:
Saul Arciniega Esparza | zaul.ae@gmail.com
Profesor Asociado C, Facultad de Ingeniería de la UNAM
"""

#%% Librerias
import os
import json
import pandas as pd
import streamlit as st


path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
url = "https://filedn.com/l31Uxc2iCI1koQr1EKWjwQH/Research/rs-app-database/"

filename = url + "Datasets_Description.csv"
df = pd.read_csv(filename, delimiter=";")

st.title("Bases de datos disponibles")
st.markdown("Se enlista a continuación las bases de datos disponibles actuales en SUPRAM.")

st.dataframe(df, use_container_width=True)

