import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração da página do Streamlit
st.set_page_config(
    layout="wide",
    page_title="Análises Simpla Invest",
    page_icon="💎"
)

# Função para carregar a planilha e a aba 'TAGS'
def load_sheet(sheet_name, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/spreadsheets",
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
    spreadsheet_tags = lancamento + ' - TAGS'
    spreadsheet_central = lancamento + ' - CENTRAL DO UTM'
    spreadsheet_pesquisa = lancamento + ' - PESQUISA TRAFEGO'
    
    try:
        # Carregar planilha de tags
        st.session_state.df = load_sheet(spreadsheet_tags, 'TAGS')
        
        # Carregar planilha central do UTM
        df_captura = load_sheet(spreadsheet_central, 'CAPTURA')
        df_vendas = load_sheet(spreadsheet_central, 'VENDAS')
        
        # Carregar planilha de pesquisa de tráfego
        df_pesquisa = load_sheet(spreadsheet_pesquisa, 'DADOS')
        
        st.session_state.df_loaded = True
        st.session_state.df_captura = df_captura
        st.session_state.df_vendas = df_vendas
        st.session_state.df_pesquisa = df_pesquisa
        
        st.success("Planilhas carregadas com sucesso!")
    except Exception as e:
        st.error(f"Erro ao carregar as planilhas: {e}")

# Se as planilhas foram carregadas com sucesso, calcular e exibir os resultados para todas as tags
if st.session_state.df_loaded:
    df = st.session_state.df.copy()
    df_captura = st.session_state.df_captura
    df_vendas = st.session_state.df_vendas
    df_pesquisa = st.session_state.df_pesquisa

    # Garantir que 'TAGS' seja uma lista e tratar entradas inválidas
    df['TAGS'] = df['TAGS'].apply(lambda x: x.split(',') if isinstance(x, str) else [])

    # Verificar se as colunas 'PATRIMONIO' e 'RENDA MENSAL' existem em df_pesquisa
    if 'PATRIMONIO' in df_pesquisa.columns and 'RENDA MENSAL' in df_pesquisa.columns:
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

        # Criar uma lista de tags excluindo 'pesquisa-EI[XX]' para a análise "Sem Tags"
        tags_list_without_pesquisa = [
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

        # Definindo as categorias para PATRIMONIO e RENDA MENSAL
        categorias_patrimonio = [
            'Menos de R$5 mil', 'Entre R$5 mil e R$20 mil', 'Entre R$20 mil e R$100 mil',
            'Entre R$100 mil e R$250 mil', 'Entre R$250 mil e R$500 mil',
            'Entre R$500 mil e R$1 milhão', 'Acima de R$1 milhão'
        ]

        categorias_renda = [
            'Até R$1.500', 'Entre R$1.500 e R$2.500', 'Entre R$2.500 e R$5.000',
            'Entre R$5.000 e R$10.000', 'Entre R$10.000 e R$20.000', 'Acima de R$20.000'
        ]

        # Convertendo as colunas para categórico com a ordem especificada
        df_pesquisa['PATRIMONIO'] = pd.Categorical(df_pesquisa['PATRIMONIO'], categories=categorias_patrimonio, ordered=True)
        df_pesquisa['RENDA MENSAL'] = pd.Categorical(df_pesquisa['RENDA MENSAL'], categories=categorias_renda, ordered=True)

        resultados = []

        for tag in tags_list:
            # Filtrar contatos com a tag
            contatos_tag = df[df['TAGS'].apply(lambda tags: tag in tags)]
            alunos_tag = alunos_df[alunos_df['TAGS'].apply(lambda tags: tag in tags)]
            leads_tag = contatos_tag[~contatos_tag['TAGS'].apply(lambda tags: tag_aluno in tags)]

            # Criar tabela cruzada de leads
            tabela_cruzada_leads = pd.crosstab(df_pesquisa[df_pesquisa['EMAIL'].isin(leads_tag['EMAIL'])]['PATRIMONIO'],
                                               df_pesquisa[df_pesquisa['EMAIL'].isin(leads_tag['EMAIL'])]['RENDA MENSAL'])

            # Criar tabela cruzada de alunos
            tabela_cruzada_alunos = pd.crosstab(df_pesquisa[df_pesquisa['EMAIL'].isin(alunos_tag['EMAIL'])]['PATRIMONIO'],
                                                df_pesquisa[df_pesquisa['EMAIL'].isin(alunos_tag['EMAIL'])]['RENDA MENSAL'])

            # Empilhar as tabelas cruzadas
            tabela_empilhada_leads = tabela_cruzada_leads.stack().reset_index()
            tabela_empilhada_alunos = tabela_cruzada_alunos.stack().reset_index()

            # Renomear colunas
            tabela_empilhada_leads.columns = ['PATRIMONIO', 'RENDA MENSAL', 'LEADS']
            tabela_empilhada_alunos.columns = ['PATRIMONIO', 'RENDA MENSAL', 'ALUNOS']

            # Combinar tabelas e preencher NaNs com 0
            tabela_combined = pd.merge(tabela_empilhada_leads.astype(str), tabela_empilhada_alunos.astype(str), on=['PATRIMONIO', 'RENDA MENSAL'], how='outer').fillna('0')
            tabela_combined['LEADS'] = tabela_combined['LEADS'].astype(int)
            tabela_combined['ALUNOS'] = tabela_combined['ALUNOS'].astype(int)
            tabela_combined['CONVERSÃO'] = (tabela_combined['ALUNOS'] / tabela_combined['LEADS']) * 100
            tabela_combined['CONVERSÃO'] = tabela_combined['CONVERSÃO'].apply(lambda x: f"{x:.2f}%")

            # Adicionar resultados à lista
            resultados.append((tag, tabela_combined))

        # Calcular para pessoas que não possuem nenhuma das tags (exceto pesquisa-EI[XX])
        contatos_sem_tags = df[~df['TAGS'].apply(lambda tags: any(tag in tags for tag in tags_list_without_pesquisa + [tag_aluno]))]
        leads_sem_tags = contatos_sem_tags[~contatos_sem_tags['TAGS'].apply(lambda tags: tag_aluno in tags)]
        alunos_sem_tags = alunos_df[~alunos_df['TAGS'].apply(lambda tags: any(tag in tags for tag in tags_list_without_pesquisa))]

        # Criar tabela cruzada de leads sem tags
        tabela_cruzada_leads_sem_tags = pd.crosstab(df_pesquisa[df_pesquisa['EMAIL'].isin(leads_sem_tags['EMAIL'])]['PATRIMONIO'],
                                                    df_pesquisa[df_pesquisa['EMAIL'].isin(leads_sem_tags['EMAIL'])]['RENDA MENSAL'])

        # Criar tabela cruzada de alunos sem tags
        tabela_cruzada_alunos_sem_tags = pd.crosstab(df_pesquisa[df_pesquisa['EMAIL'].isin(alunos_sem_tags['EMAIL'])]['PATRIMONIO'],
                                                     df_pesquisa[df_pesquisa['EMAIL'].isin(alunos_sem_tags['EMAIL'])]['RENDA MENSAL'])

        # Empilhar as tabelas cruzadas
        tabela_empilhada_leads_sem_tags = tabela_cruzada_leads_sem_tags.stack().reset_index()
        tabela_empilhada_alunos_sem_tags = tabela_cruzada_alunos_sem_tags.stack().reset_index()

        # Renomear colunas
        tabela_empilhada_leads_sem_tags.columns = ['PATRIMONIO', 'RENDA MENSAL', 'LEADS']
        tabela_empilhada_alunos_sem_tags.columns = ['PATRIMONIO', 'RENDA MENSAL', 'ALUNOS']

        # Combinar tabelas e preencher NaNs com 0
        tabela_combined_sem_tags = pd.merge(tabela_empilhada_leads_sem_tags.astype(str), tabela_empilhada_alunos_sem_tags.astype(str), on=['PATRIMONIO', 'RENDA MENSAL'], how='outer').fillna('0')
        tabela_combined_sem_tags['LEADS'] = tabela_combined_sem_tags['LEADS'].astype(int)
        tabela_combined_sem_tags['ALUNOS'] = tabela_combined_sem_tags['ALUNOS'].astype(int)
        tabela_combined_sem_tags['CONVERSÃO'] = (tabela_combined_sem_tags['ALUNOS'] / tabela_combined_sem_tags['LEADS']) * 100
        tabela_combined_sem_tags['CONVERSÃO'] = tabela_combined_sem_tags['CONVERSÃO'].apply(lambda x: f"{x:.2f}%")

        resultados.append(("Sem Tags", tabela_combined_sem_tags))

        # Exibir resultados
        for tag, tabela in resultados:
            st.write(f"Resultados para a tag: {tag}")
            st.dataframe(tabela)
    else:
        st.error("As colunas 'PATRIMONIO' e 'RENDA MENSAL' não foram encontradas na planilha de pesquisa de tráfego.")
