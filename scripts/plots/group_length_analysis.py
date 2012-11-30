'''
Created on Nov 27, 2012

@author: teon
'''

#reimplement with new class

import eelbrain.eellab as E
import basic.process as process
import basic.source as source
import os

corrs_dir = os.path.join(os.path.expanduser('~'),
                        'Dropbox', 'Experiments', 'NMG', 'results', 'corrs')
subjects = [('R0095', ['MEG 151']), ('R0498', ['MEG 066']),
            ('R0504', ['MEG 031']), ('R0414', []),
            ('R0547', ['MEG 002']), ('R0574', []),
            ('R0575', []), ('R0576', ['MEG 143'])]
#('R0569', ['MEG 143', 'MEG 090', 'MEG 151', 'MEG 084'])
rois = [('lh.fusiform',), ('lh.cuneus', 'rh.cuneus')]
roilabels = ['lh.fusiform', 'cuneus']

datasets = []

tstart = -0.1
tstop = 0.6
reject = 3e-12

for subject in subjects:
    print subject[0]
    meg_ds = process.load_meg_events(subname=subject[0], expname='NMG')
    index = meg_ds['target'].isany('prime', 'target')

#create picks to remove bad channels
    if subject[1]:
        meg_ds.info['raw'].info['bads'].extend(subject[1])

    meg_ds = meg_ds[index]

    if 't_edf' in meg_ds:
        del meg_ds['t_edf']
    #meg_ds = process.reject_blinks(meg_ds)

    #add epochs to the dataset after excluding bad channels
    meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                        #baseline=(tstart, 0), reject={'mag':reject}, preload=True)
                                        reject={'mag':reject}, preload=True)

    #do source transformation
    for roi, roilabel in zip(rois, roilabels):
        meg_ds[roilabel] = source.make_stcs(meg_ds, labels=tuple(roi), force_fixed=False)

        #collapsing across sources using a root-mean squared
        meg_ds[roilabel] = meg_ds[roilabel].summary('source',
                            #func=E.statfuncs.RMS, name=lblname)
                            #use of simple mean
                            name='roi')

        #baseline correct source estimates
        meg_ds[roilabel] -= meg_ds[roilabel].summary(time=(tstart, 0))
    del meg_ds['epochs']



    #Append to group level datasets
    datasets.append(meg_ds)

#combines the datasets for group
group_ds = E.combine(datasets)


group_ds['word_length'] = E.var(map(len, group_ds['display']))

cstart = 0
cstop = .2
ctp = .05for roilabel in roilabels:
    a = E.testnd.cluster_corr(Y=group_ds[roilabel], X=group_ds['word_length'],
                              norm=group_ds['subject'], tstart=cstart, 
                              tstop=cstop, tp=ctp)
    E.plot.uts.clusters(a).figure.savefig(os.path.join(corrs_dir,
                        'group_length_%s.pdf' % roilabel))
