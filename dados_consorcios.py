import json
import requests
import pandas as pd
import plotly.graph_objects as go

#novas implementações 
# - colocar as cores depois de filtrar (está assumindo a primeira cor, quando está no geral as cores estão certas)
# - hints nos quadros de kpi (ex: melhor mês da série, média por operação, total de registros exibidos)


# 1. Requisição à API
url = "https://royalblue-turtle-204261.hostingersite.com/ws_dados.php?tipo_pesquisa=1"

try:
    response = requests.get(url, timeout=10)
    dataJson = response.json()

    if isinstance(dataJson, dict) and "data" in dataJson:
        rawData = dataJson["data"]
    elif isinstance(dataJson, list):
        rawData = dataJson
    else:
        rawData = []
except Exception as e:
    print("Erro na API, carregando estrutura vazia:", e)
    rawData = []

# 2. DataFrame Pandas e Sanitização
df = pd.DataFrame(rawData)

# Tratamento colunas
if 'quantidade' not in df.columns:
    df['quantidade'] = 0
if 'segmento' not in df.columns:
    df['segmento'] = 'Não Informado'
if 'administradora' not in df.columns:
    df['administradora'] = 'Não Informada'
if 'data_referencia' not in df.columns:
    df['data_referencia'] = '2026-01-01'

# Formatação e limpeza dos dados
df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce').fillna(0).astype(int)
df['segmento'] = df['segmento'].astype(str).str.strip()
df['administradora'] = df['administradora'].astype(str).str.strip()

# 3. Tratamento de data e ordenação cronológica
df['dt_temp'] = pd.to_datetime(df['data_referencia'], errors='coerce')
meses_ordenados_dt = sorted([d for d in df['dt_temp'].dropna().unique()])
variavel_todos_meses = [pd.Timestamp(d).strftime('%m/%Y') for d in meses_ordenados_dt]

# Aplica a formatação definitiva MM/YYYY na coluna de referência
df['data_referencia'] = df['dt_temp'].dt.strftime('%m/%Y').fillna('Indefinido')
df.drop(columns=['dt_temp'], inplace=True)

# Extração de Segmentos e Administradoras
variavel_segmentos = sorted([s for s in df['segmento'].unique() if s and s.lower() != 'nan'])
variavel_administradoras = sorted([a for a in df['administradora'].unique() if a and a.lower() != 'nan'])

# Datas para os rótulos de período
dataInicio = variavel_todos_meses[0] if variavel_todos_meses else "N/A"
dataFim = variavel_todos_meses[-1] if variavel_todos_meses else "N/A"

# -------------------------------------------------------------
# 4. CRIAÇÃO DO GRÁFICO PLOTLY DIRETAMENTE NO PYTHON
# -------------------------------------------------------------
df_validos = df[df['data_referencia'] != 'Indefinido']

if not df_validos.empty:
    soma_por_mes = df_validos.groupby('data_referencia')['quantidade'].sum()
    melhor_mes_nome = soma_por_mes.idxmax()
    melhor_mes_valor = soma_por_mes.max()
    texto_melhor_mes_python = f"{melhor_mes_nome} ({melhor_mes_valor:,.0f})".replace(',', '.')
else:
    texto_melhor_mes_python = "N/A"

cores = ['#1A4B83', '#28A745', '#E67E22', '#8E44AD', '#17A2B8', '#D9534F', '#F39C12', '#34495E']
fig = go.Figure()

for index, seg in enumerate(variavel_segmentos):
    df_seg = df[df['segmento'] == seg]
    agrupado = df_seg.groupby('data_referencia')['quantidade'].sum().to_dict()
    valores = [agrupado.get(m, 0) for m in variavel_todos_meses]

    fig.add_trace(go.Bar(
        x=variavel_todos_meses,
        y=valores,
        name=seg,
        marker_color=cores[index % len(cores)],
        text=[f"{v:,}".replace(',', '.') if v > 0 else '' for v in valores],
        textposition='outside',
        hovertemplate='<b>%{fullData.name}</b><br>Qtd: %{y:,.0f}<extra></extra>'
    ))

fig.update_layout(
    barmode='group',
    hovermode='closest',
    margin=dict(l=40, r=20, t=30, b=60),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(showgrid=True, gridcolor='#E0E6ED', title='Quantidade Comercializada'),
    xaxis=dict(type='category', title='Mês / Ano de Referência'),
    legend=dict(orientation='h', y=1.18, x=0),
    font=dict(family="Segoe UI", color='#6C757D')
)

# Converte o gráfico criado no Python para HTML Div estático/inicial
chart_html = fig.to_html(full_html=False, include_plotlyjs=False, div_id="plotlyChart")

# Converte o DataFrame limpo para JSON para re-filtragem dinâmica no JS
dados_json_str = df.to_json(orient='records')

# 5. Geração do HTML + JS
html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Consórcios</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Plotly.js -->
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

    <style>
        :root {{
            --primary-blue: #1A4B83;
            --secondary-blue: #3478C6;
            --accent-blue: #0A2540;
            --bg-light: #F4F7FA;
            --card-bg: #FFFFFF;
            --border-color: #E0E6ED;
        }}
        body {{
            background-color: var(--bg-light);
            color: #333;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        h2 {{ color: var(--accent-blue); font-weight: 700; }}
        .kpi-card {{
            border: none;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(10, 37, 64, 0.05);
            background-color: var(--card-bg);
        }}
        .kpi-card-primary {{
            background-color: var(--primary-blue);
            color: #FFFFFF;
        }}
        .kpi-title {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.8;
        }}
        .kpi-value {{
            font-size: 1.6rem;
            font-weight: 700;
        }}
        .chart-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }}
        .filter-section {{
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 1rem 1.5rem;
            border: 1px solid var(--border-color);
            margin-bottom: 1.5rem;
        }}
    </style>
</head>
<body class="p-4">

    <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom">
            <h2>Cotas comercializadas de Consórcios</h2>
            <span class="text-muted">Dados recuperados via Python</span>
        </div>

        <!-- FILTROS -->
        <div class="filter-section shadow-sm">
            <div class="row align-items-end g-3">
                <div class="col-md-4">
                    <label for="selectSegmento" class="form-label fw-bold">Segmento:</label>
                    <select id="selectSegmento" class="form-select" onchange="aplicarFiltros()">
                        <option value="TODOS">Todos os Segmentos ({len(variavel_segmentos)})</option>
                        {"".join([f'<option value="{s}">{s}</option>' for s in variavel_segmentos])}
                    </select>
                </div>
                <div class="col-md-5">
                    <label for="selectAdmin" class="form-label fw-bold">Administradora:</label>
                    <select id="selectAdmin" class="form-select" onchange="aplicarFiltros()">
                        <option value="TODOS">Todas as Administradoras ({len(variavel_administradoras)})</option>
                        {"".join([f'<option value="{a}">{a}</option>' for a in variavel_administradoras])}
                    </select>
                </div>
                <div class="col-md-3">
                    <button class="btn btn-primary w-100 fw-bold" onclick="resetarFiltros()">
                        Filtro Geral (Limpar)
                    </button>
                </div>
            </div>
        </div>

        <!-- KPIS -->
        <div class="row mb-4">
            <div class="col-md-4 mb-3">
                <div class="card kpi-card kpi-card-primary h-100">
                    <div class="card-body">
                        <div class="kpi-title">Quantidade Total Comercializada (Período {dataInicio} - {dataFim})</div>
                        <div class="kpi-value" id="kpiTotalQtd">0</div>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card kpi-card border h-100">
                    <div class="card-body">
                        <div class="kpi-title text-muted">Melhor Mês da Série</div>
                        <div class="kpi-value" style="color: var(--secondary-blue);" id="kpiMelhorMes">0</div>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card kpi-card border h-100">
                    <div class="card-body">
                        <div class="kpi-title text-muted">Média por Operação</div>
                        <div class="kpi-value" style="color: var(--secondary-blue);" id="kpiMedia">0</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- GRÁFICO GERADO PELO PYTHON E INJETADO -->
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="chart-card">
                    <h5 class="mb-3" style="color: var(--primary-blue);">Evolução Mensal por Segmento</h5>
                    {chart_html}
                </div>
            </div>
        </div>
    </div>

    <!-- SCRIPT JS PARA MANTER A INTERATIVIDADE DOS FILTROS -->
    <script>
        const rawData = {dados_json_str};

        function aplicarFiltros() {{
            const segSelecionado = document.getElementById("selectSegmento").value;
            const adminSelecionada = document.getElementById("selectAdmin").value;

            let dadosFiltrados = rawData.filter(item => {{
                let matchSeg = (segSelecionado === "TODOS" || item.segmento === segSelecionado);
                let matchAdmin = (adminSelecionada === "TODOS" || item.administradora === adminSelecionada);
                return matchSeg && matchAdmin;
            }});

            atualizarKPIs(dadosFiltrados);
            atualizarGraficoPorSegmento(dadosFiltrados);
        }}

        function resetarFiltros() {{
            document.getElementById("selectSegmento").value = "TODOS";
            document.getElementById("selectAdmin").value = "TODOS";
            aplicarFiltros();
        }}

        function atualizarKPIs(dados) {{
            let totalQtd = dados.reduce((acc, curr) => acc + (parseInt(curr.quantidade) || 0), 0);
            let totalRegistros = dados.length;
            let media = totalRegistros > 0 ? (totalQtd / totalRegistros).toFixed(1) : 0;

            let somaPorMes = {{}};
            dados.forEach(item => {{
                let mes = item.data_referencia;
                if (mes && mes !== 'Indefinido') {{
                    somaPorMes[mes] = (somaPorMes[mes] || 0) + (parseInt(item.quantidade) || 0);
                }}
            }});

            let melhorMes = "N/A";
            let maiorValor = -1;

            Object.keys(somaPorMes).forEach(mes => {{
                if (somaPorMes[mes] > maiorValor) {{
                    maiorValor = somaPorMes[mes];
                    melhorMes = mes;
                }}
            }});

            let textoMelhorMes = maiorValor > 0 ? `${{melhorMes}} (${{maiorValor.toLocaleString('pt-BR')}})` : "N/A";

            document.getElementById("kpiTotalQtd").innerText = totalQtd.toLocaleString('pt-BR');
            document.getElementById("kpiMelhorMes").innerText = textoMelhorMes;
            document.getElementById("kpiMedia").innerText = media.replace('.', ',');
        }}

        function atualizarGraficoPorSegmento(dados) {{
            let conjuntoSegmentos = new Set();
            dados.forEach(item => {{
                if(item.segmento) conjuntoSegmentos.add(item.segmento);
            }});
            let segmentos = Array.from(conjuntoSegmentos).sort();

            let conjuntoMeses = new Set();
            dados.forEach(item => {{
                if(item.data_referencia && item.data_referencia !== 'Indefinido') {{
                    conjuntoMeses.add(item.data_referencia);
                }}
            }});

            let meses = Array.from(conjuntoMeses).sort((a, b) => {{
                let [mesA, anoA] = a.split('/').map(Number);
                let [mesB, anoB] = b.split('/').map(Number);
                return new Date(anoA, mesA - 1) - new Date(anoB, mesB - 1);
            }});

            let dadosAgrupados = {{}};
            segmentos.forEach(seg => {{
                dadosAgrupados[seg] = {{}};
                meses.forEach(mes => {{ dadosAgrupados[seg][mes] = 0; }});
            }});

            dados.forEach(item => {{
                let seg = item.segmento;
                let mes = item.data_referencia;
                if(dadosAgrupados[seg] && dadosAgrupados[seg][mes] !== undefined) {{
                    dadosAgrupados[seg][mes] += parseInt(item.quantidade || 0);
                }}
            }});

            const cores = [
                '#1A4B83', '#28A745', '#E67E22', '#8E44AD', 
                '#17A2B8', '#D9534F', '#F39C12', '#34495E'
            ];

            let traces = segmentos.map((seg, index) => {{
                let valores = meses.map(m => dadosAgrupados[seg][m]);
                return {{
                    x: meses,
                    y: valores,
                    name: seg,
                    type: 'bar',
                    marker: {{ color: cores[index % cores.length] }},
                    text: valores.map(v => v > 0 ? v.toLocaleString('pt-BR') : ''),
                    textposition: 'outside',
                    hovertemplate: '<b>%{{fullData.name}}</b><br>Qtd: %{{y:,.0f}}<extra></extra>'
                }};
            }});

            let layout = {{
                barmode: 'group',
                hovermode: 'closest',
                margin: {{ l: 40, r: 20, t: 30, b: 60 }},
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                yaxis: {{ showgrid: true, gridcolor: '#E0E6ED', title: 'Quantidade Comercializada' }},
                xaxis: {{ type: 'category', title: 'Mês / Ano de Referência' }},
                legend: {{ orientation: 'h', y: 1.18, x: 0 }},
                font: {{ family: "Segoe UI", color: '#6C757D' }}
            }};

            Plotly.react('plotlyChart', traces, layout);
        }}

        document.addEventListener("DOMContentLoaded", function() {{
            aplicarFiltros();
        }});
    </script>
</body>
</html>
"""

# 6. Salva o HTML gerado
with open("dashboard_consorcios.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Dashboard gerado via Python com sucesso!")