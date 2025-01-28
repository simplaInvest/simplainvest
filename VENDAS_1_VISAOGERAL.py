import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS, K_PCOPY_DADOS, K_GRUPOS_WPP, get_df

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

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
        status.update(label="Carregados com sucesso!", state="complete", expanded=False)
loading_container.empty()

# Carregar DataFrames para lançamento selecionado
DF_PCOPY_DADOS['Se você pudesse classificar seu nível de experiência com investimentos, qual seria?'] = DF_PCOPY_DADOS['Se você pudesse classificar seu nível de experiência com investimentos, qual seria?'].replace({
        'Totalmente iniciante. Não sei nem por onde começar.' : 'Totalmente Iniciante',
        'Iniciante. Não entendo muito bem, mas invisto do meu jeito.' : 'Iniciante',
        'Intermediário. Já invisto, até fiz outros cursos de investimentos, mas sinto que falta alguma coisa.' : 'Intermediário',
        'Profissional. Já invisto e tenho ótimos resultados! Conhecimento nunca é demais!' : ' Profissional'
})

DF_CENTRAL_CAPTURA['Vendas'] = DF_CENTRAL_CAPTURA['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower()).astype(int)
DF_PTRAFEGO_DADOS['Vendas'] = DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower()).astype(int)
DF_PCOPY_DADOS['Vendas'] = DF_PCOPY_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower()).astype(int)
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
    st.metric(label = '', value = DF_PCOPY_DADOS['Vendas'].sum())
    st.metric(label = '', value = DF_CENTRAL_PREMATRICULA['Vendas'].sum())


with col3:
    st.subheader('Conversão')
    st.metric(label = '', value = f"{round((DF_CENTRAL_VENDAS.shape[0]/DF_CENTRAL_CAPTURA.shape[0])*100,2)}%")
    st.metric(label = '', value = f"{round((DF_PTRAFEGO_DADOS['Vendas'].sum()/DF_PTRAFEGO_DADOS.shape[0])*100,2)}%")
    st.metric(label = '', value = f"{round((DF_PCOPY_DADOS['Vendas'].sum()/DF_PCOPY_DADOS.shape[0])*100,2)}%")
    st.metric(label = '', value = f"{round((DF_CENTRAL_PREMATRICULA['Vendas'].sum()/DF_CENTRAL_PREMATRICULA.shape[0])*100,2)}%")

tab1, tab2 = st.tabs(['Desempenho UTMs', 'Conversão'])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        def plot_pizza_utm_source(dataframe):
            """
            Cria um gráfico de pizza para a coluna "CAP UTM_SOURCE" com as porcentagens de cada classe.

            Parâmetros:
            - dataframe: pd.DataFrame, o dataframe contendo os dados.

            Retorna:
            - fig: plotly.graph_objects.Figure, o gráfico gerado.
            """
            # Calcular a contagem de cada valor único na coluna 'CAP UTM_SOURCE'
            source_counts = dataframe['CAP UTM_SOURCE'].value_counts()

            # Criar o gráfico de pizza
            fig = px.pie(
                source_counts,
                values=source_counts,
                names=source_counts.index,
                title="Distribuição de UTM_SOURCE",
                labels={"value": "Proporção", "names": "Fonte UTM"}
            )

            # Adicionar as porcentagens nas legendas
            fig.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1, 0.1])

            return fig

        # Exemplo de uso
        fig_pizza_utm_source = plot_pizza_utm_source(DF_CENTRAL_VENDAS)
        st.plotly_chart(fig_pizza_utm_source)


    
    with col2:
        def plot_pizza_utm_medium(dataframe):
            """
            Cria um gráfico de pizza para a coluna "CAP UTM_MEDIUM" com as porcentagens de cada classe.

            Parâmetros:
            - dataframe: pd.DataFrame, o dataframe contendo os dados.

            Retorna:
            - fig: plotly.graph_objects.Figure, o gráfico gerado.
            """
            # Calcular a contagem de cada valor único na coluna 'CAP UTM_MEDIUM'
            medium_counts = dataframe['CAP UTM_MEDIUM'].value_counts()

            # Criar o gráfico de pizza
            fig = px.pie(
                medium_counts,
                values=medium_counts,
                names=medium_counts.index,
                title="Distribuição de UTM_MEDIUM",
                labels={"value": "Proporção", "names": "Meio UTM"}
            )

            # Adicionar as porcentagens nas legendas
            fig.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1, 0.1])

            return fig

        # Exemplo de uso
        fig_pizza_utm_medium = plot_pizza_utm_medium(DF_CENTRAL_VENDAS)
        st.plotly_chart(fig_pizza_utm_medium)

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

    st.subheader('Informações de Perfil')

    def plot_taxa_conversao(dataframe, coluna):
        # Calculando a taxa de conversão
        taxa_conversao = (
        dataframe.loc[dataframe[coluna] != '']  # Filtrar linhas onde a coluna não é vazia
        .groupby(coluna)['Vendas']
        .mean()
        .reset_index()
        .rename(columns={'Vendas': 'Taxa de Conversão'})
    )
        taxa_conversao['Taxa de Conversão (%)'] = taxa_conversao['Taxa de Conversão'] * 100

        # Criando o gráfico
        fig = px.bar(
            taxa_conversao,
            x='Taxa de Conversão (%)',
            y=coluna,
            orientation='h',
            title=f"Taxa de Conversão: {coluna}",
            labels={"Taxa de Conversão (%)": "Taxa de Conversão (%)", coluna : coluna}
        )

        # Adicionando valores acima das barras
        for i, row in taxa_conversao.iterrows():
            fig.add_annotation(
                x=row['Taxa de Conversão (%)'],
                y=row[coluna],
                text=f"{row['Taxa de Conversão (%)']:.2f}%",
                showarrow=False,
                font=dict(size=15),
                align='center',
                xanchor='left'
            )

        fig.update_layout(
            xaxis_title="Taxa de Conversão (%)",
            yaxis_title="Sexo"
        )

        return fig

    col1, col2 = st.columns(2)

    with col1:
        fig_sexo = plot_taxa_conversao(DF_PCOPY_DADOS, 'Qual seu sexo?')
        st.plotly_chart(fig_sexo)

        fig_filhos = plot_taxa_conversao(DF_PCOPY_DADOS, 'Você tem filhos?')
        st.plotly_chart(fig_filhos)




    with col2:
        xp_order = ['Totalmente Iniciante',
                        'Iniciante',
                        'Intermediário',
                        'Profissional',
                        'Não Informado'
                        ]
        fig_xp = plot_taxa_conversao(DF_PCOPY_DADOS, 'Se você pudesse classificar seu nível de experiência com investimentos, qual seria?')
        st.plotly_chart(fig_xp)
        if int(VERSAO_PRINCIPAL) >= 20:
            def plot_taxa_conversao_por_faixa_etaria(dataframe, intervalo=5):
                """
                Plota a taxa de conversão por faixa etária.

                Parâmetros:
                - dataframe: pd.DataFrame, o dataframe contendo os dados.
                - intervalo: int, tamanho dos intervalos de idade (padrão: 5 anos).

                Retorna:
                - fig: plotly.graph_objects.Figure, o gráfico gerado.
                """
                # Remover valores nulos e converter para numérico
                dataframe = dataframe.dropna(subset=['Qual sua idade?'])
                dataframe['Qual sua idade?'] = pd.to_numeric(dataframe['Qual sua idade?'], errors='coerce')
                dataframe = dataframe.dropna(subset=['Qual sua idade?'])

                # Criar faixas de idade
                dataframe['Faixa de Idade'] = pd.cut(
                    dataframe['Qual sua idade?'],
                    bins=range(int(dataframe['Qual sua idade?'].min()), int(dataframe['Qual sua idade?'].max()) + intervalo, intervalo),
                    right=False
                )

                # Calcular a taxa de conversão por faixa etária
                taxa_conversao = (
                    dataframe.groupby('Faixa de Idade')['Vendas']
                    .mean()
                    .reset_index()
                    .rename(columns={'Vendas': 'Taxa de Conversão'})
                )
                taxa_conversao['Taxa de Conversão (%)'] = taxa_conversao['Taxa de Conversão'] * 100

                # Criar o gráfico de barras verticais
                taxa_conversao['Faixa de Idade'] = taxa_conversao['Faixa de Idade'].astype(str)  # Converter Interval para string
                fig = px.bar(
                    taxa_conversao,
                    x='Faixa de Idade',
                    y='Taxa de Conversão (%)',
                    title="Taxa de Conversão por Faixa Etária",
                    labels={"Taxa de Conversão (%)": "Taxa de Conversão (%)", "Faixa de Idade": "Idade"}
                )

                # Adicionar valores acima das barras
                for i, row in taxa_conversao.iterrows():
                    fig.add_annotation(
                        x=row['Faixa de Idade'],
                        y=row['Taxa de Conversão (%)'],
                        text=f"{row['Taxa de Conversão (%)']:.2f}%",
                        showarrow=False,
                        font=dict(size=12),
                        align='center',
                        yanchor = 'bottom'
                    )

                fig.update_layout(
                    xaxis_title="Faixa de Idade",
                    yaxis_title="Taxa de Conversão (%)"
                )
                return fig

            fig_histograma_idade = plot_taxa_conversao_por_faixa_etaria(DF_PCOPY_DADOS)
            st.plotly_chart(fig_histograma_idade)


    def create_conversion_heatmap(dataframe):
        """
        Função para criar um heatmap de taxa de conversão com anotações.

        Args:
        dataframe (pd.DataFrame): DataFrame contendo as colunas 'PATRIMONIO', 'RENDA MENSAL', e 'Vendas'.

        Returns:
        plotly.graph_objects.Figure: Objeto do gráfico Plotly com anotações.
        """
        # Calcular a taxa de conversão e o número de instâncias por par de PATRIMÔNIO e RENDA MENSAL
        grouped = dataframe.groupby(['PATRIMONIO', 'RENDA MENSAL']).agg(
            total=('Vendas', 'size'),
            vendas=('Vendas', 'sum')
        ).reset_index()
        grouped['conversion_rate'] = grouped['vendas'] / grouped['total']

        # Pivotar os dados para o formato de heatmap
        conversion_pivot = grouped.pivot_table(
            index='PATRIMONIO', 
            columns='RENDA MENSAL', 
            values='conversion_rate', 
            fill_value=0
        )
        count_pivot = grouped.pivot_table(
            index='PATRIMONIO', 
            columns='RENDA MENSAL', 
            values='total', 
            fill_value=0
        )

        # Criar heatmap com Plotly
        fig = go.Figure(data=go.Heatmap(
            z=conversion_pivot.values,
            x=conversion_pivot.columns,
            y=conversion_pivot.index,
            colorscale='Blues',
            colorbar=dict(title='Taxa de Conversão (%)')
        ))

        # Adicionar anotações com taxa de conversão e número de instâncias
        for i, row in enumerate(conversion_pivot.index):
            for j, col in enumerate(conversion_pivot.columns):
                conversion_rate = conversion_pivot.loc[row, col] * 100  # Converter para porcentagem
                total_instances = count_pivot.loc[row, col]
                annotation_text = f"{conversion_rate:.1f}% ({total_instances})"
                fig.add_annotation(
                    x=col,
                    y=row,
                    text=annotation_text,
                    showarrow=False,
                    font=dict(color="black", size=13, family="Arial Black")
                )

        # Atualizar layout
        fig.update_layout(
            title='Mapa de Calor: Taxa de Conversão por PATRIMÔNIO e RENDA MENSAL',
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

    chart = create_conversion_heatmap(DF_PTRAFEGO_DADOS)
    chart

st.divider()