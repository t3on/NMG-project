#load_events.py
##Written by Teon Brooks
##Created 6/10/2012

#This module is used to load eeg and meg events in the event that they are missing from the fif-file.


import numpy as np
import os
import mne
from eelbrain import vessels as V, ui as ui, eellab as E
import subprocess
import tempfile
import fnmatch
import re
import scipy.io


__hide__ = ['np', 'E', 'os', 'mne', 'V', 'scipy.io', 'subprocess', 'tempfile', 'fnmatch', 're']


def format_latency(subjects=[], expname='NMG'):
    datadir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', expname, 'data')
    root = os.path.join(os.path.expanduser('~'), 'data', expname)
    group_latency_out = os.path.join(datadir, '_'.join((expname, 'group', 'latencies.txt')))
    group_latencies = []

    for subject in subjects:
        latency_out = os.path.join(root, subject, 'data', '_'.join((subject, expname, 'latencies.txt')))
        data = os.path.join(root, subject, 'rawdata', 'behavioral', subject + '_data.txt')
        header = []
        latencies = []

        for line in open(data):
            if line.startswith('KEY\tsound'):
                latencies.append(line.strip())
                group_latencies.append('\t'.join((subject, line.strip())))
            if line.startswith('Response'):
                header.append(line.strip())

        with open(latency_out, 'w') as FILE:
            FILE.write('subject\t' + header[0] + os.linesep)
            FILE.write(os.linesep.join(latencies))
    with open(group_latency_out, 'w') as FILE:
        FILE.write('subject\t' + header[0] + os.linesep)
        FILE.write(os.linesep.join((group_latencies)))



def brain_vision2fiff(subname, expname='NMG'):

    root = os.path.join(os.path.expanduser('~'), 'data', expname, subname)
    fifdir = os.path.join(root, 'myfif')
    datadir = os.path.join(root, 'rawdata', 'eeg')
    vhdr = os.path.join(datadir, '_'.join((subname, expname + '.vhdr')))
    out = os.path.join(fifdir, '_'.join((subname, expname, 'EEG')))

    cmd = ['/Applications/mne/bin/mne_brain_vision2fiff',
           '--header', '%s' % vhdr,
           '--orignames',
           '--out', '%s' % out]
    cwd = datadir
    sp = subprocess.Popen(cmd, cwd=cwd,
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = sp.communicate()

    if stderr:
        print '\n> ERROR: %s\n%s' % (stderr, stdout)


def load_eeg_events(subname, expname='NMG'):

#Finds the file
    root = os.path.join(os.path.expanduser('~'), 'data', expname, subname)
    rawdata = os.path.join(root, 'rawdata', 'eeg')
    vmrk = os.path.join(rawdata, ''.join(('_'.join((subname, expname)), '.vmrk')))
    fifdir = os.path.join(root, 'myfif')
    datadir = os.path.join(root, 'data')

#Initialize lists
    marker = []
    eventID = []
    i_start = []
    size = []
    channel = []


#Extracts info for dataset
    for line in open(vmrk):
        if line.startswith('Mk'):
#The first marker has information about the experiment
            if line.startswith('Mk1='):
                continue
            items = line.split(',')
            eventID.append(items[1][1:])
            i_start.append(int(items[2]))
            size.append(int(items[3]))
            channel.append(int(items[4]))

    eventID = E.factor(eventID, 'eventID')
    i_start = E.var(i_start, 'i_start')
    size = E.var(size, 'size')
    channel = E.var(channel, 'channel')


#Creates dataset    
    eeg_ds = E.dataset(eventID, i_start, size, channel)
    eeg_ds['subject'] = E.factor([subname], rep=eeg_ds.N)
#Add info to dataset
    eeg_ds.info['raw'] = mne.fiff.Raw(os.path.abspath(os.path.join(fifdir, '_'.join((subname, expname, 'EEG', 'raw.fif')))))
    eeg_ds.info['fifdir'] = fifdir
    eeg_ds.info['datadir'] = datadir

    eeg_ds.info['subname'] = subname
    eeg_ds.info['expname'] = expname

    eeg_ds.info['sns_locs'], eeg_ds.info['sns_names'] = _sns_read()
    eeg_ds.info['sensors'] = V.sensors.sensor_net(locs=eeg_ds.info['sns_locs'], names=eeg_ds.info['sns_names'])

#Details listed in data/NMG/stims/sns_clusters.py
    eeg_ds.info['sns_clusters'] = dict(outer=['Fp1', 'Fp2', 'F7', 'F8', 'P7', 'P8', 'O1', 'O2'],
    									midlateral=['F3', 'F4', 'FC5', 'FC6', 'CP5', 'CP6', 'P3', 'P4'],
    									inner=['FC1', 'FC2', 'C3', 'C4', 'CP1', 'CP2'],
    									midline=['Fz', 'FCz', 'Cz', 'CPz', 'Pz', 'POz'])

    return eeg_ds



def _sns_read():
    locs = []
    names = []
    loc_file = []

    for line in open('/Users/teon/Dropbox/Experiments/tools/scripts/eeg_sns.txt'):
        if line.startswith('ID'):
            continue
        id, label, x, y, z = line.split()
        locs.append((x, y, z))
        names.append(label)

    return locs, names



def export_v(subname, expname='NMG'):

#Finds the file
    root = os.path.join(os.path.expanduser('~'), 'data', expname, subname)
    rawdata = os.path.join(root, 'rawdata', 'eeg')

    files = os.listdir(rawdata)
    vmrk_input = os.path.join(rawdata, fnmatch.filter(files, '%s_%s_*.*.*.vmrk' % (subname, expname))[0])
    vhdr_input = os.path.join(rawdata, fnmatch.filter(files, '%s_%s_*.*.*.vhdr' % (subname, expname))[0])

    vhdr_filename = os.path.join(rawdata, '_'.join((subname, expname)) + '.vhdr')
    vmrk_filename = os.path.join(rawdata, '_'.join((subname, expname)) + '.vmrk')
    vmrk_basename = os.path.basename(vmrk_filename)
    #vmrk_handle = '_'.join((eeg_ds.info['subname'], eeg_ds.info['expname'])) + '.vmrk'

#Extract header information
    header = open(vmrk_input).read().split('Mk2')[0]


#Initialize lists   
    markers = []
    eventIDs = []
    i_starts = []
    sizes = []
    channels = []

    for line in open(vmrk_input):
        if line.startswith('Mk'):
            if line.startswith('Mk1='):
                continue
            items = line.split(',')
            items[0] = '='.join((items[0].split('=')[0], 'Stimulus'))
            markers.append(items[0])
            eventIDs.append(items[1][1:])
            i_starts.append(int(items[2]))
            sizes.append(int(items[3]))
            channels.append(int(items[4]))

    vmrk = open(vmrk_filename, 'w')
    vmrk.write(header)
    for marker, eventID, i_start, size, channel in zip(markers, eventIDs, i_starts, sizes, channels):
        vmrk.write('%s,S%s,%s,%s,%s\r' % (marker, eventID, i_start, size, channel))
    vmrk.close()


    vhdr = open(vhdr_filename, 'w')
    for line in open(vhdr_input):
        if line.startswith('MarkerFile'):
            vhdr.write('MarkerFile=%s\r' % vmrk_basename)
        else:
            vhdr.write(line)

    print 'All Done!'



def eeg_align(subname, expname='NMG', voiceproblem=True):

    #Loads events
    eeg_ds = load_eeg_events(subname, expname)
    meg_ds = load_meg_events(subname, expname, voiceproblem)
    if 't_edf' in meg_ds:
        del meg_ds['t_edf']

    #Removes the fixations to match the eeg
    index = meg_ds['experiment'] != 'fixation'
    meg_ds = meg_ds[index]

    #Converts to milliseconds/original sampling rate then rezeros
    meg = (meg_ds['i_start'] - meg_ds['i_start'][0]) * 2

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
            diff.append(abs(meg[i] - eeg[j]))
            notflags.append(j)
            i = i + 1
            j = j + 1
        else:
            flags.append(j)
            j = j + 1

        if j >= len(eeg):
            in_the_file = 0

    #Removes the extra trigger events
    index = np.ones(eeg_ds.N, dtype='Bool')
    index[flags] = False
    combined_ds = eeg_ds[index]

    #Replaces the EEG triggers with ones from the MEG
    combined_ds['eventID'] = meg_ds['eventID']
    #Adds meg_ds['i_start']
    combined_ds['i_start_meg'] = meg_ds['i_start']
    #Adds eeg_ds['i_start']
    combined_ds['i_start_eeg'] = combined_ds['i_start']
    #Adds additional info
    combined_ds.update(meg_ds)
    combined_ds.info = eeg_ds.info

    #Deletes i_start (unlabeled)
    del combined_ds['i_start']

    return combined_ds


#This class is from Christian Brodbeck's subprocess in eelbrain



class marker_avg_file:
    def __init__(self, path):
        # Parse marker file, based on Tal's pipeline:
        regexp = re.compile(r'Marker \d:   MEG:x= *([\.\-0-9]+), y= *([\.\-0-9]+), z= *([\.\-0-9]+)')
        output_lines = []
        for line in open(path):
            match = regexp.search(line)
            if match:
                output_lines.append('\t'.join(match.groups()))
        txt = '\n'.join(output_lines)

        fd, self.path = tempfile.mkstemp(suffix='hpi', text=True)
        f = os.fdopen(fd, 'w')
        f.write(txt)
        f.close()

    def __del__(self):
        os.remove(self.path)



def kit2fiff(subname, expname='NMG', aligntol=25, sfreq=500, lowpass=30, highpass=0, stimthresh=1, stim=xrange(168, 160, -1), add=None):

    paramdir = os.path.join(os.path.expanduser('~'), 'data', expname, subname, 'parameters')

    mrk = os.path.join(paramdir, '_'.join((subname, expname, 'marker-coregis.txt')))
    elp = os.path.join(paramdir, '_'.join((subname, expname + '.elp')))
    hsp = os.path.join(paramdir, '_'.join((subname, expname + '.hsp')))
    if sfreq == 1000:
            rawtxt = os.path.abspath(os.path.join(paramdir, '..', 'rawdata', 'meg', '_'.join((subname, expname + '-export.txt'))))
    else:
        rawtxt = os.path.abspath(os.path.join(paramdir, '..', 'rawdata', 'meg', '_'.join((subname, expname + '-export' + str(sfreq) + '.txt'))))
    rawfif = os.path.abspath(os.path.join(paramdir, '..', 'myfif', '_'.join((subname, expname, 'raw.fif'))))
    sns = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'tools', 'parameters', 'sns.txt')

    # convert the marker file
    mrk_file = marker_avg_file(mrk)
    hpi = mrk_file.path

    stim = ':'.join(map(str, stim))

    cmd = ['/Applications/mne/bin/mne_kit2fiff',
           '--elp', elp,
           '--hsp', hsp,
           '--sns', sns,
           '--hpi', hpi,
           '--aligntol', aligntol,
           '--raw', rawtxt,
           '--out', rawfif,
           '--sfreq', sfreq,
           '--lowpass', lowpass,
           '--highpass', highpass,
           '--stim', stim,
           '--stimthresh', stimthresh]
    cwd = '/Applications/mne/bin/'

    if add:
        add = ':'.join((add))
        cmd = cmd + '--add %s' % add

    cmd = [unicode(c) for c in cmd]
    sp = subprocess.Popen(cmd, cwd=cwd,
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = sp.communicate()

    if stderr:
        print '\n> ERROR: %s\n%s' % (stderr, stdout)


def load_meg_events(subname, expname='NMG', bad_channels=None):

#Defines directories
    root = os.path.join(os.path.expanduser('~'), 'data', expname, subname)
    rawdata = os.path.join(root, 'rawdata')
    fifdir = os.path.join(root, 'myfif')
    datadir = os.path.join(root, 'data')

#Specifies whether it calls the subject's MRI or the average brain

    mridir = os.path.abspath(os.path.join(root, '..', '..', 'MRI', subname))

    if not os.path.lexists(mridir):
        mridir = os.path.abspath(os.path.join(root, '..', '..', 'MRI', '00'))
        hasMRI = False
    else:
        hasMRI = True

#Finds the file    
    logfile = os.path.join(rawdata, 'behavioral', 'logs', '_'.join((subname, 'log.txt')))
    fif_file = os.path.join(fifdir, '_'.join((subname, expname, 'raw.fif')))
    proj_file = os.path.join(fifdir, '_'.join((subname, expname, 'proj.fif')))
#Loads the triggerlist from the log file   
    #log = _logread(logfile)

#Loads the triggers from the fif and makes a dataset
    meg_ds = E.load.fiff.events(fif_file, proj=proj_file)
#Adds bad channel to list if provided
    if bad_channels:
        meg_ds.info['raw'].info['bads'].extend(bad_channels)

#Compares the log file to the triggerlist. Adds variable of boolean comparison
    #log = np.array(log)
#Asserts that the right value of triggers is given. Experimentally determined.
#For NMG: 4 trigger events per trial, 240 trials per list, 4 lists    
    #assert meg_ds.N == 3840
#This assures that the trigger values are equivalent to the ones in PTB
    #assert all(meg_ds['eventID'].x == log)

#Adds directory to rawfif    
    meg_ds.info['expdir'] = os.path.join(os.path.expanduser('~'), 'data', expname)
    meg_ds.info['mridir'] = mridir
    meg_ds.info['labeldir'] = os.path.join(mridir, 'label')
    meg_ds.info['fifdir'] = fifdir

#Adds the raw fif info used in epoching data.    
#    meg_ds.info['raw'] = mne.fiff.Raw(os.path.abspath(os.path.join(fifdir, '_'.join((subname, expname, 'raw.fif')))), verbose=False)
    meg_ds.info['rawfif'] = os.path.abspath(os.path.join(fifdir, '_'.join((subname, expname, 'raw.fif'))))
    meg_ds.info['proj'] = os.path.abspath(os.path.join(fifdir, '_'.join((subname, expname, 'proj.fif'))))
    meg_ds.info['subname'] = subname
    meg_ds.info['expname'] = expname
    meg_ds.info['datadir'] = datadir
    meg_ds.info['mne_bin'] = os.path.join('/Applications/mne/bin')

#Adds filenames for the source transformation
    meg_ds.info['fwd'] = os.path.join(fifdir, '_'.join((subname, expname, 'raw-fwd.fif')))
    meg_ds.info['cov'] = os.path.join(fifdir, '_'.join((subname, expname, 'raw-cov.fif')))
    meg_ds.info['inv'] = os.path.join(fifdir, '_'.join((subname, expname, 'raw-inv.fif')))
    meg_ds.info['trans'] = os.path.join(fifdir, '_'.join((subname, expname, 'raw-trans.fif')))

#Specifies filenames according for either subject's MRI or common average brain
    meg_ds.info['hasMRI'] = hasMRI

    if meg_ds.info['hasMRI'] == True:
        meg_ds.info['bem'] = os.path.join(mridir, 'bem', subname + '-5120-bem-sol.fif')
        meg_ds.info['src'] = os.path.join(mridir, 'bem', subname + '-ico-4-src.fif')
    else:
        meg_ds.info['bem'] = os.path.join(mridir, 'bem', '00-5120-bem-sol.fif')
        meg_ds.info['src'] = os.path.join(mridir, 'bem', '00-ico-4-src.fif')



#Loads the eyelink data
    edf_path = os.path.join(rawdata, 'behavioral', 'eyelink', '*.edf')
    if os.path.exists(os.path.dirname(edf_path)):
        edf = E.load.eyelink.Edf(edf_path)
        try:
            edf.add_T_to(meg_ds)
            meg_ds.info['edf'] = edf
        except ValueError:
            print 'Eyelink Module Not Working'
    else:
        print "%s%s This path does not exist. Please check your folder." % (edf_path, os.linesep)
#    elif not ui.ask(title='Missing Files', message='Subject %s Eyelink files are missing. Okay to proceed?' % subname, cancel=False, default=True):
#        raise RuntimeError('missing file')



#For the first five subjects in NMG, the voice trigger was mistakenly overlapped with the prime triggers.
#Repairs voice trigger value problem, if needed.
    index = range(3, meg_ds.N, 4)
    if all(meg_ds['eventID'][index].x > 128):
        meg_ds['eventID'][index] = meg_ds['eventID'][index] - 128



#Propagates itemID for all trigger events
#Since the fixation cross and the voice trigger is the same value, we only need to propagate it by factor of 2.
    index = meg_ds['eventID'] < 64
    scenario = map(int, meg_ds['eventID'][index])
    meg_ds['scenario'] = E.var(np.repeat(scenario, 2))

#Initialize lists    
    eventID_bin = []
    exp = []
    target = []
    cond = []
    type = []

#Decomposes the trigger
    for v in meg_ds['eventID']:
        binary_trig = bin(int(v))[2:]
        eventID_bin.append(binary_trig)

        if v > 128:
            exp.append(int(binary_trig[0], 2))
            target.append(int(binary_trig[1], 2))
            type.append(int(binary_trig[2:5], 2))
            cond.append(int(binary_trig[5:8], 2))
        else:
            exp.append(None)
            target.append(None)
            type.append(None)
            cond.append(None)

#Labels events    
    meg_ds['experiment'] = E.factor(exp, labels={None: 'fixation', 1: 'experiment'})
    meg_ds['target'] = E.factor(target, labels={None: 'fixation/voice', 0: 'prime', 1: 'target'})
    meg_ds['wordtype'] = E.factor(type, labels={None: 'None', 1: 'transparent', 2: 'opaque', 3: 'novel', 4: 'ortho', 5:'ortho'})
    meg_ds['condition'] = E.factor(cond, labels={None: 'None', 1: 'control_identity', 2: 'identity', 3: 'control_constituent', 4: 'first_constituent'})
    meg_ds['eventID_bin'] = E.factor(eventID_bin, 'eventID_bin')
#Labels the voice events
#Since python's indexing start at 0 the voice trigger is the fourth event in the trial, the following index is created.
    index = np.arange(3, meg_ds.N, 4)
    meg_ds['experiment'][index] = 'voice'
#Add subject as a redundant variable to the dataset
    meg_ds['subject'] = E.factor([meg_ds.info['subname']], rep=meg_ds.N, random = True)
#Add block to the ds. 4 events per trial, 240 trials per block
    #meg_ds['block'] = E.var(np.repeat([0, 1, 2, 3], repeats=960, axis=None))
#Makes a temporary ds
    temp = meg_ds[meg_ds['target'] == 'target']
#Add itemID to uniquely identify each word    
    itemID = temp['scenario'].x + (temp['wordtype'].x * 60)
    meg_ds['itemID'] = E.var(np.repeat(itemID, 4))

#Load the stim info from mat file
    stim_ds = _load_stims_info()

    idx = []
    for (scenario, wordtype) in zip(temp['scenario'], temp['wordtype']):
        a = scenario == stim_ds['scenario']
        b = wordtype == stim_ds['wordtype']
        idx.append(np.where(a * b)[0][0])

    stim_ds = stim_ds[idx].repeat(4)
    meg_ds.update(stim_ds)

#Load duration data and adds it to the dataset.
  #  meg_ds = _load_dur_info(meg_ds)


    return meg_ds



def _logread(filename):

#Initializes list
    triggers = []

#Reads the logfile and searches for the triggers
    for line in open(filename):
        if line.startswith('TRIGGER\tUSBBox'):
            items = line.split()
            triggers.append(int(items[2]))

    return triggers



def _load_stims_info(stims_info='/Users/teon/data/NMG/stims/stims_info.mat'):
    #Adds stim information

    stims = scipy.io.loadmat(stims_info)['stims']
    stim_ds = E.dataset()
    stim_ds['c1_rating'] = E.var(np.hstack(np.hstack(np.hstack(stims['c1_rating']))))
    stim_ds['c1_sd'] = E.var(np.hstack(np.hstack(np.hstack(stims['c1_sd']))))
    stim_ds['c1'] = E.factor(np.hstack(np.hstack(stims['c1'])))
    stim_ds['c1_freq'] = E.var(np.hstack(np.hstack(np.hstack(stims['c1_freq']))))
    stim_ds['elp_c1_nmg'] = E.var(np.hstack(np.hstack(np.hstack(stims['c1_nmg']))))
    stim_ds['word'] = E.factor(np.hstack(np.hstack(stims['word'])))
    stim_ds['word_freq'] = E.var(np.hstack(np.hstack(np.hstack(stims['word_freq']))))
    stim_ds['word_nmg'] = E.var(np.hstack(np.hstack(np.hstack(stims['word_nmg']))))
    stim_ds['wordtype'] = E.factor(np.hstack(np.hstack(np.hstack(stims['wordtype']))), labels={0: 'opaque', 1: 'transparent', 2: 'novel', 3: 'ortho'})
    stim_ds['scenario'] = E.var(np.hstack(np.hstack(np.hstack(stims['itemID']))))

    stim_ds['c2_rating'] = E.var(np.hstack(np.hstack(np.hstack(stims['c2_rating']))))
    stim_ds['c2_sd'] = E.var(np.hstack(np.hstack(np.hstack(stims['c2_sd']))))
    stim_ds['c2'] = E.factor(np.hstack(np.hstack(stims['c2'])))
    stim_ds['c2_freq'] = E.var(np.hstack(np.hstack(np.hstack(stims['c2_freq']))))
    stim_ds['elp_c2_nmg'] = E.var(np.hstack(np.hstack(np.hstack(stims['c2_nmg']))))

    return stim_ds



def _load_dur_info(meg_ds):
    durations_file = os.path.join(meg_ds.info['expdir'], meg_ds.info['subname'], 'data', '_'.join((meg_ds.info['subname'], 'durations.txt')))
    if os.path.lexists(durations_file):
        ds = E.load.txt.tsv(durations_file)
        index = sorted(range(ds.N), key=lambda x:ds['tsec'].x[x])
        ds = ds[index].repeat(4)
        assert all(ds['word'] == meg_ds['word'])
    #This imports the segmentation information for the orthographic words. Their segmentation is not done in the mat file.
        meg_ds['c1'] = ds['s1']
        meg_ds['c2'] = ds['s2']
        del ds['word'], ds['tsec'], ds['s1'], ds['s2']
        meg_ds.update(ds)

    return meg_ds



def reject_blinks(meg_ds):

    if 't_edf' in meg_ds:
        meg_ds.info['edf'].mark(meg_ds, tstart= -0.2, tstop=0.4, good=None, bad=False, use=['EBLINK'], T='t_edf', target='accept')
        meg = meg_ds.subset('accept')
        del meg['t_edf'], meg['accept']
    else:
        print 'No Eyelink data'
        meg = meg_ds

    return meg
