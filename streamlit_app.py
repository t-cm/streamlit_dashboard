import streamlit as st
import pandas as pd
import numpy as np
import math
from pathlib import Path
from window_functions import calculate_windowed_returns, calculate_windowed_annualized_returns
import plotly.graph_objects as go
import plotly.express as px

from custom_plots import plot_rolling_excess_returns, plot_yield_comparison, plot_stock_bond_correlation

##CONFIG
# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Short All',
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
    return df



##Intro

'''
# Short All
'''

'''
---
Attempts to uncover patterns of rise and fall in the market have produced a colorful history...

&nbsp;
'''
get_images()

'''
---
It's inductively sound and often accurate to think that the general trends of the past will continue. Going long stocks and bonds at risk parity has been an efficacious strategy.

On the other hand, betting on a broad decline in asset prices (in the United States) is a bet that things will not merely stay the same.

In this document, we'll explore the 'short-everything' strategy—a portfolio weighted between short positions on the S&P 500, 10-year Treasuries, and leveraged Dollar Index (DXY). The analysis will cover:

1. **Asset Overview**: How have stocks, bonds, DXY, and cash have performed since approximately 1971? How do we measure performance?
2. **Portfolio Construction**: How do we size the bet? How we'll has it worked in the past?
3. **Historical Reconstruction**: When it worked...why did it work?
4. **Prediction**: How bad of an idea is it to put on this trade in 2024H2? What things might I believe that would make this a good trade?
---

'''

## PART 1

'''
How have the following three investment apporaches fared historically?

1. **Cash**: Earn the "risk-free" rate
2. **Long**: long some weighting of stocks and bonds
3. **Short**: short some weighting of stocks, bonds, and leverged USD 

Cash is the effective fedral funds rate (FFR). Stocks are SPX total returns. USD is DXY. Bonds are 10Y treasuryies.

Before we investiagte the portfolio performance let's look at how indivdual assets perform. You can use the interactive graph to explore the rolling, anualized excess returns of each asset over different windows. Note that throughout this document we're going to focus mostly on returns on or after 1971 as I think the ending of Bretton Woods marks a fundamental shift in the monetary system.  

---

'''

df = get_data()  
fig_er = plot_rolling_excess_returns(df)
st.plotly_chart(fig_er)



'''
Let's also look at the yields. Periods where the risk free rate exceedes the 10Y yeild - shaded in red - bode porly for a long only strategy (presumably because if treaury buyers are willing to accept lower long-term yields it means they can't figure out a better place to park capital). 

---
''' 

df = get_data()  
fig_yeild = plot_yield_comparison(df)
st.plotly_chart(fig_yeild)


'''
On the data side, FFR is pulled directly FRED. SPX is adjusted to include dividends. 10Y bond prices are approximated by calculating it's modified duration and change in yield. After data wrangling we end up with the daily absolute and excess returns for each asset. 
When calculating returns, the short positions in stocks and bonds are assumed to be 100% short (i.e., the exact inverse of a long position) without any additional leverage. Bonds are always rolled to keep constant 10y meaturies. Borrowing cost, exchange fees, and slippage are assumed to always be de-minimis. 

Finally, before we look construct our portfolio, we can get a sense of stock bond correlation by looking at the performance of stocks and bonds per year...this is just an explorarty graph but it would appear that the correlation between stocks and bonds is pretty weak. 

---

'''

df = get_data()  
fig_yeild = plot_stock_bond_correlation(df)
st.plotly_chart(fig_yeild)


'''
To reiterate we want to find the best portfolio among:

1. **Cash**: Earn the "risk-free" rate
2. **Long**: long some weighting of stocks and bonds
3. **Short**: short some weighting of stocks, bonds, and leverged USD 

To build a short-only porfolio we will choose (w_spx, w_10y, w_dxy) with constraints (wi in [0,-1]), sum(wi=-1). Further, because we are using a 5x levered DXY index, we will restrict w_dxy to a max of 1/5. This means the portfolio can have up between (0,-1) exposure to the dollar. This also means that in the short only strategy we are short 80%+ of our capital base in some combination of stocks and bonds

To build a long-only portfolio we will chose (w_spx, w_10y)  (wi in [0,1]), sum(wi=1). In the long portfolio we are alredady implicitly long dollar (the assets are denominated in dollar and the value of the stocks and bonds are the expectation of future  so I don't see a need to bet on the DYX. Without DYX the long portfolios we make will be somewhat similar to familar 60/40 strategies and is therefore easy to interpret.


The **best** portfolio is the one with the maximum sharpe ratio over the window of time we deem relevant. 

We can simplify this by problem by thinking about with considering the excess returns of each portfolio. 

---

'''


st.markdown(r"""
## Risk Parity: A Balanced Approach to Portfolio Construction

Risk parity is an innovative and compelling approach to portfolio construction that addresses the limitations of traditional asset allocation methods. Unlike capital-weighted strategies that often result in concentration risk, risk parity seeks to equalize risk contributions across all assets in the portfolio. This approach is based on the principle that risk, not capital, should be the primary factor in allocation decisions.

The core idea of risk parity is to allocate portfolio weights such that each asset contributes equally to the overall portfolio risk. Crucially, this approach considers not just individual asset volatilities, but also the covariances between assets. The risk contribution of each asset is given by:

$$RC_i = w_i \cdot (\Sigma w)_i$$

where $w_i$ is the weight of asset $i$, $\Sigma$ is the covariance matrix of asset returns, and $(\Sigma w)_i$ is the $i$-th element of the vector resulting from the matrix multiplication of $\Sigma$ and $w$.

In a risk parity portfolio, we aim to equalize these risk contributions:

$$RC_i = RC_j \quad \forall i,j$$

This leads to a more nuanced allocation that accounts for the complex interactions between assets, achieving:

1. **Improved Diversification**: It prevents over-concentration in high-risk assets or highly correlated asset groups, leading to a more balanced risk exposure.
2. **Enhanced Risk-Adjusted Returns**: By not over-allocating to riskier assets or ignoring correlations, it can potentially improve the Sharpe ratio of the portfolio.
3. **Adaptability**: The approach naturally adjusts to changing market conditions as volatilities and correlations evolve.
4. **Reduced Tail Risk**: By avoiding concentration in any single asset or highly correlated asset class, it can help mitigate extreme downside scenarios.

The weights in a risk parity portfolio can be found by solving the following optimization problem:

$$\min_w \sum_{i=1}^n (\log(w_i) - \log(RC_i))^2$$

subject to $\sum_{i=1}^n w_i = 1$ and $w_i > 0$ for all $i$.

This sophisticated yet intuitive approach to portfolio construction offers a robust alternative to traditional methods, potentially leading to more stable and efficient portfolios over the long term by fully accounting for the covariance structure of the assets.
""")