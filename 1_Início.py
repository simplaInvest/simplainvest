# main_script.py
import streamlit as st
import pandas as pd
import numpy as np
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
st.title("Central de Lançamentos Simpla Club")
st.header("Seja bem vindo!")
st.divider()
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
    spreadsheet_grupos = lancamento + ' - GRUPOS DE WHATSAPP'
                
    worksheet_pesquisa = "DADOS"
    worksheet_captura = "CAPTURA"
    worksheet_metaads="NEW META ADS"
    worksheet_subidos="ANUNCIOS SUBIDOS"
    worksheet_prematricula="PRE-MATRICULA"
    worksheet_vendas="VENDAS"
    worksheet_copy = 'pesquisa-copy-' + lancamento.replace('.','')
    worksheet_grupos = 'SENDFLOW - ATIVIDADE EXPORT'
        
    try:
        # Carregar dados da planilha de pesquisa
        df_PESQUISA = load_sheet(spreadsheet_pesquisa, worksheet_pesquisa)
        st.session_state.df_PESQUISA = df_PESQUISA
        st.success("Planilha de pesquisa tráfego carregada com sucesso!")
        df_METAADS = load_sheet(spreadsheet_pesquisa, worksheet_metaads)
        st.session_state.df_METAADS = df_METAADS
        st.success("Planilha de meta ads carregada com sucesso!")
        df_SUBIDOS = load_sheet(spreadsheet_pesquisa, worksheet_subidos)
        st.session_state.df_SUBIDOS = df_SUBIDOS
        st.success("Planilha de subidos carregada com sucesso!")


        try:
            df_CAPTURA = load_sheet(spreadsheet_captura, worksheet_captura)
            # Converter a coluna para datetime, lidando com diferentes formatos
            df_CAPTURA['CAP DATA_CAPTURA'] = pd.to_datetime(df_CAPTURA['CAP DATA_CAPTURA'], format='ISO8601', errors='coerce')
            # Depois formatar para 'DD/MM/YYYY'
            #df_CAPTURA['CAP DATA_CAPTURA'] = df_CAPTURA['CAP DATA_CAPTURA'].dt.strftime('%d/%m/%Y às -%H:%M')
       
            st.session_state.df_CAPTURA = df_CAPTURA
            st.success("Planilha de captura carregada com sucesso!")
            df_PREMATRICULA = load_sheet(spreadsheet_captura, worksheet_prematricula)
            st.session_state.df_PREMATRICULA = df_PREMATRICULA
            st.success("Planilha de prematricula carregada com sucesso!")
            df_VENDAS = load_sheet(spreadsheet_captura, worksheet_vendas)
            st.session_state.df_VENDAS = df_VENDAS
            st.success("Planilha de vendas carregada com sucesso!")

            try:          
                df_COPY = load_sheet(spreadsheet_copy, worksheet_copy)
                df_COPY = df_COPY.astype(str)
                df_COPY = df_COPY.fillna('semdados')
                st.session_state.df_COPY = df_COPY
                st.success("Planilha de pesquisa COPY com sucesso!")
                
                st.session_state.lancamento = lancamento
                
                try:
                    df_GRUPOS = load_sheet(spreadsheet_grupos, worksheet_grupos)
                    st.session_state.df_GRUPOS = df_GRUPOS
                    st.session_state.sheets_loaded = True
                    #df_GRUPOS['Evento'] = pd.to_datetime(df_GRUPOS['Evento'], format='ISO8601', errors='coerce')
                    st.success("Planilha GRUPOS com sucesso!")
                                       
                    if st.button("Iniciar Aplicativo"):
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Erro ao carregar a planilha de grupos {e}")
                       
            except Exception as e:
                st.error(f"Erro ao carregar a planilha de Copy {e}")


        except Exception as e:
            st.error(f"Erro ao carregar as planilhas da central do UTM: {e}")
    
    except Exception as e:
        st.error(f"Erro ao carregar a planilha de pesquisa de tráfego: {e}") 

            


    