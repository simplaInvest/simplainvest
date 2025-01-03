import pandas as pd

def format_central_captura(df_central_captura):
    if df_central_captura.empty:
        raise ValueError("O DataFrame 'df_central_captura' está vazio.")
    df_central_captura['CAP DATA_CAPTURA'] = pd.to_datetime(df_central_captura['CAP DATA_CAPTURA'], dayfirst=True).dt.date
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
        df_ptrafego_metaads['VALOR USADO'] = df_ptrafego_metaads.loc[df_ptrafego_metaads['VALOR USADO'] != '']['VALOR USADO'].str.replace(",", "").str.replace("R$", "").astype(float)
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
