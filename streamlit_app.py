import streamlit as st
import pandas as pd
import numpy as np
import math
from pathlib import Path
from window_functions import calculate_windowed_returns, calculate_windowed_annualized_returns
import plotly.graph_objects as go
import plotly.express as px

from custom_plots import create_decade_scatter_plot, create_returns_plot, plot_rolling_excess_returns, plot_yield_comparison, plot_stock_bond_correlation, plot_portfolio_returns_bubble_year

##CONFIG
# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Short All Dashboard',
    page_icon='# :chart_with_downward_trend', 
)

##FUNCTIONS
@st.cache_data
def get_images():
    # Create three columns
    col1, col2, col3 = st.columns(3)
    # Add an image to each column
    with col1:
        st.image("https://miro.medium.com/v2/resize:fit:1246/format:webp/1*NHs2eDzhEjNUdFFlm_ut5A.png", caption="Liquidity Hierarchy: cyclical expansion and contraction of credit", use_column_width=True)

    with col2:
        st.image("https://substackcdn.com/image/fetch/w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6447ea09-e627-400b-bd96-ba7e69fe0777_900x629.png", caption="Investment Seasons: a time to plant, and a time to pluck up that which is planted", use_column_width=True)

    with col3:
        st.image("https://cdn.prod.website-files.com/634054c00f602044abb3060d/64625fa85ed5193ea3ad5f71_Bitcoin%20Rainbow%20Chart%20.webp", caption="Bitcoin Hyperstition: a very optimistic logistic regression", use_column_width=True)

@st.cache_data
def get_data():
    df= pd.read_pickle("./Data/processed_data.pkl")
    return df[df.index.year>1970]

st.title("Short All")
st.markdown("---")

##Table of Contents
toc = """
1. [**Overview**](#overview)
   1. [Market Cycles](#market-cycles)
   2. [Short-All Performance](#short-all-performance)
   3. [Something New](#something-new)
2. [**Portfolio Construction**](#portfolio-construction)
   1. [Asset Selection](#asset-selection)
   2. [Assumptions](#assumptions)
   3. [Excess vs Total Returns](#excess-vs-total-returns)
   4. [Asset Returns](#asset-returns)
   5. [Risk Parity Weights](#risk-parity-weights)
   6. [Max Sharpe](#max-sharpe)
3. [**Backtest**](#backtest)
   1. [When did short-all work?](#when-did-short-all-work)
   2. [Optimal Weights](#optimal-weights)
   3. [Exogenous risks](#exogenous-risks)
   4. [Counterfactuals](#counterfactuals)
4. [**Why did the short-all work?**](#why-did-the-short-all-work)
   1. [2022](#2022)
5. [**Predictions for 2024**](#predictions-for-2024)
"""
st.markdown(toc)
st.markdown("---")


# 1. Overview
st.markdown("### 1. Overview")
st.write("Though the strategy of short, some combination of stocks, bonds, and dollars has generated excess returns infrequently, there have been periods where it works. This doc analyzes when it managed to work, where it worked, and what changes would need to occur that it might work again.")

# 1.1 Market Cycles
st.markdown("##### Market Cycles")
st.write("Attempts to uncover a pattern of rise and fall - to time the ups and the down of the market - have produced a colorful history.")
st.markdown("---")
get_images()
st.markdown("---")
st.write("But at least in the U.S. the really obvious thing has been to passively go long stocks and bonds. The SP500 hits a new all time high on ~7% of trading days, and half of the time it trades within 6% of the ATH. It’s inductively sound (and is often accurate) to think that the general trends of the past will continue. And indeed, going long stocks and bonds at risk parity has been an efficacious strategy.")

# 1.2 Short-All Performance
st.markdown("##### Short-All Performance")
st.write("What happens when we go short? The assumptions, portfolio weights, and caveats are covered later in the doc...but the chart below gives an overview of how the trade performed.")
st.write("The chart shows total returns of a naive short-all strategy  - how much the short investor made vs. hiding the cash under a mattress - for each calendar year since 1971.")
st.write("You can interact with the chart hover over the bubble to see the portfolio weights, and how the underlying assets performed that year. The bigger the bubble the better the short did vs the long.")

st.markdown("---")
df = get_data()  
fig_years = plot_portfolio_returns_bubble_year(df)
st.plotly_chart(fig_years)
st.markdown("---")

st.write("Note that in 1974 the short overperformed vs the long, but the best strategy was to just to earn the risk free rate! For the rest of the doc we’ll be primarily dealing with excess returns to account for this")

st.write("For a more granular view of how the trade performed look at the bubble chart below. Select the window of time for which to put on the trade (3 months, 6 months, 12 months)...the portfolio weights are recomputed daily with 1y lookback window so putting on the trade just means expressing a short-all intention. Hover over a specific bubble to get the returns. Notice that as one chooses longer windows the short opportunities go away. A trade will work for 6 months, but the next 12 months of asset prices increases will wipe away the profit.") 
st.write("The chart shows excess annualized excess returns. A 3 month short trade that makes 10% would show up as ~40%. (plz choose a time window from the dropdown if you want the chart to display correctly)") 
st.markdown("---")
df = get_data()  
fig_decade = create_decade_scatter_plot()
st.plotly_chart(fig_decade)
st.markdown("---")

# 1.3 Something New
st.text("")
st.markdown("##### Something New")
st.write("This section introduces a novel concept or strategy that has emerged in recent market analysis.")

st.markdown("---")

# 2. Portfolio Construction
st.markdown("### 2. Portfolio Construction")

# 2.1 Asset Selection
st.text("")
st.markdown("##### Asset Selection")
st.write("The process of choosing which assets to include in a portfolio based on various criteria such as risk, return, and correlation.")

# 2.2 Assumptions
st.text("")
st.markdown("##### Assumptions")
st.write("Key assumptions made in the portfolio construction process, including expected returns, volatility, and correlation estimates.")

# 2.3 Excess vs Total Returns
st.text("")
st.markdown("##### Excess vs Total Returns")
st.write("A comparison of excess returns (returns above a benchmark) and total returns, and their implications for portfolio performance.")

# 2.4 Asset Returns
st.text("")
st.markdown("##### Asset Returns")
st.write("An analysis of the historical and expected returns for different asset classes in the portfolio.")

# 2.5 Risk Parity Weights
st.text("")
st.markdown("##### Risk Parity Weights")
st.write("Explanation of the risk parity approach to portfolio weighting and its implementation in this strategy.")

# 2.6 Max Sharpe
st.text("")
st.markdown("##### Max Sharpe")
st.write("Discussion on maximizing the Sharpe ratio for optimal risk-adjusted returns in portfolio construction.")

st.markdown("---")

# 3. Backtest
st.markdown("### 3. Backtest")

# 3.1 When did short-all work?
st.text("")
st.markdown("##### When did short-all work?")
st.write("Analysis of historical periods when the short-all strategy was particularly effective, including market conditions and economic factors.")

# 3.2 Optimal Weights
st.text("")
st.markdown("##### Optimal Weights")
st.write("Determination of the ideal asset allocation weights to maximize portfolio performance based on historical data.")

# 3.3 Exogenous risks
st.text("")
st.markdown("##### Exogenous risks")
st.write("Examination of external factors and risks that could impact the performance of the short-all strategy.")

# 3.4 Counterfactuals
st.text("")
st.markdown("##### Counterfactuals")
st.write("Exploration of alternative scenarios and their potential impacts on the strategy's performance.")

st.markdown("---")

# 4. Why did the short-all work?
st.markdown("### 4. Why did the short-all work?")

# 4.1 2022
st.text("")
st.markdown("##### 2022")
st.write("An in-depth look at the performance of the short-all strategy in 2022, examining the factors that contributed to its success or failure.")

st.markdown("---")

# 5. Predictions for 2024
st.markdown("### 5. Predictions for 2024")
st.write("Based on our analysis, here are some predictions for market trends and potential strategies for 2024.")


# ###
# "CHART 1"
# fig_main=create_decade_scatter_plot()
# st.plotly_chart(fig_main)

# "CHART 2"
# df = get_data() 
# portfolio_to_plot='ER_RP_Portfolio_SHORT' #Risk Parity short portfolio
# portfolio_returns = create_returns_plot(df)
# st.plotly_chart(portfolio_returns)

# '''
# # Short All
# '''



# '''
# ---
# Attempts to uncover patterns of rise and fall in the market have produced a colorful history...

# &nbsp;
# '''
# get_images()

# '''
# ---
# It's inductively sound and often accurate to think that the general trends of the past will continue. Going long stocks and bonds at risk parity has been an efficacious strategy.

# On the other hand, betting on a broad decline in asset prices (in the United States) is a bet that things will not merely stay the same.

# In this document, we'll explore the 'short-everything' strategy—a portfolio weighted between short positions on the S&P 500, 10-year Treasuries, and leveraged Dollar Index (DXY). The analysis will cover:

# 1. **Asset Overview**: How have stocks, bonds, DXY, and cash have performed since approximately 1971? How do we measure performance?
# 2. **Portfolio Construction**: How do we size the bet? How we'll has it worked in the past?
# 3. **Historical Reconstruction**: When it worked...why did it work?
# 4. **Prediction**: How bad of an idea is it to put on this trade in 2024H2? What things might I believe that would make this a good trade?
# ---

# '''

# ## PART 1

# '''
# How have the following three investment apporaches fared historically?

# 1. **Cash**: Earn the "risk-free" rate
# 2. **Long**: long some weighting of stocks and bonds
# 3. **Short**: short some weighting of stocks, bonds, and leverged USD 

# Cash is the effective fedral funds rate (FFR). Stocks are SPX total returns. USD is DXY. Bonds are 10Y treasuryies.

# Before we investiagte the portfolio performance let's look at how indivdual assets perform. You can use the interactive graph to explore the rolling, anualized excess returns of each asset over different windows. Note that throughout this document we're going to focus mostly on returns on or after 1971 as I think the ending of Bretton Woods marks a fundamental shift in the monetary system.  

# ---

# '''

# df = get_data()  
# fig_er = plot_rolling_excess_returns(df)
# st.plotly_chart(fig_er)



# '''
# Let's also look at the yields. Periods where the risk free rate exceedes the 10Y yeild - shaded in red - bode porly for a long only strategy (presumably because if treaury buyers are willing to accept lower long-term yields it means they can't figure out a better place to park capital). 

# ---
# ''' 

# df = get_data()  
# fig_yeild = plot_yield_comparison(df)
# st.plotly_chart(fig_yeild)


# '''
# On the data side, FFR is pulled directly FRED. SPX is adjusted to include dividends. 10Y bond prices are approximated by calculating it's modified duration and change in yield. After data wrangling we end up with the daily absolute and excess returns for each asset. 
# When calculating returns, the short positions in stocks and bonds are assumed to be 100% short (i.e., the exact inverse of a long position) without any additional leverage. Bonds are always rolled to keep constant 10y meaturies. Borrowing cost, exchange fees, and slippage are assumed to always be de-minimis. 

# Finally, before we look construct our portfolio, we can get a sense of stock bond correlation by looking at the performance of stocks and bonds per year...this is just an explorarty graph but it would appear that the correlation between stocks and bonds is pretty weak. 

# ---

# '''

# df = get_data()  
# fig_yeild = plot_stock_bond_correlation(df)
# st.plotly_chart(fig_yeild)


# '''
# These are the returns of the risk parity short portfolio by decade. The bubble size corresponds to how much better the short RP portfolio performed vs the long portfolio. The muted dots, mean that the naieve long RP portfolio outperformed.

# ---
# '''

# df = get_data()  
# fig_yeild = plot_portfolio_returns_bubble_year(df)
# st.plotly_chart(fig_yeild)

# '''

# To reiterate we want to find the best portfolio among:

# 1. **Cash**: Earn the "risk-free" rate
# 2. **Long**: long some weighting of stocks and bonds
# 3. **Short**: short some weighting of stocks, bonds, and leverged USD 

# To build a short-only porfolio we will choose (w_spx, w_10y, w_dxy) with constraints (wi in [0,-1]), sum(wi=-1). Further, because we are using a 5x levered DXY index, we will restrict w_dxy to a max of 1/5. This means the portfolio can have up between (0,-1) exposure to the dollar. This also means that in the short only strategy we are short 80%+ of our capital base in some combination of stocks and bonds

# To build a long-only portfolio we will chose (w_spx, w_10y)  (wi in [0,1]), sum(wi=1). In the long portfolio we are alredady implicitly long dollar (the assets are denominated in dollar and the value of the stocks and bonds are the expectation of future  so I don't see a need to bet on the DYX. Without DYX the long portfolios we make will be somewhat similar to familar 60/40 strategies and is therefore easy to interpret.


# The **best** portfolio is the one with the maximum sharpe ratio over the window of time we deem relevant. 

# We can simplify this by problem by thinking about with considering the excess returns of each portfolio. 

# ---

# '''


# st.markdown(r"""
# For both the long and the short portfolios we find the covarience matrix, and the weights. Use a trailing window of 252 trading days ~1 year. And compute the predicted best weights daily. The weights are forward looking, meaning we calculate them without knowing what the realized vol is, Assume that we can rebalance the portfolios once per day.

# Risk parity gives us a realistic benchamrk for what a good, but non-propeitary porfolio would look like. 
            
# A big reason risk parity makes a "good" portfolio is that volatility has autoregressive structure It's outside of the scope of this doc, but we could improve upon the naive implemntation. By having better predictive models for covarience matrix like a GARCH model.

# """)