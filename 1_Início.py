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
st.header("Seja bem-vindo!")
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

    # Inicializar `st.session_state` para `lancamento` e outros valores necessários
    st.session_state.produto = produto
    st.session_state.versao = versao
    st.session_state.lancamento = lancamento
    st.session_state.spreadsheet_central = spreadsheet_central
    
    st.write(f"Lançamento selecionado: {lancamento}")
    st.write(f"Planilha Central: {spreadsheet_central}")

    spreadsheet_captura = lancamento + ' - CENTRAL DO UTM'
    spreadsheet_pesquisa = lancamento + ' - PESQUISA TRAFEGO'
    spreadsheet_copy = lancamento + ' - PESQUISA DE COPY'
    spreadsheet_grupos = lancamento + ' - GRUPOS DE WHATSAPP'

    worksheet_pesquisa = "DADOS"
    worksheet_captura = "CAPTURA"
    worksheet_metaads = "NEW META ADS"
    worksheet_subidos = "ANUNCIOS SUBIDOS"
    worksheet_prematricula = "PRE-MATRICULA"
    worksheet_vendas = "VENDAS"
    worksheet_copy = 'pesquisa-copy-' + lancamento.replace('.', '')
    worksheet_grupos = 'SENDFLOW - ATIVIDADE EXPORT'

    # Definindo as variáveis para as datas dos lançamentos

    # Criar um container para as mensagens de status
    status_container = st.empty()

    # Criar um contador para o progresso
    progress = st.progress(0)
    total_steps = 7  # número de planilhas para carregar

    try:
        with st.spinner("Carregando planilha de pesquisa tráfego..."):
            df_PESQUISA = load_sheet(spreadsheet_pesquisa, worksheet_pesquisa)
            st.session_state.df_PESQUISA = df_PESQUISA
        status_container.text("Planilha de pesquisa tráfego carregada com sucesso!")
        progress.progress(int((1 / total_steps) * 100))

        with st.spinner("Carregando planilha de Meta Ads..."):
            df_METAADS = load_sheet(spreadsheet_pesquisa, worksheet_metaads)
            st.session_state.df_METAADS = df_METAADS
        status_container.text("Planilha de Meta Ads carregada com sucesso!")
        progress.progress(int((2 / total_steps) * 100))

        with st.spinner("Carregando planilha de Anúncios Subidos..."):
            df_SUBIDOS = load_sheet(spreadsheet_pesquisa, worksheet_subidos)
            st.session_state.df_SUBIDOS = df_SUBIDOS
        status_container.text("Planilha de Anúncios Subidos carregada com sucesso!")
        progress.progress(int((3 / total_steps) * 100))

        with st.spinner("Carregando planilhas da central do UTM..."):
            df_CAPTURA = load_sheet(spreadsheet_captura, worksheet_captura)
            st.session_state.df_CAPTURA = df_CAPTURA
        status_container.text("Planilha de Captura carregada com sucesso!")
        progress.progress(int((4 / total_steps) * 100))

        with st.spinner("Carregando planilha de Pré-Matrícula..."):
            df_PREMATRICULA = load_sheet(spreadsheet_captura, worksheet_prematricula)
            st.session_state.df_PREMATRICULA = df_PREMATRICULA
        status_container.text("Planilha de Pré-Matrícula carregada com sucesso!")
        progress.progress(int((5 / total_steps) * 100))

        with st.spinner("Carregando planilha de Vendas..."):
            df_VENDAS = load_sheet(spreadsheet_captura, worksheet_vendas)
            st.session_state.df_VENDAS = df_VENDAS
        status_container.text("Planilha de Vendas carregada com sucesso!")
        progress.progress(int((6 / total_steps) * 100))

        try:
            with st.spinner("Carregando planilha de Copy..."):
                df_COPY = load_sheet(spreadsheet_copy, worksheet_copy)
                df_COPY = df_COPY.astype(str).fillna('semdados')
                st.session_state.df_COPY = df_COPY
            status_container.text("Planilha de Copy carregada com sucesso!")
            progress.progress(int((7 / total_steps) * 100))

            try:
                with st.spinner("Carregando planilha de Grupos..."):
                    df_GRUPOS = load_sheet(spreadsheet_grupos, worksheet_grupos)
                    if not df_GRUPOS.empty:
                        st.session_state.df_GRUPOS = df_GRUPOS
                        st.session_state.sheets_loaded = True
                    status_container.text("Planilha de Grupos carregada com sucesso!")
                    progress.progress(100)

                # Iniciar Aplicativo
                if st.button("Iniciar Aplicativo"):
                    st.rerun()

            except Exception as e:
                status_container.text(f"Erro ao carregar a planilha de Grupos: {e}")

        except Exception as e:
            status_container.text(f"Erro ao carregar a planilha de Copy: {e}")

    except Exception as e:
        status_container.text(f"Erro ao carregar a planilha de pesquisa de tráfego: {e}")
