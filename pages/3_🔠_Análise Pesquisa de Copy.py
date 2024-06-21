import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from urllib.parse import unquote_plus
import nltk
nltk.download('rslp')
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
    bigrams = list(nltk.bigrams(tokens))

    # Contagem dos bigramas
    contagem_bigramas = Counter(bigrams)

    # Criando DataFrame com os dados ranqueados
    df_rankeado = pd.DataFrame(contagem_bigramas.items(), columns=['Bigrama', 'Frequência'])

    # Ordenando o DataFrame pelo número de ocorrências em ordem decrescente
    df_rankeado = df_rankeado.sort_values(by='Frequência', ascending=False).reset_index(drop=True)

    return df_rankeado

# Função para calcular a conversão dos bigramas, mantendo a ordem dos bigramas nas vendas
def calcular_conversao(df_vendas, df_pesquisa, coluna_vendas, coluna_pesquisa):
    # Processar bigramas nas vendas
    bigramas_vendas = processar_coluna_bigramas(df_vendas[coluna_vendas])
    
    # Processar bigramas na pesquisa
    bigramas_pesquisa = processar_coluna_bigramas(df_pesquisa[coluna_pesquisa])
    
    # Criar um DataFrame para armazenar a conversão, mantendo a ordem das vendas
    conversao = []
    
    for bigrama, freq_vendas in zip(bigramas_vendas['Bigrama'], bigramas_vendas['Frequência']):
        # Verificar se o bigrama está na pesquisa
        freq_pesquisa = bigramas_pesquisa[bigramas_pesquisa['Bigrama'] == bigrama]['Frequência'].values
        if len(freq_pesquisa) > 0:
            taxa_conversao = freq_vendas / freq_pesquisa[0]
        else:
            taxa_conversao = 0
        conversao.append((bigrama, freq_vendas, freq_pesquisa[0] if len(freq_pesquisa) > 0 else 0, taxa_conversao))
    
    # Criar DataFrame da conversão, mantendo a ordem das vendas
    df_conversao = pd.DataFrame(conversao, columns=['Bigrama', 'Freq Vendas', 'Freq Pesquisa', 'Conversão'])
    
    return df_conversao

# Função para aplicar o filtro no DataFrame de conversão
def aplicar_filtro(df_conversao, min_freq_vendas, min_freq_pesquisa):
    df_filtrado = df_conversao[(df_conversao['Freq Vendas'] >= min_freq_vendas) & (df_conversao['Freq Pesquisa'] >= min_freq_pesquisa)]
    return df_filtrado

# Perguntar qual lançamento a pessoa gostaria de analisar
st.write('Qual Lançamento você quer analisar?')

# Dropdown para selecionar o produto
produto = st.selectbox('Produto', ['EI', 'SC'])

# Dropdown para selecionar a versão
versao = st.selectbox('Versão', list(range(1, 31)))

# Botão para continuar para a análise
if st.button("Continuar para Análise") or 'df_VENDAS2' in st.session_state:

    if 'df_VENDAS2' not in st.session_state:
        # Formatar os inputs do usuário
        lancamento2 = f"{produto}.{str(versao).zfill(2)}"
        spreadsheet_central = lancamento2 + ' - CENTRAL DO UTM'
        spreadsheet_pesquisa_copy = lancamento2 + ' - PESQUISA COPY'

        st.write(f"Lançamento selecionado: {lancamento2}")
        st.write(f"Planilha Central: {spreadsheet_central}")
        st.write(f"Planilha Pesquisa Copy: {spreadsheet_pesquisa_copy}")

        try:
            # Carregando Planilha de Vendas Central do UTM
            df_VENDAS2 = load_sheet(spreadsheet_central, 'VENDAS')
            st.session_state.df_VENDAS2 = df_VENDAS2
        except Exception as e:
            st.error(f"Erro ao carregar a planilha de vendas: {e}")

        try:
            # Carregando Planilha de Pesquisa de Copy
            SPREADSHEETCOPY = lancamento2 + ' - PESQUISA DE COPY'
            WORKSHEETCOPY = 'pesquisa-copy-' + lancamento2.replace('.','')

            df_PESQUISA2 = load_sheet(SPREADSHEETCOPY, WORKSHEETCOPY)
            df_PESQUISA2 = df_PESQUISA2.astype(str)
            df_PESQUISA2 = df_PESQUISA2.fillna('semdados')
            st.session_state.df_PESQUISA2 = df_PESQUISA2
        except Exception as e:
            st.error(f"Erro ao carregar a planilha de Copy {e}")
    else:
        df_VENDAS2 = st.session_state.df_VENDAS2
        df_PESQUISA2 = st.session_state.df_PESQUISA2

    # Adicionar controles deslizantes para o usuário definir os filtros
    min_freq_vendas = st.slider("Quantidade mínima de alunos", min_value=0, max_value=int(df_VENDAS2['COPY MAIOR MOTIVACAO'].count()), value=1)
    min_freq_pesquisa = st.slider("Quantidade mínima de respostas na pesquisa", min_value=0, max_value=int(df_PESQUISA2['Qual é a sua maior motivação? O que te faz levantar da cama todos os dias?'].count()), value=1)

    st.write("Análise de Bigramas - Pesquisa de Copy Lançamento")

    # Palavras a serem excluídas
    excecoes = ['ter', 'pra', 'wlandsmidt', 'milazzo']

    # Tabela de conversão para cada pergunta
    st.write("Tabelas de Conversão")

    # Maior Motivação
    df_conversao_maior_motivacao = calcular_conversao(df_VENDAS2, df_PESQUISA2, 'COPY MAIOR MOTIVACAO', 'Qual é a sua maior motivação? O que te faz levantar da cama todos os dias?')
    df_conversao_maior_motivacao_filtrado = aplicar_filtro(df_conversao_maior_motivacao, min_freq_vendas, min_freq_pesquisa)
    st.write("Conversão - Maior Motivação")
    st.dataframe(df_conversao_maior_motivacao_filtrado)

    # Defina Sucesso
    df_conversao_defina_sucesso = calcular_conversao(df_VENDAS2, df_PESQUISA2, 'COPY DEFINA SUCESSO', 'O que precisa acontecer para você acreditar que é uma pessoa bem-sucedida?')
    df_conversao_defina_sucesso_filtrado = aplicar_filtro(df_conversao_defina_sucesso, min_freq_vendas, min_freq_pesquisa)
    st.write("Conversão - Defina Sucesso")
    st.dataframe(df_conversao_defina_sucesso_filtrado)

    # Maior Dificuldade
    df_conversao_maior_dificuldade = calcular_conversao(df_VENDAS2, df_PESQUISA2, 'COPY MAIOR DIFICULDADE', 'Qual é a sua maior dificuldade em relação aos investimentos e/ou finanças?')
    df_conversao_maior_dificuldade_filtrado = aplicar_filtro(df_conversao_maior_dificuldade, min_freq_vendas, min_freq_pesquisa)
    st.write("Conversão - Maior Dificuldade")
    st.dataframe(df_conversao_maior_dificuldade_filtrado)

    # Porque Investir
    df_conversao_porque_investir = calcular_conversao(df_VENDAS2, df_PESQUISA2, 'COPY PORQUE INVESTIR', 'Por que você quer aprender a investir?')
    df_conversao_porque_investir_filtrado = aplicar_filtro(df_conversao_porque_investir, min_freq_vendas, min_freq_pesquisa)
    st.write("Conversão - Porque Investir")
    st.dataframe(df_conversao_porque_investir_filtrado)

    # Expectativa CPL
    df_conversao_expectativa_cpl = calcular_conversao(df_VENDAS2, df_PESQUISA2, 'COPY EXPECTATIVA CPL', 'O que precisa acontecer na Semana do Investidor Iniciante pra você dizer que "valeu a pena"?')
    df_conversao_expectativa_cpl_filtrado = aplicar_filtro(df_conversao_expectativa_cpl, min_freq_vendas, min_freq_pesquisa)
    st.write("Conversão - Expectativa CPL")
    st.dataframe(df_conversao_expectativa_cpl_filtrado)
