import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from window_functions import calculate_windowed_returns, calculate_windowed_annualized_returns


def aggregate_daily_returns_to_annualized_returns(df, lookback_window=252, num_months=1):

    #WINDOW YEARLY RETURNS
    returns_to_aggregate=['RET_SPX_d', 'RET_10Y_d', 'RET_DXY_d', 'RET_FFR_d', 'RET_FXR_d', 'RET_SHORT_SPX_d', 'RET_SHORT_10Y_d', 'RET_SHORT_DXY_d', 'ER_SPX_d', 'ER_10Y_d', 'ER_DXY_d',
        'ER_SHORT_SPX_d', 'ER_SHORT_10Y_d', 'ER_SHORT_DXY_d','ER_RP_Portfolio_LONG', 'ER_RP_Portfolio_SHORT','RET_RP_Portfolio_LONG', 'RET_RP_Portfolio_SHORT',
        'ER_TANGENCY_Portfolio_SHORT', 'RET_TANGENCY_Portfolio_SHORT','RET_RPLONGSHORT_DELTA', 'RET_IDEALSHORT_DELTA']


    for _column in returns_to_aggregate:
        agg_colum_name='IRR_'+_column
        df[agg_colum_name]=calculate_windowed_annualized_returns(df[_column], lookback_window)

    

    #AGG YEAR SUMMARY
    windowed_columns = [col for col in df.columns if "IRR_" in col]
    weights_columns=['RP_LONG_SPX', 'RP_LONG_10Y', 'RP_SHORT_SPX','RP_SHORT_10Y', 'RP_SHORT_DXY', 'IDEAL_SHORT_SPX', 'IDEAL_SHORT_10Y', 'IDEAL_SHORT_DXY']
    df['Counter'] = 1  # Add a counter column

    agg_dict = {
        **{col: 'mean' for col in weights_columns},
        **{col: 'last' for col in windowed_columns},
        **{col: 'count' for col in ['Counter']}
    }

    # Resample and aggregate data
    sample_frequency=f'{num_months}M'
    monthly_df = df.resample(sample_frequency).agg(agg_dict)
    monthly_df = monthly_df.dropna(how='any')

    # # Prepare data for plotting
    monthly_df['Decade'] = (monthly_df.index.year // 10) * 10
    monthly_df['Month'] = (monthly_df.index.month)

    return monthly_df


def create_decade_scatter_plot(
    PLOT_FREQ_MONTHS=1, 
    COLUMN_TO_PLOT='IRR_ER_RP_Portfolio_SHORT', 
    WEIGHTS_TO_HOVER=['RP_SHORT_SPX','RP_SHORT_10Y','RP_SHORT_DXY'], 
    MARKETS_TO_HOVER=['IRR_RET_SPX_d','IRR_RET_10Y_d','IRR_RET_DXY_d'], 
    START_YEAR=1970,
    IRR_PERIOD_OPTIONS=[1, 3, 6, 12]  # List of IRR period options in months
):
    def create_trace(irr_period_months):
        lookback_window = 22 * irr_period_months

        df = aggregate_daily_returns_to_annualized_returns(pd.read_pickle("./Data/processed_data.pkl"), lookback_window, PLOT_FREQ_MONTHS)

        # Filter data based on START_YEAR
        filtered_df = df[df.index.year > START_YEAR]

        # Add Decade column if not present
        if 'Decade' not in filtered_df.columns:
            filtered_df['Decade'] = (filtered_df.index.year // 10) * 10

        assert(COLUMN_TO_PLOT in list(filtered_df.columns)), "COLUMN NOT FOUND"

        # Get unique decades and create color map
        unique_decades = sorted(filtered_df['Decade'].unique())
        colors = px.colors.qualitative.Plotly
        color_map = dict(zip(unique_decades, colors[:len(unique_decades)]))

        traces = []

        for i, decade in enumerate(unique_decades):
            decade_data = filtered_df[filtered_df['Decade'] == decade]
            
            # Add jitter to y-values
            jitter = np.random.uniform(-0.2, 0.2, len(decade_data))
            
            trace = go.Scatter(
                x=decade_data[COLUMN_TO_PLOT],
                y=[i] * len(decade_data) + jitter,
                mode='markers',
                name=f"{decade}'s",
                marker=dict(
                    size=6,
                    color=color_map[decade],
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                text=[f"Date Range: {(date - pd.DateOffset(days=int(lookback_window/252*365))).strftime('%Y-%m')} to {date.strftime('%Y-%m')}<br>"
                      f"Annualized ER: {return_:.2%}<br>"
                      f"Total ER. {return_ * (lookback_window / 252):.2%}<br>"
                      f"Weights:<br>"
                      f" SPX: {-weights_[WEIGHTS_TO_HOVER[0]]:.2%}<br>"
                      f" 10Y: {-weights_[WEIGHTS_TO_HOVER[1]]:.2%}<br>"
                      f" DXY: {-weights_[WEIGHTS_TO_HOVER[2]]:.2%}<br>"
                      f"Market AR:<br>"
                      f" SPX: {markets_[MARKETS_TO_HOVER[0]]:.2%}<br>"
                      f" 10Y: {markets_[MARKETS_TO_HOVER[1]]:.2%}<br>"
                      f" DXY: {markets_[MARKETS_TO_HOVER[2]]:.2%}<br>"
                      for date, return_, weights_, markets_ in zip(decade_data.index, 
                                                                   decade_data[COLUMN_TO_PLOT],
                                                                   decade_data[WEIGHTS_TO_HOVER].to_dict('records'),
                                                                   decade_data[MARKETS_TO_HOVER].to_dict('records'))],
                hoverinfo='text'
            )
            traces.append(trace)

        return traces

    # Create figure with dropdown menu
    fig = go.Figure()

    # Add traces for each IRR period option
    for irr_period in IRR_PERIOD_OPTIONS:
        traces = create_trace(irr_period)
        for trace in traces:
            fig.add_trace(trace)

    # Get unique decades from the first trace
    unique_decades = sorted(set(trace.name.replace("'s", "") for trace in fig.data))

    # Create and add dropdown menu
    dropdown_buttons = []
    for i, irr_period in enumerate(IRR_PERIOD_OPTIONS):
        visible = [False] * len(fig.data)
        visible[i*len(fig.data)//len(IRR_PERIOD_OPTIONS):(i+1)*len(fig.data)//len(IRR_PERIOD_OPTIONS)] = [True] * (len(fig.data)//len(IRR_PERIOD_OPTIONS))
        dropdown_buttons.append(
            dict(
                method='update',
                label=f'{irr_period} Month(s)',
                args=[{'visible': visible}]
            )
        )

    fig.update_layout(
        updatemenus=[
            dict(
                buttons=dropdown_buttons,
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ]
    )

    # Set initial visibility
    fig.data[0].visible = True
    for i in range(1, len(fig.data) // len(IRR_PERIOD_OPTIONS)):
        fig.data[i].visible = True

    # Add a vertical line at x=0
    fig.add_shape(
        type="line",
        x0=0, x1=0, y0=-0.5, y1=len(unique_decades) - 0.5,
        line=dict(color="Black", width=1, dash="dot"),
    )

    # Update the layout
    fig.update_layout(
        title={
            'text': 'Portfolio Scatter Returns',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        xaxis_title='Excess Return - Annualized',
        yaxis_title='Decade',
        xaxis=dict(tickformat='.0%', zeroline=False),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(unique_decades))),
            ticktext=[f"{decade}'s" for decade in unique_decades]
        ),
        plot_bgcolor='white',
        hovermode='closest',
        width=1000,
        height=600,
        margin=dict(t=100, l=80, r=40, b=60),
        showlegend=True,
        legend_title_text='Decade'
    )

    return fig

def create_returns_plot(df, select_col='RET_RP_Portfolio_SHORT', lookback_options=[3, 6, 12, 24]):

    
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for i, lookback in enumerate(lookback_options):
        lookback_window = 23 * lookback
        new_col = 'IRR_' + select_col
        df[new_col] = calculate_windowed_returns(df[select_col], lookback_window)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[new_col],
            mode='lines',
            name=f'{lookback} Month',
            visible=(lookback == lookback_options[0]),
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate='%{x|%Y-%m-%d}<br>Return: %{y:.2%}<extra></extra>'
        ))
    
    dropdown_buttons = []
    for i, lookback in enumerate(lookback_options):
        visible = [False] * len(fig.data)
        visible[i] = True
        dropdown_buttons.append(
            dict(
                method='update',
                label=f'{lookback} Month Lookback',
                args=[{'visible': visible},
                      {'title': f'{select_col} - {lookback} Month'}]
            )
        )
    
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=dropdown_buttons,
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.9,  # Move to the right
                xanchor="left",
                y=1.15,
                yanchor="top",
                bgcolor='rgba(255, 255, 255, 0.7)',
                bordercolor='rgba(0, 0, 0, 0.5)',
                font=dict(size=12)
            ),
        ],
        title=dict(
            text=f'{select_col} - {lookback_options[0]} Month',
            font=dict(size=24, color='#333'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Date',
            title_font=dict(size=16),
            tickfont=dict(size=12),
            showgrid=True,
            gridcolor='rgba(0, 0, 0, 0.1)'
        ),
        yaxis=dict(
            title='Total Excess Returns',
            title_font=dict(size=16),
            tickfont=dict(size=12),
            tickformat='.1%',
            showgrid=True,
            gridcolor='rgba(0, 0, 0, 0.1)',
            zeroline=True,
            zerolinecolor='rgba(0, 0, 0, 0.2)',
            zerolinewidth=2
        ),
        hovermode='x unified',
        paper_bgcolor='white',
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(255, 255, 255, 0.7)',
            bordercolor='rgba(0, 0, 0, 0.5)'
        ),
        margin=dict(l=80, r=40, t=100, b=60)
    )
    
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=20, label="20y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def plot_rolling_excess_returns(df, DXY_LEVERAGE=5):

    colors = px.colors.qualitative.Plotly

    # Assuming df is your DataFrame with the excess returns data
    # Make sure df is sorted by date
    df = df.sort_index()
    DXY_LEVERAGE=5

    colors = px.colors.qualitative.Plotly
    df['RET_DXY_d']=df['RET_DXY_d']/DXY_LEVERAGE

    # List of assets and windows
    assets = ['SPX', '10Y', 'DXY']
    windows = [63, 126, 252, 504]  # 3 months, 6 months, 1 year, 2 years
    window_labels = ['3m', '6m', '1y', '2y']

    # Calculate rolling IRR for different windows
    for asset in assets:
        for window in windows:
            col_name = f'ROLL_{asset}_IRR_{window}d'
            df[col_name] = calculate_windowed_annualized_returns(df[f'RET_{asset}_d'], window=window)

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
                            {"title": f"Rolling Returns ({label})"}],
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
        'RET_SPX_d': lambda x: (1 + x).prod() - 1,
        'RET_10Y_d': lambda x: (1 + x).prod() - 1
    }) * 100  # Convert to percentage

    # Create the grouped bar chart
    fig = go.Figure()

    # Add 10Y Treasury bars
    fig.add_trace(go.Bar(
        x=yearly_returns.index,
        y=yearly_returns['RET_10Y_d'],
        name='10Y Treasury',
        hovertemplate='Year: %{x}<br>10Y Treasury: %{y:.2f}%<extra></extra>',
        marker=dict(
            color=['#FF9999' if y < 0 else '#FF0000' for y in yearly_returns['RET_10Y_d']],
            line=dict(
                color=['#FF3333' if y < 0 else '#FF0000' for y in yearly_returns['RET_10Y_d']],
                width=[2 if y < 0 else 0 for y in yearly_returns['RET_10Y_d']]
            ),
        )
    ))

    # Add SPX bars
    fig.add_trace(go.Bar(
        x=yearly_returns.index,
        y=yearly_returns['RET_SPX_d'],
        name='S&P500',
        hovertemplate='Year: %{x}<br>S&P500: %{y:.2f}%<extra></extra>',
        marker=dict(
            color=['#9999FF' if y < 0 else '#0000FF' for y in yearly_returns['RET_SPX_d']],
            line=dict(
                color=['#3333FF' if y < 0 else '#0000FF' for y in yearly_returns['RET_SPX_d']],
                width=[2 if y < 0 else 0 for y in yearly_returns['RET_SPX_d']]
            ),
        )
    ))

    # Update the layout
    fig.update_layout(
        title='Annual Returns: SPX vs 10Y Treasury',
        xaxis_title='Year',
        yaxis_title='Annual Returns (%)',
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
                        args=[{"y": [yearly_returns['RET_10Y_d'], yearly_returns['RET_SPX_d']]},
                            {"title": "Annual Returns: SPX vs 10Y Treasury"}]),
                    dict(label="Positive Only",
                        method="update",
                        args=[{"y": [[y if y >= 0 else None for y in yearly_returns['RET_10Y_d']],
                                    [y if y >= 0 else None for y in yearly_returns['RET_SPX_d']]]},
                            {"title": "Annuals Returns: SPX vs 10Y Treasury (Positive Only)"}]),
                    dict(label="Negative Only",
                        method="update",
                        args=[{"y": [[y if y < 0 else None for y in yearly_returns['RET_10Y_d']],
                                    [y if y < 0 else None for y in yearly_returns['RET_SPX_d']]]},
                            {"title": "Annual Returns: SPX vs 10Y Treasury (Negative Only)"}]),
                ]),
            )
        ]
    )

    # Show the plot
    return fig


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def plot_portfolio_returns_bubble_year(df, window_size=256):
    #WINDOW YEARLY RETURNS
    returns_to_aggregate=['RET_SPX_d', 'RET_10Y_d', 'RET_DXY_d', 'RET_FFR_d', 'RET_SHORT_SPX_d', 'RET_SHORT_10Y_d', 'RET_SHORT_DXY_d', 'ER_SPX_d', 'ER_10Y_d', 'ER_DXY_d',
        'ER_SHORT_SPX_d', 'ER_SHORT_10Y_d', 'ER_SHORT_DXY_d','ER_RP_Portfolio_LONG', 'ER_RP_Portfolio_SHORT','RET_RP_Portfolio_LONG', 'RET_RP_Portfolio_SHORT',
        'ER_TANGENCY_Portfolio_SHORT', 'RET_TANGENCY_Portfolio_SHORT','RET_RPLONGSHORT_DELTA', 'RET_IDEALSHORT_DELTA']

    for _column in returns_to_aggregate:
        agg_column_name='WINDOWED_'+_column
        df[agg_column_name]=calculate_windowed_returns(df[_column],window_size)


    #AGG YEAR SUMMARY
    windowed_columns = [col for col in df.columns if "WINDOWED" in col]
    weights_columns=['RP_LONG_SPX', 'RP_LONG_10Y', 'RP_SHORT_SPX','RP_SHORT_10Y', 'RP_SHORT_DXY']

    agg_dict = {
        **{col: 'mean' for col in weights_columns},
        **{col: 'last' for col in windowed_columns},
        **{col: 'count' for col in ['Year']}
    }

    years=df.groupby('Year').aggregate(agg_dict)
    years['WINDOWED_RET_RPLONGSHORT_DELTA']=years['WINDOWED_RET_RPLONGSHORT_DELTA']*100
    performance_df=years.dropna(how='any') #[[col for col in years.columns if (("RP" in col) or ("d" in col and ("SHORT" and "FFR") not in col)) and "ER" not in col]]*100

    # Assuming 'years' is your dataframe
    # Create a new column for the adjusted delta values
    years = performance_df[performance_df.index>=1970]
    years['Adjusted_Delta'] = np.maximum(years['WINDOWED_RET_RPLONGSHORT_DELTA'], 0) + 1

    years['hover_text'] = years.apply(lambda row: f"""
    Year: {row.name}
    
    Performance: {row['WINDOWED_RET_RP_Portfolio_SHORT']:.2%}

    Weights:
    {-row['RP_SHORT_SPX']:.2%} SPX
    {-row['RP_SHORT_10Y']:.2%} 10Y
    {-row['RP_SHORT_DXY']:.2%} DXY


    Delta: {row['WINDOWED_RET_RPLONGSHORT_DELTA']/100:.2%}

    Market:
    SPX: {row['WINDOWED_RET_SPX_d']:.2%}
    10YT: {row['WINDOWED_RET_10Y_d']:.2%}
    DXY: {row['WINDOWED_RET_DXY_d']:.2%}

    """.strip(), axis=1)

    # Create opacity values based on delta
    years['opacity'] = np.where(years['WINDOWED_RET_RPLONGSHORT_DELTA'] >= 0, 0.8, 0.3)

    # Create the bubble plot
    fig = px.scatter(
        years,
        x=years.index,
        y='WINDOWED_RET_RP_Portfolio_SHORT',
        size='Adjusted_Delta',
        hover_name=years.index,
        custom_data=['hover_text'],
        labels={
            'WINDOWED_RET_RP_Portfolio_SHORT': 'Returns',
            'index': 'Year'
        },
        title='Strategy Returns by Year'
    )

    # Customize the layout
    fig.update_layout(
        title={
            'text': 'Short-Only Risk Parity Portfolio',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },

        annotations=[
            dict(
                text='Absolute Returns by Year',  # Your subtitle text
                xref='paper',
                yref='paper',
                x=0.5,
                y=1.05,
                xanchor='center',
                yanchor='bottom',
                showarrow=False,
                font=dict(size=16)
            )
        ],

        xaxis_title='Year',
        yaxis_title='Return',
        xaxis=dict(tickangle=45, dtick=5),
        yaxis=dict(tickformat='1%', gridcolor='lightgrey'),
        plot_bgcolor='white',
        hovermode='closest',
        width=1000,
        height=600,
        margin=dict(t=100, l=80, r=40, b=80)
    )

    # Update the traces
    fig.update_traces(
        marker=dict(
            sizeref=2.*max(years['Adjusted_Delta'])/(40.**2),
            sizemin=4,
            line=dict(width=1, color='DarkSlateGrey'),
            color='LightSeaGreen',
            opacity=years['opacity']  # Use the opacity column
        ),
        hovertemplate='%{customdata[0]}',
    )

    # Add a horizontal line at y=0
    fig.add_shape(
        type="line",
        x0=years.index.min(),
        x1=years.index.max(),
        y0=0,
        y1=0,
        line=dict(color="Grey", width=1, dash="dot"),
    )

    fig.update_xaxes(
        gridcolor='rgba(189, 195, 199, 0.5)',
        rangeslider_visible=True
    )

    return fig
