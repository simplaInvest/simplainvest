import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px

captura_ei = st.session_state.get('df_CAPTURA', pd.DataFrame())
trafego_ei = st.session_state.get('df_PESQUISA', pd.DataFrame())

st.title('Pesquisa de tráfego')
# Configurar os filtros com multiselect
columns_to_filter = ['UTM_TERM', 'UTM_CAMPAIGN', 'UTM_SOURCE', 'UTM_MEDIUM', 'UTM_ADSET']

# Criar os filtros lado a lado
filters = {}
col1, col2, col3, col4, col5 = st.columns(len(columns_to_filter))

with col1:
    unique_terms = list(trafego_ei['UTM_TERM'].unique())
    unique_terms.insert(0, 'TODOS')
    filters['UTM_TERM'] = st.multiselect("UTM_TERM", unique_terms, default="TODOS")

with col2:
    unique_campaigns = list(trafego_ei['UTM_CAMPAIGN'].unique())
    unique_campaigns.insert(0, 'TODOS')
    filters['UTM_CAMPAIGN'] = st.multiselect("UTM_CAMPAIGN", unique_campaigns, default="TODOS")

with col3:
    unique_sources = list(trafego_ei['UTM_SOURCE'].unique())
    unique_sources.insert(0, 'TODOS')
    filters['UTM_SOURCE'] = st.multiselect("UTM_SOURCE", unique_sources, default="TODOS")

with col4:
    unique_mediums = list(trafego_ei['UTM_MEDIUM'].unique())
    unique_mediums.insert(0, 'TODOS')
    filters['UTM_MEDIUM'] = st.multiselect("UTM_MEDIUM", unique_mediums, default="TODOS")

with col5:
    unique_adsets = list(trafego_ei['UTM_ADSET'].unique())
    unique_adsets.insert(0, 'TODOS')
    filters['UTM_ADSET'] = st.multiselect("UTM_ADSET", unique_adsets, default="TODOS")

# Verificar se os filtros estão vazios
if trafego_ei.empty:
    st.warning("Selecione um filtro para visualizar os dados.")
else:
    # Filtrar os dados com base nos filtros selecionados
    filtered_trafego_ei = trafego_ei.copy()

    for column, selected_values in filters.items():
        if "TODOS" not in selected_values:
            filtered_trafego_ei = filtered_trafego_ei[filtered_trafego_ei[column].isin(selected_values)]

    # Verificar se o DataFrame filtrado está vazio
    if filtered_trafego_ei.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        st.divider()

        # Métrica de total de respostas
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Respostas da pesquisa:",
                value=f"{filtered_trafego_ei.shape[0]}  ({round((filtered_trafego_ei.shape[0] / captura_ei.shape[0]) * 100, 2)}%)"
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
            patrimonio_acima_selecionado = filtered_trafego_ei[
                filtered_trafego_ei['PATRIMONIO'].isin(patrimonio_mapping[selected_patrimonio])
            ]
            st.metric(
                label=f'Patrimônio {selected_patrimonio}:',
                value=f"{patrimonio_acima_selecionado.shape[0]}  "
                      f"({round((patrimonio_acima_selecionado.shape[0] / filtered_trafego_ei.shape[0]) * 100, 2)}%)"
            )

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
patrimonio_counts = filtered_trafego_ei['PATRIMONIO'].value_counts().reindex(patrimonio_order, fill_value=0).reset_index()
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
renda_counts = filtered_trafego_ei['RENDA MENSAL'].value_counts().reindex(renda_order, fill_value=0).reset_index()
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
    st.dataframe(filtered_trafego_ei['PATRIMONIO'].value_counts().reindex(patrimonio_order), use_container_width = True)
with col2:
    final_renda_chart 
    st.dataframe(filtered_trafego_ei['RENDA MENSAL'].value_counts().reindex(renda_order), use_container_width = True)
