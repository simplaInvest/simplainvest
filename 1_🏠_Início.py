import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from urllib.parse import unquote_plus
import streamlit_calendar as st_cal
from datetime import datetime, timedelta

# Função para carregar uma aba específica de uma planilha
def load_sheet(sheet_name, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('autorizador.json', scope)
    client = gspread.authorize(creds)
    # Abrir a planilha Google
    worksheet = client.open(sheet_name).worksheet(worksheet_name)
    # Obter todos os dados da aba
    data = worksheet.get_all_values()
    return data

# Função para processar e formatar os dados
def process_data(data):
    # Definir colunas de interesse e seus novos cabeçalhos
    columns = {
        "META DE OKR": "A",
        "PRECISAMOS EM 2024": "D",
        "CONSEGUIMOS EM 2024": "F",
        "PROGRESSO": "G"
    }
    
    # Extraindo os dados das colunas específicas
    extracted_data = {new_col: [] for new_col in columns.keys()}
    for row in data[1:]:  # Skip header row
        for new_col, col_letter in columns.items():
            # Convert column letter to index (A=0, B=1, ...)
            col_index = ord(col_letter) - ord('A')
            extracted_data[new_col].append(row[col_index])
    
    # Criar DataFrame
    df = pd.DataFrame(extracted_data)
    
    # Função para limpar e converter valores numéricos
    def clean_and_convert(value):
        try:
            value = value.replace('.', '').replace('R$', '').replace(',', '.').strip()
            return float(value)
        except ValueError:
            return value

    # Função para converter valores percentuais
    def convert_percentage(value):
        try:
            return float(value.replace('%', '').replace(',', '.').strip())
        except ValueError:
            return None

    # Aplicar a função de limpeza e conversão
    for col in ["META DE OKR", "PRECISAMOS EM 2024", "CONSEGUIMOS EM 2024"]:
        df[col] = df[col].apply(clean_and_convert)
    
    # Aplicar a função de conversão de percentagens
    df["PROGRESSO"] = df["PROGRESSO"].apply(convert_percentage)
    
    return df

# Função para formatar números
def format_number(value, currency=False):
    if currency:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"{int(value):,}".replace(",", ".")

# Configuração da página do Streamlit
st.set_page_config(
    layout="wide",
    page_title="Central de Ferramentas Simpla Invest 💎",
    page_icon="💎"
)

# Adicione links para navegação manualmente (opcional)
st.sidebar.title("Navegação")


# Interface do Streamlit
st.markdown("<h1 style='text-align: center; font-size: 48px;'>Central de Ferramentas Simpla Invest 💎</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Seja bem vindo, Simpler!</h2>", unsafe_allow_html=True)

# Adicionar espaçador
st.markdown("<hr style='border: 1px solid #ccc; margin: 60px auto; width: 70%;'>", unsafe_allow_html=True)

# Nome da planilha e da aba
spreadsheet_name = "Dashboard OKR's Simpla Invest"
worksheet_name = "Dados(PY)"

# Carregar os dados da planilha
data = load_sheet(spreadsheet_name, worksheet_name)

# Processar e formatar os dados
df = process_data(data)

# Adicionar barras de progresso para a coluna "PROGRESSO"
st.markdown("<h4 style='text-align: left;'>Progresso das OKRs em 2024</h4>", unsafe_allow_html=True)

for index, row in df.iterrows():
    meta = row['META DE OKR']
    conseguimos = format_number(row['CONSEGUIMOS EM 2024'], currency=(index == 3))
    precisamos = format_number(row['PRECISAMOS EM 2024'], currency=(index == 3))
    if index == 3:
        conseguimos = f"R$ {conseguimos}"
    st.markdown(f"<div style='margin-bottom: 10px;'><strong>{meta}</strong>: ({conseguimos}/{precisamos})</div>", unsafe_allow_html=True)
    st.progress(int(row["PROGRESSO"]))


# Função para gerar intervalo de datas
def generate_date_range(start_date, end_date, title, color):
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append({"date": current_date.strftime("%Y-%m-%d"), "title": title, "color": color})
        current_date += timedelta(days=1)
    return date_range

# Adicionar calendário de eventos
st.markdown("<h4 style='text-align: left; margin-top: 50px;'>Calendário de Eventos</h4>", unsafe_allow_html=True)

# Lista de eventos pré-determinados
eventos = [
    {"date": "2024-01-01", "title": "Ano Novo"},    
    {"date": "2024-02-14", "title": "Dia dos Namorados"},
    {"date": "2024-04-21", "title": "Tiradentes"},
    {"date": "2024-05-01", "title": "Dia do Trabalhador"},
    {"date": "2024-09-07", "title": "Independência do Brasil"},
    {"date": "2024-10-12", "title": "Nossa Senhora Aparecida"},
    {"date": "2024-11-15", "title": "Proclamação da República"},
    {"date": "2024-12-25", "title": "Natal"}
]

# Eventos "Eu Investidor" (verde)
eu_investidor_eventos = []
eu_investidor_eventos += generate_date_range(datetime(2024, 1, 1), datetime(2024, 1, 25), "Eu Investidor", "green")
eu_investidor_eventos += generate_date_range(datetime(2024, 2, 12), datetime(2024, 3, 21), "Eu Investidor", "green")
eu_investidor_eventos += generate_date_range(datetime(2024, 4, 15), datetime(2024, 5, 23), "Eu Investidor", "green")
eu_investidor_eventos += generate_date_range(datetime(2024, 6, 17), datetime(2024, 7, 15), "Eu Investidor", "green")
eu_investidor_eventos += generate_date_range(datetime(2024, 8, 12), datetime(2024, 9, 19), "Eu Investidor", "green")

# Eventos "Simpla Club" (azul e outras tonalidades)
simpla_club_eventos = []
simpla_club_eventos += generate_date_range(datetime(2024, 1, 16), datetime(2024, 1, 31), "Simpla Club", "blue")
simpla_club_eventos += generate_date_range(datetime(2024, 2, 25), datetime(2024, 4, 4), "Simpla Club", "blue")
simpla_club_eventos += generate_date_range(datetime(2024, 5, 27), datetime(2024, 6, 6), "Simpla Club", "blue")
simpla_club_eventos += generate_date_range(datetime(2024, 7, 26), datetime(2024, 8, 1), "Simpla Club", "blue")
simpla_club_eventos += generate_date_range(datetime(2024, 9, 20), datetime(2024, 9, 26), "Simpla Club", "blue")
simpla_club_eventos += generate_date_range(datetime(2024, 11, 10), datetime(2024, 12, 5), "Simpla Club", "blue")

# Adicionar eventos às listas de eventos
eventos += eu_investidor_eventos + simpla_club_eventos

# Converter eventos para o formato necessário
events_list = [{"start": event["date"], "title": event["title"], "color": event.get("color", "gray")} for event in eventos]

# Mostrar calendário com eventos
st_cal.calendar(events=events_list)

