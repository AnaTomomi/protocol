clear all
close all
clc

addpath('/m/nbe/scratch/braindata/shared/toolboxes/NIFTI');
addpath(genpath('/m/nbe/scratch/braindata/shared/toolboxes/bramila/bramila'));
path = '/m/cs/scratch/networks-pm/pilot_prepro/denoise/sub-01/ses-06';
savepath = '/m/cs/scratch/networks-pm/Longitudinal/results/pilot/tsnr';

files = dir(path);
files(~contains({files.name}, {'_HPF.nii'}))=[];
n = size(files,1);

for i=1:n
    nii = load_nii(sprintf('%s/%s', files(i).folder, files(i).name));

    volout = bramila_tsnr(nii.img);
    ids = find(isnan(volout));
    volout(ids) = 0;

    nii.hdr.dime.dim(5) = 1;
    nii.hdr.dime.pixdim(5) = 1;
    nii.img = volout;
    [~,file_out] = fileparts(files(i).name);
    save_nii(nii,sprintf('%s/%s_tsnr.nii',savepath,file_out))
    disp(files(i).name)
end
