import requests
from PIL import Image, UnidentifiedImageError
import io
import streamlit as st
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from matplotlib import colormaps
import matplotlib.colors as mcolors
import time



def styled_bar_chart(x, y, title):
        fig, ax = plt.subplots()

        # Definindo cores usando colormaps de tons de azul
        cmap = colormaps['Blues']
        norm = mcolors.Normalize(vmin=0, vmax=len(x)-1)
        colors = [cmap(norm(i)) for i in range(len(x))]

        ax.bar(x, y, color=colors)
        ax.set_facecolor('none')  # Fundo do gráfico transparente
        fig.patch.set_facecolor('none')  # Fundo da figura transparente
        ax.spines['bottom'].set_color('#FFFFFF')
        ax.spines['top'].set_color('#FFFFFF')
        ax.spines['right'].set_color('#FFFFFF')
        ax.spines['left'].set_color('#FFFFFF')
        ax.tick_params(axis='x', colors='#FFFFFF', rotation=45)
        ax.tick_params(axis='y', colors='#FFFFFF')
        ax.set_title(title, color='#FFFFFF')
        ax.set_ylabel('Conversão', color='#FFFFFF')
        ax.set_xlabel(' ', color='#FFFFFF')
        plt.setp(ax.get_xticklabels(), color="#FFFFFF", rotation=45, ha='right')
        plt.setp(ax.get_yticklabels(), color="#FFFFFF")
        
        return fig


# Função para transformar link de compartilhamento do Google Drive em link direto para imagem
def transform_drive_link(link):
    if "drive.google.com" in link and "file/d/" in link:
        file_id = link.split("file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    elif "drive.google.com" in link and "id=" in link:
        file_id = link.split("id=")[1].split("&")[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    else:
        return link

# Função para baixar a imagem a partir de um link
def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        return None

df_METAADS = st.session_state.df_METAADS.copy()
df_METAADS = df_METAADS.astype(str)

colunas_numericas = [
    'CPM', 'VALOR USADO', 'LEADS', 'CPL', 'CTR', 'CONNECT RATE',
    'CONVERSAO PAG', 'IMPRESSOES', 'ALCANCE', 'FREQUENCIA',
    'CLICKS', 'CLICKS NO LINK', 'PAGEVIEWS', 'LP CTR', 'PERFIL CTR',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
    '13', '14', '15-20', '20-25', '25-30', '30-40', '40-50', '50-60', '60+'
]

for coluna in colunas_numericas:
    df_METAADS[coluna] = pd.to_numeric(df_METAADS[coluna], errors='coerce')

df_SUBIDOS = st.session_state.df_SUBIDOS.copy()
df_PESQUISA = st.session_state.df_PESQUISA.copy()

df_PESQUISA['UTM_TERM'] = df_PESQUISA['UTM_TERM'].replace('+', ' ')
df_PESQUISA = df_PESQUISA.astype(str)

ticket = 1500 * 0.7
columns = [
    'ANÚNCIO', 'TOTAL DE LEADS', 'TOTAL DE PESQUISA',
    'CUSTO POR LEAD', 'PREÇO MÁXIMO', 'DIFERENÇA', 'MARGEM', 'VALOR USADO',
    'CPM', 'CTR', 'CONNECT RATE', 'CONVERSAO PAG', 'Acima de R$1 milhão',
    'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
    'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil',
    'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil', 'TAXA DE RESPOSTA'
]
df_PORANUNCIO = pd.DataFrame(columns=columns)
taxas_conversao_patrimonio = {
    'Acima de R$1 milhão': 0.0489,
    'Entre R$500 mil e R$1 milhão': 0.0442,
    'Entre R$250 mil e R$500 mil': 0.0400,
    'Entre R$100 mil e R$250 mil': 0.0382,
    'Entre R$20 mil e R$100 mil': 0.0203,
    'Entre R$5 mil e R$20 mil': 0.0142,
    'Menos de R$5 mil': 0.0067
}
anuncios_unicos = df_METAADS['ANUNCIO: NOME'].unique()
df_PORANUNCIO['ANÚNCIO'] = pd.Series(anuncios_unicos)
df_PORANUNCIO['TOTAL DE LEADS'] = df_PORANUNCIO['ANÚNCIO'].apply(
    lambda anuncio: df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio]['LEADS'].sum()
)
df_PORANUNCIO['TOTAL DE PESQUISA'] = df_PORANUNCIO['ANÚNCIO'].apply(
    lambda anuncio: df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0]
)
faixas_patrimonio = [
    'Acima de R$1 milhão', 'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
    'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil', 'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil'
]
for faixa in faixas_patrimonio:
    df_PORANUNCIO[faixa] = df_PORANUNCIO['ANÚNCIO'].apply(
        lambda anuncio: (
            df_PESQUISA[(df_PESQUISA['UTM_TERM'] == anuncio) & 
                        (df_PESQUISA['PATRIMONIO'] == faixa)].shape[0] / 
            df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0]
        ) if df_PESQUISA[df_PESQUISA['UTM_TERM'] == anuncio].shape[0] != 0 else 0
    )
   
df_PORANUNCIO['PREÇO MÁXIMO'] = ticket * (
    taxas_conversao_patrimonio['Acima de R$1 milhão'] * df_PORANUNCIO['Acima de R$1 milhão'] +
    taxas_conversao_patrimonio['Entre R$500 mil e R$1 milhão'] * df_PORANUNCIO['Entre R$500 mil e R$1 milhão'] +
    taxas_conversao_patrimonio['Entre R$250 mil e R$500 mil'] * df_PORANUNCIO['Entre R$250 mil e R$500 mil'] +
    taxas_conversao_patrimonio['Entre R$100 mil e R$250 mil'] * df_PORANUNCIO['Entre R$100 mil e R$250 mil'] +
    taxas_conversao_patrimonio['Entre R$20 mil e R$100 mil'] * df_PORANUNCIO['Entre R$20 mil e R$100 mil'] +
    taxas_conversao_patrimonio['Entre R$5 mil e R$20 mil'] * df_PORANUNCIO['Entre R$5 mil e R$20 mil'] +
    taxas_conversao_patrimonio['Menos de R$5 mil'] * df_PORANUNCIO['Menos de R$5 mil']
)
df_PORANUNCIO['VALOR USADO'] = df_PORANUNCIO['ANÚNCIO'].apply(
    lambda anuncio: df_METAADS[df_METAADS['ANUNCIO: NOME'] == anuncio]['VALOR USADO'].sum()
)
df_PORANUNCIO['CUSTO POR LEAD'] = df_PORANUNCIO['VALOR USADO'] / df_PORANUNCIO['TOTAL DE LEADS']
df_PORANUNCIO['DIFERENÇA'] = df_PORANUNCIO['PREÇO MÁXIMO'] - df_PORANUNCIO['CUSTO POR LEAD']
df_PORANUNCIO['MARGEM'] = df_PORANUNCIO['DIFERENÇA'] / df_PORANUNCIO['PREÇO MÁXIMO']
df_PORANUNCIO['CPM'] = df_PORANUNCIO['ANÚNCIO'].apply(
    lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CPM'].mean()
    if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CPM'].empty else "Sem conversões"
)
df_PORANUNCIO['CTR'] = df_PORANUNCIO['ANÚNCIO'].apply(
    lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS'].sum() /
    df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'IMPRESSOES'].sum()
    if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS'].empty else "Sem conversões"
)
df_PORANUNCIO['CONNECT RATE'] = df_PORANUNCIO['ANÚNCIO'].apply(
    lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].sum() /
    df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'CLICKS NO LINK'].sum()
    if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].empty else "Sem conversões"
)
df_PORANUNCIO['TAXA DE RESPOSTA'] = df_PORANUNCIO.apply(
    lambda row: row['TOTAL DE PESQUISA'] / row['TOTAL DE LEADS'] if row['TOTAL DE LEADS'] != 0 else "Sem respostas", axis=1
)
df_PORANUNCIO['CONVERSAO PAG'] = df_PORANUNCIO['ANÚNCIO'].apply(
    lambda anuncio: df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'LEADS'].sum() /
    df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].sum()
    if not df_METAADS.loc[df_METAADS['ANUNCIO: NOME'].str.contains(anuncio, regex=False), 'PAGEVIEWS'].empty else "Sem conversões"
)



 # Adicionar slider para selecionar o valor mínimo de 'VALOR USADO'
min_valor_usado = st.slider("Selecione o valor mínimo de 'VALOR USADO'", 0, 1000, 250)

# Filtrar DataFrame pelo valor do slider       
df_PORANUNCIO = df_PORANUNCIO[df_PORANUNCIO['VALOR USADO'] >= min_valor_usado]
with st.expander('dataframes'):
    st.dataframe(df_PORANUNCIO)
    st.dataframe(df_METAADS)

# Criar o DataFrame df_STATUS
df_STATUS = pd.DataFrame({
    'ID UNICO': df_METAADS['ANUNCIO: NOME'] + '&' + df_METAADS['CONJUNTO: NOME'],
    'STATUS': ['ATIVO'] * len(df_METAADS)  # Inicialmente todos os status são 'ATIVO'
})

#OUTRO CÓDIGO QUE DEVERIA ESTAR PEGANDO DATAFRAMES DIFERENTES PARA MOSTRAR EM ABAS DIFERENTES

df_METAVIDS = df_METAADS.copy()
# Converter colunas de retenção para numéricas
colunas_retencao = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15-20', '20-25', '25-30', '30-40', '40-50', '50-60', '60+']
# Filtrar anúncios de vídeo (não vazios nas colunas de tempo)
df_videos = df_METAVIDS.dropna(subset=colunas_retencao, how='all')

# Agrupar por 'ANUNCIO: NOME' e calcular a média das retenções e somar 'VALOR USADO'
df_agrupado = df_videos.groupby('ANUNCIO: NOME').agg(
    {**{col: 'mean' for col in colunas_retencao}, 'VALOR USADO': 'sum'}
).reset_index()
 
tabs = st.tabs(["Top Anúncios", "Por Anuncio - Imagem", "Por Anuncio - Video", "hook analyzer"])

with tabs[0]:
    st.header('Análise de Anúncios')
         
    colunas_analise = ['MARGEM', 'VALOR USADO', 'CTR', 'CONVERSAO PAG']
    df_PORANUNCIO_COPY = df_PORANUNCIO.copy()
    for coluna_a in colunas_analise:
        df_PORANUNCIO_COPY[coluna_a] = pd.to_numeric(df_PORANUNCIO_COPY[coluna_a], errors='coerce')
    for coluna_a in colunas_analise:
        df_filtrado = df_PORANUNCIO_COPY[
            (df_PORANUNCIO_COPY[coluna_a].notnull()) &
            (df_PORANUNCIO_COPY[coluna_a] != 0) &
            (df_PORANUNCIO_COPY[coluna_a] != "Sem respostas") &
            (df_PORANUNCIO_COPY[coluna_a] != "")
        ]
        top_5 = df_filtrado.nlargest(5, coluna_a)
        bottom_5 = df_filtrado.nsmallest(5, coluna_a)
        st.subheader(f'Análise da Coluna: {coluna_a}')
        col1, col2 = st.columns(2)
        with col1:
            if not top_5.empty:
                fig_top_5 = styled_bar_chart(top_5['ANÚNCIO'], top_5[coluna_a], f'Top 5 Anúncios - {coluna_a}')
                st.pyplot(fig_top_5)
            else:
                st.write(f"Não há dados suficientes para os Top 5 Anúncios - {coluna_a}")
        with col2:
            if not bottom_5.empty and len(bottom_5) >= 5:
                fig_bottom_5 = styled_bar_chart(bottom_5['ANÚNCIO'], bottom_5[coluna_a], f'Bottom 5 Anúncios - {coluna_a}')
                st.pyplot(fig_bottom_5)
            else:
                st.write(f"Não há dados suficientes para os Bottom 5 Anúncios - {coluna_a}")

with tabs[1]:
    st.header('Detalhes do Anúncio')

    selected_anuncio = st.selectbox('Selecione o Anúncio', df_PORANUNCIO['ANÚNCIO'].unique())
    if selected_anuncio:
        anuncio_data = df_PORANUNCIO[df_PORANUNCIO['ANÚNCIO'] == selected_anuncio].iloc[0]

        # Encontrar o link da imagem correspondente no df_SUBIDOS
        drive_link = df_SUBIDOS.loc[df_SUBIDOS['ANUNCIO'] == selected_anuncio, 'LINK DO DRIVE'].values[0]
        image_link = transform_drive_link(drive_link)

        st.write(f"Anúncio: {selected_anuncio}")
        if "ADNV" in selected_anuncio:
            st.write(f"Link do Video: [Clique aqui]({image_link})")
        else:
            st.write(f"Link da Imagem: [Clique aqui]({image_link})")    

        try:
            image = download_image(image_link)
            if image:
                st.image(image, caption=selected_anuncio, width=300)
        except UnidentifiedImageError:
            st.write("Clique no link para assistir o anúncio de vídeo")

        st.subheader(f"Detalhes do Anúncio: {selected_anuncio}")
        st.markdown(f"""
        <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="color: #ffffff;">Informações Gerais</h3>
            <p style="color: #ffffff;"><strong>Total de Leads:</strong> {anuncio_data['TOTAL DE LEADS']}</p>
            <p style="color: #ffffff;"><strong>Total de Pesquisa:</strong> {anuncio_data['TOTAL DE PESQUISA']}</p>
            <p style="color: #ffffff;"><strong>Custo por Lead:</strong> {anuncio_data['CUSTO POR LEAD']:.2f}</p>
            <p style="color: #ffffff;"><strong>Preço Máximo:</strong> {anuncio_data['PREÇO MÁXIMO']:.2f}</p>
            <p style="color: #ffffff;"><strong>Diferença:</strong> {anuncio_data['DIFERENÇA']:.2f}</p>
            <p style="color: #ffffff;"><strong>Margem:</strong> {anuncio_data['MARGEM']:.2%}</p>
            <p style="color: #ffffff;"><strong>Valor Usado:</strong> {anuncio_data['VALOR USADO']:.2f}</p>
            <p style="color: #ffffff;"><strong>CPM:</strong> {anuncio_data['CPM']:.2f}</p>
            <p style="color: #ffffff;"><strong>CTR:</strong> {anuncio_data['CTR']:.2%}</p>
            <p style="color: #ffffff;"><strong>Connect Rate:</strong> {anuncio_data['CONNECT RATE']:.2%}</p>
            <p style="color: #ffffff;"><strong>Conversão da Página:</strong> {anuncio_data['CONVERSAO PAG']:.2%}</p>
            <p style="color: #ffffff;"><strong>Taxa de Resposta:</strong> {anuncio_data['TAXA DE RESPOSTA']:.2%}</p>
        </div>
        """, unsafe_allow_html=True)

        def styled_bar_chart_horizontal(labels, sizes, title):
            fig, ax = plt.subplots()

            # Definindo cores usando colormaps e invertendo a ordem
            cmap = colormaps['RdYlGn']
            norm = mcolors.Normalize(vmin=0, vmax=len(labels)-1)
            colors = [cmap(norm(i)) for i in reversed(range(len(labels)))]

            ax.barh(labels, sizes, color=colors)
            ax.set_facecolor('none')  # Fundo do gráfico transparente
            fig.patch.set_facecolor('none')  # Fundo da figura transparente
            ax.spines['bottom'].set_color('#FFFFFF')
            ax.spines['top'].set_color('#FFFFFF')
            ax.spines['right'].set_color('#FFFFFF')
            ax.spines['left'].set_color('#FFFFFF')
            ax.tick_params(axis='x', colors='#FFFFFF')
            ax.tick_params(axis='y', colors='#FFFFFF')
            ax.set_title(title, color='#FFFFFF')
            ax.set_xlabel('Porcentagem', color='#FFFFFF')
            plt.setp(ax.get_xticklabels(), color="#FFFFFF")
            plt.setp(ax.get_yticklabels(), color="#FFFFFF")
            
            return fig

        def styled_bar_chart(x, y, title):
            fig, ax = plt.subplots()

            # Definindo cores usando colormaps de tons de azul
            cmap = colormaps['Blues']
            norm = mcolors.Normalize(vmin=0, vmax=len(x)-1)
            colors = [cmap(norm(i)) for i in range(len(x))]

            ax.bar(x, y, color=colors)
            ax.set_facecolor('none')  # Fundo do gráfico transparente
            fig.patch.set_facecolor('none')  # Fundo da figura transparente
            ax.spines['bottom'].set_color('#FFFFFF')
            ax.spines['top'].set_color('#FFFFFF')
            ax.spines['right'].set_color('#FFFFFF')
            ax.spines['left'].set_color('#FFFFFF')
            ax.tick_params(axis='x', colors='#FFFFFF', rotation=45)
            ax.tick_params(axis='y', colors='#FFFFFF')
            ax.set_title(title, color='#FFFFFF')
            ax.set_ylabel('Quantidade', color='#FFFFFF')
            ax.set_xlabel(' ', color='#FFFFFF')
            plt.setp(ax.get_xticklabels(), color="#FFFFFF", rotation=45, ha='right')
            plt.setp(ax.get_yticklabels(), color="#FFFFFF")
            
            return fig

        patrimonio_labels = [
            'Acima de R$1 milhão', 'Entre R$500 mil e R$1 milhão', 'Entre R$250 mil e R$500 mil',
            'Entre R$100 mil e R$250 mil', 'Entre R$20 mil e R$100 mil', 'Entre R$5 mil e R$20 mil', 'Menos de R$5 mil'
        ]
        patrimonio_sizes = [
            anuncio_data['Acima de R$1 milhão'], anuncio_data['Entre R$500 mil e R$1 milhão'],
            anuncio_data['Entre R$250 mil e R$500 mil'], anuncio_data['Entre R$100 mil e R$250 mil'],
            anuncio_data['Entre R$20 mil e R$100 mil'], anuncio_data['Entre R$5 mil e R$20 mil'],
            anuncio_data['Menos de R$5 mil']
        ]
        fig_patrimonio = styled_bar_chart_horizontal(patrimonio_labels, patrimonio_sizes, 'Distribuição de Patrimônio')

        metrics_labels = ['MARGEM', 'CTR', 'CONVERSAO PAG']
        metrics_values = [anuncio_data['MARGEM'], anuncio_data['CTR'], anuncio_data['CONVERSAO PAG']]
        fig_metrics = styled_bar_chart(metrics_labels, metrics_values, 'Métricas Principais')

        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(fig_patrimonio)
        with col2:
            st.pyplot(fig_metrics)

with tabs[2]:
    if 'df_videos' in locals():        
        # Carregar os dados da aba 'ANUNCIOS SUBIDOS'
        df_SUBIDOS = st.session_state.df_SUBIDOS.copy()

        # Selectbox para selecionar anúncios
        st.write("Selecione até 3 anúncios para comparar:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            anuncio1 = st.selectbox("Anúncio 1", df_videos['ANUNCIO: NOME'].unique(), key='anuncio1')
            link1 = df_SUBIDOS.loc[df_SUBIDOS['ANUNCIO'] == anuncio1, 'LINK DO DRIVE'].values[0]
            st.write(f"Link: [{link1}]({link1})")

        with col2:
            anuncio2 = st.selectbox("Anúncio 2", [None] + list(df_videos['ANUNCIO: NOME'].unique()), key='anuncio2')
            if anuncio2:
                link2 = df_SUBIDOS.loc[df_SUBIDOS['ANUNCIO'] == anuncio2, 'LINK DO DRIVE'].values[0]
                st.write(f"Link: [{link2}]({link2})")
                
        with col3:
            anuncio3 = st.selectbox("Anúncio 3", [None] + list(df_videos['ANUNCIO: NOME'].unique()), key='anuncio3')
            if anuncio3:
                link3 = df_SUBIDOS.loc[df_SUBIDOS['ANUNCIO'] == anuncio3, 'LINK DO DRIVE'].values[0]
                st.write(f"Link: [{link3}]({link3})")
                
        if st.button("Gerar Análise"):
            # Criar um novo DataFrame com uma linha chamada 'média'
            df_media = df_videos[colunas_retencao].mean().to_frame().T
            df_media.index = ['média']
            
            # Obter dados dos anúncios selecionados
            df_selecionados = df_videos[df_videos['ANUNCIO: NOME'].isin([anuncio1, anuncio2, anuncio3])]

            # Preparar o gráfico de linhas estilizado
            fig, ax = plt.subplots(figsize=(12, 7))  # Aumentar levemente o tamanho da figura
            
            # Plotar os anúncios selecionados
            cores = ['#FFA500', '#32CD32', '#1E90FF']  # Cores levemente mais claras: laranja, verde e azul
            for i, anuncio in enumerate([anuncio1, anuncio2, anuncio3]):
                if anuncio:
                    ax.plot(colunas_retencao, df_selecionados[df_selecionados['ANUNCIO: NOME'] == anuncio].iloc[0, 1:-1], label=anuncio, color=cores[i])
            
            # Plotar a linha da média
            ax.plot(colunas_retencao, df_media.iloc[0], label='média', color='#FF6347')  # Vermelho claro
            
            # Configurações do gráfico
            ax.set_xlabel('Tempo de Retenção', color='white')
            ax.set_ylabel('Percentual de Retenção', color='white')
            ax.set_title('Comparação de Retenção dos Anúncios', color='white')
            ax.legend()
            ax.grid(True, color='#666666', linestyle='--', linewidth=0.5)
            ax.patch.set_alpha(0)  # Fundo do gráfico transparente
            fig.patch.set_alpha(0)  # Fundo da figura transparente
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white') 
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.tick_params(axis='x', colors='white', rotation=45)  # Rotacionar labels de tempo
            ax.tick_params(axis='y', colors='white')

            # Mostrar o gráfico
            st.pyplot(fig)

with tabs[3]:
    st.write("Análise de Hook de Vídeos")

    # Garantir que os dados estejam carregados na aba "Dados"
    if 'df_videos' in locals() and df_videos is not None:
        # Perguntar em qual segundo avaliar a retenção
        segundo = st.selectbox('Em qual segundo deseja avaliar a retenção?', list(range(1, 11)), index=4)
        
        col1, col2 = st.columns(2)
        with col1:
            top_or_bottom = st.selectbox('Selecionar', ['Melhores', 'Piores'])
        with col2:
            top_n = st.selectbox('Quantidade', list(range(3, 11)), index=2)

        # Mostrar o dataframe de acordo com a seleção
        if st.button("Mostrar Anúncios"):
            col_retenção = str(segundo)
            if top_or_bottom == 'Melhores':
                top_anuncios = df_videos.nlargest(top_n, col_retenção)
            else:
                top_anuncios = df_videos.nsmallest(top_n, col_retenção)
            
            # Mostrar o dataframe dos top anúncios
            st.write(f"Top {top_n} anúncios de acordo com a retenção no segundo {segundo}:")
            st.dataframe(top_anuncios)