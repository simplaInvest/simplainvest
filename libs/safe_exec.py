import streamlit as st

def executar_com_seguranca(titulo, funcao):
    with st.spinner(f"Carregando {titulo}..."):
        try:
            return funcao()
        except Exception as e:
            st.warning(f"❌ Não foi possível carregar os dados de {titulo}.")
            st.expander("Ver detalhes do erro").write(e)
            return None