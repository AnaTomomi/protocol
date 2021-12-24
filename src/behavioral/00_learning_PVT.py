import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

from statsmodels.tsa.stattools import adfuller
from sklearn.linear_model import LinearRegression

import seaborn as sns

path = "../../data/pilot_i/PVT/"
savepath = "../../results/pilot_i/"
os.chdir(path)

files = []
for file in os.listdir(path):
    if file.endswith("_pvt_log.txt"): 
        files.append(file)
files.sort()

performance = [None]*len(files)
median = [None]*len(files)
fast = [None]*len(files)
mean_1_RT = [None]*len(files)
slow_1_RT = [None]*len(files)
no_lapse_false = [None]*len(files)
lapse_prob = [None]*len(files)

for file in files:    
    pvt = pd.read_csv(file, sep="\t", header=[0])
    
    idx = int(file[-14:-12])-1
    
    pvt['1_RT'] = 1000/pvt.RT
    
    no_false = len(pvt[pvt['Category']=='false']) + len(pvt[pvt['RT']<=100])
    no_lapse = len(pvt[pvt['RT']>500])
    no_lapse_false[idx] = no_false + no_lapse
    performance[idx] = 1-(no_lapse_false[idx]/len(pvt))
    lapse_prob[idx] = no_lapse/(len(pvt) - no_false)
    
    pvt.drop(pvt[pvt.Category=="false"].index, inplace=True)
    
    median[idx] = pvt.RT.quantile(0.5)
    fast[idx] = pvt.RT.quantile(0.1)
    mean_1_RT[idx] = pvt["1_RT"].mean()
    slow_1_RT[idx] = pvt["1_RT"].quantile(0.9)
    print(file)

pvt_results = {"mean_1_RT": mean_1_RT, "median": median, "slow_1_RT": slow_1_RT,
               "fast": fast, "no_lapse_false": no_lapse_false, "lapse_prob": lapse_prob,
               "performance": performance}

pvt_results = pd.DataFrame.from_dict(pvt_results)

############################### Plot PVT #####################################
pvt_results["day"] = pvt_results.index +1
cols = ['mean_1_RT', 'slow_1_RT', 'median', 'fast', 'no_lapse_false', 
        'lapse_prob','performance']

fig, axes = plt.subplots(nrows=4, ncols=2, sharex=True, figsize=(5,6), dpi=300)
axes = axes.flatten()
sns.set_style("darkgrid")
#sns.set_style("ticks", {'axes.grid' : True, 'grid.linestyle': ':','font.family': ['Arial'], "font.size":"12"})
sns.set_theme(font="Arial")
for i, col in enumerate(cols):
    sns.lineplot(data=pvt_results, x="day", y=col, markers=True, dashes=False, ax=axes[i])
axes[7].set_visible(False)

axes[0].set_ylabel('1/s')
axes[1].set_ylabel('1/s')
axes[2].set_ylabel('ms')
axes[3].set_ylabel('ms')
axes[4].set_ylabel('events')
axes[5].set_ylabel('probability')
axes[6].set_ylabel('range')

axes[0].set_ylim(2.5,4)
axes[1].set_ylim(2.5,4)
axes[2].set_ylim(250, 360)
axes[3].set_ylim(250,360)
axes[4].set_ylim(-.5,10)
axes[5].set_ylim(-.005,.1)
axes[6].set_ylim(.9,1.1)

axes[5].xaxis.set_tick_params(labelbottom=True)
plt.xticks([0,5,10,15],["0","5","10","15"], color='k')

sns.despine()

axes[6].set_xlabel('day')
axes[5].set_xlabel('day')
fig.align_ylabels(axes)
fig.tight_layout()

plt.savefig(savepath+"PVT2.pdf")

################################ Test for stationarity #######################

for col in pvt_results.columns:
    result = adfuller(pvt_results[col].values)
    print(col)
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))
    print('............................................')
    
# We see some features are stationary, e.g. mean 1/RT (at p<0.05), number of lapses 
# (p<0.01), probability of lapses (p<0.05), and performance (p<0.01).

# For our analysis, we care about the RT and lapses (as they are modeled in the GLM for 
# the beta analysis). 

# The ADF stationarity test was a good start, however, there may be some external 
# factors affecting the measurement, e.g. sleep. Therefore, to really assess if there is 
# a learning effect we need to check if there is a trend that is making the RTs 
# faster (e.g. if we could fit a line with a negative slope). 

################################# Trend ######################################
for col in cols:
    x = pvt_results["day"].values
    x = x.reshape(-1,1)
    y = pvt_results[col].values
    reg = LinearRegression().fit(x, y)
    print(f'Regression stats for {col}')
    print(f'reg. coef: {reg.coef_}')
    print(f'coef. of determination: {reg.score(x, y)}')
    print("+++++++++++++++++++++++++++++++++++++++++++++")
