import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import unquote_plus

def criar_grafico_combinations(df):
    df_top10 = df.sort_values(by='counts', ascending=False)
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
        title='Combinações UTM Medium + UTM Source',
        xaxis_title='',
        yaxis_title='',
        yaxis=dict(
            automargin=True,
            tickfont=dict(size=16),
        ),
        xaxis=dict(
            tickfont=dict(size=20)
        ),
        title_font=dict(size=40, color='lightblue'),
        margin=dict(l=120, r=40, t=120, b=40),
        height=700
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

    st.markdown("<h2 style='text-align: center; font-size: 3.2vw; margin-bottom: 40px; margin-top: 40px; color: gold;hover-color: red'>Dashboard de UTMs</h2>", unsafe_allow_html=True)

    # Exibir os top 5 usando st.metric dentro de containers e colunas
    st.markdown("""<h2 style='text-align: left; font-size: 2vw; margin-bottom: 28px; color: lightblue;'> Top 5 UTM Source</h2><style> h2:hover {{color: red;}}</style>""", unsafe_allow_html=True)
    with st.container(border=True):
        cols = st.columns(5)
        for col, (source, count) in zip(cols, top5_source.items()):
            col.metric(label=source, value=count)

    st.markdown("""<h2 style='text-align: left; font-size: 2vw; margin-bottom: 28px; color: lightblue;'> Top 5 UTM Medium</h2><style> h2:hover {{color: red;}}</style>""", unsafe_allow_html=True)
    with st.container(border=True):
        cols = st.columns(5)
        for col, (medium, count) in zip(cols, top5_medium.items()):
            col.metric(label=medium, value=count)
    
    st.markdown("""<h2 style='text-align: left; font-size: 2vw; margin-bottom: 28px; color: lightblue;'> Top 5 UTM Percurso</h2><style> h2:hover {{color: red;}}</style>""", unsafe_allow_html=True)
    with st.container(border=True):
        cols = st.columns(5)
        for col, (percurso, count) in zip(cols, top5_percurso.values):
            col.metric(label=percurso, value=count)

    st.divider()

    # Criar o gráfico com a função e exibi-lo no Streamlit
    fig = criar_grafico_combinations(Combinations)
    st.plotly_chart(fig)
