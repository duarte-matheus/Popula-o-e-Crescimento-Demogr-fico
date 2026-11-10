# Dashboard Demográfico: Componentes de Natalidade Municipal (Versão Python)

Este projeto implementa uma solução analítica completa em **Python** voltada ao estudo dos **Componentes Demográficos de Natalidade**, com ênfase no **comportamento das taxas de nascimentos por município**, analisando a **variabilidade territorial**, a **amplitude** e a **dispersão regional**.

---

## 📁 Estrutura de Arquivos

```text
dashboard-demografico-natalidade/
├── app.py                           # Aplicação interativa em Streamlit & Plotly
├── analise_natalidade.py            # Script standalone de análise estatística e geração de HTML
├── dados_natalidade_municipios.csv   # Base de dados estruturada por município
├── requirements.txt                 # Dependências Python (Streamlit, Plotly, Pandas, etc.)
├── index.html                       # Versão web estática standalone
└── README.md                        # Documentação técnica e guia de execução
```

---

## 🚀 Como Executar em Python

### 1. Instalação das Dependências

Abra o terminal no diretório do projeto e execute:

```bash
pip install -r requirements.txt
```

### 2. Opção A: Executar o Dashboard Interativo (Streamlit)

O dashboard interativo em Streamlit oferece filtros laterais, recálculo dinâmico de métricas, abas analíticas, gráficos interativos em Plotly e exportação de dados:

```bash
streamlit run app.py
```

O aplicativo abrirá automaticamente no seu navegador em `http://localhost:8501`.

### 3. Opção B: Executar o Script Analítico e Gerar Relatório HTML (Standalone)

Caso prefira executar sem iniciar um servidor web, execute o script:

```bash
python analise_natalidade.py
```

O script:
1. Imprime no terminal o relatório descritivo completo (Média, Mediana, Desvio Padrão, CV%, IQR, Assimetria, Curtose e teste de hipótese de Kruskal-Wallis).
2. Gera o arquivo interativo **`dashboard_plotly.html`** contendo os 4 painéis integrados.

---

## 📌 Variáveis e Métricas do Modelo

- **TBN (Taxa Bruta de Natalidade)**: Nascimentos por 1.000 habitantes ($ \text{TBN} = \frac{\text{Nascidos Vivos}}{\text{População}} \times 1.000 $).
- **Variabilidade Territorial**: Medida pelo Desvio Padrão ($\sigma$) e pelo Coeficiente de Variação ($CV\% = \frac{\sigma}{\mu} \times 100\%$).
- **Amplitude Total**: Diferença entre a taxa máxima e mínima municipal ($A = \text{Taxa}_{\max} - \text{Taxa}_{\min}$).
- **Amplitude Interquartil (IQR)**: Mede a dispersão dos 50% centrais ($IQR = Q_3 - Q_1$).
- **Dispersão Regional**: Diagramas de caixa (Boxplots) das 5 macrorregiões com whiskers a $1.5 \times IQR$ e jittering de pontos individuais.
