import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

from libs.data_loader import K_CENTRAL_CAPTURA, K_GRUPOS_WPP, K_PCOPY_DADOS, K_PTRAFEGO_DADOS, K_CLICKS_WPP, K_CENTRAL_LANCAMENTOS, get_df
from libs.cap_wpp_funcs import plot_group_members_per_day_altair, plot_entry_per_day, plot_exit_per_day, plot_ratio_per_day, calculate_stay_duration_and_plot_histogram, plot_clicks_over_time
from libs.safe_exec import executar_com_seguranca
from libs.auth_funcs import require_authentication

# Verificação obrigatória no início
require_authentication()

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]
LANCAMENTO = st.session_state["LANÇAMENTO"]

logo = "Logo-EUINVESTIDOR-Light.png" if PRODUTO == "EI" else "Logo-SIMPLA-Light.png"
st.logo(image = logo)

# Carregar DataFrames para lançamento selecionado
loading_container = st.empty()
with loading_container:
    status = st.status("Carregando dados...", expanded=True)
    with status:
        DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
        DF_GRUPOS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_GRUPOS_WPP)
        DF_CLICKS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CLICKS_WPP)
        DF_CENTRAL_LANCAMENTOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_LANCAMENTOS)
        status.update(label="Carregados com sucesso!", state="complete", expanded=False)
loading_container.empty()

# Cria Dataframes de Entradas e Saidas dos grupos
whatsapp_entradas = DF_GRUPOS_WPP[DF_GRUPOS_WPP['Evento'] == 'Entrou no grupo']
whatsapp_saidas = DF_GRUPOS_WPP[DF_GRUPOS_WPP['Evento'] == 'Saiu do grupo']

#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("CAPTAÇÃO > GRUPOS DE WHATSAPP")
st.title('Grupos de Whatsapp')

#------------------------------------------------------------
#      01. DUMMY SECTION
#------------------------------------------------------------

DF_GRUPOS_WPP['Entry'] = DF_GRUPOS_WPP['Evento'].str.contains("Entrou", na=False).astype(int)
DF_GRUPOS_WPP['Exit'] = DF_GRUPOS_WPP['Evento'].str.contains("Saiu", na=False).astype(int)

# Group by date and calculate cumulative sums for entries and exits
daily_activity = DF_GRUPOS_WPP.groupby(DF_GRUPOS_WPP['Data'].dt.date)[['Entry', 'Exit']].sum().reset_index()

# Rename the grouped date column for clarity
daily_activity.rename(columns={'Data': 'Date'}, inplace=True)

# Calculate cumulative members
daily_activity['Members'] = daily_activity['Entry'].cumsum() - daily_activity['Exit'].cumsum()
daily_activity['Ratio'] = round((daily_activity['Exit']/daily_activity['Entry']) * 100, 2)

with st.container(border = True):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("Leads")
        st.metric(label = 'Leads Capturados', value=f"{DF_CENTRAL_CAPTURA.shape[0]}", label_visibility="collapsed")

    with col2:
        st.subheader("Entradas")
        st.metric(label = 'Entradas nos Grupos', value=f"{whatsapp_entradas.shape[0]} ({round((whatsapp_entradas.shape[0]/DF_CENTRAL_CAPTURA.shape[0])*100, 2)}%)", label_visibility="collapsed")

    with col3:
        st.subheader("Saidas")
        st.metric(label = 'Saídas dos Grupos', value=f"{whatsapp_saidas.shape[0]} ({round((whatsapp_saidas.shape[0]/DF_CENTRAL_CAPTURA.shape[0])*100, 2)}%)", label_visibility="collapsed")
        

    with col4:
        st.subheader("Nos grupos")
        nos_grupos = whatsapp_entradas.shape[0] - whatsapp_saidas.shape[0]
        st.metric(label = 'Saldo nos Grupos', value=f"{nos_grupos} ({round((nos_grupos/DF_CENTRAL_CAPTURA.shape[0])*100, 2)}%)", label_visibility="collapsed")
        

st.subheader('Número de pessoas no grupo')
executar_com_seguranca("NÚMERO DE PESSOAS NO GRUPO", lambda:plot_group_members_per_day_altair(daily_activity, DF_CENTRAL_LANCAMENTOS, LANCAMENTO))

cols_clicks_wpp = st.columns([3,1])
if DF_CLICKS_WPP.empty:
    st.write('')
else:
    with cols_clicks_wpp[0]:
        with st.container(border=True):
            st.markdown('**Clicks por dia**')
            executar_com_seguranca("CLICKS POR DIA", lambda:plot_clicks_over_time(DF_CLICKS_WPP))

    # ---- 02.D - TOTAL CLICKS
    with cols_clicks_wpp[1]:
        st.metric(label = 'Clicks hoje', value = f"{DF_CLICKS_WPP.loc[DF_CLICKS_WPP['DATA'].idxmax(), 'CLICKS NO DIA']}")
        st.metric(label = 'Clicks totais', value = f"{DF_CLICKS_WPP.loc[DF_CLICKS_WPP['DATA'].idxmax(), 'TOTAL']}")

st.subheader('Número de entradas por dia')
executar_com_seguranca("ENTRADAS POR DIA", lambda:plot_entry_per_day(daily_activity))

st.subheader('Número de saídas por dia')
executar_com_seguranca("SAÍDAS POR DIA", lambda:plot_exit_per_day(daily_activity))

st.subheader('Proporção de saídas em relação a entradaspor dia')
executar_com_seguranca("PROPORÇÃO DE SAÍDAS EM RELAÇÃO A ENTRADAS POR DIA", lambda:plot_ratio_per_day(daily_activity))


st.subheader('Distribuição de Tempo de Permanência nos Grupos (em dias)')
executar_com_seguranca("DISTRIBUIÇÃO DE TEMPO DE PERMANÊNCIA NOS GRUPOS (EM DIAS)", lambda:calculate_stay_duration_and_plot_histogram(DF_GRUPOS_WPP))
st.write('O gráfico mostra o comportamento dos leads que saem dos grupos. Cada coluna representa uma quantidade de dias e seus valores mostram quantos leads saíram depois de ficar aquela quantidade de dias no grupo')
