import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px
from libs.data_loader import K_CENTRAL_CAPTURA, K_CENTRAL_VENDAS, K_GRUPOS_WPP, K_PCOPY_DADOS, K_PTRAFEGO_DADOS, K_PTRAFEGO_META_ADS, K_CLICKS_WPP, K_CENTRAL_PRE_MATRICULA, K_CENTRAL_LANCAMENTOS, get_df

# Carregar informações sobre lançamento selecionado
# Removido código global que quebrava a importação.
# As variáveis PRODUTO e VERSAO_PRINCIPAL devem ser passadas como argumento ou acessadas dentro das funções.

# ====== Paleta alinhada ao seu tema dark (sem CSS extra) ======
PRIMARY = "#60A5FA"   # azul principal
INK     = "#E5EAF5"   # texto claro
MUTED   = "#9BA8C7"   # texto secundário
DANGER  = "#EF4444"   # vermelho (CPL)
OK      = "#22C55E"   # verde (se precisar)

# --------------------------------------------------------------
# 1) GRUPOS WPP: membros por dia (Altair)
# --------------------------------------------------------------
def plot_group_members_per_day_altair(DF_GRUPOS_WPP):
    if DF_GRUPOS_WPP.empty:
        st.warning("No data available for group entries.")
        return None

    df = DF_GRUPOS_WPP.copy()
    df['Data'] = pd.to_datetime(df['Data'])
    daily_activity = df.groupby(df['Data'].dt.date)[['Entradas', 'Saidas']].sum().reset_index()
    daily_activity.rename(columns={'Data': 'Date'}, inplace=True)
    daily_activity['Members'] = daily_activity['Entradas'].cumsum() - daily_activity['Saidas'].cumsum()

    base = alt.Chart(daily_activity).encode(
        x=alt.X('Date:T', title='Data', axis=alt.Axis(labelAngle=0, format="%d %b (%a)")),
        y=alt.Y('Members:Q', title='Número de membros', axis=alt.Axis(format="~s")),
        tooltip=[alt.Tooltip('Date:T', title='Data'), alt.Tooltip('Members:Q', title='Membros', format=',')]
    )

    line = base.mark_line(color=PRIMARY, strokeWidth=2.5)
    points = base.mark_point(color=PRIMARY, filled=True, size=60, opacity=0.95)
    labels = alt.Chart(daily_activity).mark_text(
        align='center', baseline='bottom', dy=-8, color=MUTED, fontSize=11
    ).encode(x='Date:T', y='Members:Q', text=alt.Text('Members:Q', format=','))

    # Linhas/labels de CPL opcional (via st.session_state["CPLs"])
    layers = [line, points, labels]
    if "CPLs" in st.session_state and st.session_state["CPLs"]:
        cpl_df = pd.DataFrame({
            "CPLs": pd.to_datetime(st.session_state["CPLs"]),
            "CPL_Label": [f"CPL{i+1}" for i in range(len(st.session_state["CPLs"]))],
        })
        min_d, max_d = daily_activity["Date"].min(), daily_activity["Date"].max()
        cpl_df = cpl_df[(cpl_df["CPLs"].dt.date >= min_d) & (cpl_df["CPLs"].dt.date <= max_d)]
        if not cpl_df.empty:
            cpl_lines = alt.Chart(cpl_df).mark_rule(strokeDash=[4, 4], color=DANGER).encode(x='CPLs:T')
            cpl_labels = alt.Chart(cpl_df).mark_text(align='left', baseline='top', dy=14, color=DANGER).encode(
                x='CPLs:T', text='CPL_Label'
            )
            layers += [cpl_lines, cpl_labels]

    chart = alt.layer(*layers).properties(width=700, height=400, title='Group Members Over Time').configure_axis(
        grid=False, labelColor=INK, titleColor=INK
    ).configure_title(color=INK).configure_view(strokeWidth=0).configure(background='rgba(0,0,0,0)')

    return st.altair_chart(chart, use_container_width=True)

# --------------------------------------------------------------
# 2) Leads por dia (Altair)
# --------------------------------------------------------------
def plot_leads_per_day_altair(DF_CENTRAL_CAPTURA, DF_CENTRAL_LANCAMENTOS, lancamento):
    if DF_CENTRAL_CAPTURA.empty:
        st.warning("Os dados de Leads por Dia estão vazios.")
        return None

    df_leads = DF_CENTRAL_CAPTURA[['EMAIL', 'CAP DATA_CAPTURA']].copy()
    df_lanc = DF_CENTRAL_LANCAMENTOS.copy()

    df_leads = df_leads.groupby('CAP DATA_CAPTURA').count().reset_index()
    df_leads["CAP DATA_CAPTURA"] = pd.to_datetime(df_leads["CAP DATA_CAPTURA"])
    df_lanc['CAPTACAO_INICIO'] = pd.to_datetime(df_lanc['CAPTACAO_INICIO'], dayfirst=True)
    df_lanc['VENDAS_FIM'] = pd.to_datetime(df_lanc['VENDAS_FIM'], dayfirst=True)

    min_date = df_lanc.loc[df_lanc['LANÇAMENTO'] == lancamento, 'CAPTACAO_INICIO'].iloc[0]
    max_date = df_lanc.loc[df_lanc['LANÇAMENTO'] == lancamento, 'VENDAS_FIM'].iloc[0]
    total_dias = (max_date - min_date).days
    x_scale = alt.Scale(domain=[min_date, max_date])

    base = alt.Chart(df_leads).encode(
        x=alt.X('CAP DATA_CAPTURA:T', title='Data', axis=alt.Axis(labelAngle=0, format="%d %b (%a)"), scale=x_scale),
        y=alt.Y('EMAIL:Q', title='Número de Leads', axis=alt.Axis(format="~s")),
        tooltip=[alt.Tooltip('CAP DATA_CAPTURA:T', title='Data'),
                 alt.Tooltip('EMAIL:Q', title='Leads', format=',')]
    )
    line = base.mark_line(color=PRIMARY, strokeWidth=2.5)
    pts  = base.mark_point(color=PRIMARY, filled=True, size=60, opacity=0.95)
    labels = alt.Chart(df_leads).mark_text(align='center', baseline='bottom', dy=-8, color=MUTED, fontSize=11).encode(
        x=alt.X('CAP DATA_CAPTURA:T', scale=x_scale),
        y='EMAIL:Q',
        text=alt.Text('EMAIL:Q', format=',')
    )

    # CPLs extraídas do DF_CENTRAL_LANCAMENTOS (sua lógica atual, só visual melhorado)
    cpl_df = pd.DataFrame()
    df_l = df_lanc[df_lanc['LANÇAMENTO'] == lancamento]
    if not df_l.empty:
        cpl_cols = ['CPL01', 'CPL02', 'CPL03', 'CPL04']
        dates, labels_cpl = [], []
        for i, col in enumerate(cpl_cols):
            v = df_l.iloc[0][col]
            if pd.notnull(v) and v != '':
                try:
                    d = pd.to_datetime(v, dayfirst=True)
                    dates.append(d); labels_cpl.append(f'CPL{i+1}')
                except Exception:
                    pass
        if dates:
            cpl_df = pd.DataFrame({'CPLs': dates, 'CPL_Label': labels_cpl})
            cpl_df = cpl_df[(cpl_df['CPLs'] >= min_date) & (cpl_df['CPLs'] <= max_date)]

    layers = [line, pts, labels]
    if not cpl_df.empty:
        cpl_lines = alt.Chart(cpl_df).mark_rule(strokeDash=[4, 4], color=DANGER).encode(
            x=alt.X('CPLs:T', scale=x_scale)
        )
        cpl_text = alt.Chart(cpl_df).mark_text(align='left', baseline='top', dy=14, color=DANGER).encode(
            x=alt.X('CPLs:T', scale=x_scale), text='CPL_Label'
        )
        layers += [cpl_lines, cpl_text]

    chart = alt.layer(*layers).properties(
        width=700, height=400, title=f'Leads por Dia • {total_dias} dias de captação'
    ).configure_axis(
        grid=False, labelColor=INK, titleColor=INK
    ).configure_title(
        color=INK
    ).configure_view(
        strokeWidth=0
    ).configure(
        background='rgba(0,0,0,0)'
    )

    return st.altair_chart(chart, use_container_width=True)

# --------------------------------------------------------------
# 3) Barras horizontais por classe (Altair)
# --------------------------------------------------------------
def plot_utm_source_counts_altair(df, column_name='UTM_SOURCE'):
    class_counts = df[column_name].value_counts().reset_index()
    class_counts.columns = [column_name, 'Count']
    class_counts = class_counts.sort_values(by='Count', ascending=False)

    bars = alt.Chart(class_counts).mark_bar(cornerRadiusEnd=3, opacity=0.95, color=PRIMARY).encode(
        x=alt.X('Count:Q', title='Contagem', axis=alt.Axis(format="~s")),
        y=alt.Y(f'{column_name}:N', sort='-x', title='Classe'),
        tooltip=[alt.Tooltip('Count:Q', title='Contagem', format=','), alt.Tooltip(f'{column_name}:N', title='Classe')]
    ).properties(width=640, height=420)

    text = alt.Chart(class_counts).mark_text(
        align='left', baseline='middle', dx=6, color=INK, fontSize=12
    ).encode(
        x='Count:Q', y=f'{column_name}:N', text=alt.Text('Count:Q', format=',')
    )

    chart = alt.layer(bars, text).configure_axis(
        grid=False, labelColor=INK, titleColor=INK
    ).configure_title(color=INK).configure_view(strokeWidth=0).configure(background='rgba(0,0,0,0)')

    st.altair_chart(chart, use_container_width=True)

# --------------------------------------------------------------
# 4) Pizza (donut) por medium (Altair)
# --------------------------------------------------------------
def plot_utm_medium_pie_chart(df, column_name='UTM_MEDIUM', classes_to_include=None):
    if classes_to_include is None:
        classes_to_include = ['organico', 'pago', 'indefinido']

    filtered_df = df[df[column_name].isin(classes_to_include)]
    class_counts = filtered_df[column_name].value_counts().reset_index()
    class_counts.columns = [column_name, 'Count']
    total = class_counts['Count'].sum()
    class_counts['Percentage'] = (class_counts['Count'] / max(total, 1) * 100).round(2)

    pie = alt.Chart(class_counts).mark_arc(innerRadius=70).encode(
        theta=alt.Theta('Count:Q'),
        color=alt.Color(f'{column_name}:N',
                        legend=alt.Legend(title='Classe'),
                        scale=alt.Scale(range=['#1E3A8A', '#3B82F6', '#93C5FD'])),
        tooltip=[
            alt.Tooltip(f'{column_name}:N', title='Classe'),
            alt.Tooltip('Count:Q', title='Contagem', format=','),
            alt.Tooltip('Percentage:Q', title='Porcentagem', format='.2f')
        ]
    ).properties(width=420, height=420)

    labels = alt.Chart(class_counts).mark_text(radius=130, fontSize=14, color=INK).encode(
        theta=alt.Theta('Count:Q'),
        text=alt.Text('Percentage:Q', format='.1f')
    )

    chart = alt.layer(pie, labels).configure_axis(
        grid=False, labelColor=INK, titleColor=INK
    ).configure_legend(
        labelColor=INK, titleColor=INK
    ).configure_title(color=INK).configure_view(strokeWidth=0).configure(background='rgba(0,0,0,0)')

    st.altair_chart(chart, use_container_width=True)

# --------------------------------------------------------------
# 5) Barras estilizadas (Plotly)
# --------------------------------------------------------------
def styled_bar_chart(x, y, title, colors=['#ADD8E6', '#5F9EA0']):
    fig = go.Figure(data=[
        go.Bar(x=[x[0]], y=[y[0]], marker_color=colors[0], marker_line_width=1, marker_line_color='rgba(255,255,255,0.25)', name=str(x[0]),
               text=[y[0]], textposition='outside', texttemplate='%{text:,}'),
        go.Bar(x=[x[1]], y=[y[1]], marker_color=colors[1], marker_line_width=1, marker_line_color='rgba(255,255,255,0.25)', name=str(x[1]),
               text=[y[1]], textposition='outside', texttemplate='%{text:,}')
    ])

    fig.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=INK),
        title=dict(text=title, x=0.5, font=dict(size=20, color=INK)),
        xaxis=dict(showgrid=False, tickfont=dict(color=INK)),
        yaxis=dict(showgrid=False, tickfont=dict(color=INK), rangemode='tozero'),
        margin=dict(l=10, r=10, t=48, b=10),
        showlegend=False
    )
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Valor: %{y:,}<extra></extra>')
    return fig
