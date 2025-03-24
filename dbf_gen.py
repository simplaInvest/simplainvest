import streamlit as st
from libs.debriefing_generator import generate_debriefing2

PRODUTO = st.session_state["PRODUTO"]
VERSAO_PRINCIPAL = st.session_state["VERSAO_PRINCIPAL"]

st.header(f'Dados de Debriefing {PRODUTO}.{VERSAO_PRINCIPAL}')

if st.button("Gerar dados de Debriefing"):
    conv_traf, conv_copy, conv_wpp, lista_tabs, bar_sexo, bar_filhos, bar_civil, bar_exp, graf_age, graf_ren, graf_pat, graf_inv, disc_grafs = generate_debriefing2(PRODUTO, VERSAO_PRINCIPAL)

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Conversão da pesquisa de tráfego")
        st.metric(label="", value= conv_traf)

    with col2:
        st.subheader("Conversão da pesquisa de copy")
        st.metric(label="", value= conv_copy)

    with col3:
        st.subheader("Conversão dos grupos de whatsapp")
        st.metric(label="", value= conv_wpp)
    
    st.divider()

    st.subheader('Anúncios')
    tab1, tab2, tab3 = st.tabs(["Captura", "Pré-matrícula", "Vendas"])

    with tab1:
        st.dataframe(lista_tabs[0][1], use_container_width = True, hide_index=True)

    with tab2:
        st.dataframe(lista_tabs[1][1], use_container_width = True, hide_index=True)

    with tab3:
        st.dataframe(lista_tabs[2][1], use_container_width = True, hide_index=True)

    st.divider()

    st.subheader("Perfis")

    tab_1, tab_2, tab_3 = st.tabs(["Fechadas", "Abertas", "Financeiro"])

    with tab_1:

        col_1, col_2 = st.columns(2)

        with col_1:
            bar_sexo
            bar_filhos
            bar_civil
        
        with col_2:
            bar_exp
            graf_age

    with tab_2:
        # Dividir a lista disc_grafs em duas metades
        metade = len(disc_grafs) // 2
        primeira_metade = disc_grafs[:metade]
        segunda_metade = disc_grafs[metade:]

        # Criar duas colunas no Streamlit
        col1, col2 = st.columns(2)

        # Exibir a primeira metade na primeira coluna
        with col1:
            for grafico in primeira_metade:
                st.pyplot(grafico)

        # Exibir a segunda metade na segunda coluna
        with col2:
            for grafico in segunda_metade:
                st.pyplot(grafico)

    with tab_3:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Renda")
            graf_ren
        
        with col2:
            st.subheader("Patrimônio")
            graf_pat