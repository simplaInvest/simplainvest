import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
import re
from sklearn.feature_extraction.text import CountVectorizer
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest, Filter, FilterExpression
from google.oauth2 import service_account

PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]
LANÇAMENTO = st.session_state["LANÇAMENTO"]

def generate_debriefing2(PRODUTO, VERSAO_PRINCIPAL):
    # Carregar informações sobre lançamento selecionado
    from libs.data_loader import (
        K_CENTRAL_CAPTURA, K_CENTRAL_VENDAS, K_GRUPOS_WPP, K_PCOPY_DADOS, 
        K_PTRAFEGO_DADOS, K_CLICKS_WPP, K_CENTRAL_PRE_MATRICULA, get_df
    )

    PRODUTO = st.session_state["PRODUTO"]
    VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

    DF_CENTRAL_CAPTURA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
    DF_CENTRAL_VENDAS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
    DF_CENTRAL_PREMATRICULA = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
    DF_PTRAFEGO_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
    if PRODUTO == 'EI':
        DF_PCOPY_DADOS = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PCOPY_DADOS)
    DF_GRUPOS_WPP = get_df(PRODUTO, VERSAO_PRINCIPAL, K_GRUPOS_WPP)

    if PRODUTO == 'EI':
        DF_PCOPY_DADOS = DF_PCOPY_DADOS.merge(DF_PTRAFEGO_DADOS[['EMAIL', 'RENDA MENSAL']], on='EMAIL', how='left')
        DF_PCOPY_DADOS = DF_PCOPY_DADOS.merge(DF_PTRAFEGO_DADOS[['EMAIL', 'PATRIMONIO']], on='EMAIL', how='left')

    # ✅ Mantendo as suas métricas
    conv_traf = f"{round(DF_PTRAFEGO_DADOS.shape[0] / DF_CENTRAL_CAPTURA.shape[0] * 100, 2)}%"
    if PRODUTO == 'EI':
        conv_copy = f"{round(DF_PCOPY_DADOS.shape[0] / DF_CENTRAL_CAPTURA.shape[0] * 100, 2)}%"
    conv_wpp = f"{round(DF_GRUPOS_WPP[DF_GRUPOS_WPP['Evento'] == 'Entrou no grupo'].shape[0] / DF_CENTRAL_CAPTURA.shape[0] * 100, 2)}%"

    # ✅ Mantendo a lógica das suas tabelas
    dic_terms = {
        "DF_CENTRAL_CAPTURA": ("CAP", DF_CENTRAL_CAPTURA),
        "DF_CENTRAL_PREMATRICULA": ("PM", DF_CENTRAL_PREMATRICULA),
        "DF_CENTRAL_VENDAS": ("VENDAS", DF_CENTRAL_VENDAS)
    }

    lista_tabs = []
    for nome, (prefixo, df) in dic_terms.items():
        coluna_utm = "UTM_TERM"
        if coluna_utm in df.columns:
            tab_result = df[coluna_utm].value_counts().reset_index()
            tab_result.columns = ['Anúncio', 'Leads_Absoluto']
            total_leads = tab_result['Leads_Absoluto'].sum()
            tab_result['Leads_Relativo (%)'] = round((tab_result['Leads_Absoluto'] / total_leads) * 100, 2)
            tab_result = tab_result.sort_values(by='Leads_Absoluto', ascending=False)
            lista_tabs.append((nome, tab_result))

    # 3. Perfis
    if PRODUTO == 'EI':
        total_responses = DF_PCOPY_DADOS.shape[0]

        DF_PCOPY_DADOS_cleaned = DF_PCOPY_DADOS.fillna('Não Informado')
        DF_PCOPY_DADOS_cleaned = DF_PCOPY_DADOS_cleaned.replace('', 'Não Informado')

        # Prepare the columns for the new dataframe
        variable_names = DF_PCOPY_DADOS_cleaned.columns
        num_na_values = (DF_PCOPY_DADOS_cleaned == 'Não Informado').sum().reset_index()
        proportion_na_values = (num_na_values[0] / total_responses * 100).round(2)
        data = DF_PCOPY_DADOS_cleaned

        # Create the new dataframe with the required columns
        missing_data_summary = pd.DataFrame({
            'Variável': variable_names,
            'Número de informações deixadas em branco': num_na_values[0],
            'Proporção em relação ao total de respostas da pesquisa': proportion_na_values
        })

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


        if 'Se você pudesse classificar seu nível de experiência com investimentos, qual seria?' in data.columns:
            data['Se você pudesse classificar seu nível de experiência com investimentos, qual seria?'] = data['Se você pudesse classificar seu nível de experiência com investimentos, qual seria?'].replace({
                'Totalmente iniciante. Não sei nem por onde começar.' : 'Totalmente Iniciante',
                'Iniciante. Não entendo muito bem, mas invisto do meu jeito.' : 'Iniciante',
                'Intermediário. Já invisto, até fiz outros cursos de investimentos, mas sinto que falta alguma coisa.' : 'Intermediário',
                'Profissional. Já invisto e tenho ótimos resultados! Conhecimento nunca é demais!' : ' Profissional'
            })


        def graf_barras(var):
            cor = 'green'
            titulo = f'{var} \n({round(100 - missing_data_summary.loc[missing_data_summary["Variável"] == f"{var}", "Proporção em relação ao total de respostas da pesquisa"].values[0], 2)}% de preenchimento)'

            if var == 'Qual seu sexo?':
                classes_order = ['Masculino',
                                'Feminino',
                                'Outro',
                                'Não Informado'
                                ]
            elif var == 'Você tem filhos?':
                classes_order = ['Sim',
                                'Não, mas quero ter',
                                'Não e nem pretendo'
                                ]
            elif var == 'Qual sua situação amorosa hoje?':
                classes_order = ['Solteiro(a)',
                                'Namorando',
                                'Casado(a)',
                                'Divorciado(a)',
                                'Não Informado'
                                ]
            elif var == 'Se você pudesse classificar seu nível de experiência com investimentos, qual seria?':
                classes_order = ['Totalmente Iniciante',
                        'Iniciante',
                        'Intermediário',
                        'Profissional',
                        'Não Informado'
                        ]

            # Contagem dos valores e reindexação para garantir a ordem
            variavel_data = data[var].value_counts().reindex(classes_order)
            total_respostas = variavel_data.sum()  # Total para calcular a proporção

            if total_respostas <= 101:
                warning = '⚠️ POUCAS RESPOSTAS'
            else:
                warning = ''

            # Criando o gráfico corretamente
            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.bar(variavel_data.index, variavel_data, color=cor, width=0.6, edgecolor='black')

            # Adicionando os valores e porcentagens no topo de cada barra
            for bar in bars:
                height = bar.get_height()
                
                # Verificar se o valor é NaN e substituir por 0
                if np.isnan(height):
                    height = 0
                
                count = int(height)
                perc = (count / total_respostas * 100) if total_respostas > 0 else 0  # Evita divisão por zero
                
                ax.text(bar.get_x() + bar.get_width() / 2, 
                        bar.get_height(), 
                        f"{count} ({perc:.1f}%)", 
                        ha='center', va='bottom')

            # Adicionando título e rótulos
            ax.set_title(f"{titulo} {warning}", fontsize=14)
            ax.set_xlabel('Classe', fontsize=12)
            ax.set_ylabel('Contagem', fontsize=12)

            # Rotacionando os rótulos do eixo x
            plt.xticks(rotation=0, ha='right')

            # Ajustando o layout
            plt.tight_layout()



            # Retornando a figura corretamente
            return fig       

        if PRODUTO == 'EI' and VERSAO_PRINCIPAL >= 21:
            def graf_idade():
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

                # Criando a figura e o eixo
                fig, ax = plt.subplots(figsize=(15, 6))

                # Criando o histograma
                counts, edges, _ = ax.hist(data['Qual sua idade?'], bins=bins, color='green', edgecolor='black')

                # Adicionando o valor de cada bin no topo de cada barra
                for i in range(len(counts)):
                    ax.text((edges[i] + edges[i+1]) / 2, counts[i] + 1, f"{int(counts[i])}", 
                            ha='center', va='bottom')

                # Ajustando as marcas do eixo x para que correspondam aos intervalos de 5 anos
                ax.set_xticks(bins)
                ax.set_xticklabels(bins, rotation=0)

                # Adicionando título, legenda e rótulos
                ax.set_title(f'{titulo} {warning}')
                ax.set_xlabel('Idade')
                ax.set_ylabel('Frequência')

                # Exibindo o gráfico no Streamlit
                

                # Retornando a figura para ser salva no PDF
                return fig
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
            titulo = 'RENDA MENSAL'

            # Contagem dos valores e reindexação para garantir a ordem invertida
            variavel_data = DF_PTRAFEGO_DADOS[var].value_counts().reindex(classes_order, fill_value=0)  # Evita NaN
            total_respostas = variavel_data.sum()  # Total para calcular a proporção

            # Criando a figura e o eixo
            fig, ax = plt.subplots(figsize=(10, 5))

            # Criando o gráfico de barras horizontais
            bars = ax.barh(variavel_data.index, variavel_data, color=cor, height=0.6, edgecolor='black')

            # Ajustando o limite do eixo X
            ax.set_xlim(0, 1.1 * variavel_data.max())

            # Adicionando os valores e porcentagens ao lado de cada barra
            for bar in bars:
                width = bar.get_width()  # Correção: largura representa o valor real da barra
                
                # Verificar se o valor é NaN e substituir por 0
                if np.isnan(width):
                    width = 0
                
                count = int(width)
                perc = (count / total_respostas * 100) if total_respostas > 0 else 0  # Evita divisão por zero
                
                ax.text(width + 1, bar.get_y() + bar.get_height() / 2,  # Ajustado para posição correta
                        f"{count} ({perc:.1f}%)", 
                        ha='left', va='center')

            # Adicionando título e rótulos
            ax.set_title(f'{titulo}', fontsize=14)
            ax.set_xlabel('Contagem', fontsize=12)
            ax.set_ylabel('Classe', fontsize=12)

            # Ajuste do layout
            plt.tight_layout()

            # Exibindo no Streamlit
            

            # Retornando a figura para ser salva no PDF
            return fig
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
            titulo = 'PATRIMÔNIO'

            # Contagem dos valores e reindexação para garantir a ordem invertida, evitando NaN
            variavel_data = DF_PTRAFEGO_DADOS[var].value_counts().reindex(classes_order, fill_value=0)
            total_respostas = variavel_data.sum()  # Total para calcular a proporção

            # Criando a figura e o eixo
            fig, ax = plt.subplots(figsize=(10, 5))

            # Criando o gráfico de barras horizontais
            bars = ax.barh(variavel_data.index, variavel_data, color=cor, height=0.6, edgecolor='black')

            # Ajustando o limite do eixo X
            ax.set_xlim(0, 1.1 * variavel_data.max())

            # Adicionando os valores e porcentagens ao lado de cada barra
            for bar in bars:
                width = bar.get_width()  # Correção: largura representa o valor real da barra
                
                # Verificar se o valor é NaN e substituir por 0
                if np.isnan(width):
                    width = 0
                
                count = int(width)
                perc = (count / total_respostas * 100) if total_respostas > 0 else 0  # Evita divisão por zero
                
                ax.text(width + 1, bar.get_y() + bar.get_height() / 2,  # Ajustado para posição correta
                        f"{count} ({perc:.1f}%)", 
                        ha='left', va='center')

            # Adicionando título e rótulos
            ax.set_title(f'{titulo}', fontsize=14)
            ax.set_xlabel('Contagem', fontsize=12)
            ax.set_ylabel('Classe', fontsize=12)

            # Ajuste do layout
            plt.tight_layout()

            # Exibindo no Streamlit
            

            # Retornando a figura para ser salva no PDF
            return fig
        def graf_invest():
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

        # Criando a figura e o eixo
            fig, ax = plt.subplots(figsize=(10, 6))

            # Criando o gráfico de barras horizontais
            bars = ax.barh(investment_counts_df['Tipo de Investimento'], investment_counts_df['Contagem'], 
                        color='green', edgecolor='black')

            # Adicionando os valores e porcentagens ao lado de cada barra
            for bar, count in zip(bars, investment_counts_df['Contagem']):
                percent = (count / total_instances) * 100  # Cálculo da porcentagem
                ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2, 
                        f'{count} ({percent:.1f}%)', va='center')

            # Adicionando título e rótulos
            ax.set_xlabel('Contagem')
            ax.set_title(f'{titulo} {warning}')
            ax.invert_yaxis()  # Inverte o eixo Y para uma leitura mais intuitiva

            # Ajuste do layout
            plt.tight_layout()

            # Exibindo no Streamlit
            

            # Retornando a figura para ser salva no PDF
            return fig


        bar_sexo = graf_barras('Qual seu sexo?')
        bar_filhos = graf_barras('Você tem filhos?')
        bar_civil = graf_barras('Qual sua situação amorosa hoje?')
        bar_exp = graf_barras('Se você pudesse classificar seu nível de experiência com investimentos, qual seria?')
        if PRODUTO == 'EI' and VERSAO_PRINCIPAL >= 21:
            graf_age = graf_idade()
        graf_ren = graf_renda()
        graf_pat = graf_patrim()
        graf_inv = graf_invest()

        ################################
        #          Discursivas         #
        ################################
        if int(VERSAO_PRINCIPAL) >= 23:
            open_ended_columns = [
                'Porque você quer a começar a investir?',
                'Como você imagina a vida que está buscando?',
                'Quais são os principais obstáculos que te impedem de viver essa vida hoje? ',
                'Descreva, da forma que imaginar, como seria o seu dia perfeito.',
                'Se você estivesse com o Rufino agora, qual pergunta faria?'
            ]
        if int(VERSAO_PRINCIPAL) == 22:
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
        def plot_top_bigrams_by_column(data, column, top_n=10):
            # Limpar o texto: remover pontuação e converter para minúsculas
            column_text = data[column].fillna('').str.cat(sep=' ')
            column_text = re.sub(r'[^\w\s]', '', column_text.lower())

            # Gerar bigramas
            vectorizer = CountVectorizer(ngram_range=(2, 2), stop_words=stopwords_portugues)
            bigram_counts = vectorizer.fit_transform([column_text])
            bigram_features = vectorizer.get_feature_names_out()

            # Adicionando aviso
            total_respostas = data[column].dropna().shape[0]
            warning = '⚠️ POUCAS RESPOSTAS' if total_respostas <= 101 else ''

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

            # Criando a figura e o eixo
            fig, ax = plt.subplots(figsize=(12, 8))

            # Criando o gráfico de barras horizontais para bigramas
            bars = ax.barh(bigrams, counts, color='green', edgecolor='black')

            # Ajustando limite do eixo x para evitar que o texto saia da área visível
            max_count = max(counts) if counts else 0
            ax.set_xlim(0, max_count * 1.15 if max_count > 0 else 1)  # Evita erro de xlim negativo

            # Adicionando rótulos com valores absolutos e relativos
            for bar, count in zip(bars, counts):
                relative_freq = (count / total_bigram_count * 100) if total_bigram_count > 0 else 0  # Evita divisão por zero
                ax.text(bar.get_width() + max_count * 0.02 if max_count > 0 else 0.5, 
                        bar.get_y() + bar.get_height() / 2, 
                        f'{relative_freq:.2f}% ({count})', 
                        va='center')

            # Configurando rótulos e título
            ax.set_xlabel('Frequência')
            ax.set_title(f'{column} (Total: {total_bigram_count}) {warning}')
            ax.invert_yaxis()  # Inverte o eixo Y para melhor leitura

            # Ajustando layout
            plt.tight_layout()

            return fig


        # Criando uma lista para armazenar os gráficos
        disc_grafs = [plot_top_bigrams_by_column(data, column) for column in open_ended_columns]

    if PRODUTO == 'SC':
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
            titulo = 'RENDA MENSAL'

            # Contagem dos valores e reindexação para garantir a ordem invertida
            variavel_data = DF_PTRAFEGO_DADOS[var].value_counts().reindex(classes_order, fill_value=0)  # Evita NaN
            total_respostas = variavel_data.sum()  # Total para calcular a proporção

            # Criando a figura e o eixo
            fig, ax = plt.subplots(figsize=(10, 5))

            # Criando o gráfico de barras horizontais
            bars = ax.barh(variavel_data.index, variavel_data, color=cor, height=0.6, edgecolor='black')

            # Ajustando o limite do eixo X
            ax.set_xlim(0, 1.1 * variavel_data.max())

            # Adicionando os valores e porcentagens ao lado de cada barra
            for bar in bars:
                width = bar.get_width()  # Correção: largura representa o valor real da barra
                
                # Verificar se o valor é NaN e substituir por 0
                if np.isnan(width):
                    width = 0
                
                count = int(width)
                perc = (count / total_respostas * 100) if total_respostas > 0 else 0  # Evita divisão por zero
                
                ax.text(width + 1, bar.get_y() + bar.get_height() / 2,  # Ajustado para posição correta
                        f"{count} ({perc:.1f}%)", 
                        ha='left', va='center')

            # Adicionando título e rótulos
            ax.set_title(f'{titulo}', fontsize=14)
            ax.set_xlabel('Contagem', fontsize=12)
            ax.set_ylabel('Classe', fontsize=12)

            # Ajuste do layout
            plt.tight_layout()

            # Exibindo no Streamlit
            

            # Retornando a figura para ser salva no PDF
            return fig
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
            titulo = 'PATRIMÔNIO'

            # Contagem dos valores e reindexação para garantir a ordem invertida, evitando NaN
            variavel_data = DF_PTRAFEGO_DADOS[var].value_counts().reindex(classes_order, fill_value=0)
            total_respostas = variavel_data.sum()  # Total para calcular a proporção

            # Criando a figura e o eixo
            fig, ax = plt.subplots(figsize=(10, 5))

            # Criando o gráfico de barras horizontais
            bars = ax.barh(variavel_data.index, variavel_data, color=cor, height=0.6, edgecolor='black')

            # Ajustando o limite do eixo X
            ax.set_xlim(0, 1.1 * variavel_data.max())

            # Adicionando os valores e porcentagens ao lado de cada barra
            for bar in bars:
                width = bar.get_width()  # Correção: largura representa o valor real da barra
                
                # Verificar se o valor é NaN e substituir por 0
                if np.isnan(width):
                    width = 0
                
                count = int(width)
                perc = (count / total_respostas * 100) if total_respostas > 0 else 0  # Evita divisão por zero
                
                ax.text(width + 1, bar.get_y() + bar.get_height() / 2,  # Ajustado para posição correta
                        f"{count} ({perc:.1f}%)", 
                        ha='left', va='center')

            # Adicionando título e rótulos
            ax.set_title(f'{titulo}', fontsize=14)
            ax.set_xlabel('Contagem', fontsize=12)
            ax.set_ylabel('Classe', fontsize=12)

            # Ajuste do layout
            plt.tight_layout()

            # Exibindo no Streamlit
            

            # Retornando a figura para ser salva no PDF
            return fig
        
        graf_ren = graf_renda()
        graf_pat = graf_patrim()

    if PRODUTO == 'EI' and int(VERSAO_PRINCIPAL) >= 21:
        return conv_traf, conv_copy, conv_wpp, lista_tabs, bar_sexo, bar_filhos, bar_civil, bar_exp, graf_age, graf_ren, graf_pat, graf_inv, disc_grafs
    elif PRODUTO == 'EI':
        return conv_traf, conv_copy, conv_wpp, lista_tabs, bar_sexo, bar_filhos, bar_civil, bar_exp, graf_ren, graf_pat, graf_inv, disc_grafs
    elif PRODUTO == 'SC':
        return conv_traf, conv_wpp, lista_tabs, graf_ren, graf_pat

def get_page_metrics(slug, start_date, end_date):
    # Cria o objeto de credencial a partir do secrets
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["analytics_credentials"]
    )

    if PRODUTO == 'EI':
        PROPERTY_ID = "266766007"  # Coloca aqui o número da propriedade GA4
    elif PRODUTO == 'SC':
        PROPERTY_ID = "273168895"
    
    client = BetaAnalyticsDataClient(credentials=credentials)
    #st.write(slug, start_date, end_date, PROPERTY_ID)

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="totalUsers")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.PARTIAL_REGEXP,
                    value=slug,
                )
            )
        )
    )

    response = client.run_report(request)

    return response

def get_conversion_data(slug, start_date="2024-01-01", end_date="2024-12-31"):
    response = get_page_metrics(slug, start_date, end_date)
    #st.write(response)
    data = []
    for row in response.rows:
        users = int(row.metric_values[0].value)
        
        data.append({
            "landing_page": row.dimension_values[0].value,
            "users": users
        })

    df = pd.DataFrame(data)

    return df

def get_conversions_by_campaign(conversion_slug="/cg/inscricao-pendente", start_date="2025-01-01", end_date="2025-12-31"):
    # Autenticação
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["analytics_credentials"]
    )

    if PRODUTO == 'EI':
        PROPERTY_ID = "266766007"
    elif PRODUTO == 'SC':
        PROPERTY_ID = "273168895"

    client = BetaAnalyticsDataClient(credentials=credentials)

    # ===== Parte 1: Conversões (/cg/inscricao-pendente) =====
    conversion_request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="sessionCampaignName"),
            Dimension(name="pagePath")
        ],
        metrics=[Metric(name="totalUsers")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.PARTIAL_REGEXP,
                    value=conversion_slug
                )
            )
        )
    )

    conversion_response = client.run_report(conversion_request)

    # ===== Parte 2: Visitas (/cursogratuito) =====
    visitas_request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="sessionCampaignName"),
                    Dimension(name="pagePath")],
        metrics=[Metric(name="totalUsers")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.PARTIAL_REGEXP,
                    value='/cursogratuito'
                )
            )
        )
    )

    visitas_response = client.run_report(visitas_request)



    visitas_response = client.run_report(visitas_request)

    # Processar as conversões
    conversao_data = []
    for row in conversion_response.rows:
        conversao_data.append({
            "campaign": row.dimension_values[0].value or "(not set)",
            "conversions": int(row.metric_values[0].value)
        })

    df_conversoes = pd.DataFrame(conversao_data)

    df_conversoes = df_conversoes.groupby("campaign", as_index=False)["conversions"].sum()

    # Processar as visitas
    visitas_data = []
    for row in visitas_response.rows:
        visitas_data.append({
            "campaign": row.dimension_values[0].value or "(not set)",
            "visitas": int(row.metric_values[0].value)
        })

    df_visitas = pd.DataFrame(visitas_data)

    df_visitas = df_visitas.groupby("campaign", as_index=False)["visitas"].sum()

    # Combinar os dois DataFrames por "campaign"
    df_merged = pd.merge(df_conversoes, df_visitas, on="campaign", how="left")
    df_merged = df_merged.fillna(0)

    return df_merged, df_conversoes, df_visitas

def process_campaign_data(df, versao_principal):
    # Etapa 1: aplicar filtros
    padrao = f"{versao_principal}"
    filtro_principal = (
        df["campaign"].str.contains(padrao, case=False, na=False) &
        df["campaign"].str.contains("Captacao", case=False, na=False)
    )

    df_filtrado = df[filtro_principal].copy()
    df_restante = df[~filtro_principal].copy()  # tudo que NÃO passou no filtro

    # Etapa 2: normalizar nomes das campanhas filtradas
    def normalize_campaign(name):
        name = name.replace("-", "_").replace(".", "_").lower()
        name = re.sub(r"\s+", "_", name)
        name = re.sub(r"[^a-z0-9_]", "", name)
        return name

    df_filtrado["Nome da Campanha"] = df_filtrado["campaign"].apply(normalize_campaign)

    # Etapa 3: agrupar e somar conversões e vistas das campanhas filtradas
    df_grouped = df_filtrado.groupby("Nome da Campanha", as_index=False).agg({
    "visitas": "sum",
    "conversions": "sum"
    })


    # Etapa 4: adicionar linha "outros" com soma das campanhas restantes
    if not df_restante.empty:
        outros_total = df_restante["conversions"].sum()
        visitas_total = df_restante["visitas"].sum()
        df_outros = pd.DataFrame({
            "Nome da Campanha": ["outros"],
            "visitas": [visitas_total],
            "conversions": [outros_total]
        })
        df_grouped = pd.concat([df_grouped, df_outros], ignore_index=True)
        df_grouped["Taxa de conversão (%)"] = round((df_grouped["conversions"]/df_grouped["visitas"])*100, 2)

    return df_grouped






    # request = RunReportRequest(
    #     property=f"properties/{PROPERTY_ID}",
    #     dimensions=[Dimension(name="landingPagePlusQueryString")],
    #     metrics=[Metric(name="conversions"), Metric(name="sessions")],
    #     date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    # )

    # response = client.run_report(request)

    # data = []
    # for row in response.rows:
    #     data.append({
    #         "landing_page": row.dimension_values[0].value,
    #         "conversions": int(row.metric_values[0].value),
    #         "sessions": int(row.metric_values[1].value),
    #         "conversion_rate": round(
    #             int(row.metric_values[0].value) / int(row.metric_values[1].value) * 100, 2
    #         ) if int(row.metric_values[1].value) > 0 else 0
    #     })

    # return pd.DataFrame(data)