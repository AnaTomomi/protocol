%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script breaks the BIOPAC full session into the number of runs/tasks%
% that it has. For example, if there have been two runs in one scanner    % 
% session.                                                                % 
%                                                                         %
%Author: ana.trianahoyos@aalto.fi                                         %
%created: 02.03.2021                                                      %
%modified:07.09.2021 include naming structure similar to bids             %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear all
close all
clc

drifterpath = './';
sub = 'sub-01';
ses = 'ses-01';
savepath = '../../../data/pilot_iii/biopac';
task = {'pvt', 'resting', 'movie', 'nback'}; %Tasks in the order they were taken in the scanner

%%%%%%%%% Do not modify from here on %%%%%%%%%%%%%%%%

drifterfile = sprintf('%s/%s/%s/biopac/%s_%s_acq-highfreq_biopac.mat',drifterpath,sub,ses,sub,ses);

if ~isfile(drifterfile)
    error('File does not exist. Please check the folder and file')
end

%refdata
refdata=load(drifterfile);
data = refdata.data; 

%plot the data to see what it looks like
temp=refdata.data(:,6);
dtemp=diff(temp);
unique(diff(find(dtemp==5)))
plot(temp)

%divide the intervals
interval_no = size(task,2);
for i=1:interval_no
    ids = find(temp==5);
    d = diff(find(temp==5));
    if i<interval_no
        inter_end = ids(find(d>1189,1,'first'));
    else
        inter_end = find(temp==5,1,'last');
    end
    inter_init = find(temp, 1, 'first');
    b = data(inter_init:inter_end,:);
    temp = temp(inter_end+1:end);
    
    savefile = sprintf('%s/%s/%s/%s_%s_task-%s_biopac.mat',savepath, sub, ses, sub, ses, task{i});
    save(savefile, 'b');
end
