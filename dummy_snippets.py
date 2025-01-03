import streamlit as st

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_GRUPOS_WPP, K_PCOPY_DADOS, K_PTRAFEGO_DADOS, K_PTRAFEGO_META_ADS, clear_df, get_df

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

# # Carregar DataFrames para lançamento selecionado
# DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
# DF_CENTRAL_PREMATRICULA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
# DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
# DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
# DF_PCOPY_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PCOPY_DADOS)
# DF_GRUPOS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_GRUPOS_WPP)

#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("INÍCIO > LOADED DATA")
st.title('Loaded Data')

#------------------------------------------------------------
#      01. DUMMY SECTION
#------------------------------------------------------------

if st.button("Limpar caches"):
    clear_df()

if f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_CENTRAL_CAPTURA}" in st.session_state:
    with st.expander("CENTRAL_CAPTURA"):
        st.dataframe(st.session_state[f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_CENTRAL_CAPTURA}"])
if f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_CENTRAL_PRE_MATRICULA}" in st.session_state:
    with st.expander("CENTRAL_PRE_MATRICULA"):      
        st.dataframe(st.session_state[f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_CENTRAL_PRE_MATRICULA}"])
if f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_CENTRAL_VENDAS}" in st.session_state:
    with st.expander("CENTRAL_VENDAS"):
        st.dataframe(st.session_state[f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_CENTRAL_VENDAS}"])
if f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_PTRAFEGO_DADOS}" in st.session_state:
    with st.expander("PTRAFEGO_DADOS"):
        st.dataframe(st.session_state[f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_PTRAFEGO_DADOS}"])
if f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_PTRAFEGO_META_ADS}" in st.session_state:
    with st.expander("PTRAFEGO_META_ADS"):
        st.dataframe(st.session_state[f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_PTRAFEGO_META_ADS}"])
if f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_PCOPY_DADOS}" in st.session_state:
    with st.expander("PCOPY_DADOS"):
        st.dataframe(st.session_state[f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_PCOPY_DADOS}"])
if f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_GRUPOS_WPP}" in st.session_state:
    with st.expander("GRUPOS_WPP"):
        st.dataframe(st.session_state[f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_GRUPOS_WPP}"])