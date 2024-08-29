import streamlit as st
import pandas as pd
import numpy as np
import requests
import re
from pyairtable import Table



# Função para carregar dados do Airtable usando pyairtable
@st.cache_data
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

# Função para atualizar o Airtable com o número de cliques
def update_airtable_clicks(api_key, base_id, table_id, df_airtable):
    table = Table(api_key, base_id, table_id)
    all_records = table.all()
    
    # Cria um dicionário para acesso rápido aos IDs dos registros no Airtable e aos cliques atuais
    records_dict = {
        str(record['fields']['Nome']): {'id': record['id'], 'Cliques': record['fields'].get('Cliques', 0)} 
        for record in all_records if 'Nome' in record['fields']
    }
    
    # Itera sobre o DataFrame do Airtable para atualizar os registros no Airtable
    for index, row in df_airtable.iterrows():
        nome = str(row['Nome'])
        if nome in records_dict:
            record_id = records_dict[nome]['id']
            cliques_atual = records_dict[nome]['Cliques']
            cliques_novo = row['Número de Cliques']
            if not np.isnan(cliques_novo) and cliques_novo > cliques_atual:  # Verifica se o valor é numérico e maior
                try:
                    table.update(record_id, {'Cliques': int(cliques_novo)})
                except Exception as e:
                    st.error(f"Erro ao atualizar o registro {nome}: {e}")

# Função principal

st.title("Exibição de Dados do Airtable e Bitly")

    
lancamento = st.session_state.lancamento
produto = st.session_state.produto
versao = st.session_state.versao


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
    table_id_airtable_antigo = "tblUevuzSnFx5wp0f"

    
    with st.spinner('Carregando dados do Airtable...'):
        df_airtable = load_airtable_data(api_key_airtable, base_id_airtable, table_id_airtable, lancamento)
        df_airtable['Data'] = pd.to_datetime(df_airtable['Data'], errors='coerce')
        df_airtable = df_airtable.sort_values(by='Data')
        df_airtable['Data'] = df_airtable['Data'].dt.strftime('%d/%m/%Y %H:%M')

        # Adicionar a coluna 'Número de Cliques'
        df_airtable['Número de Cliques'] = df_airtable['Link parametrizado'].apply(
            lambda link: st.session_state.df_bitly_links.loc[st.session_state.df_bitly_links['Link de Origem'] == link, 'Número de Cliques'].values[0]
            if link in st.session_state.df_bitly_links['Link de Origem'].values else np.nan  # Usar NaN para valores não encontrados
        ).astype(float)

        # Filtrar colunas desejadas e reordenar
        colunas_desejadas = ["Lançamento", "Conteúdo", "Data", "Número de Cliques", "Nome", "Etapa", "Link parametrizado"]
        df_airtable = df_airtable[colunas_desejadas]
        st.session_state.df_airtable = df_airtable        

        st.success("Dados do Airtable grupos Antigos carregados com sucesso!")

    with st.spinner('Carregando dados do Airtable Antigos...'):

        df_airtable_antigo = load_airtable_data(api_key_airtable, base_id_airtable, table_id_airtable_antigo, lancamento)
        df_airtable_antigo['Data'] = pd.to_datetime(df_airtable_antigo['Data'], errors='coerce')
        df_airtable_antigo = df_airtable_antigo.sort_values(by='Data')
        df_airtable_antigo['Data'] = df_airtable_antigo['Data'].dt.strftime('%d/%m/%Y %H:%M')

        # Adicionar a coluna 'Número de Cliques'
        df_airtable_antigo['Número de Cliques'] = df_airtable_antigo['Link parametrizado'].apply(
            lambda link: st.session_state.df_bitly_links.loc[st.session_state.df_bitly_links['Link de Origem'] == link, 'Número de Cliques'].values[0]
            if link in st.session_state.df_bitly_links['Link de Origem'].values else np.nan  # Usar NaN para valores não encontrados
        ).astype(float)

        # Filtrar colunas desejadas e reordenar
        colunas_desejadas = ["Lançamento", "Conteúdo", "Data", "Número de Cliques", "Nome", "Etapa", "Link parametrizado"]
        df_airtable_antigo = df_airtable_antigo[colunas_desejadas]
        st.session_state.df_airtable_antigo = df_airtable_antigo

        # Salvar chaves no session_state
        st.session_state.api_key_airtable = api_key_airtable
        st.session_state.base_id_airtable = base_id_airtable
        st.session_state.table_id_airtable = table_id_airtable
        st.session_state.table_id_airtable_antigo = table_id_airtable_antigo

        st.success("Dados do Airtable carregados com sucesso!")

except Exception as e:
    st.error(f"Erro ao carregar os dados do Airtable: {e}")    


tabs = st.tabs(["Grupos Novos", "Grupos Antigos"])

with tabs[0]:
    # Se os dados já foram carregados, mostrar o dataframe com o filtro
    if 'df_airtable' in st.session_state:
        # Filtro pela coluna 'Etapa'
        etapa_novo = st.selectbox('Filtrar por Etapa', ['Todas', 'Captação', 'Incomodação', 'Aquecimento', 'Perseguição', 'Pré-Matrícula', 'Vendas', 'Reabertura'], key='etapa_novo')

        if st.button("Filtrar"):
            df_airtable = st.session_state.df_airtable.copy()
            if etapa_novo != 'Todas':
                df_airtable = df_airtable[df_airtable['Etapa'] == etapa_novo]

            st.dataframe(df_bitly_links)
            st.dataframe(df_airtable)

    # Botão para atualizar cliques no Airtable
    if 'df_airtable' in st.session_state and st.button("Atualizar Cliques no Airtable"):
        try:
            with st.spinner('Atualizando cliques no Airtable...'):
                update_airtable_clicks(st.session_state.api_key_airtable, st.session_state.base_id_airtable, st.session_state.table_id_airtable, st.session_state.df_airtable)
            st.success("Cliques atualizados no Airtable com sucesso!")
        except Exception as e:
            st.error(f"Erro ao atualizar cliques no Airtable: {e}")

with tabs[1]:
    # Se os dados já foram carregados, mostrar o dataframe com o filtro
    if 'df_airtable' in st.session_state:
        # Filtro pela coluna 'Etapa'
        etapa_antigo = st.selectbox('Filtrar por Etapa', ['Todas', 'Captação', 'Incomodação', 'Aquecimento', 'Perseguição', 'Pré-Matrícula', 'Vendas', 'Reabertura'], key='etapa_antigo')

        if st.button("Filtrar"):
            df_airtable_antigo = st.session_state.df_airtable_antigo.copy()
            if etapa_antigo != 'Todas':
                df_airtable_antigo = df_airtable_antigo[df_airtable_antigo['Etapa'] == etapa_antigo]

            st.dataframe(df_bitly_links)
            st.dataframe(df_airtable_antigo)

    # Botão para atualizar cliques no Airtable
    if 'df_airtable' in st.session_state and st.button("Atualizar Cliques no Airtable"):
        try:
            with st.spinner('Atualizando cliques no Airtable...'):
                update_airtable_clicks(st.session_state.api_key_airtable, st.session_state.base_id_airtable, st.session_state.table_id_airtable, st.session_state.df_airtable_antigo)
            st.success("Cliques atualizados no Airtable com sucesso!")
        except Exception as e:
            st.error(f"Erro ao atualizar cliques no Airtable: {e}")
