import pandas as pd
import numpy as np

def calculate_windowed_returns(pct_series, window=252):
    """
    Daily Returns Pct --> Decimal Returns %

    Returns:
    pd.Series: Total returns index over the specified window.
    """
    # Calculate log returns
    log_returns = np.log1p(pct_series)
    
    # Calculate cumulative log returns over the window
    cumulative_log_returns = log_returns.rolling(window=window).sum()
    
    # Calculate total returns index
    pct_return = np.expm1(cumulative_log_returns)
    
    return pct_return


def calculate_windowed_annualized_returns(pct_series, window=252):
    """
    Daily Returns Pct --> Decimal Returns %

    Returns:
    pd.Series: Total returns index over the specified window.
    """
    log_returns = np.log1p(pct_series)
    cumulative_log_returns = log_returns.rolling(window=window).sum()
    pct_return = np.expm1(cumulative_log_returns)
    annual_return = pct_return * (252 / window)

    return annual_return

