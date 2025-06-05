import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS, K_PCOPY_DADOS, K_GRUPOS_WPP, K_CENTRAL_LANCAMENTOS, get_df
from libs.vendas_visaogeral_funcs import plot_pizza_utm_source, plot_pizza_utm_medium, plot_taxa_conversao, plot_taxa_conversao_por_faixa_etaria, create_conversion_heatmap, create_conversion_table, plot_conversao_por_dia, utm_source_medium_vendas, plot_utm_pie_chart, vendas_por_hora
from libs.safe_exec import executar_com_seguranca

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

if PRODUTO == "EI":
    # Carregar DataFrames para lançamento selecionado
    DF_PCOPY_DADOS['Se você pudesse classificar seu nível de experiência com investimentos, qual seria?'] = DF_PCOPY_DADOS['Se você pudesse classificar seu nível de experiência com investimentos, qual seria?'].replace({
            'Totalmente iniciante. Não sei nem por onde começar.' : 'Totalmente Iniciante',
            'Iniciante. Não entendo muito bem, mas invisto do meu jeito.' : 'Iniciante',
            'Intermediário. Já invisto, até fiz outros cursos de investimentos, mas sinto que falta alguma coisa.' : 'Intermediário',
            'Profissional. Já invisto e tenho ótimos resultados! Conhecimento nunca é demais!' : ' Profissional'
    })


DF_CENTRAL_CAPTURA['Vendas'] = DF_CENTRAL_CAPTURA['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower()).astype(int)
DF_PTRAFEGO_DADOS['Vendas'] = DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower()).astype(int)
if PRODUTO == "EI":
    DF_PCOPY_DADOS['Vendas'] = DF_PCOPY_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower()).astype(int)
if PRODUTO == "EI":
    DF_CENTRAL_PREMATRICULA['Vendas'] = DF_CENTRAL_PREMATRICULA['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower()).astype(int)

#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("VENDAS > VISÃO GERAL")
st.title('Central de Vendas')


#------------------------------------------------------------
#      01. FILTROS
#------------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('Leads')
    st.metric(label = 'Captação', value = DF_CENTRAL_CAPTURA.shape[0])
    st.metric(label = 'Trafego', value = DF_PTRAFEGO_DADOS.shape[0])
    st.metric(label = 'Copy', value = DF_PCOPY_DADOS.shape[0])
    st.metric(label = 'Pré-Matrícula', value = DF_CENTRAL_PREMATRICULA.shape[0])

with col2:
    st.subheader('Vendas')
    st.metric(label = '', value = DF_CENTRAL_VENDAS.shape[0])
    st.metric(label = '', value = DF_PTRAFEGO_DADOS['Vendas'].sum())
    if PRODUTO == "EI":
        st.metric(label = '', value = DF_PCOPY_DADOS['Vendas'].sum())
    if PRODUTO == "EI":
        st.metric(label = '', value = DF_CENTRAL_PREMATRICULA['Vendas'].sum())


with col3:
    st.subheader('Conversão')
    st.metric(label = '', value = f"{round((DF_CENTRAL_VENDAS.shape[0]/DF_CENTRAL_CAPTURA.shape[0])*100,2)}%")
    st.metric(label = '', value = f"{round((DF_PTRAFEGO_DADOS['Vendas'].sum()/DF_PTRAFEGO_DADOS.shape[0])*100,2)}%")
    if PRODUTO == "EI":
        st.metric(label = '', value = f"{round((DF_PCOPY_DADOS['Vendas'].sum()/DF_PCOPY_DADOS.shape[0])*100,2)}%")
    if PRODUTO == "EI":
        st.metric(label = '', value = f"{round((DF_CENTRAL_PREMATRICULA['Vendas'].sum()/DF_CENTRAL_PREMATRICULA.shape[0])*100,2)}%")

st.divider()

tab1, tab2 = st.tabs(['Desempenho UTMs', 'Conversão'])

with tab1:
    col1, col2 = st.columns([1,2])

    with col1:
        combination_counts = executar_com_seguranca("GRÁFICO DE PIZZA UTM SOURCE", lambda:utm_source_medium_vendas(DF_CENTRAL_VENDAS))
        combination_counts

    with col2:
        pie_chart = executar_com_seguranca("GRÁFICO DE PIZZA UTM MEDIUM", lambda:plot_utm_pie_chart(combination_counts))
        st.plotly_chart(pie_chart)

with tab2:
    st.subheader('Informações Financeiras')
    col1, col2 = st.columns(2)

    with col1:
        # Ordem das classes de renda
        renda_order = [
            'Até R$1.500',
            'Entre R$1.500 e R$2.500',
            'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$10.000',
            'Entre R$10.000 e R$20.000',
            'Acima de R$20.000'
        ]

        def calcular_e_plotar_taxa_conversao(dataframe, coluna_renda, coluna_vendas, ordem_renda):
            """
            Calcula a taxa de conversão por faixa de renda e produz um gráfico de barras horizontais.

            Parâmetros:
            - dataframe: pd.DataFrame, o dataframe contendo os dados.
            - coluna_renda: str, o nome da coluna que representa a faixa de renda.
            - coluna_vendas: str, o nome da coluna que contém as informações binárias de venda (1 ou 0).
            - ordem_renda: list, uma lista com a ordem das categorias de renda.

            Retorna:
            - fig: plotly.graph_objects.Figure, o gráfico de barras horizontais com anotações.
            """

            # Configurando a coluna de renda com a ordem correta
            dataframe[coluna_renda] = pd.Categorical(dataframe[coluna_renda], categories=ordem_renda, ordered=True)
            
            # Calculando a taxa de conversão
            conversion_rate = dataframe.groupby(coluna_renda)[coluna_vendas].mean().reset_index()
            conversion_rate.rename(columns={coluna_vendas: 'Taxa de Conversão'}, inplace=True)
            conversion_rate['Taxa de Conversão (%)'] = conversion_rate['Taxa de Conversão'] * 100

            # Criando o gráfico de barras horizontais
            fig = px.bar(
                conversion_rate,
                x="Taxa de Conversão",
                y=coluna_renda,
                orientation='h',
                title="Taxa de Conversão por Faixa de Renda",
                labels={"Taxa de Conversão": "Taxa de Conversão (%)", coluna_renda: "Faixa de Renda"}
            )

            # Adicionando as anotações de valores
            for i, row in conversion_rate.iterrows():
                fig.add_annotation(
                    x=row["Taxa de Conversão"],
                    y=row[coluna_renda],
                    text=f"{row['Taxa de Conversão (%)']:.2f}%",
                    showarrow=False,
                    font=dict(size=12),
                    align='center',
                    xanchor='left'
                )

            # Ajustando layout do gráfico e configurando o limite do eixo X
            fig.update_layout(
                xaxis_title="Taxa de Conversão (%)",
                yaxis_title="Faixa de Renda",
                xaxis=dict(range=[0, 0.025])  # Limite do eixo X
            )
            
            return fig

        # Exemplo de uso
        fig = calcular_e_plotar_taxa_conversao(DF_PTRAFEGO_DADOS, "RENDA MENSAL", "Vendas", renda_order)

        # Mostrar o gráfico no Streamlit
        st.plotly_chart(fig)
            
        
    with col2:
        def calcular_e_plotar_taxa_conversao(dataframe, coluna_categoria, coluna_vendas, ordem_categoria):
            """
            Calcula a taxa de conversão por categoria (ex.: PATRIMÔNIO ou RENDA) e produz um gráfico de barras horizontais.

            Parâmetros:
            - dataframe: pd.DataFrame, o dataframe contendo os dados.
            - coluna_categoria: str, o nome da coluna que representa a categoria (ex.: PATRIMÔNIO).
            - coluna_vendas: str, o nome da coluna que contém as informações binárias de venda (1 ou 0).
            - ordem_categoria: list, uma lista com a ordem das categorias.

            Retorna:
            - fig: plotly.graph_objects.Figure, o gráfico de barras horizontais com anotações.
            """

            # Configurando a coluna de categoria com a ordem correta
            dataframe[coluna_categoria] = pd.Categorical(dataframe[coluna_categoria], categories=ordem_categoria, ordered=True)
            
            # Calculando a taxa de conversão
            conversion_rate = dataframe.groupby(coluna_categoria)[coluna_vendas].mean().reset_index()
            conversion_rate.rename(columns={coluna_vendas: 'Taxa de Conversão'}, inplace=True)
            conversion_rate['Taxa de Conversão (%)'] = conversion_rate['Taxa de Conversão'] * 100

            # Criando o gráfico de barras horizontais
            fig = px.bar(
                conversion_rate,
                x="Taxa de Conversão",
                y=coluna_categoria,
                orientation='h',
                title=f"Taxa de Conversão por {coluna_categoria}",
                labels={"Taxa de Conversão": "Taxa de Conversão (%)", coluna_categoria: coluna_categoria}
            )

            # Adicionando as anotações de valores
            for i, row in conversion_rate.iterrows():
                fig.add_annotation(
                    x=row["Taxa de Conversão"],
                    y=row[coluna_categoria],
                    text=f"{row['Taxa de Conversão (%)']:.2f}%",
                    showarrow=False,
                    font=dict(size=12),
                    align='center',
                    xanchor='left'
                )

            # Ajustando layout do gráfico e configurando o limite do eixo X
            fig.update_layout(
                xaxis_title="Taxa de Conversão (%)",
                yaxis_title=coluna_categoria,
                xaxis=dict(range=[0, 0.03])  # Limite do eixo X
            )
            
            return fig

        # Exemplo de uso
        patrimonio_order = [
            'Menos de R$5 mil',
            'Entre R$5 mil e R$20 mil',
            'Entre R$20 mil e R$100 mil',
            'Entre R$100 mil e R$250 mil',
            'Entre R$250 mil e R$500 mil',
            'Entre R$500 mil e R$1 milhão',
            'Acima de R$1 milhão'
        ]

        fig = calcular_e_plotar_taxa_conversao(DF_PTRAFEGO_DADOS, "PATRIMONIO", "Vendas", patrimonio_order)

        # Mostrar o gráfico no Streamlit
        st.plotly_chart(fig)

    if PRODUTO == 'EI':
        st.subheader('Informações de Perfil')

        col1, col2 = st.columns(2)

        with col1:
            executar_com_seguranca("GRÁFICO DE PIZZA SEXO", lambda:plot_taxa_conversao(DF_PCOPY_DADOS, 'Qual seu sexo?'))
            
            executar_com_seguranca("GRÁFICO DE PIZZA FILHOS", lambda:plot_taxa_conversao(DF_PCOPY_DADOS, 'Você tem filhos?'))

        with col2:
            xp_order = ['Totalmente Iniciante',
                            'Iniciante',
                            'Intermediário',
                            'Profissional',
                            'Não Informado'
                            ]
            executar_com_seguranca("CONVERSÃO POR XP", lambda:plot_taxa_conversao(DF_PCOPY_DADOS, 'Se você pudesse classificar seu nível de experiência com investimentos, qual seria?'))
            if int(VERSAO_PRINCIPAL) >= 20:
                executar_com_seguranca("CONVERSÃO POR FAIXA ETÁRIA", lambda:plot_taxa_conversao_por_faixa_etaria(DF_PCOPY_DADOS))

    executar_com_seguranca("MAPA DE CONVERSÃO", lambda:create_conversion_heatmap(DF_PTRAFEGO_DADOS))

executar_com_seguranca("TABELA DE CONVERSÃO", lambda:create_conversion_table(DF_PTRAFEGO_DADOS))

executar_com_seguranca("CONVERSÃO POR DIA", lambda:plot_conversao_por_dia(DF_CENTRAL_CAPTURA, DF_CENTRAL_VENDAS, DF_CENTRAL_LANCAMENTOS, LANCAMENTO, PRODUTO, VERSAO_PRINCIPAL))

st.divider()

# Carregar dados
DF_CENTRAL_VENDAS["VENDA DATA_VENDA"] = pd.to_datetime(DF_CENTRAL_VENDAS["VENDA DATA_VENDA"], errors='coerce')

# Filtros
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    campaign = st.selectbox("UTM_CAMPAIGN", ["Todos"] + sorted(DF_CENTRAL_VENDAS["UTM_CAMPAIGN"].dropna().unique()))
with col2:
    source = st.selectbox("UTM_SOURCE", ["Todos"] + sorted(DF_CENTRAL_VENDAS["UTM_SOURCE"].dropna().unique()))
with col3:
    medium = st.selectbox("UTM_MEDIUM", ["Todos"] + sorted(DF_CENTRAL_VENDAS["UTM_MEDIUM"].dropna().unique()))
with col4:
    adset = st.selectbox("UTM_ADSET", ["Todos"] + sorted(DF_CENTRAL_VENDAS["UTM_ADSET"].dropna().unique()))
with col5:
    content = st.selectbox("UTM_CONTENT", ["Todos"] + sorted(DF_CENTRAL_VENDAS["UTM_CONTENT"].dropna().unique()))

# Aplicar filtros
filtered_df = DF_CENTRAL_VENDAS.copy()
if campaign != "Todos":
    filtered_df = filtered_df[filtered_df["UTM_CAMPAIGN"] == campaign]
if source != "Todos":
    filtered_df = filtered_df[filtered_df["UTM_SOURCE"] == source]
if medium != "Todos":
    filtered_df = filtered_df[filtered_df["UTM_MEDIUM"] == medium]
if adset != "Todos":
    filtered_df = filtered_df[filtered_df["UTM_ADSET"] == adset]
if content != "Todos":
    filtered_df = filtered_df[filtered_df["UTM_CONTENT"] == content]

# Criar coluna de hora inteira
filtered_df["Hora da Venda"] = filtered_df["VENDA DATA_VENDA"].dt.hour

fig = executar_com_seguranca("VENDAS POR HORA", lambda:vendas_por_hora(filtered_df))

st.plotly_chart(fig)

