#load_events.py
##Written by Teon Brooks
##Created 6/10/2012

#This module is used to load eeg and meg events in the event that they are missing from the fif-file.


import numpy as np
import eelbrain.eellab as E
import os
import mne
from eelbrain import ui, vessels as V
import scipy.io
import eelbrain.utils.subp as subp

__hide__ = ['os', 'V', 'scipy.io', 'subp', 'E', 'mne', 'ui']


def format_latency(subjects = [], expname = 'NMG'):
	root = os.path.join(os.path.expanduser('~'), 'data', expname)
	group_latency_out = os.path.join(root, 'group', '_'.join((expname, 'group', 'latencies.txt')))
	group_latencies = []

	for subject in subjects:
		latency_out = os.path.join(root, subject, 'data', '_'.join((subject, expname, 'latencies.txt')))
		data = os.path.join(root, subject, 'rawdata', 'behavioral', subject+'_data.txt')
		header = []
		latencies = []

		for line in open(data):
			if line.startswith('KEY\tsound'):
				latencies.append(line.strip())
				group_latencies.append('\t'.join((subject, line.strip())))
			if line.startswith('Response'):
				header.append(line.strip())

		with open(latency_out, 'w') as FILE:
			FILE.write(header[0]+os.linesep)
			FILE.write(os.linesep.join(latencies))
		with open(group_latency_out, 'w') as FILE:
			FILE.write(header[0]+os.linesep)
			FILE.write(os.linesep.join((group_latencies)))


    
def load_eeg_events(subname, expname = 'NMG'):

#Finds the file
    root = os.path.join(os.path.expanduser('~'), 'data', expname, subname)
    rawdata = os.path.join(root, 'rawdata')
    filename = os.path.join(rawdata, 'eeg', ''.join(('_'.join((subname, expname)), '.vmrk')))
    fifdir = os.path.join(root, 'myfif')
    datadir = os.path.join(root, 'data')
    
#Initialize lists   
    marker = []
    eventID = []
    i_start = []
    size = []
    channel = []

#Extracts info for dataset
    for line in open(filename):
        if line.startswith('Mk'):
            if line.startswith('Mk1='):
                continue
            items = line.split(',')
            items[0] = '='.join((items[0].split('=')[0], 'Stimulus'))
            marker.append(items[0])
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
    header = tmp.split('Mk2')[0]
    eeg.info['header'] = header

    eeg.info['raw'] = mne.fiff.Raw(os.path.abspath(os.path.join(fifdir, '_'.join((subname,expname,'EEG', 'raw.fif')))))
    eeg.info['fifdir'] = fifdir
    eeg.info['datadir'] = datadir
    
    eeg.info['subname'] = subname
    eeg.info['expname'] = expname
    
    eeg.info['sns_locs'], eeg.info['sns_names'] = sns_read()
    eeg.info['sensors'] = V.sensors.sensor_net(locs = eeg.info['sns_locs'], names = eeg.info['sns_names'])
    
    return eeg
    

    
def sns_read():
    locs = []
    names = []
    loc_file = []

    for line in open('/Users/teon/Dropbox/Experiments/tools/scripts/eeg_sns.txt'):
        if line.startswith('ID'):
            continue
        id, label, x, y, z = line.split()
        locs.append((x,y,z))
        names.append(label)

    return locs, names
    
    

def export_v(eeg_ds):

#Finds the file
    root = os.path.join(os.path.expanduser('~'), 'data', eeg_ds.info['expname'], eeg_ds.info['subname'])
    rawdata = os.path.join(root, 'rawdata')    
    vhdr_input = os.path.join(rawdata, 'eeg', '_'.join((eeg_ds.info['subname'], eeg_ds.info['expname'])) + '.vhdr')
    vhdr_filename = os.path.join(rawdata, 'eeg', '_'.join((eeg_ds.info['subname'], eeg_ds.info['expname'], 'new')) + '.vhdr')   
    vmrk_filename = os.path.join(rawdata, 'eeg', '_'.join((eeg_ds.info['subname'], eeg_ds.info['expname'], 'new')) + '.vmrk')
    vmrk_handle = '_'.join((eeg_ds.info['subname'], eeg_ds.info['expname'], 'new')) + '.vmrk'
        
    vmrk = open(vmrk_filename, 'w')
    vmrk.write(eeg_ds.info['header'])
    for i in range(eeg_ds.N):
        vmrk.write('%s,S%s,%s,%s,%s\n\r' %(eeg_ds['marker'][i], eeg_ds['eventID'][i], eeg_ds['i_start'][i], eeg_ds['size'][i], eeg_ds['channel'][i]))
    vmrk.close()
    
    
    vhdr = open(vhdr_filename, 'w')
    
    for line in open(vhdr_input):
        if line.startswith('MarkerFile'):
            vhdr.write('MarkerFile=%s\n\r' %vmrk_handle)
        else:
            vhdr.write(line)

    print 'All Done!'
    
    
        
def eeg_align(subname, expname = 'NMG', voiceproblem = False):

    #Loads events
    eeg_ds = load_eeg_events(subname, expname)
    meg_ds = load_meg_events(subname, expname, voiceproblem)
    
    #Removes the fixations to match the eeg
    index = meg_ds['experiment'] != 'fixation'
    meg_ds = meg_ds[index]
    
    #Converts to milliseconds/original sampling rate then rezeros
    meg = (meg_ds['i_start'] - meg_ds['i_start'][0])*2
    
    #Rezeros events.
    eeg = eeg_ds['i_start'] - eeg_ds['i_start'][0]
    
    #Initializes Iter count, flags and loop.
    i = 0
    j = 0
    
    flags = []
    diff = []
    notflags = []
    in_the_file = 1
    
    #Compares the two data streams. Flags the extraneous events
    while in_the_file:
        check = (eeg[j] < meg[i] + 100) & (eeg[j] > meg[i] - 100)
        if check:
            diff.append(abs(meg[i]-eeg[j]))
            notflags.append(j)            
            i = i + 1
            j = j + 1
        else:
            flags.append(j)
            j = j + 1
        
        if j >= len(eeg):
            in_the_file = 0
    
    #Removes the extra trigger events
    index = np.ones(eeg_ds.N, dtype = 'Bool')
    index[flags] = False
    eeg_ds = eeg_ds[index]
    
    #Replaces the EEG triggers with ones from the MEG
    eeg_ds['eventID'] = meg_ds['eventID'].as_factor(name='eventID', labels='%i')
    
    #Adds additional info
    eeg_ds['itemID'] = meg_ds['itemID']
    eeg_ds['experiment'] = meg_ds['experiment']
    eeg_ds['target'] = meg_ds['target']
    eeg_ds['wordtype'] = meg_ds['wordtype']
    eeg_ds['condition'] = meg_ds['condition']
    eeg_ds['eventID_bin'] = meg_ds['eventID_bin']
    
    
    return eeg_ds



def kit2fiff(subname, expname = 'NMG', sfreq = 500):

	paramdir = os.path.join(os.path.expanduser('~'), 'data', expname, subname, 'parameters')
		
	subp.kit2fiff(paths=dict(mrk = os.path.join(paramdir, '_'.join((subname, expname, 'marker-coregis.txt'))),
						elp = os.path.join(paramdir, '_'.join((subname, expname + '.elp'))),
						hsp = os.path.join(paramdir, '_'.join((subname, expname + '.hsp'))),
						rawtxt = os.path.abspath(os.path.join(paramdir, '..', 'rawdata', 'meg', '_'.join((subname, expname + '-export500.txt')))),
                 		rawfif = os.path.abspath(os.path.join(paramdir, '..', 'myfif', '_'.join((subname, expname, 'raw.fif')))),
                 		sns = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'tools', 'scripts', 'sns.txt')),
                 		sfreq=sfreq)



def load_meg_events(subname, expname = 'NMG', voiceproblem = True):

#Defines directories
    root = os.path.join(os.path.expanduser('~'), 'data', expname, subname)
    rawdata = os.path.join(root, 'rawdata')
    fifdir = os.path.join(root, 'myfif')
    mridir = os.path.abspath(os.path.join(root, '..', '..', 'MRI', subname))
    datadir = os.path.join(root, 'data')
    
#Finds the file    
    triggerlist = os.path.join(rawdata, 'meg', '_'.join((subname, 'triggerlist.txt')))
    logfile = os.path.join(rawdata, 'behavioral', 'logs', '_'.join((subname, 'log.txt')))
    dur_file = os.path.join(rawdata, 'behavioral', '_'.join((subname, 'durations.txt')))

#Loads the triggerlist as ds from getSQDTriggers and from the log file   
    ds = E.load.txt.tsv(triggerlist)
    log = _logread(logfile)

#Compares the log file to the triggerlist. Adds variable of boolean comparison
    log = np.array(log)
    assert ds['eventID'] == log
#Asserts that the right value of triggers is given. Experimentally determined.
#For NMG: 4 trigger events per trial, 240 trials per list, 4 lists    
    assert ds.N == 3840



#Adds the raw fif info used in epoching data.    
    ds.info['fifdir'] = fifdir
    ds.info['raw'] = mne.fiff.Raw(os.path.abspath(os.path.join(fifdir, '_'.join((subname, expname,'raw.fif')))))
    ds.info['rawfif'] = os.path.abspath(os.path.join(fifdir, '_'.join((subname, expname, 'raw.fif'))))
    ds.info['proj'] = os.path.abspath(os.path.join(fifdir, '_'.join((subname, expname, 'proj.fif'))))
    ds.info['subname'] = subname
    ds.info['expname'] = expname
    ds.info['datadir'] = datadir

#Adds mri filenames
    ds.info['fwd'] = os.path.join(fifdir, '_'.join((subname, expname, 'raw-fwd.fif')))
    ds.info['cov'] = os.path.join(fifdir, '_'.join((subname, expname, 'raw-cov.fif')))
    ds.info['inv'] = os.path.join(fifdir, '_'.join((subname, expname, 'raw-inv.fif')))
    ds.info['trans'] = os.path.join(fifdir, '_'.join((subname, expname, 'raw-trans.fif')))
    
    ds.info['bem'] = os.path.join(mridir, 'bem', subname+'-5120-bem-sol.fif')
    ds.info['src'] = os.path.join(mridir, 'bem', subname+'-ico-4-src.fif')
    ds.info['mridir'] = mridir    
    ds.info['labeldir'] = os.path.join(mridir, 'label')
    ds.info['expdir'] = os.path.join(os.path.expanduser('~'), 'data', expname)
    
    
    
#Loads the eyelink data
    edf_path = os.path.join(rawdata, 'behavioral', 'eyelink', '*.edf')
    if os.path.exists(os.path.dirname(edf_path)):
        edf = E.load.eyelink.Edf(edf_path)
        edf.add_T_to(ds)
        ds.info['edf'] = edf
    else:
        print "%s%s This path does not exist. Please check your folder." %(edf_path, os.linesep)
#     elif not ui.ask(title='Missing Files', message='Subject %s Eyelink files are missing. Okay to proceed?' %subname, cancel=False, default=True):
#         raise RuntimeError('missing file')



#Propagates itemID for all trigger events
    index = ds['eventID'] < 64
    itemID = map(int, ds['eventID'][index])
    ds['itemID'] = E.var(np.repeat(itemID, 4))

#For the first five subjects in NMG, the voice trigger was mistakenly overlapped with the prime triggers.
#Repairs voice trigger value problem, if needed.
    if voiceproblem == True:
        index = range(3,ds.N, 4)
        ds['eventID'][index] = ds['eventID'][index]-128

#Initialize lists    
    eventID_bin = []
    exp = []
    target = []
    cond = []
    type = []

#Decomposes the trigger
    for v in ds['eventID']:
        eventID_bin.append(binary_trig)

        if v > 128:        
            binary_trig = bin(int(v))[2:]
            exp.append(int(binary_trig[0], 2))
            target.append(int(binary_trig[1], 2))
            type.append(int(binary_trig[2:5], 2))
            cond.append(int(binary_trig[5:8], 2))
        else:
            binary_trig = bin(int(v))[2:]
            exp.append(None)
            target.append(None)
            type.append(None)
            cond.append(None)        

#Labels events    
    ds['experiment'] = E.factor(exp, labels={None: 'fixation', 1: 'experiment'})
    ds['target'] = E.factor(target, labels={None: 'fixation/voice', 0: 'prime', 1: 'target'})
    ds['wordtype'] = E.factor(type, labels={None: 'None', 1: 'transparent', 2: 'opaque', 3: 'novel', 4: 'ortho', 5:'ortho'})
    ds['condition'] = E.factor(cond, labels={None: 'None', 1: 'control_identity', 2: 'identity', 3: 'control_constituent', 4: 'first_constituent'})
    ds['eventID_bin'] = E.factor(eventID_bin, 'eventID_bin')
#Labels the voice events
#Since python's indexing start at 0 the voice trigger is the fourth event in the trial, the following index is created.
    index = np.arange(3,ds.N, 4)
    ds['experiment'][index] = 'voice'
#     ds['target'][index] = 'None'
#     ds['wordtype'][index] = 'None'
#     ds['condition'][index] = 'None'


#Load the stim info from mat file
	stim_ds = _load_stims_info()

    temp = ds[ds['target'] == 'target']
    idx = []
    for (itemID,wordtype) in zip(temp['itemID'],temp['wordtype']):
        a = itemID == stim_ds['itemID']
        b = wordtype == stim_ds['wordtype']
        idx.append(np.where(a*b)[0][0])

    stim_ds = stim_ds[idx].repeat(4) 
    ds.update(stim_ds)

    return ds



def _logread(filename):

#Initializes list
    triggers = []

#Reads the logfile and searches for the triggers
    for line in open(filename):
        if line.startswith('TRIGGER\tUSBBox'):
            items  = line.split()
            triggers.append(int(items[2]))

    return triggers



def _load_stims_info(stims_info = '/Users/teon/data/NMG/stims/stims_info.mat'):
	#Adds stim information

    stims = scipy.io.loadmat(stims_info)['stims']
    stim_ds = E.dataset()
    stim_ds['c1_rating'] = E.var(np.hstack(np.hstack(np.hstack(stims['c1_rating']))))
    stim_ds['c1_sd'] = E.var(np.hstack(np.hstack(np.hstack(stims['c1_sd']))))
    stim_ds['c1'] = E.factor(np.hstack(np.hstack(stims['c1'])))
    stim_ds['c1_freq'] = E.var(np.hstack(np.hstack(np.hstack(stims['c1_freq']))))
    stim_ds['c1_nmg'] = E.var(np.hstack(np.hstack(np.hstack(stims['c1_nmg']))))
    stim_ds['word'] = E.factor(np.hstack(np.hstack(stims['word'])))
    stim_ds['word_freq'] = E.var(np.hstack(np.hstack(np.hstack(stims['word_freq']))))
    stim_ds['word_nmg'] = E.var(np.hstack(np.hstack(np.hstack(stims['word_nmg']))))
    stim_ds['wordtype'] = E.factor(np.hstack(np.hstack(np.hstack(stims['wordtype']))), labels = {0: 'opaque', 1: 'transparent', 2: 'novel', 3: 'ortho'})
    stim_ds['itemID'] = E.var(np.hstack(np.hstack(np.hstack(stims['itemID']))))
    
    stim_ds['c2_rating'] = E.var(np.hstack(np.hstack(np.hstack(stims['c2_rating']))))
    stim_ds['c2_sd'] = E.var(np.hstack(np.hstack(np.hstack(stims['c2_sd']))))
    stim_ds['c2'] = E.factor(np.hstack(np.hstack(stims['c2'])))
    stim_ds['c2_freq'] = E.var(np.hstack(np.hstack(np.hstack(stims['c2_freq']))))
    stim_ds['c2_nmg'] = E.var(np.hstack(np.hstack(np.hstack(stims['c2_nmg']))))
    
    return stim_ds



def reject_blinks(meg_ds):

	if 't_edf' in meg_ds:
		meg_ds.info['edf'].mark(meg_ds, tstart=-0.2, tstop=0.4, good=None, bad=False, use=['EBLINK'], T='t_edf', target='accept')
		meg = meg_ds.subset('accept')
		del meg['t_edf'], meg['accept']
	else:
		print 'No Eyelink data'
		meg = meg_ds
	
	return meg
