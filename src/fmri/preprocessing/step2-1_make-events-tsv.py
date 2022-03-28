import os
import numpy as np
import pandas as pd

from nilearn.image import mean_img
from nilearn.plotting import plot_glass_brain, plot_stat_map
from nilearn.glm.first_level import FirstLevelModel

path = "/m/cs/scratch/networks-pm/protocol/data/pilot_iii/fmri/sub-01"
savepath = "/m/cs/scratch/networks-pm/pilot/sub-01"
os.chdir(path)

################### Generate the events.tsv file PVT #########################

files = []
for dirpath, dirnames, filenames in os.walk("."):
    for filename in [f for f in filenames if f.endswith("task-pvt_acq-highfreq_run-1_pres-response.txt")]:
        files.append(os.path.join(dirpath, filename))
files.sort()


cols = ["onset", "duration", "trial_type"]
for file in files:
    pvt = pd.read_csv(file, sep="\t", header=[0])
    ses = file.split('/')[1] 
    pvt.columns = cols
    pvt["onset"] = pvt["onset"]/1000 # Put everything in terms of sec
    pvt["duration"] = pvt["duration"]/1000
    pvt.duration[pvt["duration"] < 0] = 0.1 #Set lapses to very short periods, but not negative
    pvt.sort_values(by=['onset', 'duration'],axis=0, inplace=True)
    pvt = pvt[['trial_type', 'onset', 'duration']]
    pvt_path = os.path.join(savepath, ses, "func", f'sub-01_{ses}_task-pvt_acq-highfreq_run-1_events.tsv')
    pvt.to_csv(pvt_path, sep='\t', index=False)
    print(file)

################## Generate the events.tsv file n-back #######################

files = []
for dirpath, dirnames, filenames in os.walk("."):
    for filename in [f for f in filenames if f.endswith("task-nback_acq-highfreq_run-0_pres.log")]:
        files.append(os.path.join(dirpath, filename))
files.sort()

for file in files:
    nback = pd.read_csv(file, delimiter="\t", header=None, names=range(16))
    ses = file.split('/')[1] 
    nback.columns = nback.iloc[2]
    nback = nback.iloc[3:]
    
    # Make the block design first
    block_init_ids = nback.index[nback['Code'] == "dual_block"].tolist()
    block_end_ids = nback.index[nback['Code'] == "feedback"].tolist()
    
    if len(block_init_ids)!=len(block_end_ids):
        print("Something went wrong when detecting the blocks. Results may not be accurate. Please check")
    
    data = np.zeros((len(block_init_ids),2))
    for i in range(len(block_init_ids)):
        data[i,0] = float(nback["Time"][block_init_ids[i]])/10000
        data[i,1] = (float(nback["Time"][block_end_ids[i]]) - float(nback["Time"][block_init_ids[i]]))/10000
    block = pd.DataFrame(data=data, index=list(range(0,len(data))), columns=["onset", "duration"])
    block_type = ["one", "two", "one", "two", "one", "two", "one", "two"]
    block = block.assign(trial_type=block_type) 
    block = block[['trial_type', 'onset', 'duration']]
    block_path = os.path.join(savepath, ses, "func", f'sub-01_{ses}_task-nback_acq-highfreq_run-1_blocks.tsv')
    block.to_csv(block_path, sep='\t', index=False)

    
    #Make the events design
    event_init_ids = nback.index[nback['Code'].str.contains('ori')==True].tolist()
    event_end_ids = nback.index[nback['Code'] == "response"].tolist()
    
    if len(event_init_ids)!=len(event_end_ids):
        print("Something went wrong when detecting the events. Results may not be accurate. Please check")
    
    data = np.zeros((len(event_init_ids),2))
    for i in range(len(event_init_ids)):
        data[i,0] = float(nback["Time"][event_init_ids[i]])/10000
        data[i,1] = (float(nback["Time"][event_end_ids[i]]) - float(nback["Time"][event_init_ids[i]]))/10000
    event = pd.DataFrame(data=data, index=list(range(0,len(data))), columns=["onset", "duration"])
    event_type = [elem for elem in block_type for i in range(20)]
    event = event.assign(trial_type=event_type) 
    event = event[['trial_type', 'onset', 'duration']]
    event_path = os.path.join(savepath, ses, "func", f'sub-01_{ses}_task-nback_acq-highfreq_run-1_events.tsv')
    event.to_csv(event_path, sep='\t', index=False)
    
    print(file)
