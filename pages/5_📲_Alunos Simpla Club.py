import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from urllib.parse import unquote_plus
from datetime import datetime, timedelta
import re


# Função para carregar uma aba específica de uma planilha
def load_sheet(sheet_name, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('autorizador.json', scope)
    client = gspread.authorize(creds)
    # Abrir a planilha Google
    worksheet = client.open(sheet_name).worksheet(worksheet_name)
    # Obter todos os dados da aba
    data = worksheet.get_all_values()
    # Converter os dados em um DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

# Lendo a planilha 'ALUNOS EI' e a aba 'ALUNOS'
df_ALUNOS = load_sheet('ALUNOS SC', 'ALUNOS')
# Remover '*' dos cabeçalhos e deixar todos UPPERCASE
df_ALUNOS.columns = [col.replace('*', '').upper() for col in df_ALUNOS.columns]
df_ALUNOS = df_ALUNOS.replace('Entre R$5 mil e R$20 mil','Abaixo de R$20 mil')
df_ALUNOS = df_ALUNOS.replace('Menos de R$5 mil','Abaixo de R$20 mil')
df_ALUNOS = df_ALUNOS.replace('Entre R$20 e R$100 mil','Abaixo de R$100 mil')
df_ALUNOS = df_ALUNOS.replace('Entre R$250 e R$500 mil','Entre R$250mil e R$500 mil')
df_ALUNOS = df_ALUNOS.replace('Entre R$5 mil e R$20 mil','Abaixo de R$20 mil')
df_ALUNOS = df_ALUNOS.replace('Entre R$100 mil  e R$250 mil','Entre R$100 mil e R$250 mil')
df_ALUNOS = df_ALUNOS.replace('Entre R$250mil e R$500 mil','Entre R$250 mil e R$500 mil')
df_ALUNOS = df_ALUNOS.replace('Entre R$20 mil e R$100 mil','Abaixo de R$100 mil')
df_ALUNOS = df_ALUNOS.replace('Entre R$100 e R$250 mil','Entre R$100 mil e R$250 mil')
df_ALUNOS = df_ALUNOS.replace('Entre R$5 e R$20 mil','Abaixo de R$20 mil')

# Preencher campos vazios com 'NÃO INFORMADO'
df_ALUNOS.replace('', 'NÃO INFORMADO', inplace=True)

# Função para extrair a tag 'aluno-EI**'
def extract_turma(tags):
    match = re.search(r'aluno-SC\d+', tags)
    return match.group(0) if match else 'NÃO INFORMADO'

# Criar a nova coluna 'TURMA' com base na coluna 'TAGS'
df_ALUNOS['TURMA'] = df_ALUNOS['TAGS'].apply(extract_turma)

# Seção para Eu Investidor
st.title("SIMPLA CLUB")

# Texto e dropdown
st.markdown("### Selecione um lançamento:")
turmas = df_ALUNOS['TURMA'].unique().tolist()
turmas.sort()
turmas.insert(0, 'TODAS')
lançamento_selecionado = st.selectbox('', options=turmas)

# Filtrar os dados com base na seleção do lançamento
if lançamento_selecionado != 'TODAS':
    df_ALUNOS = df_ALUNOS[df_ALUNOS['TURMA'] == lançamento_selecionado]

# Número de alunos
num_alunos = df_ALUNOS.shape[0]
st.markdown(f"### Número de alunos: {num_alunos}")

# Espaço para a próxima seção
st.write("---")


# Contar as respostas na coluna 'SEXO'
sexo_counts = df_ALUNOS['SEXO'].value_counts()
sexo_counts['Outros'] = sexo_counts[~sexo_counts.index.isin(['Masculino', 'Feminino', 'NÃO INFORMADO'])].sum()

# Verificar se 'NÃO INFORMADO' está no índice, senão adicionar manualmente
if 'NÃO INFORMADO' not in sexo_counts.index:
    sexo_counts['NÃO INFORMADO'] = 0

# Ordenar os resultados conforme necessário
sexo_counts = sexo_counts[['Masculino', 'Feminino', 'NÃO INFORMADO']]

# Criar DataFrame com as contagens
df_sexo = pd.DataFrame(sexo_counts).reset_index()
df_sexo.columns = ['Sexo', 'Contagem']

# Função para criar gráfico de barras estilizado
def styled_bar_chart(df, title, colors, horizontal=False):
    fig, ax = plt.subplots()
    if horizontal:
        ax.barh(df.iloc[:, 0], df['Contagem'], color=colors)
    else:
        ax.bar(df.iloc[:, 0], df['Contagem'], color=colors)
        plt.xticks(rotation=45, ha='right')  # Rotacionar as legendas do eixo x
    ax.set_facecolor('none')
    fig.patch.set_facecolor('none')
    ax.spines['bottom'].set_color('#FFFFFF')
    ax.spines['top'].set_color('#FFFFFF')
    ax.spines['right'].set_color('#FFFFFF')
    ax.spines['left'].set_color('#FFFFFF')
    ax.tick_params(axis='x', colors='#FFFFFF')
    ax.tick_params(axis='y', colors='#FFFFFF')
    ax.set_title(title, color='#FFFFFF')
    ax.set_ylabel('Quantidade', color='#FFFFFF')
    ax.set_xlabel(df.columns[0], color='#FFFFFF')
    plt.setp(ax.get_xticklabels(), color="#FFFFFF")
    plt.setp(ax.get_yticklabels(), color="#FFFFFF")
    return fig

# Contar as respostas na coluna 'IDADE'
idade_counts = df_ALUNOS['IDADE'].value_counts()

# Criar DataFrame com as contagens
df_idade = pd.DataFrame(idade_counts).reset_index()
df_idade.columns = ['Idade', 'Contagem']

# Ordenar os dados conforme a faixa etária especificada
faixa_etaria_order = ['Menos de 18', 'Entre 18 a 24', 'Entre 25 a 34', 'Entre 35 a 44', 'Entre 45 a 54', 'Mais de 55', 'NÃO INFORMADO']
df_idade['Idade'] = pd.Categorical(df_idade['Idade'], categories=faixa_etaria_order, ordered=True)
df_idade = df_idade.sort_values('Idade').reset_index(drop=True)

# Exibir os dados em colunas
st.title("PERFIL DOS ALUNOS")

# Seção para Sexo
st.subheader("Sexo")
col1, col2 = st.columns([1, 1])

with col1:
    st.dataframe(df_sexo)

with col2:
    figsexo = styled_bar_chart(df_sexo, "Distribuição por Sexo", ['#5F9EA0', '#DC143C', '#A9A9A9'])
    st.pyplot(figsexo)

# Seção para Faixa Etária
st.subheader("Faixa Etária")
col3, col4 = st.columns([1, 1])

with col3:
    st.dataframe(df_idade)

with col4:
    figidade = styled_bar_chart(df_idade, "Distribuição por Idade", ['#1E90FF', '#FF6347', '#A9A9A9', '#FFD700', '#32CD32', '#8A2BE2', '#FF4500'], horizontal=True)
    st.pyplot(figidade)

# Contar as respostas na coluna 'FINAN - PATRIMÔNIO TOTAL'
patrimonio_counts = df_ALUNOS['FINAN - PATRIMÔNIO TOTAL'].value_counts()

# Criar DataFrame com as contagens
df_patrimonio = pd.DataFrame(patrimonio_counts).reset_index()
df_patrimonio.columns = ['Patrimônio', 'Contagem']

# Ordenar os dados conforme o patrimônio especificado
patrimonio_order = ['NÃO INFORMADO', 'Abaixo de R$20 mil', 'Abaixo de R$100 mil', 'Entre R$100 mil e R$250 mil', 'Entre R$250 mil e R$500 mil', 'Entre R$500 mil e R$1 milhão', 'Acima de R$1 milhão']
df_patrimonio['Patrimônio'] = pd.Categorical(df_patrimonio['Patrimônio'], categories=patrimonio_order, ordered=True)
df_patrimonio = df_patrimonio.sort_values('Patrimônio').reset_index(drop=True)


# Seção para Patrimônio Total
st.subheader("Patrimônio Total")
col5, col6 = st.columns([1, 1])

with col5:
    st.dataframe(df_patrimonio)

with col6:
    figpatrimonio = styled_bar_chart(df_patrimonio, "Distribuição por Patrimônio Total", ['#1E90FF', '#FF6347', '#A9A9A9', '#FFD700', '#32CD32', '#8A2BE2', '#FF4500'])
    st.pyplot(figpatrimonio)
