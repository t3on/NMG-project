import process
import os

trigger_dir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'data', 'besa', 'evts')
subjects = ['R0095', 'R0224', 'R0498', 'R0499', 'R0504']
trialtype = ['prime']
condition = ['identity']

for subject in subjects:
    meg_ds = process.load_meg_events(subname = subject, expname='NMG', voiceproblem=True)
    for type in trialtype:
        file = os.path.join(trigger_dir, '%s_%s.evt' %(subject,type))
        index = meg_ds['target'] == type
        index2 = meg_ds['condition'] == condition
        meg = meg_ds[index*index2]
        
        triggers = meg['eventID'].x
        tms = range(200, (meg.N+1)*800, 800)
        codes = [1]*meg.N
        
        with open(file, 'w') as FILE:
            FILE.write('Tms\tCode\tTriNo\n')
            for time, code, trigger in zip(tms, codes, triggers):
                FILE.write('%s\t%s\t%s\n' %(time,code, trigger))
