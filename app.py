"""
Dashboard Demográfico: Componentes de Natalidade Municipal
Foco: Comportamento das taxas de nascimentos, variabilidade territorial, amplitude e dispersão regional.
Autor: Antigravity Demographics Analytics
Framework: Streamlit & Plotly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import os

# Configuração da Página
st.set_page_config(
    page_title="Dashboard Demográfico: Natalidade Municipal",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada
st.markdown("""
<style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.75rem;
        padding: 1rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)

# Paleta de Cores Regionais Consistente
CORES_REGIOES = {
    "Norte": "#10b981",       # Esmeralda
    "Nordeste": "#f59e0b",    # Âmbar
    "Sudeste": "#3b82f6",     # Azul
    "Sul": "#8b5cf6",         # Roxo
    "Centro-Oeste": "#ec4899" # Rosa
}

# Carregamento de Dados com Cache
@st.cache_data
def carregar_dados():
    caminho_csv = os.path.join(os.path.dirname(__file__), "dados_natalidade_municipios.csv")
    if os.path.exists(caminho_csv):
        df = pd.read_csv(caminho_csv)
    else:
        # Fallback de segurança se o arquivo não estiver presente
        st.error(f"Arquivo CSV não encontrado em: {caminho_csv}")
        st.stop()
    return df

df_raw = carregar_dados()

# Barra Lateral: Filtros Interativos
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=64)
st.sidebar.title("Filtros Territoriais")
st.sidebar.markdown("Refine o conjunto de municípios em análise:")

# Filtro 1: Região
regioes_disponiveis = ["Todas"] + sorted(df_raw["regiao"].unique().tolist())
regiao_selecionada = st.sidebar.selectbox("Macrorregião", regioes_disponiveis, index=0)

# Filtro 2: Porte Populacional
portes_disponiveis = ["Todos"] + sorted(df_raw["faixa_porte"].unique().tolist())
porte_selecionado = st.sidebar.selectbox("Porte Populacional", portes_disponiveis, index=0)

# Filtro 3: Faixa de Natalidade
faixas_disponiveis = ["Todas"] + sorted(df_raw["classificacao_tbn"].unique().tolist())
faixa_selecionada = st.sidebar.selectbox("Classificação da TBN", faixas_disponiveis, index=0)

# Filtro 4: Busca Textual
busca = st.sidebar.text_input("Buscar Município ou UF", placeholder="Ex: Manaus, RS, SP...")

# Aplicação dos Filtros
df = df_raw.copy()

if regiao_selecionada != "Todas":
    df = df[df["regiao"] == regiao_selecionada]

if porte_selecionado != "Todos":
    df = df[df["faixa_porte"] == porte_selecionado]

if faixa_selecionada != "Todas":
    df = df[df["classificacao_tbn"] == faixa_selecionada]

if busca.strip():
    termo = busca.strip().lower()
    df = df[df["municipio"].str.lower().str.contains(termo) | df["uf"].str.lower().str.contains(termo)]

# Cabeçalho Principal
st.markdown('<div class="main-title">Componentes Demográficos: Natalidade Municipal</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Comportamento da Taxa Bruta de Natalidade (TBN por mil hab.), '
    'Variabilidade Territorial, Amplitude e Dispersão Regional (Base SINASC / DATASUS / IBGE)</div>',
    unsafe_allow_html=True
)

if df.empty:
    st.warning("Nenhum município atende aos critérios de filtro selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

# Cálculos Demográficos Centrais
media_tbn = df["tbn"].mean()
mediana_tbn = df["tbn"].median()
desvio_padrao = df["tbn"].std() if len(df) > 1 else 0.0
cv = (desvio_padrao / media_tbn * 100) if media_tbn > 0 else 0.0
min_tbn = df["tbn"].min()
max_tbn = df["tbn"].max()
amplitude_total = max_tbn - min_tbn
q1 = df["tbn"].quantile(0.25)
q3 = df["tbn"].quantile(0.75)
iqr = q3 - q1
pop_total_milhoes = df["populacao"].sum() / 1_000_000

# Painel Superior de KPIs
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("TBN Média", f"{media_tbn:.2f} ‰", help="Taxa Bruta de Natalidade média por 1.000 hab.")
with col2:
    st.metric("TBN Mediana", f"{mediana_tbn:.2f} ‰", help="Ponto central da distribuição (50% acima, 50% abaixo)")
with col3:
    st.metric("Amplitude Total", f"{amplitude_total:.2f} pts", help=f"Diferença entre Máx ({max_tbn:.2f}‰) e Mín ({min_tbn:.2f}‰)")
with col4:
    st.metric("Amplitude Interquartil", f"{iqr:.2f} pts", help=f"IQR = Q3 ({q3:.2f}‰) - Q1 ({q1:.2f}‰)")
with col5:
    st.metric("Coef. Variação (CV)", f"{cv:.1f} %", help=f"Variabilidade relativa: Desvio padrão = ±{desvio_padrao:.2f}‰")
with col6:
    st.metric("Amostra Analisada", f"{len(df)} mun.", help=f"População agregada: {pop_total_milhoes:.1f} milhões")

st.markdown("---")

# Abas Analíticas
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📦 Dispersão e Amplitude Regional",
    "🌍 Variabilidade Socioespacial",
    "📊 Distribuição de Frequências",
    "⚡ Polos Extremos de Amplitude",
    "📑 Matriz Estatística Regional",
    "💾 Dados Brutos e Exportação"
])

# ABA 1: BOXPLOT DE DISPERSÃO REGIONAL
with tab1:
    st.subheader("Dispersão Regional e Amplitude da Natalidade")
    st.markdown(
        "O diagrama de caixa (**Boxplot**) permite comparar a tendência central (mediana), "
        "a dispersão dos 50% centrais dos municípios (caixa interquartil IQR), os limites mínimos e máximos, "
        "e a presença de assimetrias ou valores atípicos (*outliers*)."
    )

    fig_box = px.box(
        df,
        x="regiao",
        y="tbn",
        color="regiao",
        color_discrete_map=CORES_REGIOES,
        points="all",
        hover_name="municipio",
        hover_data={"uf": True, "populacao": ":,", "idhm": ":.3f", "tbn": ":.2f"},
        labels={"regiao": "Macrorregião", "tbn": "Taxa Bruta de Natalidade (‰)"},
        category_orders={"regiao": ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]}
    )
    fig_box.update_layout(
        template="plotly_dark",
        height=520,
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=40),
        yaxis=dict(gridcolor="#334155", title="TBN (nascimentos por 1.000 hab.)"),
        xaxis=dict(gridcolor="#334155")
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # Destaques analíticos da dispersão
    st.info(
        "💡 **Interpretação Demográfica**: A Região Norte exibe a maior amplitude e maior mediana do país, "
        "com municípios de taxas superiores a 24‰ (transição demográfica retardada e populações jovens/indígenas). "
        "Já as Regiões Sul e Sudeste apresentam caixas compactas e valores mínimos inferiores a 7‰, "
        "caracterizando municípios de população envelhecida e fecundidade significativamente abaixo do nível de reposição."
    )

# ABA 2: VARIABILIDADE SOCIOESPACIAL (SCATTER PLOT)
with tab2:
    st.subheader("Variabilidade Socioespacial: Fatores Associados à Natalidade")
    st.markdown(
        "Explore a relação entre o comportamento da taxa de natalidade e variáveis de estrutura territorial e socioeconômica."
    )

    col_ctrl1, col_ctrl2 = st.columns([1, 3])
    with col_ctrl1:
        eixo_x_opcao = st.radio(
            "Selecione o Eixo X:",
            ["IDHM", "Grau de Urbanização (%)", "População (Escala Log)"],
            index=0
        )

    if eixo_x_opcao == "IDHM":
        x_col = "idhm"
        x_label = "Índice de Desenvolvimento Humano Municipal (IDHM)"
        log_x = False
    elif eixo_x_opcao == "Grau de Urbanização (%)":
        x_col = "grau_urbanizacao"
        x_label = "Grau de Urbanização (%)"
        log_x = False
    else:
        x_col = "populacao"
        x_label = "População Residente"
        log_x = True

    # Gráfico de Dispersão com Linha de Tendência OLS
    fig_scatter = px.scatter(
        df,
        x=x_col,
        y="tbn",
        color="regiao",
        color_discrete_map=CORES_REGIOES,
        size="populacao",
        size_max=35,
        hover_name="municipio",
        hover_data={"uf": True, "populacao": ":,", "idhm": ":.3f", "grau_urbanizacao": ":.1f", "tbn": ":.2f"},
        labels={"tbn": "TBN (‰)", x_col: x_label, "regiao": "Região"},
        log_x=log_x,
        trendline="ols" if len(df) > 3 else None,
        trendline_color_override="#f59e0b"
    )
    fig_scatter.update_layout(
        template="plotly_dark",
        height=520,
        margin=dict(l=40, r=40, t=20, b=40),
        yaxis=dict(gridcolor="#334155", title="Taxa Bruta de Natalidade (‰)"),
        xaxis=dict(gridcolor="#334155", title=x_label)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Correlação estatística
    if len(df) > 2:
        r_corr, p_val = stats.pearsonr(df[x_col], df["tbn"])
        st.markdown(
            f"**Estatística de Associação**: Coeficiente de Correlação de Pearson $r = {r_corr:.2f}$ "
            f"(Significância estatística $p = {p_val:.4f}$). "
            f"Determinação $R^2 = {r_corr**2:.2f}$."
        )

# ABA 3: HISTOGRAMA E DENSIDADE
with tab3:
    st.subheader("Distribuição Territorial de Frequência das Taxas")
    st.markdown(
        "Avalie a assimetria e o grau de concentração das taxas brutas de natalidade no território nacional."
    )

    fig_hist = px.histogram(
        df,
        x="tbn",
        color="regiao",
        color_discrete_map=CORES_REGIOES,
        nbins=18,
        marginal="violin",
        labels={"tbn": "Taxa Bruta de Natalidade (‰)", "count": "Número de Municípios"},
        opacity=0.85
    )
    # Linhas de Média e Mediana
    fig_hist.add_vline(x=media_tbn, line_dash="dash", line_color="#3b82f6", annotation_text=f"Média: {media_tbn:.2f}‰")
    fig_hist.add_vline(x=mediana_tbn, line_dash="dot", line_color="#10b981", annotation_text=f"Mediana: {mediana_tbn:.2f}‰")

    fig_hist.update_layout(
        template="plotly_dark",
        height=520,
        barmode="stack",
        margin=dict(l=40, r=40, t=30, b=40),
        yaxis=dict(gridcolor="#334155"),
        xaxis=dict(gridcolor="#334155", title="Taxa Bruta de Natalidade (‰)")
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown(
        "A distribuição apresenta nítida **assimetria à direita (positiva)**. O grosso das cidades aglomera-se "
        "entre 10,0‰ e 13,5‰, enquanto uma cauda alongada estende-se até quase 28‰, composta quase que exclusivamente "
        "por municípios do Norte e Centro-Oeste."
    )

# ABA 4: POLOS EXTREMOS DE AMPLITUDE
with tab4:
    st.subheader("Polos Extremos de Amplitude Demográfica")
    st.markdown(
        "Contraste entre os municípios de maior taxa de natalidade (polo alto) e menor taxa de natalidade (polo baixo)."
    )

    col_high, col_low = st.columns(2)

    top_altos = df.sort_values(by="tbn", ascending=False).head(8)
    top_baixos = df.sort_values(by="tbn", ascending=True).head(8)

    with col_high:
        st.markdown("##### 🟢 Maiores Taxas de Natalidade (Polo Alto)")
        fig_high = px.bar(
            top_altos,
            x="tbn",
            y="municipio",
            orientation="h",
            color="tbn",
            color_continuous_scale="Greens",
            text="tbn",
            hover_data={"uf": True, "regiao": True, "populacao": ":,"},
            labels={"tbn": "TBN (‰)", "municipio": "Município"}
        )
        fig_high.update_traces(texttemplate="%{text:.2f}‰", textposition="outside")
        fig_high.update_layout(
            template="plotly_dark",
            height=380,
            showlegend=False,
            coloraxis_showscale=False,
            yaxis=dict(autorange="reversed"),
            xaxis=dict(range=[0, max_tbn * 1.15], gridcolor="#334155")
        )
        st.plotly_chart(fig_high, use_container_width=True)

    with col_low:
        st.markdown("##### 🔴 Menores Taxas de Natalidade (Polo Baixo)")
        fig_low = px.bar(
            top_baixos,
            x="tbn",
            y="municipio",
            orientation="h",
            color="tbn",
            color_continuous_scale="Reds_r",
            text="tbn",
            hover_data={"uf": True, "regiao": True, "populacao": ":,"},
            labels={"tbn": "TBN (‰)", "municipio": "Município"}
        )
        fig_low.update_traces(texttemplate="%{text:.2f}‰", textposition="outside")
        fig_low.update_layout(
            template="plotly_dark",
            height=380,
            showlegend=False,
            coloraxis_showscale=False,
            yaxis=dict(autorange="reversed"),
            xaxis=dict(range=[0, 15], gridcolor="#334155")
        )
        st.plotly_chart(fig_low, use_container_width=True)

    ratio_extremos = (top_altos["tbn"].iloc[0] / top_baixos["tbn"].iloc[0]) if top_baixos["tbn"].iloc[0] > 0 else 0
    st.success(
        f"🎯 **Magnitude do Gap Territorial**: O município com maior taxa ({top_altos['municipio'].iloc[0]}/{top_altos['uf'].iloc[0]} com {top_altos['tbn'].iloc[0]:.2f}‰) "
        f"registra **{ratio_extremos:.1f} vezes** o ritmo proporcional de nascimentos do município na lanterna "
        f"({top_baixos['municipio'].iloc[0]}/{top_baixos['uf'].iloc[0]} com {top_baixos['tbn'].iloc[0]:.2f}‰)."
    )

# ABA 5: MATRIZ ESTATÍSTICA REGIONAL
with tab5:
    st.subheader("Matriz de Síntese Estatística da Dispersão por Região")
    st.markdown(
        "Métricas consolidadas de posição, dispersão e variabilidade das taxas de natalidade agrupadas por macrorregião:"
    )

    def calcular_estatisticas_grupo(grupo):
        taxas = grupo["tbn"]
        q1_g = taxas.quantile(0.25)
        q3_g = taxas.quantile(0.75)
        media_g = taxas.mean()
        std_g = taxas.std() if len(taxas) > 1 else 0.0
        cv_g = (std_g / media_g * 100) if media_g > 0 else 0.0
        min_g = taxas.min()
        max_g = taxas.max()
        return pd.Series({
            "Municípios": len(grupo),
            "População (M)": round(grupo["populacao"].sum() / 1_000_000, 2),
            "Média (‰)": round(media_g, 2),
            "Mediana (‰)": round(taxas.median(), 2),
            "Desvio Padrão (σ)": round(std_g, 2),
            "CV (%)": round(cv_g, 1),
            "Q1 (25%)": round(q1_g, 2),
            "Q3 (75%)": round(q3_g, 2),
            "IQR (Q3-Q1)": round(q3_g - q1_g, 2),
            "Mínimo (‰)": round(min_g, 2),
            "Máximo (‰)": round(max_g, 2),
            "Amplitude Total": round(max_g - min_g, 2)
        })

    tabela_regional = df.groupby("regiao").apply(calcular_estatisticas_grupo, include_groups=False).reset_index()
    tabela_regional.rename(columns={"regiao": "Macrorregião"}, inplace=True)

    # Linha Total Brasil
    total_brasil = calcular_estatisticas_grupo(df)
    total_brasil_df = pd.DataFrame([total_brasil])
    total_brasil_df.insert(0, "Macrorregião", "Total Analisado")
    tabela_consolidada = pd.concat([tabela_regional, total_brasil_df], ignore_index=True)

    st.dataframe(
        tabela_consolidada.style.highlight_max(subset=["Amplitude Total", "CV (%)"], color="#7f1d1d")
                               .highlight_min(subset=["Média (‰)", "Mediana (‰)"], color="#1e3a8a"),
        use_container_width=True
    )

# ABA 6: DADOS BRUTOS E DOWNLOAD
with tab6:
    st.subheader("Explorador de Dados Municipais")
    st.markdown("Consulte a base de dados filtrada e exporte os registros selecionados.")

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        csv_export = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Dados em CSV",
            data=csv_export,
            file_name="natalidade_municipal_brasil.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.dataframe(
        df[["codigo_ibge", "municipio", "uf", "regiao", "populacao", "nascidos_vivos", "tbn", "idhm", "grau_urbanizacao", "classificacao_tbn"]],
        column_config={
            "codigo_ibge": st.column_config.NumberColumn("Código IBGE", format="%d"),
            "municipio": "Município",
            "uf": "UF",
            "regiao": "Região",
            "populacao": st.column_config.NumberColumn("População", format="%d"),
            "nascidos_vivos": st.column_config.NumberColumn("Nascidos Vivos/Ano", format="%d"),
            "tbn": st.column_config.NumberColumn("TBN (‰)", format="%.2f"),
            "idhm": st.column_config.NumberColumn("IDHM", format="%.3f"),
            "grau_urbanizacao": st.column_config.NumberColumn("Urbanização (%)", format="%.1f%%"),
            "classificacao_tbn": "Classificação"
        },
        use_container_width=True,
        hide_index=True
    )

# Rodapé Metodológico
st.markdown("---")
st.caption(
    "📚 **Fonte & Metodologia**: Base de dados integrada por estimativas censitárias e projeções do IBGE cruzadas "
    "com registros do SINASC/DATASUS. A Taxa Bruta de Natalidade (TBN) corresponde ao quociente do total de nascidos vivos "
    "pela população residente no meio do ano, multiplicado por 1.000. Desenvolvido em Python com Streamlit e Plotly."
)
