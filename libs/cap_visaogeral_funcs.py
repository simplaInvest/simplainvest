import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px
from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_VENDAS, K_GRUPOS_WPP, K_PCOPY_DADOS, K_PTRAFEGO_DADOS, K_PTRAFEGO_META_ADS, K_CLICKS_WPP, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_LANCAMENTOS, get_df

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

# Carregar DataFrames para lançamento selecionado
loading_container = st.empty()
with loading_container:
    status = st.status("Carregando dados...", expanded=True)
    with status:
        try:
            DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
            DF_CENTRAL_PREMATRICULA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
            DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
            DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
            DF_PTRAFEGO_META_ADS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_META_ADS)
            DF_PCOPY_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PCOPY_DADOS)
            DF_GRUPOS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_GRUPOS_WPP)
            DF_CLICKS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CLICKS_WPP)
            DF_CENTRAL_LANCAMENTOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_LANCAMENTOS)
            status.update(label="Carregados com sucesso!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="Erro ao carregar dados: " + str(e), state="error", expanded=False)
loading_container.empty()

if 'LANÇAMENTO' in st.session_state:
        lancamento = st.session_state['LANÇAMENTO']

def plot_group_members_per_day_altair(DF_GRUPOS_WPP):
    # Verify if the DataFrame is not empty
    if DF_GRUPOS_WPP.empty:
        st.warning("No data available for group entries.")
        return None
    
    # Convert 'Data' column to datetime if not already
    DF_GRUPOS_WPP['Data'] = pd.to_datetime(DF_GRUPOS_WPP['Data'])

    # Group by date and calculate cumulative sums for entries and exits
    daily_activity = DF_GRUPOS_WPP.groupby(DF_GRUPOS_WPP['Data'].dt.date)[['Entradas', 'Saidas']].sum().reset_index()

    # Rename the grouped date column for clarity
    daily_activity.rename(columns={'Data': 'Date'}, inplace=True)

    # Calculate cumulative members
    daily_activity['Members'] = daily_activity['Entradas'].cumsum() - daily_activity['Saidas'].cumsum()

    # Create the line chart with Altair
    line_chart = alt.Chart(daily_activity).mark_line(point=True).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(labelAngle=0, format="%d %B (%a)")),
        y=alt.Y('Members:Q', title='Number of Members'),
        tooltip=['Date:T', 'Members:Q']
    )

    # Add text labels above the points
    text_chart = alt.Chart(daily_activity).mark_text(
        align='center',
        baseline='bottom',
        color='lightblue',
        dy=-10  # Adjust the vertical position of the text
    ).encode(
        x='Date:T',
        y='Members:Q',
        text=alt.Text('Members:Q', format=',')
    )

    # Adicionar linhas verticais para os dias de CPL
    if "CPLs" in st.session_state and st.session_state["CPLs"]:
        cpl_df = pd.DataFrame({
            "CPLs": pd.to_datetime(st.session_state["CPLs"]),
            "CPL_Label": [f"CPL{i+1}" for i in range(len(st.session_state["CPLs"]))]
        })

        # Filtrar datas dentro do intervalo do gráfico
        min_date = daily_activity["Date"].min()
        max_date = daily_activity["Date"].max()
        cpl_df = cpl_df[(cpl_df["CPLs"].dt.date >= min_date) & (cpl_df["CPLs"].dt.date <= max_date)]

        if not cpl_df.empty:
            cpl_lines = alt.Chart(cpl_df).mark_rule(strokeDash=[4, 4], color='red').encode(
                x='CPLs:T'
            )

            cpl_labels = alt.Chart(cpl_df).mark_text(
                align='left',
                baseline='top',
                dy=15,
                color='red'
            ).encode(
                x='CPLs:T',
                text='CPL_Label'
            )

            chart = (line_chart + text_chart + cpl_lines + cpl_labels).properties(
                title='Group Members Over Time with CPLs',
                width=700,
                height=400
            ).configure_axis(
                grid=False,
                labelColor='white',
                titleColor='white'
            ).configure_view(
                strokeWidth=0
            ).configure_title(
                color='white'
            ).configure(background='rgba(0,0,0,0)')
        
        else:
            chart = (line_chart + text_chart).properties(
                title='Group Members Over Time',
                width=700,
                height=400
            ).configure_axis(
                grid=False,
                labelColor='white',
                titleColor='white'
            ).configure_view(
                strokeWidth=0
            ).configure_title(
                color='white'
            ).configure(background='rgba(0,0,0,0)')

    else:
        chart = (line_chart + text_chart).properties(
            title='Group Members Over Time',
            width=700,
            height=400
        ).configure_axis(
            grid=False,
            labelColor='white',
            titleColor='white'
        ).configure_view(
            strokeWidth=0
        ).configure_title(
            color='white'
        ).configure(background='rgba(0,0,0,0)')

    return st.altair_chart(chart, use_container_width=True)

def plot_leads_per_day_altair(DF_CENTRAL_CAPTURA):
    # Verifica se o DataFrame de captura não está vazio
    if DF_CENTRAL_CAPTURA.empty:
        st.warning("Os dados de Leads por Dia estão vazios.")
        return None

    # Copia e agrupa os dados por data, contando a quantidade de leads (EMAIL)
    df_CONTALEADS = DF_CENTRAL_CAPTURA.copy()
    df_CONTALEADS = df_CONTALEADS[['EMAIL', 'CAP DATA_CAPTURA']].groupby('CAP DATA_CAPTURA').count().reset_index()
    
    # Converte a coluna de data para datetime
    df_CONTALEADS["CAP DATA_CAPTURA"] = pd.to_datetime(df_CONTALEADS["CAP DATA_CAPTURA"])

    # Determina o intervalo de datas (mínima e máxima) e o total de dias de captação
    min_date = df_CONTALEADS["CAP DATA_CAPTURA"].min()
    max_date = df_CONTALEADS["CAP DATA_CAPTURA"].max()
    total_dias = (max_date - min_date).days

    # Cria o gráfico de linha principal com pontos e tooltips usando Altair
    line_chart = alt.Chart(df_CONTALEADS).mark_line(point=True).encode(
        x=alt.X('CAP DATA_CAPTURA:T', title='Data', axis=alt.Axis(labelAngle=-0, format="%d %B (%a)")),
        y=alt.Y('EMAIL:Q', title='Número de Leads'),
        tooltip=['CAP DATA_CAPTURA:T', 'EMAIL:Q']
    )

    # Adiciona rótulos acima dos pontos com o número de leads
    text_chart = alt.Chart(df_CONTALEADS).mark_text(
        align='center',
        baseline='bottom',
        dy=-10,           # Ajusta a posição vertical do texto
        color='lightblue' # Define a cor do texto
    ).encode(
        x='CAP DATA_CAPTURA:T',
        y='EMAIL:Q',
        text=alt.Text('EMAIL:Q', format=',')
    )

    # ================================================================
    # NOVA IMPLEMENTAÇÃO: Extração das datas de CPL a partir do DF_CENTRAL_LANCAMENTOS
    # ================================================================
    cpl_df = pd.DataFrame()
    # Filtra a linha do DF_CENTRAL_LANCAMENTOS para o lançamento selecionado
    df_lancamento = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == lancamento]
    if not df_lancamento.empty:
        # Lista com os nomes das colunas que contém as datas de CPL
        cpl_columns = ['CPL01', 'CPL02', 'CPL03', 'CPL04']
        cpl_dates = []
        cpl_labels = []
        # Itera sobre cada coluna para extrair a data, se disponível
        for i, col in enumerate(cpl_columns):
            valor = df_lancamento.iloc[0][col]
            if pd.notnull(valor) and valor != '':
                try:
                    # Tenta converter o valor para datetime
                    data_cpl = pd.to_datetime(valor, dayfirst=True)
                    cpl_dates.append(data_cpl)
                    cpl_labels.append(f'CPL{i+1}')
                except Exception as e:
                    # Se houver erro na conversão, ignora o valor
                    pass

        # Se houverem datas válidas, monta o DataFrame de CPL
        if cpl_dates:
            cpl_df = pd.DataFrame({
                'CPLs': cpl_dates,
                'CPL_Label': cpl_labels
            })
            # Filtra as datas de CPL que estão dentro do intervalo de captação
            cpl_df = cpl_df[(cpl_df['CPLs'] >= min_date) & (cpl_df['CPLs'] <= max_date)]

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
            dy=15,    # Deslocamento vertical para o texto
            color='red'
        ).encode(
            x='CPLs:T',
            text='CPL_Label'
        )
        chart = (line_chart + text_chart + cpl_lines + cpl_labels_chart).properties(
            title=f'Leads por Dia e Datas de CPLs\n{total_dias} dias de captação',
            width=700,
            height=400
        )
    else:
        chart = (line_chart + text_chart).properties(
            title=f'Leads por Dia\n{total_dias} dias de captação',
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

    return st.altair_chart(chart, use_container_width=True)

def plot_utm_source_counts_altair(df, column_name='UTM_SOURCE'):
    """
    Função para gerar um gráfico de barras horizontais com a contagem de cada classe em uma coluna específica.
    
    Parâmetros:
        df (DataFrame): O DataFrame contendo os dados.
        column_name (str): O nome da coluna a ser analisada.
        
    Retorna:
        alt.Chart: Um gráfico Altair pronto para ser exibido.
    """
    # Contar as ocorrências de cada classe na coluna especificada
    class_counts = df[column_name].value_counts().reset_index()
    class_counts.columns = [column_name, 'Count']
    
    # Ordenar as classes em ordem decrescente de frequência
    class_counts = class_counts.sort_values(by='Count', ascending=False)
    
    # Criar o gráfico de barras horizontais
    chart = alt.Chart(class_counts).mark_bar().encode(
        x=alt.X('Count:Q', title='Contagem'),
        y=alt.Y(f'{column_name}:N', sort='-x', title='Classe'),
        tooltip=['Count', f'{column_name}']
    ).properties(
        title=f'',
        width=600,
        height=400
    )

    # Adicionar os valores no topo das barras
    text = alt.Chart(class_counts).mark_text(
        align='left',
        baseline='middle',
        color = 'lightblue',
        dx=3  # Deslocamento horizontal
    ).encode(
        x=alt.X('Count:Q'),
        y=alt.Y(f'{column_name}:N', sort='-x'),
        text='Count:Q'
    )
    
    # Combinar o gráfico de barras e os valores
    combined_chart = alt.layer(chart, text)
    st.altair_chart(combined_chart, use_container_width=True)


def plot_utm_medium_pie_chart(df, column_name='UTM_MEDIUM', classes_to_include=None):
    """
    Função para gerar um gráfico de pizza comparando os valores filtrados de uma coluna específica.

    Parâmetros:
        df (DataFrame): O DataFrame contendo os dados.
        column_name (str): O nome da coluna a ser analisada.
        classes_to_include (list): Lista de classes a serem incluídas no gráfico.

    Retorna:
        alt.Chart: Um gráfico Altair pronto para ser exibido.
    """
    if classes_to_include is None:
        classes_to_include = ['organico', 'pago', 'indefinido']
    
    # Filtrar os valores para incluir apenas as classes desejadas
    filtered_df = df[df[column_name].isin(classes_to_include)]
    
    # Contar as ocorrências de cada classe
    class_counts = filtered_df[column_name].value_counts().reset_index()
    class_counts.columns = [column_name, 'Count']
    
    # Calcular a porcentagem de cada classe
    total = class_counts['Count'].sum()
    class_counts['Percentage'] = (class_counts['Count'] / total * 100).round(2)
    
    # Criar o gráfico de pizza
    pie_chart = alt.Chart(class_counts).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field='Count', type='quantitative'),
        color=alt.Color(
            field=column_name,
            type='nominal',
            scale=alt.Scale(scheme='blues'),  # Usar tons de azul
            legend=alt.Legend(title="Classe")
        ),
        tooltip=[
            alt.Tooltip(f'{column_name}:N', title='Classe'),
            alt.Tooltip('Count:Q', title='Contagem'),
            alt.Tooltip('Percentage:Q', title='Porcentagem', format='.2f')
        ]
    ).properties(
        title=f'',
        width=400,
        height=400
    )
    
    # Adicionar os valores em porcentagem no gráfico
    text = alt.Chart(class_counts).mark_text(radius=120, size=14).encode(
        theta=alt.Theta(field='Count', type='quantitative'),
        text=alt.Text('Percentage:Q', format='.1f'),
        color=alt.value('black')
    )
    
    combined_chart = alt.layer(pie_chart, text)
    st.altair_chart(combined_chart, use_container_width=True)


# Função para estilizar e exibir gráficos com fundo transparente e letras brancas
def styled_bar_chart(x, y, title, colors=['#ADD8E6', '#5F9EA0']):
    fig = go.Figure(data=[
        go.Bar(x=[x[0]], y=[y[0]], marker_color=colors[0]),
        go.Bar(x=[x[1]], y=[y[1]], marker_color=colors[1])
    ])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  
        paper_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='white'),  
        title=dict(text=title, x=0.5, font=dict(size=20, color='white')),
        xaxis=dict(showgrid=False, tickfont=dict(color='white')),
        yaxis=dict(showgrid=False, tickfont=dict(color='white')),
        margin=dict(l=0, r=0, t=40, b=40)
    )
    return fig