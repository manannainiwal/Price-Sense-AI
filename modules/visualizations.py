"""
Visualization functions for Price Sense AI
Creates charts and graphs using Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


def create_recommendation_card(recommendation: dict, financial: dict) -> dict:
    """Create styled recommendation card data"""
    decision = recommendation['decision']
    
    colors = {
        'Strong Yes': '#10b981',
        'Maybe': '#f59e0b',
        'No': '#ef4444'
    }
    
    icons = {
        'Strong Yes': '✅',
        'Maybe': '⚠️',
        'No': '❌'
    }
    
    return {
        'decision': decision,
        'color': colors.get(decision, '#64748b'),
        'icon': icons.get(decision, '❓'),
        'reasoning': recommendation['reasoning']
    }


def create_financial_waterfall(financial: dict, product_name: str):
    """Create waterfall chart showing financial breakdown"""
    
    fig = go.Figure(go.Waterfall(
        name="Financial Impact",
        orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["Baseline<br>Margin", "Incremental<br>Margin", "Cannibalization<br>Cost", "Net<br>Profit"],
        textposition="outside",
        text=[f"${financial['baseline_margin']:,.0f}", 
              f"+${financial['incremental_margin']:,.0f}",
              f"-${financial['cannibalization_cost']:,.0f}",
              f"${financial['net_profit']:,.0f}"],
        y=[financial['baseline_margin'], 
           financial['incremental_margin'], 
           -financial['cannibalization_cost'],
           financial['net_profit']],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#3b82f6"}}
    ))
    
    fig.update_layout(
        title=f"Financial Waterfall - {product_name}",
        showlegend=False,
        height=400,
        yaxis_title="Margin ($)"
    )
    
    return fig


def create_lift_comparison_chart(lift: dict):
    """Create bar chart comparing baseline vs promoted units"""
    
    fig = go.Figure(data=[
        go.Bar(name='Baseline Units', x=['Units'], y=[lift['baseline_units']], 
               marker_color='#94a3b8', text=f"{lift['baseline_units']:,}", textposition='auto'),
        go.Bar(name='Incremental Units', x=['Units'], y=[lift['incremental_units']], 
               marker_color='#10b981', text=f"+{lift['incremental_units']:,}", textposition='auto'),
    ])
    
    fig.update_layout(
        title=f"Sales Lift: {lift['lift_pct']}%",
        barmode='stack',
        showlegend=True,
        height=400,
        yaxis_title="Units Sold"
    )
    
    return fig


def create_risk_gauge(risk_score: int):
    """Create gauge chart for risk score"""
    
    # Determine risk level and color
    if risk_score < 30:
        risk_level = "Low"
        color = "#10b981"
    elif risk_score < 70:
        risk_level = "Medium"
        color = "#f59e0b"
    else:
        risk_level = "High"
        color = "#ef4444"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Risk Level: {risk_level}"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 30], 'color': "#d1fae5"},
                {'range': [30, 70], 'color': "#fef3c7"},
                {'range': [70, 100], 'color': "#fee2e2"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def create_cannibalization_chart(cannibalization: dict):
    """Create chart showing cannibalization impact"""
    
    if not cannibalization['affected_products']:
        return None
    
    products = cannibalization['affected_products']
    
    df = pd.DataFrame(products)
    
    fig = px.bar(
        df,
        x='margin_lost',
        y='product_name',
        orientation='h',
        title=f"Cannibalization Impact: ${cannibalization['total_margin_lost']:,.0f}",
        labels={'margin_lost': 'Margin Lost ($)', 'product_name': 'Product'},
        color='margin_lost',
        color_continuous_scale=['#fee2e2', '#ef4444']
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig


def create_historical_sales_chart(df: pd.DataFrame, product_name: str):
    """Create line chart of historical sales"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['units_sold'],
        mode='lines+markers',
        name='Units Sold',
        line=dict(color='#3b82f6', width=2),
        marker=dict(size=6)
    ))
    
    # Add promotion markers if available
    if 'was_promoted' in df.columns:
        promo_df = df[df['was_promoted'] == True]
        if not promo_df.empty:
            fig.add_trace(go.Scatter(
                x=promo_df['date'],
                y=promo_df['units_sold'],
                mode='markers',
                name='Promotion Days',
                marker=dict(size=12, color='#10b981', symbol='star')
            ))
    
    fig.update_layout(
        title=f"Historical Sales - {product_name}",
        xaxis_title="Date",
        yaxis_title="Units Sold",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_scenario_comparison(results: list):
    """Create heatmap comparing multiple scenarios"""
    
    # Extract data for heatmap
    discounts = sorted(set([r['discount_pct'] for r in results]))
    durations = sorted(set([r['duration_days'] for r in results]))
    
    # Create profit matrix
    profit_matrix = []
    for duration in durations:
        row = []
        for discount in discounts:
            result = next((r for r in results 
                          if r['discount_pct'] == discount and r['duration_days'] == duration), None)
            if result:
                row.append(result['financial']['net_profit'])
            else:
                row.append(0)
        profit_matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=profit_matrix,
        x=[f"{d}%" for d in discounts],
        y=[f"{d} days" for d in durations],
        colorscale='RdYlGn',
        text=[[f"${val:,.0f}" for val in row] for row in profit_matrix],
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Net Profit ($)")
    ))
    
    fig.update_layout(
        title="Scenario Comparison Heatmap",
        xaxis_title="Discount %",
        yaxis_title="Duration",
        height=400
    )
    
    return fig
