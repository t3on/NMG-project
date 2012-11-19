#Modification of the sensor cluster used in Morris (2007).
##T7/8 > P7/8
##There are no T3/4 sensors. Instead there are three additional midline electrodes:
###FCz, CPz, POz
##with load.fiff.add_epochs, the sensors are indexed starting with 0. May differ if working in mne.

import eelbrain.eellab as E
import process, source

subjects = ['R0095', 'R0224', 'R0498', 'R0504']
datasets = []

for subject in subjects:
    eeg_ds = process.eeg_align(subject)
    eeg_ds = process.reject_blinks(eeg_ds)
    eeg_ds = eeg_ds.subset(eeg_ds['target'] == 'target')

    
    eeg_ds.info['erps'] = os.path.join(eeg_ds.info['datadir'], '_'.join((eeg_ds.info['subname'], 'eeg', 'erps.txt')))
#    eeg_ds.info['sns_clusters'] = dict(
#            outer = E.factor([0, 1, 8, 9, 10, 11, 12, 13],  labels = {0: 'Fp1', 1: 'Fp2', 8: 'O1', 9: 'O2', 10: 'F7', 11: 'F8', 12: 'P7', 13: 'P8'}),
#            midlateral = E.factor([2, 3, 6, 7, 24, 25, 26, 27], labels = {2:'F3', 3:'F4', 6:'P3', 7:'P4', 24:'FC5', 25:'FC6', 26:'CP5', 27:'CP6'}),
#            inner = E.factor([4, 5, 20, 21, 22, 23], labels = {4:'C3', 5:'C4', 20:'FC1', 21:'FC2', 22:'CP1', 23:'CP2'}),
#            midline = E.factor([14, 15, 16, 17, 18, 19], labels = {14:'Fz', 15:'FCz', 16:'Cz', 17:'CPz', 18:'Pz', 19:'POz'}))
    
    
    eeg_ds.info['sns_clusters'] = dict(
            outer = E.var([0, 1, 8, 9, 10, 11, 12, 13]),
            midlateral = E.var([2, 3, 6, 7, 24, 25, 26, 27]),
            inner = E.var([4, 5, 20, 21, 22, 23]),
            midline = E.var([14, 15, 16, 17, 18, 19]))
    
    load.fiff.add_epochs(eeg_ds, tstart =-.2, tstop = .5, baseline= (-.2,0), 
        unit ='V', proj=False, data='eeg', target='EEG', i_start = 'i_start_eeg', sensors = eeg_ds.info['sensors'])
    
    eeg_ds['outer'] = eeg_ds['EEG'].subdata(sensor = eeg_ds.info['sns_clusters']['outer'].x)
    eeg_ds['outer_n250'] = eeg_ds['outer'].summary('sensor', time = (.2, .3))
    eeg_ds['outer_n400'] = eeg_ds['outer'].summary('sensor', time = (.3, .5))
    eeg_ds['outer_p300'] = eeg_ds['outer'].summary('sensor', time = (.25, .35))
    
    eeg_ds['midlateral'] = eeg_ds['EEG'].subdata(sensor = eeg_ds.info['sns_clusters']['midlateral'].x)
    eeg_ds['midlateral_n250'] = eeg_ds['midlateral'].summary('sensor', time = (.2, .3))
    eeg_ds['midlateral_n400'] = eeg_ds['midlateral'].summary('sensor', time = (.3, .5))
    eeg_ds['midlateral_p300'] = eeg_ds['midlateral'].summary('sensor', time = (.25, .35))
        
    eeg_ds['inner'] = eeg_ds['EEG'].subdata(sensor = eeg_ds.info['sns_clusters']['inner'].x)
    eeg_ds['inner_n250'] = eeg_ds['inner'].summary('sensor', time = (.2, .3))
    eeg_ds['inner_n400'] = eeg_ds['inner'].summary('sensor', time = (.3, .5))
    eeg_ds['inner_p300'] = eeg_ds['inner'].summary('sensor', time = (.25, .35))
    
    eeg_ds['midline'] = eeg_ds['EEG'].subdata(sensor = eeg_ds.info['sns_clusters']['midline'].x)
    eeg_ds['midline_n250'] = eeg_ds['midline'].summary('sensor', time = (.2, .3))
    eeg_ds['midline_n400'] = eeg_ds['midline'].summary('sensor', time = (.3, .5))
    eeg_ds['midline_p300'] = eeg_ds['midline'].summary('sensor', time = (.25, .35))

    eeg_ds.export(eeg_ds.info['erps'])    
    del eeg_ds['outer'], eeg_ds['midlateral'], eeg_ds['inner'], eeg_ds['midline']
    del eeg_ds['size'], eeg_ds['channel'], eeg_ds['EEG']
    datasets.append(eeg_ds)

group_ds = E.combine(datasets)
group_ds.export(os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'data', 'NMG_group_erps.txt'))




