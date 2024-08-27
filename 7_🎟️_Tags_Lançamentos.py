import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials



# Função para carregar a planilha e a aba 'TAGS'
def load_sheet(sheet_name, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('autorizador.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df.fillna('não informado', inplace=True)
    return df

# Inicialização do session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'df_loaded' not in st.session_state:
    st.session_state.df_loaded = False

# Perguntar qual lançamento a pessoa gostaria de analisar
st.write('Qual Lançamento você quer analisar?')

# Dropdown para selecionar o produto
produto = st.selectbox('Produto', ['EI', 'SC'])

# Dropdown para selecionar a versão
versao = st.selectbox('Versão', list(range(1, 31)))

# Botão para continuar para a análise
if st.button("Continuar para Análise"):
    lancamento = f"{produto}.{str(versao).zfill(2)}"
    spreadsheet_name = lancamento + ' - TAGS'
    
    try:
        st.session_state.df = load_sheet(spreadsheet_name, 'TAGS')
        st.session_state.df_loaded = True
        st.success("Planilha carregada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {e}")

# Se a planilha foi carregada com sucesso, calcular e exibir os resultados para todas as tags
if st.session_state.df_loaded:
    df = st.session_state.df.copy()

    # Garantir que 'TAGS' seja uma lista e tratar entradas inválidas
    df['TAGS'] = df['TAGS'].apply(lambda x: x.split(',') if isinstance(x, str) else [])

    # Definir a lista de tags
    tags_list = [
        f"pesquisa-EI{str(versao).zfill(2)}",
        f"typeform-integration-pesquisa-copy-EI{str(versao).zfill(2)}",
        "isca-MDP",
        "isca-CALCULADORA",
        f"perfil-EI{str(versao).zfill(2)}",
        "isca-MACROALOCACAO",
        f"prematricula-EI{str(versao).zfill(2)}"
    ]

    # Filtrar contatos que viraram alunos
    tag_aluno = f"aluno-EI{str(versao).zfill(2)}"
    alunos_df = df[df['TAGS'].apply(lambda tags: tag_aluno in tags)]
    total_alunos_real = len(alunos_df)

    st.write(f"Total de alunos: {total_alunos_real}")

    # Calcular e exibir os resultados para todas as tags
    resultados = []
    for tag in tags_list:
        contatos_tag = df[df['TAGS'].apply(lambda tags: tag in tags)]
        contatos_alunos = alunos_df[alunos_df['TAGS'].apply(lambda tags: tag in tags)]
        total_contatos = len(contatos_tag)
        total_alunos = len(contatos_alunos)
        taxa_conversao = (total_alunos / total_contatos) * 100 if total_contatos > 0 else 0
        porcentagem_alunos = (total_alunos / total_alunos_real) * 100 if total_alunos_real > 0 else 0
        resultados.append([tag, total_contatos, total_alunos, f"{taxa_conversao:.2f}%", f"{porcentagem_alunos:.2f}%"])

    df_resultados = pd.DataFrame(resultados, columns=['Tag', 'Total de Contatos', 'Total de Alunos', 'Taxa de Conversão', '% do total de alunos com a tag'])
    st.write("Resultados para todas as tags:")
    st.dataframe(df_resultados)
