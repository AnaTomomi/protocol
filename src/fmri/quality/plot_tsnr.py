import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib
import numpy as np
import pandas as pd

import nibabel as nib

from nilearn.input_data import NiftiLabelsMasker
from nilearn import image
from nilearn.plotting import plot_glass_brain

from itertools import combinations

def symmetrical_colormap(cmap_settings, new_name = None ):
    ''' This function take a colormap and create a new one, as the concatenation of itself by a symmetrical fold.
    '''
    # get the colormap
    cmap = plt.cm.get_cmap(*cmap_settings)
    if not new_name:
        new_name = "sym_"+cmap_settings[0]  # ex: 'sym_Blues'
    
    # this defined the roughness of the colormap, 128 fine
    n= 32 
    
    # get the list of color from colormap
    colors_r = cmap(np.linspace(0, 1, n))    # take the standard colormap # 'right-part'
    colors_l = colors_r[::-1]                # take the first list of color and flip the order # "left-part"

    # combine them and build a new colormap
    colors = np.vstack((colors_l, colors_r))
    mymap = mcolors.LinearSegmentedColormap.from_list(new_name, colors)

    return mymap

path = '/m/cs/scratch/networks-pm/protocol/data/pilot_iii/fmri/tsnr' 
savepath = '/m/cs/scratch/networks-pm/protocol/results/pilot_iii'

files = os.listdir(path)
to_plot = {}
nback = list(filter(lambda x: 'nback' in x, files))
nback.sort()
to_plot["nback"] = nback
pvt = list(filter(lambda x: 'pvt' in x, files))
pvt.sort()
to_plot["pvt"] = pvt
movie = list(filter(lambda x: 'movie' in x, files))
movie.sort()
to_plot["movie"] = movie
resting = list(filter(lambda x: 'resting' in x, files))
resting.sort()
to_plot["resting"] = resting
titles = ["ses-01", "ses-02", "ses-03"]

cmap_settings = ('hot', None)
mymap = symmetrical_colormap(cmap_settings= cmap_settings, new_name =None )

########################### Violin plot ######################################
dfs=[]
for key in to_plot.keys():
    violin = {}
    for i,file in enumerate(pvt):
        print(os.path.join(path, file))
        nii = nib.load(os.path.join(path, file))
        data = nii.get_fdata()
        data[np.isnan(data)] = 0
        violin[titles[i]] = data[np.nonzero(data)]
    maxsize = max([a.size for a in violin.values()])
    violin_pad = {k:np.pad(v, pad_width=(0,maxsize-v.size,), mode='constant', constant_values=np.nan) for k,v in violin.items()}
    df = pd.DataFrame(violin_pad)
    df.reset_index(inplace=True)
    df = pd.melt(df, id_vars=['index'], value_vars=['ses-01', 'ses-02', 'ses-03'])
    df["task"] = key
    dfs.append(df)
violin_plot = pd.concat(dfs)

fig, ax = plt.subplots(dpi=200)
sns.set_theme(font="Arial")
sns.set_style("ticks")
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)
ax = sns.violinplot(data=violin_plot, x="task", y="value", hue="variable", order=["pvt", "resting", "movie", "nback"])
ax.set_ylim((0,450))
plt.legend(loc='upper center', ncol=3)
sns.despine()
plt.savefig(os.path.join(savepath,"violin_tsnr.pdf"))

############################### Plot tSNR ####################################
for key in to_plot.keys():
    data = to_plot[key]
    fig, axes = plt.subplots(ncols=1,nrows=3, figsize=(6,10))
    for i, ax in enumerate(axes.flat):
        ax.set_title(titles[i])
        plot_glass_brain(os.path.join(path, data[i]), cmap=mymap, vmin=0, vmax=400, axes=ax, colorbar=False, annotate=False, symmetric_cbar=False, threshold=5)
    fig.suptitle(f'tSNR per task: {key}')
    plt.show()
    plt.savefig(os.path.join(savepath,f'{key}_tsnr.pdf'))

############################## Plot colorbar #################################
fig, ax = plt.subplots(dpi=300)
fig.subplots_adjust(left=0.85)
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)
cmap = matplotlib.cm.hot
norm = matplotlib.colors.Normalize(vmin=0, vmax=400)

cb1 = matplotlib.colorbar.ColorbarBase(ax, cmap=cmap,
                                norm=norm,
                                orientation='vertical')
cb1.set_label('tSNR')
fig.show()
plt.savefig(os.path.join(savepath,'colorbar_tsnr.pdf'))