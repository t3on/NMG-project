
#subjects = ['R0095']#, 'R0224', 'R0498', 'R0499', 'R0504']

#for subject in subjects:

meg_ds = process.load_meg_events('R0504')
meg_ds = meg_ds[meg_ds['target'] == 'target']
meg_ds = load.fiff.add_epochs(meg_ds, tstart=-0.2, tstop=0.6, baseline=(-.2,0))
gui.pca(meg_ds, Y='MEG', nplots=(1, 1), dpi=50, figsize=(10, 6))