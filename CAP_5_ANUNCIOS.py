import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go

from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_VENDAS, K_PTRAFEGO_DADOS, get_df

# Carregar informações sobre lançamento selecionado
PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

# Carregar DataFrames para lançamento selecionado
loading_container = st.empty()
with loading_container:
    status = st.status("Carregando dados...", expanded=True)
    with status:
        df_captura = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_CAPTURA)
        df_prematricula = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_PRE_MATRICULA)
        df_vendas = get_df(PRODUTO, VERSAO_PRINCIPAL, K_CENTRAL_VENDAS)
        df_ptrafego_dados = get_df(PRODUTO, VERSAO_PRINCIPAL, K_PTRAFEGO_DADOS)
        status.update(label="Carregados com sucesso!", state="complete", expanded=False)
loading_container.empty()

if 'Captacao' not in st.session_state:
    Cap = []
    st.write('Lista de Captação vazia')
else:
    Cap = st.session_state['Captacao']

#------------------------------------------------------------
#      INÍCIO DO LAYOUT
#------------------------------------------------------------

st.caption("CAPTAÇÃO >  ANÚNCIOS")
st.title('Anúncios')

# Filtrar apenas os leads vindos de tráfego pago
df_captura_pago = df_captura[df_captura["UTM_MEDIUM"] == "pago"]


# Criar dummies para pré-matrícula e vendas
if df_prematricula is not None:
    df_captura_pago["PREMATRICULA"] = df_captura_pago["EMAIL"].isin(df_prematricula["EMAIL"]).astype(int)
else:
    df_captura_pago["PREMATRICULA"] = 0

if df_vendas is not None:
    df_captura_pago["VENDA"] = df_captura_pago["EMAIL"].isin(df_vendas["EMAIL"]).astype(int)
else:
    df_captura_pago["VENDA"] = 0

# Contar leads, pré-matrículas e vendas por anúncio
ranking_leads = df_captura_pago.groupby("UTM_TERM").agg(
    Leads_Capturados=("EMAIL", "count"),
    Prematriculas=("PREMATRICULA", "sum"),
    Vendas=("VENDA", "sum")
).reset_index()

# Renomear coluna de anúncios
ranking_leads = ranking_leads.rename(columns={"UTM_TERM": "Anúncio"})

# Ordenar do maior para o menor em número de leads capturados
ranking_leads = ranking_leads.sort_values(by="Leads_Capturados", ascending=False)

# Evitar divisão por zero
ranking_leads["Taxa de Conversão"] = ranking_leads.apply(
    lambda row: row["Vendas"] / row["Leads_Capturados"] if row["Leads_Capturados"] > 0 else 0, axis=1
)

# Formatar como porcentagem
ranking_leads["Taxa de Conversão"] = ranking_leads["Taxa de Conversão"] * 100  # Convertendo para %


cols = st.columns(2)

with cols[0]:
    # Exibir a tabela no Streamlit
    st.write("### 🔝 Ranking dos Melhores Anúncios")
    st.dataframe(ranking_leads, hide_index = True)

with cols[1]:
    # Filtrar os top 10 anúncios com mais vendas
    top_10_vendas = ranking_leads.sort_values(by="Vendas", ascending=False).head(10)

    # Criar gráfico de pizza usando Plotly
    fig_pizza = px.pie(
        top_10_vendas,
        names="Anúncio",
        values="Vendas",
        title="🍕 Top 10 Anúncios",
        labels={"Vendas": "Vendas"},
        hole=0.4  # Criar um gráfico de rosca
    )

    # Exibir gráfico no Streamlit
    st.plotly_chart(fig_pizza, use_container_width=True)

threshold = st.number_input("Digite um número:", min_value=0, max_value=1000, value=100)

# Criar gráfico de dispersão usando Plotly sem rótulos sobre os pontos e sem variação de tamanho
fig = px.scatter(
    ranking_leads[ranking_leads["Leads_Capturados"] >= threshold],
    x="Leads_Capturados",
    y="Taxa de Conversão",
    color="Taxa de Conversão",
    hover_name="Anúncio",
    title="🎯 Leads Capturados vs. Taxa de Conversão",
    labels={"Leads_Capturados": "Leads Capturados", "Taxa de Conversão": "Taxa de Conversão (%)"},
)

# Ajustar layout: definir tamanho fixo dos pontos e remover rótulos sobre os pontos
fig.update_traces(marker=dict(size=8))  # Define tamanho fixo dos pontos

fig.update_layout(
    xaxis=dict(title="Leads Capturados"),
    yaxis=dict(title="Taxa de Conversão (%)"),
    showlegend=False
)

# Exibir gráfico no Streamlit
st.plotly_chart(fig, use_container_width=True)

st.divider()

###########################################################
#
#               Scatterplot previsto
#
###########################################################

# proxy_vendas = pd.read_csv("proxy_vendas.csv", index_col = 0)

# # Filtrar apenas leads vindos de tráfego pago
# df_ptrafego_dados = df_ptrafego_dados[df_ptrafego_dados["UTM_MEDIUM"] == "pago"]

# # Criar um dicionário para armazenar os resultados
# resultados = []

# # Iterar sobre cada anúncio
# for anuncio in df_ptrafego_dados["UTM_TERM"].unique():
#     # Filtrar os leads daquele anúncio
#     df_anuncio = df_ptrafego_dados[df_ptrafego_dados["UTM_TERM"] == anuncio]
    
#     # Criar a tabela de captura (matriz renda x patrimônio)
#     tabela_captura = df_anuncio.pivot_table(
#         index="RENDA MENSAL",
#         columns="PATRIMONIO",
#         values="EMAIL",
#         aggfunc="count",
#         fill_value=0
#     )

#     # Garantir que as faixas estão na ordem correta
#     tabela_captura = tabela_captura.reindex(index=proxy_vendas.index, columns=proxy_vendas.columns, fill_value=0)

#     # Multiplicar pela proxy de vendas para obter as vendas previstas
#     tabela_vendas_previstas = tabela_captura * proxy_vendas

#     # Calcular o total de leads capturados e o total de vendas previstas
#     total_leads = tabela_captura.sum().sum()
#     total_vendas_previstas = tabela_vendas_previstas.sum().sum()

#     # Calcular a taxa de conversão prevista
#     taxa_conversao_prevista = (total_vendas_previstas / total_leads) if total_leads > 0 else 0

#     # Armazenar os resultados
#     resultados.append([anuncio, total_leads, taxa_conversao_prevista])

# # Criar um DataFrame final com os resultados
# df_resultado = pd.DataFrame(resultados, columns=["Nome do Anúncio", "Captura", "Taxa de Conversão Prevista"])

# # Ordenar do maior para o menor número de capturas
# df_resultado = df_resultado.sort_values(by="Captura", ascending=False)

# #Formatar a coluna de taxa de conversão para exibição melhorada
# df_resultado["Taxa de Conversão Prevista"] = df_resultado["Taxa de Conversão Prevista"] * 100

# # Exibir o resultado
# import streamlit as st
# st.write("### 📊 Previsão de Conversão por Anúncio")
# st.dataframe(df_resultado)

# # Criar gráfico de dispersão usando Plotly sem rótulos sobre os pontos e sem variação de tamanho
# fig = px.scatter(
#     df_resultado[df_resultado["Captura"] >= threshold],
#     y="Taxa de Conversão Prevista",
#     x="Captura",
#     color="Taxa de Conversão Prevista",
#     hover_name="Nome do Anúncio",
#     title="🎯 Leads Capturados vs. Taxa de Conversão Prevista",
#     labels={"Captura": "Leads Capturados", "Taxa de Conversão Prevista": "Taxa de Conversão Prevista (%)"},
# )

# # Ajustar layout: definir tamanho fixo dos pontos e remover rótulos sobre os pontos
# fig.update_traces(marker=dict(size=8))  # Define tamanho fixo dos pontos

# fig.update_layout(
#     xaxis=dict(title="Leads Capturados"),
#     yaxis=dict(title="Taxa de Conversão Prevista (%)"),
#     showlegend=False
# )

# # Exibir gráfico no Streamlit
# st.plotly_chart(fig, use_container_width=True)


# # Filtrar apenas os anúncios que capturaram mais de 'threshold' leads
# predictions = df_resultado[df_resultado["Captura"] >= threshold].copy()
# real = ranking_leads[ranking_leads["Leads_Capturados"] >= threshold].copy()

# # Ajustar índices para facilitar a comparação
# predictions.set_index("Nome do Anúncio", inplace=True)
# real.set_index("Anúncio", inplace=True)

# # Garantir que os DataFrames tenham apenas anúncios em comum
# anuncios_comuns = predictions.index.intersection(real.index)

# # Filtrar os DataFrames com base nos anúncios comuns
# predictions = predictions.loc[anuncios_comuns]
# real = real.loc[anuncios_comuns]

# # Calcular erro absoluto médio (MAE)
# mae = (real["Taxa de Conversão"] - predictions["Taxa de Conversão Prevista"]).abs().mean()
# mae


