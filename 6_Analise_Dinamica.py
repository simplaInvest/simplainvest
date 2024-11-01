import pandas as pd
import matplotlib.pyplot as plt  
import numpy as np
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as stopwords
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import re

active_ei20 = st.session_state.get('df_PESQUISA', pd.DataFrame())
copy_ei20 = st.session_state.get('df_COPY', pd.DataFrame())

trafego_ei20 = active_ei20[['EMAIL','RENDA MENSAL', 'PATRIMONIO']]

copy_ei20['Email'] = copy_ei20['LIBERE A FERRAMENTA: Digite o e-mail que usou ao fazer sua inscrição no MPI']
copy_ei20 = copy_ei20.drop('LIBERE A FERRAMENTA: Digite o e-mail que usou ao fazer sua inscrição no MPI', axis =1)

# Passo 1: Criar um novo dataframe com emails em comum entre 'trafego_ei20' e 'copy_ei20'
filtered_trafego_ei20 = trafego_ei20[trafego_ei20['EMAIL'].isin(copy_ei20['Email'])]

# Renomeando as colunas para facilitar o merge posterior
filtered_trafego_ei20 = filtered_trafego_ei20.rename(columns={
    'RENDA MENSAL': 'Renda Mensal',
    'PATRIMONIO': 'Patrimônio Total',
    'EMAIL' : 'Email'
})

# Passo 2: Mesclar os dados no dataframe 'copy_ei20' para adicionar as novas colunas
copy_ei20 = copy_ei20.merge(filtered_trafego_ei20[['Email','Renda Mensal', 'Patrimônio Total']], on='Email', how='left')

# Step 1: Remove the 'utm' columns from the dataframe
columns_to_drop = [col for col in copy_ei20.columns if 'utm' in col]
copy_ei20_cleaned = copy_ei20.drop(columns=columns_to_drop)

# Closed-ended response columns: categorical responses or choices
closed_ended_columns = [
    "Qual seu sexo?", 
    "Você tem filhos?", 
    "Qual sua idade?", 
    "Qual seu estado civil atual?", 
    "Você já investe seu dinheiro atualmente?", 
    "Renda Mensal", 
    "Patrimônio Total"
]

# Open-ended response columns: free-text responses
open_ended_columns = [
    "Porque você quer a começar a investir?", 
    "Como você imagina a vida que está buscando?", 
    "Quais são os principais obstáculos que te impedem de viver essa vida hoje? ", 
    ]

# Calculate the total number of responses in the dataframe
total_responses = copy_ei20_cleaned.shape[0]

copy_ei20_cleaned = copy_ei20_cleaned.fillna('Não Informado')
copy_ei20_cleaned = copy_ei20_cleaned.replace('', 'Não Informado')

# Prepare the columns for the new dataframe
variable_names = copy_ei20_cleaned.drop(['Token', 'Email', 'Submitted At', 'Qual seu Whatsapp para receber suporte?'], axis = 1).columns
num_na_values = (copy_ei20_cleaned.drop(['Token', 'Email', 'Submitted At', 'Qual seu Whatsapp para receber suporte?'], axis = 1) == 'Não Informado').sum().reset_index()
proportion_na_values = (num_na_values[0] / total_responses * 100).round(2)

# Create the new dataframe with the required columns
missing_data_summary = pd.DataFrame({
    'Variável': variable_names,
    'Número de informações deixadas em branco': num_na_values[0],
    'Proporção em relação ao total de respostas da pesquisa': proportion_na_values
})

copy_ei20_cleaned['Por último, qual sua experiência com investimentos?'].replace({
    'Totalmente iniciante. Não sei nem por onde começar.' : 'Totalmente Iniciante', 'Iniciante. Não entendo muito bem, mas invisto do meu jeito.' : 'Iniciante',
    'Intermediário. Já invisto, até fiz outros cursos de investimentos, mas sinto que falta alguma coisa.' : 'Intermediário', 
    'Profissional. Já invisto e tenho ótimos resultados! Conhecimento nunca é demais!' : 'Profissional'
    }, inplace=True)

filtered_trafego_ei20.fillna('Não Informado')
######################################################################################################

st.title('Painel de análise dinâmica dos leads')
st.write('Neste painel você encontra um resumo dos dados coletados na pesquisa de Copy do lançamento selecionado. Estes dados são atualizados em tempo real.')
st.divider()

st.header('Dados ausentes')
st.write(missing_data_summary.set_index('Variável'))
st.divider()
with st.container(border=False):
        st.markdown("<h2 style='text-align: left; font-size: 2vw; margin-bottom: 28px; color: lightblue;hover-color: red'>Métricas Gerais</h1>", unsafe_allow_html=True)
        ctcol1, ctcol2, ctcol3= st.columns([1, 1, 1])
        with ctcol1:
            st.metric("Total de leads que preencheram a pesquisa de tráfego:", trafego_ei20.shape[0])
        with ctcol2:
            st.metric("Total de leads que preencheram a pesquisa de copy:", copy_ei20_cleaned.shape[0])
        with ctcol3:
            st.metric("Taxa e preenchimento da pesquisa de copy", f"{round((copy_ei20_cleaned.shape[0]/trafego_ei20.shape[0])*100, 2)}%")        
st.divider()

st.header('Gráficos')

data = copy_ei20_cleaned

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
    ax = variavel_data.plot(kind='bar', color=cor, width=0.6, ylim=(0, 1.1 * variavel_data.max()), edgecolor='black')

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
    variavel_data = data[var].value_counts().reindex(classes_order)
    total_respostas = variavel_data.sum()  # Total para calcular a proporção

    # Criando o gráfico
    plt.figure(figsize=(10, 5))
    ax = variavel_data.plot(kind='bar', color=cor, width=0.6, ylim=(0, 1.1 * variavel_data.max()), edgecolor='black')

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
    var = 'Qual seu estado civil atual?'
    classes_order = ['Solteiro(a)',
                     'Namorando',
                     'Casado(a)',
                     'Divorciado(a)',
                     'Não Informado'
                     ]
    cor = 'green'
    titulo = f'{var}'

    # Contagem dos valores e reindexação para garantir a ordem
    variavel_data = data[var].value_counts().reindex(classes_order)
    total_respostas = variavel_data.sum()  # Total para calcular a proporção

    # Criando o gráfico
    plt.figure(figsize=(10, 5))
    ax = variavel_data.plot(kind='bar', color=cor, width=0.6, ylim=(0, 1.1 * variavel_data.max()), edgecolor='black')

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
    var = 'Por último, qual sua experiência com investimentos?'
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
    ax = variavel_data.plot(kind='bar', color=cor, width=0.6, ylim=(0, 1.1 * variavel_data.max()), edgecolor='black')

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
    variavel_data = trafego_ei20[var].value_counts().reindex(classes_order)
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
    variavel_data = trafego_ei20[var].value_counts().reindex(classes_order)
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
    filtered_data = data[(data['Renda Mensal'] != 'Não informado') & (data['Patrimônio Total'] != 'Não informado')]

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
        filtered_data['Renda Mensal'], filtered_data['Patrimônio Total'],
        rownames=['Renda Mensal'], colnames=['Patrimônio Total']
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
    with col2:
        graf_exp()
        graf_filhos()

# Aba 2: Informações Financeiras
with tab2:
    st.header("Informações Financeiras")
    
    col3, col4 = st.columns(2)
    with col3:
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
