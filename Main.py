import streamlit as st
from datetime import datetime

## PÁGINA DE SETUP
if not "PRODUTO" in st.session_state and not "VERSAO_PRINCIPAL" in st.session_state:
    st.set_page_config(
        layout="centered",
        page_title="Central de Ferramentas Simpla Invest 💎",
        page_icon="💎"
    )
    pages = {
        'CONFIGURAÇÕES': [
            st.Page("0_Inicio.py", title="🏠 Início"),
        ]
    }
## PÁGINAS DE ANÁLISES
else:
    st.set_page_config(
        layout="wide",
        page_title="Central de Ferramentas Simpla Invest 💎",
        page_icon="💎"
    )
    with st.sidebar:
        st.text("Lançamento selecionado:")
        lancamento_cod = st.session_state["PRODUTO"] + ' - ' + str(st.session_state["VERSAO_PRINCIPAL"])
        with st.expander(lancamento_cod):
            PRODUTO = st.radio(
                "Produto", 
                ["Eu Investidor", "Simpla Club", "Simpla Wealth"]
            )
            options = list(reversed(range(1, 26)))
            index = options.index(st.session_state["VERSAO_PRINCIPAL"])
            VERSAO_PRINCIPAL = st.selectbox('Versão', options, index=index)
            if st.button('Alterar', use_container_width=True):
                if PRODUTO is not None and VERSAO_PRINCIPAL is not None:
                    if PRODUTO == "Eu Investidor":
                        st.session_state["PRODUTO"] = "EI"
                    if PRODUTO == "Simpla Club":
                        st.session_state["PRODUTO"] = "SC"
                    elif PRODUTO == "Simpla Wealth":
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

pages_after_load = {
    'INÍCIO': [
        st.Page("dummy_snippets.py", title="🏠 Início"),
    ],
    'CAPTAÇÃO': [
        st.Page("CAP_1_VISAOGERAL.py", title="📊 Visão Geral"),
        st.Page("CAP_2_PTRAFEGO.py", title="💲 Pesquisa de Tráfego"),
        st.Page("CAP_3_PCOPY.py", title="🧑 Pesquisa de Copy"),
        st.Page("CAP_4_GRUPOS_WPP.py", title="📞 Grupos de Whatsapp"),
        st.Page("CAP_5_ANUNCIOS.py", title="📲 Anúncios"),
        st.Page("5_General_Message_analyzer.py", title="💬 Message Analyser")
    ],
    'PRÉ-MATRÍCULA': [
        st.Page("PM_1_VISAOGERAL.py", title="⭐ Visão Geral"),
    ],
    'VENDAS': [
        st.Page("VENDAS_1_VISAOGERAL.py", title="💵 Visão geral"),
    ],
    'GERAL': [
        st.Page("ETC_EVOLUCAO.py", title="🎯 Comparação de Lançamentos"),
        st.Page("dbf_gen.py", title="🔮 Gerador de Debriefing")
    ]
}

pages = pages_after_load



# Configurar a navegação
nav = st.navigation(pages, position="sidebar")
nav.run()