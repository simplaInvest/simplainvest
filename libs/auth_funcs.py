import streamlit as st

def require_authentication():
    """
    Verifica se o usuário está autenticado.
    Se não estiver, redireciona para a página de login.
    """
    if not st.session_state.get("authenticated", False):
        st.error("🔒 Você precisa fazer login para acessar esta página.")
        st.info("👈 Use a navegação lateral para voltar ao início e fazer login.")
        st.stop()
    
    return True

def get_current_user():
    """
    Retorna informações do usuário atual
    """
    return {
        "authenticated": st.session_state.get("authenticated", False)
    }

def is_authenticated():
    """
    Verifica se o usuário está autenticado (função simples)
    """
    return st.session_state.get("authenticated", False)