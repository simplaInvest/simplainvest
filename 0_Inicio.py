import streamlit as st
import pandas as pd
import numpy as np
from sheet_loader import load_sheet
from datetime import datetime
from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS, K_PTRAFEGO_META_ADS, K_PTRAFEGO_ANUNCIOS_SUBIDOS, K_PCOPY_DADOS, K_GRUPOS_WPP, K_CENTRAL_LANCAMENTOS
from libs.auth_funcs import require_authentication

# Verificação obrigatória no início
require_authentication()

st.image("Logo-SIMPLAINVEST-Light.png")
st.divider()

# Perguntar qual lançamento a pessoa gostaria de analisar
st.header('Qual Lançamento você quer analisar?')

with st.container(border=True):
    cols = st.columns(2)

    with cols[0]:
        PRODUTO = st.radio('Produto', ['Eu Investidor', 'Simpla Club', 'Simpla Wealth'], horizontal=True)
    with cols[1]:
        VERSAO_PRINCIPAL = st.selectbox('Versão', list(reversed(range(1, 26))))

    if st.button('Continuar', use_container_width=True):
        if PRODUTO is not None and VERSAO_PRINCIPAL is not None:
            if PRODUTO == 'Eu Investidor':
                st.session_state["PRODUTO"] = "EI"
            elif PRODUTO == 'Simpla Club':
                st.session_state["PRODUTO"] = "SC"
            else:
                st.session_state["PRODUTO"] = "SW"
            st.session_state["VERSAO_PRINCIPAL"] = VERSAO_PRINCIPAL
            if "PRODUTO" in st.session_state and "VERSAO_PRINCIPAL" in st.session_state:
                if st.session_state["PRODUTO"] == 'EI':
                    st.session_state["LANÇAMENTO"] = f"EI{VERSAO_PRINCIPAL}"
                elif st.session_state["PRODUTO"] == 'SC':
                    st.session_state["LANÇAMENTO"] = f"SC{VERSAO_PRINCIPAL}"
                else:
                    st.session_state["LANÇAMENTO"] = f"SW{VERSAO_PRINCIPAL}"
            st.rerun()


   


