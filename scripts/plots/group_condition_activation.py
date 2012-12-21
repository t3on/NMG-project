#'''
#Created on Nov 29, 2012
#
#@author: teon
#'''
#
#import os
#import pickle
#import eelbrain.eellab as E
#import basic.process as process
#
root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
saved_data = os.path.join(root, 'data', 'group_ds_stcs.pickled')
plots_dir = os.path.join(root, 'results', 'meg', 'plots', 'activation')
roilabels = ['lh.fusiform', 'vmPFC', 'LATL', 'lh.inferiortemporal', 'LPTL']

#e = process.NMG()
#
#tstart = -0.1
#tstop = 0.6
#reject = 3e-12
#
#datasets = []
wordtypes = ['opaque', 'novel', 'transparent', 'ortho']
conditions = [('control_constituent', 'first_constituent'),
              ('control_identity', 'identity')]

if os.path.lexists(saved_data):
    group_ds = pickle.load(open(saved_data))
else:
    e = process.NMG()
    for _ in e.iter_vars(['subject']):
        meg_ds = e.load_events(edf=True)
        index = meg_ds['target'].isany('prime', 'target')
        meg_ds = meg_ds[index]

        #add epochs to the dataset after excluding bad channels
        orig_N = meg_ds.N
        meg_ds = E.load.fiff.add_mne_epochs(meg_ds, tstart=tstart, tstop=tstop,
                                            reject={'mag':reject}, preload=True)
        remainder = meg_ds.N*100/orig_N
        e.logger('epochs: %d' % remainder + r'% ' + 'of trials remain' )

        #do source transformation
        for roilabel in roilabels:
            meg_ds[roilabel] = e.make_stcs(meg_ds, 
                                           labels=tuple(e.rois[roilabel]), 
                                           force_fixed=False)

            #mean source activity
            meg_ds[roilabel] = meg_ds[roilabel].summary('source', name='stc')
            #baseline correct source estimates
            meg_ds[roilabel] -= meg_ds[roilabel].summary(time=(tstart, 0))

        del meg_ds['epochs']
        meg_ds = meg_ds.compress(meg_ds['target'] % meg_ds['condition']
                                 % meg_ds['wordtype'], drop_bad=True)

        #Append to group level datasets
        datasets.append(meg_ds)

    #combines the datasets for group
    group_ds = E.combine(datasets)
    E.save.pickle(group_ds, saved_data)
    
for roilabel in roilabels:
    for wtype in wordtypes:
        ida = group_ds['target'] == 'target'
        idb = group_ds['wordtype'] == wtype
        idc = group_ds['condition'].isany(conditions[0][0], conditions[0][1])
        p = E.plot.uts.stat(Y=roilabel, X='condition', ds=group_ds,
                            sub=ida * idb * idc, dev=None, ylabel = 'dSPM',
                            title='%s: %s in %s' % (roilabel, conditions[0][1], wtype),
                            legend='upper left', width=12, height=9)
        p.figure.savefig(os.path.join(plots_dir,
                        'group_%s_%s_%s.pdf' % (roilabel, conditions[0][1], wtype)))

        if wtype != 'ortho':
            idx = group_ds['target'] == 'prime'
            idy = group_ds['condition'] == 'identity'
            idz = group_ds['wordtype'].isany(wtype, 'ortho')
            q = E.plot.uts.stat(Y=roilabel, X='wordtype', ds=group_ds,
                                sub=idx * idy * idz, dev=None, ylabel = 'dSPM',
                                title='%s: %s in %s' % (roilabel, conditions[1][1], wtype),
                                legend='upper left', width=12, height=9)
            q.figure.savefig(os.path.join(plots_dir,
                            'group_%s_%s_%s.pdf' % (roilabel, conditions[1][1], wtype)))
