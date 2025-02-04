# -*- coding: utf-8 -*-
"""
Mapa de visualizacion de datos de uso de suelo

Autor:
Saul Arciniega Esparza | zaul.ae@gmail.com
Profesor Asociado C, Facultad de Ingeniería de la UNAM
"""

#%% Librerias
import os
import json
import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events

import warnings
warnings.filterwarnings("ignore")

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
url = "https://filedn.com/l31Uxc2iCI1koQr1EKWjwQH/Research/rs-app-database/"


#%% Configuration
datasets_options = pd.read_csv(url + "LandCover_Datasets.csv")
datasets_labels = pd.read_csv(url + "LandCover_Labels.csv")


#%% Functions
def get_datasets_list():
    return datasets_options.loc[:, "Dataset"].to_list()


def get_datasets_labels(dataset):
    return datasets_labels.loc[datasets_labels["Dataset"] == dataset, "Description"].to_list()


@st.cache_data
def load_table():
    table = pd.read_csv(os.path.join(path, "layers", "aquifers_data.csv"))
    return table

table = load_table()


@st.cache_data
def create_map(dataset, land_cover):
    
    with open(os.path.join(os.path.join(path, "layers", "aquifers.geojson"))) as fid:
        layer = json.load(fid)
    
    filename = f"layers_landuse/{dataset}".replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    data = pd.read_feather(url + filename)
    id_lc = datasets_labels.loc[datasets_labels["Description"] == land_cover, "ID"].values[0]
    aquifer_lc = data.loc[((data["ID"] == id_lc))].iloc[:, 1:].transpose().squeeze()
    aquifer_lc.index = [int(x) for x in aquifer_lc.index]
    
    data_table = table.set_index("id", drop=False)
    if len(aquifer_lc) == 0:
        data_table["Uso Suelo (%)"] = 0.0
    else:    
        data_table["Uso Suelo (%)"] = aquifer_lc
           
    fig = px.choropleth_map(
            data_table,
            geojson=layer,
            color="Uso Suelo (%)",
            locations="id",
            featureidkey="properties.id",
            hover_data=["id", "name", "Uso Suelo (%)"],
            labels={"id": "ID", "name": "Acuifero"},
            #range_color=(vmin, vmax),
            opacity=0.6,
            center={"lat": 23, "lon": -102},
            color_continuous_scale="icefire",
            map_style="carto-positron",
            zoom=3.5
        )
    
    fig.update_layout(
        clickmode="event+select",
        margin={"r":0,"t":0,"l":0,"b":0},
        modebar_remove=["select2d", "lasso2d"]
        ) 
    return fig


@st.cache_data
def load_serie(id_aquifer, dataset, threshold):
    col = str(id_aquifer)
    filename = f"land_use/{dataset}/{id_aquifer}".replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    data = pd.read_feather(url + filename)
    mask = data[col] >= threshold
    lc_predominant = data.loc[mask, :]
    lc_sparse = data.loc[~mask, :]
    others = lc_sparse[["Year", col]].groupby("Year").sum().reset_index()
    others["ID"] = -1
    labels = datasets_labels.loc[datasets_labels["Dataset"] == dataset, :]
    labels.set_index("ID", inplace=True)
    lc_predominant.loc[:, "Description"] = labels.loc[lc_predominant["ID"].values, "Description"].values
    others["Description"] = "Otros"
    lc_full = pd.concat((lc_predominant, others)).sort_values(["Year", "ID"])
    lc_full.columns = ["Año", "ID", "%Covertura", "Descripcion"]
    return lc_full


@st.cache_data
def create_plot(data, dataset, gmode):

    labels = datasets_labels.loc[datasets_labels["Dataset"] == dataset, ["Description", "Color"]]
    colors = labels.set_index("Description").squeeze().to_dict()
    colors["Otros"] = "#212f3d"

    if gmode:
        barmode = "stack"
    else:
        barmode = "group"
    
    fig = px.bar(
        data,
        x="Año",
        y="%Covertura",
        color="Descripcion",
        hover_data=["ID"],
        barmode=barmode,
        color_discrete_map=colors
    )
    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Covertura de Suelo (%)",
        legend_title=f"Covertura con {dataset}",
        legend={
            "orientation":"h",
            #"entrywidth": 70,
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1
        }
    )
    return fig


@st.cache_data
def download_data(data):
    return data.to_csv(index=False).encode('utf-8')


#%% App

st.title("Uso de suelo de los Acuíferos de México")
st.sidebar.title("Bases de datos")

dataset_selection = st.sidebar.selectbox(
    "Base de datos",
    get_datasets_list(),
    key="dataset_lc1"
)
st.sidebar.markdown("**Opciones del mapa**")
lc_selection = st.sidebar.selectbox(
    "Variable",
    get_datasets_labels(dataset_selection),
    key="variable_lc1"
)
st.sidebar.markdown("**Opciones graficas**")
threshold = st.sidebar.number_input(
    "Coverturas con % menor agrupar en otros",
    min_value=0.,
    max_value=100.,
    value=1., step=0.5,
    key="threshold_lc1",
)
gmode = st.sidebar.checkbox("Agrupar por año")

st.markdown(f"**Mapa de uso de suelo de {lc_selection} con {dataset_selection}**")
fig = create_map(dataset_selection, lc_selection)
selected_geometry = plotly_events(fig, click_event=True, hover_event=False)

if selected_geometry and dataset_selection:
    idx = selected_geometry[0]["pointIndex"]
    if idx in table.index: 
        aquifer_data = table.loc[idx, :].squeeze()
        id_aquifer, aquifer_name = aquifer_data["id"], aquifer_data["name"]

        st.markdown(f"**Covertura de suelo para el Acuífero {aquifer_name}**")

        lc_table = load_serie(id_aquifer, dataset_selection, threshold)

        lc_fig = create_plot(lc_table, dataset_selection, gmode)
        st.plotly_chart(lc_fig, use_container_width=True)

        with st.expander("Tabla de covertura de suelo"):
            st.dataframe(lc_table, hide_index=True, use_container_width=True)


        output = download_data(lc_table)
        st.download_button(
            label="Descargar datos",
            data=output,
            file_name=f"CoverturaSuelo_{id_aquifer}_{dataset_selection}.csv",
            mime="text/csv",
        )