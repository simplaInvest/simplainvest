import streamlit as st
import pandas as pd
from pyairtable import Table

# Configuração da página do Streamlit
st.set_page_config(
    layout="wide",
    page_title="Exibição de Dados do Airtable",
    page_icon="📊"
)

# Função para carregar dados do Airtable usando pyairtable
def load_airtable_data(api_key, base_id, table_id):
    table = Table(api_key, base_id, table_id)
    all_records = table.all()

    # Extrair campos dos registros
    records_data = [record['fields'] for record in all_records]
    df = pd.DataFrame(records_data)
    return df

# Função principal
def main():
    st.title("Exibição de Dados do Airtable")

    # Carregar dados do Airtable
    api_key = "patprpIekfruKBiQc.290906f8b9dc7dfdfa4aa2641e7c10971ca1375bf52174d8d0b2f43969fae862"
    base_id = "appfMl5wuWgZAPQ0g"
    table_id = "tblFoPgpbbSAj7S9G"

    try:
        with st.spinner('Carregando dados do Airtable...'):
            df_airtable = load_airtable_data(api_key, base_id, table_id)
            st.success("Dados carregados com sucesso!")

        st.dataframe(df_airtable)
    
    except Exception as e:
        st.error(f"Erro ao carregar os dados do Airtable: {e}")

if __name__ == "__main__":
    main()
