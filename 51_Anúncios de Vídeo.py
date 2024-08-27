import os
import streamlit as st
import requests
import io
from tempfile import NamedTemporaryFile
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import gspread
import moviepy.editor as mp
import matplotlib.pyplot as plt
from pydub import AudioSegment
import speech_recognition as sr
import time
import tempfile
import openai


openai.api_key = 'sk-riani-ZC3qM6m7FffUF15VLda0T3BlbkFJ4paSvTriCSNbUGvPccmC'

# Função para transformar link de compartilhamento do Google Drive em link direto para download
def transform_drive_link(link):
    if "drive.google.com" in link and "file/d/" in link:
        file_id = link.split("file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    elif "drive.google.com" in link and "id=" in link:
        file_id = link.split("id=")[1].split("&")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    else:
        return link

# Função para baixar o vídeo do Google Drive
def download_video(video_url, output_path):
    try:
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return output_path
        else:
            st.error("Erro ao baixar o vídeo. Verifique o link e tente novamente.")
            return None
    except Exception as e:
        st.error(f"Erro ao baixar o vídeo: {e}")
        return None

# Função para extrair áudio do vídeo
def extract_audio(video_path):
    try:
        video = mp.VideoFileClip(video_path)
        temp_audio = NamedTemporaryFile(delete=False, suffix=".wav")
        video.audio.write_audiofile(temp_audio.name)
        st.write(f"Áudio extraído para: {temp_audio.name}")
        return temp_audio.name
    except Exception as e:
        st.error(f"Erro ao extrair áudio: {e}")
        return None

# Função para transcrever áudio usando SpeechRecognition
def transcribe_audio_speech_recognition(audio_path):
    try:
        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(audio_path)
        with audio_file as source:
            audio_data = recognizer.record(source)
        transcript = recognizer.recognize_google(audio_data, language="pt-BR")
        return transcript
    except Exception as e:
        st.error(f"Erro ao transcrever áudio: {e}")
        return None

# Função para carregar uma aba específica de uma planilha
#@st.cache


# Interface principal com abas
st.title("Análise de Desempenho de Anúncios em Vídeo")

# Criar as abas
tab1, tab2, tab3 = st.tabs(["Dados", "Análise", "Hook analyzer"])

# Aba Dados
with tab1:   
    # Slider para selecionar o valor mínimo de 'VALOR USADO'
    min_valor_usado = st.slider("Selecione o valor mínimo de 'VALOR USADO'", 0, 1000, 250)
  
    df_METAADS = st.session_state.df_METAADS.copy()
        
    # Converter colunas de retenção para numéricas
    colunas_retenção = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15-20', '20-25', '25-30', '30-40', '40-50', '50-60', '60+']
    for coluna in colunas_retenção:
        df_METAADS[coluna] = pd.to_numeric(df_METAADS[coluna], errors='coerce')
    
    # Converter coluna 'VALOR USADO' para numérico
    df_METAADS['VALOR USADO'] = pd.to_numeric(df_METAADS['VALOR USADO'], errors='coerce')
    
    # Filtrar anúncios de vídeo (não vazios nas colunas de tempo)
    df_videos = df_METAADS.dropna(subset=colunas_retenção, how='all')
    
    st.write("Total de anúncios de vídeo antes de agrupar:", len(df_videos))

    # Agrupar por 'ANUNCIO: NOME' e calcular a média das retenções e somar 'VALOR USADO'
    df_agrupado = df_videos.groupby('ANUNCIO: NOME').agg(
        {**{col: 'mean' for col in colunas_retenção}, 'VALOR USADO': 'sum'}
    ).reset_index()
    
    st.write("Total de anúncios agrupados antes do filtro:", len(df_agrupado))

    # Filtrar anúncios com 'VALOR USADO' maior ou igual ao valor mínimo selecionado
    df_filtrado = df_agrupado[df_agrupado['VALOR USADO'] >= min_valor_usado].reset_index(drop=True)
    
    st.write("Total de anúncios após aplicar o filtro de valor gasto:", len(df_filtrado))

    # Exibir o DataFrame resultante
    st.write("Média de Retenção por Anúncio de Vídeo")
    st.dataframe(df_filtrado)
    st.write(f"Total de anúncios exibidos: {len(df_filtrado)}")

# Aba Análise
with tab2:
    
    if 'df_filtrado' in locals():
        # Carregar os dados da aba 'ANUNCIOS SUBIDOS'
        df_SUBIDOS = st.session_state.df_SUBIDOS.copy()

        # Selectbox para selecionar anúncios
        st.write("Selecione até 3 anúncios para comparar:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            anuncio1 = st.selectbox("Anúncio 1", df_filtrado['ANUNCIO: NOME'].unique(), key='anuncio1')
            link1 = df_SUBIDOS.loc[df_SUBIDOS['ANUNCIO'] == anuncio1, 'LINK DO DRIVE'].values[0]
            st.write(f"Link: [{link1}]({link1})")

        with col2:
            anuncio2 = st.selectbox("Anúncio 2", [None] + list(df_filtrado['ANUNCIO: NOME'].unique()), key='anuncio2')
            if anuncio2:
                link2 = df_SUBIDOS.loc[df_SUBIDOS['ANUNCIO'] == anuncio2, 'LINK DO DRIVE'].values[0]
                st.write(f"Link: [{link2}]({link2})")
                
        with col3:
            anuncio3 = st.selectbox("Anúncio 3", [None] + list(df_filtrado['ANUNCIO: NOME'].unique()), key='anuncio3')
            if anuncio3:
                link3 = df_SUBIDOS.loc[df_SUBIDOS['ANUNCIO'] == anuncio3, 'LINK DO DRIVE'].values[0]
                st.write(f"Link: [{link3}]({link3})")
                
        if st.button("Gerar Análise"):
            # Criar um novo DataFrame com uma linha chamada 'média'
            df_media = df_filtrado[colunas_retenção].mean().to_frame().T
            df_media.index = ['média']
            
            # Obter dados dos anúncios selecionados
            df_selecionados = df_filtrado[df_filtrado['ANUNCIO: NOME'].isin([anuncio1, anuncio2, anuncio3])]

            # Preparar o gráfico de linhas estilizado
            fig, ax = plt.subplots(figsize=(12, 7))  # Aumentar levemente o tamanho da figura
            
            # Plotar os anúncios selecionados
            cores = ['#FFA500', '#32CD32', '#1E90FF']  # Cores levemente mais claras: laranja, verde e azul
            for i, anuncio in enumerate([anuncio1, anuncio2, anuncio3]):
                if anuncio:
                    ax.plot(colunas_retenção, df_selecionados[df_selecionados['ANUNCIO: NOME'] == anuncio].iloc[0, 1:-1], label=anuncio, color=cores[i])
            
            # Plotar a linha da média
            ax.plot(colunas_retenção, df_media.iloc[0], label='média', color='#FF6347')  # Vermelho claro
            
            # Configurações do gráfico
            ax.set_xlabel('Tempo de Retenção', color='white')
            ax.set_ylabel('Percentual de Retenção', color='white')
            ax.set_title('Comparação de Retenção dos Anúncios', color='white')
            ax.legend()
            ax.grid(True, color='#666666', linestyle='--', linewidth=0.5)
            ax.patch.set_alpha(0)  # Fundo do gráfico transparente
            fig.patch.set_alpha(0)  # Fundo da figura transparente
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white') 
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.tick_params(axis='x', colors='white', rotation=45)  # Rotacionar labels de tempo
            ax.tick_params(axis='y', colors='white')

            # Mostrar o gráfico
            st.pyplot(fig)


# Aba Hook analyzer
with tab3:
    st.write("Análise de Hook de Vídeos")

    # Garantir que os dados estejam carregados na aba "Dados"
    if 'df_filtrado' in locals() and df_filtrado is not None:
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
                top_anuncios = df_filtrado.nlargest(top_n, col_retenção)
            else:
                top_anuncios = df_filtrado.nsmallest(top_n, col_retenção)
            
            # Mostrar o dataframe dos top anúncios
            st.write(f"Top {top_n} anúncios de acordo com a retenção no segundo {segundo}:")
            st.dataframe(top_anuncios)

            # Carregar os dados da aba 'ANUNCIOS SUBIDOS'
            df_SUBIDOS = st.session_state.df_SUBIDOS.copy()

            progress_text = st.empty()
            progress_bar = st.progress(0)

            transcriptions = []

            with st.expander("Detalhes do processo de extração e transcrição", expanded=False):
                for index, anuncio in enumerate(top_anuncios['ANUNCIO: NOME'], start=1):
                    progress_text.text(f"Extraindo transcrição {index}/{len(top_anuncios)}...")
                    progress_bar.progress(index / len(top_anuncios))

                    # Encontrar o link do vídeo no Google Drive
                    drive_link = df_SUBIDOS.loc[df_SUBIDOS['ANUNCIO'] == anuncio, 'LINK DO DRIVE'].values[0]
                    direct_link = transform_drive_link(drive_link)

                    with st.spinner(f"Baixando e transcrevendo o vídeo do anúncio: {anuncio}..."):
                        try:
                            # Usar um diretório temporário para armazenar os arquivos
                            with tempfile.TemporaryDirectory() as tmpdirname:
                                video_path = os.path.join(tmpdirname, f"{anuncio}.mp4")
                                
                                # Baixar vídeo
                                video_path = download_video(direct_link, video_path)
                                if video_path:
                                    # Extrair áudio
                                    audio_path = extract_audio(video_path)
                                    
                                    if audio_path:  # Verifique se o áudio foi extraído com sucesso
                                        # Adicione verificação de existência do arquivo
                                        if os.path.isfile(audio_path):
                                            st.write(f"Arquivo de áudio encontrado: {audio_path}")
                                            # Transcrever áudio
                                            transcript = transcribe_audio_speech_recognition(audio_path)
                                            
                                            if transcript:  # Verifique se a transcrição foi bem-sucedida
                                                # Obter a retenção no segundo escolhido
                                                retencao_segundo = top_anuncios.loc[top_anuncios['ANUNCIO: NOME'] == anuncio, col_retenção].values[0]
                                                # Adicionar ao bloco de transcrições
                                                transcriptions.append({
                                                    'anuncio': anuncio,
                                                    'retencao_segundo': retencao_segundo,
                                                    'transcript': transcript
                                                })
                                        else:
                                            st.error(f"Arquivo de áudio não encontrado: {audio_path}")
                                    else:
                                        st.error(f"Erro ao extrair áudio do anúncio: {anuncio}")
                        except Exception as e:
                            if "WinError 32" not in str(e):
                                st.error(f"Erro durante o processo de download e transcrição: {e}")
                            else:
                                st.warning(f"Erro durante o processo de download e transcrição: O arquivo já está sendo usado por outro processo. Ignorando...")

                progress_text.text("Processo de extração e transcrição concluído!")
                progress_bar.empty()

            # Exibir as transcrições
            st.markdown("## Transcrições dos Vídeos")
            for i, item in enumerate(transcriptions, start=1):
                st.markdown(f"""
                ### VÍDEO {i}: {item['anuncio']}
                **Retenção aos {segundo} segundos:** <span style='font-size: 1.2em;'>{item['retencao_segundo']}%</span>
                <br><br>
                **Transcrição do Vídeo:**
                <pre style="white-space: pre-wrap; word-wrap: break-word;">{item['transcript']}</pre>
                """, unsafe_allow_html=True)
    else:
        st.write("Por favor, carregue os dados na aba 'Dados' primeiro.")
