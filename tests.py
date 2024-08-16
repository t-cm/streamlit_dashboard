import pandas as pd
df= pd.read_pickle("./Data/processed_data.pkl")

#BOND RET
assert((-df['RET_10Y_d']+df['RET_FFR_d']).mean()==df['RET_SHORT_10Y_d'].mean(), "Bond Short 1Issue")
print((df['RET_10Y_d']-df['RET_FFR_d']).mean()-df['ER_10Y_d'].mean())
print((-df['RET_10Y_d']).mean()-df['ER_SHORT_10Y_d'].mean())