import streamlit as st
import pandas as pd
import numpy as np
import math
from pathlib import Path
from window_functions import calculate_windowed_returns, calculate_windowed_annualized_returns
import plotly.graph_objects as go
import plotly.express as px


from custom_plots import create_decade_scatter_plot, create_returns_plot, plot_rolling_excess_returns, plot_yield_comparison, plot_stock_bond_correlation, plot_portfolio_returns_bubble_year


st.cache_data.clear()


##CONFIG
# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
   page_title='Short All Dashboard',
   page_icon='# :chart_with_downward_trend',
)


##FUNCTIONS
# @st.cache_data
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


# @st.cache_data
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
   3. [Asset Returns](#asset-returns)
   4. [Risk Parity Weights](#risk-parity-weights)
3. [**Backtest**](#backtest)
   1. [When did short-all work?](#when-did-short-all-work)
   2. [Exogenous risks](#exogenous-risks)
4. [**Why did the short-all work?**](#why-did-the-short-all-work)
5. [**Predictions**](#predictions-for-2024)
"""
st.markdown(toc)
st.markdown("---")

st.markdown("---")




# 1. Overview
st.markdown("### 1. Overview")
st.write("Though the strategy of short, some combination of stocks, bonds, and dollars has generated excess returns infrequently, there have been periods where it works. This doc analyzes when it managed to work, where it worked, and what changes would need to occur that it might work again.")
st.text("")


# 1.1 Market Cycles
st.markdown("#### Market Cycles")
st.write("Attempts to uncover a pattern of rise and fall - to time the up and the down of the market - have produced a colorful history.")
st.markdown("---")
get_images()
st.markdown("---")
st.write("But at least in the U.S. the really obvious thing has been to passively go long stocks and bonds. The SP500 hits a new all time high on ~7% of trading days, and half of the time it trades within 6% of the ATH. It’s inductively sound (and is often accurate) to think that the general trends of the past will continue. And indeed, going long stocks and bonds at risk parity has been an efficacious strategy.")
st.text("")


# 1.2 Short-All Performance
st.markdown("#### Short-All Performance")
st.write("What happens when we go short? The assumptions, portfolio weights, and caveats are covered later in the doc...but the chart below gives an overview of how the trade performed.")
st.write("The chart shows total returns of a naive short-all strategy  - how much the short investor made vs. hiding the cash under a mattress - for each calendar year since 1971.")
st.write("You can interact with the chart hover over the bubble to see the portfolio weights, and how the underlying assets performed that year. The bigger the bubble the better the short did vs the long.")


st.markdown("---")
df = get_data() 
fig_years = plot_portfolio_returns_bubble_year(df)
st.plotly_chart(fig_years)
st.markdown("---")


st.write("Note that in 1974 the short overperformed vs the long, but the compelling thing to do was to just to earn the risk free rate! For the rest of the doc we’ll be primarily dealing with excess returns to account for this")


st.write("For a more granular view of how the trade performed look at the bubble chart below. Select the window of time for which to put on the trade (3 months, 6 months, 12 months)...the portfolio weights are recomputed daily with 1y lookback window so putting on the trade just means expressing a short-all intention. Hover over a specific bubble to get the returns. Notice that as one chooses longer windows the short opportunities go away. A trade will work for 6 months, but the next 12 months of asset prices increases will wipe away the profit.")
st.write("The chart shows excess annualized excess returns. A 3 month short trade that makes 10% would show up as ~40%. (plz choose a time window from the dropdown if you want the chart to display correctly)")
st.markdown("---")
df = get_data()


fig_decade = create_decade_scatter_plot()
st.plotly_chart(fig_decade)
st.markdown("---")
st.text("")


# 1.3 Something New
st.markdown("#### Something New")
st.write("I get into this in more detail in the Counterfactual section…but I think there are some core, potentially unexamined, assumptions which make the approach of long stocks+bonds work. I don’t think these assumptions have been challenged much in the last 100 years.")
st.write("The place where the short trade probably performs the best is where one can foresee some total break with convention or expectation. The trade in its ideal form is therefore future looking and ought not be inferred from past data.")


st.markdown("---")


# 2. Portfolio Construction
st.markdown("### 2. Portfolio Construction")


# 2.1 Asset Selection
st.text("")
st.markdown("##### Asset Selection")
'''
The short-everything strategy is a portfolio with weighted short positions on the S&P 500, 10-year Treasuries, and leveraged Dollar Index (DXY).


The first step is to figure out the returns for each of these and the returns on cash held at the risk free rate. FFR is pulled directly FRED. SPX is adjusted to include dividends. 10Y bond prices are estimated -modified_duration_daily*delta_yield_daily and we add back in the yield earned. After data wrangling we end up with the daily absolute and excess returns for each asset.
'''
st.write("Here's summary of the yields. Red sections are where the yields are inverted (FFR > 10Y)")


st.markdown("---")
df = get_data() 
fig_yeild = plot_yield_comparison(df)
st.plotly_chart(fig_yeild)
st.markdown("---")


st.write("We can also get a sense of how stocks and bonds move by looking at the each calendar year")
st.markdown("---")
df = get_data() 
fig_yeild = plot_stock_bond_correlation(df)
st.plotly_chart(fig_yeild)
st.markdown("---")




# 2.2 Assumptions


st.write("""
  Some assumptions about how to calculate excess returns for both the long and short of these assets.
  Let "r" be the returns of the underlying series, "q" is the dividend, "y" is 10Y bond yield and "i" is some risk free rate paid to dollar holders, FX basket of currencies, or money in margin account.
       """)


st.text("")


st.latex(r"\text{SPX}_{long} = r_{SPX} + q_{div} - i_{US}")
st.latex(r"\text{SPX}_{short} = -r_{SPX} - q_{div} + (i_{sweep} - i_{borrow}) - i_{US}")
st.text("")


st.latex(r"\text{10Y}_{long} = r + y - i_{US}")
st.latex(r"\text{10Y}_{short} = -r - y")


st.text("")


st.latex(r"\text{DXY}_{long} = 5 \times (r + (i_{US} - i_{FX}))")
st.latex(r"\text{DXY}_{short} = 5 \times (-r + (i_{FX} - i_{US}))")
st.text("")


st.markdown("##### Assumptions")
st.write("""
Some assumptions..
When calculating returns, the short positions in stocks and bonds are assumed to be 100% short (i.e., the exact inverse of a long position) without any additional leverage. While short must pay (are negative) dividends in the case of stock and yield in the case of bonds.
       
Bonds are always rolled to keep constant 10y maturities.
       
When shorting stocks we assume the borrowing cost and the sweep rate are approximately the same. Otherwise, Borrowing cost, exchange fees, and slippage are assumed to always be de-minimis.


The portfolio can be rebalanced daily
       
DXY positions are done with 5x leverage. Un-levered DXY positions don't have compelling excess returns. 

The risk free rate of the euro-component of the DXY basket is approximated with the German 90 day interbank rank FRED:IR3TIB01DEM156N

Mechanically what happens when going short DXY with leverage is that we borrow USD, swap it into a basket of foreign currencies. So it’s the change in the price of the DXY index plus/minus the relative over or underperformance of the yield on that basket of foreign currencies vs. the yield we owe on the USD.  


Data before the end of Bretton woods in 1971, is for the most part excluded from this analysis""")


# 2.3 Asset Returns
st.text("")
st.write("""
Asset Overview: How have stocks, bonds, levered DXY, and cash have performed since approximately 1971? The chart below shows the rolling (non-excess) returns of each.


Note that it’s very uncommon for all three to be negative. Where they are are areas of interest. 2022 briefly, 1987 post flash crash, etc.
""")
st.markdown("##### Asset Returns")
st.markdown("---")
df = get_data() 
fig_er = plot_rolling_excess_returns(df)
st.plotly_chart(fig_er)
st.markdown("---")


# 2.5 Risk Parity Weights
st.text("")
st.markdown("##### Risk Parity Weights")
st.write("""
      


We want to find the best portfolio among:




1. **Cash**: Earn the "risk-free" rate
2. **Long**: long some weighting of stocks and bonds
3. **Short**: short some weighting of stocks, bonds, and leveraged USD




To build a short-only portfolio we will choose (w_spx, w_10y, w_dxy) with constraints (wi in [0,-1]), sum(wi=-1). Further, because we are using a 5x levered DXY index, we will restrict w_dxy to a max of 1/5. This means the portfolio can have between (0,-1) exposure to the dollar.




To build a long-only portfolio we will choose (w_spx, w_10y)  (wi in [0,1]), sum(wi=1). In the long portfolio we are already implicitly long dollar (the assets are denominated in dollar and the value of the stocks and bonds is the expectation of future dollars so I don't see a need to place a bet on the DYX. Without DYX the long portfolios we make will be somewhat similar to familiar 60/40 strategies and are therefore easy to interpret.




For the short and long only portfolios we will consider how they perform versus cash - the excess returns…and versus each other.




To calculate weights (w_spx, w_10y, w_dxy) we first calculate the covariance matrix of the excess returns of each asset. In the code these are the “ER_SPX_d” type columns. In most of the charts I use a 252 day (~1 year) lookback window - i.e the cov. Matrix is based on last year of daily vol. Data. Weights are forward looking and recomputed daily.




Once we have the cov. matrix, we calculate risk parity weights with the above constraints, for both the long and short portfolio.”




Risk parity gives us a realistic benchmark for what a good, but non-proprietary portfolio would look like.
        
A big reason risk parity makes a "good" portfolio is that volatility has autoregressive structure. It's outside of the scope of this doc, but we could improve upon the naive implementation…(for example by having better models for future vol like with a GARCH model). Because of this I also calculated weights for the “best” portfolio. The best portfolio is the set of fix weights w* with the same constraints (wi in [0,-1]), sum(wi=-1),  w_dxy<⅕) that maximize the sharpe ratio over that window of time. In MPT this is just the actual tangency portfolio. The ideal weights are backwards looking…it’s what a PM with the same constraints, able to make one selection of weights, but with perfect information would pick.




The weights of the realistic best portfolio are somewhere between the risk parity weights and the ideal weights.
       
""")


st.markdown("---")


# 3. Backtest
st.markdown("### 3. Backtest")


# 3.1 When did short-all work?
st.text("")
st.markdown("##### When did short-all work?")


st.text("Below are some different visualizations of well the trade worked")


st.text("Perf Case Performance")
st.markdown("---")
df = get_data() 
fig_ert = create_returns_plot(df, select_col='ER_TANGENCY_Portfolio_SHORT', lookback_options=[6, 12, 24])
st.plotly_chart(fig_ert)
st.markdown("---")


st.text("Risk Parity Case Performance")
st.markdown("---")
df = get_data() 
fig_erp = create_returns_plot(df, select_col='ER_RP_Portfolio_SHORT', lookback_options=[6, 12, 24])
st.plotly_chart(fig_erp)
st.markdown("---")


st.text("When does the ideal short outperform the long RP?")
st.markdown("---")
df = get_data() 
fig_idelta = create_returns_plot(df, select_col='RET_IDEALSHORT_DELTA', lookback_options=[6, 12, 24])
st.plotly_chart(fig_idelta)
st.markdown("---")


st.text("When does the short RP outperform the long RP?")
st.markdown("---")
df = get_data() 
fig_rpdelta = create_returns_plot(df, select_col='RET_RPLONGSHORT_DELTA', lookback_options=[6, 12, 24])
st.plotly_chart(fig_rpdelta)
st.markdown("---")


st.text("Risk Parity Bubble Plot")
st.markdown("---")
fig_b=create_decade_scatter_plot(
   PLOT_FREQ_MONTHS=1,
   COLUMN_TO_PLOT='IRR_ER_RP_Portfolio_SHORT',
   WEIGHTS_TO_HOVER=['RP_SHORT_SPX','RP_SHORT_10Y','RP_SHORT_DXY'],
   MARKETS_TO_HOVER=['IRR_ER_SPX_d','IRR_ER_10Y_d','IRR_ER_DXY_d'],
   START_YEAR=1971,
   IRR_PERIOD_OPTIONS=[1, 3, 6, 12]  # List of IRR period options in months
)


st.plotly_chart(fig_b)
st.markdown("---")


# 3.3 Exogenous risks
st.text("")
st.markdown("##### Exogenous risks")
st.write("""
One important question asked in the case that I haven’t touched on is “ What are the characteristics of the payoff function?”


The very short answer is that the short portfolio is asymmetric in the wrong direction! It loses most of the time, and the longer you put on the trade the more likely it is to lose money. Theoretical upside is capped at a 2x, so-called infinite downside and so on.


But there’s another bigger problem, which is the better my theoretical returns are the less likely I am to actually get paid. As I approach a 2x return, the probability that I actually get that money approaches 0.


There are a lot of exogenous risks  that can mess up the trade. Even if these are typically small risks the better I expect my trade to do in theory the more I should expect to encounter these risks in practice.


> The exchange halts trading and I can’t exit the position


> The clearing house becomes illiquid and unwinds my trade


> The government steps in and bans short selling


> My counterparties become illiquid




Were there a crash in stocks, bonds, and dollars big enough to generate short returns in excess of 50%, maybe I’m walking away with 30% if I’m lucky.


I would argue that expected actual return conditioned on the theoretical return becomes negative when the theoretical return exceeds 65%. This happens all the time in crypto by the way ... .one might think it was a good idea to short SOL at the peak in 2021. But the only two places to go short were FTX and MangoMarkets. Both went bust and you ended up way down, despite 50%+ theoretical returns.


""")


st.markdown("---")


# 4. Why did the short-all work?
st.markdown("### 4. When does it work?")




st.write("""
There's no natural law that says going long stocks and bonds will produce 5% returns per year.  I think there are two things that underpin why the risk-parity long strategy has worked so well and so consistently .


One, Anglo-america has been on the winning side of every major international conflict since the War of Spanish Succession in the early 1700s. This regime has been unduly kind to the long-only risk parity style investing. They have tended to view commerce in an almost soteriological way:


Saw the Vision of the world, and all the wonder that would be;
Saw the heavens fill with commerce, argosies of magic sails,
Pilots of the purple twilight dropping down with costly bales


As a counterfactual, consider Russia (early 2000s) or China (early 2010s) both had periods of immense wealth creation, but this was not captured well by going long the countries stock market and bonds.   


Two, there’s a lot of money and it needs to go somewhere. Were we to look at when the short-all strategy worked normalized against M2 money supply, it would be far more compelling. There’s a lot of money and that money needs to go somewhere. The US being the de-facto market-makers for a bunch of commodities make it the obvious place for liquidity to go.


Were either of those assumptions to break...I think this becomes much much more viable. For now the best I can do is offer brief explanations for why the trade worked during certain periods.
""")
              
# 4.1 2022
st.text("")
st.write("""
        The trade performs well when there are suprise rate hikes. And more generally when rates are/are becoming inverted.


       """)
st.markdown("##### 2022")


st.write("""
Rates went up because there was a lot of inflation from covid. Partly because there was a record amount of money printed, partly because consumer spending went way down and then way back up, and partly because the companies cut production and there was a rush to turn back on production capacity.
Rates were sitting sub-zero in many developed economies, and sub 1% in the US. The Fed raised rates to counteract inflation. This became obvious in late 2021, I’m not sure why stocks didn’t drop more quickly. Bonds and Stocks both fall, which leads to okay returns for the short portfolio.


I'm surprised that stocks and bonds did not go down more at the end of 2021. I would expect to see vol. in the commodities and an increase in the cost of manufacturing inputs to have been priced in earlier. """)        
st.markdown("---")


# 5. Predictions for 2024
st.markdown("### 5. Predictions for next 18 months")


st.write("""
I think there are two possible catalysts that could happen, and if I had more conviction around would recommend going short.


**Tariffs**
       
The US in view of new geopolitical tensions decides it needs to strengthen specific parts of its defense and manufacturing sectors. They decide to use selective tariffs…Trump is promoting a 10% universal import tariff on all imports and a 60% tariff on China goods and while this is probably negotiation posturing, odds of protectionism scenarios are definitely rising in the US.
The first order effect is that a surge in tariffs increases prices for buyers and related producers. An increase in pricing across multiple key consumption areas has a good chance of increasing inflation.
The second order effect, which is much more interesting, is that countries may create segregated pools of liquidity. Consider a Chinese electric car company, with no US investment or US based revenue, which wants to open up a factory in Mexico. They may choose to withdraw their investment in Mexico over fears that the US, in the future, will pressure Mexico to apply the same tariffs. The Chinese EV company might choose to invest in Vietnam instead, even if the underlying economics of the factory are better in Mexico.


**Asset Seizure**
       
The US has already flirted with this during the Ukraine war. Were there another global conflict, it wouldn't be that surprising if the US decided that all Chinese and Russian owned real estate is now the property of the DOJ, or that the US is selectively defaulting on foreign owned bonds.
I think this would be neutral to bullish for US equities, but the dollar and the 10Y treasuries are likely to get hammered.


**Most Likely Scenario**
       
Recent returns in the S&P 500 (SPX) have been largely driven by the largest tech megacaps. Even small changes in the assumptions about their business performance could result in a significant drop in the SPX. Additionally, the yield curve remains inverted, which historically precedes a downturn in stocks.
The Fed is likely to cut interest rates, above current expectations. Dollar might weaken slightly. However, this weakening will be less pronounced than in previous similar rate drops due to the lack of better alternatives to the US dollar.


Recommendation: against the short-all strategy


""")





