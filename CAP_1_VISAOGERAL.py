import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px
from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_VENDAS, K_GRUPOS_WPP, K_PCOPY_DADOS, K_PTRAFEGO_DADOS, K_PTRAFEGO_META_ADS, K_CLICKS_WPP, get_df

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]
CPL = st.session_state['CPLs']

# Carregar DataFrames para lançamento selecionado
loading_container = st.empty()
with loading_container:
    status = st.status("Carregando dados...", expanded=True)
    with status:
        try:
            DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
            DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
            DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
            DF_PTRAFEGO_META_ADS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_META_ADS)
            DF_PCOPY_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PCOPY_DADOS)
            DF_GRUPOS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_GRUPOS_WPP)
            DF_CLICKS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CLICKS_WPP)
            status.update(label="Carregados com sucesso!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="Erro ao carregar dados: " + str(e), state="error", expanded=False)
loading_container.empty()


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

    return chart

def plot_leads_per_day_altair(DF_CENTRAL_CAPTURA):
    # Verificar se o DataFrame não está vazio
    if DF_CENTRAL_CAPTURA.empty:
        st.warning("Os dados de Leads por Dia estão vazios.")
        return None
    
    # Contar o número de leads por dia
    df_CONTALEADS = DF_CENTRAL_CAPTURA.copy()
    df_CONTALEADS = df_CONTALEADS[['EMAIL', 'CAP DATA_CAPTURA']].groupby('CAP DATA_CAPTURA').count().reset_index()

    # Converter para datetime64 no Pandas para evitar erros de tipo
    df_CONTALEADS["CAP DATA_CAPTURA"] = pd.to_datetime(df_CONTALEADS["CAP DATA_CAPTURA"])

    # Calcular o tempo total de captação
    min_date = df_CONTALEADS["CAP DATA_CAPTURA"].min()
    max_date = df_CONTALEADS["CAP DATA_CAPTURA"].max()
    total_dias = (max_date - min_date).days

    # Criar o gráfico de linhas com Altair
    line_chart = alt.Chart(df_CONTALEADS).mark_line(point=True).encode(
        x=alt.X('CAP DATA_CAPTURA:T', title='Data', axis=alt.Axis(labelAngle=-0, format="%d %B (%a)")),
        y=alt.Y('EMAIL:Q', title='Número de Leads'),
        tooltip=['CAP DATA_CAPTURA:T', 'EMAIL:Q']
    )

    # Adicionar valores como texto acima dos pontos
    text_chart = alt.Chart(df_CONTALEADS).mark_text(
        align='center',
        baseline='bottom',
        dy=-10,  # Ajusta a posição vertical do texto
        color='lightblue'  # Define a cor do texto
    ).encode(
        x='CAP DATA_CAPTURA:T',
        y='EMAIL:Q',
        text=alt.Text('EMAIL:Q', format=',')  # Exibe o número formatado
    )

    # Adicionar linhas verticais para os dias de CPL
    if "CPLs" in st.session_state and st.session_state["CPLs"]:
        cpl_df = pd.DataFrame({
            "CPLs": pd.to_datetime(st.session_state["CPLs"]),
            "CPL_Label": [f"CPL{i+1}" for i in range(len(st.session_state["CPLs"]))]
        })

        # Filtrar datas dentro do intervalo do gráfico
        cpl_df = cpl_df[(cpl_df["CPLs"] >= min_date) & (cpl_df["CPLs"] <= max_date)]

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
                title=f'Leads por Dia e Datas de CPLs\n{total_dias} dias de captação',
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
                title=f'Leads por Dia\n{total_dias} dias de captação',
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
            title=f'Leads por Dia\n{total_dias} dias de captação',
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

    return chart

@st.cache_data
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
    return chart + text

@st.cache_data
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
    
    return pie_chart + text

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

#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("CAPTAÇÃO > VISÃO GERAL")
st.title('Visão Geral')

#------------------------------------------------------------
#      01. KEY METRICS
#------------------------------------------------------------
with st.container(border=True):
    col_captura, col_trafego, col_copy, col_whatsapp, col_cpl = st.columns(5)

    with col_captura:
        st.subheader("Captura")
        st.metric(label="Total", value=f"{DF_CENTRAL_CAPTURA.shape[0]}")

    with col_trafego:
        st.subheader("Tráfego")
        st.metric(label="Total", value=f"{DF_PTRAFEGO_DADOS.shape[0]}")
        st.metric(label="Conversão", value=f"{round(DF_PTRAFEGO_DADOS.shape[0]/DF_CENTRAL_CAPTURA.shape[0] * 100, 2)}%", delta="")

    with col_copy:
        st.subheader("Copy")
        st.metric(label="Total", value=f"{DF_PCOPY_DADOS.shape[0]}")
        st.metric(label="Conversão", value=f"{round(DF_PCOPY_DADOS.shape[0]/DF_CENTRAL_CAPTURA.shape[0] * 100, 2)}%", delta="")

    with col_whatsapp:
        st.subheader("WhatsApp")
        wpp_members = DF_GRUPOS_WPP[DF_GRUPOS_WPP["Evento"] == "Entrou no grupo"]
        st.metric(label="Total", value=f"{wpp_members.shape[0]}")
        st.metric(label="Conversão", value=f"{round(wpp_members.shape[0]/DF_CENTRAL_CAPTURA.shape[0] * 100, 2)}%", delta="")
    
    with col_cpl:
        if VERSAO_PRINCIPAL >= 17:
            st.subheader("CPL")
            st.metric(label = "CPL Geral", value = f"R$ {round(DF_PTRAFEGO_META_ADS['VALOR USADO'].sum()/DF_CENTRAL_CAPTURA.shape[0],2)}")
            st.metric(label = "CPL Trafego", value = f"R$ {round(DF_PTRAFEGO_META_ADS['VALOR USADO'].sum()/DF_CENTRAL_CAPTURA[DF_CENTRAL_CAPTURA['CAP UTM_MEDIUM'] == 'pago'].shape[0],2)}")


#------------------------------------------------------------
#      02. GRUPOS DE WHATSAPP
#------------------------------------------------------------

# ---- 02.A - LEADS POR DIA  
with st.container(border=True):
    fig = plot_leads_per_day_altair(DF_CENTRAL_CAPTURA)
    if fig:
        st.altair_chart(fig, use_container_width=True)

# ---- 02.B - TOTAL DE LEADS POR DIA
with st.container(border=True):
    st.markdown('**Total de leads nos grupos**')
    fig = plot_group_members_per_day_altair(DF_GRUPOS_WPP)
    if fig:
        st.altair_chart(fig, use_container_width=True)

st.divider()
#------------------------------------------------------------
#      03. CAPTAÇÃO: ORIGEM / MÍDIA
#------------------------------------------------------------
st.header("Fontes de Leads")
st.caption("Principais origem/mídias de captação")
cols_captacao_utm = st.columns([5, 4])

# ---- 03.A - ORIGEM
with cols_captacao_utm[0]:
    with st.container(border=True):
        st.subheader("Origem")
        chart = plot_utm_source_counts_altair(DF_CENTRAL_CAPTURA, column_name='UTM_SOURCE')
        st.altair_chart(chart, use_container_width=True)

# ---- 03.B - MÍDIA
with cols_captacao_utm[1]:
    with st.container(border=True):
        st.subheader("Mídia")
        chart = plot_utm_medium_pie_chart(DF_CENTRAL_CAPTURA, column_name='UTM_MEDIUM')
        st.altair_chart(chart, use_container_width=True)

st.divider()


### TODO: FINALIZAR CÓDIGO ABAIXO (NÃO PRIORITÁRIA)
# 04 - FUNIL: PERCURSO COMPLETO
st.header("Trackeamento de Funil")
st.caption("CAPTAÇÃO > PRÉ-MATRÍCULA > VENDAS")
cols_captacao_utm = st.columns([5, 4])

df_vendas_copy = DF_CENTRAL_VENDAS.copy()
df_vendas_copy['CAP UTM_SOURCE'] = df_vendas_copy.apply(
    lambda x: f"{x['CAP UTM_SOURCE']} {x['CAP UTM_MEDIUM']}" if x['CAP UTM_SOURCE'] == 'ig' else x['CAP UTM_SOURCE'],
    axis=1
       )
df_vendas_copy['PERCURSO'] = df_vendas_copy['CAP UTM_SOURCE'].astype(str) + ' > ' + \
                            df_vendas_copy['PM UTM_SOURCE'].astype(str) + ' > ' + \
                            df_vendas_copy['UTM_SOURCE'].astype(str)

percurso_counts = df_vendas_copy['PERCURSO'].value_counts().reset_index()
percurso_counts.columns = ['PERCURSO', 'COUNT']

top_20_percurso = percurso_counts.head(20)

col1, col2 = st.columns([2, 2])

with col1:
    st.table(top_20_percurso)

top_5_percurso = top_20_percurso.head(5).sort_values(by='COUNT', ascending=True)

with col2:
    fig, ax = plt.subplots()
    colors = cm.Blues(np.linspace(0.4, 1, len(top_5_percurso)))
    ax.barh(top_5_percurso['PERCURSO'], top_5_percurso['COUNT'], color=colors)
    ax.set_xlabel('Count', color='#FFFFFF')
    ax.set_ylabel('PERCURSO', color='#FFFFFF')
    ax.set_title('Top 5 Percursos Mais Comuns', color='#FFFFFF')
    ax.set_facecolor('none')
    fig.patch.set_facecolor('none')
    ax.spines['bottom'].set_color('#FFFFFF')
    ax.spines['top'].set_color('#FFFFFF')
    ax.spines['right'].set_color('#FFFFFF')
    ax.spines['left'].set_color('#FFFFFF')
    ax.tick_params(axis='x', colors='#FFFFFF')
    ax.tick_params(axis='y', colors='#FFFFFF')
    plt.tight_layout()
    st.pyplot(fig)

### TODO: FINALIZAR O CÓDIGO ACIMA (FIM)