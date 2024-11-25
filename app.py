import folium
from folium import Choropleth
from folium import Choropleth, GeoJson, LayerControl
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import math
import os

st.set_page_config(page_title="MAPA",
                   layout="wide"
)

st.title("Dados demográficos da cidade de Manaus - CENSO 2022 (IBGE)")

current_working_directory = os.getcwd()

shp_manaus = os.path.join(current_working_directory, "Manaus_Bairros_CD2022.shp")

data_path = os.path.join(current_working_directory, "demografia_bairro_manaus.xlsx")

zonas_path = os.path.join(current_working_directory, "bairros_manaus_zonas.xlsx")

m = folium.Map(location=[-3.057334413281103, -59.98600479911497], zoom_start=11)

manaus_setores = gpd.read_file(shp_manaus)
#manaus_setores = am_setores.loc[am_setores["NM_MUN"] == "Manaus"]
#manaus_setores = manaus_setores[["CD_SETOR", "NM_BAIRRO", "geometry"]]

population = pd.read_excel(data_path)
population['CD_BAIRRO'] = population['CD_BAIRRO'].astype(str)

manaus_zonas = pd.read_excel(zonas_path)

zonas_dic =  manaus_zonas.set_index('NM_BAIRRO')['Zona administrativa'].to_dict()

resultado = manaus_setores.merge(population, on="CD_BAIRRO")

resultado['ZONA ADMINISTRATIVA'] = resultado['NM_BAIRRO'].map(zonas_dic)

zona = st.sidebar.multiselect('Escolha a zona administrativa:', resultado['ZONA ADMINISTRATIVA'].unique().tolist())

if (len(zona) == 0):
  print(zona)
  print("sem dados")
  #resultado = resultado.rename(columns={"Quantidade de moradores": "população"})
elif (len(zona) == 1):
   print(zona)
   resultado = resultado.loc[resultado["ZONA ADMINISTRATIVA"] == zona[0]]
else:
  print(zona)
  resultado = resultado.loc[resultado["ZONA ADMINISTRATIVA"].isin(zona)]

demografia = st.sidebar.multiselect('Escolha a variável demográfica:', ['Quantidade de moradores', 'Sexo masculino', 'Sexo feminino','Sexo masculino, 0 a 4 anos', 'Sexo masculino, 5 a 9 anos','Sexo masculino, 10 a 14 anos', 'Sexo masculino, 15 a 19 anos','Sexo masculino, 20 a 24 anos', 'Sexo masculino, 25 a 29 anos','Sexo masculino, 30 a 39 anos', 'Sexo masculino, 40 a 49 anos','Sexo masculino, 50 a 59 anos', 'Sexo masculino, 60 a 69 anos','Sexo masculino, 70 anos ou mais', 'Sexo feminino, 0 a 4 anos','Sexo feminino, 5 a 9 anos', 'Sexo feminino, 10 a 14 anos','Sexo feminino, 15 a 19 anos', 'Sexo feminino, 20 a 24 anos','Sexo feminino, 25 a 29 anos', 'Sexo feminino, 30 a 39 anos','Sexo feminino, 40 a 49 anos', 'Sexo feminino, 50 a 59 anos','Sexo feminino, 60 a 69 anos', 'Sexo feminino, 70 anos ou mais','0 a 4 anos', '5 a 9 anos', '10 a 14 anos', '15 a 19 anos','20 a 24 anos', '25 a 29 anos', '30 a 39 anos', '40 a 49 anos','50 a 59 anos', '60 a 69 anos', '70 anos ou mais'], default=['Quantidade de moradores'])

if (len(demografia) > 1) or (len(demografia) == 0):
  print("sem dados")
  resultado["população"] = 0
  #resultado = resultado.rename(columns={"Quantidade de moradores": "população"})
else:
  resultado = resultado[["NM_BAIRRO","CD_BAIRRO", "geometry", demografia[0]]]
  resultado = resultado.rename(columns={demografia[0]: "população"})

  populacao_bairro = resultado[["CD_BAIRRO", "geometry", "população"]]

  geo_json_data = populacao_bairro[['geometry', 'CD_BAIRRO']].set_index('CD_BAIRRO').__geo_interface__

  Choropleth(
        geo_data=geo_json_data,
        name='choropleth',
        data=populacao_bairro,
        columns=['CD_BAIRRO', 'população'],  # Nome da coluna de união e a coluna de valores
        key_on='feature.id',  # Mapeia os dados pela chave (assumindo que 'bairros' é o identificador)
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='População por Bairro'
    ).add_to(m)
  
  folium.LayerControl().add_to(m)


grouped = resultado.groupby("NM_BAIRRO").agg({
    "população": "sum"
}).reset_index()

col1, col2 = st.columns([2, 1])
with col1:
    st.write("MAPA CLOROPLÉTICO")
    st_data = st_folium(m, width=800, height=500)

with col2:
    st.write("TABELA DA POPULAÇÃO POR BAIRRO")
    st.dataframe(grouped, width=800, height=500)