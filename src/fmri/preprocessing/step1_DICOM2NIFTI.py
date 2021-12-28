"""
This script converts DICOM files to NIFTI and organizes the files in pseudo-BIDS format.

Requirements: 
            - DICOM files organized in a pseudo-BIDS format. E.g. subject as a parent folder, 
              sesssions as subfolders, and inside the sessions, the folders from AMI centre. 
            - dcm2niix installed in a folder that can be accessed by the user. 
            - known sequence of images taken in the scanner. There are 2 fields that are needed, 
              sequences: this refers to the type of sequences. For now, only 'T1', 'EPI', 'localizer' 
              are accepted.
              tasks: this refers to the names that will be used in the BIDS format. For example, 'localizer',
              'MPRAGE_T1w', 'resting', etc. These names can be anything, but they have to match the order of
              sequences.

Outputs: - NIFTI and JSON files in the specified folder. 

If you need help on the order of BIDS labels, please see https://docs.flywheel.io/hc/en-us/articles/360017426934-How-do-I-name-scan-acquisitions-so-they-can-be-in-BIDS-format-in-Flywheel-

@author: ana.trianahoyos@aalto.fi
Created: 16.02.2021
Modified: 09.07.2021 Include more labels in the names
"""

################################## User input needed ##########################
# Please modify this part 
datapath = '~/project/networks-pm/human'
savepath = '~/scratch/networks-pm/pilot'
dcm2niix_path = '~/code/external/dcm2niix/build/bin/dcm2niix'
subject = 'sub-01'
session = 'ses-01'

#This mapping is needed to change the names of the EPI files in case there are different tasks in a session
sequences = {'1': 'localizer', '2':'EPI', '3':'EPI', '4':'EPI', '5':'EPI'} #type of image taken at the scanner in the order they were taken
tasks = {'1': 'localizer', '2':'pvt', '3':'resting', '4':'movie', '5':'nback'} #task name that will be written in the name
acq = {'1': 'localizer', '2':'highfreq', '3':'highfreq', '4':'highfreq', '5':'highfreq'} #acquisition label, referring to the sequence name
run = {'1': 'none', '2':'1', '3':'1', '4':'1', '5':'1'} #run number in case there are some

###############################################################################

# No major modifications required! Modify if you are sure or need another sequence.
import os

#Prepare the paths and batch convert all that was scanned in the session
folder = os.path.join(datapath, subject, session)

subfolders = next(os.walk(folder))[1]
subfolders.sort()
if len(subfolders)==0:
    raise NameError('The folder does not have any DICOM images')
    
if len(subfolders)!=len(sequences):
    raise NameError('Number of sequences does not match the number of subfolders. Please check the sequences.')
if len(subfolders)!=len(tasks):
    raise NameError('Number of sequences does not match the number of tasks. Please check the tasks.')
if len(tasks)!=len(sequences):
    raise NameError('Number of sequences does not match the number of tasks. Please check the sequences and the tasks.')

print("Starting DICOM to NIFTI conversion...")
for subfolder, i in zip(subfolders,tasks):
    in_folder = os.path.join(folder,subfolder)
    print(in_folder)
    if sequences[i]=='localizer':
        print("Localizers are not converted")
        continue
    elif sequences[i]=='T1':
       out_folder = os.path.join(savepath,subject,session,"anat")
       filename = f'{subject}_{session}_acq-{acq[i]}_T1w'
    elif sequences[i]=='T2':
       out_folder = os.path.join(savepath,subject,session,"anat")
       filename = f'{subject}_{session}_acq-{acq[i]}_T2w'
    elif sequences[i]=='EPI':
       out_folder = os.path.join(savepath,subject,session,"func")
       filename = f'{subject}_{session}_task-{tasks[i]}_acq-{acq[i]}_run-{run[i]}_bold'
    elif sequences[i]=='DIFF':
        print("Diffusion not yet supported")
        continue
    else:
       raise NameError('Sequence type not found, please add it to the script (line 66)')
    
    if not os.path.isdir(out_folder):
        os.makedirs(out_folder)
    if not os.path.isfile(os.path.join(out_folder,filename+".nii")):
        command =  f'{dcm2niix_path} -z n -b y -f {filename} -o {out_folder} {in_folder}'
        os.system(command)
    else:
        print("the file already exists. Please check the folders. No conversion is done.")

print("Conversion finnished!")
