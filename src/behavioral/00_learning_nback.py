import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import os

from statsmodels.tsa.stattools import adfuller
from sklearn.linear_model import LinearRegression

import matplotlib.transforms as mtransforms

datapath = "/u/68/trianaa1/unix/trianaa1/protocol/data/pilot_i/nback/s1/"
os.chdir(datapath)

def get_dual_data(stim2back):
    count=1
    for key in stim2back["DD1"]:
        print(key)
        stat = stim2back["DD1"][key].groupby([" change_correct "]).size().to_frame().T
        if count==1:
            stats = stat
        else:
            stats = pd.concat([stats,stat])
        count = count+1
    stats = stats.rename(columns={"0": "wrong", "1": "correct", "5":"missing"})
    stats = stats.reset_index()
    stats = stats.drop(columns=["index"])
    stats["days"] = range(1,len(stats)+1)
    return stats

def adf(stats, cols):
    for col in cols:
        result = adfuller(stats[col].values)
        print(col)
        print('ADF Statistic: %f' % result[0])
        print('p-value: %f' % result[1])
        print('Critical Values:')
        for key, value in result[4].items():
            print('\t%s: %.3f' % (key, value))
        print('............................................')

def linear(stats, cols):
    for col in cols:
        x = stats["days"].values
        x = x.reshape(-1,1)
        y = stats[col].values
        reg = LinearRegression().fit(x, y)
        print(f'Regression stats for {col}')
        print(f'reg. coef: {reg.coef_}')
        print(f'coef. of determination: {reg.score(x, y)}')
        print("+++++++++++++++++++++++++++++++++++++++++++++")

twoback = []
for file in os.listdir(datapath):
    if file.endswith("_2back_OnlyNovels_fMRI_rawdata.txt"):
        twoback.append(file)
twoback.sort()

oneback = []
for file in os.listdir(datapath):
    if file.endswith("_OnlyNovels_fMRI_rawdata.txt"):
        if not file.endswith("_2back_OnlyNovels_fMRI_rawdata.txt"):
            oneback.append(file)
oneback.sort()

#Organize the data in dictionaries
table_names = ["DD1"]
days2back = dict()
for file in twoback:
    content = pd.read_csv(file, delimiter="\t", header=None, names=range(16))
    groups = content[1].isin(table_names).cumsum()
    tables = dict()
    for k,g in content.groupby(groups):
        df = g.iloc[1:]
        df = df.reset_index(drop=True)
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        tables[g.iloc[0,1]] = df
    days2back[int(file[-36:-34])] = tables
    print(file)

days1back = dict()
for file in oneback:
    content = pd.read_csv(file, delimiter="\t", header=None, names=range(16))
    groups = content[1].isin(table_names).cumsum()
    tables = dict()
    for k,g in content.groupby(groups):
        df = g.iloc[1:]
        df = df.reset_index(drop=True)
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        tables[g.iloc[0,1]] = df
    days1back[int(file[-30:-28])] = tables
    print(file)
    
#Flip the info to store per stimuli
stim2back = dict()
for name in table_names:
    stim2back[name] = dict()
    for key in days2back:
        stim2back[name][key] = days2back[key][name]
        print(key, name)

stim1back = dict()
for name in table_names:
    stim1back[name] = dict()
    for key in days1back:
        stim1back[name][key] = days1back[key][name]
        print(key, name) 

#Get the results
label = ["A", "B"]
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)

fig, axes = plt.subplots(nrows=2, ncols=1, sharex=False, figsize=(6,6))
trans = mtransforms.ScaledTranslation(-20/72, 7/72, fig.dpi_scale_trans)
axes[0].text(0.0, 1.0, label[0], transform=axes[0].transAxes + trans, va='bottom')
stats = get_dual_data(stim1back)
stats.plot(x="days",y=["wrong","correct","missing"], kind="line", style='-o', ax=axes[0])
axes[0].legend(loc='upper right', ncol=3)
axes[0].set_ylabel('count')
axes[0].set_ylim([0,60])

axes[1].text(0.0, 1.0, label[1], transform=axes[1].transAxes + trans, va='bottom')
stats = get_dual_data(stim2back)
stats.plot(x="days",y=["wrong","correct","missing"], kind="line", style='-o', ax=axes[1])
axes[1].legend(loc='upper right', ncol=3)
axes[1].set_ylabel('count')
axes[1].set_ylim([0,60])

sns.despine()
fig.align_ylabels(axes)
fig.tight_layout()
plt.savefig('/u/68/trianaa1/unix/trianaa1/protocol/results/pilot_i/nback.pdf')

############################## Linear model ##################################
cols = list(stats.columns)
cols.pop(-1)
print("..........Results for 1-back.........")
stats = get_dual_data(stim1back)
adf(stats, cols)

print("..........Results for 2-back..........")
stats = get_dual_data(stim2back)
adf(stats, cols)    
################################# Trend ######################################
print("..........Results for 1-back.........")
stats = get_dual_data(stim1back)
linear(stats, cols)

print("..........Results for 2-back..........")
stats = get_dual_data(stim2back)
linear(stats, cols)
