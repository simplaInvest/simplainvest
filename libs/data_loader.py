import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

from libs.data_formatter import format_central_captura, format_grupos_wpp, format_ptrafego_metaads, format_ptrafego_clicks, format_ptrafego_dados, format_pesquisa_trafego_colunas_monetarias

# CONSTANTS
K_CENTRAL_CAPTURA = "K_CENTRAL_CAPTURA"
K_CENTRAL_PRE_MATRICULA = "K_CENTRAL_PRE_MATRICULA"
K_CENTRAL_VENDAS = "K_CENTRAL_VENDAS"
K_PTRAFEGO_DADOS = "K_PTRAFEGO_DADOS"
K_PTRAFEGO_META_ADS = "K_PTRAFEGO_META_ADS"
K_PTRAFEGO_ANUNCIOS_SUBIDOS = "K_PTRAFEGO_ANUNCIOS_SUBIDOS"
K_PCOPY_DADOS = "K_PCOPY_DADOS"
K_GRUPOS_WPP = "K_GRUPOS_WPP"
K_CLICKS_WPP = "K_CLICKS_WPP"
K_CENTRAL_LANCAMENTOS = "K_CENTRAL_LANCAMENTOS"
K_PESQUISA_TRAFEGO_PORCAMPANHA = "K_PESQUISA_TRAFEGO_PORCAMPANHA"
K_PESQUISA_TRAFEGO_PORANUNCIO = "K_PESQUISA_TRAFEGO_PORANUNCIO"
K_PESQUISA_TRAFEGO_PORCONJUNTO = "K_PESQUISA_TRAFEGO_PORCONJUNTO"

def setupSheets(produto, versao):
    lancamento = f"{produto}.{str(versao).zfill(2)}"
    # PLANILHAS
    SHEET_CENTRAL_DO_UTM = lancamento + " - CENTRAL DO UTM"
    SHEET_PESQUISA_TRAFEGO_DADOS = lancamento + " - PTRAFEGO DADOS"
    SHEET_PESQUISA_TRAFEGO_ADS = lancamento + " - PESQUISA TRAFEGO"
    SHEET_PESQUISA_COPY = lancamento + " - PESQUISA DE COPY"
    SHEET_GRUPOS_WPP = lancamento + " - GRUPOS DE WHATSAPP"
    SHEET_CENTRAL_LANCAMENTOS = "CENTRAL DE LANÇAMENTOS"
    # ABAS
    ABA_CENTRAL_CAPTURA = "CAPTURA"
    ABA_CENTRAL_PRE_MATRICULA = "PRE-MATRICULA"
    ABA_CENTRAL_VENDAS = "VENDAS"
    ABA_PTRAFEGO_DADOS = "DADOS"
    ABA_PTRAFEGO_META_ADS = "NEW META ADS"
    ABA_PTRAFEGO_ANUNCIOS_SUBIDOS = "ANUNCIOS SUBIDOS"
    ABA_PCOPY_DADOS = 'pesquisa-copy-' + lancamento.replace(".", "")
    ABA_GRUPOS_WPP = 'SENDFLOW - ATIVIDADE EXPORT'
    ABA_CLICKS_WPP = 'CLICKS POR DIA - BOAS-VINDAS'
    ABA_CENTRAL_LANCAMENTOS = 'DATAS'
    ABA_PESQUISA_TRAFEGO_PORCAMPANHA = 'POR CAMPANHA'
    ABA_PESQUISA_TRAFEGO_PORANUNCIO = 'POR ANUNCIO'
    ABA_PESQUISA_TRAFEGO_PORCONJUNTO= 'POR CONJUNTO'

    # PLANILHAS
    SHEETS = {
        K_CENTRAL_CAPTURA: { "id": "K_CENTRAL_CAPTURA",
                            "sheet": SHEET_CENTRAL_DO_UTM,
                            "aba": ABA_CENTRAL_CAPTURA,
                            "dataframe": None,
                            },
        K_CENTRAL_PRE_MATRICULA: { "id": "K_CENTRAL_PRE_MATRICULA",
                            "sheet": SHEET_CENTRAL_DO_UTM,
                            "aba": ABA_CENTRAL_PRE_MATRICULA,
                            "dataframe": None,
                            },
        K_CENTRAL_VENDAS: { "id": "K_CENTRAL_VENDAS",
                            "sheet": SHEET_CENTRAL_DO_UTM,
                            "aba": ABA_CENTRAL_VENDAS,
                            "dataframe": None,
                            },
        K_PTRAFEGO_DADOS: { "id": "K_PTRAFEGO_DADOS",
                            "sheet": SHEET_PESQUISA_TRAFEGO_DADOS if st.session_state["PRODUTO"] == 'EI' and st.session_state["VERSAO_PRINCIPAL"] >= 21 or st.session_state["PRODUTO"] == 'SW' or st.session_state['PRODUTO'] == 'SC' and st.session_state["VERSAO_PRINCIPAL"] >= 14 else SHEET_PESQUISA_TRAFEGO_ADS,
                            "aba": ABA_PTRAFEGO_DADOS,
                            "dataframe": None,
                            },
        K_PTRAFEGO_META_ADS: { "id": "K_PTRAFEGO_META_ADS",
                            "sheet": SHEET_PESQUISA_TRAFEGO_DADOS if st.session_state["PRODUTO"] == 'EI' and st.session_state["VERSAO_PRINCIPAL"] >= 22 else SHEET_PESQUISA_TRAFEGO_ADS,
                            "aba": ABA_PTRAFEGO_META_ADS,
                            "dataframe": None,
                            },
        K_PTRAFEGO_ANUNCIOS_SUBIDOS: { "id": "K_PTRAFEGO_ANUNCIOS_SUBIDOS",
                            "sheet": SHEET_PESQUISA_TRAFEGO_ADS,
                            "aba": ABA_PTRAFEGO_ANUNCIOS_SUBIDOS,
                            "dataframe": None,
                            },
        K_PCOPY_DADOS: { "id": "K_PCOPY_DADOS",
                            "sheet": SHEET_PESQUISA_COPY,
                            "aba": ABA_PCOPY_DADOS,
                            "dataframe": None,
                            },
        K_GRUPOS_WPP: { "id": "K_GRUPOS_WPP",
                            "sheet": SHEET_GRUPOS_WPP,
                            "aba": ABA_GRUPOS_WPP,
                            "dataframe": None,
                            },
        K_CLICKS_WPP: { "id": "K_GRUPOS_WPP",
                            "sheet": SHEET_GRUPOS_WPP,
                            "aba": ABA_CLICKS_WPP,
                            "dataframe": None,
                             },
        K_CENTRAL_LANCAMENTOS: { "id": "K_CENTRAL_LANCAMENTOS",
                            "sheet": SHEET_CENTRAL_LANCAMENTOS,
                            "aba": ABA_CENTRAL_LANCAMENTOS,
                            "dataframe": None,
                             },
        K_PESQUISA_TRAFEGO_PORCAMPANHA: { "id": "K_PESQUISA_TRAFEGO_PORCAMPANHA",
                                         "sheet": SHEET_PESQUISA_TRAFEGO_ADS,
                                         "aba": ABA_PESQUISA_TRAFEGO_PORCAMPANHA,
                                         "dataframe": None,
                                         },
        K_PESQUISA_TRAFEGO_PORANUNCIO: { "id": "K_PESQUISA_TRAFEGO_PORCAMPANHA",
                                         "sheet": SHEET_PESQUISA_TRAFEGO_ADS,
                                         "aba": ABA_PESQUISA_TRAFEGO_PORANUNCIO,
                                         "dataframe": None,
                                         },
        K_PESQUISA_TRAFEGO_PORCONJUNTO: { "id": "K_PESQUISA_TRAFEGO_PORCAMPANHA",
                                         "sheet": SHEET_PESQUISA_TRAFEGO_ADS,
                                         "aba": ABA_PESQUISA_TRAFEGO_PORCONJUNTO,
                                         "dataframe": None,
                                         }
    }
    
    return SHEETS

@st.cache_data(show_spinner=False, ttl=1800)
def get_df(PRODUTO, VERSAO_PRINCIPAL, K_PLANILHA):
    ui_status = st.empty()
    with ui_status:
        st.write(f"Carregando {K_PLANILHA.replace('K_', '').replace('_', ' ').title()}...")

    if K_PLANILHA in st.session_state and K_PLANILHA == K_CENTRAL_LANCAMENTOS:
        df = st.session_state[K_CENTRAL_LANCAMENTOS]
    elif K_PLANILHA in st.session_state:
        df = st.session_state[f"{PRODUTO}-{VERSAO_PRINCIPAL}-{K_PLANILHA}"]
    else:
        dataLoader = DataLoader(PRODUTO, VERSAO_PRINCIPAL)
        df = dataLoader.load_df(K_PLANILHA)

    with ui_status:
        st.write(f"✅ {K_PLANILHA.replace('K_', '').replace('_', ' ').title()}.")
    return df.copy()

def clear_df():
    get_df.clear()

class DataLoader:
    def __init__(self, produto, versao):
        self.produto = produto
        self.versao = versao
        self.client = self.authenticate()
        self.sheets = setupSheets(produto, versao)

    def authenticate(self):
        """Autentica com o Google e retorna um cliente autorizado."""
        if 'client' in st.session_state:
            return st.session_state.client
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        st.session_state.client = client
        return client

    def load_gsheet(self, sheet_name, aba_name):
        """Carrega os dados do Google Sheets e retorna como DataFrame."""
        try:
            data = self.client.open(sheet_name).worksheet(aba_name).get_all_values()
            return pd.DataFrame() if not data else pd.DataFrame(data[1:], columns=data[0])
        except Exception as e:
            st.error(f"Erro ao carregar a planilha '{sheet_name} > {aba_name}': {str(e)}")
            return pd.DataFrame()
        
    def load_gsheet_paginated(self, sheet_name, aba_name, page_size=5000):
        try:
            worksheet = self.client.open(sheet_name).worksheet(aba_name)
            headers = worksheet.row_values(1)
            num_cols = len(headers)
            all_data = []
            
            total_rows = worksheet.row_count
            last_col = chr(ord('A') + num_cols - 1)
            
            for start_row in range(2, total_rows + 1, page_size):
                end_row = min(start_row + page_size - 1, total_rows)
                print(f"carrengado da {start_row} à {end_row} linha")
                range_str = f'A{start_row}:{last_col}{end_row}'
                chunk = worksheet.get(range_str)
                # Ensure each row has correct number of columns
                chunk = [row + [''] * (num_cols - len(row)) for row in chunk]
                all_data.extend(chunk)
                
            return pd.DataFrame(all_data, columns=headers)
        except Exception as e:
            st.error(f"Erro ao carregar planilha '{sheet_name} > {aba_name}': {str(e)}")
            return pd.DataFrame()
        
    def load_df(self, K_PLANILHA):
        """Busca o dataframe da planilha referenciada."""

        if K_PLANILHA not in self.sheets:
            raise ValueError(f"Planilha inválida: {K_PLANILHA}")

        print('load_df(): loading df for', K_PLANILHA)

        # Get self.sheet reference
        sheet = self.sheets[K_PLANILHA]

        # Load the data
        df_sheet = self.load_gsheet(sheet["sheet"], sheet["aba"])

        # Format data
        match K_PLANILHA:
            case "K_CENTRAL_CAPTURA":
                df_sheet = format_central_captura(df_sheet)
            case "K_CENTRAL_PRE_MATRICULA":
                df_sheet = df_sheet
            case "K_CENTRAL_VENDAS":
                df_sheet = df_sheet
            case "K_PTRAFEGO_DADOS":
                df_sheet = format_ptrafego_dados(df_sheet)
            case "K_PTRAFEGO_META_ADS":
                df_sheet = format_ptrafego_metaads(df_sheet)
            case "K_PTRAFEGO_META_ADS_L4":
                df_sheet = format_ptrafego_metaads(df_sheet)
            case "K_PTRAFEGO_ANUNCIOS_SUBIDOS":
                df_sheet = df_sheet
            case "K_PCOPY_DADOS":
                df_sheet = df_sheet
            case "K_GRUPOS_WPP":
                df_sheet = format_grupos_wpp(df_sheet)
            case "K_CLICKS_WPP":
                df_sheet = format_ptrafego_clicks(df_sheet)
            case "K_CENTRAL_LANCAMENTOS":
                df_sheet = df_sheet
                return df_sheet
            case "K_PESQUISA_TRAFEGO_PORCAMPANHA":
                df_sheet = format_pesquisa_trafego_colunas_monetarias(df_sheet)
                return df_sheet
            case "K_PESQUISA_TRAFEGO_PORANUNCIO":
                df_sheet = format_pesquisa_trafego_colunas_monetarias(df_sheet)
                return df_sheet
            case "K_PESQUISA_TRAFEGO_PORCONJUNTO":
                df_sheet = format_pesquisa_trafego_colunas_monetarias(df_sheet)
                return df_sheet
            case _:
                raise ValueError(f"Planilha inválida: {K_PLANILHA}")

        # Store in instance and session state
        self.sheets[K_PLANILHA]["dataframe"] = df_sheet
        st.session_state[f"{self.produto}-{self.versao}-{K_PLANILHA}"] = df_sheet
        
        return df_sheet