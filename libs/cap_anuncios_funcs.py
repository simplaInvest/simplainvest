import streamlit as st
import pandas as pd
import plotly.express as px


#------------------------------------------------------------
# Funções para renderizar cada análise
#------------------------------------------------------------

def mostrar_analise_captacao(DF_CENTRAL_CAPTURA, DF_CENTRAL_PREMATRICULA, DF_CENTRAL_VENDAS, PRODUTO):
    st.subheader("🔍 Análise de Captação")
    cols_anun = st.columns(2)

    with cols_anun[0]:
        # ➤ 0. Filtrar apenas anúncios pagos
        df_captura_filtrado = DF_CENTRAL_CAPTURA[DF_CENTRAL_CAPTURA['UTM_MEDIUM'] == 'pago'].copy()

        # 1. Métricas da Captação
        df_captura = df_captura_filtrado.groupby('UTM_TERM').agg(CAPTURA_Leads=('EMAIL', 'nunique'))
        total_captura = df_captura_filtrado['EMAIL'].nunique()
        df_captura['CAPTURA_Relativo'] = round(df_captura['CAPTURA_Leads'] / total_captura * 100, 2)

        # 2. Métricas da Pré-Matrícula (somente se PRODUTO == 'EI')
        if PRODUTO == 'EI':
            df_pm_merge = pd.merge(
                df_captura_filtrado[['EMAIL', 'UTM_TERM']],
                DF_CENTRAL_PREMATRICULA[['EMAIL']],
                on='EMAIL',
                how='inner'
            )
            df_pm = df_pm_merge.groupby('UTM_TERM').agg(PM_Leads=('EMAIL', 'nunique'))

            df_final = df_captura.join(df_pm, how='left')
            df_final['PM_Leads'] = df_final['PM_Leads'].fillna(0)
            df_final['PM_Conversao'] = round((df_final['PM_Leads'] / df_final['CAPTURA_Leads']) * 100, 2)
        else:
            df_final = df_captura.copy()

        # 3. Métricas de Vendas
        df_vendas_merge = pd.merge(
            df_captura_filtrado[['EMAIL', 'UTM_TERM']],
            DF_CENTRAL_VENDAS[['EMAIL']],
            on='EMAIL',
            how='inner'
        )
        df_vendas = df_vendas_merge.groupby('UTM_TERM').agg(VENDAS_Alunos=('EMAIL', 'nunique'))

        df_final = df_final.join(df_vendas, how='left')
        df_final['VENDAS_Alunos'] = df_final['VENDAS_Alunos'].fillna(0)
        df_final['VENDAS_Conversao'] = round((df_final['VENDAS_Alunos'] / df_final['CAPTURA_Leads']) * 100, 2)

        # Reordenar colunas
        colunas = ['CAPTURA_Relativo', 'CAPTURA_Leads']
        if PRODUTO == 'EI':
            colunas += ['PM_Leads', 'PM_Conversao']
        colunas += ['VENDAS_Alunos', 'VENDAS_Conversao']

        df_final = df_final[colunas]

        # Definir index
        df_final.index.name = 'UTM_TERM'

        cols_filtro = st.columns([1, 1])
        with cols_filtro[0]:
            # Threshold
            threshold = st.number_input("Digite um número:", min_value=0, max_value=1000, value=100 if PRODUTO == 'EI' else 5)
            df_final = df_final[df_final["CAPTURA_Leads"] >= threshold]

        with cols_filtro[1]:
            # Filtrar por UTM_TERM
            selected_terms = st.multiselect("Filtrar anúncios específicos:", df_final.index.tolist())
            if selected_terms:
                df_final = df_final.loc[selected_terms]

        st.dataframe(df_final)

    with cols_anun[1]:
        if PRODUTO == 'EI':
            options = ("Conversão Prematrícula", "Conversão Vendas")
            conversao_tipo = st.radio("Selecione a métrica de conversão", options)
            coluna_metrica = "PM_Conversao" if conversao_tipo == "Conversão Prematrícula" else "VENDAS_Conversao"
        else:
            coluna_metrica = "VENDAS_Conversao"
            conversao_tipo = "Conversão Vendas"

        # Top 10
        df_top = df_final.sort_values(coluna_metrica, ascending=False).head(10)

        fig = px.bar(
            df_top,
            x=coluna_metrica,
            y=df_top.index,
            orientation='h',
            text=df_top[coluna_metrica],
            title=f"Top 10 Anúncios com Maior {conversao_tipo}"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            xaxis_title='Taxa de Conversão',
            yaxis_title='Anúncio (UTM_TERM)',
            margin=dict(l=100, r=20, t=60, b=50)
        )

        st.plotly_chart(fig, use_container_width=True)

    # Calcular média de conversão de vendas
    media_conversao = df_final['VENDAS_Conversao'].mean()

    # Resetar index para manipular UTM_TERM como coluna
    df_base = df_final.reset_index()

    # Marcar destaques com base na conversão
    df_base['DESTAQUE'] = df_base['VENDAS_Conversao'].apply(
        lambda x: 'Alta' if x > media_conversao * 1.5 else ('Baixa' if x < media_conversao * 0.5 else None)
    )

    # DataFrame dos campeões
    df_campeoes = df_base[df_base['DESTAQUE'] == 'Alta'].copy()
    df_campeoes['🏆 Rank'] = df_campeoes['VENDAS_Conversao'].rank(method='min', ascending=False).astype(int)
    df_campeoes = df_campeoes.sort_values('VENDAS_Conversao', ascending=False)

    # DataFrame dos perdedores
    df_perdedores = df_base[df_base['DESTAQUE'] == 'Baixa'].copy()
    df_perdedores['📉 Rank'] = df_perdedores['VENDAS_Conversao'].rank(method='min', ascending=False).astype(int)
    df_perdedores = df_perdedores.sort_values('VENDAS_Conversao', ascending=False)

    # Selecionar apenas colunas de interesse para visualização
    colunas_visual = ['UTM_TERM', 'CAPTURA_Leads', 'VENDAS_Alunos', 'VENDAS_Conversao']

    # Exibir os dois dataframes lado a lado
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔝 Anúncios Campeões")
        if not df_campeoes.empty:
            st.dataframe(
                df_campeoes[colunas_visual].rename(columns={
                    'UTM_TERM': 'Anúncio',
                    'CAPTURA_Leads': 'Leads Captados',
                    'VENDAS_Alunos': 'Vendas',
                    'VENDAS_Conversao': 'Conversão (%)'
                }).set_index(df_campeoes['🏆 Rank']),
                use_container_width=True
            )
        else:
            st.write("Nenhum anúncio com performance muito acima da média.")

    with col2:
        st.subheader("⚠️ Anúncios com Baixa Performance")
        if not df_perdedores.empty:
            st.dataframe(
                df_perdedores[colunas_visual].rename(columns={
                    'UTM_TERM': 'Anúncio',
                    'CAPTURA_Leads': 'Leads Captados',
                    'VENDAS_Alunos': 'Vendas',
                    'VENDAS_Conversao': 'Conversão (%)'
                }).set_index(df_perdedores['📉 Rank']),
                use_container_width=True
            )
        else:
            st.write("Nenhum anúncio com performance muito abaixo da média.")


def mostrar_analise_pm(DF_CENTRAL_PREMATRICULA, DF_CENTRAL_VENDAS):
    st.subheader("🧪 Análise de Pré-Matrícula")
    # 0. Filtrar apenas anúncios pagos
    DF_PM_FILTRADO = DF_CENTRAL_PREMATRICULA[DF_CENTRAL_PREMATRICULA['UTM_MEDIUM'] == 'pago'].copy()

    # 1. Métricas da Pré-Matrícula:
    df_pm_stage = DF_PM_FILTRADO.groupby('UTM_TERM').agg(PM_Leads=('EMAIL', 'nunique'))
    total_pm = DF_PM_FILTRADO['EMAIL'].nunique()
    df_pm_stage['PM_Relativo'] = round(df_pm_stage['PM_Leads'] / total_pm * 100, 2)

    # 2. Métricas de Vendas:
    df_vendas_from_pm = pd.merge(
        DF_PM_FILTRADO[['EMAIL', 'UTM_TERM']],
        DF_CENTRAL_VENDAS[['EMAIL']],
        on='EMAIL',
        how='inner'
    )
    df_vendas_grouped = df_vendas_from_pm.groupby('UTM_TERM').agg(VENDAS_Alunos=('EMAIL', 'nunique'))

    # 3. Junção e cálculo de conversão:
    df_pm_final = df_pm_stage.join(df_vendas_grouped, how='left')
    df_pm_final['VENDAS_Alunos'] = df_pm_final['VENDAS_Alunos'].fillna(0)
    df_pm_final['VENDAS_Conversao'] = round((df_pm_final['VENDAS_Alunos'] / df_pm_final['PM_Leads']) * 100, 2)

    # Reorganizar colunas e definir índice
    df_pm_final = df_pm_final[['PM_Leads', 'VENDAS_Alunos', 'VENDAS_Conversao']]
    df_pm_final.index.name = 'UTM_TERM'

    # Filtro por mínimo de PMs
    coll = st.columns([1, 1])

    with coll[0]:
        threshold_pm = st.number_input("Digite um número mínimo de pré-matrículas:", min_value=0, max_value=1000, value=0)
        df_pm_final = df_pm_final[df_pm_final["PM_Leads"] >= threshold_pm]

        st.dataframe(df_pm_final)

    with coll[1]:
        # Gráfico de barras invertido (top 10 conversão)
        df_top_pm = df_pm_final.sort_values("VENDAS_Conversao", ascending=False).head(10)
        fig_pm = px.bar(
            df_top_pm,
            x='VENDAS_Conversao',
            y=df_top_pm.index,
            orientation='h',
            text='VENDAS_Conversao',
            title="Top 10 Anúncios com Maior Conversão de Vendas (PM)"
        )
        fig_pm.update_traces(textposition='outside')
        fig_pm.update_layout(
            yaxis=dict(autorange="reversed"),
            xaxis_title='Taxa de Conversão',
            yaxis_title='Anúncio (UTM_TERM)',
            margin=dict(l=100, r=20, t=60, b=50)
        )
        st.plotly_chart(fig_pm, use_container_width=True)

    #------------------------------------------------------------
    #      Campeões e Perdedores da Pré-Matrícula
    #------------------------------------------------------------

    # Resetar index para manipular UTM_TERM como coluna
    df_base_pm = df_pm_final.reset_index()

    # Calcular média e definir DESTAQUE
    media_conversao_pm = df_base_pm['VENDAS_Conversao'].mean()
    df_base_pm['DESTAQUE'] = df_base_pm['VENDAS_Conversao'].apply(
        lambda x: 'Alta' if x > media_conversao_pm * 1.5 else ('Baixa' if x < media_conversao_pm * 0.5 else None)
    )

    # Campeões
    df_campeoes_pm = df_base_pm[df_base_pm['DESTAQUE'] == 'Alta'].copy()
    df_campeoes_pm['🏆 Rank'] = df_campeoes_pm['VENDAS_Conversao'].rank(method='min', ascending=False).astype(int)
    df_campeoes_pm = df_campeoes_pm.sort_values('VENDAS_Conversao', ascending=False)

    # Perdedores
    df_perdedores_pm = df_base_pm[df_base_pm['DESTAQUE'] == 'Baixa'].copy()
    df_perdedores_pm['📉 Rank'] = df_perdedores_pm['VENDAS_Conversao'].rank(method='min', ascending=False).astype(int)
    df_perdedores_pm = df_perdedores_pm.sort_values('VENDAS_Conversao', ascending=False)

    # Colunas a exibir
    colunas_exibir = ['UTM_TERM', 'PM_Leads', 'VENDAS_Alunos', 'VENDAS_Conversao']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔝 Anúncios Campeões (PM)")
        if not df_campeoes_pm.empty:
            st.dataframe(
                df_campeoes_pm[colunas_exibir].rename(columns={
                    'UTM_TERM': 'Anúncio',
                    'PM_Leads': 'Pré-Matrículas',
                    'VENDAS_Alunos': 'Vendas',
                    'VENDAS_Conversao': 'Conversão (%)'
                }).set_index(df_campeoes_pm['🏆 Rank']),
                use_container_width=True
            )
        else:
            st.write("Nenhum anúncio com performance muito acima da média.")

    with col2:
        st.subheader("⚠️ Anúncios com Baixa Performance (PM)")
        if not df_perdedores_pm.empty:
            st.dataframe(
                df_perdedores_pm[colunas_exibir].rename(columns={
                    'UTM_TERM': 'Anúncio',
                    'PM_Leads': 'Pré-Matrículas',
                    'VENDAS_Alunos': 'Vendas',
                    'VENDAS_Conversao': 'Conversão (%)'
                }).set_index(df_perdedores_pm['📉 Rank']),
                use_container_width=True
            )
        else:
            st.write("Nenhum anúncio com performance muito abaixo da média.")


def mostrar_analise_vendas(DF_CENTRAL_VENDAS):
    st.subheader("💰 Análise de Vendas")
    # 0. Filtrar apenas anúncios pagos
    DF_VENDAS_FILTRADO = DF_CENTRAL_VENDAS[DF_CENTRAL_VENDAS['UTM_MEDIUM'] == 'pago'].copy()

    # 1. Métricas de Vendas:
    df_vendas_stage = DF_VENDAS_FILTRADO.groupby('UTM_TERM').agg(VENDAS_Alunos=('EMAIL', 'nunique'))
    total_vendas = DF_VENDAS_FILTRADO['EMAIL'].nunique()
    df_vendas_stage['VENDAS_Relativo'] = round(df_vendas_stage['VENDAS_Alunos'] / total_vendas * 100, 2)

    # Reorganizar colunas e definir índice
    df_vendas_stage = df_vendas_stage[['VENDAS_Alunos', 'VENDAS_Relativo']]
    df_vendas_stage = df_vendas_stage.sort_values('VENDAS_Alunos', ascending=False)
    df_vendas_stage.index.name = 'UTM_TERM'


    # Filtro mínimo
    coll = st.columns([1, 1])

    with coll[0]:
        threshold_vendas = st.number_input("Digite um número mínimo de alunos:", min_value=0, max_value=1000, value=0)
        df_vendas_stage = df_vendas_stage[df_vendas_stage["VENDAS_Alunos"] >= threshold_vendas]

        st.dataframe(df_vendas_stage)

    #------------------------------------------------------------
    #      Campeões e Perdedores (Vendas)
    #------------------------------------------------------------

    # Resetar index para manipular UTM_TERM como coluna
    df_base_vendas = df_vendas_stage.reset_index()

    # Calcular média e definir DESTAQUE com base no volume de vendas
    media_vendas = df_base_vendas['VENDAS_Alunos'].mean()
    df_base_vendas['DESTAQUE'] = df_base_vendas['VENDAS_Alunos'].apply(
        lambda x: 'Alta' if x > media_vendas * 1.5 else ('Baixa' if x < media_vendas else None)
    )

    # Campeões
    df_campeoes_vendas = df_base_vendas[df_base_vendas['DESTAQUE'] == 'Alta'].copy()
    df_campeoes_vendas['🏆 Rank'] = df_campeoes_vendas['VENDAS_Alunos'].rank(method='min', ascending=False).astype(int)
    df_campeoes_vendas = df_campeoes_vendas.sort_values('VENDAS_Alunos', ascending=False)

    # Perdedores
    df_perdedores_vendas = df_base_vendas[df_base_vendas['DESTAQUE'] == 'Baixa'].copy()
    df_perdedores_vendas['📉 Rank'] = df_perdedores_vendas['VENDAS_Alunos'].rank(method='min', ascending=False).astype(int)
    df_perdedores_vendas = df_perdedores_vendas.sort_values('VENDAS_Alunos', ascending=False)

    # Colunas a exibir
    colunas_exibir = ['UTM_TERM', 'VENDAS_Alunos', 'VENDAS_Relativo']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔝 Anúncios Campeões (Vendas)")
        if not df_campeoes_vendas.empty:
            st.dataframe(
                df_campeoes_vendas[colunas_exibir].rename(columns={
                    'UTM_TERM': 'Anúncio',
                    'VENDAS_Alunos': 'Vendas',
                    'VENDAS_Relativo': 'Participação (%)'
                }).set_index(df_campeoes_vendas['🏆 Rank']),
                use_container_width=True
            )
        else:
            st.write("Nenhum anúncio com performance muito acima da média.")

    with col2:
        st.subheader("⚠️ Anúncios com Baixa Performance (Vendas)")
        if not df_perdedores_vendas.empty:
            st.dataframe(
                df_perdedores_vendas[colunas_exibir].rename(columns={
                    'UTM_TERM': 'Anúncio',
                    'VENDAS_Alunos': 'Vendas',
                    'VENDAS_Relativo': 'Participação (%)'
                }).set_index(df_perdedores_vendas['📉 Rank']),
                use_container_width=True
            )
        else:
            st.write("Nenhum anúncio com performance muito abaixo da média.")
