import streamlit as st
import pandas as pd
from libs.debriefing_generator import generate_debriefing2, get_conversion_data, get_conversions_by_campaign, process_campaign_data
from libs.data_loader import K_CENTRAL_LANCAMENTOS, get_df

PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]
LANÇAMENTO = st.session_state["LANÇAMENTO"]

DF_CENTRAL_LANCAMENTOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_LANCAMENTOS)
def convert_dates_to_iso(df, date_columns):
    """
    Converte as datas das colunas especificadas no DataFrame do formato DD/MM/YYYY para YYYY-MM-DD.
    
    Parâmetros:
        df (pd.DataFrame): DataFrame com datas no formato DD/MM/YYYY.
        date_columns (list): Lista dos nomes das colunas que devem ser convertidas.
        
    Retorna:
        pd.DataFrame: Cópia do DataFrame com as datas convertidas para o formato ISO.
    """
    df = df.copy()
    for col in date_columns:
        try:
            # Converter a coluna utilizando o formato conhecido e formatar como string com YYYY-MM-DD
            df[col] = pd.to_datetime(df[col], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Erro ao converter a coluna {col}: {e}")
    return df.copy()
DF_CENTRAL_LANCAMENTOS = convert_dates_to_iso(DF_CENTRAL_LANCAMENTOS, ['CAPTACAO_INICIO', 'CAPTACAO_FIM', 'PM_INICIO', 'PM_FIM', 'VENDAS_INICIO', 'VENDAS_FIM'])

st.header(f'Dados de Debriefing {PRODUTO}.{VERSAO_PRINCIPAL}')

if PRODUTO == 'EI' and int(VERSAO_PRINCIPAL) >= 21:
    conv_traf, conv_copy, conv_wpp, lista_tabs, bar_sexo, bar_filhos, bar_civil, bar_exp, graf_age, graf_ren, graf_pat, graf_inv, disc_grafs = generate_debriefing2(PRODUTO, VERSAO_PRINCIPAL)
if PRODUTO == 'EI':
    conv_traf, conv_copy, conv_wpp, lista_tabs, bar_sexo, bar_filhos, bar_civil, bar_exp, graf_ren, graf_pat, graf_inv, disc_grafs = generate_debriefing2(PRODUTO, VERSAO_PRINCIPAL)
if PRODUTO == 'SC':
    conv_traf, conv_wpp, lista_tabs, graf_ren, graf_pat = generate_debriefing2(PRODUTO, VERSAO_PRINCIPAL)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Conversão da pesquisa de tráfego")
    st.metric(label="", value= conv_traf)

with col2:
    if PRODUTO == 'EI':
        st.subheader("Conversão da pesquisa de copy")
        st.metric(label="", value= conv_copy)

with col3:
    st.subheader("Conversão dos grupos de whatsapp")
    st.metric(label="", value= conv_wpp)

st.divider()

st.subheader('Anúncios')
tab1, tab2, tab3 = st.tabs(["Captura", "Pré-matrícula", "Vendas"])

with tab1:
    st.dataframe(lista_tabs[0][1], use_container_width = True, hide_index=True)

with tab2:
    st.dataframe(lista_tabs[1][1], use_container_width = True, hide_index=True)

with tab3:
    st.dataframe(lista_tabs[2][1], use_container_width = True, hide_index=True)

st.divider()

st.subheader("Perfis")

if PRODUTO == 'EI':

    tab_1, tab_2, tab_3 = st.tabs(["Fechadas", "Abertas", "Financeiro"])

    with tab_1:

        col_1, col_2 = st.columns(2)

        with col_1:
            bar_sexo
            bar_filhos
            bar_civil
        
        with col_2:
            bar_exp
            if PRODUTO == 'EI' and int(VERSAO_PRINCIPAL) >= 21:
                graf_age

    with tab_2:
        # Dividir a lista disc_grafs em duas metades
        metade = len(disc_grafs) // 2
        primeira_metade = disc_grafs[:metade]
        segunda_metade = disc_grafs[metade:]

        # Criar duas colunas no Streamlit
        col1, col2 = st.columns(2)

        # Exibir a primeira metade na primeira coluna
        with col1:
            for grafico in primeira_metade:
                st.pyplot(grafico)

        # Exibir a segunda metade na segunda coluna
        with col2:
            for grafico in segunda_metade:
                st.pyplot(grafico)

    with tab_3:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Renda")
            graf_ren
        
        with col2:
            st.subheader("Patrimônio")
            graf_pat

if PRODUTO == 'SC':
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Renda")
        graf_ren
    
    with col2:
        st.subheader("Patrimônio")
        graf_pat

st.divider()

st.header('Analytics')

if PRODUTO == 'EI':

    pag_cols = st.columns(3)
    start_date_captura = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO]['CAPTACAO_INICIO'].values[0]
    end_date_captura = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO]['CAPTACAO_FIM'].values[0]

    start_date_pm = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO]['PM_INICIO'].values[0]
    end_date_pm = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO]['PM_FIM'].values[0]

    start_date_ven = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO]['VENDAS_INICIO'].values[0]
    end_date_ven = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO]['VENDAS_FIM'].values[0]

    with pag_cols[0]:
        st.subheader('Página de Captura')

        ### Visitas 
        df = get_conversion_data(slug = '/cursogratuito', start_date = start_date_captura, end_date = end_date_captura)
        pagina_alvo = "/cursogratuito"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Visitas', pagina['users'].sum())
            visitas_cap = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            visitas_cap = 0

        ### Conversões
        df = get_conversion_data(slug = '/cg/inscricao-pendente', start_date = start_date_captura, end_date = end_date_captura)
        pagina_alvo = "/cg/inscricao-pendente"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Conversões', pagina['users'].sum())
            conv_cap = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            conv_cap = 0
        
        ### Tx. de conversão
        if not visitas_cap == 0:
            tx_cap = f'{round((conv_cap/visitas_cap)*100, 2)}%'
            st.metric('Taxa de conversão', tx_cap)

        df, df_conversoes, df_visitas = get_conversions_by_campaign(conversion_slug="/cg/inscricao-pendente", start_date = start_date_captura, end_date = end_date_captura)
        
        df_processado = process_campaign_data(df, versao_principal=VERSAO_PRINCIPAL)
        
    with pag_cols[1]:
        st.subheader('Página de Pré-Matrícula')

        ### Visitas
        df = get_conversion_data(slug = '/ei/prematricula', start_date = start_date_pm, end_date = end_date_pm)
        pagina_alvo = "/ei/prematricula"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Visitas', pagina['users'].sum())
            visitas_pm = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            visitas_pm = 0
        
        ### Conversões
        df = get_conversion_data(slug = '/parabens-ei', start_date = start_date_pm, end_date = end_date_pm)
        pagina_alvo = "/parabens-ei"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Conversões', pagina['users'].sum())
            conv_pm = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            conv_pm = 0
        
        ### Tx. de conversão
        if not visitas_pm == 0:
            tx_pm = f'{round((conv_pm/visitas_pm)*100, 2)}%'
            st.metric('Taxa de conversão', tx_pm)

    with pag_cols[2]:
        st.subheader('Página de Vendas')

        ### Visitas
        df = get_conversion_data(slug = '/euinvestidor', start_date = start_date_ven, end_date = end_date_ven)
        pagina_alvo = "/euinvestidor"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Visitas', pagina['users'].sum())
            visitas_ven = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            visitas_ven = 0
        
        ### Conversões
        df = get_conversion_data(slug = 'X11050759S', start_date = start_date_ven, end_date = end_date_ven)
        pagina_alvo = "X11050759S"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Conversões', pagina['users'].sum())
            conv_ven = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            conv_ven = 0
        
        ### Tx. de conversão
        if not visitas_ven == 0:
            tx_ven = f'{round((conv_ven/visitas_ven)*100, 2)}%'
            st.metric('Taxa de conversão', tx_ven)

    metrics_cols = st.columns([2,3])

    with metrics_cols[0]:
        st.subheader('Números de leads convertidos e taxa de conversão por campanha')
        st.dataframe(data= df_processado, use_container_width=True, hide_index=True)

    df = pd.DataFrame()


if PRODUTO == 'SC':
    pag_cols = st.columns(2)

    start_date_captura = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO]['CAPTACAO_INICIO'].values[0]
    end_date_captura = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO]['CAPTACAO_FIM'].values[0]

    start_date_ven = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO]['VENDAS_INICIO'].values[0]
    end_date_ven = DF_CENTRAL_LANCAMENTOS[DF_CENTRAL_LANCAMENTOS['LANÇAMENTO'] == LANÇAMENTO]['VENDAS_FIM'].values[0]

    with pag_cols[0]:
        st.subheader('Página de Captura')

        ### Visitas
        df = get_conversion_data(slug = '/promocao', start_date = start_date_captura, end_date = end_date_captura)
        pagina_alvo = "/promocao"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Visitas', pagina['users'].sum())
            visitas_cap = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            visitas_cap = 0

        ### Conversões
        df = get_conversion_data(slug = '/inscricao-pendente', start_date = start_date_captura, end_date = end_date_captura)
        pagina_alvo = "/inscricao-pendente"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Conversões', pagina['users'].sum())
            conv_cap = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            conv_cap = 0
        
        ### Tx. de conversão
        if visitas_cap != 0:
            tx_cap = f'{round((conv_cap/visitas_cap)*100, 2)}%'
            st.metric('Taxa de conversão', tx_cap)

    with pag_cols[1]:
        st.subheader('Página de Vendas')

        ### Visitas
        df = get_conversion_data(slug = '/especial', start_date = start_date_ven, end_date = end_date_ven)
        pagina_alvo = "/especial"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Visitas', pagina['users'].sum())
            visitas_ven = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            visitas_ven = 0
        
        ### Conversões
        df = get_conversion_data(slug = '/oportunidade-wealth',start_date = start_date_ven, end_date = end_date_ven)
        pagina_alvo = "/oportunidade-wealth"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Conversões', pagina['users'].sum())
            conv_ven = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            conv_ven = 0
        
        ### Tx. de conversão
        if not visitas_ven == 0:
            tx_ven = f'{round((conv_ven/visitas_ven)*100, 2)}%'
            st.metric('Taxa de conversão', tx_ven)