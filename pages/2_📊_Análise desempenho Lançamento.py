import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from urllib.parse import unquote_plus

# Configuração da página do Streamlit
st.set_page_config(
    layout="wide",
    page_title="Análises Simpla Invest",
    page_icon="💎"
)


# Estilização das abas
st.markdown(
    """
    <style>
    .css-1n543e5 {  /* class for tab buttons */
        border-radius: 8px !important;
        margin-right: 8px !important;
    }
    .css-1n543e5:hover {  /* class for tab buttons on hover */
        background-color: #f0f0f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Função para carregar as quatro primeiras abas de uma planilha
def load_first_four_sheets(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('autorizador.json', scope)
    client = gspread.authorize(creds)
    # Abrir a planilha Google
    sheet = client.open(sheet_name)
    # Obter todas as abas e pegar as quatro primeiras
    all_sheets = sheet.worksheets()[:4]
    data_frames = {}
    for worksheet in all_sheets:
        data = worksheet.get_all_records()
        df_name = f"df_{worksheet.title.replace(' ', '_')}"
        df = pd.DataFrame(data)
        df.replace('', pd.NA, inplace=True)
        df.fillna('não informado', inplace=True)
        data_frames[df_name] = df
    return data_frames

# Função para carregar uma aba específica de uma planilha
def load_sheet(sheet_name, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('autorizador.json', scope)
    client = gspread.authorize(creds)
    # Abrir a planilha Google
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    # Obter todos os dados da aba
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df.replace('', pd.NA, inplace=True)
    df.fillna('não informado', inplace=True)
    return df

# Função para estilizar e exibir gráficos com fundo transparente e letras brancas
def styled_bar_chart(x, y, title, color=['blue', 'orange']):
    fig, ax = plt.subplots()
    ax.bar(x, y, color=color)
    ax.set_facecolor('none')  # Fundo do gráfico transparente
    fig.patch.set_facecolor('none')  # Fundo da figura transparente
    ax.spines['bottom'].set_color('#FFFFFF')
    ax.spines['top'].set_color('#FFFFFF')
    ax.spines['right'].set_color('#FFFFFF')
    ax.spines['left'].set_color('#FFFFFF')
    ax.tick_params(axis='x', colors='#FFFFFF')
    ax.tick_params(axis='y', colors='#FFFFFF')
    ax.set_title(title, color='#FFFFFF')
    ax.set_ylabel('Quantidade', color='#FFFFFF')
    ax.set_xlabel(' ', color='#FFFFFF')
    plt.setp(ax.get_xticklabels(), color="#FFFFFF")
    plt.setp(ax.get_yticklabels(), color="#FFFFFF")
    return fig

# Perguntar qual lançamento a pessoa gostaria de analisar
st.write('Qual Lançamento você quer analisar?')

# Dropdown para selecionar o produto
produto = st.selectbox('Produto', ['EI', 'SC'])

# Dropdown para selecionar a versão
versao = st.selectbox('Versão', list(range(1, 31)))

# Botão para continuar para a análise
if st.button("Continuar para Análise"):
    # Formatar os inputs do usuário
    lancamento1 = f"{produto}.{str(versao).zfill(2)}"
    spreadsheet_central = lancamento1 + ' - CENTRAL DO UTM'
    spreadsheet_pesquisa_copy = lancamento1 + ' - PESQUISA COPY'

    st.write(f"Lançamento selecionado: {lancamento1}")
    st.write(f"Planilha Central: {spreadsheet_central}")
    st.write(f"Planilha Pesquisa Copy: {spreadsheet_pesquisa_copy}")

    spreadsheet_captura = lancamento1 + ' - CENTRAL DO UTM'
    spreadsheet_pesquisa = lancamento1 + ' - PESQUISA TRAFEGO'

    try:
        # Carregar dados das quatro primeiras abas da planilha de captura
        captura_data_frames = load_first_four_sheets(spreadsheet_captura)
        st.success("Planilhas de captura carregadas com sucesso!")                                   
        
        worksheet_pesquisa = "DADOS"
        try:
            # Carregar dados da planilha de pesquisa
            df_PESQUISA = load_sheet(spreadsheet_pesquisa, worksheet_pesquisa)
            st.success("Planilha de pesquisa carregada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao carregar a planilha de pesquisa: {e}")

        # Verifica se ambas as planilhas foram carregadas
        if captura_data_frames and not df_PESQUISA.empty:
            # Variáveis locais para contagem
            leads_totais_captura = len(captura_data_frames.get('df_CAPTURA', []))
            vendas_totais = len(captura_data_frames.get('df_VENDAS', []))
            leads_totais_pesquisa = len(df_PESQUISA)

            # Calcular conversões
            conversao_geral = (vendas_totais / leads_totais_captura) * 100 if leads_totais_captura > 0 else 0
            conversao_captura_pesquisa = (leads_totais_pesquisa / leads_totais_captura) * 100 if leads_totais_captura > 0 else 0

            # Criar DataFrame com os dados e valores
            data = {
                'DADO': ['Leads Totais Captura', 'Vendas Totais', 'Conversão Geral do Lançamento', 'Leads Totais Pesquisa', 'Conversão Captura/Pesquisa'],
                'VALOR': [leads_totais_captura, vendas_totais, f"{conversao_geral:.2f}%", leads_totais_pesquisa, f"{conversao_captura_pesquisa:.2f}%"]
            }
            df_dados = pd.DataFrame(data)
            
            # Abas para navegação
            tabs = st.tabs(["Dados Gerais do Lançamento", "Conversão Leads x Alunos por Faixa Patrimonial", "Análise de Percurso dos Leads"])

            with tabs[0]:
                st.subheader("DADOS GERAIS DO LANÇAMENTO")
                col1, col2, col3 = st.columns([1,0.2,1])

                with col1:
                    st.markdown("### Dados de Vendas")
                    st.markdown(f"**Leads Totais Captura:** {leads_totais_captura}")
                    st.markdown(f"**Vendas Totais:** {vendas_totais}")
                    st.markdown(f"**Conversão Geral do Lançamento:** {conversao_geral:.2f}%")
                    
                    # Gráfico de barras mostrando o número de leads e vendas
                    fig = styled_bar_chart(['Leads Totais Captura', 'Vendas Totais'], [leads_totais_captura, vendas_totais], 'Leads Totais Captura vs Vendas Totais')
                    st.pyplot(fig)

                with col3:
                    st.markdown("### Dados de Pesquisa")
                    st.markdown(f"**Leads Totais Captura:** {leads_totais_captura}")
                    st.markdown(f"**Leads Totais Pesquisa:** {leads_totais_pesquisa}")
                    st.markdown(f"**Conversão Captura/Pesquisa:** {conversao_captura_pesquisa:.2f}%")
                    
                    # Gráfico de barras mostrando o número de leads de captura e pesquisa
                    fig = styled_bar_chart(['Leads Totais Captura', 'Leads Totais Pesquisa'], [leads_totais_captura, leads_totais_pesquisa], 'Leads Totais Captura vs Leads Totais Pesquisa')
                    st.pyplot(fig)
            
            with tabs[1]:
                # Definindo a ordem das categorias para PATRIMÔNIO e RENDA MENSAL
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
                df_PESQUISA['PATRIMÔNIO'] = pd.Categorical(df_PESQUISA['PATRIMÔNIO'], categories=categorias_patrimonio, ordered=True)
                df_PESQUISA['RENDA MENSAL'] = pd.Categorical(df_PESQUISA['RENDA MENSAL'], categories=categorias_renda, ordered=True)

                # Recriando a tabela cruzada com as colunas categóricas ordenadas
                tabela_cruzada1_ordenada = pd.crosstab(df_PESQUISA['PATRIMÔNIO'], df_PESQUISA['RENDA MENSAL'])

                # Definindo variável total para a aba de vendas
                df_VENDAS = captura_data_frames['df_VENDAS']
                df_VENDAS['PATRIMÔNIO'] = pd.Categorical(df_VENDAS['PATRIMÔNIO'], categories=categorias_patrimonio, ordered=True)
                df_VENDAS['RENDA MENSAL'] = pd.Categorical(df_VENDAS['RENDA MENSAL'], categories=categorias_renda, ordered=True)
                tabela_cruzada1_vendas = pd.crosstab(df_VENDAS['PATRIMÔNIO'], df_VENDAS['RENDA MENSAL'])
                
                # Empilhando a tabela cruzada para transformar em um DataFrame com uma coluna para as combinações
                # e outra para os resultados (contagens)
                tabela_empilhada = tabela_cruzada1_ordenada.stack().reset_index()
                tabela_empilhada_vendas = tabela_cruzada1_vendas.stack().reset_index()

                # Renomeando as colunas do novo DataFrame para refletir o conteúdo
                tabela_empilhada.columns = ['PATRIMÔNIO', 'RENDA MENSAL', 'LEADS']
                tabela_empilhada_vendas.columns = ['PATRIMÔNIO', 'RENDA MENSAL', 'ALUNOS']

                # Criando uma nova coluna que combina 'PATRIMÔNIO' e 'RENDA MENSAL' em uma única string
                tabela_empilhada['FAIXA PATRIMÔNIO x RENDA MENSAL'] = tabela_empilhada['PATRIMÔNIO'].astype(str) + ' x ' + tabela_empilhada['RENDA MENSAL'].astype(str)
                tabela_empilhada_vendas['FAIXA PATRIMÔNIO x RENDA MENSAL'] = tabela_empilhada_vendas['PATRIMÔNIO'].astype(str) + ' x ' + tabela_empilhada['RENDA MENSAL'].astype(str)

                # Selecionando apenas as colunas de interesse para o novo DataFrame
                tabela_final = tabela_empilhada[['FAIXA PATRIMÔNIO x RENDA MENSAL', 'LEADS']]
                tabela_final_vendas = tabela_empilhada_vendas[['FAIXA PATRIMÔNIO x RENDA MENSAL', 'ALUNOS']]

                # Combinando as duas tabelas finais em uma única tabela
                tabela_combined = pd.merge(tabela_final, tabela_final_vendas, on='FAIXA PATRIMÔNIO x RENDA MENSAL', how='outer').fillna(0)

                # Adicionando a coluna de conversão
                tabela_combined['CONVERSÃO'] = (tabela_combined['ALUNOS'] / tabela_combined['LEADS']) * 100
                tabela_combined['CONVERSÃO'] = tabela_combined['CONVERSÃO'].apply(lambda x: f"{x:.2f}%")

                # Ordenando a tabela_combined pela ordem das categorias originais
                tabela_combined['PATRIMÔNIO'] = pd.Categorical(
                    tabela_combined['FAIXA PATRIMÔNIO x RENDA MENSAL'].str.split(' x ').str[0],
                    categories=categorias_patrimonio,
                    ordered=True
                )
                tabela_combined['RENDA MENSAL'] = pd.Categorical(
                    tabela_combined['FAIXA PATRIMÔNIO x RENDA MENSAL'].str.split(' x ').str[1],
                    categories=categorias_renda,
                    ordered=True
                )
                tabela_combined = tabela_combined.sort_values(by=['PATRIMÔNIO', 'RENDA MENSAL']).reset_index(drop=True)

                # Exibindo a nova tabela combinada e os gráficos lado a lado
                st.subheader("CONVERSÃO LEADS X ALUNOS POR FAIXA PATRIMONIAL")
                col1, col2 = st.columns([3, 2])
                with col1:
                    # Função para aplicar estilos
                    def color_rows(row):
                        colors = {
                            'Menos de R$5 mil': 'background-color: #660000',  # Dark Red (darker)
                            'Entre R$5 mil e R$20 mil': 'background-color: #8B1A1A',  # Dark Brown (darker)
                            'Entre R$20 mil e R$100 mil': 'background-color: #8F6500',  # Dark Goldenrod (darker)
                            'Entre R$100 mil e R$250 mil': 'background-color: #445522',  # Dark Olive Green (darker)
                            'Entre R$250 mil e R$500 mil': 'background-color: #556B22',  # Olive Drab (darker)
                            'Entre R$500 mil e R$1 milhão': 'background-color: #000070',  # Dark Blue (darker)
                            'Acima de R$1 milhão': 'background-color: #2F4F4F'  # Dark Slate Gray
                        }
                        return [colors.get(row['PATRIMÔNIO'], '')] * len(row)

                    # Aplicar estilo
                    styled_df = tabela_combined.style.apply(color_rows, axis=1)
                    st.dataframe(styled_df)                                                                        

                with col2:
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

                    # Gráfico de barras para Conversão por Faixa de Patrimônio
                    tabela_combined['CONVERSÃO_NUM'] = tabela_combined['CONVERSÃO'].str.rstrip('%').astype('float')
                    ax1.bar(tabela_combined['PATRIMÔNIO'], tabela_combined['CONVERSÃO_NUM'])
                    ax1.set_title('Conversão por Faixa de Patrimônio', color='#FFFFFF')
                    ax1.set_ylabel('Conversão (%)', color='#FFFFFF')
                    ax1.set_xticklabels(tabela_combined['PATRIMÔNIO'], rotation=45, ha='right', color='#FFFFFF')
                    ax1.set_facecolor('none')  # Fundo do gráfico transparente
                    fig.patch.set_facecolor('none')  # Fundo da figura transparente
                    ax1.spines['bottom'].set_color('#FFFFFF')
                    ax1.spines['top'].set_color('#FFFFFF')
                    ax1.spines['right'].set_color('#FFFFFF')
                    ax1.spines['left'].set_color('#FFFFFF')
                    ax1.tick_params(axis='x', colors='#FFFFFF')
                    ax1.tick_params(axis='y', colors='#FFFFFF')

                    # Gráfico de barras para Número Bruto de Alunos por Faixa de Patrimônio
                    ax2.bar(tabela_combined['PATRIMÔNIO'], tabela_combined['ALUNOS'])
                    ax2.set_title('Número Bruto de Alunos por Faixa de Patrimônio', color='#FFFFFF')
                    ax2.set_ylabel('Número de Alunos', color='#FFFFFF')
                    ax2.set_xticklabels(tabela_combined['PATRIMÔNIO'], rotation=45, ha='right', color='#FFFFFF')
                    ax2.set_facecolor('none')  # Fundo do gráfico transparente
                    fig.patch.set_facecolor('none')  # Fundo da figura transparente
                    ax2.spines['bottom'].set_color('#FFFFFF')
                    ax2.spines['top'].set_color('#FFFFFF')
                    ax2.spines['right'].set_color('#FFFFFF')
                    ax2.spines['left'].set_color('#FFFFFF')
                    ax2.tick_params(axis='x', colors='#FFFFFF')
                    ax2.tick_params(axis='y', colors='#FFFFFF')

                    plt.tight_layout()
                    st.pyplot(fig)
            
            with tabs[2]:
                # Criar a coluna 'PERCURSO' no DataFrame df_VENDAS sem alterar o original
                df_vendas_copy = df_VENDAS.copy()

                # Modificar o campo 'CAP UTM_SOURCE' se for igual a 'ig'
                df_vendas_copy['CAP UTM_SOURCE'] = df_vendas_copy.apply(
                    lambda x: f"{x['CAP UTM_SOURCE']} {x['CAP UTM_MEDIUM']}" if x['CAP UTM_SOURCE'] == 'ig' else x['CAP UTM_SOURCE'],
                    axis=1
                )

                # Concatenar os campos para formar o campo 'PERCURSO'
                df_vendas_copy['PERCURSO'] = df_vendas_copy['CAP UTM_SOURCE'].astype(str) + ' > ' + \
                                            df_vendas_copy['PM UTM_SOURCE'].astype(str) + ' > ' + \
                                            df_vendas_copy['UTM_SOURCE'].astype(str)

                # Contar os valores de 'PERCURSO' e ordenar do maior para o menor
                percurso_counts = df_vendas_copy['PERCURSO'].value_counts().reset_index()
                percurso_counts.columns = ['PERCURSO', 'COUNT']

                # Mostrar apenas os 20 primeiros resultados
                top_20_percurso = percurso_counts.head(20)

                # Exibir a análise de percurso de leads
                st.subheader("Análise de Percurso de Leads")
                col1, col2 = st.columns([3, 2])

                with col1:
                    st.table(top_20_percurso)

                # Preparar dados para o gráfico de barras
                top_5_percurso = top_20_percurso.head(5).sort_values(by='COUNT', ascending=True)

                with col2:
                    fig, ax = plt.subplots()
                    
                    # Gerar tons de azul para as barras
                    colors = cm.Blues(np.linspace(0.4, 1, len(top_5_percurso)))

                    ax.barh(top_5_percurso['PERCURSO'], top_5_percurso['COUNT'], color=colors)
                    ax.set_xlabel('Count', color='#FFFFFF')
                    ax.set_ylabel('PERCURSO', color='#FFFFFF')
                    ax.set_title('Top 5 Percursos Mais Comuns', color='#FFFFFF')
                    ax.set_facecolor('none')  # Fundo do gráfico transparente
                    fig.patch.set_facecolor('none')  # Fundo da figura transparente
                    ax.spines['bottom'].set_color('#FFFFFF')
                    ax.spines['top'].set_color('#FFFFFF')
                    ax.spines['right'].set_color('#FFFFFF')
                    ax.spines['left'].set_color('#FFFFFF')
                    ax.tick_params(axis='x', colors='#FFFFFF')
                    ax.tick_params(axis='y', colors='#FFFFFF')
                    plt.tight_layout()
                    st.pyplot(fig)
            
    except Exception as e:
        st.error(f"Erro ao carregar as planilhas de captura: {e}")
