############################################################
# This file plots the results from ISC as computed by the  #
# ISCToolbox (Kauppi et al., 2014) for the pilot_iii data. #
#                                                          #
# author: ana.trianahoyos@aalto.fi 			   #
############################################################

import matplotlib.pyplot as plt
import matplotlib

from nilearn.plotting import plot_glass_brain

buda = "./data/pilot_iii/fmri/ISC/budapest.nii.gz"
pilot = "./data/pilot_iii/fmri/ISC/pilot.nii.gz"

fig = plt.figure(dpi=200)
font = {'family' : 'Arial','size': 12}
matplotlib.rc('font', **font)
ax = fig.add_subplot(211)
plot_glass_brain(pilot, colorbar=True, vmin=0.7, axes=ax, annotate=False)
ax.text(-0.1, 1.02, 'A', transform=ax.transAxes, size=10, weight='bold')
ax = fig.add_subplot(212)
plot_glass_brain(buda, colorbar=True, vmin=0.5, axes=ax, annotate=False)
ax.text(-0.1, 1.02, 'B', transform=ax.transAxes, size=10, weight='bold')

plt.show()
plt.savefig('./results/pilot_iii/SupplementaryFigure11.pdf')
                         
# Comparison between sessions

ses1 = "./data/pilot_iii/fmri/ISC/firstISC.nii.gz"
ses2 = "./data/pilot_iii/fmri/ISC/secondISC.nii.gz"
ses3 = "./data/pilot_iii/fmri/ISC/thirdISC.nii.gz"

fig = plt.figure(dpi=200)
font = {'family' : 'Arial','size': 12}
matplotlib.rc('font', **font)
ax = fig.add_subplot(311)
plot_glass_brain(ses1, colorbar=True, vmax=0.8, axes=ax, annotate=False)
ax.text(-0.1, 1.02, 'A', transform=ax.transAxes, size=10, weight='bold')
ax = fig.add_subplot(312)
plot_glass_brain(ses2, colorbar=True, vmax=0.8, axes=ax, annotate=False)
ax.text(-0.1, 1.02, 'B', transform=ax.transAxes, size=10, weight='bold')
ax = fig.add_subplot(313)
plot_glass_brain(ses3, colorbar=True, vmax=0.8, axes=ax, annotate=False)
ax.text(-0.1, 1.02, 'C', transform=ax.transAxes, size=10, weight='bold')
plt.show()
plt.savefig('./results/pilot_iii/SupplementaryFigure12.pdf')
