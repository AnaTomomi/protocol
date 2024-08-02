# What?
This folder contains the data for the pilot referenced in "Longitudinal single-subject neuroimaging study reveals effects of daily environmental, physiological and lifestyle factors on functional brain connectivity", according to the preregistration https://osf.io/5hu9c/.

Some data may be missing in this folder because it is not yet pseudononymized or because it is too big for sharing on GIT. All pilot data are available for reviewers. Please write to ana.trianahoyos@aalto.fi or researchdata@aalto.fi to request access.

There are three subfolders, one for each pilot:

## 1. pilot_i: contains two subfolders **"behavioral"** and **"PVT"**. 

The behavioral folder contains the data collected with smartphones and wearables. There are six files, one for each sensor:
- battery: smartphone battery
- esm: questionnaires 
- light: light captured by the smartphone
- location: GPS-anonymized data, i.e., the exact coordinates have been replaced and only the timestamps at which each datapoint was collected remain untouched
- oura: sleep and activity data collected with the oura smartring
- wifi: wifi-anonymized data, i.e., the exact wifi networks have been deleted and only the timestamps at which each datapoint was collected and the rssi remain untouched

The PVT folder contains the presentation logs for each PVT task. There is one log per day (=15).
 
## 2. pilot_ii: contains the presentation logs for each n-back task. Each task creates a rawdata and a summary file. Both files are needed to understand the subject's learning curve. There are 56 files, i.e., four files per day, two files per task. 

### 3. pilot_iii: contains two subfolders **"behavioral"** and **"fmri"**. 

The behavioral folder contains the data collected with smartphones and wearables. There are six files, one for each sensor. See (1.) for a description of each file.

The fMRI folder has two subfolders and several files:
- the subfolder "ISC" contains the results from the ISC analysis in preprocessed fMRI data. We employed the ISC Toolbox to generate these files (https://www.nitrc.org/projects/isc-toolbox/). 
- the subfolder "tsnr" conatins the results from computing the TSNR in each session for the images taken at the AMI centre 3T Siemens MRI scanner. We employed custom code to compute the TSNR. Naming of these files is based on the BIDS format, so it should be self-explanatory. 
- All .tsv files are the confounds yielded by fmriprep for each task at each particular session. The naming follows the BIDS convention. These files are used mainly to inspect the framewise displacement. 
- r_brain.nii.gz and r_gs_brain.nii.gz and the R2 correlation maps between the preprocessed (and denoised) signal and the original fMRI data. These maps are used to understand where the confound regression is affecting the BOLD signal in the brain. 
- *.pickle files are the vectors and specific voxel signals after detrending or preprocessing the fMRI signal. These are used to generate the Supplementary Figure 5. The analysis of preprocessing was carried for all tasks and sessions. Due to the large fMRI files and anonymization protocols, we only release the necessary data to reproduce the SF5 for transparency in this GIT. 
