import streamlit as st, pathlib
from datetime import datetime
import hashlib

# Configuração inicial da página (DEVE ser a primeira chamada Streamlit)
st.set_page_config(
    layout="wide",
    page_title="Central de Ferramentas Simpla Invest 💎",
    page_icon="💎"
)

# Carrega CSS
css = pathlib.Path("styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def check_authentication():
    """Verifica se o usuário está autenticado"""
    # Verifica parâmetros da URL para autenticação automática
    params = st.query_params
    auth = params.get("auth", None)
    page = params.get("page", None)
    
    if auth and "authenticated" not in st.session_state:
        # Carrega as senhas do secrets.toml
        try:
            # Acessa a seção passwords do secrets.toml
            passwords_section = st.secrets["passwords"]
            passwords_list = passwords_section["passwords"]
            
            if auth in passwords_list:
                st.session_state.authenticated = True
                
                # Redireciona se a página for passada na URL
                if page:
                    page_mapping = {
                        "inicio": "0_Inicio.py",
                        "visao_geral": "CAP_1_VISAOGERAL.py",
                        "trafego": "CAP_2_PTRAFEGO.py",
                        "copy": "CAP_3_PCOPY.py",
                        "whatsapp": "CAP_4_GRUPOS_WPP.py",
                        "anuncios": "CAP_5_ANUNCIOS.py",
                        "message_analyzer": "5_General_Message_analyzer.py",
                        "pre_matricula": "PM_1_VISAOGERAL.py",
                        "vendas": "VENDAS_1_VISAOGERAL.py",
                        "evolucao": "ETC_EVOLUCAO.py",
                        "debriefing": "dbf_gen.py"
                    }
                    
                    if page in page_mapping:
                        try:
                            st.switch_page(page_mapping[page])
                        except Exception as e:
                            st.warning(f"Não foi possível acessar a página '{page}'. Redirecionando para o início.")
                            st.switch_page("0_Inicio.py")
                    else:
                        st.warning(f"Página '{page}' não encontrada. Redirecionando para o início.")
                        st.switch_page("0_Inicio.py")
                    
                return True
        except Exception as e:
            st.error("Erro ao carregar configurações de login")
    
    return st.session_state.get("authenticated", False)

def show_login_form():
    """Exibe o formulário de login"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>💎 Central de Ferramentas Simpla Invest</h1>
        <p style="font-size: 1.2em; color: #666;">Digite a senha para acessar o dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Criar colunas para centralizar o formulário
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("### 🔐 Acesso")
            
            password = st.text_input("🔑 Senha", type="password", placeholder="Digite a senha de acesso")
            
            submit_button = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit_button:
                if authenticate_password(password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")

def authenticate_password(password):
    """Autentica o usuário com base na senha"""
    try:
        # Acessa a seção passwords do secrets.toml
        passwords_section = st.secrets["passwords"]
        passwords_list = passwords_section["passwords"]
        
        # Verifica se a senha está na lista de senhas válidas
        if password in passwords_list:
            return True
                
    except KeyError as e:
        st.error(f"Configurações de senha não encontradas: {str(e)}. Verifique o arquivo secrets.toml")
    except Exception as e:
        st.error(f"Erro na autenticação: {str(e)}")
    
    return False

def show_logout_button():
    """Exibe botão de logout na sidebar"""
    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("👤 **Usuário logado**")
        
        with col2:
            if st.button("🚪", help="Logout", use_container_width=True):
                # Limpa todas as variáveis de sessão relacionadas à autenticação
                if "authenticated" in st.session_state:
                    del st.session_state["authenticated"]
                st.rerun()

# VERIFICAÇÃO DE AUTENTICAÇÃO
if not check_authentication():
    show_login_form()
    st.stop()

# RESTO DO CÓDIGO ORIGINAL (após autenticação bem-sucedida)

## PÁGINA DE SETUP
if not "PRODUTO" in st.session_state and not "VERSAO_PRINCIPAL" in st.session_state:
    # Removemos a chamada duplicada de st.set_page_config aqui
    pages = {
        'CONFIGURAÇÕES': [
            st.Page("0_Inicio.py", title="🏠 Início"),
        ]
    }
## PÁGINAS DE ANÁLISES
else:
    # Apenas reconfigura o layout para wide se necessário, mas st.set_page_config só pode ser chamado uma vez.
    # Como já foi chamado no início como "centered", não podemos mudar para "wide" dinamicamente no mesmo script sem rerun.
    # O Streamlit não permite chamar set_page_config duas vezes.
    # Solução: Definir layout="wide" no início como padrão, ou aceitar que a troca exige recarregamento.
    # Neste caso, vamos manter a configuração inicial única e adaptar o CSS se preciso, ou aceitar que será wide para tudo.
    
    # Para corrigir o erro imediato, removemos a segunda chamada:
    pass 
    
    # Adiciona botão de logout
    show_logout_button()
    
    with st.sidebar:
        st.text("Lançamento selecionado:")
        lancamento_cod = st.session_state["PRODUTO"] + ' - ' + str(st.session_state["VERSAO_PRINCIPAL"])
        with st.expander(lancamento_cod):
            opcoes = ["Eu Investidor", "Simpla Club", "Simpla Wealth"]
            default_opcao = 0 if st.session_state["PRODUTO"] == 'EI' else 1 if st.session_state["PRODUTO"] == 'SC' else 2
            PRODUTO = st.radio(
                "Produto", 
                opcoes,
                index=default_opcao
            )
            options = list(reversed(range(1, 36)))
            index = options.index(st.session_state["VERSAO_PRINCIPAL"])
            VERSAO_PRINCIPAL = st.selectbox('Versão', options, index=index)
            if st.button('Alterar', use_container_width=True):
                if PRODUTO is not None and VERSAO_PRINCIPAL is not None:
                    if PRODUTO == "Eu Investidor":
                        st.session_state["PRODUTO"] = "EI"
                    elif PRODUTO == "Simpla Club":
                        st.session_state["PRODUTO"] = "SC"
                    elif PRODUTO == "Simpla Wealth":
                        st.session_state["PRODUTO"] = "SW"
                    st.session_state["VERSAO_PRINCIPAL"] = VERSAO_PRINCIPAL
                    if "PRODUTO" in st.session_state and "VERSAO_PRINCIPAL" in st.session_state:
                        if st.session_state["PRODUTO"] == 'EI':
                            st.session_state["LANÇAMENTO"] = f"EI{VERSAO_PRINCIPAL}"
                        elif st.session_state["PRODUTO"] == 'SC':
                            st.session_state["LANÇAMENTO"] = f"SC{VERSAO_PRINCIPAL}"
                        else:
                            st.session_state["LANÇAMENTO"] = f"SW{VERSAO_PRINCIPAL}"
                        PRODUTO = st.session_state["PRODUTO"]
                        VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]
                st.rerun()

    pages_after_load = {
        'INÍCIO': [
            st.Page("dummy_snippets.py", title="🏠 Início"),
        ],
        'CAPTAÇÃO': (
            [
                st.Page("CAP_1_VISAOGERAL.py", title="📊 Visão Geral"),
                st.Page("CAP_2_PTRAFEGO.py", title="💲 Pesquisa de Tráfego")
            ]
            + ([st.Page("CAP_3_PCOPY.py", title="🧑 Pesquisa de Copy")] if st.session_state["PRODUTO"] == 'EI' else [])
            + [
                st.Page("CAP_4_GRUPOS_WPP.py", title="📞 Grupos de Whatsapp"),
                st.Page("CAP_5_ANUNCIOS.py", title="📲 Anúncios"),
                st.Page("5_General_Message_analyzer.py", title="💬 Message Analyser")
            ]
        ),
        **({"PRÉ-MATRÍCULA": [st.Page("PM_1_VISAOGERAL.py", title="⭐ Visão Geral")]} if st.session_state["PRODUTO"] == 'EI' else {}),
        'VENDAS': [
            st.Page("VENDAS_1_VISAOGERAL.py", title="💵 Visão geral"),
        ],
        'GERAL': [
            st.Page("ETC_EVOLUCAO.py", title="🎯 Comparação de Lançamentos"),
            st.Page("dbf_gen.py", title="🔮 Gerador de Debriefing")
        ]
    }

    pages = pages_after_load

# Configurar a navegação
nav = st.navigation(pages, position="sidebar")
nav.run()