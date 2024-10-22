import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px



df_CAPTURA = st.session_state.df_CAPTURA.copy()
df_SUBIDOS = st.session_state.df_SUBIDOS.copy()
df_TOPANUNCIOS = df_CAPTURA["CAP UTM_TERM"].value_counts()
st.dataframe(df_TOPANUNCIOS)

# Reseta o index do df_TOPANUNCIOS e renomeia as colunas para evitar confusão
df_top_anuncios_reset = df_TOPANUNCIOS.reset_index()
df_top_anuncios_reset.columns = ['CAP UTM_TERM', 'count']

# Fazemos o merge para pegar os links do drive correspondentes, se houver
df_result = pd.merge(df_top_anuncios_reset, df_SUBIDOS[['ANUNCIO', 'LINK DO DRIVE']], 
                     left_on='CAP UTM_TERM', right_on='ANUNCIO', how='left')

# Preenchemos com "não é anuncio" onde não houver link correspondente
df_result['LINK DO DRIVE'] = df_result['LINK DO DRIVE'].fillna('não é anuncio')

# Remover a coluna 'ANUNCIO' que veio do merge
df_result = df_result.drop(columns=['ANUNCIO'])

# Mostrar o dataframe resultante
st.dataframe(df_result)