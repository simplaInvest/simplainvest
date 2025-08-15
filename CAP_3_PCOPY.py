import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from sklearn.feature_extraction.text import CountVectorizer

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PCOPY_DADOS, K_PTRAFEGO_DADOS, get_df
from libs.safe_exec import executar_com_seguranca
from libs.cap_copy_funcs import plot_bar_chart, graf_idade, graf_renda, graf_invest, graf_patrim, plot_confusion_matrix_renda_patrimonio, plot_top_bigrams_by_column, stopwords_portugues
from libs.auth_funcs import require_authentication

# Verificação obrigatória no início
require_authentication()

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

logo = "Logo-EUINVESTIDOR-Light.png" if PRODUTO == "EI" else "Logo-SIMPLA-Light.png"
st.logo(image = logo)

# Carregar DataFrames para lançamento selecionado
loading_container = st.empty()
with loading_container:
    status = st.status("Carregando dados...", expanded=True)
    with status:
        DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
        DF_CENTRAL_PREMATRICULA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
        DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
        DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
        DF_PCOPY_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PCOPY_DADOS)
        status.update(label="Carregados com sucesso!", state="complete", expanded=False)
loading_container.empty()

#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("CAPTAÇÃO > PESQUISA DE COPY")
st.title('Pesquisa de Copy')

#------------------------------------------------------------
#      01. FILTROS
#------------------------------------------------------------

# Data Cleaning
if 'Qual sua situação amorosa hoje?' in DF_PCOPY_DADOS:
    DF_PCOPY_DADOS['Qual sua situação amorosa hoje?'] = DF_PCOPY_DADOS['Qual sua situação amorosa hoje?'].str.lower()
    DF_PCOPY_DADOS['Qual sua situação amorosa hoje?'] = DF_PCOPY_DADOS['Qual sua situação amorosa hoje?'].replace({
        'união estável': 'união estável',
        'união estavel': 'união estável',
        'casada somente no religioso': 'casado(a)',
        'ajuntando': 'morando juntos',
        'amaseado': 'morando juntos',
        'amasiado': 'morando juntos',
        'só junto': 'morando juntos',
        'moro junto': 'morando juntos',
        'união estavel': 'união estável',
        'viúva': 'viúvo(a)',
        'viuva': 'viúvo(a)',
        'viúvo': 'viúvo(a)'
    })

if VERSAO_PRINCIPAL >= 20:
    DF_PCOPY_DADOS['Qual sua idade?'] = pd.to_numeric(DF_PCOPY_DADOS['Qual sua idade?'], errors='coerce')

gender_options = ['TODOS'] + ['Masculino', 'Feminino', 'Outro']
children_options = ['TODOS'] + list(DF_PCOPY_DADOS['Você tem filhos?'].dropna().unique())
marital_status_options = ['TODOS'] + ['solteiro(a)', 'namorando', 'casado(a)', 'divorciado(a)', 'viúvo(a)', 'outro']
investment_experience_options = [
    'TODOS',
    'Totalmente iniciante',
    'Iniciante',
    'Intermediário',
    'Profissional'
]

# Filter columns layout
col1, col2, col3, col4 = st.columns(4)

# Gender filter
gender_filter = col1.multiselect("Sexo", gender_options, default='TODOS')

# Children filter
children_filter = col2.multiselect("Filhos", children_options, default='TODOS')

# Marital Status filter
marital_status_filter = col3.multiselect("Estado civil", marital_status_options, default='TODOS')

# Investment Experience filter
investment_experience_filter = col4.multiselect(
    "Experiência",
    investment_experience_options,
    default='TODOS'
)

if int(VERSAO_PRINCIPAL) >= 20:
    # Age range slider
    age_min = int(DF_PCOPY_DADOS['Qual sua idade?'].min())
    age_max = int(DF_PCOPY_DADOS['Qual sua idade?'].max())
    age_range = st.slider("Selecione a faixa etária:", min_value=age_min, max_value=age_max, value=(age_min, age_max))

# Mesclar os dataframes com base na coluna Email
DF_PCOPY_DADOS = DF_PCOPY_DADOS.merge(DF_PTRAFEGO_DADOS[['EMAIL', 'RENDA MENSAL']], on='EMAIL', how='left')
DF_PCOPY_DADOS = DF_PCOPY_DADOS.merge(DF_PTRAFEGO_DADOS[['EMAIL', 'PATRIMONIO']], on='EMAIL', how='left')

# Filtering logic
filtered_DF_PCOPY_DADOS = DF_PCOPY_DADOS.copy()

if 'TODOS' not in gender_filter:
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[filtered_DF_PCOPY_DADOS['Qual seu sexo?'].isin(gender_filter)]

if 'TODOS' not in children_filter:
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[filtered_DF_PCOPY_DADOS['Você tem filhos?'].dropna().isin(children_filter)]

if 'TODOS' not in marital_status_filter:
    if 'Qual sua situação amorosa hoje?' in filtered_DF_PCOPY_DADOS:
        filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[filtered_DF_PCOPY_DADOS['Qual sua situação amorosa hoje?'].isin(marital_status_filter)]
    else:
        filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[filtered_DF_PCOPY_DADOS['Qual seu estado civil atual?'].isin(marital_status_filter)]

if 'TODOS' not in investment_experience_filter:
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[
        filtered_DF_PCOPY_DADOS['Se você pudesse classificar seu nível de experiência com investimentos, qual seria?']
        .str.contains('|'.join(investment_experience_filter), na=False)
    ]


if int(VERSAO_PRINCIPAL) >= 20:
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[
        (filtered_DF_PCOPY_DADOS['Qual sua idade?'] >= age_range[0]) &
        (filtered_DF_PCOPY_DADOS['Qual sua idade?'] <= age_range[1])
    ]

# Filter columns layout
colu1, colu2, colu3 = st.columns([1,1,3])
with colu1:
    with st.container(border = True):
        st.subheader('Pré-Matrícula:')
        opcao_prematricula = st.radio("Escolha uma opção", ("Todos", "Com", "Sem"))

# Aplicar o filtro de pré-matrícula se a opção estiver marcada
if opcao_prematricula == 'Todos':
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS
elif opcao_prematricula == 'Com':
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[filtered_DF_PCOPY_DADOS['EMAIL'].isin(DF_CENTRAL_PREMATRICULA['EMAIL'].str.lower())]
elif opcao_prematricula == 'Sem':
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[~filtered_DF_PCOPY_DADOS['EMAIL'].str.lower().isin(DF_CENTRAL_PREMATRICULA['EMAIL'].str.lower())]

with colu2:
    with st.container(border = True):
        st.subheader('Vendas:')
        opcao_vendas = st.radio("Escolha uma opção", ("Ambos", "Sim", "Não"))

# Aplicar o filtro de pré-matrícula se a opção estiver marcada
if opcao_vendas == 'Ambos':
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS
elif opcao_vendas == 'Sim':
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[filtered_DF_PCOPY_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower())]
elif opcao_vendas == 'Não':
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[~filtered_DF_PCOPY_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower())]

# Closed-ended response columns: categorical responses or choices
closed_ended_columns = [
    "Qual seu sexo?", 
    "Você tem filhos?", 
    "Qual sua idade?", 
    "Qual sua situação amorosa hoje?", 
    "Você já investe seu dinheiro atualmente?", 
    "RENDA MENSAL", 
    "PATRIMONIO"
]

# Open-ended response columns: free-text responses

if int(VERSAO_PRINCIPAL) >= 22:
    open_ended_columns = [
        'Porque você quer a começar a investir?',
        'Como você imagina a vida que está buscando?',
        'Quais são os principais obstáculos que te impedem de viver essa vida hoje? ',
        'Descreva, da forma que imaginar, como seria o seu dia perfeito.',
        'Se você estivesse com o Rufino agora, qual pergunta faria?'
    ]
if int(VERSAO_PRINCIPAL) == 21:
    open_ended_columns = [
        "Porque você quer a começar a investir?", 
        "Como você imagina a vida que está buscando?", 
        "Quais são os principais obstáculos que te impedem de viver essa vida hoje? ",
        "Descreva, da forma que imaginar, como seria o seu dia perfeito.",
        "Se você estivesse com o Rufino agora, qual pergunta faria?"
        ]
if int(VERSAO_PRINCIPAL) == 20:
    open_ended_columns = [
        "Por que você quer aprender a investir?", 
        "Como você imagina a vida que está buscando?", 
        "Quais são os principais obstáculos que te impedem de viver essa vida hoje? ", 
        ]
if int(VERSAO_PRINCIPAL) == 19:
    open_ended_columns = [
        'Qual é a sua maior motivação? O que te faz levantar da cama todos os dias?',
        'O que precisa acontecer para você acreditar que é uma pessoa bem-sucedida?',
        'Por que você quer aprender a investir?',
        'O que precisa acontecer na Semana do Investidor Iniciante pra você dizer que "valeu a pena"?'
        ]
if int(VERSAO_PRINCIPAL) == 18:
    open_ended_columns = [
        'Qual é a sua maior motivação? O que te faz levantar da cama todos os dias?',
        'O que precisa acontecer para você acreditar que é uma pessoa bem-sucedida?',
        'Por que você quer aprender a investir?',
        'O que precisa acontecer na Semana do Investidor Iniciante pra você dizer que "valeu a pena"?'
    ]
if int(VERSAO_PRINCIPAL) == 17:
    open_ended_columns = [
        'Qual é a sua maior motivação? O que te faz levantar da cama todos os dias?',
        'O que precisa acontecer para você acreditar que é uma pessoa bem-sucedida?',
        'Por que você quer aprender a investir?',
        'O que precisa acontecer na Semana do Investidor Iniciante pra você dizer que "valeu a pena"?'
    ]
if int(VERSAO_PRINCIPAL) == 16:
    open_ended_columns = [
        'Qual é o maior desafio que você enfrenta hoje para investir melhor o seu dinheiro?',
        'Como você imagina a sua vida se dinheiro não fosse um problema ou um limitador?',
        'Por que decidiu participar do Curso Gratuito: Invista em 4 dias?',
        'Se você tivesse uma hora para conversar pessoalmente comigo (Rufino), qual pergunta sobre investimentos, finanças ou vida, você me faria?'
    ]
###############################################################################################################################

st.divider()

total_responses = filtered_DF_PCOPY_DADOS.shape[0]

DF_PCOPY_DADOS_cleaned = filtered_DF_PCOPY_DADOS.fillna('Não Informado')
DF_PCOPY_DADOS_cleaned = DF_PCOPY_DADOS_cleaned.replace('', 'Não Informado')

# Prepare the columns for the new dataframe
variable_names = DF_PCOPY_DADOS_cleaned.columns
num_na_values = (DF_PCOPY_DADOS_cleaned == 'Não Informado').sum().reset_index()
proportion_na_values = (num_na_values[0] / total_responses * 100).round(2)

# Create the new dataframe with the required columns
missing_data_summary = pd.DataFrame({
    'Variável': variable_names,
    'Número de informações deixadas em branco': num_na_values[0],
    'Proporção em relação ao total de respostas da pesquisa': proportion_na_values
})

with st.container(border=False):
        st.markdown("<h2 style='text-align: left; font-size: 2vw; margin-bottom: 28px; color: lightblue;hover-color: red'>Métricas Gerais</h2>", unsafe_allow_html=True)
        ctcol1, ctcol2, ctcol3= st.columns([1, 1, 1])
        with ctcol1:
            st.metric("Total de leads CAPTURA:", DF_CENTRAL_CAPTURA.shape[0])
        with ctcol2:
            st.metric("Total de leads que preencheram a pesquisa de copy:", DF_PCOPY_DADOS_cleaned.shape[0])
        with ctcol3:
            st.metric("Taxa De preenchimento da pesquisa de copy", f"{round((DF_PCOPY_DADOS_cleaned.shape[0]/DF_CENTRAL_CAPTURA.shape[0])*100, 2)}%")
st.divider()

#############################################################
#      INÍCIO DO GRÁFICOS
#############################################################

st.header('Gráficos')

data = DF_PCOPY_DADOS_cleaned

# Criando as abas
tab1, tab2, tab3, tab4 = st.tabs(["Informações Pessoais", "Informações Financeiras", "Bigramas", "Respostas" ])

# Aba 1: Informações Pessoais
with tab1:
    st.subheader("Informações Pessoais")
        
    col1, col2 = st.columns(2)
    with col1:
        executar_com_seguranca("CIVIL", lambda:plot_bar_chart(
            data=data,
            var_name='Qual seu sexo?',
            classes_order=['Masculino', 'Feminino', 'Outro', 'Não Informado'],
            missing_data_summary=missing_data_summary,
            color='green'
        )
        )
        executar_com_seguranca("IDADE", lambda:plot_bar_chart(
            data=data,
            var_name='Qual sua situação amorosa hoje?',
            classes_order=['solteiro(a)', 'namorando', 'casado(a)', 'divorciado(a)', 'Não Informado'],
            missing_data_summary=missing_data_summary,
            color='green'
        )
        )
        if int(VERSAO_PRINCIPAL) >= 20:
            executar_com_seguranca("IDADE", lambda:graf_idade(data, missing_data_summary))
    with col2:
        executar_com_seguranca("EXP", lambda:plot_bar_chart(
            data=data,
            var_name='Se você pudesse classificar seu nível de experiência com investimentos, qual seria?',
            classes_order=['Totalmente Iniciante', 'Iniciante', 'Intermediário', 'Profissional', 'Não Informado'],
            missing_data_summary=missing_data_summary,
            color='green',
            rename_dict={
                'Totalmente iniciante. Não sei nem por onde começar.': 'Totalmente Iniciante',
                'Iniciante. Não entendo muito bem, mas invisto do meu jeito.': 'Iniciante',
                'Intermediário. Já invisto, até fiz outros cursos de investimentos, mas sinto que falta alguma coisa.': 'Intermediário',
                'Profissional. Já invisto e tenho ótimos resultados! Conhecimento nunca é demais!': 'Profissional'
            }
        )
        )
        if int(VERSAO_PRINCIPAL) >= 20:
            executar_com_seguranca("FILHOS", lambda:plot_bar_chart(
            data=data,
            var_name='Você tem filhos?',
            classes_order=['Sim', 'Não, mas quero ter', 'Não e nem pretendo'],
            missing_data_summary=missing_data_summary,
            color='green'
        )
        )


# Aba 2: Informações Financeiras
with tab2:
    st.subheader("Informações Financeiras")
        
    col3, col4 = st.columns(2)
    with col3:
        if int(VERSAO_PRINCIPAL) >= 20:
            executar_com_seguranca("INVEST", lambda:graf_invest(data, missing_data_summary))
            executar_com_seguranca("PATRIM", lambda:graf_patrim(data, missing_data_summary))
    with col4:
        executar_com_seguranca("RENDA", lambda:graf_renda(data, missing_data_summary))
    st.divider()
    # Colocando a matriz de confusão em uma linha separada
    st.subheader("Matriz de Confusão entre Renda e Patrimônio")
    executar_com_seguranca("MATRIX", lambda:plot_confusion_matrix_renda_patrimonio(data))

# Aba 3: Análise Textual
with tab3:
    st.subheader("Bigramas")
        
    col1, col2 = st.columns(2)
    with col1:
        executar_com_seguranca("BIGRAMA 1", lambda:plot_top_bigrams_by_column(data, open_ended_columns[:3]))
    with col2:
        executar_com_seguranca("BIGRAMA 2", lambda:plot_top_bigrams_by_column(data, open_ended_columns[3:]))
        
with tab4:
    st.subheader("Respostas")
    st.dataframe(data[open_ended_columns])

st.divider()
st.header('Dados ausentes')
st.write(missing_data_summary.set_index('Variável'))
st.divider()