import folium
from folium import Choropleth
from folium import Choropleth, GeoJson, LayerControl
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import pandas as pd
import math
import os
from shapely.geometry import Point


st.set_page_config(page_title="MAPA",
                   layout="wide"
)

# CSS customizado
st.markdown(
    """
    <style>
        /* Sidebar fundo */
        [data-testid="stSidebar"] {
            background-color: #2C3E50;  /* azul escuro */
            color: white;
        }

        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Selectbox dentro da sidebar */
        [data-testid="stSidebar"] .stSelectbox > div > div {
            background-color: #2C3E50;   /* igual ao sidebar */
            color: white;
            border: 1px solid white;     /* borda branca */
            border-radius: 8px;
        }

        /* Quando abre a lista de opções */
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="popover"] {
            background-color: #2C3E50;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

current_working_directory = os.getcwd()

shp_path = os.path.join(current_working_directory, "BAIRROS.shp")

censo_path = os.path.join(current_working_directory, "CENSO 2010 E 2022.xlsx")

# Ler o shapefile
gdf = gpd.read_file(shp_path).to_crs("EPSG:4326")

censo = pd.read_excel(censo_path)

# Criar mapa base
m = folium.Map(location=[-3.057334413281103, -59.98600479911497], zoom_start=11.50)

# Unir com o shapefile
gdf_mapa = gdf.merge(censo[["BAIRRO","Censo 2010"]], left_on='NOME_BAIRR', right_on='BAIRRO', how='left')

gdf_mapa = gdf_mapa.merge(censo[["BAIRRO","Censo 2022"]], left_on='NOME_BAIRR', right_on='BAIRRO', how='left')

gdf_mapa = gdf_mapa.merge(censo[["BAIRRO","Evolução (2010 - 2022) %"]], left_on='NOME_BAIRR', right_on='BAIRRO', how='left')

st.sidebar.title("Mapa da zona urbana da cidade de Manaus")

local = st.sidebar.multiselect('Escolha o bairro:', gdf['NOME_BAIRR'].unique())

if (len(local) > 1) or (len(local) == 0):
   print(local)
else:
    print(local)
    bairro_shp = gdf.loc[gdf['NOME_BAIRR']  ==  local[0]]
    geojson_bairro = bairro_shp.to_json()
    # Adicionar o segundo GeoJSON ao mapa com uma cor diferente
    folium.GeoJson(
        geojson_bairro,
    name='shapefile',
    style_function=lambda x: {
        'color': 'purple',        # cor da borda
        'weight': 6,              # espessura da borda
        'opacity': 1.0,           # opacidade da borda
        'fillColor': 'purple',    # cor de preenchimento
        'fillOpacity': 0.7
    }
    ).add_to(m)

censo_opcao = st.sidebar.multiselect('Escolha o Censo:', ["Censo 2010", "Censo 2022", "Evolução (2010 - 2022) %"])

print(censo_opcao)

if (len(censo_opcao) == 0):
    # Camada com contornos dos bairros
    folium.GeoJson(
        gdf_mapa,
        name="Bairros",
        style_function=lambda feature: {
            'fillOpacity': 0,
            'color': 'black',
            'weight': 0.5
        },
        tooltip=folium.GeoJsonTooltip(
        fields=['NOME_BAIRR'],
        aliases=['Bairro:'])
    ).add_to(m)

    st_folium(m, width=1000, returned_objects=[])
else:
    # Adicionar o mapa coroplético
    Choropleth(
        geo_data=gdf_mapa.to_json(),
        name='choropleth',
        data=gdf_mapa,
        columns=['NOME_BAIRR', censo_opcao[0]],
        key_on='feature.properties.NOME_BAIRR',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=censo_opcao[0],
        nan_fill_color='white'
    ).add_to(m)

    # Camada com contornos dos bairros
    folium.GeoJson(
        gdf_mapa,
        name="Bairros",
        style_function=lambda feature: {
            'fillOpacity': 0,
            'color': 'black',
            'weight': 0.5
        },
        tooltip=folium.GeoJsonTooltip(
        fields=['NOME_BAIRR', censo_opcao[0]],
        aliases=['Bairro:', 'População:'])
    ).add_to(m)

    # Controles
    folium.LayerControl().add_to(m)

    st_folium(m, width=1000, returned_objects=[])