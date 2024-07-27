###############################################################################
# This code generates the Supplementary Figure 9 of the paper "Longitudinal   #
# single-subject neuroimaging study reveals effects of daily environmental,   #
# physiological and lifestyle factors on functional brain connectivity"       #
#                                                                             #
# Data for this Figure is in the ./data/pilot_iii/behavioral folder           #
###############################################################################

import os
import pandas as pd
import numpy as np
from functools import reduce
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

######################### Pepare paths #######################################
path = './data/pilot_iii/behavioral/' 
savepath = './results/pilot_iii/SupplementaryFigure9.pdf'
##############################################################################

pilot = pd.read_csv(os.path.join(os.path.abspath(path),'sub-01_sensor-oura.csv'))
cmap = 'seismic'

##############################################################################
# 1. Correlation between measurements as divided by sleep, ANS, and physical activity
pilot.drop(columns=['date', 'Sleep Timing.1', 'Bedtime Start', 'Bedtime End', 'HRV Balance Score'], inplace=True)

corr = pilot.corr(method='pearson')
upt = corr.where(abs(np.triu(corr.values, k=0)) > 0.5, other=0)
lot = corr.where(abs(np.tril(corr.values, k=-1)) > 0, other=0)
dfs = [upt, lot]
corr = reduce(lambda x, y: x.add(y, fill_value=0), dfs)

sleep_cols = ['Total Bedtime', 'Total Sleep Time', 'Awake Time', 'Restless Sleep', 'Sleep Efficiency', 'Sleep Latency', 'Sleep Timing']
sleep = corr[sleep_cols]
sleep = sleep.loc[sleep_cols]

acti_cols = ['Activity Burn', 'Total Burn', 'Target Calories', 'Steps', 'Daily Movement',
       'Inactive Time', 'Rest Time', 'Low Activity Time', 'Medium Activity Time', 'High Activity Time', 'Non-wear Time',
       'Average MET', 'Long Periods of Inactivity']
activity = corr[acti_cols]
activity = activity.loc[acti_cols]

#Plot the results
fig = plt.figure(figsize=(8,4),dpi=300)
sns.set_style("dark")
sns.set_context(context="paper", font_scale=.4)
gs0 = fig.add_gridspec(1, 2)
ax0 = fig.add_subplot(gs0[0])
gs1 = gs0[1].subgridspec(2, 8)
ax1= fig.add_subplot(gs1[0,0:7])
ax2 = fig.add_subplot(gs1[1,0:7])
ax3 = fig.add_subplot(gs1[:,7])

sns.heatmap(corr, xticklabels=corr.columns.values,yticklabels=corr.columns.values, vmin=-1, vmax=1, cmap=cmap, square=True, cbar=False, ax=ax0)
sns.heatmap(sleep, xticklabels=sleep.columns.values,yticklabels=sleep.columns.values, vmin=-1, vmax=1, cmap=cmap, square=True, cbar=False, ax=ax1)
sns.heatmap(activity, xticklabels=activity.columns.values,yticklabels=activity.columns.values, vmin=-1, vmax=1, cmap=cmap, square=True, cbar=False, ax=ax2)
cmap = mpl.cm.seismic
norm = mpl.colors.Normalize(vmin=-1, vmax=1)
fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
             cax=ax3, orientation='vertical', label='Correlation coefficient')
plt.savefig(os.path.abspath(savepath))

#We see some high correlations between variables. It is worth discarding those 
#variables that are highly correlated so that it doesn't affect the PCA contribution

sleep_cols = ['Total Sleep Time', 'Awake Time', 'Restless Sleep', 'Sleep Efficiency', 'Sleep Latency']

acti_cols = ['Target Calories', 'Steps', 'Inactive Time', 'Rest Time', 'High Activity Time', 'Non-wear Time', 'Long Periods of Inactivity']
##############################################################################


#2 PCA contribution sleep
sleep = pilot[sleep_cols]
sleep.dropna(axis=0, inplace=True)
data = StandardScaler().fit_transform(sleep.values)
pca = PCA(n_components=3)
pca.fit(data)

print(f'Variance explained... {pca.explained_variance_ratio_}') #Check how much each PC explains the variance

pcs = abs(pca.components_)
num = -4 #the n first contributors to the PC
for i in range(len(pcs)):
    ind = np.argpartition(pcs[i], num)[num:]
    ind[np.argsort(pcs[i][ind])][::-1]
    names = [sleep_cols[index] for index in ind]
    print (f'For PC{i+1}, the variables that contribute the most are: {names}')

#2 PCA contribution activity
activity = pilot[acti_cols]
activity.dropna(axis=0, inplace=True)
data = StandardScaler().fit_transform(activity.values)
pca = PCA(n_components=4)
pca.fit(data)

print(f'Variance explained... {pca.explained_variance_ratio_}') #Check how much each PC explains the variance

pcs = abs(pca.components_)
num = -4 #the n first contributors to the PC
for i in range(len(pcs)):
    ind = np.argpartition(pcs[i], num)[num:]
    ind[np.argsort(pcs[i][ind])][::-1]
    names = [acti_cols[index] for index in ind]
    print (f'For PC{i+1}, the variables that contribute the most are: {names}')
