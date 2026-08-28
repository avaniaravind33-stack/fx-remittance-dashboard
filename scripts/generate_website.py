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

    # Load reconciliation data
    recon_df = pd.read_csv('data/reconciliation_records.csv')
    recon_df['Recon Date'] = pd.to_datetime(recon_df['Recon Date'])

    # Load query data
    query_df = pd.read_csv('data/query_management.csv')
    query_df['Query Date'] = pd.to_datetime(query_df['Query Date'])

    return df, recon_df, query_df

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

def create_reconciliation_status(recon_df):
    """Create reconciliation status breakdown"""
    status_data = recon_df['Status'].value_counts()
    colors = {'Matched': '#70AD47', 'Unmatched': '#FFC000', 'Duplicate': '#C00000'}

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
        title="Reconciliation Status",
        xaxis_title="Status",
        yaxis_title="Count",
        height=400,
    )
    return fig

def create_issue_breakdown(recon_df):
    """Create issue type breakdown"""
    unmatched = recon_df[recon_df['Status'] != 'Matched']
    issue_data = unmatched['Issue Type'].value_counts()

    fig = go.Figure(data=[
        go.Bar(
            x=issue_data.values,
            y=issue_data.index,
            orientation='h',
            marker=dict(color='#FFC000'),
            text=issue_data.values,
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="Reconciliation Issues Breakdown",
        xaxis_title="Count",
        yaxis_title="Issue Type",
        height=400,
    )
    return fig

def create_query_status(query_df):
    """Create query status breakdown"""
    status_data = query_df['Status'].value_counts()
    colors = {'Resolved': '#70AD47', 'Closed': '#3b82f6', 'In Progress': '#FFC000',
              'Escalated': '#C00000', 'Pending': '#94a3b8'}

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
        title="Query Management Status",
        xaxis_title="Status",
        yaxis_title="Count",
        height=400,
    )
    return fig

def create_query_type_breakdown(query_df):
    """Create query type breakdown"""
    type_data = query_df['Query Type'].value_counts().head(8)

    fig = go.Figure(data=[
        go.Bar(
            x=type_data.values,
            y=type_data.index,
            orientation='h',
            marker=dict(color='#3b82f6'),
            text=type_data.values,
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="Top Query Types",
        xaxis_title="Count",
        yaxis_title="Query Type",
        height=400,
    )
    return fig

def create_query_resolution_time(query_df):
    """Create query resolution time trend"""
    resolution_by_type = query_df.groupby('Query Type')['Days to Resolve'].mean().sort_values(ascending=False).head(8)

    fig = go.Figure(data=[
        go.Bar(
            x=resolution_by_type.index,
            y=resolution_by_type.values,
            marker=dict(color='#10b981'),
            text=[f'{v:.1f}d' for v in resolution_by_type.values],
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="Average Resolution Time by Query Type",
        xaxis_title="Query Type",
        yaxis_title="Days to Resolve",
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
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
                min-height: 100vh;
                padding: 30px 20px;
                color: #e2e8f0;
            }}

            .container {{
                max-width: 1700px;
                margin: 0 auto;
            }}

            .header {{
                background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 50%, #0c4a6e 100%);
                color: white;
                padding: 60px 40px;
                border-radius: 16px;
                margin-bottom: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3), 0 0 60px rgba(30, 64, 175, 0.2);
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                right: -10%;
                width: 500px;
                height: 500px;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%);
                border-radius: 50%;
            }}

            .header h1 {{
                font-size: 3em;
                margin-bottom: 15px;
                font-weight: 800;
                letter-spacing: -1px;
                position: relative;
                z-index: 1;
            }}

            .header p {{
                font-size: 1.2em;
                opacity: 0.95;
                position: relative;
                z-index: 1;
                font-weight: 300;
            }}

            .reporting-date {{
                font-size: 0.95em;
                opacity: 0.8;
                margin-top: 15px;
                position: relative;
                z-index: 1;
                font-weight: 400;
            }}

            .kpi-section {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 25px;
                margin-bottom: 45px;
            }}

            .kpi-card {{
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                padding: 30px;
                border-radius: 12px;
                border: 1px solid #334155;
                text-align: center;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }}

            .kpi-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                transition: left 0.5s;
            }}

            .kpi-card:hover::before {{
                left: 100%;
            }}

            .kpi-card:hover {{
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 15px 40px rgba(30, 64, 175, 0.2), 0 0 30px rgba(59, 130, 246, 0.1);
                border-color: #3b82f6;
            }}

            .kpi-label {{
                font-size: 0.85em;
                color: #94a3b8;
                margin-bottom: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            .kpi-value {{
                font-size: 2.2em;
                font-weight: 800;
                color: #3b82f6;
                margin-bottom: 5px;
            }}

            .kpi-value.success {{
                color: #10b981;
            }}

            .kpi-value.warning {{
                color: #f59e0b;
            }}

            .kpi-value.danger {{
                color: #ef4444;
            }}

            .charts-section {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 35px;
                margin-bottom: 40px;
            }}

            .chart-container {{
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                padding: 30px;
                border-radius: 12px;
                border: 1px solid #334155;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                transition: all 0.3s ease;
            }}

            .chart-container:hover {{
                border-color: #3b82f6;
                box-shadow: 0 15px 40px rgba(30, 64, 175, 0.2);
            }}

            .chart-title {{
                font-size: 1.3em;
                font-weight: 700;
                color: #e2e8f0;
                margin-bottom: 20px;
                padding-bottom: 12px;
                border-bottom: 2px solid #334155;
            }}

            .full-width {{
                grid-column: 1 / -1;
            }}

            footer {{
                text-align: center;
                color: #94a3b8;
                margin-top: 60px;
                padding: 30px;
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border-radius: 12px;
                border: 1px solid #334155;
                font-size: 0.95em;
            }}

            footer p {{
                margin: 8px 0;
            }}

            @media (max-width: 768px) {{
                .header {{
                    padding: 40px 25px;
                }}

                .header h1 {{
                    font-size: 2em;
                }}

                .charts-section {{
                    grid-template-columns: 1fr;
                    gap: 25px;
                }}

                .kpi-section {{
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                }}

                .kpi-card {{
                    padding: 20px;
                }}

                .kpi-value {{
                    font-size: 1.8em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 HDFC FX Remittance Operations</h1>
                <p>Real-time Analytics Dashboard</p>
                <div class="reporting-date">Last updated {datetime.now().strftime('%B %d, %Y • %H:%M UTC')}</div>
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
                    <div class="kpi-label">Reconciliation Match Rate</div>
                    <div class="kpi-value success">{kpis['matched_rate']:.1f}%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Queries Resolved</div>
                    <div class="kpi-value">{kpis['resolved_queries']}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Open Queries</div>
                    <div class="kpi-value warning">{kpis['open_queries']}</div>
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

            <div class="charts-section" style="margin-top: 50px; border-top: 2px solid #334155; padding-top: 40px;">
                <div class="chart-container full-width">
                    <div style="text-align: center; font-size: 1.4em; font-weight: 700; color: #e2e8f0; margin-bottom: 30px;">
                        📋 RECONCILIATION & QUERY MANAGEMENT
                    </div>
                </div>
                <div class="chart-container">
                    <div id="recon-status"></div>
                </div>
                <div class="chart-container">
                    <div id="issue-breakdown"></div>
                </div>
                <div class="chart-container">
                    <div id="query-status"></div>
                </div>
                <div class="chart-container">
                    <div id="query-types"></div>
                </div>
                <div class="chart-container full-width">
                    <div id="query-time"></div>
                </div>
            </div>

            <footer>
                <p><strong>HDFC Bank FX Remittance Operations Dashboard</strong></p>
                <p>International Remittance Analytics | Data source: Simulated transaction dataset</p>
            </footer>
        </div>
    </body>
    </html>
    """

    return html_content

def main():
    print("Loading data...")
    df, recon_df, query_df = load_data()

    print("Computing KPIs...")
    kpis = create_kpi_cards(df)

    # Add reconciliation and query KPIs
    kpis['matched_rate'] = (len(recon_df[recon_df['Status'] == 'Matched']) / len(recon_df) * 100)
    kpis['open_queries'] = len(query_df[query_df['Status'].isin(['Pending', 'In Progress'])])
    kpis['resolved_queries'] = len(query_df[query_df['Status'] == 'Resolved'])
    kpis['escalated_queries'] = len(query_df[query_df['Status'] == 'Escalated'])
    kpis['avg_resolution_time'] = query_df['Days to Resolve'].mean()

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
        'recon_status': create_reconciliation_status(recon_df),
        'issue_breakdown': create_issue_breakdown(recon_df),
        'query_status': create_query_status(query_df),
        'query_types': create_query_type_breakdown(query_df),
        'query_time': create_query_resolution_time(query_df),
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
        'recon-status': charts['recon_status'].to_html(include_plotlyjs=False, div_id='recon-status'),
        'issue-breakdown': charts['issue_breakdown'].to_html(include_plotlyjs=False, div_id='issue-breakdown'),
        'query-status': charts['query_status'].to_html(include_plotlyjs=False, div_id='query-status'),
        'query-types': charts['query_types'].to_html(include_plotlyjs=False, div_id='query-types'),
        'query-time': charts['query_time'].to_html(include_plotlyjs=False, div_id='query-time'),
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
