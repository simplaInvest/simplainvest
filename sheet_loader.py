import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

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


@st.cache_data(ttl=1200)
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
