%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script cuts the BIOPAC post-processed data according to the cuts   %
% defined for the NII files.                                              % 
%                                                                         %
%Author: ana.trianahoyos@aalto.fi                                         %
%created: 08.09.2021                                                      %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear all
close all
clc

path = '../../../data/pilot_iii/biopac';
sub = 'sub-01';
ses = 'ses-01';
tasks = {'pvt', 'resting', 'movie', 'nback'}; %Tasks in the order they were taken in the scanner
runs = {'1', '1', '1', '1'};

for i=1:length(tasks)
    task = tasks{i};
    run = runs{i};
    load(sprintf('%s/%s/%s/%s_%s_task-%s_run-%s_biopac-downsampled.mat', path, sub, ses, sub, ses, task, run))
    disp(task)
    if strcmp(task,'pvt')
        downsampled_cut = downsampled_tr(:,59:1070);
        disp(size(downsampled_cut))
    elseif strcmp(task,'resting')
        downsampled_cut = downsampled_tr(:,50:755);
        disp(size(downsampled_cut))
    elseif strcmp(task,'movie')
        downsampled_cut = downsampled_tr(:,33:1039);
        disp(size(downsampled_cut))
    elseif strcmp(task,'nback')
        downsampled_cut = downsampled_tr;
        disp(size(downsampled_cut))
    end
    
    save(sprintf('%s/%s/%s/%s_%s_task-%s_run-%s_biopac-downsampledcut.mat', path, sub, ses, sub, ses, task, run), 'downsampled_cut');
end
