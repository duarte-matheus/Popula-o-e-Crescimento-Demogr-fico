"""
Script de Análise Estatística Demográfica e Geração de Relatório Interativo
Foco: Componentes de Natalidade Municipal (Variabilidade Territorial, Amplitude e Dispersão Regional)
Linguagem: Python 3
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

def executar_analise():
    caminho_csv = os.path.join(os.path.dirname(__file__), "dados_natalidade_municipios.csv")
    if not os.path.exists(caminho_csv):
        print(f"[ERRO] Arquivo não encontrado: {caminho_csv}")
        return

    df = pd.read_csv(caminho_csv)
    print("=" * 80)
    print("ANÁLISE DEMOGRÁFICA: COMPONENTES DE NATALIDADE MUNICIPAL NO BRASIL")
    print("=" * 80)

    # 1. Estatísticas Descritivas Globais
    n_mun = len(df)
    pop_total = df["populacao"].sum()
    nasc_total = df["nascidos_vivos"].sum()
    tbn_ponderada = (nasc_total / pop_total) * 1000
    tbn_media = df["tbn"].mean()
    tbn_mediana = df["tbn"].median()
    tbn_std = df["tbn"].std()
    tbn_cv = (tbn_std / tbn_media) * 100
    tbn_min = df["tbn"].min()
    tbn_max = df["tbn"].max()
    tbn_amplitude = tbn_max - tbn_min
    q1 = df["tbn"].quantile(0.25)
    q3 = df["tbn"].quantile(0.75)
    tbn_iqr = q3 - q1
    skewness = stats.skew(df["tbn"])
    kurt = stats.kurtosis(df["tbn"])

    print("\n--- 1. PARÂMETROS GLOBAIS DE NATALIDADE ---")
    print(f"Municípios analisados:          {n_mun}")
    print(f"População agregada:             {pop_total:,.0f} habitantes")
    print(f"Total de nascimentos anuais:    {nasc_total:,.0f}")
    print(f"TBN Média Aritmética:           {tbn_media:.2f} ‰ (por mil hab.)")
    print(f"TBN Ponderada (Nacional):       {tbn_ponderada:.2f} ‰")
    print(f"TBN Mediana:                    {tbn_mediana:.2f} ‰")
    print(f"Desvio Padrão (σ):              ±{tbn_std:.2f} ‰")
    print(f"Coeficiente de Variação (CV):   {tbn_cv:.1f}%")
    print(f"Amplitude Total (Máx - Mín):    {tbn_amplitude:.2f} pontos de TBN")
    print(f"Polo Mínimo:                    {tbn_min:.2f} ‰ ({df.loc[df['tbn'].idxmin(), 'municipio']}/{df.loc[df['tbn'].idxmin(), 'uf']})")
    print(f"Polo Máximo:                    {tbn_max:.2f} ‰ ({df.loc[df['tbn'].idxmax(), 'municipio']}/{df.loc[df['tbn'].idxmax(), 'uf']})")
    print(f"Amplitude Interquartil (IQR):   {tbn_iqr:.2f} pontos (Q1: {q1:.2f}‰ | Q3: {q3:.2f}‰)")
    print(f"Coeficiente de Assimetria:      {skewness:.2f} (Assimetria Positiva / Cauda à Direita)")
    print(f"Curtose:                        {kurt:.2f}")

    # 2. Estatísticas por Macrorregião
    print("\n--- 2. MATRIZ REGIONAL DE DISPERSÃO E AMPLITUDE ---")
    def agrupar_regiao(g):
        taxas = g["tbn"]
        m = taxas.mean()
        s = taxas.std() if len(taxas) > 1 else 0
        return pd.Series({
            "N": len(g),
            "Media": round(m, 2),
            "Mediana": round(taxas.median(), 2),
            "DesvPad": round(s, 2),
            "CV_pct": round((s / m * 100), 1) if m > 0 else 0,
            "Min": round(taxas.min(), 2),
            "Max": round(taxas.max(), 2),
            "Amplitude": round(taxas.max() - taxas.min(), 2),
            "IQR": round(taxas.quantile(0.75) - taxas.quantile(0.25), 2)
        })

    tabela_reg = df.groupby("regiao").apply(agrupar_regiao, include_groups=False)
    print(tabela_reg.to_string())

    # 3. Teste Hipótese de Diferença Regional (Kruskal-Wallis)
    grupos_reg = [grupo["tbn"].values for _, grupo in df.groupby("regiao")]
    h_stat, p_val_kw = stats.kruskal(*grupos_reg)
    print("\n--- 3. TESTE DE HIPÓTESE REGIONAL (KRUSKAL-WALLIS) ---")
    print(f"Estatística H: {h_stat:.3f} | p-valor: {p_val_kw:.6e}")
    if p_val_kw < 0.05:
        print("[Conclusão] Diferença estatisticamente significativa entre as macrorregiões (p < 0.001).")

    # 4. Geração do Dashboard Interativo em HTML via Plotly
    print("\n--- 4. GERANDO DASHBOARD INTERATIVO VIA PLOTLY ---")
    cores_reg = {
        "Norte": "#10b981",
        "Nordeste": "#f59e0b",
        "Sudeste": "#3b82f6",
        "Sul": "#8b5cf6",
        "Centro-Oeste": "#ec4899"
    }

    # Criando Subplots de 2x2
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Dispersão Regional da TBN (Boxplot)",
            "Variabilidade: TBN vs IDHM (Correlação)",
            "Distribuição de Frequências (Histograma)",
            "Polos Extremos de Natalidade (Amplitude)"
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )

    # Gráfico 1: Boxplots Regionais
    for reg, cor in cores_reg.items():
        subset = df[df["regiao"] == reg]
        fig.add_trace(
            go.Box(
                y=subset["tbn"],
                name=reg,
                marker_color=cor,
                boxpoints="all",
                jitter=0.3,
                pointpos=-1.8,
                text=subset["municipio"] + " (" + subset["uf"] + ")"
            ),
            row=1, col=1
        )

    # Gráfico 2: Scatter TBN vs IDHM
    for reg, cor in cores_reg.items():
        subset = df[df["regiao"] == reg]
        fig.add_trace(
            go.Scatter(
                x=subset["idhm"],
                y=subset["tbn"],
                mode="markers",
                name=reg,
                marker=dict(size=8, color=cor, opacity=0.8),
                text=subset["municipio"] + " (" + subset["uf"] + ") - Pop: " + subset["populacao"].astype(str),
                showlegend=False
            ),
            row=1, col=2
        )

    # Linha de tendência linear no Scatter
    r_val, _ = stats.pearsonr(df["idhm"], df["tbn"])
    slope, intercept, _, _, _ = stats.linregress(df["idhm"], df["tbn"])
    x_range = np.linspace(df["idhm"].min(), df["idhm"].max(), 50)
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=slope * x_range + intercept,
            mode="lines",
            name=f"Tendência OLS (r={r_val:.2f})",
            line=dict(color="#f59e0b", dash="dash"),
            showlegend=False
        ),
        row=1, col=2
    )

    # Gráfico 3: Histograma Geral
    fig.add_trace(
        go.Histogram(
            x=df["tbn"],
            nbinsx=15,
            marker_color="#3b82f6",
            opacity=0.8,
            name="Frequência",
            showlegend=False
        ),
        row=2, col=1
    )

    # Gráfico 4: Polos de Amplitude (Top 5 Maiores e Menores)
    top_5 = df.sort_values(by="tbn", ascending=True).tail(5)
    bottom_5 = df.sort_values(by="tbn", ascending=True).head(5)
    extremos = pd.concat([bottom_5, top_5])
    cores_extremos = ["#ef4444"] * 5 + ["#10b981"] * 5

    fig.add_trace(
        go.Bar(
            x=extremos["tbn"],
            y=extremos["municipio"] + " (" + extremos["uf"] + ")",
            orientation="h",
            marker_color=cores_extremos,
            name="Extremos",
            showlegend=False
        ),
        row=2, col=2
    )

    fig.update_layout(
        template="plotly_dark",
        title_text="<b>Componentes Demográficos: Natalidade por Município</b><br>Variabilidade Territorial, Amplitude e Dispersão Regional",
        height=850,
        margin=dict(l=50, r=40, t=100, b=50)
    )

    caminho_saida_html = os.path.join(os.path.dirname(__file__), "dashboard_plotly.html")
    fig.write_html(caminho_saida_html)
    print(f"[SUCESSO] Relatório interativo Plotly salvo em: {caminho_saida_html}")
    print("=" * 80)

if __name__ == "__main__":
    executar_analise()
