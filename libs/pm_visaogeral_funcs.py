import streamlit as st
import pandas as pd
import altair as alt


def grafico_linhas_cap_data_captura(df, start_date, end_date, VERSAO_PRINCIPAL):
    # Convertendo start_date e end_date para datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtrar dados com base no intervalo de tempo
    if int(VERSAO_PRINCIPAL) == 20:
        filtered_df = df[(df['CAP DATA_CAPTURA'] >= start_date) & (df['CAP DATA_CAPTURA'] <= end_date)]
        df_grouped = filtered_df['CAP DATA_CAPTURA'].dt.date.value_counts().reset_index()
    else:
        filtered_df = df[(df['PM DATA_CAPTURA'] >= start_date) & (df['PM DATA_CAPTURA'] <= end_date)]
        df_grouped = filtered_df['PM DATA_CAPTURA'].dt.date.value_counts().reset_index()
    df_grouped.columns = ['Data', 'Contagem']
    df_grouped.sort_values(by='Data', inplace=True)

    # Gráfico de linhas com pontos
    line_chart = alt.Chart(df_grouped).mark_line(point=alt.OverlayMarkDef(color='lightblue')).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Contagem:Q', title='Número de Capturas'),
        tooltip=['Data', 'Contagem']
    )

    # Anotações dos valores nos pontos
    text_chart = alt.Chart(df_grouped).mark_text(
        align='center',
        baseline='bottom',
        color='lightblue',
        dx=0,
        dy=-10  # Ajuste vertical da anotação
    ).encode(
        x=alt.X('Data:T'),
        y=alt.Y('Contagem:Q'),
        text=alt.Text('Contagem:Q')
    )

    # Combinar os gráficos
    chart = (line_chart + text_chart).properties(
        title='Gráfico de Linhas - DATA_CAPTURA'
    )

    st.altair_chart(chart, use_container_width=True)

def grafico_barras_horizontais_utm_source_medium(df):
    df['PM UTM_SOURCE_MEDIUM'] = df['PM UTM_SOURCE'] + ' / ' + df['PM UTM_MEDIUM']
    df_grouped = df['PM UTM_SOURCE_MEDIUM'].value_counts().reset_index()
    df_grouped.columns = ['PM UTM_SOURCE_MEDIUM', 'Contagem']

    chart = alt.Chart(df_grouped).mark_bar(color='lightblue').encode(
        x=alt.X('Contagem:Q', title='Número de Ocorrências'),
        y=alt.Y('PM UTM_SOURCE_MEDIUM:N', sort='-x', title='Fonte'),
        tooltip=['PM UTM_SOURCE_MEDIUM', 'Contagem']
    ).properties(
        title='Gráfico de Barras Horizontais - UTM_SOURCE_MEDIUM'
    )
    st.altair_chart(chart, use_container_width=True)

def grafico_barras_horizontais(df, column):
    df_grouped = df[column].value_counts().reset_index()
    df_grouped.columns = [column, 'Contagem']
    df_grouped = df_grouped.head(10)

    chart = alt.Chart(df_grouped).mark_bar(color='lightblue').encode(
        x=alt.X('Contagem:Q', title='Número de Ocorrências'),
        y=alt.Y(f'{column}:N', sort='-x', title='Fonte'),
        tooltip=[f'{column}', 'Contagem']
    ).properties(
        title=f'Gráfico de Barras Horizontais - {column}'
    )
    st.altair_chart(chart, use_container_width=True)

def grafico_pizza(df, column):
    # Agrupar dados por UTM_MEDIUM
    df_grouped = df[column].value_counts(normalize=True).reset_index()
    df_grouped.columns = [column, 'Proporção']
    df_grouped['Proporção (%)'] = (df_grouped['Proporção'] * 100).round(2)  # Convertendo para porcentagem

    # Criar o gráfico de pizza
    chart = alt.Chart(df_grouped).mark_arc().encode(
        theta=alt.Theta(field='Proporção', type='quantitative', title='Proporção'),
        color=alt.Color(field=f'{column}', type='nominal', title='Medium'),
        tooltip=[f'{column}', alt.Tooltip('Proporção (%)', format='.2f')]
    ).properties(
        title=f'Gráfico de Pizza - {column}'
    )

    st.altair_chart(chart, use_container_width=True)