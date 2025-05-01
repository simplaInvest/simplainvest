import pandas as pd
import streamlit as st

def format_central_captura(df_central_captura):
    if df_central_captura.empty:
        raise ValueError(f"O DataFrame '{df_central_captura}' está vazio.")
    df_central_captura['CAP DATA_CAPTURA'] = pd.to_datetime(df_central_captura['CAP DATA_CAPTURA'], errors = 'coerce', dayfirst=True).dt.date
    return df_central_captura

def format_grupos_wpp(df_grupos_wpp):
    if df_grupos_wpp.empty:
        return df_grupos_wpp
    # Converte coluna "Data" (string) em datetime
    if 'Data' in df_grupos_wpp.columns:
        if df_grupos_wpp['Data'].dtype == 'object':  # Apenas se ainda for texto
            df_grupos_wpp['Data'] = df_grupos_wpp['Data'].str.replace(' às ', ' ')
            df_grupos_wpp['Data'] = pd.to_datetime(df_grupos_wpp['Data'], dayfirst=True, errors='coerce')
    # Cria colunas "Entradas" e "Saidas" com base na coluna "Evento"
    df_grupos_wpp['Entradas'] = df_grupos_wpp['Evento'].str.contains("Entrou", na=False).astype(int)
    df_grupos_wpp['Saidas'] = df_grupos_wpp['Evento'].str.contains("Saiu", na=False).astype(int)
    return df_grupos_wpp

def format_ptrafego_metaads(df_ptrafego_metaads):
    if df_ptrafego_metaads.empty:
        return df_ptrafego_metaads
    else:
        # Verifica se a coluna já está em formato float
        if not pd.api.types.is_numeric_dtype(df_ptrafego_metaads['VALOR USADO']):
            # Remove R$ and commas, then convert to float
            df_ptrafego_metaads['VALOR USADO'] = df_ptrafego_metaads['VALOR USADO'].astype(str).str.replace('R$', '').str.replace(',', '.').str.strip()
            # Convert to float, replacing empty strings with NaN
            df_ptrafego_metaads['VALOR USADO'] = pd.to_numeric(df_ptrafego_metaads['VALOR USADO'], errors='coerce')
        return df_ptrafego_metaads
    
def format_ptrafego_clicks(df_ptrafego_clicks):
    if df_ptrafego_clicks.empty:
        return df_ptrafego_clicks
    else:
        # Converter a coluna 'DATA' para datetime
        df_ptrafego_clicks['DATA'] = pd.to_datetime(df_ptrafego_clicks['DATA'], dayfirst=True)
        # Converter as demais colunas para int
        for col in df_ptrafego_clicks.columns:
            if col != 'DATA':
                df_ptrafego_clicks[col] = df_ptrafego_clicks[col].astype(int)

    return df_ptrafego_clicks

def format_ptrafego_dados(df_ptrafego_dados):
    if df_ptrafego_dados.empty:
        raise ValueError(f"O Dataframe '{df_ptrafego_dados}' está vazio")
    else:
        # converter a coluna 'DATA DE CAPTURA' para datetime no formato correto
        df_ptrafego_dados["DATA DE CAPTURA"] = pd.to_datetime(df_ptrafego_dados["DATA DE CAPTURA"], format="%d/%m/%Y %H:%M", errors="coerce")
        # Verifica colunas duplicadas
        if df_ptrafego_dados.columns.duplicated().any():
            st.warning("Colunas duplicadas foram encontradas e excluídas.")
            df_ptrafego_dados = df_ptrafego_dados.loc[:, ~df_ptrafego_dados.columns.duplicated()]
    return df_ptrafego_dados