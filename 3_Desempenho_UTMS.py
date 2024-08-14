import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from urllib.parse import unquote_plus

def criar_grafico_combinations(df):
    df_top10 = df.sort_values(by='counts', ascending=False).head(10)
    df_top10 = df_top10.sort_values(by='counts', ascending=True)

    fig = go.Figure(go.Bar(
        x=df_top10['counts'],
        y=df_top10['Percurso'],
        orientation='h',
        marker=dict(
            color=df_top10['counts'],
            colorscale='Blues',
            line=dict(color='white', width=1)
        )
    ))

    fig.update_layout(
        title='Top 10 Combinações UTM Medium + UTM Source',
        xaxis_title='Counts',
        yaxis_title='Percurso',
        yaxis=dict(
            automargin=True,
            tickfont=dict(size=16),
        ),
        xaxis=dict(
            tickfont=dict(size=20)
        ),
        title_font=dict(size=20),
        margin=dict(l=120, r=40, t=60, b=40),
        height=500
    )

    return fig

# Verifique se os dados foram carregados
if 'sheets_loaded' in st.session_state and st.session_state.sheets_loaded:
    # Carregar os dataframes da sessão
    df_CAPTURA = st.session_state.df_CAPTURA.copy()
    df_PREMATRICULA = st.session_state.df_PREMATRICULA.copy()
    df_VENDAS = st.session_state.df_VENDAS.copy()    

    # Top 5 UTM Source
    top5_source = df_CAPTURA['CAP UTM_SOURCE'].value_counts().head(5)
    
    # Top 5 UTM Medium
    top5_medium = df_CAPTURA['CAP UTM_MEDIUM'].value_counts().head(5)
    
    # Top 5 Percurso (Combinações de Medium + Source)
    Combinations = df_CAPTURA.groupby(['CAP UTM_MEDIUM', 'CAP UTM_SOURCE']).size().reset_index(name='counts').sort_values(by='counts', ascending=False)
    Combinations['Percurso'] = Combinations['CAP UTM_MEDIUM'] + ' - ' + Combinations['CAP UTM_SOURCE']
    top5_percurso = Combinations.head(5)[['Percurso', 'counts']]

    # Exibir os top 5 usando st.metric dentro de containers e colunas
    st.subheader("Top 5 UTM Source")
    with st.container(border=True):
        cols = st.columns(5)
        for col, (source, count) in zip(cols, top5_source.items()):
            col.metric(label=source, value=count)

    st.subheader("Top 5 UTM Medium")
    with st.container(border=True):
        cols = st.columns(5)
        for col, (medium, count) in zip(cols, top5_medium.items()):
            col.metric(label=medium, value=count)
    
    st.subheader("Top 5 Percurso")
    with st.container(border=True):
        cols = st.columns(5)
        for col, (percurso, count) in zip(cols, top5_percurso.values):
            col.metric(label=percurso, value=count)

    st.divider()

    # Criar o gráfico com a função e exibi-lo no Streamlit
    fig = criar_grafico_combinations(Combinations)
    st.plotly_chart(fig)
