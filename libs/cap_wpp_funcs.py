import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

def plot_group_members_per_day_altair(df, DF_CENTRAL_LANCAMENTOS, LANCAMENTO):
    # Verifica se o DataFrame de entradas do grupo não está vazio
    if df.empty:
        st.warning("No data available for group entries.")
        return None

    # Converte a coluna 'Date' para datetime, se ainda não estiver
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

    # Cria o gráfico de linha principal com pontos e tooltips usando Altair
    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(labelAngle=0, format="%d %B (%a)")),
        y=alt.Y('Members:Q', title='Number of Members'),
        tooltip=['Date:T', 'Members:Q']
    )

    # Adiciona rótulos de texto acima dos pontos com o número de membros
    text_chart = alt.Chart(df).mark_text(
        align='center',
        baseline='bottom',
        color='lightblue',
        dy=-10  # Ajuste na posição vertical do texto
    ).encode(
        x='Date:T',
        y='Members:Q',
        text=alt.Text('Members:Q', format=',')
    )

    # =====================================================
    # Extração das datas de CPL a partir de DF_CENTRAL_LANCAMENTOS
    # =====================================================
    cpl_df = pd.DataFrame()
    if 'LANCAMENTO' in st.session_state:
        lancamento = st.session_state['LANCAMENTO']
        # Filtra a linha de DF_CENTRAL_LANCAMENTOS com base no lançamento selecionado
        df_lancamento = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANCAMENTO]
        if not df_lancamento.empty:
            # Colunas que contêm as datas de CPL
            cpl_columns = ['CPL01', 'CPL02', 'CPL03', 'CPL04']
            cpl_dates = []
            cpl_labels = []
            # Itera sobre cada coluna para extrair a data de CPL, se disponível
            for i, col in enumerate(cpl_columns):
                valor = df_lancamento.iloc[0][col]
                if pd.notnull(valor) and valor != '':
                    try:
                        # Converte para datetime
                        data_cpl = pd.to_datetime(valor, dayfirst=True)
                        cpl_dates.append(data_cpl)
                        cpl_labels.append(f'CPL{i+1}')
                    except Exception as e:
                        # Em caso de erro na conversão, ignora o valor
                        pass

            # Se houver datas válidas, monta o DataFrame de CPL
            if cpl_dates:
                cpl_df = pd.DataFrame({
                    'CPLs': cpl_dates,
                    'CPL_Label': cpl_labels
                })
                # Filtra as datas que estão dentro do intervalo do gráfico
                min_date = df["Date"].min()
                max_date = df["Date"].max()
                cpl_df = cpl_df[(cpl_df["CPLs"] >= min_date) & (cpl_df["CPLs"] <= max_date)]

    # ================================================================================
    # Montagem do gráfico final, incorporando as linhas de CPL (caso haja datas válidas)
    # ================================================================================
    if not cpl_df.empty:
        # Cria as linhas verticais pontilhadas para cada data de CPL
        cpl_lines = alt.Chart(cpl_df).mark_rule(strokeDash=[4, 4], color='red').encode(
            x='CPLs:T'
        )
        # Adiciona os rótulos para as datas de CPL
        cpl_labels_chart = alt.Chart(cpl_df).mark_text(
            align='left',
            baseline='top',
            dy=15,
            color='red'
        ).encode(
            x='CPLs:T',
            text='CPL_Label'
        )
        chart = (line_chart + text_chart + cpl_lines + cpl_labels_chart).properties(
            title='Group Members Over Time with CPLs',
            width=700,
            height=400
        )
    else:
        chart = (line_chart + text_chart).properties(
            title='Group Members Over Time',
            width=700,
            height=400
        )

    # Configurações finais de estilo do gráfico
    chart = chart.configure_axis(
        grid=False,
        labelColor='white',
        titleColor='white'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        color='white'
    ).configure(background='rgba(0,0,0,0)')

    st.altair_chart(chart, use_container_width=True)

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

    st.altair_chart(chart, use_container_width=True)

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

    st.altair_chart(chart, use_container_width=True)

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

    st.altair_chart(chart, use_container_width=True)

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

    combined_chart = alt.layer(bars, text)
    st.altair_chart(combined_chart, use_container_width=True)

def plot_clicks_over_time(df):
    """
    Cria um gráfico de linhas com a coluna 'CLICKS NO DIA' no eixo Y
    e 'DATA' no eixo X (considerando apenas o dia), anotando os valores de cada ponto.
    
    Parâmetros:
    - df (pd.DataFrame): DataFrame contendo as colunas 'DATA' e 'CLICKS NO DIA'.
    
    Retorna:
    - fig (plotly.graph_objects.Figure): Objeto da figura gerada.
    """
    # Garantir que 'DATA' esteja no formato datetime e considerar apenas a data (sem horas)
    df['DATA'] = pd.to_datetime(df['DATA'], dayfirst=True).dt.date

    # Criar o gráfico de linhas
    fig = px.line(
        df, 
        x='DATA', 
        y='CLICKS NO DIA', 
        title='Clicks no Dia ao Longo do Tempo',
        labels={'DATA': 'Data', 'CLICKS NO DIA': 'Clicks no Dia'},
        markers=True  # Adicionar marcadores nos pontos
    )
    
    # Adicionar os valores sobre os pontos
    fig.update_traces(
        text=df['CLICKS NO DIA'].astype(str), 
        textposition='top center',
        mode='lines+markers+text'  # Inclui texto nos marcadores
    )
    
    # Ajustar layout
    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Clicks no Dia',
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)