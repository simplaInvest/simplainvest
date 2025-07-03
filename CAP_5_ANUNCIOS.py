import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS, get_df
from libs.cap_anuncios_funcs import mostrar_analise_captacao, mostrar_analise_pm, mostrar_analise_vendas
from libs.safe_exec import executar_com_seguranca
from libs.auth_funcs import require_authentication

# Verificação obrigatória no início
require_authentication()

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

logo = "Logo-EUINVESTIDOR-Light.png" if PRODUTO == "EI" else "Logo-SIMPLA-Light.png"
st.logo(image = logo)

# Carregar DataFrames para lançamento selecionado
loading_container = st.empty()
with loading_container:
    status = st.status("Carregando dados...", expanded=True)
    with status:
        df_captura = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
        df_prematricula = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
        df_vendas = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
        df_ptrafego_dados = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
        status.update(label="Carregados com sucesso!", state="complete", expanded=False)
loading_container.empty()

#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("CAPTAÇÃO >  ANÚNCIOS")
st.title('Anúncios')

abas = ["Captação", "Vendas"]
if PRODUTO == "EI":
    abas.insert(1, "Pré-Matrícula")

abas_streamlit = st.tabs(abas)

# Mapeia cada aba ao seu conteúdo correspondente
with abas_streamlit[0]:
    executar_com_seguranca("ANÁLISE DE CAPTAÇÃO", lambda:mostrar_analise_captacao(df_captura, df_prematricula, df_vendas, PRODUTO))

if PRODUTO == "EI":
    with abas_streamlit[1]:
        executar_com_seguranca("ANÁLISE DE PRÉ-MATRÍCULA", lambda:mostrar_analise_pm(df_prematricula, df_vendas))
    with abas_streamlit[2]:
        executar_com_seguranca("ANÁLISE DE VENDAS", lambda:mostrar_analise_vendas(df_vendas))
else:
    with abas_streamlit[1]:
        executar_com_seguranca("ANÁLISE DE VENDAS", lambda:mostrar_analise_vendas(df_vendas))


