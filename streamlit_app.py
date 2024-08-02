import streamlit as st
import pandas as pd
import math
from pathlib import Path
from window_functions import calculate_windowed_returns, calculate_windowed_annualized_returns


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

# @st.cache_data
def get_data():
    df= pd.read_pickle("./Data/processed_data.pkl")
    return df.head(5)


##APP
df=get_data()
print(df.columns)

# df.head(2)



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

In this document, we'll explore the 'short-everything' strategy—a portfolio weighted between short positions on the S&P 500, 10-year Treasuries, and leveraged Dollar Index (DXY). Our analysis will unfold as follows:

1. **Historical Performance**: How have stocks, bonds, DXY, and cash have performed since approximately 1971? 
2. **Portfolio Construction**: How do we size the bet? How we'll has it worked in the past?
3. **Historical Reconstruction**: When it worked...why did it work?
4. **Prediction**: How bad of an idea is it to put on this trade in 2024H2? What things might I belive that would make this a good trade?
---

'''
# -----------------------------------------------------------------------------
# Declare some useful functions.
