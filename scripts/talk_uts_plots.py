
import eelbrain.eellab as E
import process, source
datadir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'talk', 'plots')

subjects = ['R0095', 'R0498', 'R0504']
group_ds = []

labels = ['lh.parstriangularis', 'lh.medialorbitofrontal']

tstart = -0.2
tstop = 0.4
reject = 3e-12

for subject in subjects:
    subject_datasets = []
        
    meg_ds = process.load_meg_events(subname = subject, expname='NMG', voiceproblem=True)
    index = meg_ds['target'] == 'target'

    meg_ds = meg_ds[index]
    meg_ds = process.reject_blinks(meg_ds)
    meg_ds.info['epochs'] = load.fiff.mne_Epochs(meg_ds, tstart=tstart, tstop=tstop, baseline=(tstart, 0), reject={'mag':reject}, preload=True)

    for lbl in labels:
        ds = source.make_stc_epochs(meg_ds, tstart = tstart, tstop = tstop, reject = reject, label = lbl, force_fixed = True, from_file = True, method = 'rms')
#Append to subject level datasets        
        subject_datasets.append(ds)

#Combines label into one dataset   
    subject_ds = E.combine(subject_datasets)
    group_ds.append(subject_ds)

group_ds = E.combine(group_ds)

#[('identity', 'opaque'), ('identity', 'transparent'), ('identity', 'novel'), ('identity', 'ortho'), ('control_constituent', 'opaque'), ('control_constituent', 'transparent'), ('control_constituent', 'novel'), ('control_constituent', 'ortho'), ('control_identity', 'opaque'), ('control_identity', 'transparent'), ('control_identity', 'novel'), ('control_identity', 'ortho'), ('first_constituent', 'opaque'), ('first_constituent', 'transparent'), ('first_constituent', 'novel'), ('first_constituent', 'ortho')]

graph_colors = {'control_identity': 'blue', 'control_constituent': 'blue', 'identity': 'green', 
                     'first_constituent': 'green'}


for lbl in labels:
    kw = dict(legend = None, dev = None, colors = graph_colors, title = False, bottom = 0.6, top = 2.0, ylabel = 'RMS of dSPM')
    
    identity = group_ds[group_ds['condition'].isany('identity', 'control_identity')]
    identity = identity[identity['label'] == lbl]
    a = E.plot.uts.stat(identity['stc'], identity['condition'], **kw)
    a.axes[0].axvspan(.3, .4, zorder = -1, color = (.8,.8,.8))
    a.figure.savefig(os.path.join(datadir, 'priming_identity_%s.png' %lbl))
    
    constituent = group_ds[group_ds['condition'].isany('first_constituent', 'control_constituent')]
    constituent = constituent[constituent['label'] == lbl]
    b = E.plot.uts.stat(constituent['stc'], constituent['condition'], **kw)
    b.axes[0].axvspan(.3, .4, zorder = -1, color = (.8,.8,.8))
    b.figure.savefig(os.path.join(datadir, 'priming_constituent_%s.png' %lbl))
    
    colors = kw.pop('colors')
    b2 = E.plot.uts.stat(constituent['stc'], constituent['wordtype']%constituent['condition'], **kw)
    b2.axes[0].axvspan(.3, .4, zorder = -1, color = (.8,.8,.8))
    b2.figure.savefig(os.path.join(datadir, 'wt_priming_constituent_%s.png' %lbl))
    
    kw['colors'] = colors
    #Plots
    for type in group_ds['wordtype'].cells:
        kw['title'] = '%s: Source Estimates' %type
        a = identity[identity['wordtype'] == type]
        b = constituent[constituent['wordtype'] == type]
       
        a = E.plot.uts.stat(a['stc'], a['condition'], **kw)
        a.axes[0].axvspan(.3, .4, zorder = -1, color = (.8,.8,.8))
        #a.figure.legend(prop={'size':6})
        a.figure.savefig(os.path.join(datadir, '%s_identity_%s.png' %(lbl, type)))
        
        b = E.plot.uts.stat(b['stc'], b['condition'], **kw)
        b.axes[0].axvspan(.3, .4, zorder = -1, color = (.8,.8,.8))
        b.figure.savefig(os.path.join(datadir, '%s_constituent_%s.png' %(lbl, type)))