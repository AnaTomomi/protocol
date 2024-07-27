"""
This script compares fmriprep confounds.
            
Outputs: - Plot of correlations of confounds
         - R2 maps between the different strategies and the original data

    1. Plot the correlation between possible confounds
    2. Run GLM with motion parameters (Friston)
    3. Plot the before and after detrend plots
    
NOTE: The carpet plots require the original data, which is only available 
by writing to researchdata@aalto.fi. Therefore, the carpet plots will be left 
blank.

@author: ana.trianahoyos@aalto.fi
Created: 19.02.2021
Modified: 27.12.2021
Modified: 27.07.2024
"""

import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import cm
import matplotlib
import matplotlib.gridspec as gridspec
import numpy as np
from scipy import stats
import pickle
import nibabel as nib

from nilearn.plotting import plot_glass_brain

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


################################## User input needed ##########################
# Please modify this part 
path = './data/pilot_iii/fmri' 
savepath = './results/pilot_iii/'

###############################################################################
#No further modifications needed

# Load all the data
r_brain = nib.load(os.path.join(os.path.abspath(path),'r_brain.nii.gz'))
r_gs_brain = nib.load(os.path.join(os.path.abspath(path),'r_gs_brain.nii.gz'))

with open(os.path.join(os.path.abspath(path),'SF5_postpro.pickle'), 'rb') as handle:
    postpro = pickle.load(handle)['postpro']

with open(os.path.join(os.path.abspath(path),'SF5_postpro_det.pickle'), 'rb') as handle:
    postpro_det = pickle.load(handle)['postpro_det']

with open(os.path.join(os.path.abspath(path),'SF5_postpro_det_gs.pickle'), 'rb') as handle:
    postpro_det_gs = pickle.load(handle)['postpro_det_gs']
    
with open(os.path.join(os.path.abspath(path),'SF5_postpro_gs.pickle'), 'rb') as handle:
    postpro_gs = pickle.load(handle)['postpro_gs']

with open(os.path.join(os.path.abspath(path),'SF5_r.pickle'), 'rb') as handle:
    r = pickle.load(handle)['r']
        
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
        
nmap = ListedColormap([(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.656,0.863,0.707),(0.305,0.699,0.824),(0.031,0.344,0.617)])
plot_glass_brain(r_brain, threshold=0.5, cmap=nmap, vmax=1, annotate=False, colorbar=True, display_mode='lzry', figure=fig, axes=ax1)
        
ax2.plot(postpro_det_gs, c='darkorange', linestyle='-', linewidth=1, label='detrended only')
ax2.plot(postpro_gs, color='darkblue', linestyle='-', linewidth=1, label='denoised')
ax2.set_ylim(-1,1)
ax2.set_ylabel('GS')
ax2.set_xlabel('TR')
ax2.legend(ncol=3, loc='lower right', fontsize=10, frameon=False)
        
ax6.plot(stats.zscore(postpro_det), c='darkorange', linestyle='-', linewidth=1, label='voxel before')
ax6.plot(stats.zscore(postpro), c='darkblue', linestyle='-', linewidth=1, label='voxel after')
ax6.set_ylim(-5,5)
ax6.set_xlabel('TR')
ax6.set_ylabel('voxel signal')
ax6.legend(ncol=2, loc='lower right', fontsize=10, frameon=False)
        
#plot_carpet(orig_nii, mask, detrend=True, figure=fig, axes=ax3, vmin=-2, vmax=2, title='before confounds')
#plot_carpet(nii, mask, detrend=True, figure=fig, axes=ax4, vmin=-2, vmax=2, title='after confounds')
        
top = cm.get_cmap('Oranges_r', 4)
bottom = cm.get_cmap('Blues', 4)
newcolors = np.vstack((top(np.linspace(0, 1, 4)), bottom(np.linspace(0, 1, 4))))
nmap = ListedColormap(newcolors,'OrangeBlue')
plot_glass_brain(r_gs_brain, cmap=nmap, colorbar=True, plot_abs=False, vmin=-1, vmax=1, figure=fig, axes=ax5, annotate=False)

ax7.plot(stats.zscore(postpro), c='darkorange', linestyle='-', linewidth=1, label='voxel signal')
ax7.plot(postpro_gs, color='darkblue', linestyle='-', linewidth=1, label='global signal')
ax7.set_ylabel('signal')
ax7.set_xlabel('TR')
ax7.set_ylim(-5,5)
cor, _ = stats.pearsonr(stats.zscore(postpro[:,45609]),postpro_gs)
ax7.text(0,3,f'corr: {round(cor,3)}')
ax7.legend(ncol=2, loc='lower right', fontsize=10, frameon=False)
        
plt.savefig(os.path.join(os.path.abspath(savepath),'SupplementaryFigure5.pdf'), bbox_inches='tight')
        