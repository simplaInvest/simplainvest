import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go

dados = pd.read_csv('Métricas_EI - Dados.csv')


#------------------------------------------------------------
#      01.GRÁFICOS DE LINHA
#------------------------------------------------------------

dados['conv_traf'] = (dados['Trafego'] / dados['Captura']) * 100
dados['conv_copy'] = (dados['Copy'] / dados['Captura']) * 100
dados['conv_wpp'] = (dados['Whatsapp'] / dados['Captura']) * 100
dados['conv_alunos'] = (dados['Alunos'] / dados['Captura']) * 100

# Arredondar as novas colunas para duas casas decimais
columns_to_round = ['conv_traf', 'conv_copy', 'conv_wpp', 'conv_alunos']
dados[columns_to_round] = dados[columns_to_round].round(2)

@st.cache_data
def create_line_chart(df, variable, conv=None, title='', variable_legend=None, conv_legend=None):
    """
    Create a line chart for a specific variable and an optional conversion variable in the DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data.
    variable (str): Column name of the primary variable to plot.
    conv (str, optional): Column name of the conversion variable to plot (in percentages).
    title (str): Title of the chart.
    variable_legend (str, optional): Custom name for the primary variable in the legend.
    conv_legend (str, optional): Custom name for the conversion variable in the legend.

    Returns:
    fig: Plotly Figure object.
    """
    fig = go.Figure()

    # Define legend names with fallback to column names
    variable_legend = variable_legend if variable_legend else variable
    conv_legend = conv_legend if conv_legend else conv

    # Add the primary variable line
    fig.add_trace(go.Scatter(
        x=df['EI'],
        y=df[variable],
        mode='lines+markers+text',
        text=df[variable],
        textposition='top center',
        line=dict(width=2, color='blue'),
        marker=dict(size=8),
        name=variable_legend
    ))

    # Add the conversion variable line if provided
    if conv:
        # Calculate min and max values for y2 axis
        min_val = df[conv].min()
        max_val = df[conv].max()
        y2_min = min_val * 0.95  # 90% of minimum value
        y2_max = max_val * 1.05  # 110% of maximum value

        fig.add_trace(go.Scatter(
            x=df['EI'],
            y=df[conv],
            mode='lines+markers+text',
            text=df[conv].round(2).astype(str) + '%',
            textposition='top center',
            line=dict(width=2, color='green', dash='dot'),
            marker=dict(size=8),
            name=conv_legend,
            yaxis='y2'  # Specify secondary y-axis
        ))

        # Add horizontal line for the mean of `conv`
        mean_conv = df[conv].mean()
        fig.add_hline(
            y=mean_conv,
            line=dict(color='yellow', dash='dot'),
            annotation_text=f'Média: {mean_conv:.2f}%',
            annotation_position='top right',
            yref='y2'
        )

        # Update layout for dual-axis with new range and hidden ticks
        fig.update_layout(
            yaxis=dict(
                title=variable,
                titlefont=dict(color='blue'),
                tickfont=dict(color='blue')
            ),
            yaxis2=dict(
                title='Taxa (%)',
                titlefont=dict(color='green'),
                tickfont=dict(color='green'),
                overlaying='y',
                side='right',
                range=[y2_min, y2_max],
                showticklabels=True,  # Show tick labels
                showgrid=False,        # Hide grid lines
                zeroline=False         # Hide zero line
            )
        )

    # General layout updates
    fig.update_layout(
        title=title,
        xaxis_title='Lançamento (EI)',
        template='plotly_white',
        font=dict(size=12),
        margin=dict(l=40, r=40, t=50, b=40)
    )

    return fig


#------------------------------------------------------------
#      02.GRÁFICOS DE BARRAS EMPILHADAS
#------------------------------------------------------------
patrim_columns = [col for col in dados.columns if 'Patrim:' in col]
patrim = dados[patrim_columns]

ascending_columns = [
    'Patrim: Menos de 5 mil',
    'Patrim: Entre 5 e 20 mil',
    'Patrim: Entre 20 e 100 mil',
    'Patrim: Entre 100 e 250 mil',
    'Patrim: Entre 250 e 500 mil',
    'Patrim: Entre 500 mil e 1 milhão',
    'Patrim: Acima de 1 milhão'
]
patrim = patrim[ascending_columns]

renda_columns = [col for col in dados.columns if 'Renda:' in col]
renda = dados[renda_columns]

# Reordenar as colunas para que as faixas fiquem na ordem ascendente de renda
ascending_renda_columns = sorted(renda_columns, key=lambda x: int(x.split('Renda: ')[1].split(' ')[0].replace('mil', '').replace('R$', '')) if 'mil' in x else float('inf'))

# Reordenar o dataframe com base nas faixas de renda
renda = renda[ascending_renda_columns]

# Função reutilizável para gerar o gráfico de barras empilhadas
@st.cache_data
def gerar_barras_empilhadas(dataframe, colunas_renda, title):
    """
    Gera um gráfico de barras empilhadas para a distribuição de leads por faixa de renda,
    com botão para alternar entre valores absolutos e percentuais.

    Parâmetros:
        dataframe (pd.DataFrame): O dataframe contendo os dados.
        colunas_renda (list): Lista de colunas relacionadas à renda em ordem ascendente.
        title (str): Título do gráfico
        
    Retorno:
        fig: Objeto Figure do Plotly com o gráfico.
    """
    # Garantir que as colunas estão na ordem correta
    dataframe = dataframe[colunas_renda].copy()
    
    # Calcular o total de cada linha (lançamento)
    dataframe['total'] = dataframe.sum(axis=1)
    
    # Calcular as porcentagens para cada coluna
    for col in colunas_renda:
        dataframe[f'{col}_pct'] = (dataframe[col] / dataframe['total'] * 100).round(1)
    
    # Criar o gráfico de barras empilhadas
    fig = go.Figure()

    # Criar duas listas para armazenar os dados de ambas as visualizações
    data_abs = []
    data_pct = []

    # Preparar os dados para valores absolutos
    for col in colunas_renda:
        data_abs.append(go.Bar(
            name=col,
            x=[f'EI.{i+15}' for i in range(len(dataframe))],
            y=dataframe[col],
            text=dataframe[col],
            textposition='auto',
            hovertemplate='%{text}<extra></extra>',
            visible=True
        ))

    # Preparar os dados para porcentagens
    for col in colunas_renda:
        data_pct.append(go.Bar(
            name=col,
            x=[f'EI.{i+15}' for i in range(len(dataframe))],
            y=dataframe[f'{col}_pct'],
            text=dataframe[f'{col}_pct'].apply(lambda x: f'{x}%'),
            textposition='auto',
            hovertemplate='%{text}<extra></extra>',
            visible=False
        ))

    # Adicionar todos os traces ao gráfico
    fig.add_traces(data_abs + data_pct)

    # Criar o dropdown para alternar entre valores absolutos e percentuais
    updatemenus = [
        dict(
            type="dropdown",
            direction="down",
            x=0.3,  # Centralizado horizontalmente
            y=1.15,  # Logo acima do gráfico
            showactive=True,
            bgcolor="rgba(240, 240, 240, 0.8)",  # Fundo cinza claro translúcido
            borderwidth=1,
            bordercolor="lightgray",
            font=dict(color="black", size=12),
            buttons=[
                dict(
                    label="Valores Absolutos",
                    method="update",
                    args=[{"visible": [True]*len(colunas_renda) + [False]*len(colunas_renda)},
                          {"yaxis": {"title": "Quantidade"}}]
                ),
                dict(
                    label="Porcentagem",
                    method="update",
                    args=[{"visible": [False]*len(colunas_renda) + [True]*len(colunas_renda)},
                          {"yaxis": {"title": "Proporção (%)", "range": [0, 100]}}]
                )
            ]
        )
    ]

    # Atualizar o layout do gráfico
    fig.update_layout(
        barmode='stack',
        title={
            'text': f'{title}',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Lançamentos',
        yaxis_title='Quantidade',
        legend_title='Faixas de Renda',
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(dataframe))),
            ticktext=[f'EI.{i+15}' for i in range(len(dataframe))],
            tickangle=0
        ),
        template='plotly_white',
        showlegend=True,
        updatemenus=updatemenus
    )

    return fig

#------------------------------------------------------------
#      03.LAYOUT
#------------------------------------------------------------
st.title('Evolução das métricas')
st.divider()

tab1, tab2 = st.tabs(['Métricas', 'Dados Financeiros'])

with tab1:

    colunas = st.columns(2)

    variaveis = ['Captura', 'Trafego', 'Copy', 'Whatsapp', 'Alunos' ]

    with colunas[0]:
        with st.container(border=True):
            st.subheader('Captura')
            chart = create_line_chart(dados, variaveis[0])
            chart
        with st.container(border=True):
            st.subheader('Copy')
            chart = create_line_chart(dados, variaveis[2], conv = 'conv_copy', variable_legend = 'Copy', conv_legend = 'Proporção respostas')
            chart

    with colunas[1]:
        with st.container(border=True):
            st.subheader('Trafego')
            chart = create_line_chart(dados, variaveis[1], conv = 'conv_traf',variable_legend = 'Leads', conv_legend = 'Pesquisas')
            chart
        with st.container(border=True):
            st.subheader('Whatsapp')
            chart = create_line_chart(dados, variaveis[3], conv = 'conv_wpp', variable_legend = 'Whatsapp', conv_legend = 'Proporção whatsapp')
            chart

    with st.container(border=True):
        st.subheader('Alunos')
        chart = create_line_chart(dados, variaveis[4], conv = 'conv_alunos', variable_legend = 'Alunos', conv_legend = 'Conversão')
        chart

with tab2:

    colunas = st.columns(2)

    with colunas[0]:
        st.subheader('Capturas')
        with st.container(border=True):
            chart = gerar_barras_empilhadas(patrim, ascending_columns, 'Patrimônio')
            chart
        with st.container(border=True):
            chart = gerar_barras_empilhadas(renda, ascending_renda_columns, 'Renda')
            chart

    with colunas[1]:
        st.subheader('Alunos')
        with st.container(border = True):
            alunos_patrim = ['Alunos: Menos de R$5 mil',
                            'Alunos: Entre R$5 mil e R$20 mil',
                            'Alunos: Entre R$20 mil e R$100 mil ',
                            'Alunos: Entre R$100 mil e R$250 mil',
                            'Alunos: Entre R$250 mil e R$500 mil',
                            'Alunos: Entre R$500 mil e R$1 milhão',
                            'Alunos: Acima de R$1 milhão']
            # Gráfico de Patrimônio dos Alunos
            chart = gerar_barras_empilhadas(dados, alunos_patrim, 'Alunos: Patrimônio')
            chart
        with st.container(border=True):
            alunos_renda = ['Alunos: Menos de R$1.500',
                            'Alunos: Entre R$1.500 e R$2.500',
                            'Alunos: Entre R$2.500 e R$5.000',
                            'Alunos: Entre R$5.000 e R$10.000',
                            'Alunos: Entre R$10.000 e R$20.000',
                            'Alunos: Acima de R$20.000']
            # Gráfico de Renda dos Alunos
            chart = gerar_barras_empilhadas(dados, alunos_renda, 'Alunos: Renda')
            st.plotly_chart(chart, use_container_width=True)