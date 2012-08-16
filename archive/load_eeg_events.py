import numpy as np
import os
import eelbrain.eellab as E
import mne


def load_eeg_events(subdir, expdir = 'NMG'):

#Finds the file
    root = os.path.join('/', 'Users', 'teon', 'data', expdir, subdir, 'rawdata')
    filename = os.path.join(root, 'eeg', ''.join(('_'.join((subdir, expdir)), '.vmrk')))

#Initialize lists   
    marker = []
    eventID = []
    i_start = []
    size = []
    channel = []

#Extracts info for dataset
    for line in open(filename):
        if line.startswith('Mk'):
            #if line.startswith('Mk1='):
            #    continue
            items = line.split(',')
            marker.append(items[0])
            if items[1] == '':
                eventID.append(items[1])
            else:
                eventID.append(items[1][1:])
            i_start.append(int(items[2]))
            size.append(int(items[3]))
            channel.append(int(items[4]))

    marker = E.factor(marker, 'marker')            
    eventID = E.factor(eventID, 'eventID')
    i_start = E.var(i_start, 'i_start')
    size = E.var(size, 'size')
    channel = E.var(channel, 'channel')

#Creates dataset    
    eeg = E.dataset(marker, eventID, i_start, size, channel)

#Adds header information to the dataset
    tmp = open(filename).read()
    header = tmp.split('Mk1')[0]
    eeg.info['header'] = header

    eeg.info['raw'] = mne.fiff.Raw(os.path.abspath(os.path.join(root, '..', 'myfif', '_'.join((subdir,expdir,'EEG', 'raw.fif')))))

    return eeg


    