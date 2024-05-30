import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from urllib.parse import unquote_plus
import nltk

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from string import punctuation
from collections import Counter

    # Função para carregar uma aba específica de uma planilha
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

# Input para o nome da planilha de captura
import streamlit as st

# Perguntar qual lançamento a pessoa gostaria de analisar
st.write('Qual Lançamento você quer analisar?')

# Dropdown para selecionar o produto
produto = st.selectbox('Produto', ['EI', 'SC'])

# Dropdown para selecionar a versão
versao = st.selectbox('Versão', list(range(1, 31)))

# Botão para continuar para a análise
if st.button("Continuar para Análise"):

    # Formatar os inputs do usuário
    lancamento2 = f"{produto}.{str(versao).zfill(2)}"
    spreadsheet_central = lancamento2 + ' - CENTRAL DO UTM'
    spreadsheet_pesquisa_copy = lancamento2 + ' - PESQUISA COPY'

    st.write(f"Lançamento selecionado: {lancamento2}")
    st.write(f"Planilha Central: {spreadsheet_central}")
    st.write(f"Planilha Pesquisa Copy: {spreadsheet_pesquisa_copy}")

    spreadsheet_central = lancamento2 + ' - CENTRAL DO UTM'
    spreadsheet_pesquisa_copy = lancamento2 + ' - PESQUISA COPY'

    if lancamento2:
        try:
            # Carregando Planilha de Vendas Central do UTM
            df_VENDAS2 = load_sheet(spreadsheet_central, 'VENDAS')
            #st.dataframe(df_VENDAS2)
        except Exception as e:
            st.error(f"Erro ao carregar a planilha de vendas: {e}")
        
        try:
            # Carregando Planilha de Pesquisa de Copy
            SPREADSHEETCOPY = lancamento2 + ' - PESQUISA DE COPY'
            WORKSHEETCOPY = 'pesquisa-copy-' + lancamento2.replace('.','')

            df_PESQUISA2 = load_sheet(SPREADSHEETCOPY, WORKSHEETCOPY)
            df_PESQUISA2 = df_PESQUISA2.astype(str)
            df_PESQUISA2 = df_PESQUISA2.fillna('semdados')
            #st.dataframe(df_PESQUISA2)

        except Exception as e:
            st.error(f"Erro ao carregar a planilha de Copy {e}")

        try:
            st.write("Análise de Bigramas - Pesquisa de Copy Lançamento")

            # Função para processar e ranquear os bigramas
            def processar_coluna_bigramas(respostas_coluna, excecoes=[]):
                # Criando lista de stopwords em português
                nltk.download('punkt')
                nltk.download('stopwords')
                stop_words = set(stopwords.words('portuguese'))
                stop_words.update(set(punctuation))

                # Adicionando exceções à lista de stopwords
                for excecao in excecoes:
                    stop_words.discard(excecao)

                # Criando o stemmer
                stemmer = RSLPStemmer()

                # Juntando todas as respostas em uma única string
                text = " ".join(respostas_coluna)

                # Tokenização das palavras com filtragem das stopwords e pontuações, e aplicação do stemming
                tokens = [stemmer.stem(word.lower()) for word in word_tokenize(text) if word.lower() not in stop_words and word.isalpha() and word.lower() not in excecoes]

                # Gerando bigramas
                bigrams = [(min(token1, token2), max(token1, token2)) for token1, token2 in nltk.ngrams(tokens, 2)]

                # Contagem dos bigramas
                contagem_bigramas = Counter(bigrams)

                # Criando DataFrame com os dados ranqueados
                df_rankeado = pd.DataFrame(contagem_bigramas.items(), columns=['Bigrama', 'Frequência'])

                # Ordenando o DataFrame pelo número de ocorrências em ordem decrescente
                df_rankeado = df_rankeado.sort_values(by='Frequência', ascending=False).reset_index(drop=True)

                return df_rankeado

            # Palavras a serem excluídas
            excecoes = ['ter', 'pra', 'rufino', 'wlandsmidt', 'milazzo']

            st.title('VENDAS')
            st.text('Bigramas recorrentes em diferentes categorias')

            # Criando colunas para exibir os dataframes
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.text('Maior Motivação')
                df_maior_motivacao = processar_coluna_bigramas(df_VENDAS2['COPY MAIOR MOTIVAÇÃO'], excecoes)
                st.dataframe(df_maior_motivacao)

            with col2:
                st.text('Defina Sucesso')
                df_defina_sucesso = processar_coluna_bigramas(df_VENDAS2['COPY DEFINA SUCESSO'], excecoes)
                st.dataframe(df_defina_sucesso)

            with col3:
                st.text('Maior Dificuldade')
                df_maior_dificuldade = processar_coluna_bigramas(df_VENDAS2['COPY MAIOR DIFICULDADE'], excecoes)
                st.dataframe(df_maior_dificuldade)

            with col4:
                st.text('Porque Investir')
                df_porque_investir = processar_coluna_bigramas(df_VENDAS2['COPY PORQUE INVESTIR'], excecoes)
                st.dataframe(df_porque_investir)

            with col5:
                st.text('Expectativa CPL')
                df_expectativa_cpl = processar_coluna_bigramas(df_VENDAS2['COPY EXPECTATIVA CPL'], excecoes)
                st.dataframe(df_expectativa_cpl)

            st.title('PESQUISA')
            st.text('Bigramas recorrentes em diferentes categorias')

            # Criando colunas para exibir os dataframes
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.text('Maior Motivação')
                df_maior_motivacao = processar_coluna_bigramas(df_PESQUISA2['Qual é a sua maior motivação? O que te faz levantar da cama todos os dias?'], excecoes)
                st.dataframe(df_maior_motivacao)

            with col2:
                st.text('Defina Sucesso')
                df_defina_sucesso = processar_coluna_bigramas(df_PESQUISA2['O que precisa acontecer para você acreditar que é uma pessoa bem-sucedida?'], excecoes)
                st.dataframe(df_defina_sucesso)

            with col3:
                st.text('Maior Dificuldade')
                df_maior_dificuldade = processar_coluna_bigramas(df_PESQUISA2['Qual é a sua maior dificuldade em relação aos investimentos e/ou finanças?'], excecoes)
                st.dataframe(df_maior_dificuldade)

            with col4:
                st.text('Porque Investir')
                df_porque_investir = processar_coluna_bigramas(df_PESQUISA2['Por que você quer aprender a investir?'], excecoes)
                st.dataframe(df_porque_investir)

            with col5:
                st.text('Expectativa CPL')
                df_expectativa_cpl = processar_coluna_bigramas(df_PESQUISA2['O que precisa acontecer na Semana do Investidor Iniciante pra você dizer que "valeu a pena"?'], excecoes)
                st.dataframe(df_expectativa_cpl)

        except Exception as e:
            st.error(f"Erro no código dos bigramas {e}")