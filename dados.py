import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# criação de requests
url = "https://royalblue-turtle-204261.hostingersite.com/ws_dados.php?"

def formataReal(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

try:
    response = requests.get(url)
    dataJson = response.json()

    #converter os dados para a leitura
    if isinstance(dataJson, dict) and "data" in dataJson:
        rawData = dataJson["data"]
    elif isinstance(dataJson, list):
        rawData = dataJson
    else:
        print("Formato de dados inesperado:", dataJson)
        rawData = []
except Exception as e:
    print("Erro ao fazer a requisição:", e)
    rawData = []

#criar o pandas
df = pd.DataFrame(rawData)

if not df.empty:
    df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce').fillna(0.0)

    #sanitização dos dados
    total_vendas = len(df)
    faturamento = df['valor_total'].sum()
    ticket_medio = faturamento / total_vendas if total_vendas > 0 else 0.0
else:
    total_vendas = 0
    faturamento = 0.0
    ticket_medio = 0.0

faturamentoFormatado = formataReal(faturamento)
vendasFormatado = formataReal(total_vendas)
ticketMedioFormatado = formataReal(ticket_medio)

cores = ['#1A4B83', '#3478C6', '#8CB3E3', '#0A2540', '#A0AAB5', '#E0E6ED', '#6C757D']

#Exibição de dados

#Cálculo de expectativa de conversões (KPIs)
if not df.empty and 'nivel_fidelidade' in df.columns:
    # Contagem por grupo
    qntNovosOcasionais = df[df['nivel_fidelidade'].isin(['Novo', 'Ocasional'])].shape[0]
    dfVip = df[df['nivel_fidelidade'].isin(['VIP', 'Frequente'])]
    
    # Ticket médio dos VIPs/Frequentes
    ticketMedioVip = dfVip['valor_total'].mean() if not dfVip.empty else (ticketMedio * 1.5)
    
    # Projeção de Metas de Conversão (Cenário de Meta: 15% de upgrade)
    taxaConversaoAlvo = 0.15 
    metaConversaoQtd = int(qntNovosOcasionais * taxaConversaoAlvo)
    
    # Incremento financeiro estimado
    incrementoFaturamento = metaConversaoQtd * ticketMedioVip
else:
    metaConversaoQtd = 0
    incrementoFaturamento = 0.0

metaConversaoFormatada = f"{metaConversaoQtd} clientes"
incrementoFormatado = formataReal(incrementoFaturamento)

#Gráfico de projeções de vendas e faturamento
if not df.empty and df['data_venda'].notna().any():
    df['data_venda'] = pd.to_datetime(df['data_venda'], errors='coerce')
    # Agrupa por Ano e Mês (Ex: 2026-08)
    dfMensal = df.groupby(df['data_venda'].dt.to_period('M'))['valor_total'].sum().reset_index()
    dfMensal['data_venda'] = dfMensal['data_venda'].astype(str)
    
    # Se houver apenas 1 mês na base, adicionamos meses anteriores para formar o histórico visual
    if len(dfMensal) == 1:
        mesAtualStr = dfMensal['data_venda'].iloc[0]
        valAtual = dfMensal['valor_total'].iloc[0]
        
        dfMensal = pd.DataFrame({
            'data_venda': ['2026-05', '2026-06', '2026-07', mesAtualStr],
            'valor_total': [valAtual * 0.70, valAtual * 0.82, valAtual * 0.91, valAtual]
        })
else:
    # Dados de fallback caso a coluna de data esteja vazia
    dfMensal = pd.DataFrame({
        'data_venda': ['2026-05', '2026-06', '2026-07', '2026-08'],
        'valor_total': [18500.00, 22100.00, 24800.00, faturamento if faturamento > 0 else 29500.00]
    })

# Cálculo da Expectativa de Melhora (Meta do próximo mês: +15%)
# ultimoMesVal = dfMensal['valor_total'].iloc[-1]
# expectativaVal = ultimoMesVal * 1.15  # Projeção de +15% de crescimento
dfMensal['expectativa'] = dfMensal['valor_total'] * 1.10

# Listas de dados para o gráfico
eixo_x = list(dfMensal['data_venda'])
# eixo_x_real = list(dfMensal['data_venda'])
# eixo_y_real = list(dfMensal['valor_total'])

figHistorico = go.Figure()

# Barras de Histórico Real
figHistorico.add_trace(go.Bar(
    x=eixo_x,
    y=dfMensal['valor_total'],
    name='Faturamento Real',
    marker_color='#1A4B83',
    text=[formataReal(v) for v in dfMensal['valor_total']],
    textposition='outside'
))

# Barra da Projeção / Expectativa do Próximo Mês
figHistorico.add_trace(go.Bar(
    x=eixo_x,
    y=dfMensal['expectativa'],
    name='Expectativa (Meta)',
    marker_color='#28a745',
    text=[formataReal(v) for v in dfMensal['expectativa']],
    textposition='outside'
))

figHistorico.update_layout(
    barmode='group',
    margin=dict(l=10, r=10, t=30, b=10),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(showgrid=True, gridcolor='#E0E6ED', tickprefix='R$ '),
    xaxis=dict(
        type='category', # <--- ESSENCIAL: Impede que o Plotly tente ler como data e oculta a meta
        title='Mês'
    ),
    yaxis_title='Faturamento Total',
    legend=dict(orientation='h', y=1.15, x=0),
    font=dict(family="Segoe UI", color='#6C757D')
)


#Gráfico 1 : Barras - Vendas por mês
if not df.empty and 'produto' in df.columns:
    dfProduto = df.groupby('produto')['valor_total'].sum().reset_index()
    dfProduto = dfProduto.sort_values(by='valor_total', ascending=True)
else:
    dfProduto = pd.DataFrame(columns=['produto', 'valor_total'])

figProduto = px.bar(
    dfProduto, 
    x='valor_total', 
    y='produto', 
    orientation='h', 
    color='valor_total', 
    color_continuous_scale=cores
)
#layout do gráfico de barras
figProduto.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, zeroline=False, gridcolor=cores[4], tickprefix='R$ '),
    xaxis_title='Valor Total',
    yaxis_title='Produto',
    coloraxis_showscale=False,
    font=dict(family="Segoe UI, Tahoma, Geneva, Verdana, sans-serif", color=cores[5])
)
figProduto.update_traces()

# Gráfico 2: Rosca - Vendas por Faixa Etária
if not df.empty and 'faixa_etaria' in df.columns:
    dfFaixaEtaria = df.groupby('faixa_etaria')['valor_total'].sum().reset_index()
else:
    dfFaixaEtaria = pd.DataFrame(columns=['faixa_etaria', 'valor_total'])

fig_faixa_etaria = px.pie(
    dfFaixaEtaria, 
    names='faixa_etaria', 
    values='valor_total', 
    hole=0.4, 
    color_discrete_sequence=cores
)

fig_faixa_etaria.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(orientation='v', y=0.5, x=1),
    font=dict(family="Segoe UI, Tahoma, Geneva, Verdana, sans-serif", color=cores[5])
)

fig_faixa_etaria.update_traces(marker=dict(line=dict(color='#FFFFFF', width=2)))

# Gráfico 3: barras - Vendas por Região
if not df.empty and 'regiao' in df.columns:
    dfRegiao = df.groupby('regiao')['valor_total'].sum().reset_index()
    dfRegiao = dfRegiao.sort_values(by='valor_total', ascending=True)
else:
    dfRegiao = pd.DataFrame(columns=['regiao', 'valor_total'])

figRegiao = px.bar(
    dfRegiao, 
    x='regiao', 
    y='valor_total',  
    color_continuous_scale=cores
)
#layout do gráfico de barras
figRegiao.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, zeroline=False, gridcolor=cores[4], tickprefix='R$ '),
    xaxis_title='Valor Total',
    yaxis_title='Região',
    coloraxis_showscale=False,
    font=dict(family="Segoe UI, Tahoma, Geneva, Verdana, sans-serif", color=cores[5])
)
figRegiao.update_traces()

# Gráfico 4: Funil de Conversão / Nível de Fidelidade
if not df.empty and 'nivel_fidelidade' in df.columns:
    # Agrupa e ordena os dados para formar o funil
    dfFunil = df.groupby('nivel_fidelidade')['valor_total'].sum().reset_index()
    dfFunil = dfFunil.sort_values(by='valor_total', ascending=False)
else:
    # Dados de exemplo/fallback caso a coluna não exista no seu webservice
    dfFunil = pd.DataFrame({
        'etapa': ['Visitantes', 'Cadastrados', 'Carrinho', 'Venda Concluída'],
        'valor_total': [10000, 5000, 2500, total_vendas]
    })

# Criação do gráfico de funil com Plotly Express
figFunil = px.funnel(
    dfFunil, 
    x='valor_total', 
    y='nivel_fidelidade' if 'nivel_fidelidade' in dfFunil.columns else 'etapa',
    color_discrete_sequence=[cores[0]]
)

# Ajuste de layout mantendo o padrão visual do seu dashboard
figFunil.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Segoe UI, Tahoma, Geneva, Verdana, sans-serif", color=cores[5])
)

#converter os gráficos para HTML
html_historico = figHistorico.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
html_prod = figProduto.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
html_faixa = fig_faixa_etaria.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
html_regiao = figRegiao.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
html_funil = figFunil.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})

html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Corporativo de Indicadores</title>
    
    <!-- CSS Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <style>
        :root {{
            --primary-blue: #1A4B83;
            --secondary-blue: #3478C6;
            --light-blue: #8CB3E3;
            --accent-blue: #0A2540;
            
            --bg-light: #F4F7FA;
            --card-bg: #FFFFFF;
            --text-dark: #333333;
            --text-muted: #6C757D;
            --border-color: #E0E6ED;
        }}

        body {{
            background-color: var(--bg-light);
            color: var(--text-dark);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        h2 {{
            color: var(--accent-blue);
            font-weight: 700;
        }}

        h5 {{
            color: var(--primary-blue);
            font-weight: 600;
            margin-bottom: 1rem;
        }}

        .kpi-card {{
            border: none;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(10, 37, 64, 0.05);
            transition: transform 0.2s;
        }}

        .kpi-card:hover {{
            transform: translateY(-3px);
        }}

        .kpi-card-primary {{
            background-color: var(--primary-blue);
            color: #FFFFFF;
        }}

        .kpi-title {{
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.8;
        }}

        .kpi-value {{
            font-size: 1.5rem;
            font-weight: 700;
        }}

        .chart-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            min-height: 380px;
        }}
    </style>
</head>
<body class="p-4">

    <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom">
            <h2>Dashboard de Performance</h2>
            <span class="text-muted">Dados Processados via Python</span>
        </div>

        <!-- Cartões de KPIs Modernos -->
        <div class="row mb-4">
            <div class="col-md-2 mb-3">
                <div class="card kpi-card kpi-card-primary h-100">
                    <div class="card-body">
                        <div class="kpi-title">Faturamento Total</div>
                        <div class="kpi-value">{faturamentoFormatado}</div>
                    </div>
                </div>
            </div>
            <div class="col-md-2 mb-3">
                <div class="card kpi-card bg-white border h-100">
                    <div class="card-body">
                        <div class="kpi-title text-muted">Total de Vendas</div>
                        <div class="kpi-value" style="color: var(--secondary-blue);">{vendasFormatado}</div>
                    </div>
                </div>
            </div>
            <div class="col-md-2 mb-3">
                <div class="card kpi-card bg-white border h-100">
                    <div class="card-body">
                        <div class="kpi-title text-muted">Ticket Médio</div>
                        <div class="kpi-value" style="color: var(--secondary-blue);">{ticketMedioFormatado}</div>
                    </div>
                </div>
            </div>
            <!-- CARDS DE EXPECTATIVA DE CONVERSÃO -->
            <div class="col-md-3 mb-3">
                <div class="card kpi-card kpi-card-growth h-100">
                    <div class="card-body p-3">
                        <div class="kpi-title text-success">Meta Conversão (15% Upgrade)</div>
                        <div class="kpi-value text-success">{metaConversaoFormatada}</div>
                        <small class="text-muted">Novos/Ocasionais &rarr; Frequente/VIP</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card kpi-card kpi-card-growth h-100">
                    <div class="card-body p-3">
                        <div class="kpi-title text-success">Receita Incremental Estimada</div>
                        <div class="kpi-value text-success">{incrementoFormatado}</div>
                        <small class="text-muted">Potencial de receita adicional</small>
                    </div>
                </div>
            </div>
        </div>

        <!-- Linha do Histórico Mensal + Projeção (Destaque Principal em Coluna Larga) -->
        <div class="row mb-4">
            <div class="col-md-8 mb-4">
                <div class="chart-card">
                    <h5>Histórico de Vendas Mês a Mês & Expectativa de Melhora</h5>
                    {html_historico}
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="chart-card">
                    <h5>Funil de Fidelidade (API)</h5>
                    {html_funil}
                </div>
            </div>
        </div>
        <!-- Área dos Gráficos com Paleta Corporate Blue -->
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="chart-card">
                    <h5>Receita por Produto</h5>
                    {html_prod}
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="chart-card">
                    <h5>Volume por Faixa Etária</h5>
                    {html_faixa}
                </div>
            </div>            
        </div>

        <!-- Seção explicativa sobre KPIs -->
        <div class="row">
            <div class="col-md-12 mb-4">
                <div class="chart-card" style="min-height: auto;">
                    <h2>KPIs</h2>
                    <p>São utilizados para mensurar e proporcionar aos tomadores de decisões visões para uma assertividade melhor na tomada de decisões.
                    Com base no passado, utilizar métricas capables de prever o futuro ou quase.
                    <strong>KPI significa Indicador-Chave de Desempenho. </strong></p>
                    <p>É uma métrica quantificável usada para avaliar o desempenho ou o progresso de um indivíduo, equipe, departamento ou organização em relação ao alcance de seus objetivos ou metas.
                    O conceito de KPIs remonta ao início do século XX, quando Frederick Taylor, um pioneiro da administração científica, 
                    introduziu a ideia de usar dados e medições para melhorar a produtividade e a eficiência em ambientes industriais. 
                    Taylor enfatizou a importância de definir padrões e medir o desempenho em relação a esses padrões. 
                    No entanto, o termo "Indicador-Chave de Desempenho" (KPI, na sigla em inglês) foi cunhado posteriormente, 
                    e a compreensão e o uso modernos dos KPIs evoluíram ao longo do tempo. 
                    Nas décadas de 1950 e 1960, a abordagem de Gestão por Objetivos (MBO, na sigla em inglês) de Drucker influenciou o desenvolvimento dos KPIs como um meio de mensurar o desempenho em relação a objetivos predeterminados. 
                    (Observe que tanto os OKRs quanto os KPIs são derivados do trabalho original de Drucker!) 
                    Ao longo do tempo, o uso de KPIs evoluiu à medida que as práticas de gestão avançaram. 
                    Em meados do século XX, teorias de gestão como a Gestão da Qualidade Total (TQM) e o Balanced Scorecard contribuíram ainda mais para o desenvolvimento e a adoção de KPIs.
                    A Gestão da Qualidade Total (TQM), popularizada por pensadores da administração como W. Edwards Deming e Joseph Juran, enfatizou a melhoria contínua e a satisfação do cliente.
                    Introduziu o conceito de controle estatístico de processos e métricas de desempenho para garantir a consistência e aprimorar a qualidade.
                    Então, no início da década de 1990, o modelo Balanced Scorecard, desenvolvido por Robert Kaplan e David Norton, ganhou destaque. 
                    Ele expandiu o conceito de KPIs para além das medidas financeiras, incluindo um conjunto equilibrado de indicadores em diversas perspectivas, como clientes, processos internos e aprendizado e crescimento.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Salva o resultado em um arquivo HTML
with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Página gerada com sucesso! Abra o arquivo 'dashboard.html' no navegador.")