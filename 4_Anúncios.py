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
import plotly.graph_objects as go
from plotly.colors import n_colors

# Carrega o arquivo CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

import plotly.graph_objects as go
import numpy as np

import plotly.graph_objects as go
import numpy as np

def styled_bar_chart_horizontal(labels, sizes):
    # Define a cor para cada valor baseado no colormap 'Blues'
    colorscale = 'Blues'
    normalized_sizes = np.linspace(0, 1, len(sizes))  # Normaliza o tamanho para aplicação da escala de cor

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=labels,
        x=sizes,
        orientation='h',
        marker=dict(
            color=normalized_sizes,  # Aplica cores normalizadas
            colorscale=colorscale,   # Colormap azul
            line=dict(color='#FFFFFF', width=1)
        )
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo do gráfico transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fundo da figura transparente
        xaxis=dict(
            title='',  # Remove o título do eixo X
            color='#FFFFFF',
            tickfont=dict(size=14, color='#FFFFFF'),  # Aumenta o tamanho do texto dos ticks
            showgrid=True,
            gridcolor='#666666'
        ),
        yaxis=dict(
            color='#FFFFFF',
            tickfont=dict(size=16, color='#FFFFFF')  # Aumenta o tamanho do texto dos ticks
        ),
        height=500,  # Define a altura do gráfico
        margin=dict(l=40, r=40, t=20, b=20)  # Ajuste da margem superior para 120
    )

    return fig




def styled_bar_chart_plotly(x, y, title):
    # Usando o colormap 'Blues' do Plotly Express para obter as cores
    num_bars = len(x)
    colors = px.colors.sequential.Blues[num_bars]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=x,
        y=y,
        marker=dict(color=colors),  # Aplicando as cores
    ))

    # Ajustando o layout para corresponder ao estilo do gráfico original
    fig.update_layout(
        title=title,
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fundo da figura transparente
        autosize=True,
        font=dict(color='#FFFFFF'),  # Texto branco
        xaxis=dict(
            tickangle=45,  # Rotacionando os rótulos do eixo x
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

        # Definindo cores usando colormaps de tons de azul
        cmap = colormaps['Blues']
        norm = mcolors.Normalize(vmin=0, vmax=len(x)-1)
        colors = [cmap(norm(i)) for i in range(len(x))]

        ax.bar(x, y, color=colors)
        ax.set_facecolor('none')  # Fundo do gráfico transparente
        fig.patch.set_facecolor('none')  # Fundo da figura transparente
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
def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        return None

df_METAADS = st.session_state.df_METAADS.copy()
df_METAADS = df_METAADS.astype(str)

colunas_numericas = [
    'CPM', 'VALOR USADO', 'LEADS', 'CPL', 'CTR', 'CONNECT RATE',
    'CONVERSAO PAG', 'IMPRESSOES', 'ALCANCE', 'FREQUENCIA',
    'CLICKS', 'CLICKS NO LINK', 'PAGEVIEWS', 'LP CTR', 'PERFIL CTR',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
    '13', '14', '15-20', '20-25', '25-30', '30-40', '40-50', '50-60', '60+'
]


for coluna in colunas_numericas:
    df_METAADS[coluna] = pd.to_numeric(df_METAADS[coluna], errors='coerce')

df_SUBIDOS = st.session_state.df_SUBIDOS.copy()
df_PESQUISA = st.session_state.df_PESQUISA.copy()

df_PESQUISA['UTM_TERM'] = df_PESQUISA['UTM_TERM'].replace('+', ' ')
df_PESQUISA = df_PESQUISA.astype(str)

ticket = 1500 * 0.7
columns = [
    'ANUNCIO', 'TOTAL DE LEADS', 'TOTAL DE PESQUISA',
    'CUSTO POR LEAD', 'PREÇO MÁXIMO', 'DIFERENÇA', 'MARGEM', 'VALOR USADO',
    'CPM', 'CTR', 'CONNECT RATE', 'CONVERSAO PAG', 'Acima de R$1 milhão',
    'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
    'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil',
    'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil', 'TAXA DE RESPOSTA'
]
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
df_PORANUNCIO['TOTAL DE LEADS'] = df_PORANUNCIO['ANUNCIO'] .apply(
    lambda anuncio: df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio]['LEADS'].sum()
)
df_PORANUNCIO['TOTAL DE PESQUISA'] = df_PORANUNCIO['ANUNCIO'] .apply(
    lambda anuncio: df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0]
)
faixas_patrimonio = [
    'Acima de R$1 milhão', 'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
    'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil', 'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil'
]
for faixa in faixas_patrimonio:
    df_PORANUNCIO[faixa] = df_PORANUNCIO['ANUNCIO'] .apply(
        lambda anuncio: (
            df_PESQUISA[(df_PESQUISA['UTM_TERM'] == anuncio) & 
                        (df_PESQUISA['PATRIMONIO'] == faixa)].shape[0] / 
            df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0]
        ) if df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0] != 0 else 0
    )
   
df_PORANUNCIO['PREÇO MÁXIMO'] = ticket * (
    taxas_conversao_patrimonio['Acima de R$1 milhão'] * df_PORANUNCIO['Acima de R$1 milhão'] +
    taxas_conversao_patrimonio['Entre R$500 mil e R$1 milhão'] * df_PORANUNCIO['Entre R$500 mil e R$1 milhão'] +
    taxas_conversao_patrimonio['Entre R$250 mil e R$500 mil'] * df_PORANUNCIO['Entre R$250 mil e R$500 mil'] +
    taxas_conversao_patrimonio['Entre R$100 mil e R$250 mil'] * df_PORANUNCIO['Entre R$100 mil e R$250 mil'] +
    taxas_conversao_patrimonio['Entre R$20 mil e R$100 mil'] * df_PORANUNCIO['Entre R$20 mil e R$100 mil'] +
    taxas_conversao_patrimonio['Entre R$5 mil e R$20 mil'] * df_PORANUNCIO['Entre R$5 mil e R$20 mil'] +
    taxas_conversao_patrimonio['Menos de R$5 mil'] * df_PORANUNCIO['Menos de R$5 mil']
)
df_PORANUNCIO['VALOR USADO'] = df_PORANUNCIO['ANUNCIO'] .apply(
    lambda anuncio: df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio]['VALOR USADO'].sum()
)
df_PORANUNCIO['CUSTO POR LEAD'] = df_PORANUNCIO['VALOR USADO'] / df_PORANUNCIO['TOTAL DE LEADS']
df_PORANUNCIO['DIFERENÇA'] = df_PORANUNCIO['PREÇO MÁXIMO'] - df_PORANUNCIO['CUSTO POR LEAD']
df_PORANUNCIO['MARGEM'] = df_PORANUNCIO['DIFERENÇA'] / df_PORANUNCIO['PREÇO MÁXIMO']
df_PORANUNCIO['CPM'] = df_PORANUNCIO['ANUNCIO'] .apply(
    lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CPM'].mean()
    if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CPM'].empty else "Sem conversões"
)
df_PORANUNCIO['CTR'] = df_PORANUNCIO['ANUNCIO'] .apply(
    lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS'].sum() /
    df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'IMPRESSOES'].sum()
    if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS'].empty else "Sem conversões"
)
df_PORANUNCIO['CONNECT RATE'] = df_PORANUNCIO['ANUNCIO'] .apply(
    lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].sum() /
    df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS NO LINK'].sum()
    if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].empty else "Sem conversões"
)
df_PORANUNCIO['TAXA DE RESPOSTA'] = df_PORANUNCIO.apply(
    lambda row: row['TOTAL DE PESQUISA'] / row['TOTAL DE LEADS'] if row['TOTAL DE LEADS'] != 0 else "Sem respostas", axis=1
)
df_PORANUNCIO['CONVERSAO PAG'] = df_PORANUNCIO['ANUNCIO'] .apply(
    lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'LEADS'].sum() /
    df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].sum()
    if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].empty else "Sem conversões"
)

# Adicionando as colunas de retenção por segundo ao df_PORANUNCIO
colunas_retencao = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
                    '13', '14', '15-20', '20-25', '25-30', '30-40', '40-50', '50-60', '60+']

for col in colunas_retencao:
    df_PORANUNCIO[col] = df_PORANUNCIO['ANUNCIO'] .apply(
        lambda anuncio: df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio][col].mean()
        if not df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio].empty else 0
    )



 # Adicionar slider para selecionar o valor mínimo de 'VALOR USADO'
st.subheader("Selecione o valor mínimo de VALOR USADO:")
min_valor_usado = st.slider("",0, 1000, 250)

# Filtrar DataFrame pelo valor do slider       
df_PORANUNCIO = df_PORANUNCIO[df_PORANUNCIO['VALOR USADO'] >= min_valor_usado]
with st.expander('dataframes'):
    st.dataframe(df_PORANUNCIO)
    st.dataframe(df_METAADS)

# Criar o DataFrame df_STATUS
df_STATUS = pd.DataFrame({
    'ID UNICO': df_METAADS['ANUNCIO: NOME'] + '&' + df_METAADS['CONJUNTO: NOME'],
    'STATUS': ['ATIVO'] * len(df_METAADS)  # Inicialmente todos os status são 'ATIVO'
})

#OUTRO CÓDIGO QUE DEVERIA ESTAR PEGANDO DATAFRAMES DIFERENTES PARA MOSTRAR EM ABAS DIFERENTES

df_METAVIDS = df_METAADS.copy()
# Converter colunas de retenção para numéricas
colunas_retencao = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15-20', '20-25', '25-30', '30-40', '40-50', '50-60', '60+']
# Filtrar anúncios de vídeo (não vazios nas colunas de tempo)
df_videos = df_METAVIDS.dropna(subset=colunas_retencao, how='all')

# Agrupar por 'ANUNCIO: NOME' e calcular a média das retenções e somar 'VALOR USADO'
df_agrupado = df_videos.groupby('ANUNCIO: NOME').agg(
    {**{col: 'mean' for col in colunas_retencao}, 'VALOR USADO': 'sum'}
).reset_index()
 
tabs = st.tabs(["Top Anúncios", "Por Anuncio", "Ranking de hooks"])

with tabs[0]:
    st.header('Análise de Anúncios')
         
    colunas_analise = ['MARGEM', 'VALOR USADO', 'CTR', 'CONVERSAO PAG']
    df_PORANUNCIO_COPY = df_PORANUNCIO.copy()
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
                fig_bottom_5 = styled_bar_chart_plotly(bottom_5['ANUNCIO'], bottom_5[coluna_a], f'Bottom 5 Anúncios - {coluna_a}')
                st.plotly_chart(fig_bottom_5)
            else:
                st.write(f"Não há dados suficientes para os 5 Piores Anúncios - {coluna_a}")

        st.divider()

with tabs[1]:    
    st.header('Detalhes do Anúncio')

    # Pegar todos os anúncios para o selectbox
    anuncios_imagens = df_PORANUNCIO['ANUNCIO'] .unique()

    # Criar o selectbox com todos os anúncios
    selected_anuncio = st.selectbox('Selecione o Anúncio', anuncios_imagens)
    st.divider()

    # Verifica se o anúncio selecionado contém 'ADNI' ou 'ADOI'
    if "ADNI" in selected_anuncio or "ADOI" in selected_anuncio:
        anuncio_data = df_PORANUNCIO[df_PORANUNCIO['ANUNCIO']  == selected_anuncio].iloc[0]     
        st.header(f"Anúncio: {selected_anuncio}")
        
        # Ajuste das colunas para exibir a imagem e o gráfico de patrimônio
        x1, x2 = st.columns([0.2, 0.8])
        with st.container():
            with x1:
                # Encontrar o link da imagem correspondente no df_SUBIDOS
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
                st.plotly_chart(fig_patrimonio, use_container_width=True)  # Use o máximo de espaço disponível

        # Espaçamento entre o gráfico e as métricas
        st.divider()

        # Cria as métricas embaixo da imagem e do gráfico
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
            
        # Código para anúncios de vídeo   
        st.header(f"Anúncio: {selected_anuncio}")
        
        # Colunas para gráfico de retenção (50%) e gráfico de patrimônio (50%)
        video_col1, video_col2 = st.columns([0.5, 0.5])
        
        with video_col1:
            st.subheader("Retenção do Vídeo:")
            
            # Segundos ou faixas de tempo
            retencao_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
                            '11', '12', '13', '14', '15-20', '20-25', '25-30', 
                            '30-40', '40-50', '50-60', '60+']  
            
            # Obtenha os valores de retenção correspondentes
            retencao_values = [df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, label].values[0] 
                            for label in retencao_labels]
            
            # Expandir as faixas de tempo em valores individuais
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
            
            # Criar o gráfico de área sob a curva de retenção usando Plotly
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

            # Adicionando o CTR abaixo do gráfico de retenção
            st.subheader("CTR:")
            st.metric(label="CTR", value=f"{df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'CTR'].values[0]:.2%}", delta_color="off")

        with video_col2:
            st.subheader("Distribuição de Patrimônio:")
            patrimonio_labels = [
                'Acima de R$1 milhão', 'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
                'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil', 'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil'
            ]
            patrimonio_sizes = [
                df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, label].values[0] 
                for label in patrimonio_labels
            ]

            fig_patrimonio = styled_bar_chart_horizontal(patrimonio_labels, patrimonio_sizes)
            st.plotly_chart(fig_patrimonio, use_container_width=True)  # Use o máximo de espaço disponível

        # Espaçamento entre o gráfico/CTR e as métricas gerais
        st.divider()

        # Cria as métricas gerais abaixo do gráfico e do CTR
        st.subheader(f"Detalhes do Anúncio: {selected_anuncio}")
        img_metrica1, img_metrica2, img_metrica3, img_metrica4 = st.columns(4)
        with img_metrica1:
            st.metric(label="Total de Leads", value=df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'TOTAL DE LEADS'].values[0])
        with img_metrica2:
            st.metric(label="Total de Pesquisa", value=df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'TOTAL DE PESQUISA'].values[0])
        with img_metrica3:
            st.metric(label="Custo por Lead", value=f"R$ {df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'CUSTO POR LEAD'].values[0]:.2f}")
        with img_metrica4:
            st.metric(label="Preço Máximo", value=f"R$ {df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'PREÇO MÁXIMO'].values[0]:.2f}")
        
        img_metrica5, img_metrica6, img_metrica7, img_metrica8 = st.columns(4)
        with img_metrica5:
            st.metric(label="Diferença", value=f"R$ {df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'DIFERENÇA'].values[0]:.2f}")
        with img_metrica6:
            st.metric(label="Margem", value=f"{df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'MARGEM'].values[0]:-.2%}")
        with img_metrica7:
            st.metric(label="Valor Usado", value=f"R$ {df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'VALOR USADO'].values[0]:.2f}")
        with img_metrica8:
            st.metric(label="CPM", value=f"R$ {df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'CPM'].values[0]:.2f}")

        img_metrica9, img_metrica10, img_metrica11, img_metrica12 = st.columns(4)
        with img_metrica9:
            st.metric(label="Connect Rate", value=f"{df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'CONNECT RATE'].values[0]:.2%}")
        with img_metrica10:
            st.metric(label="Conversão da Página", value=f"{df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'CONVERSAO PAG'].values[0]:.2%}")
        with img_metrica11:
            st.metric(label="Taxa de Resposta", value=f"{df_PORANUNCIO.loc[df_PORANUNCIO['ANUNCIO']  == selected_anuncio, 'TAXA DE RESPOSTA'].values[0]:.2%}")


with tabs[2]:
    st.write("Análise de Hook de Vídeos")

    # Garantir que os dados estejam carregados na aba "Dados"
    if 'df_videos' in locals() and df_videos is not None:
        # Perguntar em qual segundo avaliar a retenção
        segundo = st.selectbox('Em qual segundo deseja avaliar a retenção?', list(range(1, 11)), index=4)
        
        col1, col2 = st.columns(2)
        with col1:
            top_or_bottom = st.selectbox('Selecionar', ['Melhores', 'Piores'])
        with col2:
            top_n = st.selectbox('Quantidade', list(range(3, 11)), index=2)

        # Mostrar o dataframe de acordo com a seleção
        if st.button("Mostrar Anúncios"):
            col_retenção = str(segundo)
            if top_or_bottom == 'Melhores':
                top_anuncios = df_videos.nlargest(top_n, col_retenção)
            else:
                top_anuncios = df_videos.nsmallest(top_n, col_retenção)
            
            # Mostrar o dataframe dos top anúncios
            st.write(f"Top {top_n} anúncios de acordo com a retenção no segundo {segundo}:")
            st.dataframe(top_anuncios)