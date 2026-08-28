"""
FX Remittance Dashboard - Static Website Generator
Generates interactive Plotly charts and exports as static HTML
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime

def load_data():
    """Load and prepare transaction data"""
    df = pd.read_csv('data/remittance_transactions.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')
    return df

def create_kpi_cards(df):
    """Create KPI metrics"""
    return {
        'total_transactions': len(df),
        'total_inr_value': df['INR Amount'].sum(),
        'inward_count': len(df[df['Direction'] == 'Inward']),
        'outward_count': len(df[df['Direction'] == 'Outward']),
        'completed_count': len(df[df['Status'] == 'Completed']),
        'completed_pct': (len(df[df['Status'] == 'Completed']) / len(df) * 100),
        'exception_rate': (len(df[df['Exception Flag'] == 'Yes']) / len(df) * 100),
        'avg_processing_time': df['Processing Time (Hours)'].mean(),
        'sla_breach_count': len(df[df['SLA Breach'] == 'Yes']),
        'failed_count': len(df[df['Status'] == 'Failed']),
    }

def create_volume_chart(df):
    """Create transaction volume by corridor"""
    corridor_data = df['Corridor'].value_counts().head(8)
    fig = go.Figure(data=[
        go.Bar(
            x=corridor_data.index,
            y=corridor_data.values,
            marker=dict(color='#0070C0'),
            text=corridor_data.values,
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="Transaction Volume by Corridor",
        xaxis_title="Corridor",
        yaxis_title="Number of Transactions",
        hovermode='x unified',
        height=400,
    )
    return fig

def create_currency_pie(df):
    """Create currency distribution pie chart"""
    # Use 'To Currency' for proper currency split
    currency_data = df['To Currency'].value_counts()
    fig = go.Figure(data=[
        go.Pie(
            labels=currency_data.index,
            values=currency_data.values,
            hole=0.3,
        )
    ])
    fig.update_layout(
        title="Currency Distribution",
        height=400,
    )
    return fig

def create_direction_split(df):
    """Create inward/outward split"""
    direction_data = df['Direction'].value_counts()
    colors = ['#0070C0', '#C00000']
    fig = go.Figure(data=[
        go.Bar(
            x=direction_data.index,
            y=direction_data.values,
            marker=dict(color=colors),
            text=direction_data.values,
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="Inward vs Outward Transactions",
        xaxis_title="Direction",
        yaxis_title="Count",
        height=400,
    )
    return fig

def create_status_breakdown(df):
    """Create status distribution"""
    status_data = df['Status'].value_counts()
    colors = {'Completed': '#70AD47', 'Pending': '#FFC000', 'Failed': '#C00000', 'On-hold': '#FF6B6B'}
    fig = go.Figure(data=[
        go.Bar(
            x=status_data.index,
            y=status_data.values,
            marker=dict(color=[colors.get(s, '#999') for s in status_data.index]),
            text=status_data.values,
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="Transaction Status Breakdown",
        xaxis_title="Status",
        yaxis_title="Count",
        height=400,
    )
    return fig

def create_value_by_corridor(df):
    """Create INR value by corridor"""
    corridor_value = df.groupby('Corridor')['INR Amount'].sum().sort_values(ascending=False).head(8)
    fig = go.Figure(data=[
        go.Bar(
            x=corridor_value.index,
            y=corridor_value.values,
            marker=dict(color='#70AD47'),
            text=[f'₹{v/1e5:.1f}L' for v in corridor_value.values],
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="Total INR Value by Corridor",
        xaxis_title="Corridor",
        yaxis_title="INR Amount",
        hovermode='x unified',
        height=400,
    )
    return fig

def create_daily_trend(df):
    """Create daily transaction trend"""
    daily_data = df.groupby(df['Date'].dt.date).size()
    fig = go.Figure(data=[
        go.Scatter(
            x=daily_data.index,
            y=daily_data.values,
            mode='lines+markers',
            line=dict(color='#0070C0', width=2),
            fill='tozeroy',
            hovertemplate='<b>%{x}</b><br>Transactions: %{y}<extra></extra>'
        )
    ])
    fig.update_layout(
        title="Daily Transaction Trend",
        xaxis_title="Date",
        yaxis_title="Number of Transactions",
        height=400,
    )
    return fig

def create_processing_time_distribution(df):
    """Create processing time histogram"""
    fig = go.Figure(data=[
        go.Histogram(
            x=df['Processing Time (Hours)'],
            nbinsx=30,
            marker=dict(color='#0070C0'),
        )
    ])
    fig.update_layout(
        title="Processing Time Distribution",
        xaxis_title="Hours",
        yaxis_title="Number of Transactions",
        height=400,
    )
    return fig

def create_channel_performance(df):
    """Create channel performance chart"""
    channel_stats = df.groupby('Channel').agg({
        'Processing Time (Hours)': 'mean',
        'Transaction ID': 'count'
    }).reset_index()
    channel_stats.columns = ['Channel', 'Avg Processing Time', 'Count']

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=channel_stats['Channel'], y=channel_stats['Count'], name='Count', marker=dict(color='#0070C0')),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=channel_stats['Channel'], y=channel_stats['Avg Processing Time'], name='Avg Time (hrs)',
                   mode='lines+markers', line=dict(color='#C00000', width=3)),
        secondary_y=True,
    )
    fig.update_layout(
        title="Channel Performance Analysis",
        xaxis_title="Channel",
        hovermode='x unified',
        height=400,
    )
    fig.update_yaxes(title_text="Transaction Count", secondary_y=False)
    fig.update_yaxes(title_text="Avg Processing Time (Hours)", secondary_y=True)
    return fig

def create_exception_breakdown(df):
    """Create exception reasons breakdown"""
    exceptions_df = df[df['Exception Flag'] == 'Yes']
    if len(exceptions_df) > 0:
        exception_reasons = exceptions_df['Exception Reason'].value_counts()
        fig = go.Figure(data=[
            go.Bar(
                x=exception_reasons.values,
                y=exception_reasons.index,
                orientation='h',
                marker=dict(color='#C00000'),
                text=exception_reasons.values,
                textposition='auto',
            )
        ])
        fig.update_layout(
            title="Exception Reasons Breakdown",
            xaxis_title="Count",
            yaxis_title="Reason",
            height=400,
        )
    else:
        fig = go.Figure()
        fig.add_annotation(text="No exceptions in dataset")
    return fig

def create_sla_breaches_by_corridor(df):
    """Create SLA breach analysis by corridor"""
    sla_data = df.groupby('Corridor').apply(
        lambda x: (len(x[x['SLA Breach'] == 'Yes']) / len(x) * 100) if len(x) > 0 else 0
    ).sort_values(ascending=False).head(8)

    fig = go.Figure(data=[
        go.Bar(
            x=sla_data.index,
            y=sla_data.values,
            marker=dict(color=['#C00000' if v > 1 else '#70AD47' for v in sla_data.values]),
            text=[f'{v:.1f}%' for v in sla_data.values],
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="SLA Breach Rate by Corridor (%)",
        xaxis_title="Corridor",
        yaxis_title="SLA Breach %",
        height=400,
    )
    return fig

def generate_html_dashboard(df, kpis):
    """Generate complete HTML dashboard"""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HDFC FX Remittance Operations Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 20px;
            }}

            .container {{
                max-width: 1600px;
                margin: 0 auto;
            }}

            .header {{
                background: linear-gradient(135deg, #203A5F 0%, #366092 100%);
                color: white;
                padding: 40px 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}

            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 700;
            }}

            .header p {{
                font-size: 1.1em;
                opacity: 0.9;
            }}

            .reporting-date {{
                font-size: 0.9em;
                opacity: 0.8;
                margin-top: 10px;
            }}

            .kpi-section {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}

            .kpi-card {{
                background: white;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s, box-shadow 0.3s;
            }}

            .kpi-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}

            .kpi-label {{
                font-size: 0.9em;
                color: #666;
                margin-bottom: 10px;
                font-weight: 500;
                text-transform: uppercase;
            }}

            .kpi-value {{
                font-size: 2em;
                font-weight: 700;
                color: #203A5F;
            }}

            .kpi-value.success {{
                color: #70AD47;
            }}

            .kpi-value.warning {{
                color: #FFC000;
            }}

            .kpi-value.danger {{
                color: #C00000;
            }}

            .charts-section {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 30px;
                margin-bottom: 30px;
            }}

            .chart-container {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}

            .chart-title {{
                font-size: 1.2em;
                font-weight: 600;
                color: #203A5F;
                margin-bottom: 15px;
            }}

            .full-width {{
                grid-column: 1 / -1;
            }}

            footer {{
                text-align: center;
                color: #666;
                margin-top: 50px;
                padding: 20px;
                background: white;
                border-radius: 8px;
            }}

            @media (max-width: 768px) {{
                .header h1 {{
                    font-size: 1.8em;
                }}

                .charts-section {{
                    grid-template-columns: 1fr;
                }}

                .kpi-section {{
                    grid-template-columns: repeat(2, 1fr);
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 HDFC FX Remittance Operations Dashboard</h1>
                <p>Real-time analytics for international remittance processing</p>
                <div class="reporting-date">Dashboard generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</div>
            </div>

            <div class="kpi-section">
                <div class="kpi-card">
                    <div class="kpi-label">Total Transactions</div>
                    <div class="kpi-value">{kpis['total_transactions']:,}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Total Value (INR)</div>
                    <div class="kpi-value">₹{kpis['total_inr_value']/1e7:.1f}Cr</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Completion Rate</div>
                    <div class="kpi-value success">{kpis['completed_pct']:.1f}%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Exception Rate</div>
                    <div class="kpi-value warning">{kpis['exception_rate']:.2f}%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Avg Processing Time</div>
                    <div class="kpi-value">{kpis['avg_processing_time']:.1f}h</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">SLA Breaches</div>
                    <div class="kpi-value danger">{kpis['sla_breach_count']}</div>
                </div>
            </div>

            <div class="charts-section">
                <div class="chart-container">
                    <div id="volume-chart"></div>
                </div>
                <div class="chart-container">
                    <div id="currency-chart"></div>
                </div>
                <div class="chart-container">
                    <div id="direction-chart"></div>
                </div>
                <div class="chart-container">
                    <div id="status-chart"></div>
                </div>
                <div class="chart-container">
                    <div id="value-chart"></div>
                </div>
                <div class="chart-container">
                    <div id="processing-dist"></div>
                </div>
                <div class="chart-container full-width">
                    <div id="daily-trend"></div>
                </div>
                <div class="chart-container full-width">
                    <div id="channel-perf"></div>
                </div>
                <div class="chart-container">
                    <div id="exception-chart"></div>
                </div>
                <div class="chart-container">
                    <div id="sla-chart"></div>
                </div>
            </div>

            <footer>
                <p><strong>HDFC Bank FX Remittance Operations & MIS Dashboard</strong></p>
                <p>Data source: Simulated transaction dataset | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </footer>
        </div>
    </body>
    </html>
    """

    return html_content

def main():
    print("Loading data...")
    df = load_data()

    print("Computing KPIs...")
    kpis = create_kpi_cards(df)

    print("Creating charts...")
    charts = {
        'volume': create_volume_chart(df),
        'currency': create_currency_pie(df),
        'direction': create_direction_split(df),
        'status': create_status_breakdown(df),
        'value': create_value_by_corridor(df),
        'processing_dist': create_processing_time_distribution(df),
        'daily_trend': create_daily_trend(df),
        'channel_perf': create_channel_performance(df),
        'exception': create_exception_breakdown(df),
        'sla': create_sla_breaches_by_corridor(df),
    }

    print("Generating HTML...")
    html = generate_html_dashboard(df, kpis)

    # Add Plotly chart scripts to HTML
    chart_divs = {
        'volume-chart': charts['volume'].to_html(include_plotlyjs=False, div_id='volume-chart'),
        'currency-chart': charts['currency'].to_html(include_plotlyjs=False, div_id='currency-chart'),
        'direction-chart': charts['direction'].to_html(include_plotlyjs=False, div_id='direction-chart'),
        'status-chart': charts['status'].to_html(include_plotlyjs=False, div_id='status-chart'),
        'value-chart': charts['value'].to_html(include_plotlyjs=False, div_id='value-chart'),
        'processing-dist': charts['processing_dist'].to_html(include_plotlyjs=False, div_id='processing-dist'),
        'daily-trend': charts['daily_trend'].to_html(include_plotlyjs=False, div_id='daily-trend'),
        'channel-perf': charts['channel_perf'].to_html(include_plotlyjs=False, div_id='channel-perf'),
        'exception-chart': charts['exception'].to_html(include_plotlyjs=False, div_id='exception-chart'),
        'sla-chart': charts['sla'].to_html(include_plotlyjs=False, div_id='sla-chart'),
    }

    # Extract just the script portion from each chart
    for chart_id, chart_html in chart_divs.items():
        # Extract Plotly data and layout
        start = chart_html.find('Plotly.newPlot(')
        end = chart_html.rfind(');') + 2
        if start != -1 and end != 0:
            script_content = chart_html[start:end]
            chart_divs[chart_id] = f"<script>{script_content}</script>"

    # Insert charts into HTML
    final_html = html
    for chart_id, chart_script in chart_divs.items():
        final_html = final_html.replace(f'<div id="{chart_id}"></div>', f'<div id="{chart_id}"></div>\n{chart_script}')

    # Save to file
    output_path = 'website/index.html'
    with open(output_path, 'w') as f:
        f.write(final_html)

    print(f"✓ Website dashboard saved to {output_path}")

if __name__ == '__main__':
    main()
