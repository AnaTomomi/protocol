import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

from statsmodels.tsa.stattools import adfuller

import seaborn as sns
sns.set_style("ticks",{'axes.grid' : True, 'grid.linestyle': ':','font.family': ['Arial'],})

path = "/u/68/trianaa1/unix/trianaa1/Longitudinal/data/miniplot/PVT/"
savepath = "/u/68/trianaa1/unix/trianaa1/Longitudinal/results/minipilot/"
sheet_name = 'pilot'
os.chdir(path)

files = []
for file in os.listdir(path):
    if file.endswith("_pvt_log.txt"): #pvt_dual_log.txt
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
pvt_results.to_excel(f'{savepath}pvt_scores.xlsx', sheet_name=sheet_name)