import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import os
import re

from statsmodels.tsa.stattools import adfuller
from sklearn.linear_model import LinearRegression

import matplotlib.transforms as mtransforms

datapath = "/u/68/trianaa1/unix/trianaa1/protocol/"
os.chdir(datapath)

def get_dual_data(dfs):
    stats_data = []
    for key, df in dfs.items():
        counts = df[' change_correct '].value_counts().to_frame().T
        stats_data.append(counts)
    stats = pd.concat(stats_data, ignore_index=True)
    stats.rename(columns={'1':'correct','5':'missing','0':'wrong'}, inplace=True)
    stats['days'] = range(1,15)
    return stats

def extract_thresholds(text):
    pattern = r"Block type:\s*DD1.*?threshold:\s*([\d\.]+).*?threshold:\s*([\d\.]+)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        aud_threshold, vis_threshold = match.groups()
        return {'auditory': float(aud_threshold), 'visual': float(vis_threshold)}
    else:
        return {'auditory': None, 'visual': None}


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
days2back = dict()
for file in twoback:
    content = pd.read_csv(file, delimiter="\t", header=None, names=range(16))
    #select only those 60 trials of the DD1
    dd1_start_index = content.index[content.apply(lambda row: row.astype(str).str.contains('Block type:').any() and 'DD1' in row.astype(str).values, axis=1)].tolist()
    dd1_start_index = dd1_start_index[0]+1
    dd1_end_index = dd1_start_index + 61 
    tables = content.iloc[dd1_start_index:dd1_end_index]
    #set the header
    new_header = tables.iloc[0]  
    tables = tables[1:]  
    tables.columns = new_header 
    days2back[int(file[-36:-34])] = tables
    print(file)

days1back = dict()
for file in oneback:
    content = pd.read_csv(file, delimiter="\t", header=None, names=range(16))
    #select only those 60 trials of the DD1
    dd1_start_index = content.index[content.apply(lambda row: row.astype(str).str.contains('Block type:').any() and 'DD1' in row.astype(str).values, axis=1)].tolist()
    dd1_start_index = dd1_start_index[0]+1
    dd1_end_index = dd1_start_index + 61 
    tables = content.iloc[dd1_start_index:dd1_end_index]
    #set the header
    new_header = tables.iloc[0]  
    tables = tables[1:]  
    tables.columns = new_header 
    days1back[int(file[-30:-28])] = tables
    print(file)
   
# Get the task difficulty
d2 = []
for file in os.listdir(datapath):
    if file.endswith("_2back_OnlyNovels_fMRI_summary.txt"):
        d2.append(file)
d2.sort()

d1 = []
for file in os.listdir(datapath):
    if file.endswith("_OnlyNovels_fMRI_summary.txt"):
        if not file.endswith("_2back_OnlyNovels_fMRI_summary.txt"):
            d1.append(file)
d1.sort()

d2back = dict()
for f in d2:
    with open(f, 'r') as file:
        text_data = file.read()
    thresholds = extract_thresholds(text_data)
    


#Get the results
label = ["A", "B", "C", "D"]
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)

fig, axes = plt.subplots(nrows=2, ncols=2, sharex=False, figsize=(6,6))
axes = axes.flatten()
trans = mtransforms.ScaledTranslation(-20/72, 7/72, fig.dpi_scale_trans)
axes[0].text(0.0, 1.0, label[0], transform=axes[0].transAxes + trans, va='bottom')
stats = get_dual_data(days1back)
stats.plot(x="days",y=["wrong","correct","missing"], kind="line", style='-o', ax=axes[0])
axes[0].legend(loc='upper right', ncol=3)
axes[0].set_ylabel('count')
axes[0].set_ylim([0,60])

axes[1].text(0.0, 1.0, label[1], transform=axes[1].transAxes + trans, va='bottom')
stats = get_dual_data(days2back)
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
