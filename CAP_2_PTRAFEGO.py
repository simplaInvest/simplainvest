import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS, get_df

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

# Carregar DataFrames para lançamento selecionado
DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
DF_CENTRAL_PREMATRICULA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)

#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("CAPTAÇÃO > PESQUISA DE TRÁFEGO")
st.title('Pesquisa de Tráfego')

#------------------------------------------------------------
#      01. FILTROS
#------------------------------------------------------------

# Colunas a serem filtradas
columns_to_filter = ['UTM_TERM', 'UTM_CAMPAIGN', 'UTM_SOURCE', 'UTM_MEDIUM', 'UTM_ADSET']

# Criar os filtros lado a lado
filters = {}
cols_filters = st.columns(len(columns_to_filter))

## 1.A Anúncios (utm_term)
with cols_filters[0]:
    unique_terms = list(DF_PTRAFEGO_DADOS['UTM_TERM'].unique())
    unique_terms.insert(0, 'TODOS')
    filters['UTM_TERM'] = st.multiselect("**Anúncios** *(utm_term)*", unique_terms, default="TODOS")

## 1.B Campanhas (utm_campaign)
with cols_filters[1]:
    unique_campaigns = list(DF_PTRAFEGO_DADOS['UTM_CAMPAIGN'].unique())
    unique_campaigns.insert(0, 'TODOS')
    filters['UTM_CAMPAIGN'] = st.multiselect("**Campanhas** *(utm_campaign)*", unique_campaigns, default="TODOS")

## 1.C Origens (utm_source)
with cols_filters[2]:
    unique_sources = list(DF_PTRAFEGO_DADOS['UTM_SOURCE'].unique())
    unique_sources.insert(0, 'TODOS')
    filters['UTM_SOURCE'] = st.multiselect("**Origens** *(utm_source)*", unique_sources, default="TODOS")

## 1.D Mídias (utm_medium)
with cols_filters[3]:
    unique_mediums = list(DF_PTRAFEGO_DADOS['UTM_MEDIUM'].unique())
    unique_mediums.insert(0, 'TODOS')
    filters['UTM_MEDIUM'] = st.multiselect("**Mídias** *(utm_medium)*", unique_mediums, default="TODOS")

## 1.E Conjuntos (utm_adset)
with cols_filters[4]:
    unique_adsets = list(DF_PTRAFEGO_DADOS['UTM_ADSET'].unique())
    unique_adsets.insert(0, 'TODOS')
    filters['UTM_ADSET'] = st.multiselect("**Conjuntos** *(utm_adset)*", unique_adsets, default="TODOS")

# Filtrar os dados com base nos filtros selecionados
filtered_DF_PTRAFEGO_DADOS = DF_PTRAFEGO_DADOS.copy()


for column, selected_values in filters.items():
    if "TODOS" not in selected_values:
        filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS[column].isin(selected_values)]

# Verificar se o DataFrame filtrado está vazio
if filtered_DF_PTRAFEGO_DADOS.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
else:
    st.divider()

    # Métrica de total de respostas
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Respostas da pesquisa:",
            value=f"{filtered_DF_PTRAFEGO_DADOS.shape[0]}  ({round((filtered_DF_PTRAFEGO_DADOS.shape[0] / DF_CENTRAL_CAPTURA.shape[0]) * 100, 2)}%)"
        )

    # Selectbox e métrica condicionada
    patrimonio_options = [
        'Mais de 5 mil',
        'Mais de 20 mil',
        'Mais de 100 mil',
        'Mais de 250 mil',
        'Mais de 500 mil',
        'Mais de 1 milhão'
    ]

    patrimonio_mapping = {
        'Mais de 5 mil': ['Entre R$5 mil e R$20 mil',
                            'Entre R$20 mil e R$100 mil',
                            'Entre R$100 mil e R$250 mil',
                            'Entre R$250 mil e R$500 mil',
                            'Entre R$500 mil e R$1 milhão',
                            'Acima de R$1 milhão'],
        'Mais de 20 mil': ['Entre R$20 mil e R$100 mil',
                            'Entre R$100 mil e R$250 mil',
                            'Entre R$250 mil e R$500 mil',
                            'Entre R$500 mil e R$1 milhão',
                            'Acima de R$1 milhão'],
        'Mais de 100 mil': ['Entre R$100 mil e R$250 mil',
                            'Entre R$250 mil e R$500 mil',
                            'Entre R$500 mil e R$1 milhão',
                            'Acima de R$1 milhão'],
        'Mais de 250 mil': ['Entre R$250 mil e R$500 mil',
                            'Entre R$500 mil e R$1 milhão',
                            'Acima de R$1 milhão'],
        'Mais de 500 mil': ['Entre R$500 mil e R$1 milhão',
                            'Acima de R$1 milhão'],
        'Mais de 1 milhão': ['Acima de R$1 milhão']
    }

    with col2:
        selected_patrimonio = st.selectbox("Selecione o intervalo de patrimônio:", patrimonio_options)
        patrimonio_acima_selecionado = filtered_DF_PTRAFEGO_DADOS[
            filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].isin(patrimonio_mapping[selected_patrimonio])
        ]
        st.metric(
            label=f'Patrimônio {selected_patrimonio}:',
            value=f"{patrimonio_acima_selecionado.shape[0]}  "
                    f"({round((patrimonio_acima_selecionado.shape[0] / filtered_DF_PTRAFEGO_DADOS.shape[0]) * 100, 2)}%)"
        )

    prematricula_filter = st.checkbox("Pré-matrícula")

    # Aplicar o filtro de pré-matrícula se a opção estiver marcada
    if prematricula_filter:
        filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_PREMATRICULA['EMAIL'].str.lower())]

    vendas_filter = st.checkbox("Venda")

    # Aplicar o filtro de pré-matrícula se a opção estiver marcada
    if vendas_filter:
        filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower())]

    st.divider()

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

# Contagem de valores por patrimônio
patrimonio_counts = filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].value_counts().reindex(patrimonio_order, fill_value=0).reset_index()
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
renda_counts = filtered_DF_PTRAFEGO_DADOS['RENDA MENSAL'].value_counts().reindex(renda_order, fill_value=0).reset_index()
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
    st.dataframe(filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].value_counts().reindex(patrimonio_order), use_container_width = True)
with col2:
    final_renda_chart 
    st.dataframe(filtered_DF_PTRAFEGO_DADOS['RENDA MENSAL'].value_counts().reindex(renda_order), use_container_width = True)
