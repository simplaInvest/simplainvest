import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import re
import seaborn as sns

def plot_bar_chart(data, var_name, classes_order, missing_data_summary, color='green', rename_dict=None):
    """
    Gera um gráfico de barras verticais com contagem e percentual para uma variável categórica.

    Parâmetros:
    - data: DataFrame contendo os dados da pesquisa.
    - var_name: Nome da coluna a ser analisada.
    - classes_order: Ordem desejada das categorias.
    - missing_data_summary: DataFrame com o percentual de preenchimento das variáveis.
    - color: Cor da barra.
    - rename_dict: Dicionário opcional para renomear valores da coluna.
    """

    # Renomeia valores, se necessário
    if rename_dict:
        data[var_name] = data[var_name].replace(rename_dict)

    # Título com % de preenchimento
    preenchimento = 100 - missing_data_summary.loc[
        missing_data_summary["Variável"] == var_name,
        "Proporção em relação ao total de respostas da pesquisa"
    ].values[0]
    titulo = f'{var_name} \n({round(preenchimento, 2)}% de preenchimento)'

    # Contagem
    variavel_data = data[var_name].dropna().value_counts().reindex(classes_order, fill_value=0)
    total_respostas = variavel_data.sum()

    warning = '⚠️ POUCAS RESPOSTAS' if total_respostas <= 101 else ''

    # Plot
    plt.figure(figsize=(10, 5))
    ax = variavel_data.plot(kind='bar', color=color, width=0.6, edgecolor='black')

    for p in ax.patches:
        count = int(p.get_height())
        perc = (count / total_respostas) * 100 if total_respostas > 0 else 0
        ax.annotate(f"{count} ({perc:.1f}%)", (p.get_x() + p.get_width() / 2, p.get_height()),
                    ha='center', va='bottom')

    plt.title(f'{titulo} {warning}', fontsize=14)
    plt.xlabel('Classe', fontsize=12)
    plt.ylabel('Contagem', fontsize=12)
    plt.xticks(rotation=0, ha='right')
    plt.tight_layout()

    st.pyplot(plt)

def graf_idade(data, missing_data_summary):
        # Convertendo para valores numéricos, substituindo não numéricos por NaN
        data['Qual sua idade?'] = pd.to_numeric(data['Qual sua idade?'], errors='coerce')
        var = 'Qual sua idade?'
        titulo = f'{var} \n({round(100 - missing_data_summary.loc[missing_data_summary["Variável"] == f"{var}", "Proporção em relação ao total de respostas da pesquisa"].values[0], 2)}% de preenchimento)'
        
        # Removendo valores NaN
        idade_data = data['Qual sua idade?'].dropna()
        # Definindo o intervalo de idades e criando os bins que começam em 0 com intervalos de 5 anos
        idade_max = data['Qual sua idade?'].max()
        bins = np.arange(0, idade_max + 5, 5)

        # Calculando o total de respostas
        total_respostas = idade_data.shape[0]

        if total_respostas <= 101:
            warning = '⚠️ POUCAS RESPOSTAS'
        else:
            warning = ''

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
        plt.title(f'{titulo} {warning}')
        plt.xlabel('Idade')
        plt.ylabel('Frequência')
        plt.legend()

        # Exibindo o gráfico com valores de média e desvio-padrão no eixo x
        st.pyplot(plt)

def graf_renda(data, missing_data_summary):
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
    titulo = f'{var} \n({round(100 - missing_data_summary.loc[missing_data_summary["Variável"] == f"{var}", "Proporção em relação ao total de respostas da pesquisa"].values[0], 2)}% de preenchimento)'

    # Contagem dos valores e reindexação para garantir a ordem invertida
    variavel_data = data[var].value_counts().reindex(classes_order)
    total_respostas = variavel_data.sum()  # Total para calcular a proporção

    if total_respostas <= 101:
        warning = '⚠️ POUCAS RESPOSTAS'
    else:
        warning = ''

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
    plt.title(f'{titulo} {warning}', fontsize=14)
    plt.xlabel('Contagem', fontsize=12)
    plt.ylabel('Classe', fontsize=12)

    # Ajuste do layout
    plt.tight_layout()
    st.pyplot(plt)

def graf_patrim(data, missing_data_summary):
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
    titulo = f'{var} \n({round(100 - missing_data_summary.loc[missing_data_summary["Variável"] == f"{var}", "Proporção em relação ao total de respostas da pesquisa"].values[0], 2)}% de preenchimento)'

    # Contagem dos valores e reindexação para garantir a ordem invertida
    variavel_data = data[var].value_counts().reindex(classes_order)
    total_respostas = variavel_data.sum()  # Total para calcular a proporção

    if total_respostas <= 101:
        warning = '⚠️ POUCAS RESPOSTAS'
    else:
        warning = ''

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
    plt.title(f'{titulo} {warning}', fontsize=14)
    plt.xlabel('Contagem', fontsize=12)
    plt.ylabel('Classe', fontsize=12)

    # Ajuste do layout
    plt.tight_layout()
    st.pyplot(plt)

def graf_invest(data, missing_data_summary):
    # Access the specified column and transform it into a single string
    investment_column_string = ' '.join(data['Você já investe seu dinheiro atualmente?'].dropna().astype(str))
    from collections import Counter

    total_respostas = data['Você já investe seu dinheiro atualmente?'].dropna().shape[0]

    if total_respostas <= 101:
        warning = '⚠️ POUCAS RESPOSTAS'
    else:
        warning = ''

    var = 'Você já investe seu dinheiro atualmente?'
    titulo = f'{var} \n({round(100 - missing_data_summary.loc[missing_data_summary["Variável"] == f"{var}", "Proporção em relação ao total de respostas da pesquisa"].values[0], 2)}% de preenchimento)'

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
    plt.title(f'{titulo} {warning}')
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
        # Limpar o texto: remover pontuação e converter para minúsculas
        column_text = data[column].fillna('').str.cat(sep=' ')
        column_text = re.sub(r'[^\w\s]', '', column_text.lower())
        
        # Gerar bigramas
        vectorizer = CountVectorizer(ngram_range=(2, 2), stop_words=stopwords_portugues)
        bigram_counts = vectorizer.fit_transform([column_text])
        bigram_features = vectorizer.get_feature_names_out()

        # Adicionando aviso
        total_respostas = data[column].dropna().shape[0]

        if total_respostas <= 101:
            warning = '⚠️ POUCAS RESPOSTAS'
        else:
            warning = ''
        
        # Ordenar as palavras em cada bigrama e remover bigramas com palavras iguais
        filtered_bigrams = []
        for bigram in bigram_features:
            words = bigram.split()
            if words[0] != words[1]:  # Apenas incluir bigramas com palavras diferentes
                filtered_bigrams.append(' '.join(sorted(words)))
        
        # Calcular as frequências somadas de bigramas equivalentes
        bigram_sums = bigram_counts.toarray().sum(axis=0)
        bigram_frequencies = {}
        for bigram, count in zip(filtered_bigrams, bigram_sums):
            bigram_frequencies[bigram] = bigram_frequencies.get(bigram, 0) + count
        
        # Selecionar os top N bigramas
        top_bigrams = sorted(bigram_frequencies.items(), key=lambda x: x[1], reverse=True)[:top_n]
        bigrams, counts = zip(*top_bigrams) if top_bigrams else ([], [])
        
        # Calcular o total de bigramas
        total_bigram_count = sum(bigram_frequencies.values())
        
        # Criar o gráfico
        plt.figure(figsize=(12, 8))
        bars = plt.barh(bigrams, counts, color='green', edgecolor='black')
        
        # Ajustar limite do eixo x para evitar texto fora
        max_count = max(counts) if counts else 0
        plt.xlim(0, max_count * 1.15)
        
        # Adicionar rótulos com valores absolutos e relativos
        for bar, count in zip(bars, counts):
            relative_freq = (count / total_bigram_count) * 100
            plt.text(bar.get_width() + max_count * 0.02, 
                     bar.get_y() + bar.get_height() / 2, 
                     f'{relative_freq:.2f}% ({count})', 
                     va='center')
        
        # Configurar rótulos e título
        plt.xlabel('Frequency')
        plt.title(f'{column} (Total: {total_bigram_count}) {warning}')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        # Renderizar o gráfico com streamlit
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