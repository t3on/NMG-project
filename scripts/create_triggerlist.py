import process
import os
import eelbrain.eellab as E

trigger_dir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'data', 'besa', 'triggerlists')
subjects = ['R0095', 'R0224', 'R0498', 'R0499', 'R0504']
trialtype = ['prime']
condition = 'identity'

for subject in subjects:
    meg_ds = process.load_meg_events(subname = subject, expname='NMG', voiceproblem=True)
    for type in trialtype:
        index = meg_ds['target'] == type
        index2 = meg_ds['condition'] == condition
        meg = meg_ds[index*index2]
        
        triggertime = E.var(meg['i_start'].x/meg.info['raw'].info['sfreq'], name = 'triggertime')
        export_ds = E.dataset(triggertime)
        export_ds.export(os.path.join(trigger_dir, '%s_%s_%s.txt' % (subject, condition, type)), header=False)
