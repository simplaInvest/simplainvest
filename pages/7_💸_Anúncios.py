import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import matplotlib.cm as cm

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

# Perguntar qual lançamento a pessoa gostaria de analisar
st.write('Qual o Lançamento em Questão?')

# Dropdown para selecionar o produto
produto = st.selectbox('Produto', ['EI', 'SC'])

# Dropdown para selecionar a versão
versao = st.selectbox('Versão', list(range(1, 31)))

# Botão para continuar para a análise
if st.button("Continuar para Análise"):
    # Formatar os inputs do usuário
    lancamentoT = f"{produto}.{str(versao).zfill(2)}"   
    #spreadsheet_pesquisa_copy = lancamento1 + ' - PESQUISA COPY'
    spreadsheet_trafego = lancamentoT + ' - PESQUISA TRAFEGO'
    st.write(f"Lançamento selecionado: {lancamentoT}")
    st.write(f"Planilha Central: {spreadsheet_trafego}")
    
    try:
        # Carregar dados da New Meta Ads
        df_METAADS = load_sheet(spreadsheet_trafego, 'NEW META ADs')
        st.success("NEW META ADs carregadas com sucesso!")
    
        try:
            # Carregar dados de Anúncios Subidos
            df_SUBIDOS = load_sheet(spreadsheet_trafego, 'ANUNCIOS SUBIDOS')
            st.success("Anúncios Subidos carregado com sucesso!")

            try:
                # Carregar dados de pesquisa
                df_PESQUISA = load_sheet(spreadsheet_trafego, 'DADOS')
                st.success("Dados carregado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao carregar a planilha de pesquisa: {e}")

        except Exception as e:
            st.error(f"Erro ao carregar a planilha de Anúncios Subidos: {e}")

    except Exception as e:
        st.error(f"Erro ao carregar a planilha de New Meta Ads: {e}")

   



