import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import re
from sklearn.feature_extraction.text import CountVectorizer

st.title('Grupos de Whatsapp')

captura_ei = st.session_state.get('df_CAPTURA', pd.DataFrame())
trafego_ei = st.session_state.get('df_PESQUISA', pd.DataFrame())
copy_ei = st.session_state.get('df_COPY', pd.DataFrame())
whatsapp_ei = st.session_state.get('df_GRUPOS', pd.DataFrame())
whatsapp_entradas = whatsapp_ei[whatsapp_ei['Evento'] == 'Entrou no grupo']
whatsapp_saidas = whatsapp_ei[whatsapp_ei['Evento'] == 'Saiu do grupo']

@st.cache_data
def plot_group_members_per_day_altair(df):
    # Verify if the DataFrame is not empty
    if df.empty:
        st.warning("No data available for group entries.")
        return None

    # Create the line chart with Altair
    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(labelAngle=0, format="%d %B (%a)")),
        y=alt.Y('Members:Q', title='Number of Members'),
        tooltip=['Date:T', 'Members:Q']
    )

    # Add text labels above the points
    text_chart = alt.Chart(df).mark_text(
        align='center',
        baseline='bottom',
        color = 'lightblue',
        dy=-10  # Adjust the vertical position of the text
    ).encode(
        x='Date:T',
        y='Members:Q',
        text=alt.Text('Members:Q', format=',')
    )

    # Combine the charts
    chart = (line_chart + text_chart).properties(
        title='',
        width=600,
        height=400
    )

    return chart

@st.cache_data
def plot_entry_per_day(df):
    # Verify if the DataFrame is not empty
    if df.empty:
        st.warning("No data available for group entries.")
        return None

    # Create the line chart with Altair
    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(labelAngle=0, format="%d %B (%a)")),
        y=alt.Y('Entry:Q', title='Número de entradas'),
        tooltip=['Date:T', 'Entry:Q']
    )

    # Add text labels above the points
    text_chart = alt.Chart(df).mark_text(
        align='center',
        baseline='bottom',
        color = 'lightblue',
        dy=-10  # Adjust the vertical position of the text
    ).encode(
        x='Date:T',
        y='Entry:Q',
        text=alt.Text('Entry:Q', format=',')
    )

    # Combine the charts
    chart = (line_chart + text_chart).properties(
        title='',
        width=600,
        height=400
    )

    return chart

@st.cache_data
def plot_exit_per_day(df):
    # Verify if the DataFrame is not empty
    if df.empty:
        st.warning("No data available for group exits.")
        return None

    # Create the line chart with Altair
    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(labelAngle=0, format="%d %B (%a)")),
        y=alt.Y('Exit:Q', title='Número de entradas'),
        tooltip=['Date:T', 'Exit:Q']
    )

    # Add text labels above the points
    text_chart = alt.Chart(df).mark_text(
        align='center',
        baseline='bottom',
        color = 'lightblue',
        dy=-10  # Adjust the vertical position of the text
    ).encode(
        x='Date:T',
        y='Exit:Q',
        text=alt.Text('Exit:Q', format=',')
    )

    # Combine the charts
    chart = (line_chart + text_chart).properties(
        title='',
        width=600,
        height=400
    )

    return chart

@st.cache_data
def plot_ratio_per_day(df):
    # Verify if the DataFrame is not empty
    if df.empty:
        st.warning("No data available for group ratios.")
        return None
    
     # Clip the Ratio values to a maximum of 300
    df['Ratio'] = df['Ratio'].clip(upper=300)

    # Create the line chart with Altair
    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(labelAngle=0, format="%d %B (%a)")),
        y=alt.Y('Ratio:Q', title='Número de entradas', ),
        tooltip=['Date:T', 'Ratio:Q']
    )

    # Add text labels above the points
    text_chart = alt.Chart(df).mark_text(
        align='center',
        baseline='bottom',
        color = 'lightblue',
        dy=-10  # Adjust the vertical position of the text
    ).encode(
        x='Date:T',
        y='Ratio:Q',
        text=alt.Text('Ratio:Q', format=',')
    )

    # Combine the charts
    chart = (line_chart + text_chart).properties(
        title='',
        width=600,
        height=400
    )

    return chart

@st.cache_data
def calculate_stay_duration_and_plot_histogram(df):
    """
    Calcula o tempo de permanência de cada número nos grupos com base nos eventos de entrada e saída,
    e plota um histograma anotado com Altair para visualização.

    Args:
    - df (pd.DataFrame): DataFrame contendo colunas 'Numero', 'Evento' e 'Data'.

    Returns:
    - alt.Chart: Gráfico Altair representando o histograma dos tempos de permanência em dias.
    """
    # Convertendo a coluna 'Data' para datetime
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y às %H:%M:%S')

    # Ordenando os dados por número e data
    df = df.sort_values(by=['Numero', 'Data'])

    # Calculando o tempo de permanência para cada número
    permanencia = []

    # Agrupando por número
    for numero, group in df.groupby('Numero'):
        group = group.reset_index()
        for i in range(len(group) - 1):
            if group.loc[i, 'Evento'] == 'Entrou no grupo' and group.loc[i + 1, 'Evento'] == 'Saiu do grupo':
                entrada = group.loc[i, 'Data']
                saida = group.loc[i + 1, 'Data']
                permanencia.append((saida - entrada).total_seconds() / 86400)  # Tempo em dias

    # Criando o DataFrame com os tempos de permanência
    df_permanencia = pd.DataFrame(permanencia, columns=['TempoPermanencia'])

    # Criando o histograma com Altair
    base = alt.Chart(df_permanencia).encode(
        alt.X('TempoPermanencia:Q', bin=alt.Bin(maxbins=30), title='Tempo de Permanência (dias)'),
        alt.Y('count()', title='Frequência'),
        tooltip=['count()']
    )

    # Gráfico de barras
    bars = base.mark_bar(color='skyblue').properties(
        title='',
        width=800,
        height=400
    )

    # Adicionando anotações com os valores das bins
    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-5,  # Ajuste da posição vertical
        color='lightblue'
    ).encode(
        text='count()'
    )

    return bars + text

whatsapp_ei['Entry'] = whatsapp_ei['Evento'].str.contains("Entrou", na=False).astype(int)
whatsapp_ei['Exit'] = whatsapp_ei['Evento'].str.contains("Saiu", na=False).astype(int)

# Group by date and calculate cumulative sums for entries and exits
daily_activity = whatsapp_ei.groupby(whatsapp_ei['Data'].dt.date)[['Entry', 'Exit']].sum().reset_index()

# Rename the grouped date column for clarity
daily_activity.rename(columns={'Data': 'Date'}, inplace=True)

# Calculate cumulative members
daily_activity['Members'] = daily_activity['Entry'].cumsum() - daily_activity['Exit'].cumsum()
daily_activity['Ratio'] = round((daily_activity['Exit']/daily_activity['Entry']) * 100, 2)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Captura")
    st.metric(label = '', value=f"{captura_ei.shape[0]}")

with col2:
    st.subheader("Whatsapp")
    st.metric(label = '', value=f"{whatsapp_entradas.shape[0]}")

with col3:
    st.subheader("Conversão")
    st.metric(label = '', value=f"{round((whatsapp_entradas.shape[0]/captura_ei.shape[0])*100, 2)}%")

st.subheader('Número de pessoas no grupo')
fig = plot_group_members_per_day_altair(daily_activity)
if fig:
    st.altair_chart(fig, use_container_width=True)

st.subheader('Número de entradas por dia')
fig = plot_entry_per_day(daily_activity)
if fig:
    st.altair_chart(fig, use_container_width=True)

st.subheader('Número de saídas por dia')
fig = plot_exit_per_day(daily_activity)
if fig:
    st.altair_chart(fig, use_container_width=True)

st.subheader('Proporção de saídas em relação a entradaspor dia')
fig = plot_ratio_per_day(daily_activity)
if fig:
    st.altair_chart(fig, use_container_width=True)

st.subheader('Distribuição de Tempo de Permanência nos Grupos (em dias)')
fig = calculate_stay_duration_and_plot_histogram(whatsapp_ei)
if fig:
    st.altair_chart(fig, use_container_width=True)
