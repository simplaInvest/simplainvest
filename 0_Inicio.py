import streamlit as st
st.set_page_config(page_title="Inteligência de Dados", page_icon="📊")

import pandas as pd
import numpy as np
from sheet_loader import load_sheet
from datetime import datetime
from libs.data_loader import (
    K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS,
    K_PTRAFEGO_META_ADS, K_PTRAFEGO_ANUNCIOS_SUBIDOS, K_PCOPY_DADOS, K_GRUPOS_WPP,
    K_CENTRAL_LANCAMENTOS
)
from libs.auth_funcs import require_authentication

# Verificação obrigatória no início
require_authentication()

# ---------- Cabeçalho compacto e profissional ----------
with st.container():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("Logo-SIMPLAINVEST-Light.png", use_container_width=True)

st.divider()

# ---------- Título + Stepper visual (apenas estético) ----------
st.markdown("""
<div class="stepper">
  <div class="step active"></div><span class="step-line"></span>
  <div class="step"></div><span class="step-line"></span>
  <div class="step"></div>
</div>
""", unsafe_allow_html=True)
st.header('Qual Lançamento você quer analisar?')

with st.container(border=True):
    cols = st.columns(2)

    # Mantém os MESMOS valores que você usa depois (EI/SC/SW via mapping)
    produtos = ['Eu Investidor', 'Simpla Club', 'Simpla Wealth']
    produto_emojis = {
        'Eu Investidor': '📘 Eu Investidor',
        'Simpla Club': '🏆 Simpla Club',
        'Simpla Wealth': '💎 Simpla Wealth'
    }

    with cols[0]:
        PRODUTO = st.radio(
            'Produto',
            produtos,
            horizontal=True,
            format_func=lambda x: produto_emojis.get(x, x),
            help="Escolha o produto do lançamento."
        )

    with cols[1]:
        VERSAO_PRINCIPAL = st.selectbox(
            'Versão',
            list(reversed(range(1, 28))),
            help="Selecione a versão principal do lançamento (1 a 27)."
        )

    # Pré-visualização do código do lançamento (apenas visual, não altera a lógica)
    if PRODUTO is not None and VERSAO_PRINCIPAL is not None:
        prod_code = "EI" if PRODUTO == "Eu Investidor" else ("SC" if PRODUTO == "Simpla Club" else "SW")
        preview = f"{prod_code}{VERSAO_PRINCIPAL}"
        st.markdown(f"""
        <div class="card" style="margin-top:8px;">
          <strong>Pré-visualização:</strong> <span class="chip chip--ok">{preview}</span>
          <span class="muted" style="margin-left:8px;">(confira antes de continuar)</span>
        </div>
        """, unsafe_allow_html=True)

    st.write("")  # respiro

    # Botão idêntico (só o rótulo com ícone)
    if st.button('Continuar →', use_container_width=True):
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
