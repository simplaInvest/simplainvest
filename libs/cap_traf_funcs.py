import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import streamlit as st
from libs.data_loader import K_CENTRAL_LANCAMENTOS, get_df


PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

DF_CENTRAL_LANCAMENTOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_LANCAMENTOS)

cols_finan_01 = 'PATRIMONIO'
cols_finan_02 = 'QUANTO_POUPA' if PRODUTO == "SW" else 'RENDA MENSAL'


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

def calcular_proporcoes_e_plotar(dataframe, coluna, lista_faixas):
        # 1. Filtrar dados relevantes e tratar NaNs
        dataframe = dataframe.dropna(subset=["DATA DE CAPTURA", coluna])  # Remove linhas sem data ou patrimônio.
        dataframe["DIA"] = dataframe["DATA DE CAPTURA"].dt.date  # Extrai apenas a data (ignora horas e minutos).

        # Filtrar pelo parâmetro de data_inicio
        Cap = DF_CENTRAL_LANCAMENTOS.loc[
            DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == st.session_state['LANÇAMENTO'],
            'CAPTACAO_INICIO'
        ].iloc[0]
        dataframe = dataframe[dataframe["DIA"] >= pd.to_datetime(Cap).date()]  



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
        return st.plotly_chart(fig, use_container_width=True)

def create_heatmap(dataframe):
    """
    Cria um heatmap (mapa de calor) entre PATRIMÔNIO e RENDA MENSAL,
    exibindo apenas as classes mapeadas nas listas de ordem.
    
    Args:
    - dataframe (pd.DataFrame): deve conter colunas 'PATRIMONIO' e cols_finan_02
    
    Returns:
    - Gráfico de heatmap com anotações
    """

    # Define as ordens explícitas
    patrimonio_order = [
        'Menos de R$5 mil', 'Entre R$5 mil e R$20 mil', 'Entre R$20 mil e R$100 mil',
        'Entre R$100 mil e R$250 mil', 'Entre R$250 mil e R$500 mil',
        'Entre R$500 mil e R$1 milhão', 'Acima de R$1 milhão'
    ]

    col2_order = [
        'Até R$1.500', 'Entre R$1.500 e R$2.500', 'Entre R$2.500 e R$5.000',
        'Entre R$5.000 e R$10.000', 'Entre R$10.000 e R$20.000', 'Acima de R$20.000'
    ]

    # Filtrar somente as classes mapeadas
    df_filtrado = dataframe[
        dataframe['PATRIMONIO'].isin(patrimonio_order) & 
        dataframe[cols_finan_02].isin(col2_order)
    ]

    # Criar pivot e garantir ordem com reindex
    heatmap_pivot = df_filtrado.pivot_table(
        index='PATRIMONIO', 
        columns=cols_finan_02, 
        aggfunc='size', 
        fill_value=0
    ).reindex(index=patrimonio_order, columns=col2_order, fill_value=0)

    # Criar gráfico
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns.tolist(),
        y=heatmap_pivot.index.tolist(),
        colorscale='Blues',
        colorbar=dict(title='Quantidade')
    ))

    # Anotações
    for i, row in enumerate(heatmap_pivot.index):
        for j, col in enumerate(heatmap_pivot.columns):
            fig.add_annotation(
                x=col,
                y=row,
                text=str(heatmap_pivot.loc[row, col]),
                showarrow=False,
                font=dict(color="black", size=15, family="Arial")
            )

    # Layout
    fig.update_layout(
        title='Mapa de Calor: PATRIMÔNIO vs RENDA MENSAL',
        xaxis_title="Faixa de Renda Mensal",
        yaxis_title="Faixa de Patrimônio",
        xaxis=dict(categoryorder='array', categoryarray=col2_order),
        yaxis=dict(categoryorder='array', categoryarray=patrimonio_order)
    )

    return st.plotly_chart(fig, use_container_width=True)
