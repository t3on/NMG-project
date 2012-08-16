from eelbrain.eellab import load
import eelbrain.eellab as E
import os
import numpy as np
import mne

def logread(filename):

#Initializes list
    triggers = []

#Reads the logfile and searches for the triggers
    for line in open(filename):
        if line.startswith('TRIGGER\tUSBBox'):
            items  = line.split()
            triggers.append(int(items[2]))

    return triggers


def load_meg_events(subdir, expdir = 'NMG'):

#Finds the file
    root = os.path.join('/', 'Users', 'teon', 'data', expdir, subdir, 'rawdata')
    triggerlist = os.path.join(root, 'meg', '_'.join((subdir, 'triggerlist.txt')))
    logfile = os.path.join(root, 'behavioral', 'logs', '_'.join((subdir, 'log.txt')))

#Loads the triggerlist from getSQDTriggers and from the log file   
    ds = E.load.txt.tsv(triggerlist)
    log = logread(logfile)

#Compares the log file to the triggerlist. Adds variable of boolean comparison
    log = np.array(log)
    compare  = ds['eventID'] == log
    ds['compare'] = compare
    ds['sqdread'] = ds['eventID']

#Replaces all events with the log. The log takes precedent since this is the value provided by PTB.    
    ds['eventID'][:] = log

#Asserts that the right value of triggers is given. Experimentally determined.
#For NMG: 4 trigger events per trial, 240 trials per list, 4 lists    
    assert ds.N == 3840

#Loads the eyelink data
    edf = E.load.eyelink.Edf(os.path.join(root, 'behavioral', 'eyelink', '*.edf'))
    edf.add_T_by_Id(ds)
    ds.info['edf'] = edf

#Propagates itemID for all trigger events
    index = ds['eventID'] < 64
    itemID = ds['eventID'][index]
    ds['itemID'] = E.factor(itemID, rep=4)
    

#Initialize lists    
    eventID_bin = []
    exp = []
    target = []
    cond = []
    cat = []

#Decomposes the trigger
    for v in ds['eventID']:
        if v > 128:        
            binary_trig = bin(int(v))[2:]
            eventID_bin.append(binary_trig)
            exp.append(int(binary_trig[0], 2))
            target.append(int(binary_trig[1], 2))
            cat.append(int(binary_trig[2:5], 2))
            cond.append(int(binary_trig[5:8], 2))
        else:
            binary_trig = bin(int(v))[2:]
            eventID_bin.append(binary_trig)
            exp.append(7)
            target.append(7)
            cat.append(7)
            cond.append(7)        

#Labels events    
    ds['experiment'] = E.factor(exp, labels={7: 'fixation', 1: 'experiment'})
    ds['target'] = E.factor(target, labels={7: 'fixation/voice', 0: 'prime', 1: 'target'})
    ds['category'] = E.factor(cat, labels={7: 'None', 1: 'transparent', 2: 'opaque', 3: 'novel', 4: 'ortho', 5:'ortho'})
    ds['condition'] = E.factor(cond, labels={7: 'None', 1: 'control_identity', 2: 'identity', 3: 'control_constituent', 4: 'first_constituent'})

#Labels the voice events
    index = np.arange(3,ds.N, 4)
    ds['experiment'][index] = 'voice'
    ds['target'][index] = 'None'
    ds['category'][index] = 'None'
    ds['condition'][index] = 'None'
    
#Adds the raw fif info used in epoching data.	
    ds.info['raw'] = mne.fiff.Raw(os.path.abspath(os.path.join(root, '..', 'myfif', '_'.join((subdir,expdir,'raw.fif')))))

    return ds