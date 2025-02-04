import streamlit as st
import pandas as pd
import numpy as np
from sheet_loader import load_sheet
from datetime import datetime
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
            variaveis_para_inicializar = ["Captacao", "CPLs", "Vendas", "VIP", "Reabertura"]
            for var in variaveis_para_inicializar:
                st.session_state.setdefault(var, None)  # Inicializa com None se não existir ainda
            if "PRODUTO" in st.session_state and "VERSAO_PRINCIPAL" in st.session_state:
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
                    versao_atual = st.session_state["VERSAO_PRINCIPAL"]
                    if versao_atual in versoes:
                        for chave, valor in versoes[versao_atual].items():
                            st.session_state[chave] = valor
            st.rerun()


   


