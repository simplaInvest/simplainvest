import plotly.express as px
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

    st.plotly_chart(fig, use_container_width=True)

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

    st.plotly_chart(fig, use_container_width=True)

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

    st.plotly_chart(fig, use_container_width=True)

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
    st.plotly_chart(fig, use_container_width=True)

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

        st.plotly_chart(fig, use_container_width=True)

def create_conversion_table(DF_PTRAFEGO_DADOS):
    # Calcular a taxa de conversão para cada faixa de patrimônio e renda
    taxas_patrimonio = DF_PTRAFEGO_DADOS.groupby('PATRIMONIO')['Vendas'].mean() * 100
    taxas_renda = DF_PTRAFEGO_DADOS.groupby('RENDA MENSAL')['Vendas'].mean() * 100

    taxas_patrimonio = taxas_patrimonio.round(2).astype(str) + '%'
    taxas_renda = taxas_renda.round(2).astype(str) + '%'

    # Calculando número absoluto de leads
    leads_patrimonio = DF_PTRAFEGO_DADOS.groupby('PATRIMONIO').size()
    leads_renda = DF_PTRAFEGO_DADOS.groupby('RENDA MENSAL').size()

    # Calculando número absoluto de compradores
    compradores_patrimonio = DF_PTRAFEGO_DADOS.groupby('PATRIMONIO')['Vendas'].sum()
    compradores_renda = DF_PTRAFEGO_DADOS.groupby('RENDA MENSAL')['Vendas'].sum()

    # Criar os índices e estrutura do DataFrame
    headers = [('Patrimônio', col) for col in taxas_patrimonio.index] + [('Renda', col) for col in taxas_renda.index]
    multi_index = pd.MultiIndex.from_tuples(headers)

    # Criar a tabela com 3 linhas (Taxa de conversão, Leads, Compradores)
    tabela_taxas = pd.DataFrame([
        list(taxas_patrimonio) + list(taxas_renda),
        list(leads_patrimonio) + list(leads_renda),
        list(compradores_patrimonio) + list(compradores_renda)
    ], index=['Taxa de Conversão', 'Total de Leads', 'Total de Compradores'], columns=multi_index)

  
    st.dataframe(tabela_taxas, hide_index=False, use_container_width=True)

def plot_conversao_por_dia(
    DF_CENTRAL_CAPTURA,
    DF_CENTRAL_VENDAS,
    DF_CENTRAL_LANCAMENTOS,
    LANCAMENTO,
    PRODUTO,
    VERSAO_PRINCIPAL
    ):

    # Criar a coluna AVENDA (1 se o e-mail está em DF_CENTRAL_VENDAS, 0 caso contrário)
    DF_CENTRAL_CAPTURA['AVENDA'] = DF_CENTRAL_CAPTURA['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL']).astype(int)

    # Converter CAP DATA_CAPTURA para datetime e extrair apenas a data
    DF_CENTRAL_CAPTURA['DATA'] = pd.to_datetime(DF_CENTRAL_CAPTURA['CAP DATA_CAPTURA'], format='%d/%m/%Y %H:%M').dt.date

    # Calcular a taxa de conversão por dia
    df_conversao = DF_CENTRAL_CAPTURA.groupby('DATA').agg(
        total_entradas=('AVENDA', 'count'),
        total_convertidos=('AVENDA', 'sum')
    ).reset_index()

    df_conversao['taxa_conversao'] = (df_conversao['total_convertidos'] / df_conversao['total_entradas']) * 100

    # Obter intervalo de datas do lançamento
    min_date = pd.to_datetime(
        DF_CENTRAL_LANCAMENTOS.loc[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANCAMENTO, 'CAPTACAO_INICIO'].values[0], dayfirst=True
    ).date()

    max_date = pd.to_datetime(
        DF_CENTRAL_LANCAMENTOS.loc[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANCAMENTO, 'CAPTACAO_FIM'].values[0], dayfirst=True
    ).date()

    # Criar a figura base
    fig = go.Figure()

    # Adicionar as barras de taxa de conversão
    fig.add_trace(go.Bar(
        x=df_conversao['DATA'],
        y=df_conversao['taxa_conversao'],
        name='Taxa de Conversão (%)',
        text=df_conversao['taxa_conversao'].round(2).astype(str) + '%',
        textposition='outside',
        marker_color='cornflowerblue',
        yaxis='y1'
    ))

    # Adicionar a linha de total de entradas com valores
    fig.add_trace(go.Scatter(
        x=df_conversao['DATA'],
        y=df_conversao['total_entradas'],
        name='Total de Entradas',
        mode='lines+markers+text',
        line=dict(color='red', width=2),
        text=df_conversao['total_entradas'],
        textposition='top center',
        yaxis='y2'
    ))

    # Atualizar layout com dois eixos y e limites do eixo x
    fig.update_layout(
        title=f'Conversão por Dia - {PRODUTO}.{VERSAO_PRINCIPAL}',
        xaxis=dict(
            title='Data',
            range=[min_date, max_date]
        ),
        yaxis=dict(
            title='Taxa de Conversão (%)',
            side='left',
            showgrid=False
        ),
        yaxis2=dict(
            title='Total de Entradas',
            overlaying='y',
            side='right',
            showgrid=False,
            fixedrange=True
        ),
        legend=dict(x=0.01, y=0.99),
        bargap=0.2
    )

    st.plotly_chart(fig, use_container_width=True)