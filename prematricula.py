import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import re
from sklearn.feature_extraction.text import CountVectorizer

st.title('Pré-Matrícula')

captura_ei = st.session_state.get('df_CAPTURA', pd.DataFrame())
trafego_ei = st.session_state.get('df_PESQUISA', pd.DataFrame())
copy_ei = st.session_state.get('df_COPY', pd.DataFrame())
whatsapp_ei = st.session_state.get('df_GRUPOS', pd.DataFrame())
prematricula_ei = st.session_state.get('df_PREMATRICULA', pd.DataFrame())
versao_ei = st.session_state.get('versao')

# Configurar os filtros com multiselect
columns_to_filter = ['PM UTM_TERM', 'PM UTM_CAMPAIGN', 'PM UTM_SOURCE', 'PM UTM_MEDIUM', 'PM UTM_ADSET']

# Criar os filtros lado a lado
filters = {}
col1, col2, col3, col4, col5 = st.columns(len(columns_to_filter))

with col1:
    unique_terms = list(prematricula_ei['PM UTM_TERM'].unique())
    unique_terms.insert(0, 'TODOS')
    filters['PM UTM_TERM'] = st.multiselect("PM UTM_TERM", unique_terms, default="TODOS")

with col2:
    unique_campaigns = list(prematricula_ei['PM UTM_CAMPAIGN'].unique())
    unique_campaigns.insert(0, 'TODOS')
    filters['PM UTM_CAMPAIGN'] = st.multiselect("PM UTM_CAMPAIGN", unique_campaigns, default="TODOS")

with col3:
    unique_sources = list(prematricula_ei['PM UTM_SOURCE'].unique())
    unique_sources.insert(0, 'TODOS')
    filters['PM UTM_SOURCE'] = st.multiselect("PM UTM_SOURCE", unique_sources, default="TODOS")

with col4:
    unique_mediums = list(prematricula_ei['PM UTM_MEDIUM'].unique())
    unique_mediums.insert(0, 'TODOS')
    filters['PM UTM_MEDIUM'] = st.multiselect("PM UTM_MEDIUM", unique_mediums, default="TODOS")

with col5:
    unique_adsets = list(prematricula_ei['PM UTM_ADSET'].unique())
    unique_adsets.insert(0, 'TODOS')
    filters['PM UTM_ADSET'] = st.multiselect("PM UTM_ADSET", unique_adsets, default="TODOS")
    

# Verificar se os filtros estão vazios
if prematricula_ei.empty:
    st.warning("Selecione um filtro para visualizar os dados.")
else:
    # Filtrar os dados com base nos filtros selecionados
    filtered_prematricula_ei = prematricula_ei.copy()

    for column, selected_values in filters.items():
        if "TODOS" not in selected_values:
            filtered_prematricula_ei = filtered_prematricula_ei[filtered_prematricula_ei[column].isin(selected_values)]

    # Verificar se o DataFrame filtrado está vazio
    if filtered_prematricula_ei.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        st.divider()

# Convertendo colunas de data para datetime, se necessário
filtered_prematricula_ei['PM DATA_CAPTURA'] = pd.to_datetime(filtered_prematricula_ei['PM DATA_CAPTURA'], errors='coerce')
filtered_prematricula_ei['CAP DATA_CAPTURA'] = pd.to_datetime(filtered_prematricula_ei['CAP DATA_CAPTURA'], errors='coerce')

# Função para criar o gráfico de linhas de PM DATA_CAPTURA
@st.cache_data
def grafico_linhas_cap_data_captura(df, start_date, end_date):
    # Convertendo start_date e end_date para datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtrar dados com base no intervalo de tempo
    if int(versao_ei) == 20:
        filtered_df = df[(df['CAP DATA_CAPTURA'] >= start_date) & (df['CAP DATA_CAPTURA'] <= end_date)]
        df_grouped = filtered_df['CAP DATA_CAPTURA'].dt.date.value_counts().reset_index()
    else:
        filtered_df = df[(df['PM DATA_CAPTURA'] >= start_date) & (df['PM DATA_CAPTURA'] <= end_date)]
        df_grouped = filtered_df['PM DATA_CAPTURA'].dt.date.value_counts().reset_index()
    df_grouped.columns = ['Data', 'Contagem']
    df_grouped.sort_values(by='Data', inplace=True)

    # Gráfico de linhas com pontos
    line_chart = alt.Chart(df_grouped).mark_line(point=alt.OverlayMarkDef(color='lightblue')).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Contagem:Q', title='Número de Capturas'),
        tooltip=['Data', 'Contagem']
    )

    # Anotações dos valores nos pontos
    text_chart = alt.Chart(df_grouped).mark_text(
        align='center',
        baseline='bottom',
        color='lightblue',
        dx=0,
        dy=-10  # Ajuste vertical da anotação
    ).encode(
        x=alt.X('Data:T'),
        y=alt.Y('Contagem:Q'),
        text=alt.Text('Contagem:Q')
    )

    # Combinar os gráficos
    chart = (line_chart + text_chart).properties(
        title='Gráfico de Linhas - DATA_CAPTURA'
    )

    return chart

# Função para criar o gráfico de barras horizontais para UTM_SOURCE
@st.cache_data
def grafico_barras_horizontais_utm_source(df):
    df_grouped = df['PM UTM_SOURCE'].value_counts().reset_index()
    df_grouped.columns = ['PM UTM_SOURCE', 'Contagem']

    chart = alt.Chart(df_grouped).mark_bar(color='lightblue').encode(
        x=alt.X('Contagem:Q', title='Número de Ocorrências'),
        y=alt.Y('PM UTM_SOURCE:N', sort='-x', title='Fonte'),
        tooltip=['PM UTM_SOURCE', 'Contagem']
    ).properties(
        title='Gráfico de Barras Horizontais - UTM_SOURCE'
    )
    return chart

# Função para criar o gráfico de pizza para UTM_MEDIUM
@st.cache_data
def grafico_pizza_utm_medium(df):
    # Agrupar dados por UTM_MEDIUM
    df_grouped = df['PM UTM_MEDIUM'].value_counts(normalize=True).reset_index()
    df_grouped.columns = ['PM UTM_MEDIUM', 'Proporção']
    df_grouped['Proporção (%)'] = (df_grouped['Proporção'] * 100).round(2)  # Convertendo para porcentagem

    # Criar o gráfico de pizza
    chart = alt.Chart(df_grouped).mark_arc().encode(
        theta=alt.Theta(field='Proporção', type='quantitative', title='Proporção'),
        color=alt.Color(field='PM UTM_MEDIUM', type='nominal', title='Medium'),
        tooltip=['PM UTM_MEDIUM', alt.Tooltip('Proporção (%)', format='.2f')]
    ).properties(
        title='Gráfico de Pizza - UTM_MEDIUM'
    )

    return chart

# dataframes com os que responderam às pesquisa de trafego e copy
pm_traf = filtered_prematricula_ei[filtered_prematricula_ei['EMAIL'].isin(trafego_ei['EMAIL'])]
pm_copy = filtered_prematricula_ei[filtered_prematricula_ei['EMAIL'].isin(copy_ei['EMAIL'])]


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total", value=filtered_prematricula_ei.shape[0])
    st.metric(label = "Com pesquisa", value = pm_traf.shape[0])
    st.metric(label= 'Com copy', value = pm_copy.shape[0])

with col2:
    st.metric(label='Conversão', value = round((filtered_prematricula_ei.shape[0]/captura_ei.shape[0])*100, 2))
    st.metric(label='Proporção em relação ao total de pré-matrículas', value = round((pm_traf.shape[0]/prematricula_ei.shape[0])*100, 2))
    st.metric(label='Proporção em relação ao total de pré-matrículas', value = round((pm_copy.shape[0]/prematricula_ei.shape[0])*100, 2))

with col3:
    st.metric(label='Proporção do filtro em relação ao total', value = round((filtered_prematricula_ei.shape[0]/prematricula_ei.shape[0])*100, 2))

st.divider()

tab1, tab2 = st.tabs(["Origens","Tráfego"])

with tab1:
    st.subheader('Captação')
    if int(versao_ei) >= 20:
        # Preparar os dados para o slider
        min_date = pd.to_datetime(filtered_prematricula_ei['CAP DATA_CAPTURA'].min()).date()
        max_date = pd.to_datetime(filtered_prematricula_ei['CAP DATA_CAPTURA'].max()).date()

        # Criar o slider para selecionar o intervalo de tempo
        start_date, end_date = st.slider(
            "Selecione o intervalo de tempo:",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),  # Valores iniciais
            format="YYYY-MM-DD"
        )

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        fig = grafico_linhas_cap_data_captura(filtered_prematricula_ei, start_date, end_date)
        if fig:
            st.altair_chart(fig, use_container_width=True)

    st.subheader('Source')
    fig = grafico_barras_horizontais_utm_source(filtered_prematricula_ei)
    if fig:
        st.altair_chart(fig, use_container_width=True)

    st.subheader('Medium')
    fig = grafico_pizza_utm_medium(filtered_prematricula_ei)
    if fig:
        st.altair_chart(fig, use_container_width=True)

with tab2:
    filtered_prematricula_ei['EMAIL'] = filtered_prematricula_ei['EMAIL'].str.lower()
    trafego_ei['EMAIL'] = trafego_ei['EMAIL'].str.lower()

    # Realizar o merge com base na coluna de EMAIL
    filtered_prematricula_ei = filtered_prematricula_ei.merge(
        trafego_ei[['EMAIL', 'RENDA MENSAL', 'PATRIMONIO']],  # Colunas para juntar
        left_on='EMAIL',  # Coluna no dataframe base
        right_on='EMAIL',  # Coluna no dataframe de origem
        how='left'  # Merge à esquerda para manter todas as linhas do dataframe base
    )

    patrimonio_order = [
        'Menos de R$5 mil',
        'Entre R$5 mil e R$20 mil',
        'Entre R$20 mil e R$100 mil',
        'Entre R$100 mil e R$250 mil',
        'Entre R$250 mil e R$500 mil',
        'Entre R$500 mil e R$1 milhão',
        'Acima de R$1 milhão'
    ]

    renda_order = [
            'Menos de R$1.500',
            'Entre R$1.500 e R$2.500',
            'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$10.000',
            'Entre R$10.000 e R$20.000',
            'Acima de R$20.000'
        ]

    if 'PATRIMONIO_y' or 'RENDA MENSAL_y' in filtered_prematricula_ei.columns:
        filtered_prematricula_ei = filtered_prematricula_ei.rename(columns={"PATRIMONIO_y": "PATRIMONIO"})
        filtered_prematricula_ei = filtered_prematricula_ei.rename(columns={"RENDA MENSAL_y": "RENDA MENSAL"})
    
    # Contagem de valores por patrimônio
    patrimonio_counts = filtered_prematricula_ei['PATRIMONIO'].value_counts().reindex(patrimonio_order, fill_value=0).reset_index()
    patrimonio_counts.columns = ['PATRIMONIO', 'count']

    # Criar gráfico de barras horizontais para patrimônio
    patrimonio_chart = alt.Chart(patrimonio_counts).mark_bar().encode(
        y=alt.Y('PATRIMONIO:N', sort=patrimonio_order, title='Faixa de Patrimônio'),
        x=alt.X('count:Q', title='Quantidade de Pessoas'),
        tooltip=['PATRIMONIO:N', 'count:Q']
    ).properties(
        title='Distribuição por Patrimônio',
        width=600,
        height=400
    )

    # Adicionar os valores ao lado das barras
    patrimonio_text = alt.Chart(patrimonio_counts).mark_text(
        align='left',
        baseline='middle',
        color = 'lightblue',
        dx=3  # deslocamento horizontal
    ).encode(
        y=alt.Y('PATRIMONIO:N', sort=patrimonio_order),
        x=alt.X('count:Q'),
        text=alt.Text('count:Q')
    )

    # Combinar o gráfico e os valores
    final_patrimonio_chart = patrimonio_chart + patrimonio_text

    # Contagem de valores por renda mensal
    renda_counts = filtered_prematricula_ei['RENDA MENSAL'].value_counts().reindex(renda_order, fill_value=0).reset_index()
    renda_counts.columns = ['RENDA MENSAL', 'count']

    # Criar gráfico de barras horizontais para renda
    renda_chart = alt.Chart(renda_counts).mark_bar(color='lightgreen').encode(
        y=alt.Y('RENDA MENSAL:N', sort=renda_order, title='Faixa de Renda Mensal'),
        x=alt.X('count:Q', title='Quantidade de Pessoas'),
        tooltip=['RENDA MENSAL:N', 'count:Q']
    ).properties(
        title='Distribuição por Renda Mensal',
        width=600,
        height=400
    )

    # Adicionar os valores ao lado das barras
    renda_text = alt.Chart(renda_counts).mark_text(
        align='left',
        baseline='middle',
        color = 'lightgreen',
        dx=3  # deslocamento horizontal
    ).encode(
        y=alt.Y('RENDA MENSAL:N', sort=renda_order),
        x=alt.X('count:Q'),
        text=alt.Text('count:Q')
    )

    # Combinar o gráfico e os valores
    final_renda_chart = renda_chart + renda_text

    col1, col2 = st.columns(2)
    with col1:
        final_patrimonio_chart
        st.dataframe(filtered_prematricula_ei['PATRIMONIO'].value_counts().reindex(patrimonio_order), use_container_width = True)
    with col2:
        final_renda_chart 
        st.dataframe(filtered_prematricula_ei['RENDA MENSAL'].value_counts().reindex(renda_order), use_container_width = True)


