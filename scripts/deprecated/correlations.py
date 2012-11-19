import scipy.stats as stats
import matplotlib
import matplotlib.pyplot as pyplot

corrs_dir = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'write-up', 'corrs')
subjects = ['R0095', 'R0224', 'R0498', 'R0499']
labels = ['lh.fusiform', 'lh.temporalpole']

datasets = []



for subject in subjects:
    for iter, lbl in enumerate(labels):

        meg_ds = process.load_meg_events(subname = subject, expname='NMG', voiceproblem=True)
        index1 = meg_ds['target'] == 'target'
        index2 = meg_ds['wordtype'].isany('opaque', 'transparent')

        meg_ds = meg_ds[index1*index2]
        meg_ds = process.reject_blinks(meg_ds)

        ds = source.make_stc_epochs(meg_ds, reject=4e-12, label=lbl, from_file=True)

#This z-scores your data for each subject separately 
        ds['stc'].x = stats.mstats.zscore(ds['stc'].x)

        datasets.append(ds)
        
group_ds = E.combine(datasets)
group_ds.info = datasets[0].info['raw'].info

sfreq = float(group_ds.info['sfreq'][0])

start = abs(group_ds['stc'].time.x[0]*sfreq)
time = np.round(group_ds['stc'].time.x[start:]*1000)

effects = ['c1_freq', 'c2_freq', 'word_freq', 'c1_nmg', 'c2_nmg', 'word_nmg', 'c1_rating', 'c2_rating']
titles = ['C1 Frequency', 'C2 Frequency', 'Word Frequency', 'C1 NMG Latency', 'C2 NMG Latency', 'Word NMG Latency', 'C1 Transparency', 'C2 Transparency']
lbl_titles = ['Left Fusiform', 'Left Temporal Pole']


for effect, title in zip(effects, titles):
    corrs = []
    sigs = []
    for i, lbl in enumerate(labels):
        corr = []
        sig = []
        index1 = group_ds['label'] == lbl
        index2 = ~np.isnan(group_ds[effect])
        ds = group_ds[index1*index2]
        stc = ds['stc'].x[:,start:]

        for sample in range(stc.shape[1]):
            r, p = stats.pearsonr(stc[:,sample], ds[effect].x)
            corr.append(r)
            sig.append(p)

        corrs.append(corr)
        sigs.append(sig)


        index = np.array(sigs[i]) <= 0.05
        if any(index) == True:
            sigvalue = np.array(corrs[i])[index].min()

            pyplot.figure()
            pyplot.plot(time, corrs[i])
            pyplot.plot(time, sigvalue*np.ones(time.shape), 'g--')
            pyplot.plot(time, -sigvalue*np.ones(time.shape), 'g--')
            pyplot.xlabel('Time from Stimulus Onset (ms)')
            pyplot.ylabel('Strength of Correlation')
            pyplot.title('Effects of %s on %s Activity' %(title, lbl_titles[i]))
            pyplot.savefig(os.path.join(corrs_dir, '%s-%s.png' %(lbl, effect)))
        else:
            continue
