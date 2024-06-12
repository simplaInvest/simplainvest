import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import time

# Função para carregar uma aba específica de uma planilha
def load_sheet(sheet_name, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('autorizador.json', scope)
    client = gspread.authorize(creds)
    # Open the Google spreadsheet
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    # Get all data from the sheet
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Perguntar qual lançamento a pessoa gostaria de analisar
st.write('Qual o Lançamento em Questão?')

# Dropdown para selecionar o produto
produto = st.selectbox('Produto', ['EI', 'SC'])

# Dropdown para selecionar a versão
versao = st.selectbox('Versão', list(range(1, 31)))

# Botão para continuar para a análise
if st.button("Continuar para Análise"):
    # Formatar os inputs do usuário
    lancamentoT = f"{produto}.{str(versao).zfill(2)}"   
    #spreadsheet_pesquisa_copy = lancamento1 + ' - PESQUISA COPY'
    spreadsheet_trafego = lancamentoT + ' - PESQUISA TRAFEGO'
    st.write(f"Lançamento selecionado: {lancamentoT}")
    st.write(f"Planilha Central: {spreadsheet_trafego}")

    # Declarar variáveis de taxas de conversão para as faixas de patrimônio
    taxas_conversao_patrimonio = {
        'Acima de R$1 milhão': 0.0489,
        'Entre R$500 mil e R$1 milhão': 0.0442,
        'Entre R$250 mil e R$500 mil': 0.0400,
        'Entre R$100 mil e R$250 mil': 0.0382,
        'Entre R$20 mil e R$100 mil': 0.0203,
        'Entre R$5 mil e R$20 mil': 0.0142,
        'Menos de R$5 mil': 0.0067
    }
    
    try:
        # Carregar dados da New Meta Ads
        df_METAADS = load_sheet(spreadsheet_trafego, 'NEW META ADs')
        st.success("NEW META ADs carregadas com sucesso!")
        df_METAADS = df_METAADS.astype(str)



        # Garantir que os valores das colunas especificadas sejam numéricos
        colunas_numericas = [
            'CPM', 'VALOR USADO', 'LEADS', 'CPL', 'CTR', 'CONNECT RATE', 
            'CONVERSÃO DA PÁGINA', 'IMPRESSÕES', 'ALCANCE', 'FREQUÊNCIA', 
            'CLICKS', 'CLICKS NO LINK', 'PAGEVIEWS', 'LP CTR', 'PERFIL CTR', 
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 
            '13', '14', '15-20', '20-25', '25-30', '30-40', '40-50', '50-60', '60+'
        ]

        for coluna in colunas_numericas:
            df_METAADS[coluna] = df_METAADS[coluna].str.replace('.', '', regex=False)  # Remove separador de milhar
            df_METAADS[coluna] = df_METAADS[coluna].str.replace(',', '.', regex=False)  # Substitui separador decimal
            df_METAADS[coluna] = pd.to_numeric(df_METAADS[coluna], errors='coerce')

        try:
            # Carregar dados de Anúncios Subidos
            df_SUBIDOS = load_sheet(spreadsheet_trafego, 'ANUNCIOS SUBIDOS')
            st.success("Anúncios Subidos carregado com sucesso!")

            try:
                # Carregar dados de pesquisa
                df_PESQUISA = load_sheet(spreadsheet_trafego, 'DADOS')
                st.success("Dados carregado com sucesso!")

                # Criar o novo DataFrame com as colunas especificadas
                
                ticket = 1490*0.7
                
                
                columns = [
                    'ANÚNCIO', 'TOTAL DE LEADS', 'TOTAL DE PESQUISA',
                    'CUSTO POR LEAD', 'PREÇO MÁXIMO', 'DIFERENÇA', 'MARGEM', 'VALOR USADO', 
                    'CPM', 'CTR', 'CONNECT RATE', 'CONVERSÃO PÁG', 'Acima de R$1 milhão',
                    'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil', 
                    'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil', 
                    'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil', 'TAXA DE RESPOSTA'
                ]
                # Criar um DataFrame vazio com todas as colunas especificadas
                df_PORANUNCIO = pd.DataFrame(columns=columns)

                # Obter valores únicos da coluna 'ANÚNCIO: NOME'
                anuncios_unicos = df_METAADS['ANÚNCIO: NOME'].unique()

                # Preencher a coluna 'ANÚNCIO' com valores únicos
                df_PORANUNCIO['ANÚNCIO'] = pd.Series(anuncios_unicos)

                # Calcular 'TOTAL DE LEADS'
                df_PORANUNCIO['TOTAL DE LEADS'] = df_PORANUNCIO['ANÚNCIO'].apply(
                    lambda anuncio: df_METAADS[df_METAADS['ANÚNCIO: NOME'] == anuncio]['LEADS'].sum()
                )

                # Calcular 'TOTAL DE PESQUISA'
                df_PORANUNCIO['TOTAL DE PESQUISA'] = df_PORANUNCIO['ANÚNCIO'].apply(
                    lambda anuncio: df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0]                    
                )

                
                start_time = time.time()
                # Lista das faixas de patrimônio
                faixas_patrimonio = [
                    'Acima de R$1 milhão', 'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
                    'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil', 'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil'
                ]

                # Calcular as colunas de faixas de patrimônio
                for faixa in faixas_patrimonio:
                    df_PORANUNCIO[faixa] = df_PORANUNCIO['ANÚNCIO'].apply(
                        lambda anuncio: (
                            df_PESQUISA[(df_PESQUISA['UTM_TERM'] == anuncio) & 
                                        (df_PESQUISA['PATRIMÔNIO'] == faixa)].shape[0] / 
                            df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0]
                        ) if df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0] != 0 else 0
                    )
                end_time = time.time()
                execution_time = end_time - start_time    
                st.write("Tempo de execução do código otimizado:", execution_time)

                #calcular 'PREÇO MÁXIMO'
                df_PORANUNCIO['PREÇO MÁXIMO'] = ticket*(
                    taxas_conversao_patrimonio['Acima de R$1 milhão'] * df_PORANUNCIO['Acima de R$1 milhão'] +
                    taxas_conversao_patrimonio['Entre R$500 mil e R$1 milhão']*df_PORANUNCIO['Entre R$500 mil e R$1 milhão'] +
                    taxas_conversao_patrimonio['Entre R$250 mil e R$500 mil']*df_PORANUNCIO['Entre R$250 mil e R$500 mil'] +
                    taxas_conversao_patrimonio['Entre R$100 mil e R$250 mil']*df_PORANUNCIO['Entre R$100 mil e R$250 mil'] +
                    taxas_conversao_patrimonio['Entre R$20 mil e R$100 mil']*df_PORANUNCIO['Entre R$20 mil e R$100 mil'] +
                    taxas_conversao_patrimonio['Entre R$5 mil e R$20 mil']*df_PORANUNCIO['Entre R$5 mil e R$20 mil'] +
                    taxas_conversao_patrimonio['Menos de R$5 mil']*df_PORANUNCIO['Menos de R$5 mil']
                )

                #calcular 'VALOR USADO'
                df_PORANUNCIO['VALOR USADO'] = df_PORANUNCIO['ANÚNCIO'].apply(
                    lambda anuncio: df_METAADS[df_METAADS['ANÚNCIO: NOME'] == anuncio]['VALOR USADO'].sum()
                )

                #calcular 'DIFERENÇA'            
                df_PORANUNCIO['DIFERENÇA'] = df_PORANUNCIO['PREÇO MÁXIMO'] - df_PORANUNCIO['CUSTO POR LEAD']

                st.header('TA ERRADO O PREÇO MAXIMO DEPOIS CORRIJA')
                # Exibir o novo DataFrame
                st.dataframe(df_PORANUNCIO)

                df_lalala = []
                df_lalala = pd.DataFrame(df_lalala)
                df_lalala['teste'] = df_METAADS['VALOR USADO']*2

                    
                # Comentar a exibição dos outros dataframes
                # st.dataframe(df_PESQUISA)
                # st.dataframe(df_SUBIDOS)
                st.dataframe(df_METAADS)
                st.dataframe(df_lalala)

            except Exception as e:
                st.error(f"Erro ao carregar a planilha de pesquisa: {e}")

        except Exception as e:
            st.error(f"Erro ao carregar a planilha de Anúncios Subidos: {e}")

    except Exception as e:
        st.error(f"Erro ao carregar a planilha de New Meta Ads: {e}")
