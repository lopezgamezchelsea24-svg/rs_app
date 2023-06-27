# -*- coding: utf-8 -*-
"""

@author: Saul Arciniega Esparza
@email: zaul.ae@gmail.com
@institution: Faculty of Engineering at UNAM
"""

#%% Libraries
import os
import json
import streamlit as st
from PIL import Image

path = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="SUPRAM", layout="wide")

#%% Initial data


#%% App

st.title("Sistema Unificado de datos derivados de Percepción Remota para Acuíferos de México (SUPRAM)")
st.sidebar.title("SUPRAM")

st.image(Image.open(os.path.join(path, "img", "logos.png")), width=500)

st.markdown("""
## Acerca de

Plataforma para la consulta y visualización del datos climatológicos, hidrológicos, suelo y vegetación
derivados de Percepción Remota y Modelos Globales para los acuíferos de México.

Este proyecto ha sido desarrollado como parte del Servicio Social ([**2022-12/81-758**](https://www.siass.unam.mx/programa/36079))
titulado *Aplicación de datos de percepción remota para la evaluación cuantitativa de acuíferos*, que tiene por objetivo
generar una base de datos de series temporales y espaciales de información derivada de percepción remota para la evaluación
de recursos hídricos en acuíferos de México.

La información proporcionada en esta aplicación está destinada a propósitos educativos, de investigación y de aplicación,
por lo que puede ser utilizada, redistribuida o modificada. Si hace uso de esta plataforma o de su información le pedimos citar
este trabajo como:

Arciniega-Esparza S, Celso-Crescencio MI, Morales-Padilla D, Moreno-Iturria DR, Salinas-Calleros G, Hernández-Espriú JA (2023)
**Application of remote sensing data for the quantitative evaluation of aquifers**. Hydrogeology Group, Faculty of Engineering,
Universidad Nacional Autonoma de Mexico (UNAM).


## Instrucciones

- En el panel izquierdo se muestran las diferentes ventanas a las cuales se puede acceder en SUPRAM. Si no se visualiza el panel izquierdo
se puede dar clic en el botón **X** de la parte superior izquierda.

- Se deberá entrar a la categoría correspondiente e ingresar las opciones de visualización del mapa, las bases de datos a consultar,
y la escala de tiempo a la cual se quiera trabajar.

- Finalmente, se deberá seleccionar un acuífero en el mapa interactivo para consultar la información de las bases de datos seleccionadas.



## Agradecimientos

Este proyecto ha sido posible gracias al apoyo de la [División de Ingeniería en Ciencias de la Tierra (DICT)](http://www.dict.unam.mx/)
de la [Facultad de Ingeniería de la UNAM (FIUNAM)](https://www.ingenieria.unam.mx/), al Grupo de Hidrogeología de la FIUNAM, y a los y
las alumnas que han colaborado en este proyecto de investigación/divulgación.


## Colaboradores

- **Investigador Principal**:

**Dr. Saúl Arciniega Esparza** | Profesor Asociado C de Tiempo Completo, Facultad de Ingeniería de la UNAM | 
[Linkedin](https://www.linkedin.com/in/saularciniegaesparza/) | [ResearchGate](https://www.researchgate.net/profile/Saul-Arciniega-Esparza)

- **Colaboradores**

**Dr. Antonio Hernández Espriú** | Profesor Titular B de Tiempo Completo, Facultad de Ingeniería de la UNAM | 
[Twitter](https://twitter.com/hydrogeologymx) | [ResearchGate](https://www.researchgate.net/profile/Antonio-Hernandez-Espriu)

**Ing. Gabriel Salinas Calleros** | Técnico Académico, Facultad de Ingeniería de la UNAM | 
[Linkedin](https://www.linkedin.com/in/gabriel-salinas-calleros-40a4954a/)


- **Alumn@s:**

**Ing. Maria Isabel Celso Crescencio** | Geofísica | Facultad de Ingeniería de la UNAM

**Ing. Diana Cecilia Morales Padilla** | Geológa | Facultad de Ingeniería de la UNAM

**Ing. Daniel Rodrigo Moreno Iturria** | Geológo | Facultad de Ingeniería de la UNAM
""")

