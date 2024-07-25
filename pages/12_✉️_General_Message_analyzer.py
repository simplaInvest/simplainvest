import streamlit as st
import pandas as pd
import requests
import re
from pyairtable import Table

# Configuração da página do Streamlit
st.set_page_config(
    layout="wide",
    page_title="Exibição de Dados do Airtable e Bitly",
    page_icon="📊"
)

# Função para carregar dados do Airtable usando pyairtable
def load_airtable_data(api_key, base_id, table_id, lancamento):
    table = Table(api_key, base_id, table_id)
    all_records = table.all()
    records_data = [record['fields'] for record in all_records if record['fields'].get('Lançamento') == lancamento]
    df = pd.DataFrame(records_data)
    return df

# Função para obter o Group ID do Bitly
def get_bitly_group_id(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api-ssl.bitly.com/v4/groups", headers=headers)
    response.raise_for_status()
    data = response.json()
    return data['groups'][0]['guid']

# Função para obter links do Bitly com paginação
def get_bitly_links(access_token, campaign_code, domain="bit.ly"):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    group_id = get_bitly_group_id(access_token)
    params = {
        "size": 100,
        "group_guid": group_id,
        "domain": domain
    }
    links = []
    url = f"https://api-ssl.bitly.com/v4/groups/{group_id}/bitlinks"
    page = 1

    while url and page <= 3:  # Limitar a 3 páginas
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if 'links' not in data or not data['links']:
            break

        for link in data['links']:
            if 'title' in link and link['title'].startswith(campaign_code):
                link_id = link['id']
                click_response = requests.get(f"https://api-ssl.bitly.com/v4/bitlinks/{link_id}/clicks/summary", headers=headers)
                click_response.raise_for_status()
                clicks_data = click_response.json()
                clicks = clicks_data.get('total_clicks', 0)
                match = re.search(r'\d{2}/\d{2} \d{2}:\d{2}', link['title'])
                data_match = match.group(0) if match else 'não informado'
                links.append({
                    "Nome": link['title'],
                    "Link de Origem": link['long_url'],
                    "Número de Cliques": clicks,
                    "Data": data_match
                })

        url = data.get('pagination', {}).get('next')
        params = None  # Remover params para que a URL de paginação seja usada
        page += 1

    return pd.DataFrame(links)

# Função principal
def main():
    st.title("Exibição de Dados do Airtable e Bitly")

    # Perguntar qual lançamento a pessoa gostaria de analisar
    st.write('Qual Lançamento você quer analisar?')

    # Dropdown para selecionar o produto
    produto = st.selectbox('Produto', ['EI', 'SC'], key='produto')

    # Dropdown para selecionar a versão
    versao = st.selectbox('Versão', list(range(1, 31)), key='versao')

    # Botão para continuar para a análise
    if st.button("Continuar para Análise"):
        lancamento = f"{produto}.{str(versao).zfill(2)}"
        st.session_state.lancamento = lancamento

        try:
            # Chamar a função para obter links do Bitly
            access_token_bitly = "84d69683f952b86bd62ea9f8c1cd3998ab7e8ba3"
            with st.spinner('Carregando dados do Bitly...'):
                campaign_code = f"{produto}.{str(versao).zfill(2)}"
                df_bitly_links = get_bitly_links(access_token_bitly, campaign_code)
                st.session_state.df_bitly_links = df_bitly_links
                st.success("Dados do Bitly carregados com sucesso!")
        
        except Exception as e:
            st.error(f"Erro ao carregar os dados do Bitly: {e}")

        try:
            # Carregar dados do Airtable
            api_key_airtable = "patprpIekfruKBiQc.290906f8b9dc7dfdfa4aa2641e7c10971ca1375bf52174d8d0b2f43969fae862"
            base_id_airtable = "appfMl5wuWgZAPQ0g"
            table_id_airtable = "tblFoPgpbbSAj7S9G"
            
            with st.spinner('Carregando dados do Airtable...'):
                df_airtable = load_airtable_data(api_key_airtable, base_id_airtable, table_id_airtable, lancamento)
                df_airtable['Data'] = pd.to_datetime(df_airtable['Data'], errors='coerce')
                df_airtable = df_airtable.sort_values(by='Data')
                df_airtable['Data'] = df_airtable['Data'].dt.strftime('%d/%m/%Y %H:%M')

                # Adicionar a coluna 'Número de Cliques'
                df_airtable['Número de Cliques'] = df_airtable['Link parametrizado'].apply(
                    lambda link: st.session_state.df_bitly_links.loc[st.session_state.df_bitly_links['Link de Origem'] == link, 'Número de Cliques'].values[0]
                    if link in st.session_state.df_bitly_links['Link de Origem'].values else "bitly não encontrado"
                )

                # Filtrar colunas desejadas e reordenar
                colunas_desejadas = ["Lançamento", "Conteúdo", "Data", "Número de Cliques", "Nome", "Etapa", "Link parametrizado"]
                df_airtable = df_airtable[colunas_desejadas]
                st.session_state.df_airtable = df_airtable

                st.success("Dados do Airtable carregados com sucesso!")
    
        except Exception as e:
            st.error(f"Erro ao carregar os dados do Airtable: {e}")

    # Se os dados já foram carregados, mostrar o dataframe com o filtro
    if 'df_airtable' in st.session_state:
        # Filtro pela coluna 'Etapa'
        etapa = st.selectbox('Filtrar por Etapa', ['Todas', 'Captação', 'Incomodação', 'Aquecimento', 'Perseguição', 'Pré-Matrícula', 'Vendas', 'Reabertura'], key='etapa')

        if st.button("Filtrar"):
            df_airtable = st.session_state.df_airtable.copy()
            if etapa != 'Todas':
                df_airtable = df_airtable[df_airtable['Etapa'] == etapa]

            st.dataframe(df_airtable)

if __name__ == "__main__":
    main()