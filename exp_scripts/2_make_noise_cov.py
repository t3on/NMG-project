from basic import process
import mne 


raw = 'calm_iir_hp1_lp40'
e = process.NMG(None, '{home}')
e.set(raw=raw)
e.exclude['subject'] = ['R0414']

for _ in e:
    raw = e.get('raw')
    ds = e.load_events(redo=True, proj=False, edf=False)
    idx = ds['experiment'] == 'fixation'
    ds = ds[idx]
    ds = ds[::4]
    ds = e.make_epochs(ds, tmin=-.2, tmax=0, decim=0, baseline=(None,0),
                       reject={'mag': 4e-12})
    ds = ds[::2]
    cov = mne.compute_covariance(ds['epochs'], method='auto')
    mne.write_cov(e.get('cov', raw = raw + '_auto'), cov)