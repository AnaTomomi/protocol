clear all 
close all
clc
task={'pvt', 'nback',  'music', 'restingmovie1', 'restingmovie2'};

for i=1:5
load(sprintf('/m/cs/scratch/networks-pm/Longitudinal/results/pilot/biopac/%s_refdata.mat',task{i}));

b_c = refdata{1,1};
h_c = refdata{1,2};

sr=0.594;
fig=figure();
suptitle(task{i})
subplot(2,2,1)
[s,f] = pmtm(zscore(b_c.FF),4,1024,1/sr);
plot(f,s,'LineWidth',2)
set(gca, 'YScale', 'log')
set(gca, 'XScale', 'log')
xlabel('frequency')
ylabel('s')
set(gca,'XGrid','on')
title('breath after drifter')

subplot(2,2,2)
histogram(b_c.FF/60,20,'FaceColor',[0.8500 0.3250 0.0980],'FaceAlpha',0.5)
title('breath after drifter')

subplot(2,2,3)
[s,f] = pmtm(zscore(h_c.FF),4,1024,1/sr);
plot(f,s,'LineWidth',2)
set(gca, 'XScale', 'log')
set(gca, 'YScale', 'log')
xlabel('frequency')
ylabel('s')
set(gca,'XGrid','on')
title('heart after drifter')

subplot(2,2,4)
histogram(h_c.FF/60,20,'FaceColor',[0.8500 0.3250 0.0980],'FaceAlpha',0.5)
title('heart after drifter')

saveas(fig,sprintf('/m/cs/scratch/networks-pm/Longitudinal/results/pilot/post-prepro/BIOPAC_power_%s.pdf', task{i}))
end