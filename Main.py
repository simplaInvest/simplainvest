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
                    variaveis_para_inicializar = ["Captacao", "CPLs", "Vendas", "VIP", "Reabertura"]
                    for var in variaveis_para_inicializar:
                        st.session_state.setdefault(var, None)  # Inicializa com None se não existir ainda
                    if st.session_state["PRODUTO"] == 'EI':
                        # Dicionário com as datas para cada versão
                        versoes = {
                            16: {
                                'Captacao': [datetime(2024, 2, 12), datetime(2024, 3, 3)],
                                'CPLs': [datetime(2024, 3, dia) for dia in [3, 4, 5, 10]],
                                'Vendas': [datetime(2024, 3, dia) for dia in range(10, 15)],
                                'VIP': [datetime(2024, 3, dia) for dia in range(15, 21)],
                                'Reabertura': datetime(2024, 3, 21),
                            },
                            17: {
                                'Captacao': [datetime(2024, 4, 15), datetime(2024, 5, 5)],
                                'CPLs': [datetime(2024, 5, dia) for dia in [5, 6, 7, 13]],
                                'Vendas': [datetime(2024, 5, dia) for dia in range(13, 18)],
                                'VIP': [datetime(2024, 5, dia) for dia in range(18, 23)],
                                'Reabertura': datetime(2024, 5, 23),
                            },
                            18: {
                                'Captacao': [datetime(2024, 6, 17), datetime(2024, 7, 7)],
                                'CPLs': [datetime(2024, 7, dia) for dia in [7, 8, 9, 15]],
                                'Vendas': [datetime(2024, 7, dia) for dia in range(15, 19)],
                                'VIP': [datetime(2024, 7, dia) for dia in range(18, 23)],
                                'Reabertura': datetime(2024, 7, 25),
                            },
                            19: {
                                'Captacao': [datetime(2024, 8, 12), datetime(2024, 9, 1)],
                                'CPLs': [datetime(2024, 9, dia) for dia in [1, 2, 3, 9]],
                                'Vendas': [datetime(2024, 9, dia) for dia in range(9, 13)],
                                'VIP': [datetime(2024, 9, dia) for dia in range(12, 17)],
                                'Reabertura': datetime(2024, 9, 19),
                            },
                            20: {
                                'Captacao': [datetime(2024, 10, 14), datetime(2024, 11, 3)],
                                'CPLs': [datetime(2024, 11, dia) for dia in [4, 5, 6, 11]],
                                'Vendas': [datetime(2024, 11, dia) for dia in range(11, 15)],
                            },
                            21: {
                                'Captacao': [datetime(2024, 12, 16), datetime(2025, 1, 6)],
                                'CPLs': [datetime(2025, 1, dia) for dia in [6, 7, 8, 9]],
                                'Vendas': [datetime(2025, 1, dia) for dia in range(9, 17)],
                            }
                        }

                        # Define as datas no session_state conforme a versão selecionada
                        versao_atual = VERSAO_PRINCIPAL
                        if versao_atual in versoes:
                            for chave, valor in versoes[versao_atual].items():
                                st.session_state[chave] = valor
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
            st.Page("CAP_5_ANUNCIOS.py", title = "📲 Anúncios"),
            st.Page("5_General_Message_analyzer.py", title = "💬 Message Analyser")
        ],
        'PRÉ-MATRÍCULA': [
            st.Page("PM_1_VISAOGERAL.py", title = "⭐ Visão Geral"),
        ],
        'VENDAS': [
            st.Page("VENDAS_1_VISAOGERAL.py", title = "💵 Visão geral"),
        ],
        'GERAL': [
            st.Page("ETC_EVOLUCAO.py", title = "🎯 Comparação de Lançamentos"),
            st.Page("dbf_gen.py", title = "🔮 Gerador de Debriefing")
        ]
    }
    pages = pages_after_load

# Configurar a navegação
nav = st.navigation(pages, position="sidebar")
nav.run()