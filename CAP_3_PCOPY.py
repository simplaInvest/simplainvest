import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import re
from sklearn.feature_extraction.text import CountVectorizer

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PCOPY_DADOS, K_PTRAFEGO_DADOS, get_df

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

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

prematricula_filter = st.checkbox("Pré-matrícula")

# Aplicar o filtro de pré-matrícula se a opção estiver marcada
if prematricula_filter:
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[filtered_DF_PCOPY_DADOS['EMAIL'].isin(DF_CENTRAL_PREMATRICULA['EMAIL'].str.lower())]

vendas_filter = st.checkbox("Venda")

# Aplicar o filtro de pré-matrícula se a opção estiver marcada
if vendas_filter:
    filtered_DF_PCOPY_DADOS = filtered_DF_PCOPY_DADOS[filtered_DF_PCOPY_DADOS['EMAIL'].isin(DF_CENTRAL_VENDAS['EMAIL'].str.lower())]

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

st.header('Dados ausentes')
st.write(missing_data_summary.set_index('Variável'))
st.divider()
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

st.header('Gráficos')

data = DF_PCOPY_DADOS_cleaned

def graf_sexo():
    var = 'Qual seu sexo?'
    classes_order = ['Masculino',
                     'Feminino',
                     'Outro',
                     'Não Informado'
                     ]
    cor = 'green'
    titulo = f'{var}'

    # Contagem dos valores e reindexação para garantir a ordem
    variavel_data = data[var].value_counts().reindex(classes_order)
    total_respostas = variavel_data.sum()  # Total para calcular a proporção

    # Criando o gráfico
    plt.figure(figsize=(10, 5))
    ax = variavel_data.plot(kind='bar', color=cor, width=0.6, edgecolor='black')

    # Adicionando os valores e porcentagens no topo de cada barra
    for p in ax.patches:
        count = int(p.get_height())
        perc = (count / total_respostas) * 100  # Cálculo da porcentagem
        ax.annotate(f"{count} ({perc:.1f}%)", (p.get_x() + p.get_width() / 2, p.get_height()), ha='center', va='bottom')

    # Adicionando título e rótulos
    plt.title(titulo, fontsize=14)
    plt.xlabel('Classe', fontsize=12)
    plt.ylabel('Contagem', fontsize=12)

    # Rotacionando os rótulos do eixo x
    plt.xticks(rotation=0, ha='right')

    # Exibindo o gráfico
    plt.tight_layout()
    st.pyplot(plt)

if int(VERSAO_PRINCIPAL) >= 20:
    def graf_idade():
        # Convertendo para valores numéricos, substituindo não numéricos por NaN
        data['Qual sua idade?'] = pd.to_numeric(data['Qual sua idade?'], errors='coerce')
        
        # Removendo valores NaN
        idade_data = data['Qual sua idade?'].dropna()
        # Definindo o intervalo de idades e criando os bins que começam em 0 com intervalos de 5 anos
        idade_max = data['Qual sua idade?'].max()
        bins = np.arange(0, idade_max + 5, 5)

        # Calculando média e desvio-padrão
        media_idade = data['Qual sua idade?'].mean()
        desvio_padrao = data['Qual sua idade?'].std()

        # Plotando o histograma com os novos bins
        plt.figure(figsize=(15, 6))
        counts, edges, _ = plt.hist(data['Qual sua idade?'], bins=bins, color='green', edgecolor='black')

        # Adicionando o valor de cada bin no topo de cada barra
        for i in range(len(counts)):
            plt.text((edges[i] + edges[i+1]) / 2, counts[i] + 1, f"{int(counts[i])}", ha='center', va='bottom')

        # Ajustando as marcas do eixo x para que correspondam aos intervalos de 5 anos
        plt.xticks(bins, rotation=0)

        # Adicionando título, legenda e rótulos
        plt.title('Distribuição da Idade dos Respondentes')
        plt.xlabel('Idade')
        plt.ylabel('Frequência')
        plt.legend()

        # Exibindo o gráfico com valores de média e desvio-padrão no eixo x
        st.pyplot(plt)

def graf_filhos():
    var = 'Você tem filhos?'
    classes_order = ['Sim',
                     'Não, mas quero ter',
                     'Não e nem pretendo'
                     ]
    cor = 'green'
    titulo = f'{var}'

    # Contagem dos valores e reindexação para garantir a ordem
    variavel_data = data[var].dropna().value_counts().reindex(classes_order)
    total_respostas = variavel_data.sum()  # Total para calcular a proporção

    # Criando o gráfico
    plt.figure(figsize=(10, 5))
    ax = variavel_data.plot(kind='bar', color=cor, width=0.6, edgecolor='black')

    # Adicionando os valores e porcentagens no topo de cada barra
    for p in ax.patches:
        count = int(p.get_height())
        perc = (count / total_respostas) * 100  # Cálculo da porcentagem
        ax.annotate(f"{count} ({perc:.1f}%)", (p.get_x() + p.get_width() / 2, p.get_height()), ha='center', va='bottom')

    # Adicionando título e rótulos
    plt.title(titulo, fontsize=14)
    plt.xlabel('Classe', fontsize=12)
    plt.ylabel('Contagem', fontsize=12)

    # Rotacionando os rótulos do eixo x
    plt.xticks(rotation=0, ha='right')

    # Exibindo o gráfico
    plt.tight_layout()
    st.pyplot(plt)

def graf_civil():
    var = 'Qual sua situação amorosa hoje?'
    classes_order = ['solteiro(a)',
                     'namorando',
                     'casado(a)',
                     'divorciado(a)',
                     'Não Informado'
                     ]
    cor = 'green'
    titulo = f'{var}'

    # Contagem dos valores e reindexação para garantir a ordem
    variavel_data = data[var].value_counts().reindex(classes_order)
    total_respostas = variavel_data.sum()  # Total para calcular a proporção

    # Criando o gráfico
    plt.figure(figsize=(10, 5))
    ax = variavel_data.plot(kind='bar', color=cor, width=0.6, edgecolor='black')

    # Adicionando os valores e porcentagens no topo de cada barra
    for p in ax.patches:
        count = int(p.get_height())
        perc = (count / total_respostas) * 100  # Cálculo da porcentagem
        ax.annotate(f"{count} ({perc:.1f}%)", (p.get_x() + p.get_width() / 2, p.get_height()), ha='center', va='bottom')

    # Adicionando título e rótulos
    plt.title(titulo, fontsize=14)
    plt.xlabel('Classe', fontsize=12)
    plt.ylabel('Contagem', fontsize=12)

    # Rotacionando os rótulos do eixo x
    plt.xticks(rotation=0, ha='right')

    # Exibindo o gráfico
    plt.tight_layout()
    st.pyplot(plt)

def graf_exp():
    var = 'Se você pudesse classificar seu nível de experiência com investimentos, qual seria?'
    data[var] = data[var].replace({
        'Totalmente iniciante. Não sei nem por onde começar.' : 'Totalmente Iniciante',
        'Iniciante. Não entendo muito bem, mas invisto do meu jeito.' : 'Iniciante',
        'Intermediário. Já invisto, até fiz outros cursos de investimentos, mas sinto que falta alguma coisa.' : 'Intermediário',
        'Profissional. Já invisto e tenho ótimos resultados! Conhecimento nunca é demais!' : ' Profissional'
})
    classes_order = ['Totalmente Iniciante',
                     'Iniciante',
                     'Intermediário',
                     'Profissional',
                     'Não Informado'
                     ]
    cor = 'green'
    titulo = f'{var}'

    # Contagem dos valores e reindexação para garantir a ordem
    variavel_data = data[var].value_counts().reindex(classes_order)
    total_respostas = variavel_data.sum()  # Total para calcular a proporção

    # Criando o gráfico
    plt.figure(figsize=(10, 5))
    ax = variavel_data.plot(kind='bar', color=cor, width=0.6, edgecolor='black')

    # Adicionando os valores e porcentagens no topo de cada barra
    for p in ax.patches:
        count = int(p.get_height())
        perc = (count / total_respostas) * 100  # Cálculo da porcentagem
        ax.annotate(f"{count} ({perc:.1f}%)", (p.get_x() + p.get_width() / 2, p.get_height()), ha='center', va='bottom')

    # Adicionando título e rótulos
    plt.title(titulo, fontsize=14)
    plt.xlabel('Classe', fontsize=12)
    plt.ylabel('Contagem', fontsize=12)

    # Rotacionando os rótulos do eixo x
    plt.xticks(rotation=0, ha='right')

    # Exibindo o gráfico
    plt.tight_layout()
    st.pyplot(plt)

def graf_renda():
    var = 'RENDA MENSAL'
    classes_order = ['Não Informado',
                     'Acima de R$20.000',
                     'Entre R$10.000 e R$20.000',
                     'Entre R$5.000 e R$10.000',
                     'Entre R$2.500 e R$5.000',
                     'Entre R$1.500 e R$2.500',
                     'Até R$1.500'
                     ]
    cor = 'green'
    titulo = f'{var}'

    # Contagem dos valores e reindexação para garantir a ordem invertida
    variavel_data = data[var].value_counts().reindex(classes_order)
    total_respostas = variavel_data.sum()  # Total para calcular a proporção

    # Criando o gráfico com ordem invertida
    plt.figure(figsize=(10, 5))
    ax = variavel_data.plot(kind='barh', color=cor, width=0.6, xlim=(0, 1.1 * variavel_data.max()), edgecolor='black')

    # Adicionando os valores e porcentagens ao lado de cada barra
    for p in ax.patches:
        count = int(p.get_width())
        perc = (count / total_respostas) * 100  # Cálculo da porcentagem
        ax.annotate(f"{count} ({perc:.1f}%)", (p.get_width() + 1, p.get_y() + p.get_height() / 2), 
                    ha='left', va='center')

    # Adicionando título e rótulos
    plt.title(titulo, fontsize=14)
    plt.xlabel('Contagem', fontsize=12)
    plt.ylabel('Classe', fontsize=12)

    # Ajuste do layout
    plt.tight_layout()
    st.pyplot(plt)

def graf_patrim():
    var = 'PATRIMONIO'
    classes_order = [
    'Não Informado',
    'Acima de R$1 milhão',
    'Entre R$500 mil e R$1 milhão',
    'Entre R$250 mil e R$500 mil',
    'Entre R$100 mil e R$250 mil',
    'Entre R$20 mil e R$100 mil',
    'Entre R$5 mil e R$20 mil',
    'Menos de R$5 mil'
]

    cor = 'green'
    titulo = f'{var}'

    # Contagem dos valores e reindexação para garantir a ordem invertida
    variavel_data = data[var].value_counts().reindex(classes_order)
    total_respostas = variavel_data.sum()  # Total para calcular a proporção

    # Criando o gráfico com ordem invertida
    plt.figure(figsize=(10, 5))
    ax = variavel_data.plot(kind='barh', color=cor, width=0.6, xlim=(0, 1.1 * variavel_data.max()), edgecolor='black')

    # Adicionando os valores e porcentagens ao lado de cada barra
    for p in ax.patches:
        count = int(p.get_width())
        perc = (count / total_respostas) * 100  # Cálculo da porcentagem
        ax.annotate(f"{count} ({perc:.1f}%)", (p.get_width() + 1, p.get_y() + p.get_height() / 2), 
                    ha='left', va='center')

    # Adicionando título e rótulos
    plt.title(titulo, fontsize=14)
    plt.xlabel('Contagem', fontsize=12)
    plt.ylabel('Classe', fontsize=12)

    # Ajuste do layout
    plt.tight_layout()
    st.pyplot(plt)

if int(VERSAO_PRINCIPAL) >= 20:
    def graf_invest():
        # Access the specified column and transform it into a single string
        investment_column_string = ' '.join(data['Você já investe seu dinheiro atualmente?'].dropna().astype(str))
        from collections import Counter

        # Define the list of investment categories to count in the string
        investment_classes = [
            'Ainda não invisto',
            'Poupança',
            'Renda Fixa (CDB, Tesouro direto, LCIs, LCAs)',
            'Renda Variável (Ações, Fundos imobiliários)',
            'Investimentos estrangeiros (Stocks, ETFs REITs)',
            'Previdência'
        ]

        # Count occurrences of each category in the single string created earlier
        investment_counts = {category: investment_column_string.count(category) for category in investment_classes}

        # Create a DataFrame from the counts
        investment_counts_df = pd.DataFrame(list(investment_counts.items()), columns=['Tipo de Investimento', 'Contagem'])

        # Calculate the total count of instances in the original dataframe
        total_instances = len(data)

        # Generate the horizontal bar chart with values and percentages on top of each bar
        plt.figure(figsize=(10, 6))
        bars = plt.barh(investment_counts_df['Tipo de Investimento'], investment_counts_df['Contagem'], color='green',
                        edgecolor = 'black')

        # Add the count and percentage labels to the bars
        for bar, count in zip(bars, investment_counts_df['Contagem']):
            percent = (count / total_instances) * 100
            plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2, f'{count} ({percent:.1f}%)', va='center')

        # Labeling
        plt.xlabel('Contagem')
        plt.title('Frequência de cada Tipo de Investimento com Proporção')
        plt.gca().invert_yaxis()  # Invert the y-axis for a more intuitive reading order

        st.pyplot(plt)

stopwords_portugues = [
    'a', 'à', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo',
    'as', 'até', 'às', 'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele', 
    'deles', 'desde', 'do', 'dos', 'e', 'é', 'em', 'entre', 'era', 'eram', 'esse', 
    'essa', 'esses', 'essas', 'esta', 'estas', 'este', 'estes', 'eu', 'foi', 'fomos', 
    'foram', 'há', 'isso', 'isto', 'já', 'lhe', 'lhes', 'lá', 'mas', 'me', 'mesmo', 
    'minha', 'minhas', 'meu', 'meus', 'muito', 'na', 'nas', 'não', 'nem', 'no', 'nos', 
    'nós', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos', 'por', 'qual', 
    'quando', 'que', 'quem', 'se', 'seu', 'seus', 'sua', 'suas', 'só', 'também', 
    'te', 'tem', 'tém', 'tendo', 'tens', 'tenho', 'ter', 'teu', 'teus', 'tinha', 
    'tinham', 'tive', 'tivemos', 'tiveram', 'tu', 'tua', 'tuas', 'um', 'uma', 'umas', 
    'uns', 'vai', 'vão', 'você', 'vocês', 'vos', 'àquele', 'àqueles', 'àquela', 'àquelas',
    'agora', 'ainda', 'além', 'ambos', 'antes', 'após', 'assim', 'cada', 'certa', 
    'certas', 'certo', 'certos', 'contra', 'debaixo', 'dessa', 'desse', 'deste', 
    'dessa', 'disso', 'disto', 'doutro', 'doutros', 'durante', 'ela', 'elas', 'ele', 
    'eles', 'está', 'estão', 'esta', 'estamos', 'estava', 'estavam', 'esteja', 
    'estejam', 'estou', 'eu', 'fará', 'farão', 'farias', 'faz', 'fazem', 'fazendo', 
    'fazer', 'feita', 'feitas', 'feito', 'feitos', 'fim', 'for', 'fosse', 'fostes', 
    'grande', 'grandes', 'há', 'haja', 'hão', 'isso', 'isto', 'lhe', 'lhes', 'lá', 
    'maior', 'mais', 'mas', 'me', 'meio', 'menos', 'mesma', 'mesmas', 'mesmo', 'mesmos', 
    'mim', 'minha', 'minhas', 'muito', 'muitos', 'nela', 'nele', 'nem', 'nenhuma', 
    'nenhum', 'nós', 'nosso', 'nossos', 'nossa', 'nossas', 'num', 'numa', 'outra', 
    'outras', 'outro', 'outros', 'para', 'pela', 'pelas', 'pelo', 'pelos', 'pouca', 
    'poucas', 'pouco', 'poucos', 'primeira', 'primeiras', 'primeiro', 'primeiros', 
    'qual', 'quais', 'qualquer', 'quando', 'quanto', 'quantos', 'quão', 'quem', 
    'será', 'serão', 'seria', 'seriam', 'seu', 'seus', 'sua', 'suas', 'tal', 
    'tão', 'tais', 'tão', 'toda', 'todas', 'todo', 'todos', 'tua', 'tuas', 'um', 
    'uma', 'umas', 'uns', 'vai', 'vão', 'você', 'vocês', 'vos', 'é', 'às', 'alguns', 
    'algumas', 'algum', 'alguma'
]
def plot_top_bigrams_by_column(data, columns, top_n=10):
    for column in columns:
        # Clean the text by removing punctuation and converting to lowercase
        column_text = data[column].fillna('').str.cat(sep=' ')
        column_text = re.sub(r'[^\w\s]', '', column_text.lower())
        
        # Use CountVectorizer to create bigrams and calculate their frequency
        vectorizer = CountVectorizer(ngram_range=(2, 2), stop_words=stopwords_portugues)
        bigram_counts = vectorizer.fit_transform([column_text])
        
        # Sum up the counts for each bigram
        bigram_sums = bigram_counts.toarray().sum(axis=0)
        bigram_frequencies = dict(zip(vectorizer.get_feature_names_out(), bigram_sums))
        
        # Sort bigrams by frequency and select the top N
        top_bigrams = sorted(bigram_frequencies.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # Separate bigrams and their counts for plotting
        bigrams, counts = zip(*top_bigrams) if top_bigrams else ([], [])
        
        # Calculate the total bigram count for this column
        total_bigram_count = sum(bigram_frequencies.values())
        
        # Plot the results for this column
        plt.figure(figsize=(10, 6))
        bars = plt.barh(bigrams, counts, color='green', edgecolor='black')
        
        # Add text labels for each bar
        for bar, count in zip(bars, counts):
            plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2, f'{count}', va='center')
        
        # Labeling
        plt.xlabel('Frequency')
        plt.title(f'Top {top_n} Bigramas na coluna: {column} (Total: {total_bigram_count})')
        plt.gca().invert_yaxis()
        st.pyplot(plt)

def plot_confusion_matrix_renda_patrimonio(data):
    """
    Plots a confusion matrix for 'Renda Mensal' vs 'Patrimônio Total' with counts and proportions.

    Parameters:
        data (pd.DataFrame): DataFrame containing 'Renda Mensal' and 'Patrimônio Total' columns.

    Returns:
        None: Displays the confusion matrix plot.
    """
    # Filter out rows with 'Não informado' in either 'Renda Mensal' or 'Patrimônio Total'
    filtered_data = data[(data['RENDA MENSAL'] != 'Não informado') & (data['PATRIMONIO'] != 'Não informado')]

    # Define the order of categories from smallest to largest for both 'Renda Mensal' and 'Patrimônio Total'
    renda_order = [
        "Menos de R$1.500", "Entre R$1.500 e R$2.500", "Entre R$2.500 e R$5.000",
        "Entre R$5.000 e R$10.000", "Entre R$10.000 e R$20.000", "Mais de R$20.000"
    ]
    patrimonio_order = [
        "Menos de R$5 mil", "Entre R$5 mil e R$20 mil", "Entre R$20 mil e R$100 mil",
        "Entre R$100 mil e R$500 mil", "Entre R$500 mil e R$1 milhão", "Mais de R$1 milhão"
    ]

    # Create a crosstab (confusion matrix) for 'Renda Mensal' vs 'Patrimônio Total'
    confusion_matrix = pd.crosstab(
        filtered_data['RENDA MENSAL'], filtered_data['PATRIMONIO'],
        rownames=['RENDA MENSAL'], colnames=['PATRIMONIO']
    ).reindex(index=renda_order, columns=patrimonio_order, fill_value=0)

    # Calculate the total instances for proportion calculation
    total_instances = confusion_matrix.values.sum()

    # Annotate the matrix with counts and proportions
    annot = np.empty_like(confusion_matrix, dtype=object)
    for i in range(confusion_matrix.shape[0]):
        for j in range(confusion_matrix.shape[1]):
            count = confusion_matrix.iloc[i, j]
            proportion = (count / total_instances) * 100
            annot[i, j] = f"{count}\n({proportion:.1f}%)"

    # Plot the confusion matrix with Seaborn
    plt.figure(figsize=(10, 8))
    sns.heatmap(confusion_matrix, annot=annot, fmt='', cmap='Blues', cbar=False, linewidths=0.5)
    plt.title('Matriz de Confusão - Renda vs Patrimônio')
    plt.ylabel('Renda Mensal')
    plt.xlabel('Patrimônio Total')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    st.pyplot(plt)

# Criando as abas
tab1, tab2, tab3 = st.tabs(["Informações Pessoais", "Informações Financeiras", "Análise Textual"])

# Aba 1: Informações Pessoais
with tab1:
    st.header("Informações Pessoais")
    
    col1, col2 = st.columns(2)
    with col1:
        graf_sexo()
        graf_civil()
        if int(VERSAO_PRINCIPAL) >= 20:
            graf_idade()
    with col2:
        graf_exp()
        if int(VERSAO_PRINCIPAL) >= 20:
            graf_filhos()

# Aba 2: Informações Financeiras
with tab2:
    st.header("Informações Financeiras")
    
    col3, col4 = st.columns(2)
    with col3:
        if int(VERSAO_PRINCIPAL) >= 20:
            graf_invest()
        graf_patrim()
    with col4:
        graf_renda()
    st.divider()
    # Colocando a matriz de confusão em uma linha separada
    st.subheader("Matriz de Confusão entre Renda e Patrimônio")
    plot_confusion_matrix_renda_patrimonio(data)

# Aba 3: Análise Textual
with tab3:
    st.header("Análise Textual")
    
    st.subheader("Principais Bigramas")
    plot_top_bigrams_by_column(data, open_ended_columns)

