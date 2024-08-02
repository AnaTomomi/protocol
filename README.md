
# protocol
This GIT contains all materials referenced in "Effects of daily environmental, physiological, and lifestyle factors in functional brain connectivity" pre-registration (see https://osf.io/5hu9c/). This work is later published as "Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological and lifestyle factors on functional brain connectivity".

There are three folders in this GIT:
* data: contains data if it has been pseudononymized. Some data may be missing in this folder because it is not yet pseudononymized or because it is too big for sharing on GIT. All pilot data are available for reviewers. Please write to ana.trianahoyos@aalto.fi or researchdata@aalto.fi to request access.
* results: this folder stores results (mainly Supplementary Figures). 
* src: source code for pilot analysis. 

# 1. Project description
This GIT contains the code and data collected for the Pilot phase of the paper "Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological and lifestyle factors on functional brain connectivity". 
In this paper, we conducted a 19-week experiment with a single participant who provided frequently sampled data from three sources: MRI, behavioral, and cognitive. Over the 19 weeks, smartphones and wearables collected objective behavioral data outside the scanner, while the participant completed daily cognitive tests and mental state questionnaires. For 15 weeks, the participant also underwent two MRI sessions per week, collecting structural, functional, and diffusion MRI data.

We conducted three separate pilot studies to evaluate various aspects of our research project, including study feasibility, data collection system effectiveness, and participant tolerance to the protocol. The first pilot focused solely on behavioral data, testing the psychomotor vigilance task (PVT) and data collection feasibility using smartphones and wearables. The second involved the n-back task, aimed at identifying potential learning effects. The third combined MRI and behavioral data to evaluate MRI sequences, the quality of fMRI data, and participant responses to the protocol. 

Results from these data and analysis are reported in the Supplementary Information file of the paper "Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological and lifestyle factors on functional brain connectivity" by Triana AM, Salmi J, Hayward N, Saramäki J, and Glerean E. The reported results are also available in the OSF pre-registration of the paper accesible at: https://osf.io/67tb4

# 2. subfolder explanations
There are three folders in this GIT:
- data: contains the data for each pilot
- docs: contains important documentation about the folders and code
- results: contains the results for each pilot
- src: source code for analysis

# 3. How to?
Most of the code in this GIT is dedicated to plot the Supplementary Figures 2-11. Here is the complete list of how to produce the Figures:

- Supplementary Figure 2: Run the script ```./src/behavioral/00_learning_PVT.py``` Data is located in the ./data/pilot_i/PVT/ folder. 
- Supplementary Figure 3: Run the script ```./src/behavioral/00_missing_data.py``` Data is located in the ./data/pilot_iii/behavioral folder. Remember to check the dates in the script, as pilot I was run from 2020-07-06 to 2020-07-20. 
- Supplementary Figure 4: Run the script ```./src/behavioral/00_learning_nback.py``` Data is located in the ./data/pilot_ii/ folder.
- Supplementary Figure 5: Run the script ```./src/fmri/preprocessing/plot_preprocess.py``` Data is located in the ./data/pilot_iii/fmri folder. MRI data is available on request (see Data availability section, write to researchdata@aalto.fi).
- Supplementary Figure 6: Run the script ```./src/fmri/quality/plot_tsnr.py``` Data is located in the ./data/pilot_iii/fmri/tsnr/ folder.
- Supplementary Figure 7: Run the script ```./src/fmri/quality/plot_fd.py``` Data is located in the ./data/pilot_iii/fmri/ folder.
- Supplementary Figure 8: Run the script ```./src/behavioral/00_missing_data.py``` Data is located in the . /data/pilot_iii
/behavioral/ folder. Remember to check the dates in the script, as pilot I was run from 2021-08-02 to 2021-09-07.
- Supplementary Figure 9: Run the script ```./src/behavioral/01_feature-selection.py``` Data is located in the ./data/pilot_iii/behavioral/ folder.
- Supplementary Figure 10: Run the script ```./src/behavioral/01_imputation.py``` Data is located in the ./data/pilot_iii/behavioral/ folder. 
- Supplementary Figure 11: Run the script ```./src/fmri/analysis/plot_ISC.py``` Data is located in the ./data/pilot_iii/fmri/ISC/.
- Supplementary Figure 12: Run the script ```./src/fmri/analysis/plot_ISC.py``` Data is located in the ./data/pilot_iii/fmri/ISC/.

# 4. Questions?
If there is something unclear, please write to ana.trianahoyos@aalto.fi
