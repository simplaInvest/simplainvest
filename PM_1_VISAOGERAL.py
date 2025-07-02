import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS, K_PCOPY_DADOS, K_GRUPOS_WPP, K_CENTRAL_LANCAMENTOS, get_df
from libs.pm_visaogeral_funcs import grafico_linhas_cap_data_captura, grafico_barras_horizontais_utm_source_medium, grafico_barras_horizontais, grafico_pizza
from libs.safe_exec import executar_com_seguranca
from libs.auth_funcs import require_authentication

# Verificação obrigatória no início
require_authentication()

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]
LANCAMENTO = st.session_state["LANÇAMENTO"]

# Carregar DataFrames para lançamento selecionado
loading_container = st.empty()
with loading_container:
    status = st.status("Carregando dados...", expanded=True)
    with status:
        # Carregar DataFrames para lançamento selecionado
        DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
        DF_CENTRAL_PREMATRICULA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
        DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
        DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
        DF_PCOPY_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PCOPY_DADOS)
        DF_GRUPOS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_GRUPOS_WPP)
        DF_CENTRAL_LANCAMENTOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_LANCAMENTOS)
        status.update(label="Carregados com sucesso!", state="complete", expanded=False)
loading_container.empty()

#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("PRÉ-MATRÍCULA > VISÃO GERAL")
st.title('Pré-Matrícula')


#------------------------------------------------------------
#      01. FILTROS
#------------------------------------------------------------

# Configurar os filtros com multiselect
columns_to_filter = ['PM UTM_TERM', 'PM UTM_CAMPAIGN', 'PM UTM_SOURCE', 'PM UTM_MEDIUM', 'PM UTM_ADSET']

# Criar os filtros lado a lado
filters = {}
col1, col2, col3, col4, col5, col6 = st.columns(len(columns_to_filter)+1)

with col1:
    unique_terms = list(DF_CENTRAL_PREMATRICULA['PM UTM_TERM'].unique())
    unique_terms.insert(0, 'TODOS')
    filters['PM UTM_TERM'] = st.multiselect("PM UTM_TERM", unique_terms, default="TODOS")

with col2:
    unique_campaigns = list(DF_CENTRAL_PREMATRICULA['PM UTM_CAMPAIGN'].unique())
    unique_campaigns.insert(0, 'TODOS')
    filters['PM UTM_CAMPAIGN'] = st.multiselect("PM UTM_CAMPAIGN", unique_campaigns, default="TODOS")

with col3:
    unique_sources = list(DF_CENTRAL_PREMATRICULA['PM UTM_SOURCE'].unique())
    unique_sources.insert(0, 'TODOS')
    filters['PM UTM_SOURCE'] = st.multiselect("PM UTM_SOURCE", unique_sources, default="TODOS")

with col4:
    unique_mediums = list(DF_CENTRAL_PREMATRICULA['PM UTM_MEDIUM'].unique())
    unique_mediums.insert(0, 'TODOS')
    filters['PM UTM_MEDIUM'] = st.multiselect("PM UTM_MEDIUM", unique_mediums, default="TODOS")

with col5:
    unique_adsets = list(DF_CENTRAL_PREMATRICULA['PM UTM_ADSET'].unique())
    unique_adsets.insert(0, 'TODOS')
    filters['PM UTM_ADSET'] = st.multiselect("PM UTM_ADSET", unique_adsets, default="TODOS")

# Verificar se os filtros estão vazios
if DF_CENTRAL_PREMATRICULA.empty:
    st.warning("Selecione um filtro para visualizar os dados.")
else:
    # Filtrar os dados com base nos filtros selecionados
    filtered_DF_CENTRAL_PREMATRICULA = DF_CENTRAL_PREMATRICULA.copy()

    for column, selected_values in filters.items():
        if "TODOS" not in selected_values:
            filtered_DF_CENTRAL_PREMATRICULA = filtered_DF_CENTRAL_PREMATRICULA[filtered_DF_CENTRAL_PREMATRICULA[column].isin(selected_values)]

with col6:
    with st.container(border=True):
        st.metric(label=f'% do filtro em relação ao total', value = f'{round((filtered_DF_CENTRAL_PREMATRICULA.shape[0]/DF_CENTRAL_PREMATRICULA.shape[0])*100, 2)}%')

# Verificar se o DataFrame filtrado está vazio
if filtered_DF_CENTRAL_PREMATRICULA.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
else:
    st.divider()

# Convertendo colunas de data para datetime, se necessário
filtered_DF_CENTRAL_PREMATRICULA['PM DATA_CAPTURA'] = pd.to_datetime(
    filtered_DF_CENTRAL_PREMATRICULA['PM DATA_CAPTURA'], 
    format='%d/%m/%Y %H:%M', 
    errors='coerce'
)

filtered_DF_CENTRAL_PREMATRICULA['CAP DATA_CAPTURA'] = pd.to_datetime(
    filtered_DF_CENTRAL_PREMATRICULA['CAP DATA_CAPTURA'], 
    format='%d/%m/%Y %H:%M', 
    errors='coerce'
)

# dataframes com os que responderam às pesquisa de trafego e copy
pm_traf = filtered_DF_CENTRAL_PREMATRICULA[filtered_DF_CENTRAL_PREMATRICULA['EMAIL'].isin(DF_PTRAFEGO_DADOS['EMAIL'])]
pm_copy = filtered_DF_CENTRAL_PREMATRICULA[filtered_DF_CENTRAL_PREMATRICULA['EMAIL'].isin(DF_PCOPY_DADOS['EMAIL'])]


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(label="Total", value=filtered_DF_CENTRAL_PREMATRICULA.shape[0])

with col2:
    st.metric(label='Conversão', value = f'{round((filtered_DF_CENTRAL_PREMATRICULA.shape[0]/DF_CENTRAL_CAPTURA.shape[0])*100, 2)}%')

with col3:
    st.metric(label = "Com pesquisa", value = f'{pm_traf.shape[0]} ({round((pm_traf.shape[0]/DF_CENTRAL_PREMATRICULA.shape[0])*100, 2)}%)')

with col4:
    st.metric(label= 'Com copy', value = f'{pm_copy.shape[0]} ({round((pm_copy.shape[0]/DF_CENTRAL_PREMATRICULA.shape[0])*100, 2)}%)')

st.divider()

tab1, tab2 = st.tabs(["Trackeamento","Pesquisa"])

with tab1:
    st.subheader('Captação')
    if int(VERSAO_PRINCIPAL) >= 20:
        # Preparar os dados para o slider
        min_date = pd.to_datetime(DF_CENTRAL_LANCAMENTOS.loc[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANCAMENTO, 'PM_INICIO'].values[0], dayfirst=True).date()
        max_date = pd.to_datetime(DF_CENTRAL_LANCAMENTOS.loc[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANCAMENTO, 'PM_FIM'].values[0], dayfirst=True).date()

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

        executar_com_seguranca("GRÁFICO DE LINHAS DE CAP DATA CAPTURA", lambda:grafico_linhas_cap_data_captura(filtered_DF_CENTRAL_PREMATRICULA, start_date, end_date, VERSAO_PRINCIPAL))
        

    st.divider()

    with st.container(border=True):
        st.subheader('Source/Medium')
        executar_com_seguranca("GRÁFICO DE BARRAS HORIZONTAIS UTM SOURCE MEDIUM", lambda:grafico_barras_horizontais_utm_source_medium(filtered_DF_CENTRAL_PREMATRICULA))
    

    lista_colunas = ['PM UTM_SOURCE', 'PM UTM_MEDIUM', 'PM UTM_ADSET', 'PM UTM_TERM']

    for coluna in lista_colunas:
        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                executar_com_seguranca("GRÁFICO DE BARRAS HORIZONTAIS", lambda:grafico_barras_horizontais(filtered_DF_CENTRAL_PREMATRICULA, coluna))

        with col2:
            with st.container(border=True):
                executar_com_seguranca("GRÁFICO DE PIZZA", lambda:grafico_pizza(filtered_DF_CENTRAL_PREMATRICULA, coluna))


with tab2:
    filtered_DF_CENTRAL_PREMATRICULA['EMAIL'] = filtered_DF_CENTRAL_PREMATRICULA['EMAIL'].str.lower()
    DF_PTRAFEGO_DADOS['EMAIL'] = DF_PTRAFEGO_DADOS['EMAIL'].str.lower()

    # Realizar o merge com base na coluna de EMAIL
    filtered_DF_CENTRAL_PREMATRICULA = filtered_DF_CENTRAL_PREMATRICULA.merge(
        DF_PTRAFEGO_DADOS[['EMAIL', 'RENDA MENSAL', 'PATRIMONIO']],  # Colunas para juntar
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

    if 'PATRIMONIO_y' or 'RENDA MENSAL_y' in filtered_DF_CENTRAL_PREMATRICULA.columns:
        filtered_DF_CENTRAL_PREMATRICULA = filtered_DF_CENTRAL_PREMATRICULA.rename(columns={"PATRIMONIO_y": "PATRIMONIO"})
        filtered_DF_CENTRAL_PREMATRICULA = filtered_DF_CENTRAL_PREMATRICULA.rename(columns={"RENDA MENSAL_y": "RENDA MENSAL"})
    
    # Contagem de valores por patrimônio
    patrimonio_counts = filtered_DF_CENTRAL_PREMATRICULA['PATRIMONIO'].value_counts().reindex(patrimonio_order, fill_value=0).reset_index()
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
    renda_counts = filtered_DF_CENTRAL_PREMATRICULA['RENDA MENSAL'].value_counts().reindex(renda_order, fill_value=0).reset_index()
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
        st.dataframe(filtered_DF_CENTRAL_PREMATRICULA['PATRIMONIO'].value_counts().reindex(patrimonio_order), use_container_width = True)
    with col2:
        final_renda_chart 
        st.dataframe(filtered_DF_CENTRAL_PREMATRICULA['RENDA MENSAL'].value_counts().reindex(renda_order), use_container_width = True)


