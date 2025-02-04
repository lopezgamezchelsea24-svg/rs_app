# -*- coding: utf-8 -*-
"""
Mapa de visualizacion y consulta de datos derivados de Percepcion Ramota

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


path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
url = "https://filedn.com/l31Uxc2iCI1koQr1EKWjwQH/Research/rs-app-database/"


#%% Configuration
datasets_options = pd.read_csv(url + "Datasets.csv")
plot_type = ["Diaria", "Mensual", "Media Mensual", "Anual"]
variable_types = datasets_options["Label"].unique().tolist()

MIN_COLOR = (8, 48, 107)
MID_COLOR = (15, 168, 227)
MAX_COLOR = (111, 198, 107)


#%% Functions

def get_n_colors(n):
    """Interpolate colors for time series"""
    
    if n == 0:
        colors = []
    elif n == 1:
        colors = [f"rgb{str(MIN_COLOR)}"]
    elif n == 2:
        colors = [f"rgb{str(MIN_COLOR)}", f"rgb{str(MID_COLOR)}"]
    elif n == 3:
        colors = [
            f"rgb{str(MIN_COLOR)}",
            f"rgb{str(MID_COLOR)}",
            f"rgb{str(MAX_COLOR)}"
            ]
    else:
        n1 = int(np.round(n / 2))
        n2 = n - n1
        color_tuples1 = px.colors.n_colors(MIN_COLOR, MID_COLOR, n1)
        color_tuples2 = px.colors.n_colors(MID_COLOR, MAX_COLOR, n2 + 1)
        colors = [f"rgb{str(color)}" for color in color_tuples1]
        colors.extend([f"rgb{str(color)}" for color in color_tuples2][1:])
    return colors


def get_datasets_list(ptype, vtype):
    mask = (datasets_options["Label"] == vtype)
    if ptype == "Diaria":
        mask  =  mask & (datasets_options["Timestep"] == ptype)
    dataset_list = datasets_options.loc[mask, "Dataset"].to_list()
    return dataset_list


def get_dataset_info(dataset, vtype):
    mask = (datasets_options["Label"] == vtype) & (datasets_options["Dataset"] == dataset)
    info = datasets_options.loc[mask, :]
    return info.squeeze()


@st.cache_data
def load_table():
    table = pd.read_csv(os.path.join(path, "layers", "aquifers_data.csv"))
    return table

table = load_table()


@st.cache_data
def create_map(varname, dataset):
    
    with open(os.path.join(os.path.join(path, "layers", "aquifers.geojson"))) as fid:
        layer = json.load(fid)
    
    filename = f"layers_series/{varname}/{dataset}".replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    serie = pd.read_feather(url + filename)
    serie = serie.set_index("ID").squeeze()
    mask = (datasets_options["Dataset"] == dataset) & (datasets_options["Label"] == varname)
    var_label = datasets_options.loc[mask, "Variable"].values[0]
    units = datasets_options.loc[mask, "Units"].values[0]
    var_label_units = f"{var_label.title()} ({units})"
    
    data_table = table.set_index("id", drop=False)
    data_table[var_label] = serie.round(2)
           
    fig = px.choropleth_map(
            data_table,
            geojson=layer,
            color=var_label,
            locations="id",
            featureidkey="properties.id",
            hover_data=["id", "name", var_label],
            labels={"id": "ID", "name": "Acuifero", var_label: var_label_units},
            #range_color=(vmin, vmax),
            opacity=0.6,
            center={"lat": 23, "lon": -102},
            color_continuous_scale="icefire",
            mapbox_style="carto-positron",
            zoom=3.5
        )
    
    fig.update_layout(
        clickmode="event+select",
        margin={"r":0,"t":0,"l":0,"b":0},
        modebar_remove=["select2d", "lasso2d"]
        ) 
    return fig


@st.cache_data
def load_serie(id_aquifer, datasets, variable, timestep):
    data = []
    for dataset in datasets:
        info = get_dataset_info(dataset, variable)
        varname = info["Variable"]
        agg_fun = info["Agg"]

        filename = f"timeseries/{dataset}_{varname}/{id_aquifer}".replace(" ", "%20").replace("(", "%28").replace(")", "%29")
        serie = pd.read_feather(url + filename).set_index("Dates").squeeze()
        if timestep == "Mensual" and info["Timestep"] == "Diaria":
            if agg_fun == "mean":
                serie = serie.resample("1M").mean()
                serie.index = serie.index - pd.offsets.MonthBegin()
            else:
                serie = serie.resample("1M").sum()
                serie.index = serie.index - pd.offsets.MonthBegin()
        elif timestep == "Anual":
            if agg_fun == "mean":
                serie = serie.groupby(serie.index.year).mean()
            else:
                serie = serie.groupby(serie.index.year).sum()
        elif timestep == "Media Mensual":
            if info["Timestep"] == "Diaria":
                if agg_fun == "mean":
                    serie = serie.resample("1M").mean()
                    serie.index = serie.index - pd.offsets.MonthBegin()
                else:
                    serie = serie.resample("1M").sum()
                    serie.index = serie.index - pd.offsets.MonthBegin()
            serie = serie.groupby(serie.index.month).mean()
        serie = serie.rename(dataset)
        data.append(serie)
    if data:
        return pd.concat(data, axis=1).round(4)
    else:
        return pd.DataFrame([])


@st.cache_data
def create_plot(serie, varname):
    units = datasets_options.loc[datasets_options["Label"] == varname, "Units"].values[0]
    colors = get_n_colors(serie.shape[1])
    data_plot = []
    for i, col in enumerate(serie.columns):
        data_plot.append(
            go.Scatter(
                x=serie.index,
                y=serie[col],
                mode="lines",
                name=col,
                showlegend=True,
                marker_color=colors[i]
            )
        )
    layout = go.Layout(yaxis={"title": f"{varname} ({units})"})
    fig = go.Figure(data=data_plot, layout=layout)
    fig.update_layout(
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
    return data.to_csv().encode('utf-8')


#%% App

st.title("Hidrología de los Acuíferos de México")
st.sidebar.title("Bases de datos")

variable_selection = st.sidebar.selectbox("Variable", variable_types, key="variable1")
st.sidebar.markdown("**Opciones del mapa**")
map_dataset_selection = st.sidebar.selectbox(
    "Base de datos para mapa",
    get_datasets_list("Mensual", variable_selection),
    key="dataset2"
)
st.sidebar.markdown("**Opciones de graficas**")
timestep_selection = st.sidebar.selectbox("Tipo de grafica", plot_type, key="timestep1")
dataset_selection = st.sidebar.multiselect(
    "Base de datos para gráficas",
    get_datasets_list(timestep_selection, variable_selection),
    key="dataset1"
)

st.markdown(f"**Mapa de {variable_selection} media anual con la base de datos {map_dataset_selection}**")
fig = create_map(variable_selection, map_dataset_selection)
selected_geometry = plotly_events(fig, click_event=True, hover_event=False)

if selected_geometry and dataset_selection:
    idx = selected_geometry[0]["pointIndex"]
    if idx in table.index: 
        aquifer_data = table.loc[idx, :].squeeze()
        id_aquifer, aquifer_name = aquifer_data["id"], aquifer_data["name"]

        st.markdown(f"**Series del Acuífero {aquifer_name}**")

        time_serie = load_serie(id_aquifer, dataset_selection, variable_selection, timestep_selection)
        fig1 = create_plot(time_serie, variable_selection)
        st.plotly_chart(fig1, use_container_width=True)

        output = download_data(time_serie)
        st.download_button(
            label="Descargar datos",
            data=output,
            file_name=f"{id_aquifer}_{variable_selection}_{timestep_selection}.csv",
            mime="text/csv",
        )
