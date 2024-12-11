import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    layout="wide",
    page_title="Central de Ferramentas Simpla Invest 💎",
    page_icon="💎"
)

# Adicionar informações no topo da sidebar
with st.sidebar:
    if 'lancamento' in st.session_state:
        st.header('Você escolheu o Lançamento:')
        st.header(st.session_state.lancamento)

# Definir as páginas
pages = {
    'SETUP': [
        st.Page("1_Início.py", title="🏠 Início"),
    ]
}

if 'sheets_loaded' in st.session_state:
    pages_after_load = {
        'ANALISES': [
            st.Page("Captação - Visão Geral", title = "📊 Captação - Visão Geral"),
            st.Page("trafego.py", title = "🔎 Pesquisa de Tráfego"),
            st.Page("copy_1.py", title = "👤 Pesquisa de Copy"),
            st.Page("whatsapp.py", title = "📞 Grupos de Whatsapp"),
            st.Page("prematricula.py", title = "✅ Pré-Matrícula"),
            st.Page("vendas.py", title = "💸 Central de Vendas"),
            st.Page("2_Análise Geral Lançamento.py", title=" Análise Geral Lançamento"),
            st.Page("4_Anúncios.py", title="Anuncios"),
            st.Page("3_Desempenho_UTMS.py", title="Desempenho UTMS"),
            st.Page("5_General_Message_analyzer.py", title="Message Analyzer"),
            st.Page("98_Tester.py", title="anunciosss"),
            st.Page("6_Analise_Dinamica.py", title="Análise dinâmica")
        ]
    }
    pages = pages_after_load

# Configurar a navegação
nav = st.navigation(pages, position="sidebar")
nav.run()
