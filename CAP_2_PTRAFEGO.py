import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go
import datetime

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS, K_CENTRAL_LANCAMENTOS, get_df
from libs.cap_traf_funcs import create_distribution_chart, calcular_proporcoes_e_plotar, create_heatmap
from libs.safe_exec import executar_com_seguranca
from libs.auth_funcs import require_authentication

# Verificação obrigatória no início
require_authentication()

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]
LANÇAMENTO = st.session_state["LANÇAMENTO"]

# Carregar DataFrames para lançamento selecionado
loading_container = st.empty()
with loading_container:
    status = st.status("Carregando dados...", expanded=True)
    with status:
        DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
        DF_CENTRAL_PREMATRICULA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
        DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
        DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
        DF_CENTRAL_LANCAMENTOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_LANCAMENTOS)
        status.update(label="Carregados com sucesso!", state="complete", expanded=False)
loading_container.empty()


#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("CAPTAÇÃO > PESQUISA DE TRÁFEGO")

cols_1 = st.columns(2)

with cols_1[0]:
    st.title('Pesquisa de Tráfego')

with cols_1[1]:
    filter_container = st.container()



#------------------------------------------------------------
#      01. FILTROS
#------------------------------------------------------------

# Colunas a serem filtradas
columns_to_filter = ['UTM_TERM', 'UTM_CAMPAIGN', 'UTM_SOURCE', 'UTM_MEDIUM', 'UTM_ADSET']

# Colunas financeiras
cols_finan_01 = 'PATRIMONIO'
cols_finan_02 = 'QUANTO_POUPA' if PRODUTO == "SW" else 'RENDA MENSAL'

# Criar os filtros lado a lado com session_state
filters = {}
cols_filters = st.columns(len(columns_to_filter))

## 1.A Anúncios (utm_term)
with cols_filters[0]:
    unique_terms = list(DF_PTRAFEGO_DADOS['UTM_TERM'].unique())
    unique_terms.insert(0, 'TODOS')
    if "UTM_TERM" not in st.session_state:
        st.session_state["UTM_TERM"] = ["TODOS"]
    filters['UTM_TERM'] = st.multiselect(
        "**Anúncios** *(utm_term)*",
        unique_terms,
        default=["TODOS"],
        key="UTM_TERM"
    )

## 1.B Campanhas (utm_campaign)
with cols_filters[1]:
    unique_campaigns = list(DF_PTRAFEGO_DADOS['UTM_CAMPAIGN'].unique())
    unique_campaigns.insert(0, 'TODOS')
    if "UTM_CAMPAIGN" not in st.session_state:
        st.session_state["UTM_CAMPAIGN"] = ["TODOS"]
    filters['UTM_CAMPAIGN'] = st.multiselect(
        "**Campanhas** *(utm_campaign)*",
        unique_campaigns,
        default=["TODOS"],
        key="UTM_CAMPAIGN"
    )

## 1.C Origens (utm_source)
with cols_filters[2]:
    unique_sources = list(DF_PTRAFEGO_DADOS['UTM_SOURCE'].unique())
    unique_sources.insert(0, 'TODOS')
    if "UTM_SOURCE" not in st.session_state:
        st.session_state["UTM_SOURCE"] = ["TODOS"]
    filters['UTM_SOURCE'] = st.multiselect(
        "**Origens** *(utm_source)*",
        unique_sources,
        default=["TODOS"],
        key="UTM_SOURCE"
    )

## 1.D Mídias (utm_medium)
with cols_filters[3]:
    unique_mediums = list(DF_PTRAFEGO_DADOS['UTM_MEDIUM'].unique())
    unique_mediums.insert(0, 'TODOS')
    if "UTM_MEDIUM" not in st.session_state:
        st.session_state["UTM_MEDIUM"] = ["TODOS"]
    filters['UTM_MEDIUM'] = st.multiselect(
        "**Mídias** *(utm_medium)*",
        unique_mediums,
        default=["TODOS"],
        key="UTM_MEDIUM"
    )

## 1.E Conjuntos (utm_adset)
with cols_filters[4]:
    unique_adsets = list(DF_PTRAFEGO_DADOS['UTM_ADSET'].dropna().unique())
     # Adiciona opções especiais
    if any('[LS]' in str(adset) for adset in unique_adsets):
        unique_adsets = ['TODOS', 'LEADSCORE'] + unique_adsets
    else:
        unique_adsets = ['TODOS'] + unique_adsets

    if "UTM_ADSET" not in st.session_state:
        st.session_state["UTM_ADSET"] = ["TODOS"]
    filters['UTM_ADSET'] = st.multiselect(
        "**Conjuntos** *(utm_adset)*",
        unique_adsets,
        default=["TODOS"],
        key="UTM_ADSET"
    )

#------------------------------------------------------------
#      02. RESUMO
#------------------------------------------------------------

# Filtrar os dados com base nos filtros selecionados
filtered_DF_PTRAFEGO_DADOS = DF_PTRAFEGO_DADOS.copy()

# Inicializar selected_dates como None
selected_dates = None

filtered_DF_PTRAFEGO_DADOS = DF_PTRAFEGO_DADOS.copy()

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

# Verificar se o DataFrame filtrado está vazio
if filtered_DF_PTRAFEGO_DADOS.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
else:
    st.divider()

    with filter_container:
        cols_container = st.columns(2)
        with cols_container[0]:
            options = ["Captação", "Pré-matrícula", "Vendas"]
            filters_etapas = st.multiselect(
                label="Filtros por etapa:", options=options
            )
            if filters_etapas is not None:
                if "Captação" in filters_etapas:
                    filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_CAPTURA['EMAIL'].str.lower())]
                if "Pré-matrícula" in filters_etapas:
                    filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_PREMATRICULA['EMAIL'].str.lower())]
                if "Vendas" in filters_etapas:
                    filtered_DF_PTRAFEGO_DADOS = filtered_DF_PTRAFEGO_DADOS[filtered_DF_PTRAFEGO_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower())]
        
        with cols_container[1]:
            # 02.B: MÉTRICAS PRINCIPAIS
            st.metric(
                label="Respostas da pesquisa:",
                value=f"{filtered_DF_PTRAFEGO_DADOS.shape[0]}  ({round((filtered_DF_PTRAFEGO_DADOS.shape[0] / DF_CENTRAL_CAPTURA.shape[0]) * 100, 2)}%)"
            )

    # 02.A: FILTROS POR ETAPA
    cols_resumo = st.columns(3)
    
    # 02.C: MÉTRICAS PRINCIPAIS
    patrimonio_order = [
            'Menos de R$5 mil',
            'Entre R$5 mil e R$20 mil',
            'Entre R$20 mil e R$100 mil',
            'Entre R$100 mil e R$250 mil',
            'Entre R$250 mil e R$500 mil',
            'Entre R$500 mil e R$1 milhão',
            'Acima de R$1 milhão'
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
    if PRODUTO == "EI" or PRODUTO == "SW":
        def criar_slider(order, nome_da_var,):
            return st.select_slider(
                    f'Selecione as faixas de {nome_da_var}',
                    options= order,
                    value= (order[3], order[-1]) if order == patrimonio_order else (order[2], order[-1]) # Define o valor inicial e final como padrão
                )
    if PRODUTO == "SC":
        def criar_slider(order, nome_da_var,):
            return st.select_slider(
                    f'Selecione as faixas de {nome_da_var}',
                    options= order,
                    value= (order[1], order[-1]) if order == patrimonio_order else (order[2], order[-1]) # Define o valor inicial e final como padrão
                )
        
    with cols_resumo[0]:
        with st.container(border = True):
            st.markdown("**Filtro por Data de Captura**")
            # Remover NaT e pegar min/max das datas válidas
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
                            selected_dates[0],
                            selected_dates[1]
                        )
                    ]
            else:
                st.warning("Não há datas válidas disponíveis para filtrar.")
                selected_dates = None

    with cols_resumo[1]:
        with st.container(border = True):
            selected_patrimonio_start, selected_patrimonio_end = criar_slider(patrimonio_order, 'Patrimônio')

            patrimonio_acima_selecionado = filtered_DF_PTRAFEGO_DADOS[
                filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].isin(
                    patrimonio_order[patrimonio_order.index(selected_patrimonio_start) : patrimonio_order.index(selected_patrimonio_end) + 1]
                )
            ]

    with cols_resumo[2]:
        with st.container(border = True):
            selected_renda_start, selected_renda_end = criar_slider(col2_order, f'{cols_finan_02}')

            renda_acima_selecionado = filtered_DF_PTRAFEGO_DADOS[
                (filtered_DF_PTRAFEGO_DADOS[cols_finan_02].isin(
                    col2_order[col2_order.index(selected_renda_start) : col2_order.index(selected_renda_end) + 1]
                ))
            ]

    renda_patrimonio_acima_selecionado = filtered_DF_PTRAFEGO_DADOS[
        (filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].isin(
            patrimonio_order[patrimonio_order.index(selected_patrimonio_start) : patrimonio_order.index(selected_patrimonio_end) + 1]
        )) &
        (filtered_DF_PTRAFEGO_DADOS[cols_finan_02].isin(
            col2_order[col2_order.index(selected_renda_start) : col2_order.index(selected_renda_end) + 1]
        ))
    ]

with st.container(border = True):
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        df_unido = pd.concat([patrimonio_acima_selecionado, renda_acima_selecionado])
        df_unido = df_unido[~df_unido.index.duplicated(keep='first')]
        st.metric(
            label=f'TOTAL DE PESQUISAS',
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
                label=f'{cols_finan_01} e {cols_finan_02}:',
                value=f"{renda_patrimonio_acima_selecionado.shape[0]}  "
                        f"({round((renda_patrimonio_acima_selecionado.shape[0] / filtered_DF_PTRAFEGO_DADOS.shape[0]) * 100, 2) if filtered_DF_PTRAFEGO_DADOS.shape[0] != 0 else 0}%)"
            )

st.divider()

#------------------------------------------------------------
#      03. GRÁFICOS DE BARRAS & DATAFRAME
#------------------------------------------------------------

secondary_order = col2_order

# CONFIGURAÇÕES DOS GRÁFICOS
CHART_CONFIG = {
    'patrimonio': {
        'column': 'PATRIMONIO',
        'color': 'lightblue',
        'title': '',
        'display_name': 'Patrimônio'
    },
    'renda': {
        'column': cols_finan_02,
        'color': 'lightgreen',
        'title': '',
        'display_name': 'Renda' if PRODUTO == "SW" else 'Quanto poupa'
    }
}

#  Filtrando dados com base nos valores permitidos
filtered_patrimonio = filtered_DF_PTRAFEGO_DADOS[
    filtered_DF_PTRAFEGO_DADOS['PATRIMONIO'].isin(patrimonio_order)
]

renda_coluna = 'QUANTO POUPA' if PRODUTO == 'SW' else 'RENDA MENSAL'
filtered_renda = filtered_DF_PTRAFEGO_DADOS[
    filtered_DF_PTRAFEGO_DADOS[renda_coluna].isin(col2_order)
]

col1, col2 = st.columns(2)

# 03.A: PATRIMÔNIO
with col1:
    st.subheader("Patrimônio")
    patrimonio_chart, patrimonio_df = executar_com_seguranca("PATRIMÔNIO", lambda: create_distribution_chart(
        filtered_patrimonio,
        'PATRIMONIO',
        patrimonio_order,
        CHART_CONFIG['patrimonio']['color'],
        CHART_CONFIG['patrimonio']['title']
    ))
    st.altair_chart(patrimonio_chart)
    st.dataframe(
        patrimonio_df[['PATRIMONIO', 'count']].rename(
            columns={'PATRIMONIO': 'Patrimônio', 'count': 'Quantidade'}
        ),
        use_container_width=True,
        hide_index=True
    )

# 03.B: RENDA MENSAL
with col2:
    st.subheader("Quanto poupa" if PRODUTO == "SW" else "Renda mensal")
    renda_chart, renda_df = executar_com_seguranca("RENDA MENSAL", lambda: create_distribution_chart(
        filtered_renda,
        renda_coluna,
        col2_order,
        CHART_CONFIG['renda']['color'],
        CHART_CONFIG['renda']['title']
    ))
    st.altair_chart(renda_chart)
    st.dataframe(
        renda_df[[renda_coluna, 'count']].rename(
            columns={renda_coluna: "Quanto poupa" if PRODUTO == "SW" else "Renda mensal", 'count': 'Quantidade'}
        ),
        use_container_width=True,
        hide_index=True
    )

st.divider()


# if VERSAO_PRINCIPAL >= 21:
#     col1, col2 = st.columns(2)

#     with col1:
#         with st.container(border=True):
#             executar_com_seguranca("PATRIMÔNIO", lambda:calcular_proporcoes_e_plotar(DF_PTRAFEGO_DADOS, 'PATRIMONIO', patrimonio_order))

#     with col2:
#         with st.container(border=True):
#             executar_com_seguranca("RENDA MENSAL", lambda:calcular_proporcoes_e_plotar(DF_PTRAFEGO_DADOS, cols_finan_02, secondary_order))



#------------------------------------------------------------
#      04. HEATMAP
#------------------------------------------------------------

col1, col2, col3 = st.columns([1,7,1])

with col2:
    executar_com_seguranca("HEATMAP", lambda:create_heatmap(filtered_DF_PTRAFEGO_DADOS))

st.divider()


df_ptrafego_dados = DF_PTRAFEGO_DADOS.copy()
df_central_vendas = DF_CENTRAL_VENDAS.copy()

# Criar a dummy indicando se o lead comprou (1) ou não (0)
df_ptrafego_dados["Comprou"] = df_ptrafego_dados["EMAIL"].isin(df_central_vendas["EMAIL"]).astype(int)


# Criar a tabela de total de leads capturados por faixa de renda e patrimônio
tabela_leads = df_ptrafego_dados.pivot_table(
    index="RENDA MENSAL",
    columns="PATRIMONIO",
    values="EMAIL",
    aggfunc="count",
    fill_value=0
)

# Criar a tabela de total de vendas por faixa de renda e patrimônio
tabela_vendas = df_ptrafego_dados.pivot_table(
    index="RENDA MENSAL",
    columns="PATRIMONIO",
    values="Comprou",
    aggfunc="sum",
    fill_value=0
)

# Reindexar as tabelas para garantir a ordem correta das faixas
tabela_leads = tabela_leads.reindex(index=col2_order, columns=patrimonio_order, fill_value=0)
tabela_vendas = tabela_vendas.reindex(index=col2_order, columns=patrimonio_order, fill_value=0)

# Calcular a proxy de vendas (taxa de conversão)
proxy_vendas = tabela_vendas / tabela_leads

(proxy_vendas*100).T

