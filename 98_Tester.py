import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Cacheamento de Processamento de Dados

def authenticate():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('autorizador.json', scope)
    client = gspread.authorize(creds)
    return client

def make_unique(columns):
    # Cria cabeçalhos únicos para evitar duplicidades
    counts = {}
    unique_columns = []
    for col in columns:
        if col in counts:
            counts[col] += 1
            unique_columns.append(f"{col}_{counts[col]}")
        else:
            counts[col] = 0
            unique_columns.append(col)
    return unique_columns

def load_sheet(sheet_name, worksheet_name, chunk_size=10000):
    client = authenticate()

    # Abre a planilha
    spreadsheet = client.open(sheet_name)
    worksheet = spreadsheet.worksheet(worksheet_name)
    
    # Obtém o número total de linhas
    all_data = worksheet.get_all_values()
    total_rows = len(all_data)
    
    # Lista para armazenar os DataFrames
    df_list = []

    # Cabeçalhos únicos
    columns = make_unique(all_data[0])

    # Lê os dados em chunks
    start_row = 1  # Começa após o cabeçalho
    while start_row < total_rows:
        end_row = min(start_row + chunk_size, total_rows)
        data_chunk = all_data[start_row:end_row]
        if data_chunk:  # Verifica se o chunk não está vazio
            df_chunk = pd.DataFrame(data_chunk, columns=columns)
            df_list.append(df_chunk)
        start_row = end_row
    
    # Verifica se df_list não está vazio antes de concatenar
    if df_list:
        final_df = pd.concat(df_list, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=columns)  # Retorna um DataFrame vazio com os mesmos cabeçalhos

    return final_df



# Estilização das abas
st.markdown(
    """
    <style>
    .css-1n543e5 { 
        border-radius: 8px !important;
        margin-right: 8px !important;
    }
    .css-1n543e5:hover {  
        background-color: #f0f0f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

lancamento = "SC.09"

# Verifique se os dados foram carregados
df_PESQUISA = load_sheet( lancamento + ' - PESQUISA TRAFEGO', 'DADOS')
df_CAPTURA = load_sheet(lancamento + ' - CENTRAL DO UTM', 'CAPTURA')
df_VENDAS = load_sheet(lancamento + ' - CENTRAL DO UTM', 'VENDAS')
    

# Calcular conversões

total_pesquisa = len(df_PESQUISA)
total_captura = len(df_CAPTURA)
total_vendas = len(df_VENDAS)

conversao_pesquisa = (total_pesquisa / total_captura) * 100 if total_pesquisa > 0 else 0
conversao_vendas = (total_vendas / total_captura) * 100 if total_vendas > 0 else 0

# Criando tabelas cruzadas PATRIMONIO x RENDA
categorias_patrimonio = [
    'Menos de R$5 mil', 'Entre R$5 mil e R$20 mil', 'Entre R$20 mil e R$100 mil',
    'Entre R$100 mil e R$250 mil', 'Entre R$250 mil e R$500 mil',
    'Entre R$500 mil e R$1 milhão', 'Acima de R$1 milhão'
]
categorias_renda = [
    'Até R$1.500', 'Entre R$1.500 e R$2.500', 'Entre R$2.500 e R$5.000',
    'Entre R$5.000 e R$10.000', 'Entre R$10.000 e R$20.000', 'Acima de R$20.000'
]

df_PESQUISA['PATRIMONIO'] = pd.Categorical(df_PESQUISA['PATRIMONIO'], categories=categorias_patrimonio, ordered=True)
df_PESQUISA['RENDA MENSAL'] = pd.Categorical(df_PESQUISA['RENDA MENSAL'], categories=categorias_renda, ordered=True)

tabela_cruzada1_ordenada = pd.crosstab(df_PESQUISA['PATRIMONIO'], df_PESQUISA['RENDA MENSAL'])

if not df_VENDAS.empty:
    df_VENDAS['PATRIMONIO'] = pd.Categorical(df_VENDAS['PATRIMONIO'], categories=categorias_patrimonio, ordered=True)
    df_VENDAS['RENDA MENSAL'] = pd.Categorical(df_VENDAS['RENDA MENSAL'], categories=categorias_renda, ordered=True)
    tabela_cruzada1_vendas = pd.crosstab(df_VENDAS['PATRIMONIO'], df_VENDAS['RENDA MENSAL'])

    tabela_empilhada = tabela_cruzada1_ordenada.stack().reset_index()
    tabela_empilhada_vendas = tabela_cruzada1_vendas.stack().reset_index()

    tabela_empilhada.columns = ['PATRIMONIO', 'RENDA MENSAL', 'LEADS']
    tabela_empilhada_vendas.columns = ['PATRIMONIO', 'RENDA MENSAL', 'ALUNOS']

    tabela_empilhada['FAIXA PATRIMONIO x RENDA MENSAL'] = tabela_empilhada['PATRIMONIO'].copy().astype(str) + ' x ' + tabela_empilhada['RENDA MENSAL'].astype(str)
    tabela_empilhada_vendas['FAIXA PATRIMONIO x RENDA MENSAL'] = tabela_empilhada_vendas['PATRIMONIO'].astype(str) + ' x ' + tabela_empilhada_vendas['RENDA MENSAL'].astype(str)

    tabela_final = tabela_empilhada[['FAIXA PATRIMONIO x RENDA MENSAL', 'LEADS', 'PATRIMONIO']]
    tabela_final_vendas = tabela_empilhada_vendas[['FAIXA PATRIMONIO x RENDA MENSAL', 'ALUNOS','PATRIMONIO']]
    #st.dataframe(tabela_final)
    #st.dataframe(tabela_final_vendas)
    
    tabela_combined = pd.merge(tabela_final, tabela_final_vendas, on='FAIXA PATRIMONIO x RENDA MENSAL', how='outer')
    tabela_combined[['LEADS', 'ALUNOS']] = tabela_combined[['LEADS', 'ALUNOS']].fillna(0)
    tabela_combined['CONVERSÃO'] = (tabela_combined['ALUNOS'] / tabela_combined['LEADS'])
    #st.dataframe(tabela_combined)

else:
    tabela_empilhada = tabela_cruzada1_ordenada.stack().reset_index()
    tabela_empilhada.columns = ['PATRIMONIO', 'RENDA MENSAL', 'LEADS']
    tabela_empilhada['FAIXA PATRIMONIO x RENDA MENSAL'] = tabela_empilhada['PATRIMONIO'].astype(str) + ' x ' + tabela_empilhada['RENDA MENSAL'].astype(str)
    tabela_combined = tabela_empilhada[['FAIXA PATRIMONIO x RENDA MENSAL', 'LEADS']]
    total_leads = tabela_combined['LEADS'].sum()
    tabela_combined['% DO TOTAL DE LEADS'] = (tabela_combined['LEADS'] / total_leads)
    df_EXIBICAO = tabela_combined.copy()
    df_EXIBICAO['% DO TOTAL DE LEADS'] = df_EXIBICAO['% DO TOTAL DE LEADS']*100
    df_EXIBICAO['% DO TOTAL DE LEADS'] = df_EXIBICAO['% DO TOTAL DE LEADS'].apply(lambda x: f"{x:.2f}%")

tabela_combined['PATRIMONIO'] = pd.Categorical(
    tabela_combined['FAIXA PATRIMONIO x RENDA MENSAL'].str.split(' x ').str[0],
    categories=categorias_patrimonio,
    ordered=True
)
tabela_combined['RENDA MENSAL'] = pd.Categorical(
    tabela_combined['FAIXA PATRIMONIO x RENDA MENSAL'].str.split(' x ').str[1],
    categories=categorias_renda,
    ordered=True
)
tabela_combined = tabela_combined.sort_values(by=['PATRIMONIO', 'RENDA MENSAL']).reset_index(drop=True)

    
tabs = st.tabs(["Dados Gerais do Lançamento" , "Análises de Patrimônio e Renda"])


#--------------------------------------------------------------------------#
# Sessão de exibição dos dados e gráficos

with tabs[0]:
    st.markdown("<h1 style='text-align: center; font-size: 3.2vw; margin-bottom: 40px; margin-top: 40px; color: gold;hover-color: red'>Dados Gerais do Lançamento</h1>", unsafe_allow_html=True)
    st.title("LANÇAMENTO:")
    st.subheader(lancamento)
    st.divider()
    with st.container(border=False):
        st.markdown("<h2 style='text-align: left; font-size: 2vw; margin-bottom: 28px; color: lightblue;hover-color: red'>Métricas Gerais</h1>", unsafe_allow_html=True)
        ctcol1, ctcol2, ctcol3, ctcol4, ctcol5 = st.columns([1, 1, 1, 1, 1])
        with ctcol1:
            st.metric("Leads Totais Captura", total_captura)
        with ctcol2:
            st.metric("Leads Totais Pesquisa", total_pesquisa)
        with ctcol3:
            st.metric("Conversão Geral Pesquisa", f"{conversao_pesquisa:.2f}%")        
        with ctcol4:
            st.metric("Vendas Totais", total_vendas)
        with ctcol5:
            st.metric("Conversão Geral do Lançamento", f'{conversao_vendas:.2f}%')
    
    st.divider()
   

with tabs[1]:     
    if not df_VENDAS.empty:
       st.write("lalala")
    
    st.subheader("CONVERSÃO POR FAIXA DE PATRIMONIO")
    col3, col4 = st.columns([3, 2])
    with col3:
        if not df_VENDAS.empty:
            tabela_patrimonio = tabela_combined.groupby('PATRIMONIO').agg({'LEADS': 'sum', 'ALUNOS': 'sum'}).reset_index()
            tabela_patrimonio['CONVERSÃO'] = (tabela_patrimonio['ALUNOS'] / tabela_patrimonio['LEADS']) * 100
            tabela_patrimonio['CONVERSÃO'] = tabela_patrimonio['CONVERSÃO'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_patrimonio)
        else:
            tabela_patrimonio = tabela_combined.groupby('PATRIMONIO').agg({'LEADS': 'sum'}).reset_index()
            total_leads = tabela_patrimonio['LEADS'].sum()
            tabela_patrimonio['% DO TOTAL DE LEADS'] = (tabela_patrimonio['LEADS'] / total_leads) * 100
            tabela_patrimonio['% DO TOTAL DE LEADS'] = tabela_patrimonio['% DO TOTAL DE LEADS'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_patrimonio)

    with col4:
        if not df_VENDAS.empty:
            fig_patrimonio, ax_patrimonio = plt.subplots()
            tabela_patrimonio['CONVERSÃO_NUM'] = tabela_patrimonio['CONVERSÃO'].str.rstrip('%').astype('float')
            ax_patrimonio.bar(tabela_patrimonio['PATRIMONIO'], tabela_patrimonio['CONVERSÃO_NUM'])
            ax_patrimonio.set_title('Conversão por Faixa de PATRIMONIO', color='#FFFFFF')
            ax_patrimonio.set_ylabel('Conversão (%)', color='#FFFFFF')
            ax_patrimonio.set_xticklabels(tabela_patrimonio['PATRIMONIO'], rotation=45, ha='right', color='#FFFFFF')
            ax_patrimonio.set_facecolor('none')
            fig_patrimonio.patch.set_facecolor('none')
            ax_patrimonio.spines['bottom'].set_color('#FFFFFF')
            ax_patrimonio.spines['top'].set_color('#FFFFFF')
            ax_patrimonio.spines['right'].set_color('#FFFFFF')
            ax_patrimonio.spines['left'].set_color('#FFFFFF')
            ax_patrimonio.tick_params(axis='x', colors='#FFFFFF')
            ax_patrimonio.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_patrimonio)
        else:
            fig_patrimonio, ax_patrimonio = plt.subplots()
            tabela_patrimonio['PERCENTUAL_NUM'] = tabela_patrimonio['% DO TOTAL DE LEADS'].str.rstrip('%').astype('float')
            ax_patrimonio.bar(tabela_patrimonio['PATRIMONIO'], tabela_patrimonio['PERCENTUAL_NUM'])
            ax_patrimonio.set_title('Percentual de LEADS por Faixa de PATRIMONIO', color='#FFFFFF')
            ax_patrimonio.set_ylabel('Percentual (%)', color='#FFFFFF')
            ax_patrimonio.set_xticklabels(tabela_patrimonio['PATRIMONIO'], rotation=45, ha='right', color='#FFFFFF')
            ax_patrimonio.set_facecolor('none')
            fig_patrimonio.patch.set_facecolor('none')
            ax_patrimonio.spines['top'].set_color('#FFFFFF')
            ax_patrimonio.spines['bottom'].set_color('#FFFFFF')
            ax_patrimonio.spines['left'].set_color('#FFFFFF')
            ax_patrimonio.spines['right'].set_color('#FFFFFF')
            ax_patrimonio.tick_params(axis='x', colors='#FFFFFF')
            ax_patrimonio.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_patrimonio)

    st.subheader("CONVERSÃO POR FAIXA DE RENDA")
    col5, col6 = st.columns([3, 2])
    with col5:
        if not df_VENDAS.empty:
            tabela_renda = tabela_combined.groupby('RENDA MENSAL').agg({'LEADS': 'sum', 'ALUNOS': 'sum'}).reset_index()
            tabela_renda['CONVERSÃO'] = (tabela_renda['ALUNOS'] / tabela_renda['LEADS']) * 100
            tabela_renda['CONVERSÃO'] = tabela_renda['CONVERSÃO'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_renda)
        else:
            tabela_renda = tabela_combined.groupby('RENDA MENSAL').agg({'LEADS': 'sum'}).reset_index()
            total_leads = tabela_renda['LEADS'].sum()
            tabela_renda['% DO TOTAL DE LEADS'] = (tabela_renda['LEADS'] / total_leads) * 100
            tabela_renda['% DO TOTAL DE LEADS'] = tabela_renda['% DO TOTAL DE LEADS'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_renda)

    with col6:
        if not df_VENDAS.empty:
            fig_renda, ax_renda = plt.subplots()
            tabela_renda['CONVERSÃO_NUM'] = tabela_renda['CONVERSÃO'].str.rstrip('%').astype('float')
            ax_renda.bar(tabela_renda['RENDA MENSAL'], tabela_renda['CONVERSÃO_NUM'])
            ax_renda.set_title('Conversão por Faixa de Renda', color='#FFFFFF')
            ax_renda.set_ylabel('Conversão (%)', color='#FFFFFF')
            ax_renda.set_xticklabels(tabela_renda['RENDA MENSAL'], rotation=45, ha='right', color='#FFFFFF')
            ax_renda.set_facecolor('none')
            fig_renda.patch.set_facecolor('none')
            ax_renda.spines['bottom'].set_color('#FFFFFF')
            ax_renda.spines['top'].set_color('#FFFFFF')
            ax_renda.spines['right'].set_color('#FFFFFF')
            ax_renda.spines['left'].set_color('#FFFFFF')
            ax_renda.tick_params(axis='x', colors='#FFFFFF')
            ax_renda.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_renda)
        else:
            fig_renda, ax_renda = plt.subplots()
            tabela_renda['PERCENTUAL_NUM'] = tabela_renda['% DO TOTAL DE LEADS'].str.rstrip('%').astype('float')
            ax_renda.bar(tabela_renda['RENDA MENSAL'], tabela_renda['PERCENTUAL_NUM'])
            ax_renda.set_title('Percentual de LEADS por Faixa de Renda', color='#FFFFFF')
            ax_renda.set_ylabel('Percentual (%)', color='#FFFFFF')
            ax_renda.set_xticklabels(tabela_renda['RENDA MENSAL'], rotation=45, ha='right', color='#FFFFFF')
            ax_renda.set_facecolor('none')
            fig_renda.patch.set_facecolor('none')
            ax_renda.spines['bottom'].set_color('#FFFFFF')
            ax_renda.spines['top'].set_color('#FFFFFF')
            ax_renda.spines['right'].set_color('#FFFFFF')
            ax_renda.spines['left'].set_color('#FFFFFF')
            ax_renda.tick_params(axis='x', colors='#FFFFFF')
            ax_renda.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_renda)

    