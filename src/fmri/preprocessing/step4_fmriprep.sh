#!/bin/bash
#SBATCH --time=2-00:00:00
#SBATCH --mem=64G
#SBATCH --array=1
#SBATCH --output=/m/cs/scratch/networks-pm/fmriprep_dummy.out
#SBATCH --cpus-per-task=4

module load singularity-fmriprep/latest
singularity_wrapper exec fmriprep ~/scratch/networks-pm/pilot/  ~/scratch/networks-pm/pilot_prepro/ -w  ~/temp/ participant --participant-label sub-01 --fs-no-reconall --output-spaces MNI152NLin6Asym:res-2 --fs-license-file /scratch/shareddata/set1/freesurfer/license.txt
