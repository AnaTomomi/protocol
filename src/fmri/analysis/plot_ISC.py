############################################################
# This file plots the results from ISC as computed by the  #
# ISCToolbox (Kauppi et al., 2014) for the pilot_iii data. #
#                                                          #
# author: ana.trianahoyos@aalto.fi 			   #
############################################################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from nilearn.plotting import plot_glass_brain, plot_stat_map

buda = "/m/cs/scratch/networks-pm/Longitudinal/results/pilot/ISC/budapest/results/ISCcorrmapBand0Session1.nii"
pilot = "/m/cs/scratch/networks-pm/Longitudinal/results/pilot/ISC/timo-3sess/results/ISCcorrmapBand0Session1.nii"

fig = plt.figure(dpi=200)
font = {'family' : 'Arial','size': 12}
matplotlib.rc('font', **font)
ax = fig.add_subplot(211)
plot_glass_brain(pilot, colorbar=True, vmin=0.7, axes=ax, annotate=False)
ax = fig.add_subplot(212)
plot_glass_brain(buda, colorbar=True, vmin=0.5, axes=ax, annotate=False)

plt.show()
plt.savefig('/m/cs/scratch/networks-pm/protocol/results/pilot_iii/ISC.pdf')
                         
# Comparison between sessions

ses1 = "/m/cs/scratch/networks-pm/Longitudinal/results/pilot/ISC/timo-3sess/firstISC.nii"
ses2 = "/m/cs/scratch/networks-pm/Longitudinal/results/pilot/ISC/timo-3sess/secondISC.nii"
ses3 = "/m/cs/scratch/networks-pm/Longitudinal/results/pilot/ISC/timo-3sess/thirdISC.nii"

fig = plt.figure(dpi=200)
font = {'family' : 'Arial','size': 12}
matplotlib.rc('font', **font)
ax = fig.add_subplot(311)
plot_glass_brain(ses1, colorbar=True, vmax=0.8, axes=ax, annotate=False)
ax = fig.add_subplot(312)
plot_glass_brain(ses2, colorbar=True, vmax=0.8, axes=ax, annotate=False)
ax = fig.add_subplot(313)
plot_glass_brain(ses3, colorbar=True, vmax=0.8, axes=ax, annotate=False)
plt.show()
plt.savefig('/m/cs/scratch/networks-pm/protocol/results/pilot_iii/ISC_comparison.pdf')