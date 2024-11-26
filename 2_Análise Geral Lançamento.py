import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px

# Cacheamento de Processamento de Dados
@st.cache_data
def processa_dados_grupos(df_GRUPOS):
    # Verifique se o DataFrame está vazio
    if df_GRUPOS.empty:
        st.warning("O DataFrame 'df_GRUPOS' está vazio.")
        return pd.DataFrame()

    # Verifique se a coluna 'Data' existe
    if 'Data' not in df_GRUPOS.columns:
        st.error("A coluna 'Data' não foi encontrada no DataFrame 'df_GRUPOS'.")
        return pd.DataFrame()

    # Converta a coluna 'Data' para datetime, se necessário
    if not pd.api.types.is_datetime64_any_dtype(df_GRUPOS['Data']):
        try:
            df_GRUPOS['Data'] = pd.to_datetime(df_GRUPOS['Data'].astype(str).str.split(' às ').str[0], format='%d/%m/%Y', errors='coerce')
        except Exception as e:
            st.error(f"Erro ao converter a coluna 'Data': {e}")
            return pd.DataFrame()

    # Adicione uma coluna 'Membros' para representar as entradas/saídas
    df_GRUPOS['Membros'] = df_GRUPOS['Evento'].apply(lambda x: 1 if x == 'Entrou no grupo' else -1)

    # Faça o cálculo cumulativo de membros por dia
    try:
        df_GRUPOS = df_GRUPOS.groupby('Data')['Membros'].sum().cumsum().reset_index()
        df_GRUPOS.columns = ['Date', 'Members']
    except Exception as e:
        st.error(f"Erro ao processar os dados de membros: {e}")
        return pd.DataFrame()

    return df_GRUPOS



# Cacheamento para Gráficos
@st.cache_data
def plot_group_members_per_day_altair(df_CONTAGRUPOS):
    # Verificar se o DataFrame não está vazio
    if df_CONTAGRUPOS.empty:
        st.warning("Os dados de contagem de membros estão vazios.")
        return None

    # Criar o gráfico de linhas com Altair
    line_chart = alt.Chart(df_CONTAGRUPOS).mark_line(point=True).encode(
        x=alt.X('Date:T', title='Data', axis=alt.Axis(labelAngle=-45, format="%d %B (%a)")),
        y=alt.Y('Members:Q', title='Número de Membros'),
        tooltip=['Date:T', 'Members:Q']
    )

    # Adicionar valores como texto acima dos pontos
    text_chart = alt.Chart(df_CONTAGRUPOS).mark_text(
        align='center',
        baseline='bottom',
        color = 'lightblue',
        dy=-10  # Ajusta a posição vertical do texto
    ).encode(
        x='Date:T',
        y='Members:Q',
        text=alt.Text('Members:Q', format=',')  # Exibe o número formatado
    )

    # Combinar os gráficos
    chart = (line_chart + text_chart).properties(
        title='Número de Membros no Grupo por Dia',
        width=600,
        height=400
    ).configure_axis(
        grid=False,
        labelColor='white',
        titleColor='white'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        color='white'
    ).configure(background='rgba(0,0,0,0)')

    return chart

@st.cache_data
def plot_leads_per_day_altair(df_CONTALEADS):
    # Verificar se o DataFrame não está vazio
    if df_CONTALEADS.empty:
        st.warning("Os dados de Leads por Dia estão vazios.")
        return None

    # Criar o gráfico de linhas com Altair
    line_chart = alt.Chart(df_CONTALEADS).mark_line(point=True).encode(
        x=alt.X('CAP DATA_CAPTURA:T', title='Data', axis=alt.Axis(labelAngle=-45, format="%d %B (%a)")),
        y=alt.Y('EMAIL:Q', title='Número de Leads'),
        tooltip=['CAP DATA_CAPTURA:T', 'EMAIL:Q']
    )

    # Adicionar valores como texto acima dos pontos
    text_chart = alt.Chart(df_CONTALEADS).mark_text(
        align='center',
        baseline='bottom',
        dy=-10,  # Ajusta a posição vertical do texto
        color='lightblue'  # Define a cor do texto
    ).encode(
        x='CAP DATA_CAPTURA:T',
        y='EMAIL:Q',
        text=alt.Text('EMAIL:Q', format=',')  # Exibe o número formatado
    )

    # Combinar os gráficos
    chart = (line_chart + text_chart).properties(
        title='Leads por Dia',
        width=600,
        height=400
    ).configure_axis(
        grid=False,
        labelColor='white',
        titleColor='white'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        color='white'
    ).configure(background='rgba(0,0,0,0)')

    return chart


# Função para estilizar e exibir gráficos com fundo transparente e letras brancas
def styled_bar_chart(x, y, title, colors=['#ADD8E6', '#5F9EA0']):
    fig = go.Figure(data=[
        go.Bar(x=[x[0]], y=[y[0]], marker_color=colors[0]),
        go.Bar(x=[x[1]], y=[y[1]], marker_color=colors[1])
    ])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  
        paper_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='white'),  
        title=dict(text=title, x=0.5, font=dict(size=20, color='white')),
        xaxis=dict(showgrid=False, tickfont=dict(color='white')),
        yaxis=dict(showgrid=False, tickfont=dict(color='white')),
        margin=dict(l=0, r=0, t=40, b=40)
    )
    return fig

# Função para aplicar estilos
def color_rows(row):
    colors = {
        'Menos de R$5 mil': 'background-color: #660000', 
        'Entre R$5 mil e R$20 mil': 'background-color: #8B1A1A', 
        'Entre R$20 mil e R$100 mil': 'background-color: #8F6500', 
        'Entre R$100 mil e R$250 mil': 'background-color: #445522', 
        'Entre R$250 mil e R$500 mil': 'background-color: #556B22', 
        'Entre R$500 mil e R$1 milhão': 'background-color: #000070', 
        'Acima de R$1 milhão': 'background-color: #2F4F4F'  
    }
    return [colors.get(row['PATRIMONIO'], '')] * len(row)

# Estilização das abas
st.markdown(
    """
    <style>
    .css-1n543e5 { 
        border-radius: 8px !important;
        margin-right: 8px !important;
    }
    .css-1n543e5:hover {  
        background-color: #f0f0f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Verifique se os dados foram carregados
if 'sheets_loaded' in st.session_state and st.session_state.sheets_loaded:
    df_PESQUISA = st.session_state.df_PESQUISA.copy()
    df_CAPTURA = st.session_state.df_CAPTURA.copy()
    df_PREMATRICULA = st.session_state.df_PREMATRICULA.copy()
    df_VENDAS = st.session_state.df_VENDAS.copy()
    df_COPY = st.session_state.df_COPY.copy()
    df_GRUPOS = processa_dados_grupos(st.session_state.df_GRUPOS)
else:
    st.error("Os dados não foram carregados. Por favor, atualize a página e carregue os dados. Se o erro persistir, contacte o time de TI.")
    st.query_params = {"page": "Inicio"}

# Calcular conversões
total_copy = len(df_COPY)
total_pesquisa = len(df_PESQUISA)
total_captura = len(df_CAPTURA)
total_prematricula = len(df_PREMATRICULA)
total_vendas = len(df_VENDAS)

conversao_pesquisa = (total_pesquisa / total_captura) * 100 if total_pesquisa > 0 else 0
conversao_prematricula = (total_prematricula / total_captura) * 100 if total_captura > 0 else 0
conversao_vendas = (total_vendas / total_captura) * 100 if total_prematricula > 0 else 0
conversao_copy = (total_copy / total_captura) * 100 if total_vendas > 0 else 0


df_CONTALEADS = df_CAPTURA.copy()
df_CONTALEADS['CAP DATA_CAPTURA'] = pd.to_datetime(df_CONTALEADS['CAP DATA_CAPTURA']).dt.date
#st.dataframe(df_CONTALEADS)
df_CONTALEADS = df_CONTALEADS[['EMAIL', 'CAP DATA_CAPTURA']].groupby('CAP DATA_CAPTURA').count().reset_index()

df_CONTAGRUPOS = df_GRUPOS.copy()
#df_CONTAGRUPOS['Data'] = pd.to_datetime(df_CONTAGRUPOS['Data']).dt.date
#st.dataframe(df_CONTAGRUPOS)





# Contar o número de membros por dia utilizando df_GRUPOS
if not df_GRUPOS.empty and 'Data' in df_GRUPOS.columns:
    df_member_count = df_GRUPOS[['Data', 'Members']].copy()

# Criando tabelas cruzadas PATRIMONIO x RENDA
categorias_patrimonio = [
    'Menos de R$5 mil', 'Entre R$5 mil e R$20 mil', 'Entre R$20 mil e R$100 mil',
    'Entre R$100 mil e R$250 mil', 'Entre R$250 mil e R$500 mil',
    'Entre R$500 mil e R$1 milhão', 'Acima de R$1 milhão'
]
categorias_renda = [
    'Até R$1.500', 'Entre R$1.500 e R$2.500', 'Entre R$2.500 e R$5.000',
    'Entre R$5.000 e R$10.000', 'Entre R$10.000 e R$20.000', 'Acima de R$20.000'
]

df_PESQUISA['PATRIMONIO'] = pd.Categorical(df_PESQUISA['PATRIMONIO'], categories=categorias_patrimonio, ordered=True)
df_PESQUISA['RENDA MENSAL'] = pd.Categorical(df_PESQUISA['RENDA MENSAL'], categories=categorias_renda, ordered=True)

tabela_cruzada1_ordenada = pd.crosstab(df_PESQUISA['PATRIMONIO'], df_PESQUISA['RENDA MENSAL'])

if not df_VENDAS.empty:
    df_VENDAS['PATRIMONIO'] = pd.Categorical(df_VENDAS['PATRIMONIO'], categories=categorias_patrimonio, ordered=True)
    df_VENDAS['RENDA MENSAL'] = pd.Categorical(df_VENDAS['RENDA MENSAL'], categories=categorias_renda, ordered=True)
    tabela_cruzada1_vendas = pd.crosstab(df_VENDAS['PATRIMONIO'], df_VENDAS['RENDA MENSAL'])

    tabela_empilhada = tabela_cruzada1_ordenada.stack().reset_index()
    tabela_empilhada_vendas = tabela_cruzada1_vendas.stack().reset_index()

    tabela_empilhada.columns = ['PATRIMONIO', 'RENDA MENSAL', 'LEADS']
    tabela_empilhada_vendas.columns = ['PATRIMONIO', 'RENDA MENSAL', 'ALUNOS']

    tabela_empilhada['FAIXA PATRIMONIO x RENDA MENSAL'] = tabela_empilhada['PATRIMONIO'].copy().astype(str) + ' x ' + tabela_empilhada['RENDA MENSAL'].astype(str)
    tabela_empilhada_vendas['FAIXA PATRIMONIO x RENDA MENSAL'] = tabela_empilhada_vendas['PATRIMONIO'].astype(str) + ' x ' + tabela_empilhada_vendas['RENDA MENSAL'].astype(str)

    tabela_final = tabela_empilhada[['FAIXA PATRIMONIO x RENDA MENSAL', 'LEADS', 'PATRIMONIO']]
    tabela_final_vendas = tabela_empilhada_vendas[['FAIXA PATRIMONIO x RENDA MENSAL', 'ALUNOS','PATRIMONIO']]
    #st.dataframe(tabela_final)
    #st.dataframe(tabela_final_vendas)
    
    tabela_combined = pd.merge(tabela_final, tabela_final_vendas, on='FAIXA PATRIMONIO x RENDA MENSAL', how='outer')
    tabela_combined[['LEADS', 'ALUNOS']] = tabela_combined[['LEADS', 'ALUNOS']].fillna(0)
    tabela_combined['CONVERSÃO'] = (tabela_combined['ALUNOS'] / tabela_combined['LEADS'])
    #st.dataframe(tabela_combined)
    df_EXIBICAO = tabela_combined.copy()
    df_EXIBICAO['CONVERSÃO'] = df_EXIBICAO['CONVERSÃO']*100
    df_EXIBICAO['CONVERSÃO'] = df_EXIBICAO['CONVERSÃO'].apply(lambda x: f"{x:.2f}%")
    df_EXIBICAO.drop(columns=['PATRIMONIO_y'], inplace=True)
    df_EXIBICAO.rename(columns={'PATRIMONIO_x': 'PATRIMONIO'}, inplace=True)
    #st.dataframe(df_EXIBICAO)
    df_EXIBICAO_STYLED = df_EXIBICAO.style.apply(color_rows, axis=1) 




else:
    tabela_empilhada = tabela_cruzada1_ordenada.stack().reset_index()
    tabela_empilhada.columns = ['PATRIMONIO', 'RENDA MENSAL', 'LEADS']
    tabela_empilhada['FAIXA PATRIMONIO x RENDA MENSAL'] = tabela_empilhada['PATRIMONIO'].astype(str) + ' x ' + tabela_empilhada['RENDA MENSAL'].astype(str)
    tabela_combined = tabela_empilhada[['FAIXA PATRIMONIO x RENDA MENSAL', 'LEADS']]
    total_leads = tabela_combined['LEADS'].sum()
    tabela_combined['% DO TOTAL DE LEADS'] = (tabela_combined['LEADS'] / total_leads)
    df_EXIBICAO = tabela_combined.copy()
    df_EXIBICAO['% DO TOTAL DE LEADS'] = df_EXIBICAO['% DO TOTAL DE LEADS']*100
    df_EXIBICAO['% DO TOTAL DE LEADS'] = df_EXIBICAO['% DO TOTAL DE LEADS'].apply(lambda x: f"{x:.2f}%")
    df_EXIBICAO_STYLED = df_EXIBICAO.style.apply(color_rows, axis=1) 

tabela_combined['PATRIMONIO'] = pd.Categorical(
    tabela_combined['FAIXA PATRIMONIO x RENDA MENSAL'].str.split(' x ').str[0],
    categories=categorias_patrimonio,
    ordered=True
)
tabela_combined['RENDA MENSAL'] = pd.Categorical(
    tabela_combined['FAIXA PATRIMONIO x RENDA MENSAL'].str.split(' x ').str[1],
    categories=categorias_renda,
    ordered=True
)
tabela_combined = tabela_combined.sort_values(by=['PATRIMONIO', 'RENDA MENSAL']).reset_index(drop=True)

    
tabs = st.tabs(["Dados Gerais do Lançamento" , "Análises de Patrimônio e Renda", "Análise de Percurso dos Leads"])

#--------------------------------------------------------------------------#
#Criando dados para o Heatmap e Scatterplot

if not df_VENDAS.empty:
    new_colorscale = [
        [0.0, 'white'],      
        [0.0001, 'green'],   
        [0.25, 'yellow'],
        [0.5, 'orange'],
        [0.75, 'red'],
        [1.0, 'purple']
    ]

    contagem = pd.crosstab(tabela_combined['PATRIMONIO'], tabela_combined['RENDA MENSAL'], values=tabela_combined['LEADS'], aggfunc='sum').fillna(0)
    vendas = pd.crosstab(tabela_combined['PATRIMONIO'], tabela_combined['RENDA MENSAL'], values=tabela_combined['ALUNOS'], aggfunc='sum').fillna(0)
    taxa_conversao = (vendas / contagem).fillna(0)

    max_taxa_conversao = taxa_conversao.max().max()
    max_valor = max_taxa_conversao + 0.05

    crosstab = contagem.astype(int).astype(str) + ' Leads<br>' + vendas.astype(int).astype(str) + ' Alunos<br>' + (taxa_conversao * 100).round(2).astype(str) + '% Conversão'

    heatmap = go.Figure(data=go.Heatmap(
        z=taxa_conversao.values,
        x=contagem.columns,
        y=contagem.index,
        text=crosstab.values,
        texttemplate="%{text}",
        textfont={"size": 14, "color": "black"},
        colorscale=new_colorscale,  
        zmin=0,
        zmax=max_valor,
        colorbar=dict(title='Taxa de Conversão', tickcolor='white')
    ))

    heatmap.update_layout(
        title='Mapa de Calor: Patrimônio vs Renda com Taxa de Conversão',
        xaxis=dict(title='Renda', showgrid=False),
        yaxis=dict(title='Patrimônio', showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)',  
        paper_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='white'),
        coloraxis_colorbar=dict(title='Taxa de Conversão', tickcolor='white'),
        autosize=False,
        width=1200,  
        height=900  
    )

    contagem_flat = contagem.stack().reset_index()
    contagem_flat.columns = ['PATRIMONIO', 'RENDA MENSAL', 'LEADS']
    vendas_flat = vendas.stack().reset_index()
    vendas_flat.columns = ['PATRIMONIO', 'RENDA MENSAL', 'ALUNOS']
    taxa_conversao_flat = taxa_conversao.stack().reset_index()
    taxa_conversao_flat.columns = ['PATRIMONIO', 'RENDA MENSAL', 'TAXA_CONVERSAO']

    scatter_df = contagem_flat.merge(vendas_flat, on=['PATRIMONIO', 'RENDA MENSAL']).merge(taxa_conversao_flat, on=['PATRIMONIO', 'RENDA MENSAL'])
    size_scale = 100
    scatter_df['size'] = np.log1p(scatter_df['LEADS']) * size_scale  

    scttplt = px.scatter(
        scatter_df,
        x='RENDA MENSAL',
        y='PATRIMONIO',
        size='size',
        color='TAXA_CONVERSAO',
        color_continuous_scale=new_colorscale,
        hover_data={'LEADS': True, 'ALUNOS': True, 'TAXA_CONVERSAO': True, 'size': False},
        title='Scatterplot: Patrimônio vs Renda com Taxa de Conversão',
        size_max=30
    )

    scttplt.update_layout(
        xaxis=dict(title='Renda Mensal', showgrid=False),
        yaxis=dict(title='Patrimônio', showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)',  
        paper_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='white')
    )

#--------------------------------------------------------------------------#
# Sessão de exibição dos dados e gráficos

with tabs[0]:
    st.markdown("<h1 style='text-align: center; font-size: 3.2vw; margin-bottom: 40px; margin-top: 40px; color: gold;hover-color: red'>Dados Gerais do Lançamento</h1>", unsafe_allow_html=True)
    st.divider()
    with st.container(border=False):
        st.markdown("<h2 style='text-align: left; font-size: 2vw; margin-bottom: 28px; color: lightblue;hover-color: red'>Métricas Gerais</h1>", unsafe_allow_html=True)
        ctcol1, ctcol2, ctcol3, ctcol4, ctcol5 = st.columns([1, 1, 1, 1, 1])
        with ctcol1:
            st.metric("Leads Totais Captura", total_captura)
        with ctcol2:
            st.metric("Leads Totais Pesquisa", total_pesquisa)
        with ctcol3:
            st.metric("Conversão Geral Pesquisa", f"{conversao_pesquisa:.2f}%")        
        with ctcol4:
            st.metric("Vendas Totais", total_vendas)
        with ctcol5:
            st.metric("Conversão Geral do Lançamento", f"{conversao_vendas:.2f}%")
    
    st.divider()
   
    fig = plot_leads_per_day_altair(df_CONTALEADS)
    if fig:
        st.altair_chart(fig, use_container_width=True)

    

    # Exibindo o gráfico usando Altair
    fig = plot_group_members_per_day_altair(df_CONTAGRUPOS)
    if fig:
        st.altair_chart(fig, use_container_width=True)


with tabs[1]:   
   
    if not df_VENDAS.empty:
        st.plotly_chart(heatmap)    
        st.plotly_chart(scttplt)            
        st.dataframe(df_EXIBICAO_STYLED)  
    
    st.subheader("CONVERSÃO POR FAIXA DE PATRIMONIO")
    col3, col4 = st.columns([3, 2])
    with col3:
        if not df_VENDAS.empty:
            tabela_patrimonio = tabela_combined.groupby('PATRIMONIO').agg({'LEADS': 'sum', 'ALUNOS': 'sum'}).reset_index()
            tabela_patrimonio['CONVERSÃO'] = (tabela_patrimonio['ALUNOS'] / tabela_patrimonio['LEADS']) * 100
            tabela_patrimonio['CONVERSÃO'] = tabela_patrimonio['CONVERSÃO'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_patrimonio)
        else:
            tabela_patrimonio = tabela_combined.groupby('PATRIMONIO').agg({'LEADS': 'sum'}).reset_index()
            total_leads = tabela_patrimonio['LEADS'].sum()
            tabela_patrimonio['% DO TOTAL DE LEADS'] = (tabela_patrimonio['LEADS'] / total_leads) * 100
            tabela_patrimonio['% DO TOTAL DE LEADS'] = tabela_patrimonio['% DO TOTAL DE LEADS'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_patrimonio)

    with col4:
        if not df_VENDAS.empty:
            fig_patrimonio, ax_patrimonio = plt.subplots()
            tabela_patrimonio['CONVERSÃO_NUM'] = tabela_patrimonio['CONVERSÃO'].str.rstrip('%').astype('float')
            ax_patrimonio.bar(tabela_patrimonio['PATRIMONIO'], tabela_patrimonio['CONVERSÃO_NUM'])
            ax_patrimonio.set_title('Conversão por Faixa de PATRIMONIO', color='#FFFFFF')
            ax_patrimonio.set_ylabel('Conversão (%)', color='#FFFFFF')
            ax_patrimonio.set_xticklabels(tabela_patrimonio['PATRIMONIO'], rotation=45, ha='right', color='#FFFFFF')
            ax_patrimonio.set_facecolor('none')
            fig_patrimonio.patch.set_facecolor('none')
            ax_patrimonio.spines['bottom'].set_color('#FFFFFF')
            ax_patrimonio.spines['top'].set_color('#FFFFFF')
            ax_patrimonio.spines['right'].set_color('#FFFFFF')
            ax_patrimonio.spines['left'].set_color('#FFFFFF')
            ax_patrimonio.tick_params(axis='x', colors='#FFFFFF')
            ax_patrimonio.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_patrimonio)
        else:
            fig_patrimonio, ax_patrimonio = plt.subplots()
            tabela_patrimonio['PERCENTUAL_NUM'] = tabela_patrimonio['% DO TOTAL DE LEADS'].str.rstrip('%').astype('float')
            ax_patrimonio.bar(tabela_patrimonio['PATRIMONIO'], tabela_patrimonio['PERCENTUAL_NUM'])
            ax_patrimonio.set_title('Percentual de LEADS por Faixa de PATRIMONIO', color='#FFFFFF')
            ax_patrimonio.set_ylabel('Percentual (%)', color='#FFFFFF')
            ax_patrimonio.set_xticklabels(tabela_patrimonio['PATRIMONIO'], rotation=45, ha='right', color='#FFFFFF')
            ax_patrimonio.set_facecolor('none')
            fig_patrimonio.patch.set_facecolor('none')
            ax_patrimonio.spines['top'].set_color('#FFFFFF')
            ax_patrimonio.spines['bottom'].set_color('#FFFFFF')
            ax_patrimonio.spines['left'].set_color('#FFFFFF')
            ax_patrimonio.spines['right'].set_color('#FFFFFF')
            ax_patrimonio.tick_params(axis='x', colors='#FFFFFF')
            ax_patrimonio.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_patrimonio)

    st.subheader("CONVERSÃO POR FAIXA DE RENDA")
    col5, col6 = st.columns([3, 2])
    with col5:
        if not df_VENDAS.empty:
            tabela_renda = tabela_combined.groupby('RENDA MENSAL').agg({'LEADS': 'sum', 'ALUNOS': 'sum'}).reset_index()
            tabela_renda['CONVERSÃO'] = (tabela_renda['ALUNOS'] / tabela_renda['LEADS']) * 100
            tabela_renda['CONVERSÃO'] = tabela_renda['CONVERSÃO'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_renda)
        else:
            tabela_renda = tabela_combined.groupby('RENDA MENSAL').agg({'LEADS': 'sum'}).reset_index()
            total_leads = tabela_renda['LEADS'].sum()
            tabela_renda['% DO TOTAL DE LEADS'] = (tabela_renda['LEADS'] / total_leads) * 100
            tabela_renda['% DO TOTAL DE LEADS'] = tabela_renda['% DO TOTAL DE LEADS'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_renda)

    with col6:
        if not df_VENDAS.empty:
            fig_renda, ax_renda = plt.subplots()
            tabela_renda['CONVERSÃO_NUM'] = tabela_renda['CONVERSÃO'].str.rstrip('%').astype('float')
            ax_renda.bar(tabela_renda['RENDA MENSAL'], tabela_renda['CONVERSÃO_NUM'])
            ax_renda.set_title('Conversão por Faixa de Renda', color='#FFFFFF')
            ax_renda.set_ylabel('Conversão (%)', color='#FFFFFF')
            ax_renda.set_xticklabels(tabela_renda['RENDA MENSAL'], rotation=45, ha='right', color='#FFFFFF')
            ax_renda.set_facecolor('none')
            fig_renda.patch.set_facecolor('none')
            ax_renda.spines['bottom'].set_color('#FFFFFF')
            ax_renda.spines['top'].set_color('#FFFFFF')
            ax_renda.spines['right'].set_color('#FFFFFF')
            ax_renda.spines['left'].set_color('#FFFFFF')
            ax_renda.tick_params(axis='x', colors='#FFFFFF')
            ax_renda.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_renda)
        else:
            fig_renda, ax_renda = plt.subplots()
            tabela_renda['PERCENTUAL_NUM'] = tabela_renda['% DO TOTAL DE LEADS'].str.rstrip('%').astype('float')
            ax_renda.bar(tabela_renda['RENDA MENSAL'], tabela_renda['PERCENTUAL_NUM'])
            ax_renda.set_title('Percentual de LEADS por Faixa de Renda', color='#FFFFFF')
            ax_renda.set_ylabel('Percentual (%)', color='#FFFFFF')
            ax_renda.set_xticklabels(tabela_renda['RENDA MENSAL'], rotation=45, ha='right', color='#FFFFFF')
            ax_renda.set_facecolor('none')
            fig_renda.patch.set_facecolor('none')
            ax_renda.spines['bottom'].set_color('#FFFFFF')
            ax_renda.spines['top'].set_color('#FFFFFF')
            ax_renda.spines['right'].set_color('#FFFFFF')
            ax_renda.spines['left'].set_color('#FFFFFF')
            ax_renda.tick_params(axis='x', colors='#FFFFFF')
            ax_renda.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_renda)

    

with tabs[2]:
    if not df_VENDAS.empty:
        df_vendas_copy = df_VENDAS.copy()
        df_vendas_copy['CAP UTM_SOURCE'] = df_vendas_copy.apply(
            lambda x: f"{x['CAP UTM_SOURCE']} {x['CAP UTM_MEDIUM']}" if x['CAP UTM_SOURCE'] == 'ig' else x['CAP UTM_SOURCE'],
            axis=1
        )
        df_vendas_copy['PERCURSO'] = df_vendas_copy['CAP UTM_SOURCE'].astype(str) + ' > ' + \
                                      df_vendas_copy['PM UTM_SOURCE'].astype(str) + ' > ' + \
                                      df_vendas_copy['UTM_SOURCE'].astype(str)

        percurso_counts = df_vendas_copy['PERCURSO'].value_counts().reset_index()
        percurso_counts.columns = ['PERCURSO', 'COUNT']

        top_20_percurso = percurso_counts.head(20)

        st.subheader("Análise de Percurso de Leads")
        col1, col2 = st.columns([3, 2])

        with col1:
            st.table(top_20_percurso)

        top_5_percurso = top_20_percurso.head(5).sort_values(by='COUNT', ascending=True)

        with col2:
            fig, ax = plt.subplots()
            colors = cm.Blues(np.linspace(0.4, 1, len(top_5_percurso)))
            ax.barh(top_5_percurso['PERCURSO'], top_5_percurso['COUNT'], color=colors)
            ax.set_xlabel('Count', color='#FFFFFF')
            ax.set_ylabel('PERCURSO', color='#FFFFFF')
            ax.set_title('Top 5 Percursos Mais Comuns', color='#FFFFFF')
            ax.set_facecolor('none')
            fig.patch.set_facecolor('none')
            ax.spines['bottom'].set_color('#FFFFFF')
            ax.spines['top'].set_color('#FFFFFF')
            ax.spines['right'].set_color('#FFFFFF')
            ax.spines['left'].set_color('#FFFFFF')
            ax.tick_params(axis='x', colors='#FFFFFF')
            ax.tick_params(axis='y', colors='#FFFFFF')
            plt.tight_layout()
            st.pyplot(fig)
    else:
        st.warning("Ainda não há vendas realizadas para executarmos a Análise de Percurso de Leads.")
