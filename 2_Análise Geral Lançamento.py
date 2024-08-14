import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
from urllib.parse import unquote_plus
import plotly.express as px
import plotly.express as px
import pandas as pd
import streamlit as st
import pandas as pd
import plotly.express as px

def plot_group_members_per_day(df_member_count):
    # Criar gráfico de linha
    fig = px.line(df_member_count, x='Date', y='Members', title='Número de Membros no Grupo por Dia')

    # Customizar a aparência do gráfico
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo do gráfico transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fundo da figura transparente
        font=dict(color='white'),  # Cor das fontes
        title=dict(x=0.5, font=dict(size=20, color='white')),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color='white'),
            tickformat="%d %B (%a)",  # Formato do tick do eixo x
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color='white')
        )
    )

    return fig

def plot_leads_per_day(df, date_column):
    # Certifique-se de que a coluna de datas está no formato datetime e ignore o horário
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce').dt.date

    # Contar leads por dia
    leads_per_day = df[date_column].value_counts().sort_index()

    # Criar DataFrame para os dados do gráfico
    df_leads_per_day = pd.DataFrame({'Date': leads_per_day.index, 'Leads': leads_per_day.values})
    df_leads_per_day.set_index('Date', inplace=True)

    # Criar gráfico de linha
    fig = px.line(df_leads_per_day, x=df_leads_per_day.index, y='Leads', title='Leads por Dia')

    # Customizar a aparência do gráfico
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo do gráfico transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fundo da figura transparente
        font=dict(color='white'),  # Cor das fontes
        title=dict(x=0.5, font=dict(size=20, color='white')),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color='white'),
            tickformat="%d %B (%a)",  # Formato do tick do eixo x
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color='white')
        )
    )

    return fig

# Função para estilizar e exibir gráficos com fundo transparente e letras brancas
def styled_bar_chart(x, y, title, colors=['#ADD8E6', '#5F9EA0']):

    fig = go.Figure(data=[
        go.Bar(x=[x[0]], y=[y[0]], marker_color=colors[0]),
        go.Bar(x=[x[1]], y=[y[1]], marker_color=colors[1])
    ])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo do gráfico transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fundo da figura transparente
        font=dict(color='white'),  # Cores das fontes
        title=dict(text=title, x=0.5, font=dict(size=20, color='white')),
        xaxis=dict(showgrid=False, tickfont=dict(color='white')),
        yaxis=dict(showgrid=False, tickfont=dict(color='white')),
        margin=dict(l=0, r=0, t=40, b=40)  # Ajusta as margens para evitar corte do título
    )

    return fig

 # Função para aplicar estilos
def color_rows(row):
    colors = {
        'Menos de R$5 mil': 'background-color: #660000',  # Dark Red (darker)
        'Entre R$5 mil e R$20 mil': 'background-color: #8B1A1A',  # Dark Brown (darker)
        'Entre R$20 mil e R$100 mil': 'background-color: #8F6500',  # Dark Goldenrod (darker)
        'Entre R$100 mil e R$250 mil': 'background-color: #445522',  # Dark Olive Green (darker)
        'Entre R$250 mil e R$500 mil': 'background-color: #556B22',  # Olive Drab (darker)
        'Entre R$500 mil e R$1 milhão': 'background-color: #000070',  # Dark Blue (darker)
        'Acima de R$1 milhão': 'background-color: #2F4F4F'  # Dark Slate Gray
    }
    return [colors.get(row['PATRIMONIO'], '')] * len(row)


# Estilização das abas
st.markdown(
    """
    <style>
    .css-1n543e5 {  /* class for tab buttons */
        border-radius: 8px !important;
        margin-right: 8px !important;
    }
    .css-1n543e5:hover {  /* class for tab buttons on hover */
        background-color: #f0f0f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Verifique se os dados foram carregados
if 'sheets_loaded' in st.session_state and st.session_state.sheets_loaded:
    # Carregar os dataframes da sessão
    df_PESQUISA = st.session_state.df_PESQUISA.copy()
    df_CAPTURA = st.session_state.df_CAPTURA.copy()
    df_PREMATRICULA = st.session_state.df_PREMATRICULA.copy()
    df_VENDAS = st.session_state.df_VENDAS.copy()
    df_COPY = st.session_state.df_COPY.copy()
    df_GRUPOS = st.session_state.df_GRUPOS.copy()
   
else:
    st.error("Os dados não foram carregados. Por favor, atualize a página e carregue os dados. Se o erro persistir, contacte o time de TI")
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


# Criar DataFrame com os dados e valores
data = {
    'DADO': ['Leads Totais Captura', 'Vendas Totais', 'Conversão Geral do Lançamento', 'Leads Totais Pesquisa', 'Conversão Captura/Pesquisa'],
    'VALOR': [total_captura, total_vendas, f"{conversao_vendas:.2f}%", total_pesquisa, f"{conversao_pesquisa:.2f}%"]
}
df_dados = pd.DataFrame(data)


#------------------------------------------------------------------#
#CONTAR O NUMERO DE MEMBROS POR DIA UTILIZANDO df_GRUPOS
if 'Data' in df_GRUPOS.columns:
    df_GRUPOS['Data'] = pd.to_datetime(df_GRUPOS['Data'].str.split(' às ').str[0], format='%d/%m/%Y', errors='coerce')
    df_GRUPOS = df_GRUPOS.sort_values('Data')
#else:
    #st.warning("A coluna 'Data' não foi encontrada no DataFrame df_GRUPOS. Pulando a ordenação dos dados.")
    # Se 'Data' não existir, df_GRUPOS permanece inalterado

if not df_GRUPOS.empty and 'Data' in df_GRUPOS.columns:
    # Ordenar o DataFrame pelas datas
    df_GRUPOS = df_GRUPOS.sort_values('Data')
    # Inicializar uma variável para contar o número de membros e um dicionário para armazenar o número de membros por dia
    current_members = 0
    members_per_day = {}
    # Iterar sobre os eventos para calcular o número de membros
    for i, row in df_GRUPOS.iterrows():
        if row['Evento'] == 'Entrou no grupo':
            current_members += 1
        elif row['Evento'] == 'Saiu do grupo':
            current_members -= 1

        # Atualizar o número de membros para o dia
        members_per_day[row['Data']] = current_members
    # Criar DataFrame para os dados do gráfico
    df_member_count = pd.DataFrame(list(members_per_day.items()), columns=['Date', 'Members'])
    df_member_count = df_member_count.sort_values('Date')
    #st.dataframe(df_member_count)
            
#------------------------------------------------------------------#
#CRIANDO TABELAS CRUZADAS PATRIMONIO X RENDA
# Definindo a ordem das categorias para PATRIMONIO e RENDA MENSAL
categorias_patrimonio = [
    'Menos de R$5 mil', 'Entre R$5 mil e R$20 mil', 'Entre R$20 mil e R$100 mil',
    'Entre R$100 mil e R$250 mil', 'Entre R$250 mil e R$500 mil',
    'Entre R$500 mil e R$1 milhão', 'Acima de R$1 milhão'
]

categorias_renda = [
    'Até R$1.500', 'Entre R$1.500 e R$2.500', 'Entre R$2.500 e R$5.000',
    'Entre R$5.000 e R$10.000', 'Entre R$10.000 e R$20.000', 'Acima de R$20.000'
]

# Convertendo as colunas para categórico com a ordem especificada
df_PESQUISA['PATRIMONIO'] = pd.Categorical(df_PESQUISA['PATRIMONIO'], categories=categorias_patrimonio, ordered=True)
df_PESQUISA['RENDA MENSAL'] = pd.Categorical(df_PESQUISA['RENDA MENSAL'], categories=categorias_renda, ordered=True)

# Recriando a tabela cruzada com as colunas categóricas ordenadas
tabela_cruzada1_ordenada = pd.crosstab(df_PESQUISA['PATRIMONIO'], df_PESQUISA['RENDA MENSAL'])
       
if not df_VENDAS.empty:
    df_VENDAS['PATRIMONIO'] = pd.Categorical(df_VENDAS['PATRIMONIO'], categories=categorias_patrimonio, ordered=True)
    df_VENDAS['RENDA MENSAL'] = pd.Categorical(df_VENDAS['RENDA MENSAL'], categories=categorias_renda, ordered=True)
    tabela_cruzada1_vendas = pd.crosstab(df_VENDAS['PATRIMONIO'], df_VENDAS['RENDA MENSAL'])

    # Empilhando a tabela cruzada para transformar em um DataFrame com uma coluna para as combinações
    # e outra para os resultados (contagens)
    tabela_empilhada = tabela_cruzada1_ordenada.stack().reset_index()
    tabela_empilhada_vendas = tabela_cruzada1_vendas.stack().reset_index()

    # Renomeando as colunas do novo DataFrame para refletir o conteúdo
    tabela_empilhada.columns = ['PATRIMONIO', 'RENDA MENSAL', 'LEADS']
    tabela_empilhada_vendas.columns = ['PATRIMONIO', 'RENDA MENSAL', 'ALUNOS']

    # Criando uma nova coluna que combina 'PATRIMONIO' e 'RENDA MENSAL' em uma única string
    tabela_empilhada['FAIXA PATRIMONIO x RENDA MENSAL'] = tabela_empilhada['PATRIMONIO'].astype(str) + ' x ' + tabela_empilhada['RENDA MENSAL'].astype(str)
    tabela_empilhada_vendas['FAIXA PATRIMONIO x RENDA MENSAL'] = tabela_empilhada_vendas['PATRIMONIO'].astype(str) + ' x ' + tabela_empilhada['RENDA MENSAL'].astype(str)

    # Selecionando apenas as colunas de interesse para o novo DataFrame
    tabela_final = tabela_empilhada[['FAIXA PATRIMONIO x RENDA MENSAL', 'LEADS']]
    tabela_final_vendas = tabela_empilhada_vendas[['FAIXA PATRIMONIO x RENDA MENSAL', 'ALUNOS']]

    # Combinando as duas tabelas finais em uma única tabela
    tabela_combined = pd.merge(tabela_final, tabela_final_vendas, on='FAIXA PATRIMONIO x RENDA MENSAL', how='outer').fillna(0)

    # Adicionando a coluna de conversão
    tabela_combined['CONVERSÃO'] = (tabela_combined['ALUNOS'] / tabela_combined['LEADS'])
else:
    # Caso df_VENDAS esteja vazio, apenas exibir dados de captação (LEADS)
    tabela_empilhada = tabela_cruzada1_ordenada.stack().reset_index()
    tabela_empilhada.columns = ['PATRIMONIO', 'RENDA MENSAL', 'LEADS']
    tabela_empilhada['FAIXA PATRIMONIO x RENDA MENSAL'] = tabela_empilhada['PATRIMONIO'].astype(str) + ' x ' + tabela_empilhada['RENDA MENSAL'].astype(str)
    tabela_combined = tabela_empilhada[['FAIXA PATRIMONIO x RENDA MENSAL', 'LEADS']]

    # Adicionando a coluna de porcentagem de LEADS
    total_leads = tabela_combined['LEADS'].sum()
    tabela_combined['% DO TOTAL DE LEADS'] = (tabela_combined['LEADS'] / total_leads)

# Ordenando a tabela_combined pela ordem das categorias originais
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

# Exibindo a nova tabela combinada e os gráficos lado a lado
st.subheader("CONVERSÃO PATRIMONIO X RENDA")        

# Abas para navegação
tabs = st.tabs(["Dados Gerais do Lançamento" , "Análises de Patrimônio e Renda", "Análise de Percurso dos Leads"])


#--------------------------------------------------------------------------#
#CRIANDO DADOS PARA FAZER HEATMAP

# Definindo uma nova escala de cores que enfatiza variações
if not df_VENDAS.empty:
    new_colorscale = [
        [0.0, 'white'],      # Definindo a cor branca para valores NaN
        [0.0001, 'green'],   # Começando a escala de cores normal logo após branco
        [0.25, 'yellow'],
        [0.5, 'orange'],
        [0.75, 'red'],
        [1.0, 'purple']
    ]


    # Criando a crosstab para contagem de leads e soma de alunos
    contagem = pd.crosstab(tabela_combined['PATRIMONIO'], tabela_combined['RENDA MENSAL'], values=tabela_combined['LEADS'], aggfunc='sum').fillna(0)
    vendas = pd.crosstab(tabela_combined['PATRIMONIO'], tabela_combined['RENDA MENSAL'], values=tabela_combined['ALUNOS'], aggfunc='sum').fillna(0)

    # Calculando a taxa de conversão
    taxa_conversao = (vendas / contagem).fillna(0)

    # Calculando o valor máximo da taxa de conversão para ajustar a escala do heatmap
    max_taxa_conversao = taxa_conversao.max().max()
    max_valor = max_taxa_conversao + 0.05

    # Criando a crosstab com contagem de leads, número de vendas e taxa de conversão
    crosstab = contagem.astype(int).astype(str) + ' Leads<br>' + vendas.astype(int).astype(str) + ' Alunos<br>' + (taxa_conversao * 100).round(2).astype(str) + '% Conversão'

    # Criando o heatmap no Plotly
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
        colorbar=dict(
            title='Taxa de Conversão',
            tickcolor='white'
        )
    ))

    # Personalizando o layout do gráfico
    heatmap.update_layout(
        title='Mapa de Calor: Patrimônio vs Renda com Taxa de Conversão',
        xaxis=dict(title='Renda', showgrid=False),
        yaxis=dict(title='Patrimônio', showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo do gráfico transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fundo da figura transparente
        font=dict(color='white'),
        coloraxis_colorbar=dict(title='Taxa de Conversão', tickcolor='white'),
        autosize=False,
        width=1200,  # Ajusta a largura
        height=900  # Ajusta a altura
    )

#--------------------------------------------------------------------------#
#CRIANDO DADOS PARA FAZER SCATTERPLOT

# Transformando as tabelas em DataFrames planos para facilitar o uso no scatter plot
if not df_VENDAS.empty:
    contagem_flat = contagem.stack().reset_index()
    contagem_flat.columns = ['PATRIMONIO', 'RENDA MENSAL', 'LEADS']
    vendas_flat = vendas.stack().reset_index()
    vendas_flat.columns = ['PATRIMONIO', 'RENDA MENSAL', 'ALUNOS']
    taxa_conversao_flat = taxa_conversao.stack().reset_index()
    taxa_conversao_flat.columns = ['PATRIMONIO', 'RENDA MENSAL', 'TAXA_CONVERSAO']

    # Combinando as tabelas planas em um único DataFrame
    scatter_df = contagem_flat.merge(vendas_flat, on=['PATRIMONIO', 'RENDA MENSAL']).merge(taxa_conversao_flat, on=['PATRIMONIO', 'RENDA MENSAL'])

    # Ajustando o tamanho dos pontos para ser mais expressivo
    size_scale = 100
    scatter_df['size'] = np.log1p(scatter_df['LEADS']) * size_scale  # Usando transformação logarítmica para tornar tamanhos mais expressivos

    # Criando o scatter plot com Plotly
    scttplt = px.scatter(
        scatter_df,
        x='RENDA MENSAL',
        y='PATRIMONIO',
        size='size',
        color='TAXA_CONVERSAO',
        color_continuous_scale=new_colorscale,  # Escala de cores invertida
        hover_data={'LEADS': True, 'ALUNOS': True, 'TAXA_CONVERSAO': True, 'size': False},
        title='Scatterplot: Patrimônio vs Renda com Taxa de Conversão',
        size_max=30  # Este valor pode ser ajustado conforme necessário
    )

    # Customizando o layout do scatter plot
    scttplt.update_layout(
        xaxis=dict(title='Renda Mensal', showgrid=False),
        yaxis=dict(title='Patrimônio', showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo do gráfico transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fundo da figura transparente
        font=dict(color='white')
    )

with tabs[0]:
    st.subheader("DADOS GERAIS DO LANÇAMENTO")
    
    
    with st.container(border=True):
        st.markdown("### Dados Gerais")
        ctcol1, ctcol2, ctcol3, ctcol4, ctcol5 = st.columns([1,1,1,1,1])
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
            
    
   
    # Utilização da função para plotar o gráfico de leads por dia
    fig = plot_leads_per_day(df_CAPTURA, 'CAP DATA_CAPTURA')
    st.plotly_chart(fig)  

    if not df_GRUPOS.empty:
        # Utilização da função para plotar o gráfico de membros por dia
        fig = plot_group_members_per_day(df_member_count)
        st.plotly_chart(fig)
               
    
with tabs[1]:     

    if not df_VENDAS.empty:
        # Exibir o heatmap no Streamlit
        st.plotly_chart(heatmap)    
            # Exibir o scatterplot no Streamlit
        st.plotly_chart(scttplt)     
     
    # Aplicar estilo                               
    styled_df = tabela_combined.style.apply(color_rows, axis=1)                
    st.dataframe(styled_df)  
    
                                                        
    # Sessão para Conversão por Faixa de PATRIMONIO
    st.subheader("CONVERSÃO POR FAIXA DE PATRIMONIO")
    col3, col4 = st.columns([3, 2])
    with col3:
        if not df_VENDAS.empty:
            # Tabela de Conversão por Faixa de PATRIMONIO
            tabela_patrimonio = tabela_combined.groupby('PATRIMONIO').agg({
                'LEADS': 'sum',
                'ALUNOS': 'sum'
            }).reset_index()
            tabela_patrimonio['CONVERSÃO'] = (tabela_patrimonio['ALUNOS'] / tabela_patrimonio['LEADS']) * 100
            tabela_patrimonio['CONVERSÃO'] = tabela_patrimonio['CONVERSÃO'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_patrimonio)
        else:
            # Tabela de Percentual de LEADS por Faixa de PATRIMONIO
            tabela_patrimonio = tabela_combined.groupby('PATRIMONIO').agg({
                'LEADS': 'sum'
            }).reset_index()
            total_leads = tabela_patrimonio['LEADS'].sum()
            tabela_patrimonio['% DO TOTAL DE LEADS'] = (tabela_patrimonio['LEADS'] / total_leads) * 100
            tabela_patrimonio['% DO TOTAL DE LEADS'] = tabela_patrimonio['% DO TOTAL DE LEADS'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_patrimonio)

    with col4:
        if not df_VENDAS.empty:
            # Gráfico de Conversão por Faixa de PATRIMONIO
            fig_patrimonio, ax_patrimonio = plt.subplots()
            tabela_patrimonio['CONVERSÃO_NUM'] = tabela_patrimonio['CONVERSÃO'].str.rstrip('%').astype('float')
            ax_patrimonio.bar(tabela_patrimonio['PATRIMONIO'], tabela_patrimonio['CONVERSÃO_NUM'])
            ax_patrimonio.set_title('Conversão por Faixa de PATRIMONIO', color='#FFFFFF')
            ax_patrimonio.set_ylabel('Conversão (%)', color='#FFFFFF')
            ax_patrimonio.set_xticklabels(tabela_patrimonio['PATRIMONIO'], rotation=45, ha='right', color='#FFFFFF')
            ax_patrimonio.set_facecolor('none')  # Fundo do gráfico transparente
            fig_patrimonio.patch.set_facecolor('none')  # Fundo da figura transparente
            ax_patrimonio.spines['bottom'].set_color('#FFFFFF')
            ax_patrimonio.spines['top'].set_color('#FFFFFF')
            ax_patrimonio.spines['right'].set_color('#FFFFFF')
            ax_patrimonio.spines['left'].set_color('#FFFFFF')
            ax_patrimonio.tick_params(axis='x', colors='#FFFFFF')
            ax_patrimonio.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_patrimonio)
        else:
            # Gráfico de Percentual de LEADS por Faixa de PATRIMONIO
            fig_patrimonio, ax_patrimonio = plt.subplots()
            tabela_patrimonio['PERCENTUAL_NUM'] = tabela_patrimonio['% DO TOTAL DE LEADS'].str.rstrip('%').astype('float')
            ax_patrimonio.bar(tabela_patrimonio['PATRIMONIO'], tabela_patrimonio['PERCENTUAL_NUM'])
            ax_patrimonio.set_title('Percentual de LEADS por Faixa de PATRIMONIO', color='#FFFFFF')
            ax_patrimonio.set_ylabel('Percentual (%)', color='#FFFFFF')
            ax_patrimonio.set_xticklabels(tabela_patrimonio['PATRIMONIO'], rotation=45, ha='right', color='#FFFFFF')
            ax_patrimonio.set_facecolor('none')  # Fundo do gráfico transparente
            fig_patrimonio.patch.set_facecolor('none')  # Fundo da figura transparente
            ax_patrimonio.spines['bottom'].set_color('#FFFFFF')
            ax_patrimonio.spines['top'].set_color('#FFFFFF')
            ax_patrimonio.spines['right'].set_color('#FFFFFF')
            ax_patrimonio.spines['left'].set_color('#FFFFFF')
            ax_patrimonio.tick_params(axis='x', colors='#FFFFFF')
            ax_patrimonio.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_patrimonio)

    # Sessão para Conversão por Faixa de Renda
    st.subheader("CONVERSÃO POR FAIXA DE RENDA")
    col5, col6 = st.columns([3, 2])
    with col5:
        if not df_VENDAS.empty:
            # Tabela de Conversão por Faixa de Renda
            tabela_renda = tabela_combined.groupby('RENDA MENSAL').agg({
                'LEADS': 'sum',
                'ALUNOS': 'sum'
            }).reset_index()
            tabela_renda['CONVERSÃO'] = (tabela_renda['ALUNOS'] / tabela_renda['LEADS']) * 100
            tabela_renda['CONVERSÃO'] = tabela_renda['CONVERSÃO'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_renda)
        else:
            # Tabela de Percentual de LEADS por Faixa de Renda
            tabela_renda = tabela_combined.groupby('RENDA MENSAL').agg({
                'LEADS': 'sum'
            }).reset_index()
            total_leads = tabela_renda['LEADS'].sum()
            tabela_renda['% DO TOTAL DE LEADS'] = (tabela_renda['LEADS'] / total_leads) * 100
            tabela_renda['% DO TOTAL DE LEADS'] = tabela_renda['% DO TOTAL DE LEADS'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(tabela_renda)

    with col6:
        if not df_VENDAS.empty:
            # Gráfico de Conversão por Faixa de Renda
            fig_renda, ax_renda = plt.subplots()
            tabela_renda['CONVERSÃO_NUM'] = tabela_renda['CONVERSÃO'].str.rstrip('%').astype('float')
            ax_renda.bar(tabela_renda['RENDA MENSAL'], tabela_renda['CONVERSÃO_NUM'])
            ax_renda.set_title('Conversão por Faixa de Renda', color='#FFFFFF')
            ax_renda.set_ylabel('Conversão (%)', color='#FFFFFF')
            ax_renda.set_xticklabels(tabela_renda['RENDA MENSAL'], rotation=45, ha='right', color='#FFFFFF')
            ax_renda.set_facecolor('none')  # Fundo do gráfico transparente
            fig_renda.patch.set_facecolor('none')  # Fundo da figura transparente
            ax_renda.spines['bottom'].set_color('#FFFFFF')
            ax_renda.spines['top'].set_color('#FFFFFF')
            ax_renda.spines['right'].set_color('#FFFFFF')
            ax_renda.spines['left'].set_color('#FFFFFF')
            ax_renda.tick_params(axis='x', colors='#FFFFFF')
            ax_renda.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_renda)
        else:
            # Gráfico de Percentual de LEADS por Faixa de Renda
            fig_renda, ax_renda = plt.subplots()
            tabela_renda['PERCENTUAL_NUM'] = tabela_renda['% DO TOTAL DE LEADS'].str.rstrip('%').astype('float')
            ax_renda.bar(tabela_renda['RENDA MENSAL'], tabela_renda['PERCENTUAL_NUM'])
            ax_renda.set_title('Percentual de LEADS por Faixa de Renda', color='#FFFFFF')
            ax_renda.set_ylabel('Percentual (%)', color='#FFFFFF')
            ax_renda.set_xticklabels(tabela_renda['RENDA MENSAL'], rotation=45, ha='right', color='#FFFFFF')
            ax_renda.set_facecolor('none')  # Fundo do gráfico transparente
            fig_renda.patch.set_facecolor('none')  # Fundo da figura transparente
            ax_renda.spines['bottom'].set_color('#FFFFFF')
            ax_renda.spines['top'].set_color('#FFFFFF')
            ax_renda.spines['right'].set_color('#FFFFFF')
            ax_renda.spines['left'].set_color('#FFFFFF')
            ax_renda.tick_params(axis='x', colors='#FFFFFF')
            ax_renda.tick_params(axis='y', colors='#FFFFFF')
            st.pyplot(fig_renda)


            
    with tabs[2]:
        if not df_VENDAS.empty:
            # Criar a coluna 'PERCURSO' no DataFrame df_VENDAS sem alterar o original
            df_vendas_copy = df_VENDAS.copy()

            # Modificar o campo 'CAP UTM_SOURCE' se for igual a 'ig'
            df_vendas_copy['CAP UTM_SOURCE'] = df_vendas_copy.apply(
                lambda x: f"{x['CAP UTM_SOURCE']} {x['CAP UTM_MEDIUM']}" if x['CAP UTM_SOURCE'] == 'ig' else x['CAP UTM_SOURCE'],
                axis=1
            )

            # Concatenar os campos para formar o campo 'PERCURSO'
            df_vendas_copy['PERCURSO'] = df_vendas_copy['CAP UTM_SOURCE'].astype(str) + ' > ' + \
                                        df_vendas_copy['PM UTM_SOURCE'].astype(str) + ' > ' + \
                                        df_vendas_copy['UTM_SOURCE'].astype(str)

            # Contar os valores de 'PERCURSO' e ordenar do maior para o menor
            percurso_counts = df_vendas_copy['PERCURSO'].value_counts().reset_index()
            percurso_counts.columns = ['PERCURSO', 'COUNT']

            # Mostrar apenas os 20 primeiros resultados
            top_20_percurso = percurso_counts.head(20)

            # Exibir a análise de percurso de leads
            st.subheader("Análise de Percurso de Leads")
            col1, col2 = st.columns([3, 2])

            with col1:
                st.table(top_20_percurso)

            # Preparar dados para o gráfico de barras
            top_5_percurso = top_20_percurso.head(5).sort_values(by='COUNT', ascending=True)

            with col2:
                fig, ax = plt.subplots()
                
                # Gerar tons de azul para as barras
                colors = cm.Blues(np.linspace(0.4, 1, len(top_5_percurso)))

                ax.barh(top_5_percurso['PERCURSO'], top_5_percurso['COUNT'], color=colors)
                ax.set_xlabel('Count', color='#FFFFFF')
                ax.set_ylabel('PERCURSO', color='#FFFFFF')
                ax.set_title('Top 5 Percursos Mais Comuns', color='#FFFFFF')
                ax.set_facecolor('none')  # Fundo do gráfico transparente
                fig.patch.set_facecolor('none')  # Fundo da figura transparente
                ax.spines['bottom'].set_color('#FFFFFF')
                ax.spines['top'].set_color('#FFFFFF')
                ax.spines['right'].set_color('#FFFFFF')
                ax.spines['left'].set_color('#FFFFFF')
                ax.tick_params(axis='x', colors='#FFFFFF')
                ax.tick_params(axis='y', colors='#FFFFFF')
                plt.tight_layout()
                st.pyplot(fig)
            

        else:
            st.warning("Ainda não há vendas realizadas para executarmos a Análise de Percurso de Leads")