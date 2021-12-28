import os
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import warnings
import numpy as np

from nilearn.image import get_data, new_img_like
from nilearn.plotting import plot_stat_map
from nilearn.masking import apply_mask

import nibabel as nib

from scipy import stats


def get_acompcorr(confounds, confounds_json):
    '''
    Gets the first 5 components from the white matter and the first 5 components
    from the CSF
    
    Inputs: dataframe of confounds, confounds json file from fmriprep
    Returns: list of components
    '''
    
    aCompCorr = [col for col in confounds if col.startswith('a_comp_cor')]
    aCompCorrCSFWM = []
    no_comp = 0
    while no_comp<5:
        if confounds_json[aCompCorr[no_comp]]['Mask']=='CSF':
            aCompCorrCSFWM.append(aCompCorr[no_comp])
            no_comp = no_comp+1         
            
    no_comp=0
    for comp in aCompCorr:
        if confounds_json[comp]['Mask']=='WM' and no_comp<5:
            aCompCorrCSFWM.append(comp)
            no_comp = no_comp+1
    
    return aCompCorrCSFWM

def get_acompcorr50(confounds, confounds_json):
    '''
    Gets the first components that sum up 50% of the explained variance from 
    the WM and from CSF, respectively.
    
    Inputs: dataframe of confounds, confounds json file from fmriprep
    Returns: list of components
    '''
    aCompCorr = [col for col in confounds if col.startswith('a_comp_cor')]
    aCompCorrCSFWM = []
    var = 0     
    for comp in aCompCorr:
        if confounds_json[comp]['Mask']=='CSF' and var<0.5:
            aCompCorrCSFWM.append(comp)
            var = var+confounds_json[comp]['VarianceExplained']
    var = 0     
    for comp in aCompCorr:
        if confounds_json[comp]['Mask']=='WM' and var<0.5:
            aCompCorrCSFWM.append(comp)
            var = var+confounds_json[comp]['VarianceExplained']
    
    return aCompCorrCSFWM

def get_ICAnoise(confounds,confounds_json):
    '''
    Gets the ICA components labeled as noise
    
    Inputs: dataframe of confounds, confounds json file from fmriprep
    Returns: list of components
    '''
    ica = [col for col in confounds if col.startswith('aroma_motion')]
    ica = list(map(lambda x: x.replace('_0','_').replace('_0','_'),ica))
    ica_aroma = []
    for comp in ica:
        if confounds_json[comp]['MotionNoise']:
            ica_aroma.append(comp)
    if len(ica_aroma)!=len(ica):
        warnings.warn("Warning! The number of Noise ICA components does not match the ones listed in the confounds matrix. Proceed with care.")
    ica = [col for col in confounds if col.startswith('aroma_motion')]
    return ica

def get_spike(confounds):
    '''
    Gets the TRs where high motion was detected
    
    Inputs: dataframe of confounds, confounds json file from fmriprep
    Returns: list of components
    '''
    spike = [col for col in confounds if col.startswith('motion_outlier')]
    return spike

def get_confounds(confounds, confounds_json, strategy):
    '''
    Gets the list of confounds according to the input strategy.
    
    Inputs: dataframe of confounds, confounds json file from fmriprep, strategy (string)
    Returns: dataframe of selected confounds
    '''
    
    #Forming some lists to make the code less heavy
    trans_rot = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z']
    friston = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z',
               'trans_x_derivative1','trans_y_derivative1','trans_z_derivative1',
               'trans_x_power2','trans_y_power2','trans_z_power2',
               'trans_x_derivative1_power2','trans_y_derivative1_power2','trans_z_derivative1_power2',
               'rot_x_derivative1','rot_y_derivative1','rot_z_derivative1',
               'rot_x_power2','rot_y_power2','rot_z_power2',
               'rot_x_derivative1_power2','rot_y_derivative1_power2','rot_z_derivative1_power2']
    phys8 = ['csf','csf_derivative1','csf_power2','csf_derivative1_power2',
             'white_matter','white_matter_derivative1','white_matter_power2','white_matter_derivative1_power2']
    if '6HMP'==strategy:
        conf2plot = confounds[trans_rot]
    elif '6HMP-2Phys'==strategy:
        all_confounds = trans_rot + ['csf','white_matter']
        conf2plot = confounds[all_confounds]
    elif '6HMP-2Phys-GSR'==strategy:
        all_confounds = trans_rot + ['csf','white_matter','global_signal']
        conf2plot = confounds[all_confounds]
    elif '24HMP'==strategy:
        conf2plot = confounds[friston]
    elif '24HMP-8Phys'==strategy:
        all_confounds = friston + phys8
        conf2plot = confounds[all_confounds]
    elif '24HMP-8Phys-4GSR'==strategy:
        all_confounds = friston + phys8 + ['global_signal','global_signal_derivative1',
                                              'global_signal_derivative1_power2','global_signal_power2']
        conf2plot = confounds[all_confounds]
    elif '24HMP-aCompCor'==strategy:
        all_confounds = friston + get_acompcorr(confounds,confounds_json)
        conf2plot = confounds[all_confounds]
    elif '24HMP-aCompCor-4GSR'==strategy:
        all_confounds = friston + get_acompcorr(confounds,confounds_json) + ['global_signal',
                            'global_signal_derivative1', 'global_signal_derivative1_power2','global_signal_power2']
        conf2plot = confounds[all_confounds]
    elif '24HMP-aCompcor50'==strategy:
        all_confounds = friston + get_acompcorr50(confounds,confounds_json)
        conf2plot = confounds[all_confounds]
    elif '24HMP-aCompcor50-4GSR'==strategy:
        all_confounds = friston + get_acompcorr50(confounds,confounds_json) + ['global_signal',
                            'global_signal_derivative1', 'global_signal_derivative1_power2','global_signal_power2']
        conf2plot = confounds[all_confounds]
    elif '12HMP-aCompCor'==strategy:
        all_confounds = trans_rot + ['trans_x_derivative1','trans_y_derivative1',
                                         'trans_z_derivative1','rot_x_derivative1','rot_y_derivative1',
                                         'rot_z_derivative1'] + get_acompcorr(confounds,confounds_json)
        conf2plot = confounds[all_confounds]
    elif '12HMP-aCompCor-4GSR'==strategy:
        all_confounds = trans_rot + ['trans_x_derivative1','trans_y_derivative1',
                                         'trans_z_derivative1','rot_x_derivative1','rot_y_derivative1',
                                         'rot_z_derivative1','global_signal','global_signal_derivative1',
                                         'global_signal_derivative1_power2','global_signal_power2'] + get_acompcorr(confounds,confounds_json)
        conf2plot = confounds[all_confounds]
    elif '12HMP-aCompCor50'==strategy:
        all_confounds = trans_rot + ['trans_x_derivative1','trans_y_derivative1',
                                         'trans_z_derivative1','rot_x_derivative1','rot_y_derivative1',
                                         'rot_z_derivative1'] + get_acompcorr50(confounds,confounds_json)
        conf2plot = confounds[all_confounds]
    elif 'ICA-AROMA-2Phys'==strategy:
        all_confounds = get_ICAnoise(confounds,confounds_json) + ['csf','white_matter']
        conf2plot = confounds[all_confounds]
    elif 'ICA-AROMA-2Phys-GSR'==strategy:
        all_confounds = get_ICAnoise(confounds,confounds_json) + ['csf','white_matter','global_signal']
        conf2plot = confounds[all_confounds]
    elif 'ICA-AROMA-8Phys'==strategy:
        all_confounds = get_ICAnoise(confounds,confounds_json) + phys8
        conf2plot = confounds[all_confounds]
    elif 'ICA-AROMA-8Phys-4GSR'==strategy:
        all_confounds = get_ICAnoise(confounds,confounds_json) + phys8 + ['global_signal','global_signal_derivative1',
                                              'global_signal_derivative1_power2','global_signal_power2']
        conf2plot = confounds[all_confounds]
    elif '24HMP-8Phys-4GSR-Spike'==strategy:
        all_confounds = friston + phys8 + get_spike(confounds) + ['global_signal','global_signal_derivative1',
                                              'global_signal_derivative1_power2','global_signal_power2']
        conf2plot = confounds[all_confounds]
    elif '24HMP-8Phys-Spike'==strategy:
        all_confounds = friston + phys8 + get_spike(confounds)
        conf2plot = confounds[all_confounds]
    elif 'ICA-AROMA-Spike'==strategy:
        all_confounds = get_ICAnoise(confounds,confounds_json) + get_spike(confounds)
        conf2plot = confounds[all_confounds]
    elif 'for_plotting_only'==strategy:
        all_confounds = friston + get_ICAnoise(confounds,confounds_json) + phys8 + ['global_signal',
                    'global_signal_derivative1','global_signal_derivative1_power2','global_signal_power2']
        conf2plot = confounds[all_confounds]
    else:
        raise NameError('Denoising strategy not found. Please check the available strategies')
        
    return conf2plot

def compute_r2_maps(nii, mask, predicted, vector=False):
    '''
    Computes the r2 maps between two images. R2 maps are the correlation between
    those images, voxel-wise.
    
    Inputs: reference image, brain mask, image to correlate
    Returns: array of correlation coefficient (r), p-values (p), and number of voxels affectec (n)
    '''
    
    nii_masked = apply_mask(nii, mask)
    r = np.zeros(nii_masked.shape[1])
    p = np.zeros(nii_masked.shape[1])
    if vector==False:
        predicted_masked = apply_mask(predicted, mask)
        for j in range(nii_masked.shape[1]):
            r[j], p[j] = stats.pearsonr(nii_masked[:,j],predicted_masked[:,j]) 
    else:
        for j in range(nii_masked.shape[1]):
            r[j], p[j] = stats.pearsonr(nii_masked[:,j],predicted)
    r = 1-np.square(r)
    n = (r>0.5).sum()/len(r) 
    return r,p,round(n,2)
    

def plot_r2_maps(mask, r, savepath, name, title, thres=None):
    '''
    plot the r2 maps between two images. R2 maps are the correlation between
    those images, voxel-wise.
    
    Inputs: correlation values (r), brain mask, savepath (str), name for the
            plot to be saved (str), title for the plot (str)
    Returns: figure
    '''
    if thres==None:
        thres=0.5
    data_model = get_data(mask)
    idx = np.argwhere(data_model != 0)
    brain_r2 = np.zeros(data_model.shape)
    for n in range(len(r)):
        brain_r2[idx[n][0],idx[n][1],idx[n][2]] = r[n]
    brain_r2_plot = new_img_like(mask,brain_r2,copy_header=True)
    nib.save(brain_r2_plot, os.path.join(savepath,name))
    
    #cmap = ListedColormap([(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.656,0.863,0.707),(0.305,0.699,0.824),(0.031,0.344,0.617)])
    if thres==0.5:
        nmap = ListedColormap([(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.656,0.863,0.707),(0.305,0.699,0.824),(0.031,0.344,0.617)])
    else:
        nmap = ListedColormap([(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.859,0.859,0.859),(0.938,0.973,0.906),(0.727,0.891,0.734),(0.48,0.797,0.766),(0.262,0.633,0.789),(0.031,0.406,0.672)])
    
    fig, ax1 = plt.subplots(nrows=1,ncols=1)
    plot_stat_map(brain_r2_plot, threshold=thres, display_mode='z', figure=fig, cmap=nmap, vmax=1, axes=ax1, title=title, annotate=False)
    return fig

def vector2brain(vector,mask):
    '''
    Convert a vector to a brain representation based on a mask.
    
    Inputs: correlation values (r), brain mask
    Returns: NiftiImage
    '''
    data_model = get_data(mask)
    idx = np.argwhere(data_model != 0)
    brain_r2 = np.zeros(data_model.shape)
    for n in range(len(vector)):
        brain_r2[idx[n][0],idx[n][1],idx[n][2]] = vector[n]
    brain_r2_plot = new_img_like(mask,brain_r2,copy_header=True)
    return brain_r2_plot
