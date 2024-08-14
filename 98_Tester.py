# main_script.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sheet_loader import load_sheet


# Estilização das abas
st.markdown(
    """
    <style>
    .css-1n543e5 {  /* class for tab buttons */
        border-radius: 8px !important;
        margin-right: 8px !important;
    }
    .css-1n543e5:hover {  /* class for tab buttons on hover */
        background-color: #f0f0f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Perguntar qual lançamento a pessoa gostaria de analisar
st.write('Qual Lançamento você quer analisar?')

# Dropdown para selecionar o produto
produto = st.selectbox('Produto', ['EI', 'SC'])

# Dropdown para selecionar a versão
versao = st.selectbox('Versão', list(range(1, 31)))

# Botão para continuar para a análise
if st.button("Continuar para Análise"):
    # Formatar os inputs do usuário
    lancamento = f"{produto}.{str(versao).zfill(2)}"
    spreadsheet_central = lancamento + ' - CENTRAL DO UTM'
    
    st.write(f"Lançamento selecionado: {lancamento}")
    st.write(f"Planilha Central: {spreadsheet_central}")

    spreadsheet_captura = lancamento + ' - CENTRAL DO UTM'
    spreadsheet_pesquisa = lancamento + ' - PESQUISA TRAFEGO'
    spreadsheet_copy = lancamento + ' - PESQUISA DE COPY'
                
    worksheet_pesquisa = "DADOS"
    worksheet_captura = "CAPTURA"
    worksheet_prematricula="PRE-MATRICULA"
    worksheet_vendas="VENDAS"
    worksheet_copy = 'pesquisa-copy-' + lancamento.replace('.','')
        
    try:
        # Carregar dados da planilha de pesquisa
        df_PESQUISA = load_sheet(spreadsheet_pesquisa, worksheet_pesquisa)
        st.success("Planilha de pesquisa tráfego carregada com sucesso!")

        try:
            df_CAPTURA = load_sheet(spreadsheet_captura, worksheet_captura)
            st.success("Planilha de captura carregada com sucesso!")
            df_PREMATRICULA = load_sheet(spreadsheet_captura, worksheet_prematricula)
            st.success("Planilha de prematricula carregada com sucesso!")
            df_VENDAS = load_sheet(spreadsheet_captura, worksheet_vendas)
            st.success("Planilha de vendas carregada com sucesso!")

            try:          
                df_COPY = load_sheet(spreadsheet_copy, worksheet_copy)
                df_COPY = df_COPY.astype(str)
                df_COPY = df_COPY.fillna('semdados')
                st.session_state.df_COPY = df_PESQUISA
                st.success("Planilha de pesquisa COPY com sucesso!")
            except Exception as e:
                st.error(f"Erro ao carregar a planilha de Copy {e}")


        except Exception as e:
            st.error(f"Erro ao carregar as planilhas da central do UTM: {e}")
    
    except Exception as e:
        st.error(f"Erro ao carregar a planilha de pesquisa de tráfego: {e}") 

            



    