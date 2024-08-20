import requests
from PIL import Image, UnidentifiedImageError
import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from matplotlib import colormaps
import matplotlib.colors as mcolors
import time

# Definindo as colunas do DataFrame df_PORANUNCIO
columns = [
    'ANUNCIO', 'TOTAL DE LEADS', 'TOTAL DE PESQUISA',
    'CUSTO POR LEAD', 'PREÇO MÁXIMO', 'DIFERENÇA', 'MARGEM', 'VALOR USADO',
    'CPM', 'CTR', 'CONNECT RATE', 'CONVERSAO PAG', 'Acima de R$1 milhão',
    'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
    'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil',
    'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil', 'TAXA DE RESPOSTA'
]

# Definindo as colunas numéricas que precisam ser convertidas
colunas_numericas = [
    'CPM', 'VALOR USADO', 'LEADS', 'CPL', 'CTR', 'CONNECT RATE',
    'CONVERSAO PAG', 'IMPRESSOES', 'ALCANCE', 'FREQUENCIA',
    'CLICKS', 'CLICKS NO LINK', 'PAGEVIEWS', 'LP CTR', 'PERFIL CTR',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
    '13', '14', '15-20', '20-25', '25-30', '30-40', '40-50', '50-60', '60+'
]

# Colunas de retenção de vídeos
colunas_retencao = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
    '11', '12', '13', '14', '15-20', '20-25', '25-30', 
    '30-40', '40-50', '50-60', '60+'
]

# Função para transformar link de compartilhamento do Google Drive em link direto para imagem
def transform_drive_link(link):
    if "drive.google.com" in link and "file/d/" in link:
        file_id = link.split("file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    elif "drive.google.com" in link and "id=" in link:
        file_id = link.split("id=")[1].split("&")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    else:
        return link

# Função para baixar a imagem a partir de um link
@st.cache_data
def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        return None

# Função para processar as colunas numéricas
@st.cache_data
def processa_colunas_numericas(df, colunas):
    for coluna in colunas:
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce')
    return df

# Função para calcular valores por anúncio
@st.cache_data
def calcular_valores_por_anuncio(df_METAADS, df_PESQUISA, ticket):
    # Criando o DataFrame com as colunas definidas
    df_PORANUNCIO = pd.DataFrame(columns=columns)

    taxas_conversao_patrimonio = {
        'Acima de R$1 milhão': 0.0489,
        'Entre R$500 mil e R$1 milhão': 0.0442,
        'Entre R$250 mil e R$500 mil': 0.0400,
        'Entre R$100 mil e R$250 mil': 0.0382,
        'Entre R$20 mil e R$100 mil': 0.0203,
        'Entre R$5 mil e R$20 mil': 0.0142,
        'Menos de R$5 mil': 0.0067
    }

    anuncios_unicos = df_METAADS['ANUNCIO: NOME'].unique()
    df_PORANUNCIO['ANUNCIO']  = pd.Series(anuncios_unicos)
    df_PORANUNCIO['TOTAL DE LEADS'] = df_PORANUNCIO['ANUNCIO'].apply(
        lambda anuncio: df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio]['LEADS'].sum()
    )
    df_PORANUNCIO['TOTAL DE PESQUISA'] = df_PORANUNCIO['ANUNCIO'].apply(
        lambda anuncio: df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0]
    )
    for faixa in taxas_conversao_patrimonio.keys():
        df_PORANUNCIO[faixa] = df_PORANUNCIO['ANUNCIO'].apply(
            lambda anuncio: (
                df_PESQUISA[(df_PESQUISA['UTM_TERM'] == anuncio) & 
                            (df_PESQUISA['PATRIMONIO'] == faixa)].shape[0] / 
                df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0]
            ) if df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0] != 0 else 0
        )

    df_PORANUNCIO['PREÇO MÁXIMO'] = ticket * sum(
        df_PORANUNCIO[faixa] * taxa for faixa, taxa in taxas_conversao_patrimonio.items()
    )

    df_PORANUNCIO['VALOR USADO'] = df_PORANUNCIO['ANUNCIO'].apply(
        lambda anuncio: df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio]['VALOR USADO'].sum()
    )
    df_PORANUNCIO['CUSTO POR LEAD'] = df_PORANUNCIO['VALOR USADO'] / df_PORANUNCIO['TOTAL DE LEADS']
    df_PORANUNCIO['DIFERENÇA'] = df_PORANUNCIO['PREÇO MÁXIMO'] - df_PORANUNCIO['CUSTO POR LEAD']
    df_PORANUNCIO['MARGEM'] = df_PORANUNCIO['DIFERENÇA'] / df_PORANUNCIO['PREÇO MÁXIMO']

    df_PORANUNCIO['CPM'] = df_PORANUNCIO['ANUNCIO'].apply(
        lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CPM'].mean()
        if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CPM'].empty else "Sem conversões"
    )
    df_PORANUNCIO['CTR'] = df_PORANUNCIO['ANUNCIO'].apply(
        lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS'].sum() /
        df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'IMPRESSOES'].sum()
        if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS'].empty else "Sem conversões"
    )
    df_PORANUNCIO['CONNECT RATE'] = df_PORANUNCIO['ANUNCIO'].apply(
        lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].sum() /
        df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS NO LINK'].sum()
        if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].empty else "Sem conversões"
    )
    df_PORANUNCIO['TAXA DE RESPOSTA'] = df_PORANUNCIO.apply(
        lambda row: row['TOTAL DE PESQUISA'] / row['TOTAL DE LEADS'] if row['TOTAL DE LEADS'] != 0 else "Sem respostas", axis=1
    )
    df_PORANUNCIO['CONVERSAO PAG'] = df_PORANUNCIO['ANUNCIO'].apply(
        lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'LEADS'].sum() /
        df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].sum()
        if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].empty else "Sem conversões"
    )

    # Adicionando as colunas de retenção ao DataFrame df_PORANUNCIO
    for col in colunas_retencao:
        df_PORANUNCIO[col] = df_PORANUNCIO['ANUNCIO'].apply(
            lambda anuncio: df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio][col].mean()
            if not df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio].empty else 0
        )

    return df_PORANUNCIO

# Estilização de gráficos
def styled_bar_chart_horizontal(labels, sizes):
    colorscale = 'Blues'
    normalized_sizes = np.linspace(0, 1, len(sizes))

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=labels,
        x=sizes,
        orientation='h',
        marker=dict(
            color=normalized_sizes,
            colorscale=colorscale,
            line=dict(color='#FFFFFF', width=1)
        )
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            color='#FFFFFF',
            tickfont=dict(size=14, color='#FFFFFF'),
            showgrid=True,
            gridcolor='#666666'
        ),
        yaxis=dict(
            color='#FFFFFF',
            tickfont=dict(size=16, color='#FFFFFF')
        ),
        height=500,
        margin=dict(l=40, r=40, t=20, b=20)
    )

    return fig

def styled_bar_chart_plotly(x, y, title):
    num_bars = len(x)
    colors = px.colors.sequential.Blues[num_bars]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=x,
        y=y,
        marker=dict(color=colors),
    ))

    fig.update_layout(
        title=title,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        autosize=True,
        font=dict(color='#FFFFFF'),
        xaxis=dict(
            tickangle=45,
            tickfont=dict(color='#FFFFFF'),
            showline=True,
            linecolor='#FFFFFF'
        ),
        yaxis=dict(
            tickfont=dict(color='#FFFFFF'),
            showline=True,
            linecolor='#FFFFFF'
        ),
        title_font=dict(color='#FFFFFF'),
    )

    fig.update_traces(marker_line_color='white', marker_line_width=1.5)
    
    return fig

def styled_bar_chart(x, y, title):
    fig, ax = plt.subplots()

    cmap = colormaps['Blues']
    norm = mcolors.Normalize(vmin=0, vmax=len(x)-1)
    colors = [cmap(norm(i)) for i in range(len(x))]

    ax.bar(x, y, color=colors)
    ax.set_facecolor('none')
    fig.patch.set_facecolor('none')
    ax.spines['bottom'].set_color('#FFFFFF')
    ax.spines['top'].set_color('#FFFFFF')
    ax.spines['right'].set_color('#FFFFFF')
    ax.spines['left'].set_color('#FFFFFF')
    ax.tick_params(axis='x', colors='#FFFFFF', rotation=45)
    ax.tick_params(axis='y', colors='#FFFFFF')
    ax.set_title(title, color='#FFFFFF')
    ax.set_ylabel('Conversão', color='#FFFFFF')
    ax.set_xlabel(' ', color='#FFFFFF')
    plt.setp(ax.get_xticklabels(), color="#FFFFFF", rotation=45, ha='right')
    plt.setp(ax.get_yticklabels(), color="#FFFFFF")
    
    return fig


# Carregamento dos dataframes da sessão
df_METAADS = st.session_state.df_METAADS.copy()
df_METAADS = processa_colunas_numericas(df_METAADS, colunas_numericas)

df_SUBIDOS = st.session_state.df_SUBIDOS.copy()
df_PESQUISA = st.session_state.df_PESQUISA.copy()
df_PESQUISA['UTM_TERM'] = df_PESQUISA['UTM_TERM'].replace('+', ' ')
df_PESQUISA = df_PESQUISA.astype(str)

ticket = 1500 * 0.7

# Calcular valores por anúncio com cacheamento
df_PORANUNCIO = calcular_valores_por_anuncio(df_METAADS, df_PESQUISA, ticket)

# Adicionar slider para selecionar o valor mínimo de 'VALOR USADO'
st.subheader("Selecione o valor mínimo de VALOR USADO:")
min_valor_usado = st.slider("", 0, 1000, 250)

# Filtrar DataFrame pelo valor do slider       
df_PORANUNCIO = df_PORANUNCIO[df_PORANUNCIO['VALOR USADO'] >= min_valor_usado]

with st.expander('dataframes'):
    st.dataframe(df_PORANUNCIO)
    st.dataframe(df_METAADS)

df_METAVIDS = df_METAADS.copy()
df_videos = df_METAVIDS.dropna(subset=colunas_retencao, how='all')

df_agrupado = df_videos.groupby('ANUNCIO: NOME').agg(
    {**{col: 'mean' for col in colunas_retencao}, 'VALOR USADO': 'sum'}
).reset_index()
 
tabs = st.tabs(["Top Anúncios", "Por Anuncio", "Ranking de hooks"])

with tabs[0]:
    st.header('Análise de Anúncios')
         
    colunas_analise = ['MARGEM', 'VALOR USADO', 'CTR', 'CONVERSAO PAG']
    df_PORANUNCIO_COPY = df_PORANUNCIO.copy()

    # Transformar colunas para numéricas
    for coluna_a in colunas_analise:
        df_PORANUNCIO_COPY[coluna_a] = pd.to_numeric(df_PORANUNCIO_COPY[coluna_a], errors='coerce')

    for coluna_a in colunas_analise:
        df_filtrado = df_PORANUNCIO_COPY[
            (df_PORANUNCIO_COPY[coluna_a].notnull()) &
            (df_PORANUNCIO_COPY[coluna_a] != 0) &
            (df_PORANUNCIO_COPY[coluna_a] != "Sem respostas") &
            (df_PORANUNCIO_COPY[coluna_a] != "")
        ]
        top_5 = df_filtrado.nlargest(5, coluna_a)
        bottom_5 = df_filtrado.nsmallest(5, coluna_a)
        st.subheader(f'Análise da Coluna: {coluna_a}')
        col1, col2 = st.columns(2)
        with col1:
            if not top_5.empty:
                fig_top_5 = styled_bar_chart_plotly(top_5['ANUNCIO'], top_5[coluna_a], f'5 Melhores Anúncios - {coluna_a}')
                st.plotly_chart(fig_top_5)
            else:
                st.write(f"Não há dados suficientes para os 5 Melhores Anúncios - {coluna_a}")
        with col2:
            if not bottom_5.empty and len(bottom_5) >= 5:
                fig_bottom_5 = styled_bar_chart_plotly(bottom_5['ANUNCIO'], bottom_5[coluna_a], f'5 Piores Anúncios - {coluna_a}')
                st.plotly_chart(fig_bottom_5)
            else:
                st.write(f"Não há dados suficientes para os 5 Piores Anúncios - {coluna_a}")

        st.divider()

with tabs[1]:    
    st.header('Detalhes do Anúncio')

    anuncios_imagens = df_PORANUNCIO['ANUNCIO'].unique()
    selected_anuncio = st.selectbox('Selecione o Anúncio', anuncios_imagens)
    st.divider()

    anuncio_data = df_PORANUNCIO[df_PORANUNCIO['ANUNCIO'] == selected_anuncio].iloc[0]

    if "ADNI" in selected_anuncio or "ADOI" in selected_anuncio:
        st.header(f"Anúncio: {selected_anuncio}")
        
        x1, x2 = st.columns([0.2, 0.8])
        with st.container():
            with x1:
                drive_link = df_SUBIDOS.loc[df_SUBIDOS['ANUNCIO'] == selected_anuncio, 'LINK DO DRIVE'].values[0]
                image_link = transform_drive_link(drive_link)

                if "ADNV" in selected_anuncio:               
                    st.write(f"Link do Video: [Clique aqui]({image_link})")
                else:
                    st.subheader("Imagem:")
                    st.write(f"[Link]({image_link})")    

                try:
                    image = download_image(image_link)
                    if image:
                        st.image(image, caption=selected_anuncio, width=280)  
                except UnidentifiedImageError:
                    st.write("Clique no link para assistir o anúncio de vídeo")

            with x2:
                st.subheader("Distribuição de Patrimônio:")
                patrimonio_labels = [
                    'Acima de R$1 milhão', 'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
                    'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil', 'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil'
                ]
                patrimonio_sizes = [
                    anuncio_data.get('Acima de R$1 milhão', 0), anuncio_data.get('Entre R$500 mil e R$1 milhão', 0),
                    anuncio_data.get('Entre R$250 mil e R$500 mil', 0), anuncio_data.get('Entre R$100 mil e R$250 mil', 0),
                    anuncio_data.get('Entre R$20 mil e R$100 mil', 0), anuncio_data.get('Entre R$5 mil e R$20 mil', 0),
                    anuncio_data.get('Menos de R$5 mil', 0)
                ]

                fig_patrimonio = styled_bar_chart_horizontal(patrimonio_labels, patrimonio_sizes)
                st.plotly_chart(fig_patrimonio, use_container_width=True)

        st.divider()

        st.subheader(f"Detalhes do Anúncio: {selected_anuncio}")
        img_metrica1, img_metrica2, img_metrica3, img_metrica4 = st.columns(4)
        with img_metrica1:
            st.metric(label="Total de Leads", value=anuncio_data['TOTAL DE LEADS'])
        with img_metrica2:
            st.metric(label="Total de Pesquisa", value=anuncio_data['TOTAL DE PESQUISA'])
        with img_metrica3:
            st.metric(label="Custo por Lead", value=f"R$ {anuncio_data['CUSTO POR LEAD']:.2f}")
        with img_metrica4:
            st.metric(label="Preço Máximo", value=f"R$ {anuncio_data['PREÇO MÁXIMO']:.2f}")
        
        img_metrica5, img_metrica6, img_metrica7, img_metrica8 = st.columns(4)
        with img_metrica5:
            st.metric(label="Diferença", value=f"R$ {anuncio_data['DIFERENÇA']:.2f}")
        with img_metrica6:
            st.metric(label="Margem", value=f"{anuncio_data['MARGEM']:.2%}")
        with img_metrica7:
            st.metric(label="Valor Usado", value=f"R$ {anuncio_data['VALOR USADO']:.2f}")
        with img_metrica8:
            st.metric(label="CPM", value=f"R$ {anuncio_data['CPM']:.2f}")

        img_metrica9, img_metrica10, img_metrica11, img_metrica12 = st.columns(4)
        with img_metrica9:
            st.metric(label="CTR", value=f"{anuncio_data['CTR']:.2%}")
        with img_metrica10:
            st.metric(label="Connect Rate", value=f"{anuncio_data['CONNECT RATE']:.2%}")
        with img_metrica11:
            st.metric(label="Conversão da Página", value=f"{anuncio_data['CONVERSAO PAG']:.2%}")
        with img_metrica12:
            st.metric(label="Taxa de Resposta", value=f"{anuncio_data['TAXA DE RESPOSTA']:.2%}")
    
    else:
        st.header(f"Anúncio: {selected_anuncio}")
        
        video_col1, video_col2 = st.columns([0.5, 0.5])
        
        with video_col1:
            st.subheader("Retenção do Vídeo:")
            
            retencao_labels = [
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
                '11', '12', '13', '14', '15-20', '20-25', '25-30', 
                '30-40', '40-50', '50-60', '60+'
            ]  
            
            retencao_values = [
                df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio].get(label, 0).values[0]
                for label in retencao_labels
            ]
            
            expanded_labels = []
            expanded_values = []

            for label, value in zip(retencao_labels, retencao_values):
                if '-' in label:
                    start, end = map(int, label.split('-'))
                    for i in range(start, end + 1):
                        expanded_labels.append(str(i))
                        expanded_values.append(value)
                elif '+' in label:
                    start = int(label.replace('+', ''))
                    for i in range(start, 61):
                        expanded_labels.append(str(i))
                        expanded_values.append(value)
                else:
                    expanded_labels.append(label)
                    expanded_values.append(value)
            
            fig_retencao = go.Figure()
            fig_retencao.add_trace(go.Scatter(
                x=expanded_labels,
                y=expanded_values,
                fill='tozeroy',
                line=dict(color='royalblue'),
                mode='lines'
            ))

            fig_retencao.update_layout(
                xaxis=dict(
                    title='Tempo de Retenção', 
                    color='#FFFFFF', 
                    tickfont=dict(size=14),
                    range=[1, 15]
                ),
                yaxis=dict(title='Retenção (%)', color='#FFFFFF', tickfont=dict(size=14)),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20)
            )

            st.plotly_chart(fig_retencao, use_container_width=True)

            st.subheader("CTR:")
            st.metric(label="CTR", value=f"{df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'CTR'].values[0]:.2%}", delta_color="off")

        with video_col2:
            st.subheader("Distribuição de Patrimônio:")
            patrimonio_labels = [
                'Acima de R$1 milhão', 'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
                'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil', 'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil'
            ]
            patrimonio_sizes = [
                df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio].get(label, 0).values[0] 
                for label in patrimonio_labels
            ]

            fig_patrimonio = styled_bar_chart_horizontal(patrimonio_labels, patrimonio_sizes)
            st.plotly_chart(fig_patrimonio, use_container_width=True)

        st.divider()

        st.subheader(f"Detalhes do Anúncio: {selected_anuncio}")
        img_metrica1, img_metrica2, img_metrica3, img_metrica4 = st.columns(4)
        with img_metrica1:
            st.metric(label="Total de Leads", value=df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'TOTAL DE LEADS'].values[0])
        with img_metrica2:
            st.metric(label="Total de Pesquisa", value=df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'TOTAL DE PESQUISA'].values[0])
        with img_metrica3:
            st.metric(label="Custo por Lead", value=f"R$ {df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'CUSTO POR LEAD'].values[0]:.2f}")
        with img_metrica4:
            st.metric(label="Preço Máximo", value=f"R$ {df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'PREÇO MÁXIMO'].values[0]:.2f}")
        
        img_metrica5, img_metrica6, img_metrica7, img_metrica8 = st.columns(4)
        with img_metrica5:
            st.metric(label="Diferença", value=f"R$ {df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'DIFERENÇA'].values[0]:.2f}")
        with img_metrica6:
            st.metric(label="Margem", value=f"{df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'MARGEM'].values[0]:-.2%}")
        with img_metrica7:
            st.metric(label="Valor Usado", value=f"R$ {df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'VALOR USADO'].values[0]:.2f}")
        with img_metrica8:
            st.metric(label="CPM", value=f"R$ {df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'CPM'].values[0]:.2f}")

        img_metrica9, img_metrica10, img_metrica11, img_metrica12 = st.columns(4)
        with img_metrica9:
            st.metric(label="Connect Rate", value=f"{df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'CONNECT RATE'].values[0]:.2%}")
        with img_metrica10:
            st.metric(label="Conversão da Página", value=f"{df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'CONVERSAO PAG'].values[0]:.2%}")
        with img_metrica11:
            st.metric(label="Taxa de Resposta", value=f"{df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == selected_anuncio, 'TAXA DE RESPOSTA'].values[0]:.2%}")

with tabs[2]:
    # Usando st.markdown com HTML para aumentar o tamanho do texto e adicionar um espaço
    st.markdown(
        """
        <h1 style="font-size: 48px; text-align: center; margin-bottom: 40px;">Ranking de Hooks</h1>
        """,
        unsafe_allow_html=True
    )

    # Container com borda
    with st.container(border=True):
        if 'df_videos' in locals() and df_videos is not None:
            segundo = 3  # Avaliar a retenção no 3º segundo, como exemplo
            col_retenção = str(segundo)
            
            # Garantir que a coluna 'col_retenção' exista em df_videos
            if col_retenção in df_videos.columns:
                # Ordenar os vídeos pela retenção no 3º segundo, de forma decrescente
                top_10_hooks = df_videos.nlargest(10, col_retenção).reset_index(drop=True)

                for i, row in top_10_hooks.iterrows():
                    # Título do anúncio
                    st.markdown(f"### {i + 1} - {row['ANUNCIO: NOME']}", unsafe_allow_html=True)

                    # Criando colunas para o gráfico de retenção (40%) e as métricas (60%)
                    col1, col2 = st.columns([1, 1.4], gap="large")  # Gap maior entre as colunas

                    with col1:
                        # Título menor com espaço abaixo
                        st.markdown("<h4 style='margin-bottom: 20px;'>Retenção do Vídeo:</h4>", unsafe_allow_html=True)

                        # Filtrar o DataFrame para o anúncio atual
                        filtered_df = df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO'] == row['ANUNCIO: NOME']]

                        # Verificar se há dados para o anúncio
                        if not filtered_df.empty:
                            # Obter os valores de retenção correspondentes
                            retencao_values = [
                                filtered_df.get(label, 0).values[0] for label in retencao_labels
                            ]

                            # Expandir as faixas de tempo em valores individuais
                            expanded_labels = []
                            expanded_values = []

                            for label, value in zip(retencao_labels, retencao_values):
                                if '-' in label:
                                    start, end = map(int, label.split('-'))
                                    for j in range(start, end + 1):
                                        expanded_labels.append(str(j))
                                        expanded_values.append(value)
                                elif '+' in label:
                                    start = int(label.replace('+', ''))
                                    for j in range(start, 61):
                                        expanded_labels.append(str(j))
                                        expanded_values.append(value)
                                else:
                                    expanded_labels.append(label)
                                    expanded_values.append(value)

                            # Criar o gráfico de retenção usando Plotly
                            fig_retencao = go.Figure()
                            fig_retencao.add_trace(go.Scatter(
                                x=expanded_labels,
                                y=expanded_values,
                                fill='tozeroy',
                                line=dict(color='royalblue'),
                                mode='lines'
                            ))

                            fig_retencao.update_layout(
                                xaxis=dict(
                                    title='Tempo de Retenção',
                                    color='#FFFFFF',
                                    tickfont=dict(size=14),
                                    range=[1, 15]
                                ),
                                yaxis=dict(title='Retenção (%)', color='#FFFFFF', tickfont=dict(size=14)),
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                margin=dict(l=20, r=20, t=20, b=20),
                                height=250  # Diminuindo a altura do gráfico para torná-lo mais compacto
                            )

                            st.plotly_chart(fig_retencao, use_container_width=True)
                        else:
                            st.write("Dados de retenção não disponíveis para este anúncio.")

                    with col2:
                        # Verificar novamente se há dados para exibir as métricas
                        if not filtered_df.empty:
                            # Exibir as métricas em destaque alinhadas em três colunas
                            col21, col22, col23 = st.columns(3)

                            ctr_value = filtered_df['CTR'].values[0]
                            retencao_no_segundo = filtered_df[col_retenção].values[0]
                            total_leads = filtered_df['TOTAL DE LEADS'].values[0]

                            with col21:
                                st.metric(label="CTR", value=f"{ctr_value:.2%}")
                            with col22:
                                st.metric(label=f"Retenção no segundo {segundo}", value=f"{retencao_no_segundo:.2f}%")
                            with col23:
                                st.metric(label="Total de Leads", value=int(total_leads))
                        else:
                            st.write("Métricas não disponíveis para este anúncio.")

                    st.divider()  # Linha divisória entre os blocos de anúncios
            else:
                st.error(f"A coluna '{col_retenção}' não existe no DataFrame.")
