import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    layout="wide",
    #align_items="center",
    page_title="Central de Ferramentas Simpla Invest 💎",
    page_icon="💎"
)

pages = {    
    'SETUP': [
        st.Page("1_Início.py", title="🏠 Início"),     
    ]
}

if 'sheets_loaded' in st.session_state:
    pages_after_load = {
        'ANALISES': [
            st.Page("2_Análise Geral Lançamento.py", title="📊 Análise Geral Lançamento"),
            st.Page("4_Anúncios.py", title="🔎 Anuncios"),       
            st.Page("3_Desempenho_UTMS.py", title="🌐 Desempenho UTMS")
        ]
    }   

    pages=pages_after_load    

    with st.sidebar:     
      st.header('Você escolheu o Lançamento:')
      st.header(st.session_state.lancamento)
    
  
nav = st.navigation(pages, position="sidebar")
nav.run()

