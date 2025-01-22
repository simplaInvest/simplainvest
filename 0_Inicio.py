import streamlit as st
import pandas as pd
import numpy as np
from sheet_loader import load_sheet
from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS, K_PTRAFEGO_META_ADS, K_PTRAFEGO_ANUNCIOS_SUBIDOS, K_PCOPY_DADOS, K_GRUPOS_WPP

st.title("Central de Lançamentos")
st.divider()

# Perguntar qual lançamento a pessoa gostaria de analisar
st.header('Qual Lançamento você quer analisar?')

with st.container(border=True):
    cols = st.columns(2)

    with cols[0]:
        PRODUTO = st.radio('Produto', ['Eu Investidor', 'Simpla Club'], horizontal=True)
    with cols[1]:
        VERSAO_PRINCIPAL = st.selectbox('Versão', list(reversed(range(1, 26))))

    if st.button('Continuar', use_container_width=True):
        if PRODUTO is not None and VERSAO_PRINCIPAL is not None:
            st.session_state["PRODUTO"] = "EI" if PRODUTO == "Eu Investidor" else "SC"
            st.session_state["VERSAO_PRINCIPAL"] = VERSAO_PRINCIPAL
            st.rerun()
   


