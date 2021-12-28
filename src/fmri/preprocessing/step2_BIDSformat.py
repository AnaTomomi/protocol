"""
This script creates the needed files in a folder to make it BIDS-complaint.

Requirements: 
            - Folder with NIFTI and JSON files in pseudo-BIDS format.  
            - known sequence of images taken in the scanner. There are 2 fields that are needed, 
              sequences: this refers to the type of sequences. For now, only 'T1', 'EPI', 'localizer' 
              are accepted.
              tasks: this refers to the names that will be used in the BIDS format. For example, 'localizer',
              'MPRAGE_T1w', 'resting', etc. These names can be anything, but make sure it includes all the
              names that have been used in the DICOM2NIFTI step. 

Outputs: - several JSON and tsv files. 

@author: ana.trianahoyos@aalto.fi
Created: 16.02.2021
"""

################################## User input needed ##########################
# Please modify this part 
savepath = '~/scratch/networks-pm/pilot'
dcm2niix_path = '~/code/external/dcm2niix/build/bin/dcm2niix'
subject = 'sub-01'

#This mapping is needed to change the names of the EPI files in case there are different tasks in a session
tasks = {'1': 'resting', '2':'pvt', '3':'movie', '4':'music', '5':'nback'}

###############################################################################

import os
import json
import pandas as pd
import warnings

#Create other needed files for BIDS
print("Converting to BIDS format...")
file = os.path.join(savepath,f'dataset_description.json')
if not os.path.isfile(file):
    content = {"BIDSVersion": "1.0.0",
               "License": "some licence",
               "Name": "some pilot data",
               "ReferencesAndLinks": ["some link"]}
    with open(file,'w') as f:
        json.dump(content,f, indent=4)

file = os.path.join(savepath,f'participants.json')
if not os.path.isfile(file):
    content = {"participant_id": {"Description": "Participant identifier"},
               "age": {"Description": "Participant age"}}
    with open(file,'w') as f:
        json.dump(content,f, indent=4)

file = os.path.join(savepath,f'participants.tsv')
if not os.path.isfile(file):
    content = {'participant_id': [subject], 'age': ['100']}
    data = pd.DataFrame.from_dict(content)
    data.to_csv(file, sep = '\t', index=False)
else:
    data = pd.read_csv(file, sep = '\t')
    if data['participant_id'].str.contains(subject).any():
        warnings.warn("Warning the subject already exists! No subjects are added.")
    elif set(data.columns)==set(['participant_id', 'age']):
        data = data.append({'participant_id': subject, 'age': '100'}, ignore_index=True)
        data.to_csv(file, sep = '\t', index=False)
    else:
        warnings.warn("Warning the tsv files has other fields. No modification will be made, please remember to add the info later.")

file = os.path.join(savepath,f'README')
if not os.path.isfile(file):
    with open(file, "w") as f:
        f.write("converted automatically, please check the fields")

file = os.path.join(savepath,f'.bidsignore')
if not os.path.isfile(file):
    with open(file, "w") as f:
        f.write(" ")

for i in tasks:
    if tasks[i]=='localizer' or tasks[i]=='MPRAGE_T1w':
        continue
    elif not os.path.isfile(os.path.join(savepath,f'task-{tasks[i]}_bold.json')):
        content = {"TaskName": f'{tasks[i]}'}
        with open(os.path.join(savepath,f'task-{tasks[i]}_bold.json'),'w') as f:
            json.dump(content,f)

print("BIDS format done! Please validate your folder.")
