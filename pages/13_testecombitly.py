import streamlit as st
import pandas as pd
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# Configuração da página do Streamlit
st.set_page_config(
    layout="wide",
    page_title="Análise de Vendas - CENTRAL DO UTM",
    page_icon="📊"
)

# Função para carregar uma aba específica de uma planilha
def load_sheet(sheet_name, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('autorizador.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df.replace('', 'não informado', inplace=True)
    df.fillna('não informado', inplace=True)
    return df

# Função para buscar conteúdo na aba de mensagens
def buscar_conteudo(df_mensagens, utm_term):
    filtro_link = df_mensagens['Link parametrizado'].str.contains(utm_term, na=False)
    return df_mensagens[filtro_link]['Conteúdo'].values

# Função para obter o Group ID do Bitly
def get_bitly_group_id(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api-ssl.bitly.com/v4/groups", headers=headers)
    response.raise_for_status()
    data = response.json()
    return data['groups'][0]['guid']

# Função para obter links do Bitly
def get_bitly_links(access_token, campaign_code, domain="links.simplainvest.com.br"):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    group_id = get_bitly_group_id(access_token)
    params = {
        "size": 100,  # Número de links a serem buscados por página (pode ser ajustado)
        "group_guid": group_id,
        "domain": domain
    }
    links = []

    response = requests.get(f"https://api-ssl.bitly.com/v4/groups/{group_id}/bitlinks", headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    
    for link in data.get('links', []):
        if campaign_code in link['title'] and 'Vendas' in link['title']:
            link_id = link['id']
            click_response = requests.get(f"https://api-ssl.bitly.com/v4/bitlinks/{link_id}/clicks/summary", headers=headers)
            click_response.raise_for_status()
            clicks_data = click_response.json()
            clicks = clicks_data.get('total_clicks', 0)
            # Extrair a data do nome do link
            match = re.search(r'\d{2}/\d{2} \d{2}:\d{2}', link['title'])
            data = match.group(0) if match else 'não informado'
            links.append({
                "Nome": link['title'],
                "Link de Origem": link['long_url'],
                "Número de Cliques": clicks,
                "Data": data
            })

    return pd.DataFrame(links)

# Função para adicionar informações ao dataframe ranking
def adicionar_informacoes(ranking, bitly_links):
    ranking['Número de Cliques'] = ranking['UTM_TERM'].apply(
        lambda utm_term: next((row['Número de Cliques'] for index, row in bitly_links.iterrows() if utm_term in row['Link de Origem']), 0)
    )
    ranking['Data'] = ranking['UTM_TERM'].apply(
        lambda utm_term: next((row['Data'] for index, row in bitly_links.iterrows() if utm_term in row['Link de Origem']), 'não informado')
    )
    return ranking

# Função principal
def main():
    # Inicializa o estado selecionado e a visualização da mensagem se ainda não estiverem no session_state
    if 'selected_utm_term' not in st.session_state:
        st.session_state.selected_utm_term = None
    if 'ver_mensagem' not in st.session_state:
        st.session_state.ver_mensagem = False

    # Perguntar qual lançamento a pessoa gostaria de analisar
    st.write('Qual Lançamento você quer analisar?')

    # Dropdown para selecionar o produto
    produto = st.selectbox('Produto', ['EI', 'SC'])

    # Dropdown para selecionar a versão
    versao = st.selectbox('Versão', list(range(1, 31)))

    # Botão para continuar para a análise
    if st.button("Continuar para Análise"):
        lancamento = f"{produto}.{str(versao).zfill(2)} - CENTRAL DO UTM"
        st.write(f"Lançamento selecionado: {lancamento}")

        try:
            with st.spinner('Carregando...'):
                # Carregar dados da aba 'VENDAS'
                df_vendas = load_sheet(lancamento, 'VENDAS')
                st.session_state.df_vendas = df_vendas

                # Filtrar os dados com base na coluna 'UTM_TERM'
                filtro = f"Whatsapp_EI.{str(versao).zfill(2)}"
                df_filtrado = df_vendas[df_vendas['UTM_TERM'].str.startswith(filtro, na=False)]
                st.session_state.df_filtrado = df_filtrado

                # Criar um DataFrame rankeando os 20 'UTM_TERM' que mais aparecem
                ranking = df_filtrado['UTM_TERM'].value_counts().head(20).reset_index()
                ranking.columns = ['UTM_TERM', 'Vendas']

                # Carregar dados da aba 'MENSAGENS'
                df_mensagens = load_sheet(lancamento, 'MENSAGENS')
                st.session_state.df_mensagens = df_mensagens

                # Adicionar conteúdo das mensagens ao ranking
                ranking['Conteúdo'] = ranking['UTM_TERM'].apply(lambda term: '\n'.join(buscar_conteudo(df_mensagens, term)))
                st.session_state.ranking = ranking

                # Inicializa o estado selecionado com o primeiro UTM_TERM do ranking se não estiver definido
                if st.session_state.selected_utm_term is None:
                    st.session_state.selected_utm_term = ranking['UTM_TERM'].iloc[0]

                # Chamar a função para obter links do Bitly
                access_token = "84d69683f952b86bd62ea9f8c1cd3998ab7e8ba3"
                campaign_code = f"EI.{str(versao).zfill(2)}"
                df_bitly_links = get_bitly_links(access_token, campaign_code)
                st.session_state.df_bitly_links = df_bitly_links

                # Adicionar informações ao ranking
                st.session_state.ranking = adicionar_informacoes(st.session_state.ranking, df_bitly_links)

                # Adicionar coluna de conversão
                st.session_state.ranking['Conversão'] = (st.session_state.ranking['Vendas'] / st.session_state.ranking['Número de Cliques']).apply(lambda x: f"{x:.2%}" if x > 0 else "0.00%")

            st.success("Planilha de vendas carregada com sucesso!")
            st.success("Planilha de mensagens carregada com sucesso!")

        except Exception as e:
            st.error(f"Erro ao carregar a planilha: {e}")

    if 'ranking' in st.session_state:
        st.subheader("Comunicações: Cliques e Vendas")
        
        # Reordenar colunas
        ranking_display = st.session_state.ranking[['UTM_TERM', 'Vendas', 'Número de Cliques', 'Conversão', 'Data', 'Conteúdo']]
        st.dataframe(ranking_display)

        st.subheader("Mensagens")

        # Dropdown para selecionar um dos 20 'UTM_TERM' mais frequentes
        st.session_state.selected_utm_term = st.selectbox(
            'Selecione o UTM_TERM',
            st.session_state.ranking['UTM_TERM'],
            index=st.session_state.ranking['UTM_TERM'].tolist().index(st.session_state.selected_utm_term)
        )

        # Botão para exibir a mensagem
        if st.button("Ver Mensagem"):
            st.session_state.ver_mensagem = True

        if st.session_state.ver_mensagem:
            conteudos = buscar_conteudo(st.session_state.df_mensagens, st.session_state.selected_utm_term)
            if len(conteudos) > 0:
                for conteudo in conteudos:
                    st.write(conteudo)
            else:
                st.write("Nenhuma mensagem encontrada.")

        st.subheader("Links do Bitly")
        
        # Mostrar dataframe dos links do Bitly
        st.dataframe(st.session_state.df_bitly_links)

if __name__ == "__main__":
    main()
