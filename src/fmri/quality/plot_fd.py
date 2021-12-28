import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib

import numpy as np
import pandas as pd

path = '/m/cs/scratch/networks-pm/pilot_prepro/fmriprep/sub-01' 
savepath = '/m/cs/scratch/networks-pm/protocol/results/pilot_iii'

tasks = ['pvt', 'resting', 'movie', 'nback']
sessions = ['ses-04', 'ses-05', 'ses-06']

fd = {}
for session in sessions:
    fd[session] = {}
    for task in tasks:
        confound = pd.read_csv(os.path.join(path, f'{session}/func/sub-01_{session}_task-{task}_acq-highfreq_run-1_desc-confounds_timeseries.tsv'),sep='\t')
        fd[session][task] = confound['framewise_displacement']

fig, axes = plt.subplots(nrows=3, ncols=4, sharex=False, sharey=True, figsize=(12,8))
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)
for i, session in enumerate(fd.keys()):
    for j, task in enumerate(fd[session].keys()):
        ax = axes[i,j]
        num = (100*fd[session][task].where(fd[session][task]>0.2).count())/len(fd[session][task])
        ax = sns.lineplot(data=fd[session][task],x=np.linspace(0,len(fd[session][task]),num=len(fd[session][task])),y=fd[session][task],ax=ax)
        #ax.set_title(f'{round(num,2)}% of TRs affected')
        ax.set_ylabel("framewise \n displacement")
        ax.set_xlabel("TR")
        ax.hlines(y=0.2, xmin=0,xmax=len(fd[session][task]), linewidth=2,color='r',linestyle='dashed')
        ax.hlines(y=0.5, xmin=0,xmax=len(fd[session][task]), linewidth=2,color='r',linestyle='dashed')
        ax.set_ylim(0,0.6)
        if task=="resting":
            ax.set_xlim(0,706)
        if task=="nback":
            ax.set_xlim(0,630)
plt.savefig(os.path.join(savepath,'fd.pdf'), bbox_inches='tight')