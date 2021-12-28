#!/bin/bash

module load fsl
source $FSLDIR/etc/fslconf/fsl.sh
source ~/software/pydeface/bin/activate

cd "/m/cs/scratch/networks-pm/pilot/sub-01/"

find $1 -type f -name '*MPRAGE_T1w.nii' -print -exec echo pydeface {} --outfile {} --force \;

