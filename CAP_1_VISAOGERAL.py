import streamlit as st
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px
from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_VENDAS, K_GRUPOS_WPP, K_PCOPY_DADOS, K_PTRAFEGO_DADOS, K_PTRAFEGO_META_ADS, K_CLICKS_WPP, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_LANCAMENTOS, K_PESQUISA_TRAFEGO_PORCAMPANHA, get_df
from libs.cap_visaogeral_funcs import plot_leads_per_day_altair, plot_group_members_per_day_altair, plot_utm_source_counts_altair, plot_utm_medium_pie_chart
from libs.safe_exec import executar_com_seguranca
from libs.auth_funcs import require_authentication
import pandas as pd

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
        try:
            DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
            DF_CENTRAL_PREMATRICULA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
            DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
            DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
            DF_PCOPY_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PCOPY_DADOS)
            DF_GRUPOS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_GRUPOS_WPP)
            DF_CLICKS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CLICKS_WPP)
            DF_CENTRAL_LANCAMENTOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_LANCAMENTOS)
            DF_PESQUISA_TRAFEGO_PORCAMPANHA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PESQUISA_TRAFEGO_PORCAMPANHA)
            status.update(label="Carregados com sucesso!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="Erro ao carregar dados: " + str(e), state="error", expanded=False)
loading_container.empty()

if 'LANÇAMENTO' in st.session_state:
        lancamento = st.session_state['LANÇAMENTO']

#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("CAPTAÇÃO > VISÃO GERAL")
st.title('Visão Geral')

#------------------------------------------------------------
#      01. KEY METRICS
#------------------------------------------------------------
with st.container(border=True):
    col_captura, col_trafego, col_copy, col_whatsapp, col_cpl = st.columns(5)

    with col_captura:
        st.subheader("Captura")
        st.metric(label="Total", value=f"{DF_CENTRAL_CAPTURA.shape[0]}")

    with col_trafego:
        st.subheader("Tráfego")
        st.metric(label="Total", value=f"{DF_PTRAFEGO_DADOS.shape[0]}")
        st.metric(label="Conversão", value=f"{round(DF_PTRAFEGO_DADOS.shape[0]/DF_CENTRAL_CAPTURA.shape[0] * 100, 2)}%", delta="")

    with col_copy:
        st.subheader("Copy")
        st.metric(label="Total", value=f"{DF_PCOPY_DADOS.shape[0]}")
        st.metric(label="Conversão", value=f"{round(DF_PCOPY_DADOS.shape[0]/DF_CENTRAL_CAPTURA.shape[0] * 100, 2)}%", delta="")

    with col_whatsapp:
        st.subheader("WhatsApp")
        wpp_members = DF_GRUPOS_WPP[DF_GRUPOS_WPP["Evento"] == "Entrou no grupo"]
        st.metric(label="Total", value=f"{wpp_members.shape[0]}")
        st.metric(label="Conversão", value=f"{round(wpp_members.shape[0]/DF_CENTRAL_CAPTURA.shape[0] * 100, 2)}%", delta="")
    
    with col_cpl:
        if not DF_PESQUISA_TRAFEGO_PORCAMPANHA.empty:
            DF_PESQUISA_TRAFEGO_PORCAMPANHA["VALOR USADO"] = (
                    DF_PESQUISA_TRAFEGO_PORCAMPANHA["VALOR USADO"]
                    .str.strip()          
                    .str.replace("R$", "", regex=False)  
                    .str.replace(" ", "", regex=False)
                    .str.replace(".", "")
                    .str.replace(",", ".")
                ) 
            total_gasto = DF_PESQUISA_TRAFEGO_PORCAMPANHA['VALOR USADO'].astype(str).astype(float).sum()
            n_qualificados = len(DF_PTRAFEGO_DADOS[DF_PTRAFEGO_DADOS['LEADSCORE'].astype(str).astype(int) >= 80] == True)
            n_total = DF_CENTRAL_CAPTURA.shape[0]
            cpl_qualificados = total_gasto / n_qualificados
            st.subheader("CPL")
            st.metric(label = "Total", value = f'R$ {round(total_gasto/n_total, 2)}')
            st.metric(label = "Qualificados", value = f'R$ {round(total_gasto/n_qualificados, 2)}')
        else:
            print()


#------------------------------------------------------------
#      02. GRUPOS DE WHATSAPP
#------------------------------------------------------------

# ---- 02.A - LEADS POR DIA  
with st.container(border=True):
    executar_com_seguranca("LEADS POR DIA", lambda:plot_leads_per_day_altair(DF_CENTRAL_CAPTURA, DF_CENTRAL_LANCAMENTOS, lancamento))
    

# ---- 02.B - TOTAL DE LEADS POR DIA NOS GRUPOS
with st.container(border=True):
    st.markdown('**Total de leads nos grupos**')
    executar_com_seguranca("LEADS POR DIA NOS GRUPOS", lambda:plot_group_members_per_day_altair(DF_GRUPOS_WPP))
    

st.divider()

#------------------------------------------------------------
#      03. CAPTAÇÃO: ORIGEM / MÍDIA
#------------------------------------------------------------
st.header("Fontes de Leads")
st.caption("Principais origem/mídias de captação")
cols_captacao_utm = st.columns([5, 4])

# ---- 03.A - ORIGEM
with cols_captacao_utm[0]:
    with st.container(border=True):
        st.subheader("Origem")
        executar_com_seguranca("ORIGEM", lambda:plot_utm_source_counts_altair(DF_CENTRAL_CAPTURA, column_name='UTM_SOURCE'))
        

# ---- 03.B - MÍDIA
with cols_captacao_utm[1]:
    with st.container(border=True):
        st.subheader("Mídia")
        executar_com_seguranca("MÍDIA", lambda:plot_utm_medium_pie_chart(DF_CENTRAL_CAPTURA, column_name='UTM_MEDIUM'))

st.divider()


### TODO: FINALIZAR CÓDIGO ABAIXO (NÃO PRIORITÁRIA)
# 04 - FUNIL: PERCURSO COMPLETO
if PRODUTO == 'EI':
    st.header("Trackeamento de Funil")
    st.caption("CAPTAÇÃO > PRÉ-MATRÍCULA > VENDAS")
    cols_captacao_utm = st.columns([5, 4])

    df_vendas_copy = DF_CENTRAL_VENDAS.copy()
    df_vendas_copy['CAP UTM_SOURCE'] = df_vendas_copy.apply(
        lambda x: f"{x['CAP UTM_SOURCE']} {x['CAP UTM_MEDIUM']}" if x['CAP UTM_SOURCE'] == 'ig' else x['CAP UTM_SOURCE'],
        axis=1
        )
    df_vendas_copy['PERCURSO'] = df_vendas_copy['CAP UTM_SOURCE'].astype(str) + ' > ' + \
                                df_vendas_copy['PM UTM_SOURCE'].astype(str) + ' > ' + \
                                df_vendas_copy['UTM_SOURCE'].astype(str)

    percurso_counts = df_vendas_copy['PERCURSO'].value_counts().reset_index()
    percurso_counts.columns = ['PERCURSO', 'COUNT']

    top_20_percurso = percurso_counts.head(20)

    col1, col2 = st.columns([2, 2])

    with col1:
        st.table(top_20_percurso)

    top_5_percurso = top_20_percurso.head(5).sort_values(by='COUNT', ascending=True)

    with col2:
        fig, ax = plt.subplots()
        colors = cm.Blues(np.linspace(0.4, 1, len(top_5_percurso)))
        ax.barh(top_5_percurso['PERCURSO'], top_5_percurso['COUNT'], color=colors)
        ax.set_xlabel('Count', color='#FFFFFF')
        ax.set_ylabel('PERCURSO', color='#FFFFFF')
        ax.set_title('Top 5 Percursos Mais Comuns', color='#FFFFFF')
        ax.set_facecolor('none')
        fig.patch.set_facecolor('none')
        ax.spines['bottom'].set_color('#FFFFFF')
        ax.spines['top'].set_color('#FFFFFF')
        ax.spines['right'].set_color('#FFFFFF')
        ax.spines['left'].set_color('#FFFFFF')
        ax.tick_params(axis='x', colors='#FFFFFF')
        ax.tick_params(axis='y', colors='#FFFFFF')
        plt.tight_layout()
        st.pyplot(fig)

    ### TODO: FINALIZAR O CÓDIGO ACIMA (FIM)