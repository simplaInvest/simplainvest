import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS, get_df

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

# Carregar DataFrames para lançamento selecionado
loading_container = st.empty()
with loading_container:
    status = st.status("Carregando dados...", expanded=True)
    with status:
        DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
        DF_CENTRAL_PREMATRICULA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
        DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
        DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
        status.update(label="Carregados com sucesso!", state="complete", expanded=False)
loading_container.empty()

if 'Captacao' not in st.session_state:
    Cap = []
    st.write('Lista de Captação vazia')
else:
    Cap = st.session_state['Captacao']

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

# Colunas financeiras
cols_finan_01 = 'PATRIMONIO'
cols_finan_02 = 'QUANTO_POUPA' if PRODUTO == "SW" else 'RENDA MENSAL'

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

#------------------------------------------------------------
#      02. RESUMO
#------------------------------------------------------------

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

    # 02.A: FILTROS POR ETAPA
    cols_resumo = st.columns(2)
    with cols_resumo[0]:
        options = ["Captação", "Pré-matrícula", "Vendas"]
        filters_etapas = st.multiselect(
            label="Filtros por etapa:", options=options
        )
        if filters_etapas is not None:
            if "Captação" in filters_etapas:
                filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_CAPTURA['EMAIL'].str.lower())]
            if "Pré-matrícula" in filters_etapas:
                filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_PREMATRICULA['EMAIL'].str.lower())]
            if "Vendas" in filters_etapas:
                filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower())]
        
        # 02.B: MÉTRICAS PRINCIPAIS
        st.metric(
            label="Respostas da pesquisa:",
            value=f"{filtered_DF_PTRAFEGO_DADOS.shape[0]}  ({round((filtered_DF_PTRAFEGO_DADOS.shape[0] / DF_CENTRAL_CAPTURA.shape[0]) * 100, 2)}%)"
        )

    # 02.C: MÉTRICAS PRINCIPAIS
    patrimonio_options = [
        'Todos',
        'Acima de 5 mil',
        'Acima de 20 mil',
        'Acima de 100 mil',
        'Acima de 250 mil',
        'Acima de 500 mil',
        'Acima de 1 milhão'
    ]
    patrimonio_mapping = {
        'Todos': [  'Menos de R$5 mil',
                    'Entre R$5 mil e R$20 mil',
                    'Entre R$20 mil e R$100 mil',
                    'Entre R$100 mil e R$250 mil',
                    'Entre R$250 mil e R$500 mil',
                    'Entre R$500 mil e R$1 milhão',
                    'Acima de R$1 milhão'],
        'Acima de 5 mil': ['Entre R$5 mil e R$20 mil',
                            'Entre R$20 mil e R$100 mil',
                            'Entre R$100 mil e R$250 mil',
                            'Entre R$250 mil e R$500 mil',
                            'Entre R$500 mil e R$1 milhão',
                            'Acima de R$1 milhão'],
        'Acima de 20 mil': ['Entre R$20 mil e R$100 mil',
                            'Entre R$100 mil e R$250 mil',
                            'Entre R$250 mil e R$500 mil',
                            'Entre R$500 mil e R$1 milhão',
                            'Acima de R$1 milhão'],
        'Acima de 100 mil': ['Entre R$100 mil e R$250 mil',
                            'Entre R$250 mil e R$500 mil',
                            'Entre R$500 mil e R$1 milhão',
                            'Acima de R$1 milhão'],
        'Acima de 250 mil': ['Entre R$250 mil e R$500 mil',
                            'Entre R$500 mil e R$1 milhão',
                            'Acima de R$1 milhão'],
        'Acima de 500 mil': ['Entre R$500 mil e R$1 milhão',
                            'Acima de R$1 milhão'],
        'Acima de 1 milhão': ['Acima de R$1 milhão']
    }

    renda_options = [
            'Todos',
            'Acima de R$1.500',
            'Acima de R$2.500',
            'Acima de R$5.000',
            'Acima de R$10.000',
            'Acima de R$20.000'
        ]
    renda_mapping = {
            'Todos': ['Até R$1.500',
                        'Entre R$1.500 e R$2.500',
                        'Entre R$2.500 e R$5.000',
                        'Entre R$5.000 e R$10.000',
                        'Entre R$10.000 e R$20.000',
                        'Acima de R$20.000'],
            'Acima de R$1.500': ['Entre R$1.500 e R$2.500',
                                'Entre R$2.500 e R$5.000',
                                'Entre R$5.000 e R$10.000',
                                'Entre R$10.000 e R$20.000',
                                'Acima de R$20.000'],
            'Acima de R$2.500': ['Entre R$2.500 e R$5.000',
                                'Entre R$5.000 e R$10.000',
                                'Entre R$10.000 e R$20.000',
                                'Acima de R$20.000'],
            'Acima de R$5.000': ['Entre R$5.000 e R$10.000',
                                'Entre R$10.000 e R$20.000',
                                'Acima de R$20.000'],
            'Acima de R$10.000': ['Entre R$10.000 e R$20.000',
                                'Acima de R$20.000'],
            'Acima de R$20.000': ['Acima de R$20.000']
        }
    
    quanto_poupa_options = [
        'Todos',
        'Acima de R$250',
        'Acima de R$500',
        'Acima de R$1.000',
        'Acima de R$2.500',
        'Acima de R$5.000',
        'Acima de R$15.000'
    ]
    quanto_poupa_mapping = {
        'Todos': [
            'Até R$250',
            'Entre R$250 e R$500',
            'Entre R$500 e R$1.000',
            'Entre R$1.000 e R$2.500',
            'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$15.000',
            'Acima de R$15.000'
        ],
        'Acima de R$250': [
            'Entre R$250 e R$500',
            'Entre R$500 e R$1.000',
            'Entre R$1.000 e R$2.500',
            'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$15.000',
            'Acima de R$15.000'
        ],
        'Acima de R$500': [
            'Entre R$500 e R$1.000',
            'Entre R$1.000 e R$2.500',
            'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$15.000',
            'Acima de R$15.000'
        ],
        'Acima de R$1.000': [
            'Entre R$1.000 e R$2.500',
            'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$15.000',
            'Acima de R$15.000'
        ],
        'Acima de R$2.500': [
            'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$15.000',
            'Acima de R$15.000'
        ],
        'Acima de R$5.000': [
            'Entre R$5.000 e R$15.000',
            'Acima de R$15.000'
        ],
        'Acima de R$15.000': ['Acima de R$15.000']

    }
    
    with cols_resumo[1]:
        cols_patrimonio_selector = st.columns(2)
        with cols_patrimonio_selector[0]:
            selected_patrimonio = st.selectbox("Selecione o intervalo de patrimônio:", patrimonio_options, index =1)
            patrimonio_acima_selecionado = filtered_DF_PTRAFEGO_DADOS[
                filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].isin(patrimonio_mapping[selected_patrimonio])
            ]
            selected_renda = st.selectbox('Selecione o intervalo de renda:', quanto_poupa_options if PRODUTO == "SW" else renda_options, index = 1)
            renda_acima_selecionado = filtered_DF_PTRAFEGO_DADOS[
                filtered_DF_PTRAFEGO_DADOS[cols_finan_02].isin(quanto_poupa_mapping[selected_renda] if PRODUTO == "SW" else renda_mapping[selected_renda])
            ]

            renda_patrimonio_acima_selecionado = filtered_DF_PTRAFEGO_DADOS[
                (filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].isin(patrimonio_mapping[selected_patrimonio])) &
                (filtered_DF_PTRAFEGO_DADOS[cols_finan_02].isin(quanto_poupa_mapping[selected_renda] if PRODUTO == "SW" else renda_mapping[selected_renda]))
            ]

        with cols_patrimonio_selector[1]:
            st.metric(
                label=f'{selected_patrimonio}:',
                value=f"{patrimonio_acima_selecionado.shape[0]}  "
                        f"({round((patrimonio_acima_selecionado.shape[0] / filtered_DF_PTRAFEGO_DADOS.shape[0]) * 100, 2) if filtered_DF_PTRAFEGO_DADOS.shape[0] != 0 else 0}%)"
            )
            st.metric(
                    label=f'{selected_renda}:',
                    value=f"{renda_acima_selecionado.shape[0]}  "
                            f"({round((renda_acima_selecionado.shape[0] / filtered_DF_PTRAFEGO_DADOS.shape[0]) * 100, 2) if filtered_DF_PTRAFEGO_DADOS.shape[0] != 0 else 0}%)"
                )
            st.metric(
                    label=f'Patrimônio {selected_patrimonio} e Renda {selected_renda}:',
                    value=f"{renda_patrimonio_acima_selecionado.shape[0]}  "
                            f"({round((renda_patrimonio_acima_selecionado.shape[0] / filtered_DF_PTRAFEGO_DADOS.shape[0]) * 100, 2) if filtered_DF_PTRAFEGO_DADOS.shape[0] != 0 else 0}%)"
                )

st.divider()

#------------------------------------------------------------
#      03. GRÁFICOS DE BARRAS & DATAFRAME
#------------------------------------------------------------

# DEFINE ORDEM DAS FAIXAS
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
        'Até R$1.500',
        'Entre R$1.500 e R$2.500',
        'Entre R$2.500 e R$5.000',
        'Entre R$5.000 e R$10.000',
        'Entre R$10.000 e R$20.000',
        'Acima de R$20.000'
    ]
quanto_poupa_order = [
            'Até R$250',
            'Entre R$250 e R$500',
            'Entre R$500 e R$1.000',
            'Entre R$1.000 e R$2.500',
            'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$15.000',
            'Acima de R$15.000'
    ]

secondary_order = quanto_poupa_order if PRODUTO == "SW" else renda_order

# CRIA GRÁFICO DE DISTRIBUIÇÃO EM BARRA HORIZONTAL
def create_distribution_chart(data, category_col, order_list, color='lightblue', title=''):
    # Create counts DataFrame
    counts_df = data[category_col].value_counts().reindex(order_list, fill_value=0).reset_index()
    counts_df.columns = [category_col, 'count']
    
    # Calculate percentages
    total = counts_df['count'].sum()
    counts_df['percentage'] = (counts_df['count'] / total * 100).round(1)
    counts_df['label'] = counts_df.apply(
        lambda x: f"{int(x['count'])} ({x['percentage']:.1f}%)", axis=1
    )
    
    # Create bar chart
    base_chart = alt.Chart(counts_df).mark_bar(color=color).encode(
        y=alt.Y(f'{category_col}:N', sort=order_list, title=''),
        x=alt.X('count:Q', title='Quantidade de Pessoas'),
        tooltip=[f'{category_col}:N', 'count:Q', 'percentage:Q']
    ).properties(
        width=600,
        height=400,
        title=title
    )
    
    # Add text labels
    text_chart = base_chart.mark_text(
        align='left',
        baseline='middle',
        color=color,
        dx=3
    ).encode(
        text=alt.Text('label:N')
    )
    
    return base_chart + text_chart, counts_df

# CONFIGURAÇÕES DOS GRÁFICOS
CHART_CONFIG = {
    'patrimonio': {
        'column': 'PATRIMONIO',
        'color': 'lightblue',
        'title': '',
        'display_name': 'Patrimônio'
    },
    'renda': {
        'column': cols_finan_02,
        'color': 'lightgreen',
        'title': '',
        'display_name': 'Renda' if PRODUTO == "SW" else 'Quanto poupa'
    }
}

col1, col2 = st.columns(2)

# 03.A: PATRIMÔNIO
with col1:
    st.subheader("Patrimônio")
    patrimonio_chart, patrimonio_df = create_distribution_chart(
        filtered_DF_PTRAFEGO_DADOS,
        CHART_CONFIG['patrimonio']['column'],
        patrimonio_order,
        CHART_CONFIG['patrimonio']['color'],
        CHART_CONFIG['patrimonio']['title']
    )
    st.altair_chart(patrimonio_chart)
    st.dataframe(
        patrimonio_df[['PATRIMONIO', 'count']].rename(
            columns={'PATRIMONIO': 'Patrimônio', 'count': 'Quantidade'}
        ),
        use_container_width=True,
        hide_index=True
    )

# 03.B: RENDA MENSAL
with col2:
    st.subheader("Quanto poupa" if PRODUTO == "SW" else "Renda mensal")
    renda_chart, renda_df = create_distribution_chart(
        filtered_DF_PTRAFEGO_DADOS,
        CHART_CONFIG['renda']['column'],
        secondary_order,
        CHART_CONFIG['renda']['color'],
        CHART_CONFIG['renda']['title']
    )
    renda_chart
    st.dataframe(
        renda_df[[cols_finan_02, 'count']].rename(
            columns={cols_finan_02: "Quanto poupa" if PRODUTO == "SW" else "Renda mensal", 'count': 'Quantidade'}
        ),
        use_container_width=True,
        hide_index=True
    )

st.divider()

if VERSAO_PRINCIPAL >= 21:
    def calcular_proporcoes_e_plotar(dataframe, coluna, lista_faixas):
        # 1. Filtrar dados relevantes e tratar NaNs
        dataframe = dataframe.dropna(subset=["DATA DE CAPTURA", coluna])  # Remove linhas sem data ou patrimônio.
        dataframe["DIA"] = dataframe["DATA DE CAPTURA"].dt.date  # Extrai apenas a data (ignora horas e minutos).

        # Filtrar pelo parâmetro de data_inicio
        dataframe = dataframe[dataframe["DIA"] >= pd.to_datetime(Cap[0]).date()]  



        # 2. Calcular proporções diárias por faixa de patrimônio
        proporcoes = dataframe.groupby(["DIA", coluna]).size().reset_index(name="COUNT")  # Conta leads por dia e faixa de patrimônio.
        total_por_dia = dataframe.groupby("DIA").size().reset_index(name="TOTAL")  # Conta o total de leads por dia.
        proporcoes = proporcoes.merge(total_por_dia, on="DIA")  # Junta os dois dataframes pelo dia.
        proporcoes["PROPORCAO"] = (proporcoes["COUNT"] / proporcoes["TOTAL"]) * 100  # Calcula a proporção percentual.

        proporcoes = proporcoes[proporcoes[coluna].isin(lista_faixas)]  # Filtra somente as faixas da lista
        proporcoes[coluna] = pd.Categorical(proporcoes[coluna], categories=lista_faixas, ordered=True)  # Ordena as categorias


        # 3. Gerar gradiente de cores do vermelho ao verde
        n_faixas = len(lista_faixas)
        cmap = plt.get_cmap("bwr")  # Gradiente de vermelho para verde
        colors = [cmap(i / (n_faixas - 1)) for i in range(n_faixas)]  # Gradiente normalizado
        hex_colors = [mcolors.rgb2hex(c) for c in colors]  # Converter para hexadecimal

        # 4. Criar o gráfico usando Plotly
        fig = px.line(
            proporcoes,
            x="DIA",
            y="PROPORCAO",
            color=coluna,
            title=f"Proporção Diária de Leads por Faixa de {coluna}",
            labels={"DIA": "Dia de Captação", "PROPORCAO": "Proporção (%)", coluna: f"Faixa de {coluna}"},
            color_discrete_sequence=hex_colors,  # Aplicar gradiente de cores
            category_orders={coluna: lista_faixas},
            hover_data={"COUNT": True, "TOTAL": True}
        )

        fig.update_layout(legend_title_text=f"Faixa de {coluna}")  # Adicionar título à legenda

        # Retornar o objeto fig
        return fig

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            chart = calcular_proporcoes_e_plotar(DF_PTRAFEGO_DADOS, 'PATRIMONIO', patrimonio_order)
            chart

    with col2:
        with st.container(border=True):
            chart = calcular_proporcoes_e_plotar(DF_PTRAFEGO_DADOS, cols_finan_02, secondary_order)
            chart

#------------------------------------------------------------
#      04. HEATMAP
#------------------------------------------------------------
def create_heatmap(dataframe):
    """
    Função para criar um heatmap com anotações dos valores de cada célula.
    
    Args:
    dataframe (pd.DataFrame): DataFrame contendo as colunas 'PATRIMONIO' e cols_finan_02.
    
    Returns:
    plotly.graph_objects.Figure: Objeto do gráfico Plotly com anotações.
    """
    # Criar tabela de contagem para o heatmap
    heatmap_pivot = dataframe.pivot_table(
        index='PATRIMONIO', 
        columns=cols_finan_02, 
        aggfunc='size', 
        fill_value=0
    )
    
    # Criar heatmap com Plotly
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='Blues',
        colorbar=dict(title='Quantidade')
    ))
    
    # Adicionar anotações com valores de cada célula
    for i, row in enumerate(heatmap_pivot.index):
        for j, col in enumerate(heatmap_pivot.columns):
            fig.add_annotation(
                x=col,
                y=row,
                text=str(heatmap_pivot.loc[row, col]),
                showarrow=False,
                font=dict(color="black", size = 15, family="Arial", weight="bold")
            )
    
    # Atualizar layout
    fig.update_layout(
        title='Mapa de calor: PATRIMÔNIO vs RENDA MENSAL',
        xaxis_title="Faixa de Renda Mensal",
        yaxis_title="Faixa de Patrimônio",
        xaxis=dict(categoryorder='array', categoryarray=[
            'Até R$1.500', 'Entre R$1.500 e R$2.500', 'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$10.000', 'Entre R$10.000 e R$20.000', 'Acima de R$20.000'
        ]),
        yaxis=dict(categoryorder='array', categoryarray=[
            'Menos de R$5 mil', 'Entre R$5 mil e R$20 mil', 'Entre R$20 mil e R$100 mil',
            'Entre R$100 mil e R$250 mil', 'Entre R$250 mil e R$500 mil', 'Entre R$500 mil e R$1 milhão',
            'Acima de R$1 milhão'
        ])
    )
    
    return fig

col1, col2, col3 = st.columns([1,7,1])

with col2:
    chart = create_heatmap(filtered_DF_PTRAFEGO_DADOS)

    chart