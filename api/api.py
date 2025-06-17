# main_api.py - Sua API FastAPI atualizada
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import threading
import base64
from typing import Dict, Optional, List
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import asyncio
import uvicorn
from threading import Thread
import time

from libs.data_formatter import (
    format_central_captura, 
    format_grupos_wpp, 
    format_ptrafego_metaads, 
    format_ptrafego_clicks, 
    format_ptrafego_dados
)

# Constantes
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

VALID_PRODUTOS = ["EI", "SC", "SW"]

class APIDataLoader:
    """Versão da classe DataLoader adaptada para a API"""
    
    def __init__(self, produto: str, versao: int, credentials_dict: dict):
        self.produto = produto
        self.versao = versao
        self.client = self._authenticate(credentials_dict)
        self.sheets = self._setup_sheets(produto, versao)

    def _authenticate(self, credentials_dict: dict):
        """Autentica com o Google e retorna um cliente autorizado."""
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        return gspread.authorize(creds)

    def _setup_sheets(self, produto: str, versao: int) -> dict:
        """Configuração das planilhas"""
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

        # Lógica condicional das planilhas
        ptrafego_dados_sheet = (SHEET_PESQUISA_TRAFEGO_DADOS 
                               if (produto == 'EI' and versao >= 21) or 
                                  produto == 'SW' or 
                                  (produto == 'SC' and versao >= 14)
                               else SHEET_PESQUISA_TRAFEGO_ADS)
        
        ptrafego_metaads_sheet = (SHEET_PESQUISA_TRAFEGO_DADOS 
                                 if produto == 'EI' and versao >= 22 
                                 else SHEET_PESQUISA_TRAFEGO_ADS)

        return {
            K_CENTRAL_CAPTURA: {
                "id": K_CENTRAL_CAPTURA,
                "sheet": SHEET_CENTRAL_DO_UTM,
                "aba": ABA_CENTRAL_CAPTURA,
            },
            K_CENTRAL_PRE_MATRICULA: {
                "id": K_CENTRAL_PRE_MATRICULA,
                "sheet": SHEET_CENTRAL_DO_UTM,
                "aba": ABA_CENTRAL_PRE_MATRICULA,
            },
            K_CENTRAL_VENDAS: {
                "id": K_CENTRAL_VENDAS,
                "sheet": SHEET_CENTRAL_DO_UTM,
                "aba": ABA_CENTRAL_VENDAS,
            },
            K_PTRAFEGO_DADOS: {
                "id": K_PTRAFEGO_DADOS,
                "sheet": ptrafego_dados_sheet,
                "aba": ABA_PTRAFEGO_DADOS,
            },
            K_PTRAFEGO_META_ADS: {
                "id": K_PTRAFEGO_META_ADS,
                "sheet": ptrafego_metaads_sheet,
                "aba": ABA_PTRAFEGO_META_ADS,
            },
            K_PTRAFEGO_ANUNCIOS_SUBIDOS: {
                "id": K_PTRAFEGO_ANUNCIOS_SUBIDOS,
                "sheet": SHEET_PESQUISA_TRAFEGO_ADS,
                "aba": ABA_PTRAFEGO_ANUNCIOS_SUBIDOS,
            },
            K_PCOPY_DADOS: {
                "id": K_PCOPY_DADOS,
                "sheet": SHEET_PESQUISA_COPY,
                "aba": ABA_PCOPY_DADOS,
            },
            K_GRUPOS_WPP: {
                "id": K_GRUPOS_WPP,
                "sheet": SHEET_GRUPOS_WPP,
                "aba": ABA_GRUPOS_WPP,
            },
            K_CLICKS_WPP: {
                "id": K_CLICKS_WPP,
                "sheet": SHEET_GRUPOS_WPP,
                "aba": ABA_CLICKS_WPP,
            },
            K_CENTRAL_LANCAMENTOS: {
                "id": K_CENTRAL_LANCAMENTOS,
                "sheet": SHEET_CENTRAL_LANCAMENTOS,
                "aba": ABA_CENTRAL_LANCAMENTOS,
            }
        }

    def load_gsheet(self, sheet_name: str, aba_name: str) -> pd.DataFrame:
        """Carrega os dados do Google Sheets"""
        try:
            data = self.client.open(sheet_name).worksheet(aba_name).get_all_values()
            return pd.DataFrame() if not data else pd.DataFrame(data[1:], columns=data[0])
        except Exception as e:
            print(f"Erro ao carregar a planilha '{sheet_name} > {aba_name}': {str(e)}")
            raise HTTPException(
                status_code=404, 
                detail=f"Planilha não encontrada: {sheet_name} > {aba_name}"
            )

    def load_gsheet_paginated(self, sheet_name: str, aba_name: str, page_size: int = 5000) -> pd.DataFrame:
        """Carregamento paginado para planilhas grandes"""
        try:
            worksheet = self.client.open(sheet_name).worksheet(aba_name)
            headers = worksheet.row_values(1)
            num_cols = len(headers)
            all_data = []
            
            total_rows = worksheet.row_count
            last_col = chr(ord('A') + num_cols - 1)
            
            for start_row in range(2, total_rows + 1, page_size):
                end_row = min(start_row + page_size - 1, total_rows)
                print(f"Carregando da linha {start_row} à {end_row}")
                range_str = f'A{start_row}:{last_col}{end_row}'
                chunk = worksheet.get(range_str)
                chunk = [row + [''] * (num_cols - len(row)) for row in chunk]
                all_data.extend(chunk)
                
            return pd.DataFrame(all_data, columns=headers)
        except Exception as e:
            print(f"Erro ao carregar planilha '{sheet_name} > {aba_name}': {str(e)}")
            raise HTTPException(
                status_code=404, 
                detail=f"Planilha não encontrada: {sheet_name} > {aba_name}"
            )

    def load_df(self, k_planilha: str, use_pagination: bool = False) -> pd.DataFrame:
        """Carrega e formata o dataframe"""
        if k_planilha not in self.sheets:
            raise HTTPException(
                status_code=400, 
                detail=f"Planilha inválida: {k_planilha}. Disponíveis: {list(self.sheets.keys())}"
            )

        print(f'load_df(): carregando df para {k_planilha}')
        sheet = self.sheets[k_planilha]

        # Escolhe método de carregamento baseado no tamanho esperado
        if use_pagination or k_planilha in [K_PTRAFEGO_DADOS, K_CENTRAL_CAPTURA]:
            df_sheet = self.load_gsheet_paginated(sheet["sheet"], sheet["aba"])
        else:
            df_sheet = self.load_gsheet(sheet["sheet"], sheet["aba"])

        # Formatação usando as funções existentes
        match k_planilha:
            case "K_CENTRAL_CAPTURA":
                df_sheet = format_central_captura(df_sheet)
            case "K_CENTRAL_PRE_MATRICULA":
                pass  # Sem formatação específica
            case "K_CENTRAL_VENDAS":
                pass  # Sem formatação específica
            case "K_PTRAFEGO_DADOS":
                df_sheet = format_ptrafego_dados(df_sheet)
            case "K_PTRAFEGO_META_ADS":
                df_sheet = format_ptrafego_metaads(df_sheet)
            case "K_PTRAFEGO_ANUNCIOS_SUBIDOS":
                pass  # Sem formatação específica
            case "K_PCOPY_DADOS":
                pass  # Sem formatação específica
            case "K_GRUPOS_WPP":
                df_sheet = format_grupos_wpp(df_sheet)
            case "K_CLICKS_WPP":
                df_sheet = format_ptrafego_clicks(df_sheet)
            case "K_CENTRAL_LANCAMENTOS":
                pass  # Sem formatação específica
            case _:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Planilha inválida: {k_planilha}"
                )

        return df_sheet

class DataCacheManager:
    """Sistema de cache inteligente para os dataframes"""
    
    def __init__(self, cache_ttl_minutes: int = 30, credentials_dict: dict = None):
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.lock = threading.Lock()
        self.credentials_dict = credentials_dict
        
    def _get_cache_key(self, produto: str, versao: int, k_planilha: str) -> str:
        """Gera chave única para o cache"""
        return f"{produto}_{versao}_{k_planilha}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se o cache ainda é válido"""
        if cache_key not in self.cache_timestamps:
            return False
        
        cache_time = self.cache_timestamps[cache_key]
        return datetime.now() - cache_time < self.cache_ttl
    
    def get_dataframe(self, produto: str, versao: int, k_planilha: str, force_reload: bool = False) -> pd.DataFrame:
        """Retorna dataframe com cache inteligente"""
        cache_key = self._get_cache_key(produto, versao, k_planilha)
        
        with self.lock:
            # Verifica se existe cache válido e não é reload forçado
            if not force_reload and cache_key in self.cache and self._is_cache_valid(cache_key):
                print(f"📊 Cache hit para {produto} v{versao} - {k_planilha}")
                return self.cache[cache_key].copy()
            
            # Cache inválido ou inexistente, carrega novos dados
            print(f"🔄 Carregando dados frescos para {produto} v{versao} - {k_planilha}")
            
            try:
                data_loader = APIDataLoader(produto, versao, self.credentials_dict)
                
                # Usa paginação para planilhas conhecidamente grandes
                use_pagination = k_planilha in [K_PTRAFEGO_DADOS, K_CENTRAL_CAPTURA]
                df = data_loader.load_df(k_planilha, use_pagination=use_pagination)
                
                # Armazena no cache
                self.cache[cache_key] = df.copy()
                self.cache_timestamps[cache_key] = datetime.now()
                
                print(f"✅ Dados carregados e armazenados no cache: {len(df)} registros")
                return df.copy()
                
            except Exception as e:
                print(f"❌ Erro ao carregar dados: {e}")
                raise
    
    def invalidate_cache(self, produto: str = None, versao: int = None, k_planilha: str = None):
        """Remove cache específico ou todo o cache"""
        with self.lock:
            if produto and versao and k_planilha:
                cache_key = self._get_cache_key(produto, versao, k_planilha)
                self.cache.pop(cache_key, None)
                self.cache_timestamps.pop(cache_key, None)
                print(f"🗑️ Cache removido para {produto} v{versao} - {k_planilha}")
            elif produto and versao:
                # Remove todos os caches para um produto/versão específico
                keys_to_remove = [k for k in self.cache.keys() if k.startswith(f"{produto}_{versao}_")]
                for key in keys_to_remove:
                    self.cache.pop(key, None)
                    self.cache_timestamps.pop(key, None)
                print(f"🗑️ Cache removido para {produto} v{versao} (todas as planilhas)")
            else:
                self.cache.clear()
                self.cache_timestamps.clear()
                print("🗑️ Todo cache removido")
    
    def get_cache_status(self) -> dict:
        """Retorna status do cache"""
        with self.lock:
            cache_info = {}
            for key, timestamp in self.cache_timestamps.items():
                produto, versao, k_planilha = key.split('_', 2)
                cache_info[key] = {
                    "produto": produto,
                    "versao": int(versao),
                    "planilha": k_planilha,
                    "timestamp": timestamp.isoformat(),
                    "idade_minutos": (datetime.now() - timestamp).total_seconds() / 60,
                    "valido": self._is_cache_valid(key),
                    "registros": len(self.cache[key]) if key in self.cache else 0
                }
        
        return {
            "cache_ttl_minutos": self.cache_ttl.total_seconds() / 60,
            "itens_cache": len(self.cache),
            "detalhes": cache_info
        }

# Função para conversão de gráficos
def fig_to_image_response(fig: go.Figure) -> Response:
    """Converte figura para resposta HTTP de imagem PNG"""
    img_bytes = fig.to_image(format="png", engine="kaleido")
    return Response(content=img_bytes, media_type="image/png")

def fig_to_base64_image(fig: go.Figure) -> str:
    """Converte figura Plotly para imagem base64"""
    img_bytes = fig.to_image(format="png", engine="kaleido")
    img_base64 = base64.b64encode(img_bytes).decode()
    return img_base64

# Validação de parâmetros
def validate_parameters(produto: str, versao: int):
    """Valida parâmetros da requisição"""
    if produto not in VALID_PRODUTOS:
        raise HTTPException(
            status_code=400, 
            detail=f"Produto deve ser um de: {', '.join(VALID_PRODUTOS)}"
        )
    
    if versao < 1:
        raise HTTPException(
            status_code=400, 
            detail="Versão deve ser um número inteiro positivo"
        )

def validate_planilha(k_planilha: str):
    """Valida se a planilha é válida"""
    valid_planilhas = [
        K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS,
        K_PTRAFEGO_DADOS, K_PTRAFEGO_META_ADS, K_PTRAFEGO_ANUNCIOS_SUBIDOS,
        K_PCOPY_DADOS, K_GRUPOS_WPP, K_CLICKS_WPP, K_CENTRAL_LANCAMENTOS
    ]
    
    if k_planilha not in valid_planilhas:
        raise HTTPException(
            status_code=400,
            detail=f"Planilha inválida. Disponíveis: {valid_planilhas}"
        )

# Função para carregar credenciais do Streamlit
def load_google_credentials():
    """Carrega credenciais do Streamlit secrets"""
    try:
        return dict(st.secrets["gcp_service_account"])
    except KeyError:
        raise ValueError("Credenciais não encontradas no st.secrets['gcp_service_account']")

# Inicialização da aplicação
app = FastAPI(
    title="Dashboard Lançamentos API",
    description="API para acessar dados e gráficos dos lançamentos digitais",
    version="1.0.0"
)

# Variáveis globais
cache_manager = None

@app.on_event("startup")
async def startup_event():
    """Inicializa o cache manager na startup"""
    global cache_manager
    try:
        credentials_dict = load_google_credentials()
        cache_manager = DataCacheManager(
            cache_ttl_minutes=30,
            credentials_dict=credentials_dict
        )
        print("🚀 API iniciada com sistema de cache")
    except Exception as e:
        print(f"❌ Erro ao inicializar API: {e}")
        raise

# Endpoints da API
@app.get("/")
def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Dashboard Lançamentos API",
        "status": "running",
        "produtos_validos": VALID_PRODUTOS,
        "planilhas_disponiveis": [
            K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS,
            K_PTRAFEGO_DADOS, K_PTRAFEGO_META_ADS, K_PTRAFEGO_ANUNCIOS_SUBIDOS,
            K_PCOPY_DADOS, K_GRUPOS_WPP, K_CLICKS_WPP, K_CENTRAL_LANCAMENTOS
        ]
    }

@app.get("/health")
def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_items": len(cache_manager.cache) if cache_manager else 0
    }

@app.get("/dados/{produto}/{versao}/{planilha}")
def get_dados(produto: str, versao: int, planilha: str, force_reload: bool = False):
    """Retorna dados brutos de uma planilha específica"""
    validate_parameters(produto, versao)
    validate_planilha(planilha)
    
    try:
        df = cache_manager.get_dataframe(produto, versao, planilha, force_reload)
        
        return {
            "produto": produto,
            "versao": versao,
            "planilha": planilha,
            "total_registros": len(df),
            "colunas": list(df.columns),
            "dados": df.to_dict('records')[:1000],  # Limita a 1000 registros para evitar sobrecarga
            "total_dados": len(df),
            "ultima_atualizacao": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar dados: {str(e)}")

@app.get("/dados/{produto}/{versao}/{planilha}/info")
def get_dados_info(produto: str, versao: int, planilha: str):
    """Retorna informações sobre os dados sem os dados completos"""
    validate_parameters(produto, versao)
    validate_planilha(planilha)
    
    try:
        df = cache_manager.get_dataframe(produto, versao, planilha)
        
        # Informações sobre datas se existir coluna de data
        date_info = {}
        for col in df.columns:
            if 'data' in col.lower() or 'date' in col.lower():
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    date_info[col] = {
                        "inicio": df[col].min().isoformat() if pd.notna(df[col].min()) else None,
                        "fim": df[col].max().isoformat() if pd.notna(df[col].max()) else None
                    }
        
        return {
            "produto": produto,
            "versao": versao,
            "planilha": planilha,
            "total_registros": len(df),
            "colunas": list(df.columns),
            "tipos_dados": df.dtypes.astype(str).to_dict(),
            "informacoes_datas": date_info,
            "registros_nulos": df.isnull().sum().to_dict(),
            "ultima_atualizacao": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar informações: {str(e)}")

@app.get("/admin/cache/status")
def status_cache():
    """Mostra status do cache"""
    return cache_manager.get_cache_status()

@app.post("/admin/cache/limpar")
def limpar_cache():
    """Limpa todo o cache"""
    cache_manager.invalidate_cache()
    return {"message": "Cache limpo com sucesso"}

# Classe para gerenciar a API em background
class APIManager:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.is_running = False
    
    def start(self):
        """Inicia a API em background"""
        if not self.is_running:
            print(f"🚀 Iniciando API em {self.host}:{self.port}")
            
            def run_server():
                config = uvicorn.Config(
                    app, 
                    host=self.host, 
                    port=self.port, 
                    log_level="error"  # Reduz logs para não poluir o Streamlit
                )
                self.server = uvicorn.Server(config)
                asyncio.run(self.server.serve())
            
            self.thread = Thread(target=run_server, daemon=True)
            self.thread.start()
            self.is_running = True
            
            # Aguarda um pouco para a API iniciar
            time.sleep(2)
            print(f"✅ API rodando em http://{self.host}:{self.port}")
        else:
            print("ℹ️ API já está rodando")
    
    def stop(self):
        """Para a API"""
        if self.is_running and self.server:
            self.server.should_exit = True
            self.is_running = False
            print("🛑 API parada")
    
    def is_healthy(self):
        """Verifica se a API está saudável"""
        try:
            import requests
            response = requests.get(f"http://{self.host}:{self.port}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

# Instância global do gerenciador da API
api_manager = APIManager()

if __name__ == "__main__":
    # Se executado diretamente, roda apenas a API
    uvicorn.run(app, host="0.0.0.0", port=8000)