import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from window_functions import calculate_windowed_returns, calculate_windowed_annualized_returns

def plot_rolling_excess_returns(df, DXY_LEVERAGE=5):

    colors = px.colors.qualitative.Plotly

    # Assuming df is your DataFrame with the excess returns data
    # Make sure df is sorted by date
    df = df.sort_index()
    DXY_LEVERAGE=5

    colors = px.colors.qualitative.Plotly
    df['ER_DXY_d']=df['ER_DXY_d']/DXY_LEVERAGE

    # List of assets and windows
    assets = ['SPX', '10Y', 'DXY']
    windows = [63, 126, 252, 504]  # 3 months, 6 months, 1 year, 2 years
    window_labels = ['3m', '6m', '1y', '2y']

    # Calculate rolling IRR for different windows
    for asset in assets:
        for window in windows:
            col_name = f'ROLL_{asset}_IRR_{window}d'
            df[col_name] = calculate_windowed_annualized_returns(df[f'ER_{asset}_d'], window=window)

    # Create the plot
    fig = go.Figure()

    # Add traces for each asset
    for i, asset in enumerate(assets):
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=df[f'ROLL_{asset}_IRR_252d'],  # Default to 1-year window
                name=f"{asset} IRR",
                line=dict(width=2, color=colors[i])
            )
        )

    # Customize the layout
    fig.update_layout(
        title={
            'text': "Rolling Excess Returns (1 year)",  # Default title
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24, color='#3b3734')
        },
        yaxis = dict(
            tickformat=".2%",
            gridcolor='rgba(189, 195, 199, 0.5)',
            zerolinecolor='rgba(189, 195, 199, 0.5)',
            range=[None, None],
            fixedrange=False
        ),
        xaxis_title="Date",
        yaxis_title="IRR",
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='rgba(0,0,0,0)'
        ),
        hovermode="x unified",
        plot_bgcolor='#f9f9f9',
        paper_bgcolor='#f9f9f9',
        font=dict(family="Roboto, Arial, sans-serif", size=14, color='#34495e')
    )

    # Update axes
    fig.update_yaxes(
        tickformat=".2%",
        gridcolor='rgba(189, 195, 199, 0.5)',
        zerolinecolor='rgba(189, 195, 199, 0.5)',
        autorange=True
    )
    fig.update_xaxes(
        gridcolor='rgba(189, 195, 199, 0.5)',
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=2, label="2y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(step="all")
            ]),
            font=dict(color='#34495e'),
            bgcolor='rgba(52, 152, 219, 0.2)',
            activecolor='#3498db'
        )
    )

    # Add dropdown for window selection
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(
                        args=[{"y": [df[f'ROLL_{asset}_IRR_{window}d'] for asset in assets]},
                            {"title": f"Rolling Excess Returns ({label})"}],
                        label=label,
                        method="update"
                    ) for window, label in zip(windows, window_labels)
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.9,
                xanchor="left",
                y=1.15,
                yanchor="top"
            ),
        ]
    )

    return fig


def plot_yield_comparison(df):

    # Assuming df is your DataFrame with the yield data
    # Make sure df is sorted by date
    df = df.sort_index()

    # Apply 30-day rolling average for smoothing
    df['YIELD_10Y_smooth'] = df['YIELD_10Y_y'].rolling(window=14).mean()
    df['YIELD_FFR_smooth'] = df['YIELD_FFR_y'].rolling(window=14).mean()

    # Calculate the difference
    df['yield_diff'] = df['YIELD_FFR_smooth'] - df['YIELD_10Y_smooth']

    # Create the plot
    fig = go.Figure()

    # Add 10Y Treasury Yield
    fig.add_trace(
    go.Scatter(x=df.index, y=df['YIELD_10Y_smooth'], name="10Y Treasury Yield",
                line=dict(color='#103766', width=2))  
    )

    # Add Federal Funds Rate Yield
    fig.add_trace(
    go.Scatter(x=df.index, y=df['YIELD_FFR_smooth'], name="Federal Funds Rate",
                line=dict(color='#242c34', width=1)) 
    )

    df['mask'] = df['YIELD_FFR_smooth'] > df['YIELD_10Y_smooth']

    # Delta
    fig.add_trace(
    go.Scatter(
        x=df.index,
        y=np.where(df['mask'], df['YIELD_10Y_smooth'], df['YIELD_FFR_smooth']),
        fill='tonexty',
        fillcolor='#e53935',  
        line=dict(width=0),
        name="Yield Inversion",
        hoverinfo='skip',
        fillpattern=dict(
            shape="x",
            size=1.3,
            fgcolor="#e53935",  # Darker purple
            bgcolor="white"
        )
    )
    )

    # Customize the layout
    fig.update_layout(
    title={
        'text': "10-Year Treasury Yield vs Federal Funds Rate",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(size=24, color='#3b3734')  # Dark blue-gray
    },
    yaxis = dict(
        ticksuffix="%",
        gridcolor='rgba(189, 195, 199, 0.5)',  # Light gray
        zerolinecolor='rgba(189, 195, 199, 0.5)',  # Light gray
        range=[None, None],  # Automatically adjust y-axis
        fixedrange=False  # Allow y-axis to be adjustable
    ),
    xaxis_title="Date",
    yaxis_title="Yield (%)",
    legend=dict(
        x=0.01, 
        y=0.99, 
        bgcolor='rgba(255, 255, 255, 0.5)',
        bordercolor='rgba(0,0,0,0)'
    ),
    hovermode="x unified",
    plot_bgcolor='#f9f9f9',  # Light gray background
    paper_bgcolor='#f9f9f9',  # Light gray background
    font=dict(family="Roboto, Arial, sans-serif", size=14, color='#34495e')  # Modern font
    )

    # Update axes

    fig.update_yaxes(
    ticksuffix="%", 
    gridcolor='rgba(189, 195, 199, 0.5)',  # Light gray
    zerolinecolor='rgba(189, 195, 199, 0.5)',  # Light gray
    autorange=True

    )
    fig.update_xaxes(
    gridcolor='rgba(189, 195, 199, 0.5)',  # Light gray
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=2, label="2y", step="year", stepmode="backward"),
            dict(count=5, label="5y", step="year", stepmode="backward"),
            dict(count=10, label="10y", step="year", stepmode="backward"),
            dict(step="all")
        ]),
        font=dict(color='#34495e'),  # Dark blue-gray
        bgcolor='rgba(52, 152, 219, 0.2)',  # Light blue
        activecolor='#3498db'  # Bright blue
    )
    )

    return fig

def plot_stock_bond_correlation(df):
    # Assuming df is your DataFrame with the original excess return data and a DateTimeIndex

    # Calculate yearly returns
    df['Year'] = df.index.year
    yearly_returns = df.groupby('Year').agg({
        'ER_SPX_d': lambda x: (1 + x).prod() - 1,
        'ER_10Y_d': lambda x: (1 + x).prod() - 1
    }) * 100  # Convert to percentage

    # Create the grouped bar chart
    fig = go.Figure()

    # Add 10Y Treasury bars
    fig.add_trace(go.Bar(
        x=yearly_returns.index,
        y=yearly_returns['ER_10Y_d'],
        name='10Y Treasury',
        hovertemplate='Year: %{x}<br>10Y Treasury: %{y:.2f}%<extra></extra>',
        marker=dict(
            color=['#FF9999' if y < 0 else '#FF0000' for y in yearly_returns['ER_10Y_d']],
            line=dict(
                color=['#FF3333' if y < 0 else '#FF0000' for y in yearly_returns['ER_10Y_d']],
                width=[2 if y < 0 else 0 for y in yearly_returns['ER_10Y_d']]
            ),
        )
    ))

    # Add SPX bars
    fig.add_trace(go.Bar(
        x=yearly_returns.index,
        y=yearly_returns['ER_SPX_d'],
        name='S&P500',
        hovertemplate='Year: %{x}<br>S&P500: %{y:.2f}%<extra></extra>',
        marker=dict(
            color=['#9999FF' if y < 0 else '#0000FF' for y in yearly_returns['ER_SPX_d']],
            line=dict(
                color=['#3333FF' if y < 0 else '#0000FF' for y in yearly_returns['ER_SPX_d']],
                width=[2 if y < 0 else 0 for y in yearly_returns['ER_SPX_d']]
            ),
        )
    ))

    # Update the layout
    fig.update_layout(
        title='Yearly Excess Returns: SPX vs 10Y Treasury',
        xaxis_title='Year',
        yaxis_title='Excess Returns (%)',
        yaxis=dict(tickformat='.2f', ticksuffix='%'),  # Format y-axis ticks as percentages
        barmode='group',
        bargap=0.5,  # Add gap between groups
        hovermode='closest',
        xaxis=dict(
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(count=10, label="10y", step="year", stepmode="backward"),
                    dict(count=20, label="20y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        ),
        # Change background color every year
        shapes=[dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=year - 0.5,  # Start slightly before the year to cover full width
            y0=0,
            x1=year + 0.5,  # End slightly after the year to cover full width
            y1=1,
            fillcolor="lightgray" if i % 2 == 0 else "white",
            opacity=0.2,
            layer="below",
            line_width=0,
        ) for i, year in enumerate(yearly_returns.index)],
        # Add toggle switches
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                x=0.57,
                y=1.2,
                buttons=list([
                    dict(label="All",
                        method="update",
                        args=[{"y": [yearly_returns['ER_10Y_d'], yearly_returns['ER_SPX_d']]},
                            {"title": "Yearly Excess Returns: SPX vs 10Y Treasury"}]),
                    dict(label="Positive Only",
                        method="update",
                        args=[{"y": [[y if y >= 0 else None for y in yearly_returns['ER_10Y_d']],
                                    [y if y >= 0 else None for y in yearly_returns['ER_SPX_d']]]},
                            {"title": "Yearly Excess Returns: SPX vs 10Y Treasury (Positive Only)"}]),
                    dict(label="Negative Only",
                        method="update",
                        args=[{"y": [[y if y < 0 else None for y in yearly_returns['ER_10Y_d']],
                                    [y if y < 0 else None for y in yearly_returns['ER_SPX_d']]]},
                            {"title": "Yearly Excess Returns: SPX vs 10Y Treasury (Negative Only)"}]),
                ]),
            )
        ]
    )

    # Show the plot
    return fig