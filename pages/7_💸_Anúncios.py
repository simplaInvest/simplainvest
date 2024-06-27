import requests
from PIL import Image, UnidentifiedImageError
import io
import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from matplotlib import colormaps
import matplotlib.colors as mcolors
import time
import pyarrow as pa
import pyarrow.parquet as pq


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

# Função para carregar uma aba específica de uma planilha
#@st.cache
def load_sheet(sheet_name, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('autorizador.json', scope)
    client = gspread.authorize(creds)
    # Open the Google spreadsheet
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    # Get all data from the sheet
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Carregar dados da planilha
#@st.cache
def load_data(spreadsheet_trafego):
    df_METAADS = load_sheet(spreadsheet_trafego, 'NEW META ADS')
    df_METAADS = df_METAADS.astype(str)
    colunas_numericas = [
        'CPM', 'VALOR USADO', 'LEADS', 'CPL', 'CTR', 'CONNECT RATE',
        'CONVERSAO PAG', 'IMPRESSOES', 'ALCANCE', 'FREQUENCIA',
        'CLICKS', 'CLICKS NO LINK', 'PAGEVIEWS', 'LP CTR', 'PERFIL CTR',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
        '13', '14', '15-20', '20-25', '25-30', '30-40', '40-50', '50-60', '60+'
    ]
    table = pa.Table.from_pandas(df_METAADS)
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    df_METAADS = pq.read_table(buffer).to_pandas()
    for coluna in colunas_numericas:
        df_METAADS[coluna] = pd.to_numeric(df_METAADS[coluna], errors='coerce')

    df_SUBIDOS = load_sheet(spreadsheet_trafego, 'ANUNCIOS SUBIDOS')
    df_PESQUISA = load_sheet(spreadsheet_trafego, 'DADOS')
    df_PESQUISA['UTM_TERM'] = df_PESQUISA['UTM_TERM'].replace('+', ' ')
    df_PESQUISA = df_PESQUISA.astype(str)
    table = pa.Table.from_pandas(df_PESQUISA)
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    df_PESQUISA = pq.read_table(buffer).to_pandas()

    return df_METAADS, df_SUBIDOS, df_PESQUISA

# Perguntar qual lançamento a pessoa gostaria de analisar
st.write('Qual o Lançamento em Questão?')

# Dropdown para selecionar o produto
produto = st.selectbox('Produto', ['EI', 'SC'])

# Dropdown para selecionar a versão
versao = st.selectbox('Versão', list(range(1, 31)))

# Formatar os inputs do usuário
start_time = time.time()
lancamentoT = f"{produto}.{str(versao).zfill(2)}"
spreadsheet_trafego = lancamentoT + ' - PESQUISA TRAFEGO'
st.write(f"Lançamento selecionado: {lancamentoT}")
st.write(f"Planilha Central: {spreadsheet_trafego}")

 # Adicionar slider para selecionar o valor mínimo de 'VALOR USADO'
min_valor_usado = st.slider("Selecione o valor mínimo de 'VALOR USADO'", 0, 1000, 250)

# Botão para continuar para a análise
if st.button("Continuar para Análise"):
    #st.cache.clear()  # Limpar o cache antes de recarregar os dados
    st.session_state['analyze_clicked'] = True

if 'analyze_clicked' not in st.session_state:
    st.session_state['analyze_clicked'] = False

if st.session_state['analyze_clicked']:   
    
    tabs = st.tabs(["Planilhas", "Top Anúncios", "Por Anuncio"])

    # Carregar os dados uma única vez
    df_METAADS, df_SUBIDOS, df_PESQUISA = load_data(spreadsheet_trafego)
    
    with tabs[0]:
              
        ticket = 1500 * 0.7
        columns = [
            'ANÚNCIO', 'TOTAL DE LEADS', 'TOTAL DE PESQUISA',
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
        df_PORANUNCIO['ANÚNCIO'] = pd.Series(anuncios_unicos)
        df_PORANUNCIO['TOTAL DE LEADS'] = df_PORANUNCIO['ANÚNCIO'].apply(
            lambda anuncio: df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio]['LEADS'].sum()
        )
        df_PORANUNCIO['TOTAL DE PESQUISA'] = df_PORANUNCIO['ANÚNCIO'].apply(
            lambda anuncio: df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0]
        )
        faixas_patrimonio = [
            'Acima de R$1 milhão', 'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
            'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil', 'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil'
        ]
        for faixa in faixas_patrimonio:
            df_PORANUNCIO[faixa] = df_PORANUNCIO['ANÚNCIO'].apply(
                lambda anuncio: (
                    df_PESQUISA[(df_PESQUISA['UTM_TERM'] == anuncio) & 
                                (df_PESQUISA['PATRIMONIO'] == faixa)].shape[0] / 
                    df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0]
                ) if df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0] != 0 else 0
            )
        end_time = time.time()
        execution_time = end_time - start_time    
        st.write("Tempo de execução do código otimizado:", execution_time)
        df_PORANUNCIO['PREÇO MÁXIMO'] = ticket * (
            taxas_conversao_patrimonio['Acima de R$1 milhão'] * df_PORANUNCIO['Acima de R$1 milhão'] +
            taxas_conversao_patrimonio['Entre R$500 mil e R$1 milhão'] * df_PORANUNCIO['Entre R$500 mil e R$1 milhão'] +
            taxas_conversao_patrimonio['Entre R$250 mil e R$500 mil'] * df_PORANUNCIO['Entre R$250 mil e R$500 mil'] +
            taxas_conversao_patrimonio['Entre R$100 mil e R$250 mil'] * df_PORANUNCIO['Entre R$100 mil e R$250 mil'] +
            taxas_conversao_patrimonio['Entre R$20 mil e R$100 mil'] * df_PORANUNCIO['Entre R$20 mil e R$100 mil'] +
            taxas_conversao_patrimonio['Entre R$5 mil e R$20 mil'] * df_PORANUNCIO['Entre R$5 mil e R$20 mil'] +
            taxas_conversao_patrimonio['Menos de R$5 mil'] * df_PORANUNCIO['Menos de R$5 mil']
        )
        df_PORANUNCIO['VALOR USADO'] = df_PORANUNCIO['ANÚNCIO'].apply(
            lambda anuncio: df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio]['VALOR USADO'].sum()
        )
        df_PORANUNCIO['CUSTO POR LEAD'] = df_PORANUNCIO['VALOR USADO'] / df_PORANUNCIO['TOTAL DE LEADS']
        df_PORANUNCIO['DIFERENÇA'] = df_PORANUNCIO['PREÇO MÁXIMO'] - df_PORANUNCIO['CUSTO POR LEAD']
        df_PORANUNCIO['MARGEM'] = df_PORANUNCIO['DIFERENÇA'] / df_PORANUNCIO['PREÇO MÁXIMO']
        df_PORANUNCIO['CPM'] = df_PORANUNCIO['ANÚNCIO'].apply(
            lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CPM'].mean()
            if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CPM'].empty else "Sem conversões"
        )
        df_PORANUNCIO['CTR'] = df_PORANUNCIO['ANÚNCIO'].apply(
            lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS'].sum() /
            df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'IMPRESSOES'].sum()
            if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS'].empty else "Sem conversões"
        )
        df_PORANUNCIO['CONNECT RATE'] = df_PORANUNCIO['ANÚNCIO'].apply(
            lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].sum() /
            df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS NO LINK'].sum()
            if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].empty else "Sem conversões"
        )
        df_PORANUNCIO['TAXA DE RESPOSTA'] = df_PORANUNCIO.apply(
            lambda row: row['TOTAL DE PESQUISA'] / row['TOTAL DE LEADS'] if row['TOTAL DE LEADS'] != 0 else "Sem respostas", axis=1
        )
        df_PORANUNCIO['CONVERSAO PAG'] = df_PORANUNCIO['ANÚNCIO'].apply(
            lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'LEADS'].sum() /
            df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].sum()
            if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].empty else "Sem conversões"
        )
        st.header('TRÁFEGO POR ANÚNCIO')
        # Filtrar DataFrame pelo valor do slider       
        df_PORANUNCIO = df_PORANUNCIO[df_PORANUNCIO['VALOR USADO'] >= min_valor_usado]
        st.dataframe(df_PORANUNCIO)

    with tabs[1]:
        st.header('Análise de Anúncios')
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
                ax.set_ylabel('Quantidade', color='#FFFFFF')
                ax.set_xlabel(' ', color='#FFFFFF')
                plt.setp(ax.get_xticklabels(), color="#FFFFFF", rotation=45, ha='right')
                plt.setp(ax.get_yticklabels(), color="#FFFFFF")
                
                return fig

        colunas_analise = ['MARGEM', 'VALOR USADO', 'CTR', 'CONVERSAO PAG']
        
        df_PORANUNCIO_COPY = df_PORANUNCIO.copy()
        for coluna in colunas_analise:
            df_PORANUNCIO_COPY[coluna] = pd.to_numeric(df_PORANUNCIO_COPY[coluna], errors='coerce')
        for coluna in colunas_analise:
            df_filtrado = df_PORANUNCIO_COPY[
                (df_PORANUNCIO_COPY[coluna].notnull()) &
                (df_PORANUNCIO_COPY[coluna] != 0) &
                (df_PORANUNCIO_COPY[coluna] != "Sem respostas") &
                (df_PORANUNCIO_COPY[coluna] != "")
            ]
            top_5 = df_filtrado.nlargest(5, coluna)
            bottom_5 = df_filtrado.nsmallest(5, coluna)
            st.subheader(f'Análise da Coluna: {coluna}')
            col1, col2 = st.columns(2)
            with col1:
                if not top_5.empty:
                    fig_top_5 = styled_bar_chart(top_5['ANÚNCIO'], top_5[coluna], f'Top 5 Anúncios - {coluna}')
                    st.pyplot(fig_top_5)
                else:
                    st.write(f"Não há dados suficientes para os Top 5 Anúncios - {coluna}")
            with col2:
                if not bottom_5.empty and len(bottom_5) >= 5:
                    fig_bottom_5 = styled_bar_chart(bottom_5['ANÚNCIO'], bottom_5[coluna], f'Bottom 5 Anúncios - {coluna}')
                    st.pyplot(fig_bottom_5)
                else:
                    st.write(f"Não há dados suficientes para os Bottom 5 Anúncios - {coluna}")

    with tabs[2]:
        st.header('Detalhes do Anúncio')

        selected_anuncio = st.selectbox('Selecione o Anúncio', df_PORANUNCIO['ANÚNCIO'].unique())
        if selected_anuncio:
            anuncio_data = df_PORANUNCIO[df_PORANUNCIO['ANÚNCIO'] == selected_anuncio].iloc[0]

            # Encontrar o link da imagem correspondente no df_SUBIDOS
            drive_link = df_SUBIDOS.loc[df_SUBIDOS['ANUNCIO'] == selected_anuncio, 'LINK DO DRIVE'].values[0]
            image_link = transform_drive_link(drive_link)

            st.write(f"Anúncio: {selected_anuncio}")
            st.write(f"Link da Imagem: [Clique aqui]({image_link})")

            try:
                image = download_image(image_link)
                if image:
                    st.image(image, caption=selected_anuncio, width=300)
            except UnidentifiedImageError:
                st.write("Clique no link para assistir o anúncio de vídeo")

            st.subheader(f"Detalhes do Anúncio: {selected_anuncio}")
            st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: #ffffff;">Informações Gerais</h3>
                <p style="color: #ffffff;"><strong>Total de Leads:</strong> {anuncio_data['TOTAL DE LEADS']}</p>
                <p style="color: #ffffff;"><strong>Total de Pesquisa:</strong> {anuncio_data['TOTAL DE PESQUISA']}</p>
                <p style="color: #ffffff;"><strong>Custo por Lead:</strong> {anuncio_data['CUSTO POR LEAD']:.2f}</p>
                <p style="color: #ffffff;"><strong>Preço Máximo:</strong> {anuncio_data['PREÇO MÁXIMO']:.2f}</p>
                <p style="color: #ffffff;"><strong>Diferença:</strong> {anuncio_data['DIFERENÇA']:.2f}</p>
                <p style="color: #ffffff;"><strong>Margem:</strong> {anuncio_data['MARGEM']:.2%}</p>
                <p style="color: #ffffff;"><strong>Valor Usado:</strong> {anuncio_data['VALOR USADO']:.2f}</p>
                <p style="color: #ffffff;"><strong>CPM:</strong> {anuncio_data['CPM']:.2f}</p>
                <p style="color: #ffffff;"><strong>CTR:</strong> {anuncio_data['CTR']:.2%}</p>
                <p style="color: #ffffff;"><strong>Connect Rate:</strong> {anuncio_data['CONNECT RATE']:.2%}</p>
                <p style="color: #ffffff;"><strong>Conversão da Página:</strong> {anuncio_data['CONVERSAO PAG']:.2%}</p>
                <p style="color: #ffffff;"><strong>Taxa de Resposta:</strong> {anuncio_data['TAXA DE RESPOSTA']:.2%}</p>
            </div>
            """, unsafe_allow_html=True)

            def styled_bar_chart_horizontal(labels, sizes, title):
                fig, ax = plt.subplots()

                # Definindo cores usando colormaps e invertendo a ordem
                cmap = colormaps['RdYlGn']
                norm = mcolors.Normalize(vmin=0, vmax=len(labels)-1)
                colors = [cmap(norm(i)) for i in reversed(range(len(labels)))]

                ax.barh(labels, sizes, color=colors)
                ax.set_facecolor('none')  # Fundo do gráfico transparente
                fig.patch.set_facecolor('none')  # Fundo da figura transparente
                ax.spines['bottom'].set_color('#FFFFFF')
                ax.spines['top'].set_color('#FFFFFF')
                ax.spines['right'].set_color('#FFFFFF')
                ax.spines['left'].set_color('#FFFFFF')
                ax.tick_params(axis='x', colors='#FFFFFF')
                ax.tick_params(axis='y', colors='#FFFFFF')
                ax.set_title(title, color='#FFFFFF')
                ax.set_xlabel('Porcentagem', color='#FFFFFF')
                plt.setp(ax.get_xticklabels(), color="#FFFFFF")
                plt.setp(ax.get_yticklabels(), color="#FFFFFF")
                
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
                ax.set_ylabel('Quantidade', color='#FFFFFF')
                ax.set_xlabel(' ', color='#FFFFFF')
                plt.setp(ax.get_xticklabels(), color="#FFFFFF", rotation=45, ha='right')
                plt.setp(ax.get_yticklabels(), color="#FFFFFF")
                
                return fig

            patrimonio_labels = [
                'Acima de R$1 milhão', 'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
                'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil', 'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil'
            ]
            patrimonio_sizes = [
                anuncio_data['Acima de R$1 milhão'], anuncio_data['Entre R$500 mil e R$1 milhão'],
                anuncio_data['Entre R$250 mil e R$500 mil'], anuncio_data['Entre R$100 mil e R$250 mil'],
                anuncio_data['Entre R$20 mil e R$100 mil'], anuncio_data['Entre R$5 mil e R$20 mil'],
                anuncio_data['Menos de R$5 mil']
            ]
            fig_patrimonio = styled_bar_chart_horizontal(patrimonio_labels, patrimonio_sizes, 'Distribuição de Patrimônio')

            metrics_labels = ['MARGEM', 'CTR', 'CONVERSAO PAG']
            metrics_values = [anuncio_data['MARGEM'], anuncio_data['CTR'], anuncio_data['CONVERSAO PAG']]
            fig_metrics = styled_bar_chart(metrics_labels, metrics_values, 'Métricas Principais')

            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(fig_patrimonio)
            with col2:
                st.pyplot(fig_metrics)
