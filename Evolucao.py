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
@st.cache_data
def create_line_chart(df, variable, title=''):
    """
    Create a line chart for a specific variable in the DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data.
    variable (str): Column name of the variable to plot.
    title (str): Title of the chart.

    Returns:
    fig: Plotly Figure object.
    """
    fig = go.Figure()

    # Add the line and markers to the chart
    fig.add_trace(go.Scatter(
        x=df['EI'],
        y=df[variable],
        mode='lines+markers+text',
        text=df[variable],
        textposition='top center',
        line=dict(width=2),
        marker=dict(size=8),
        name=variable
    ))

    # Update layout for better visualization
    fig.update_layout(
        title=title,
        xaxis_title='Lançamento (EI)',
        yaxis_title=variable,
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
    Gera um gráfico de barras empilhadas para a distribuição de leads por faixa de renda.

    Parâmetros:
        dataframe (pd.DataFrame): O dataframe contendo os dados.
        colunas_renda (list): Lista de colunas relacionadas à renda em ordem ascendente.
        
    Retorno:
        None: Mostra o gráfico interativo.
    """
    # Garantir que as colunas estão na ordem correta
    dataframe = dataframe[colunas_renda]
    
    # Criar o gráfico de barras empilhadas
    fig = go.Figure()

    # Adicionar cada coluna como uma camada do gráfico empilhado
    for col in colunas_renda:
        fig.add_trace(go.Bar(
            name=col,
            x=[f'EI.{i+15}' for i in range(len(dataframe))],
            y=dataframe[col],
            text=dataframe[col],
            textposition='auto',
            hoverinfo='text+name'
        ))

    # Atualizar o layout do gráfico para melhorar a visualização
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
        showlegend=True
    )

    # Mostrar o gráfico
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
            chart = create_line_chart(dados, variaveis[2])
            chart
        with st.container(border=True):
            st.subheader('Alunos')
            chart = create_line_chart(dados, variaveis[4])
            chart

    with colunas[1]:
        with st.container(border=True):
            st.subheader('Trafego')
            chart = create_line_chart(dados, variaveis[1])
            chart
        with st.container(border=True):
            st.subheader('Whatsapp')
            chart = create_line_chart(dados, variaveis[3])
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
            chart