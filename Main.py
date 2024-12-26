import streamlit as st

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
            PRODUTO = st.radio('Produto', ['Eu Investidor', 'Simpla Club'])
            options = list(reversed(range(1, 22)))
            index = options.index(st.session_state["VERSAO_PRINCIPAL"])
            VERSAO_PRINCIPAL = st.selectbox('Versão', options, index=index)
            if st.button('Alterar', use_container_width=True):
                if PRODUTO is not None and VERSAO_PRINCIPAL is not None:
                    st.session_state["PRODUTO"] = "EI" if PRODUTO == "Eu Investidor" else "SC"
                    st.session_state["VERSAO_PRINCIPAL"] = VERSAO_PRINCIPAL
                    st.rerun()
    pages_after_load = {
        'INÍCIO': [
            st.Page("dummy_snippets.py", title = "🏠 Início"),
        ],
        'CAPTAÇÃO': [
            st.Page("CAP_1_VISAOGERAL.py", title = "📊 Visão Geral"),
            st.Page("CAP_2_PTRAFEGO.py", title = "💲 Pesquisa de Tráfego"),
            st.Page("CAP_3_PCOPY.py", title = "🧑 Pesquisa de Copy"),
            st.Page("CAP_4_GRUPOS_WPP.py", title = "📞 Grupos de Whatsapp"),
            st.Page("prematricula.py", title = "✅ Pré-Matrícula"),
            st.Page("vendas.py", title = "💸 Central de Vendas"),
            st.Page("Evolucao.py", title = "Evo")
            # st.Page("2_Análise Geral Lançamento.py", title=" Análise Geral Lançamento"),
            # st.Page("4_Anúncios.py", title="Anuncios"),
            # st.Page("3_Desempenho_UTMS.py", title="Desempenho UTMS"),
            # st.Page("5_General_Message_analyzer.py", title="Message Analyzer"),
            # st.Page("98_Tester.py", title="anunciosss"),
            # st.Page("6_Analise_Dinamica.py", title="Análise dinâmica")
        ]
    }
    pages = pages_after_load

# Configurar a navegação
nav = st.navigation(pages, position="sidebar")
nav.run()