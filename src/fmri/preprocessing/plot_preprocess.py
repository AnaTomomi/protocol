"""
This script compares fmriprep confounds.

Requirements: 
            - fmriprep folder
            - savepath where the plots (outcomes) should be stored
            - subject label for which the plots will be compared
            - strategies for which you would like to compare
            - TR of the sequences
            
Outputs: - Plot of correlations of confounds
         - R2 maps between the different strategies and the original data

@author: ana.trianahoyos@aalto.fi
Created: 19.02.2021
Modified: 27.12.2021
"""

import os
import sys
import glob
import re
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import cm
import matplotlib
import matplotlib.gridspec as gridspec
import pandas as pd
import json
import numpy as np
import scipy.io
from scipy import stats
from scipy.signal import detrend

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from nilearn.image import clean_img, smooth_img
from nilearn.plotting import plot_stat_map, plot_carpet, plot_glass_brain
from nilearn.masking import apply_mask

import nibabel as nib

sys.path.append('/m/cs/scratch/networks-pm/Longitudinal/src/fmri_func/preprocessing')
from step5_denoise import get_confounds, compute_r2_maps, vector2brain

################################## User input needed ##########################
# Please modify this part 
path = '/m/cs/scratch/networks-pm/pilot_prepro/denoise/' 
conf_path = '/m/cs/scratch/networks-pm/pilot_prepro/fmriprep' 
biopacpath = '/m/cs/scratch/networks-pm/Longitudinal/results/pilot/biopac'
savepath = '/m/cs/scratch/networks-pm/protocol/results/pilot_iii/'
subject = 'sub-01'
strategies = ['24HMP-8Phys-Spike']
#strategies = ['24HMP+8Phys','24HMP+8Phys+4GSR','12HMP+aCompCor','12HMP+aCompCor+4GSR','24HMP+8Phys+Spike','24HMP+8Phys+4GSR+Spike','ICA-AROMA+2Phys','ICA-AROMA+2Phys+GSR']
tr = 0.594
###############################################################################
#No further modifications needed

'''1. Plot the correlation between possible confounds
   2. Run GLM with motion parameters (Friston)
   3. Plot the before and after detrend plots'''

tasks = ['pvt', 'resting', 'movie', 'nback', 'pvt', 'resting', 'movie', 'nback', 'pvt', 'resting', 'movie', 'nback']                                                          
sessions = ['ses-05', 'ses-05', 'ses-05', 'ses-05', 'ses-06', 'ses-06', 'ses-06', 'ses-06', 'ses-04', 'ses-04', 'ses-04', 'ses-04']
  
#task=tasks[-1]
#session=sessions[-1]
#strategy =strategies[2]

for task, session in zip(tasks, sessions):
    for strategy in strategies:                                                                                                
        print(strategy)
        orig_nii = os.path.join(conf_path, subject, session, 'func',  f'{subject}_{session}_task-{task}_acq-highfreq_run-1_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz')
        nii = os.path.join(path, subject, session, f'{subject}_{session}_task-{task}_acq-highfreq_run-1_denoised-{strategy}_HPF.nii')
        mask = os.path.join(conf_path, subject, session, 'func',  f'{subject}_{session}_task-{task}_acq-highfreq_run-1_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii.gz')
        confounds = pd.read_csv(os.path.join(conf_path, subject, session, 'func', f'{subject}_{session}_task-{task}_acq-highfreq_run-1_desc-confounds_timeseries.tsv'),sep='\t')
        with open(os.path.join(conf_path, subject, session, 'func', f'{subject}_{session}_task-{task}_acq-highfreq_run-1_desc-confounds_timeseries.json')) as f:
            confounds_json = json.load(f)
        if "ICA" in strategy:
            nii_det = os.path.join(path, subject, session, f'{subject}_{session}_task-{task}_acq-highfreq_run-1_SGdetrend_smoothed.nii')
        else:
            nii_det = os.path.join(path, subject, session, f'{subject}_{session}_task-{task}_acq-highfreq_run-1_SGdetrend.nii')
        
        print(f'Plotting R2 maps for task {task}')
        confound = get_confounds(confounds, confounds_json, strategy)
        if os.path.isfile(os.path.join(biopacpath, subject, session, f'{subject}_{session}_task-{task}_run-1_biopac-downsampledcut.mat')):
            down_tr = scipy.io.loadmat(os.path.join(biopacpath, subject, session, f'{subject}_{session}_task-{task}_run-1_biopac-downsampledcut.mat'))
            down_tr = down_tr['downsampled_cut']
            confound['breath'] = np.transpose(down_tr[0,:])
            confound['heart'] = np.transpose(down_tr[1,:])
        confound.fillna(0, inplace=True)
        confound = confound.to_numpy()
        
        print('Computing the r2 maps...')
        postpro = apply_mask(nii, mask)
        postpro_det = apply_mask(nii_det, mask)
        postpro_gs = np.mean(stats.zscore(postpro),1) #This is ok. Enrico certified.
        postpro_det_gs = np.mean(stats.zscore(postpro_det),1)
        orig_gs = stats.zscore(confounds['global_signal'])
        
        #r,_,n = compute_r2_maps(det_filt_img, mask, regconf_img, vector=False) #ok. This function is ok :)
        r = np.zeros(postpro_det.shape[1])
        p = np.zeros(postpro_det.shape[1])
        for j in range(postpro_det.shape[1]):
            r[j], p[j] = stats.pearsonr(postpro_det[:,j],postpro[:,j]) 
        r = 1-np.square(r)
        n = (r>0.5).sum()/len(r) 
        r_brain = vector2brain(r,mask)
        
        print('Computing R^2 maps for the global signal...')
        r_gs = np.zeros(postpro_det.shape[1])
        p = np.zeros(postpro_det.shape[1])
        for j in range(postpro.shape[1]):
            r_gs[j], p[j] = stats.pearsonr(postpro[:,j],postpro_gs) #this is ok, checked with Enrico's notes
        r_gs_brain = vector2brain(r_gs,mask)
        
        font = {'size': 12}
        matplotlib.rc('font', **font)
        
        fig = plt.figure(figsize=(12,10))
        gs = gridspec.GridSpec(3, 4)
        ax0 = plt.subplot(gs[0,3])
        ax1 = plt.subplot(gs[0,0:3])
        gs0 = gs[1,0:2].subgridspec(4, 1)#plt.subplot(gs[1,0:2])
        ax2 = plt.subplot(gs0[0:2,0])
        ax6 = plt.subplot(gs0[2:4,0])
        ax3 = plt.subplot(gs[1,2:4])
        ax4 = plt.subplot(gs[2,2:4])
        gs1 = gs[2,0:2].subgridspec(2, 1)
        ax5 = plt.subplot(gs1[0,0])
        ax7 = plt.subplot(gs1[1,0])
        
        bins = np.linspace(0,1,11)
        ax0.hist(r,bins=bins)
        ax0.set_ylim(0,87000)
        ax0.set_xlabel('Correlation')
        ax0.set_ylabel('Number of voxels')
        ax0.set_title(f'ratio of voxels affected: {round(n,3)}')
        
        nmap = ListedColormap([(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.656,0.863,0.707),(0.305,0.699,0.824),(0.031,0.344,0.617)])
        plot_glass_brain(r_brain, threshold=0.5, cmap=nmap, vmax=1, annotate=False, colorbar=True, display_mode='lzry', figure=fig, axes=ax1, title=f'{strategy}-HR-RR')
        
        #ax2.plot(orig_gs, color='tab:blue', linestyle='-',linewidth=1, label='original')
        ax2.plot(postpro_det_gs, c='darkorange', linestyle='-', linewidth=1, label='detrended only')
        ax2.plot(postpro_gs, color='darkblue', linestyle='-', linewidth=1, label='denoised')
        ax2.set_ylim(-1,1)
        ax2.set_ylabel('GS')
        ax2.set_xlabel('TR')
        ax2.legend(ncol=3, loc='lower right', fontsize=10, frameon=False)
        
        ax6.plot(stats.zscore(postpro_det[:,45609]), c='darkorange', linestyle='-', linewidth=1, label='voxel before')
        ax6.plot(stats.zscore(postpro[:,45609]), c='darkblue', linestyle='-', linewidth=1, label='voxel after')
        ax6.set_ylim(-5,5)
        ax6.set_xlabel('TR')
        ax6.set_ylabel('voxel signal')
        ax6.legend(ncol=2, loc='lower right', fontsize=10, frameon=False)
        
        plot_carpet(orig_nii, mask, detrend=True, figure=fig, axes=ax3, vmin=-2, vmax=2, title='before confounds')
        plot_carpet(nii, mask, detrend=True, figure=fig, axes=ax4, vmin=-2, vmax=2, title='after confounds')
        
        top = cm.get_cmap('Oranges_r', 4)
        bottom = cm.get_cmap('Blues', 4)
        newcolors = np.vstack((top(np.linspace(0, 1, 4)), bottom(np.linspace(0, 1, 4))))
        nmap = ListedColormap(newcolors,'OrangeBlue')
        plot_glass_brain(r_gs_brain, cmap=nmap, colorbar=True, plot_abs=False, vmin=-1, vmax=1, figure=fig, axes=ax5, annotate=False)

        ax7.plot(stats.zscore(postpro[:,45609]), c='darkorange', linestyle='-', linewidth=1, label='voxel signal')
        ax7.plot(postpro_gs, color='darkblue', linestyle='-', linewidth=1, label='global signal')
        ax7.set_ylabel('signal')
        ax7.set_xlabel('TR')
        ax7.set_ylim(-5,5)
        cor, _ = stats.pearsonr(stats.zscore(postpro[:,45609]),postpro_gs)
        ax7.text(0,3,f'corr: {round(cor,3)}')
        ax7.legend(ncol=2, loc='lower right', fontsize=10, frameon=False)
        
        fig.suptitle(task)
        plt.tight_layout()
        plt.savefig(os.path.join(savepath,f'{session}-{task}-{strategy}.pdf'), bbox_inches='tight')
        plt.close()
    print(f'session {session} - task {task} done!')
        