import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go
import datetime

from libs.data_loader import (
    K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS,
    K_PTRAFEGO_DADOS, K_CENTRAL_LANCAMENTOS, K_PESQUISA_TRAFEGO_PORCAMPANHA, get_df
)
from libs.cap_traf_funcs import create_distribution_chart, calcular_proporcoes_e_plotar, create_heatmap
from libs.safe_exec import executar_com_seguranca
from libs.auth_funcs import require_authentication

# ===========================
# Verificação obrigatória
# ===========================
require_authentication()

# ===========================
# Contexto selecionado
# ===========================
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]
LANÇAMENTO = st.session_state["LANÇAMENTO"]

logo = "Logo-EUINVESTIDOR-Light.png" if PRODUTO == "EI" else "Logo-SIMPLA-Light.png"
st.logo(image=logo)

st.caption("CAPTAÇÃO > PESQUISA DE TRÁFEGO")

# ===========================
# Carregamento de dados
# ===========================
loading_container = st.empty()
with loading_container:
    status = st.status("Carregando dados...", expanded=True)
    with status:
        DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
        DF_CENTRAL_PREMATRICULA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
        DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
        DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
        DF_CENTRAL_LANCAMENTOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_LANCAMENTOS)
        DF_PESQUISA_TRAFEGO_PORCAMPANHA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PESQUISA_TRAFEGO_PORCAMPANHA)
        status.update(label="Carregados com sucesso!", state="complete", expanded=False)
loading_container.empty()

# ===========================
# Layout
# ===========================
cols_1 = st.columns(2)
with cols_1[0]:
    st.title('Pesquisa de Tráfego')
with cols_1[1]:
    filter_container = st.container()

# ------------------------------------------------------------
# 01. FILTROS (mesma lógica, UI organizada)
# ------------------------------------------------------------
with st.container(border=True):
    st.subheader("Filtros")
    st.caption("Refine os dados por UTM e período. Selecione “TODOS” para não filtrar.")

    columns_to_filter = ['UTM_TERM', 'UTM_CAMPAIGN', 'UTM_SOURCE', 'UTM_MEDIUM', 'UTM_ADSET']
    filters = {}
    cols_filters = st.columns(len(columns_to_filter))

    # 1.A Anúncios (utm_term)
    with cols_filters[0]:
        unique_terms = list(DF_PTRAFEGO_DADOS['UTM_TERM'].dropna().unique())
        unique_terms = ['TODOS'] + unique_terms
        filters['UTM_TERM'] = st.multiselect("**Anúncios** *(utm_term)*", unique_terms, default=["TODOS"], key="UTM_TERM")

    # 1.B Campanhas (utm_campaign)
    with cols_filters[1]:
        unique_campaigns = list(DF_PTRAFEGO_DADOS['UTM_CAMPAIGN'].dropna().unique())
        unique_campaigns = ['TODOS'] + unique_campaigns
        if "UTM_CAMPAIGN" not in st.session_state:
            st.session_state["UTM_CAMPAIGN"] = ["TODOS"]
        filters['UTM_CAMPAIGN'] = st.multiselect("**Campanhas** *(utm_campaign)*", unique_campaigns, default=st.session_state["UTM_CAMPAIGN"], key="UTM_CAMPAIGN")

    # 1.C Origens (utm_source)
    with cols_filters[2]:
        unique_sources = list(DF_PTRAFEGO_DADOS['UTM_SOURCE'].dropna().unique())
        unique_sources = ['TODOS'] + unique_sources
        if "UTM_SOURCE" not in st.session_state:
            st.session_state["UTM_SOURCE"] = ["TODOS"]
        filters['UTM_SOURCE'] = st.multiselect("**Origens** *(utm_source)*", unique_sources, default=st.session_state["UTM_SOURCE"], key="UTM_SOURCE")

    # 1.D Mídias (utm_medium)
    with cols_filters[3]:
        unique_mediums = list(DF_PTRAFEGO_DADOS['UTM_MEDIUM'].dropna().unique())
        unique_mediums = ['TODOS'] + unique_mediums
        if "UTM_MEDIUM" not in st.session_state:
            st.session_state["UTM_MEDIUM"] = ["TODOS"]
        filters['UTM_MEDIUM'] = st.multiselect("**Mídias** *(utm_medium)*", unique_mediums, default=st.session_state["UTM_MEDIUM"], key="UTM_MEDIUM")

    # 1.E Conjuntos (utm_adset)
    with cols_filters[4]:
        unique_adsets = list(DF_PTRAFEGO_DADOS['UTM_ADSET'].dropna().unique())
        unique_adsets = (['TODOS', 'LEADSCORE'] if any('[LS]' in str(a) for a in unique_adsets) else ['TODOS']) + unique_adsets
        if "UTM_ADSET" not in st.session_state:
            st.session_state["UTM_ADSET"] = ["TODOS"]
        filters['UTM_ADSET'] = st.multiselect("**Conjuntos** *(utm_adset)*", unique_adsets, default=st.session_state["UTM_ADSET"], key="UTM_ADSET")

# Normalização visual: se “TODOS” + outros, ignora “TODOS”
for k, vals in filters.items():
    if "TODOS" in vals and len(vals) > 1:
        filters[k] = [v for v in vals if v != "TODOS"]

# Aplicar filtros (mesma lógica)
filtered_DF_PTRAFEGO_DADOS = DF_PTRAFEGO_DADOS.copy()
selected_dates = None

for column, selected_values in filters.items():
    if "TODOS" not in selected_values:
        if column == "UTM_ADSET":
            condicoes = []
            if "LEADSCORE" in selected_values:
                condicoes.append(filtered_DF_PTRAFEGO_DADOS['UTM_ADSET'].str.contains(r'\[LS\]', na=False))
                selected_values = [x for x in selected_values if x != "LEADSCORE"]
            if selected_values:
                condicoes.append(filtered_DF_PTRAFEGO_DADOS['UTM_ADSET'].isin(selected_values))
            if condicoes:
                from functools import reduce
                import operator
                filtro_final = reduce(operator.or_, condicoes)
                filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtro_final]
        else:
            filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS[column].isin(selected_values)]

# Se vazio, avisa e não segue
if filtered_DF_PTRAFEGO_DADOS.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
else:
    st.divider()

    # ------------------------------------------------------------
    # 02. RESUMO
    # ------------------------------------------------------------
    with filter_container:
        cols_container = st.columns(2)
        with cols_container[0]:
            st.subheader("Etapas")
            options = ["Captação", "Pré-matrícula", "Vendas"]
            filters_etapas = st.multiselect(label="Filtros por etapa:", options=options)
            if filters_etapas is not None:
                if "Captação" in filters_etapas:
                    filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[
                        filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_CAPTURA['EMAIL'].str.lower())
                    ]
                if "Pré-matrícula" in filters_etapas:
                    filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[
                        filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_PREMATRICULA['EMAIL'].str.lower())
                    ]
                if "Vendas" in filters_etapas:
                    filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[
                        filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower())
                    ]

        with cols_container[1]:
            st.subheader("Amostra atual")
            st.metric(
                label="Respostas da pesquisa",
                value=f"{filtered_DF_PTRAFEGO_DADOS.shape[0]}  "
                      f"({round((filtered_DF_PTRAFEGO_DADOS.shape[0] / DF_CENTRAL_CAPTURA.shape[0]) * 100, 2) if DF_CENTRAL_CAPTURA.shape[0] != 0 else 0}%)"
            )

    # Ordens/Sliders
    cols_finan_01 = 'PATRIMONIO'
    cols_finan_02 = 'QUANTO_POUPA' if PRODUTO == "SW" else 'RENDA MENSAL'

    patrimonio_order = [
        'Menos de R$5 mil',
        'Entre R$5 mil e R$20 mil',
        'Entre R$20 mil e R$100 mil',
        'Entre R$100 mil e R$250 mil',
        'Entre R$250 mil e R$500 mil',
        'Entre R$500 mil e R$1 milhão',
        'Acima de R$1 milhão',
        'Entre R$1 milhão e R$5 milhões',
        'Acima de R$5 milhões'
    ]

    escolaridade_order = [
        'Ensino técnico',
        'Ensino médio',
        'Ensino superior incompleto',
        'Ensino superior completo',
        'Mestrado',
        'Doutorado'
    ]

    if PRODUTO != 'SW':
        col2_order = [
            'Até R$1.500',
            'Entre R$1.500 e R$2.500',
            'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$10.000',
            'Entre R$10.000 e R$20.000',
            'Acima de R$20.000'
        ]
    else:
        col2_order = [
            'Até R$250',
            'Entre R$250 e R$500',
            'Entre R$500 e R$1.000',
            'Entre R$1.000 e R$2.500',
            'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$15.000',
            'Acima de R$15.000'
        ]

    if PRODUTO in ("EI", "SW"):
        def criar_slider(order, nome_da_var):
            return st.select_slider(
                f'Selecione as faixas de {nome_da_var}',
                options=order,
                value=(order[3], order[-1]) if order == patrimonio_order else (order[2], order[-1])
            )
    if PRODUTO == "SC":
        def criar_slider(order, nome_da_var):
            return st.select_slider(
                f'Selecione as faixas de {nome_da_var}',
                options=order,
                value=(order[1], order[-1]) if order == patrimonio_order else (order[2], order[-1])
            )

    cols_resumo = st.columns(3)

    # 02.A Filtro Data de Captura
    with cols_resumo[0]:
        with st.container(border=True):
            st.markdown("**Filtro por Data de Captura**")
            valid_dates = filtered_DF_PTRAFEGO_DADOS['DATA DE CAPTURA'].dropna()
            if not valid_dates.empty:
                cap_inicio = pd.to_datetime(
                    DF_CENTRAL_LANCAMENTOS.loc[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO, 'CAPTACAO_INICIO'].values[0],
                    dayfirst=True
                )
                cap_fim = pd.to_datetime(
                    DF_CENTRAL_LANCAMENTOS.loc[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO, 'CAPTACAO_FIM'].values[0],
                    dayfirst=True
                )
                selected_dates = st.date_input(
                    "Selecione o período",
                    value=(cap_inicio, cap_fim),
                    min_value=cap_inicio,
                    max_value=cap_fim,
                    key="date_filter"
                )
                if len(selected_dates) == 2:
                    filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[
                        filtered_DF_PTRAFEGO_DADOS['DATA DE CAPTURA'].dt.date.between(
                            selected_dates[0], selected_dates[1]
                        )
                    ]
            else:
                st.warning("Não há datas válidas disponíveis para filtrar.")
                selected_dates = None

    # 02.B Patrimônio
    with cols_resumo[1]:
        with st.container(border=True):
            selected_patrimonio_start, selected_patrimonio_end = criar_slider(patrimonio_order, 'Patrimônio')
            patrimonio_acima_selecionado = filtered_DF_PTRAFEGO_DADOS[
                filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].isin(
                    patrimonio_order[
                        patrimonio_order.index(selected_patrimonio_start): patrimonio_order.index(selected_patrimonio_end) + 1
                    ]
                )
            ]

    # 02.C Renda/Quanto Poupa
    with cols_resumo[2]:
        with st.container(border=True):
            selected_renda_start, selected_renda_end = criar_slider(col2_order, f'{cols_finan_02}')
            renda_acima_selecionado = filtered_DF_PTRAFEGO_DADOS[
                filtered_DF_PTRAFEGO_DADOS[cols_finan_02].isin(
                    col2_order[col2_order.index(selected_renda_start): col2_order.index(selected_renda_end) + 1]
                )
            ]

    renda_patrimonio_acima_selecionado = filtered_DF_PTRAFEGO_DADOS[
        (filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].isin(
            patrimonio_order[patrimonio_order.index(selected_patrimonio_start): patrimonio_order.index(selected_patrimonio_end) + 1]
        )) &
        (filtered_DF_PTRAFEGO_DADOS[cols_finan_02].isin(
            col2_order[col2_order.index(selected_renda_start): col2_order.index(selected_renda_end) + 1]
        ))
    ]

    # Métricas-resumo em cards
    with st.container(border=True):
        metrics_cols = st.columns(6)
        with metrics_cols[0]:
            df_unido = pd.concat([patrimonio_acima_selecionado, renda_acima_selecionado])
            df_unido = df_unido[~df_unido.index.duplicated(keep='first')]
            st.metric(
                label='TOTAL DE PESQUISAS',
                value=f"{df_unido.shape[0]}  "
                      f"({round((df_unido.shape[0] / filtered_DF_PTRAFEGO_DADOS.shape[0]) * 100, 2) if filtered_DF_PTRAFEGO_DADOS.shape[0] != 0 else 0}%)"
            )
        with metrics_cols[1]:
            st.metric(
                label=f'{cols_finan_01}',
                value=f"{patrimonio_acima_selecionado.shape[0]}  "
                      f"({round((patrimonio_acima_selecionado.shape[0] / filtered_DF_PTRAFEGO_DADOS.shape[0]) * 100, 2) if filtered_DF_PTRAFEGO_DADOS.shape[0] != 0 else 0}%)"
            )
        with metrics_cols[2]:
            st.metric(
                label=f'{cols_finan_02}:',
                value=f"{renda_acima_selecionado.shape[0]}  "
                      f"({round((renda_acima_selecionado.shape[0] / filtered_DF_PTRAFEGO_DADOS.shape[0]) * 100, 2) if filtered_DF_PTRAFEGO_DADOS.shape[0] != 0 else 0}%)"
            )
        with metrics_cols[3]:
            st.metric(
                label=f'{cols_finan_01} e\n{cols_finan_02}:',
                value=f"{renda_patrimonio_acima_selecionado.shape[0]}  "
                      f"({round((renda_patrimonio_acima_selecionado.shape[0] / filtered_DF_PTRAFEGO_DADOS.shape[0]) * 100, 2) if filtered_DF_PTRAFEGO_DADOS.shape[0] != 0 else 0}%)"
            )
        with metrics_cols[4]:
            n_qualificados = len(filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS['LEADSCORE'].astype(str).astype(int) >= 80] == True)
            st.metric(
                label = 'Nº de leads qualificados\n(LEADSCORE)',
                value = f'{len(filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS['LEADSCORE'].astype(str).astype(int) >= 80] == True)} '
                        f'({round((n_qualificados / filtered_DF_PTRAFEGO_DADOS.shape[0]) * 100, 2) if filtered_DF_PTRAFEGO_DADOS.shape[0] != 0 else 0}%)'
            )
        with metrics_cols[5]:
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
                cpl_qualificados = total_gasto / n_qualificados
                st.metric(
                    label = 'CPL QUALIFICADO:',
                    value = f'R$ {round(cpl_qualificados, 2)}'
                )
            else:
                print()

    st.divider()

    # ------------------------------------------------------------
    # 03. GRÁFICOS DE BARRAS & DATAFRAME
    # ------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(['Perfil', 'Heatmap & Proxy', 'LEADSCORE'])

    with tab1:
        secondary_order = col2_order
        CHART_CONFIG = {
            'patrimonio': {'column': 'PATRIMONIO', 'color': 'lightblue', 'title': '', 'display_name': 'Patrimônio'},
            'renda': {'column': cols_finan_02, 'color': 'lightgreen', 'title': '', 'display_name': 'Renda' if PRODUTO == "SW" else 'Quanto poupa'},
            'escolaridade': {'column': 'ESCOLARIDADE', 'color': 'lightyellow', 'title': '', 'display_name': 'Escolaridade'}
        }

        filtered_patrimonio = filtered_DF_PTRAFEGO_DADOS[
            filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].isin(patrimonio_order)
        ]

        renda_coluna = 'QUANTO POUPA' if PRODUTO == 'SW' else 'RENDA MENSAL'
        filtered_renda = filtered_DF_PTRAFEGO_DADOS[
            filtered_DF_PTRAFEGO_DADOS[renda_coluna].isin(col2_order)
        ]

        if 'ESCOLARIDADE' in filtered_DF_PTRAFEGO_DADOS.columns:
            filtered_escolaridade = filtered_DF_PTRAFEGO_DADOS[
                filtered_DF_PTRAFEGO_DADOS['ESCOLARIDADE'].isin(escolaridade_order)
            ]

        col1, col2 = st.columns(2)

        # 03.A Patrimônio + Escolaridade
        with col1:
            with st.container(border=True):
                st.subheader("Patrimônio")
                st.caption("Distribuição por faixa")
                patrimonio_chart, patrimonio_df = executar_com_seguranca(
                    "PATRIMÔNIO",
                    lambda: create_distribution_chart(
                        filtered_patrimonio, 'PATRIMONIO', patrimonio_order,
                        CHART_CONFIG['patrimonio']['color'], CHART_CONFIG['patrimonio']['title']
                    )
                )
                st.altair_chart(patrimonio_chart, use_container_width=True)
                st.dataframe(
                    patrimonio_df[['PATRIMONIO', 'count']].rename(columns={'PATRIMONIO': 'Patrimônio', 'count': 'Quantidade'}),
                    use_container_width=True, hide_index=True
                )

            if 'ESCOLARIDADE' in filtered_DF_PTRAFEGO_DADOS.columns:
                with st.container(border=True):
                    st.subheader("Escolaridade")
                    st.caption("Distribuição por nível")
                    escolaridade_chart, escolaridade_df = executar_com_seguranca(
                        "ESCOLARIDADE",
                        lambda: create_distribution_chart(
                            filtered_escolaridade, 'ESCOLARIDADE', escolaridade_order,
                            CHART_CONFIG['escolaridade']['color'], CHART_CONFIG['escolaridade']['title']
                        )
                    )
                    st.altair_chart(escolaridade_chart, use_container_width=True)
                    st.dataframe(
                        escolaridade_df[['ESCOLARIDADE', 'count']].rename(columns={'ESCOLARIDADE': 'Escolaridade', 'count': 'Quantidade'}),
                        use_container_width=True, hide_index=True
                    )

        # 03.B Renda/Quanto poupa
        with col2:
            with st.container(border=True):
                st.subheader("Quanto poupa" if PRODUTO == "SW" else "Renda mensal")
                st.caption("Distribuição por faixa")
                renda_chart, renda_df = executar_com_seguranca(
                    "RENDA MENSAL",
                    lambda: create_distribution_chart(
                        filtered_renda, renda_coluna, col2_order,
                        CHART_CONFIG['renda']['color'], CHART_CONFIG['renda']['title']
                    )
                )
                st.altair_chart(renda_chart, use_container_width=True)
                st.dataframe(
                    renda_df[[renda_coluna, 'count']].rename(
                        columns={renda_coluna: "Quanto poupa" if PRODUTO == "SW" else "Renda mensal", 'count': 'Quantidade'}
                    ),
                    use_container_width=True, hide_index=True
                )

        st.divider()

    with tab2:
        # ------------------------------------------------------------
        # 04. HEATMAP
        # ------------------------------------------------------------
        col1, col2, col3 = st.columns([1, 7, 1])
        with col2:
            with st.container(border=True):
                st.subheader("Mapa de calor de respostas")
                st.caption("Correlação visual entre variáveis-chave da pesquisa")
                executar_com_seguranca("HEATMAP", lambda: create_heatmap(filtered_DF_PTRAFEGO_DADOS))

        st.divider()

        # ------------------------------------------------------------
        # 05. Proxy de Vendas (tabelas + exibição formatada)
        # ------------------------------------------------------------
        df_ptrafego_dados = DF_PTRAFEGO_DADOS.copy()
        df_central_vendas = DF_CENTRAL_VENDAS.copy()

        # Dummy de compra
        df_ptrafego_dados["Comprou"] = df_ptrafego_dados["EMAIL"].isin(df_central_vendas["EMAIL"]).astype(int)

        # Tabelas de leads e vendas por faixa
        tabela_leads = df_ptrafego_dados.pivot_table(
            index="RENDA MENSAL", columns="PATRIMONIO", values="EMAIL", aggfunc="count", fill_value=0
        )
        tabela_vendas = df_ptrafego_dados.pivot_table(
            index="RENDA MENSAL", columns="PATRIMONIO", values="Comprou", aggfunc="sum", fill_value=0
        )

        # Ordenação
        tabela_leads = tabela_leads.reindex(index=col2_order, columns=patrimonio_order, fill_value=0)
        tabela_vendas = tabela_vendas.reindex(index=col2_order, columns=patrimonio_order, fill_value=0)

        # Proxy de conversão
        proxy_vendas = tabela_vendas / tabela_leads
        proxy_pct = (proxy_vendas * 100).round(1)

        with st.container(border=True):
            st.subheader("Proxy de Vendas por Renda × Patrimônio")
            st.caption("Taxa de conversão (%) = vendas / leads, por faixa")
            st.dataframe(proxy_pct.T, use_container_width=True)

    with tab3:
        if 'LEADSCORE' in DF_PTRAFEGO_DADOS.columns:
            df_leadscore = filtered_DF_PTRAFEGO_DADOS['LEADSCORE'].astype(str).astype(int)
            fig = px.histogram(df_leadscore, x = 'LEADSCORE', nbins = 15, text_auto=True, title= 'Distribuição dos leadscores (qualidade geral da captação)')
            st.plotly_chart(fig)
        else:
            print()