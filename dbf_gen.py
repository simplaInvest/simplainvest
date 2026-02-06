import streamlit as st
import pandas as pd
from libs.debriefing_generator import generate_debriefing2, get_conversion_data, get_conversions_by_campaign, process_campaign_data
from libs.data_loader import K_CENTRAL_LANCAMENTOS, K_PCOPY_DADOS, get_df
from libs.auth_funcs import require_authentication

# Verificação obrigatória no início
require_authentication()

PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]
LANÇAMENTO = st.session_state["LANÇAMENTO"]

logo = "Logo-EUINVESTIDOR-Light.png" if PRODUTO == "EI" else "Logo-SIMPLA-Light.png"
st.logo(image = logo)

DF_CENTRAL_LANCAMENTOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_LANCAMENTOS)

# Nota: a página agora carrega normalmente mesmo se Copy estiver vazio;
# mensagens são exibidas apenas nas seções que dependem de DF_PCOPY_DADOS.
def convert_dates_to_iso(df, date_columns):
    """
    Converte as datas das colunas especificadas para YYYY-MM-DD.
    Aceita entradas em 'DD/MM/YYYY', 'YYYY-MM-DD' e também 'MM/DD/YYYY'.
    """
    df = df.copy()

    def _to_iso(val):
        import pandas as pd
        from datetime import datetime
        if pd.isna(val):
            return val
        s = str(val).strip()
        if not s:
            return s
        # Já ISO?
        try:
            dt = datetime.strptime(s, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
        except Exception:
            pass
        # DD/MM/YYYY
        try:
            dt = datetime.strptime(s, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except Exception:
            pass
        # MM/DD/YYYY
        try:
            dt = datetime.strptime(s, '%m/%d/%Y')
            return dt.strftime('%Y-%m-%d')
        except Exception:
            pass
        # Fallback: tentativa com pandas (dayfirst True, depois False)
        try:
            dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
            if pd.notnull(dt):
                return pd.to_datetime(dt).strftime('%Y-%m-%d')
            dt2 = pd.to_datetime(s, dayfirst=False, errors='coerce')
            if pd.notnull(dt2):
                return pd.to_datetime(dt2).strftime('%Y-%m-%d')
        except Exception:
            pass
        # Sem conversão: retorna original
        return s

    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(_to_iso)
    return df.copy()
DF_CENTRAL_LANCAMENTOS = convert_dates_to_iso(DF_CENTRAL_LANCAMENTOS, ['CAPTACAO_INICIO', 'CAPTACAO_FIM', 'PM_INICIO', 'PM_FIM', 'VENDAS_INICIO', 'VENDAS_FIM'])

st.header(f'Dados de Debriefing {PRODUTO}.{VERSAO_PRINCIPAL}')

if PRODUTO == 'EI' and VERSAO_PRINCIPAL >= 21:
    conv_traf, conv_copy, conv_wpp, lista_tabs, bar_sexo, bar_filhos, bar_civil, bar_exp, graf_age, graf_ren, graf_pat, graf_inv, disc_grafs = generate_debriefing2(PRODUTO, VERSAO_PRINCIPAL)
elif PRODUTO == 'EI':
    conv_traf, conv_copy, conv_wpp, lista_tabs, bar_sexo, bar_filhos, bar_civil, bar_exp, graf_ren, graf_pat, graf_inv, disc_grafs = generate_debriefing2(PRODUTO, VERSAO_PRINCIPAL)
elif PRODUTO == 'SC':
    conv_traf, conv_wpp, lista_tabs, graf_ren, graf_pat = generate_debriefing2(PRODUTO, VERSAO_PRINCIPAL)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Conversão da pesquisa de tráfego", value= conv_traf)

with col2:
    if PRODUTO == 'EI':
        # Mostrar metric somente se houver dados de Copy;
        # caso contrário, exibir aviso pontual.
        if bar_sexo is not None or (disc_grafs and len(disc_grafs) > 0) or graf_inv is not None:
            st.metric(label="Conversão da pesquisa de copy", value= conv_copy)
        else:
            st.info("💡 A pesquisa de copy está vazia neste lançamento.")
    elif PRODUTO == 'SC':
        st.metric(label="Conversão dos grupos de whatsapp", value= conv_wpp)

with col3:
    if PRODUTO == 'EI':
        st.metric(label="Conversão dos grupos de whatsapp", value= conv_wpp)

st.divider()

if PRODUTO == 'EI': 
    st.subheader('Anúncios')
    tab1, tab2, tab3 = st.tabs(["Captura", "Pré-matrícula", "Vendas"])

    with tab1:
        st.dataframe(lista_tabs[0][1], use_container_width = True, hide_index=True)

    with tab2:
        st.dataframe(lista_tabs[1][1], use_container_width = True, hide_index=True)

    with tab3:
        st.dataframe(lista_tabs[2][1], use_container_width = True, hide_index=True)

elif PRODUTO == 'SC':
    st.subheader('Anúncios')
    tab1, tab2 = st.tabs(["Captura", "Vendas"])

    with tab1:
        st.dataframe(lista_tabs[0][1], use_container_width = True, hide_index=True)

    with tab2:
        st.dataframe(lista_tabs[1][1], use_container_width = True, hide_index=True)

st.divider()

st.subheader("Perfis")

if PRODUTO == 'EI':

    tab_1, tab_2, tab_3 = st.tabs(["Fechadas", "Abertas", "Financeiro"])

    with tab_1:
        # Seções dependentes de Copy: exibir aviso quando Copy estiver vazio
        if bar_sexo is None and bar_filhos is None and bar_civil is None and bar_exp is None:
            st.info("💡 Sem dados da pesquisa de copy para perfis fechadas.")
        else:
            col_1, col_2 = st.columns(2)

            with col_1:
                if bar_sexo is not None:
                    st.pyplot(bar_sexo)
                if bar_filhos is not None:
                    st.pyplot(bar_filhos)
                if bar_civil is not None:
                    st.pyplot(bar_civil)
            
            with col_2:
                if bar_exp is not None:
                    st.pyplot(bar_exp)
                if PRODUTO == 'EI' and int(VERSAO_PRINCIPAL) >= 21 and graf_age is not None:
                    st.pyplot(graf_age)

    with tab_2:
        if not disc_grafs:
            st.info("💡 Sem dados da pesquisa de copy para perfis abertas.")
        else:
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
        
        with st.expander("🔍 Detalhes (Diagnóstico)"):
            st.markdown(f"**Intervalo de Datas:** {start_date_captura} até {end_date_captura}")
            st.markdown("**Visitas (Páginas Detectadas):**")
            # Recarrega dados de visitas para exibir (já que df foi sobrescrito)
            df_visitas_debug = get_conversion_data(slug = '/cursogratuito', start_date = start_date_captura, end_date = end_date_captura)
            st.dataframe(df_visitas_debug, use_container_width=True, hide_index=True)
            
            st.markdown("**Conversões (Páginas Detectadas):**")
            # O df atual já é o de conversões
            st.dataframe(df, use_container_width=True, hide_index=True)

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

        with st.expander("🔍 Detalhes (Diagnóstico)"):
            st.markdown(f"**Intervalo de Datas:** {start_date_pm} até {end_date_pm}")
            st.markdown("**Visitas (Páginas Detectadas):**")
            df_visitas_pm_debug = get_conversion_data(slug = '/ei/prematricula', start_date = start_date_pm, end_date = end_date_pm)
            st.dataframe(df_visitas_pm_debug, use_container_width=True, hide_index=True)
            
            st.markdown("**Conversões (Páginas Detectadas):**")
            st.dataframe(df, use_container_width=True, hide_index=True)

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
        df = get_conversion_data(slug = '/?X11050759S', start_date = start_date_ven, end_date = end_date_ven)
        pagina_alvo = "/?X11050759S"
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
            
        with st.expander("🔍 Detalhes (Diagnóstico)"):
            st.markdown(f"**Intervalo de Datas:** {start_date_ven} até {end_date_ven}")
            st.markdown("**Visitas (Páginas Detectadas):**")
            df_visitas_ven_debug = get_conversion_data(slug = '/euinvestidor', start_date = start_date_ven, end_date = end_date_ven)
            st.dataframe(df_visitas_ven_debug, use_container_width=True, hide_index=True)
            
            st.markdown("**Conversões (Páginas Detectadas):**")
            st.dataframe(df, use_container_width=True, hide_index=True)

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
        df = get_conversion_data(slug = 'promocao|bf-', start_date = start_date_captura, end_date = end_date_captura)
        pagina_alvo = "promocao|bf-"
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
            
        with st.expander("🔍 Detalhes (Diagnóstico)"):
            st.markdown(f"**Intervalo de Datas:** {start_date_captura} até {end_date_captura}")
            st.markdown("**Visitas (Páginas Detectadas):**")
            df_visitas_sc_debug = get_conversion_data(slug = 'promocao|bf-', start_date = start_date_captura, end_date = end_date_captura)
            st.dataframe(df_visitas_sc_debug, use_container_width=True, hide_index=True)
            
            st.markdown("**Conversões (Páginas Detectadas):**")
            st.dataframe(df, use_container_width=True, hide_index=True)

    with pag_cols[1]:
        st.subheader('Página de Vendas')

        ### Visitas
        df = get_conversion_data(slug = 'especial|blackfriday', start_date = start_date_ven, end_date = end_date_ven)
        pagina_alvo = "especial|blackfriday"
        pagina = df[df["landing_page"].str.contains(pagina_alvo, case=False)]

        if not pagina.empty:
            st.metric('Visitas', pagina['users'].sum())
            visitas_ven = pagina['users'].sum()
        else:
            st.warning("Página não encontrada nos dados.")
            visitas_ven = 0
        
        ### Conversões
        df = get_conversion_data(slug = 'oportunidade', start_date = start_date_ven, end_date = end_date_ven)
        pagina_alvo = "oportunidade"
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
            
        with st.expander("🔍 Detalhes (Diagnóstico)"):
            st.markdown(f"**Intervalo de Datas:** {start_date_ven} até {end_date_ven}")
            st.markdown("**Visitas (Páginas Detectadas):**")
            df_visitas_ven_sc_debug = get_conversion_data(slug = 'especial|blackfriday', start_date = start_date_ven, end_date = end_date_ven)
            st.dataframe(df_visitas_ven_sc_debug, use_container_width=True, hide_index=True)
            
            st.markdown("**Conversões (Páginas Detectadas):**")
            st.dataframe(df, use_container_width=True, hide_index=True)
