import mne
from basic import process
from mne.report import Report

e = process.NMG()
e.set(filter='iir_hp1_lp40')

e.exclude['subject'] = ['R0095', 'R0224', 'R0338', 'R0370', 'R0414']
for _ in e:
    report = Report()
    raw = e.get('raw')
    ds = e.load_events(proj=False)
    ds = ds[ds['target'] == 'prime']
    ds = e.make_epochs(ds, tmin=-.1, tmax=.6, decim=2,
                       reject={'mag': 4e-12}, evoked=True, model='target')
    if 'epochs' in ds:
        cov = mne.read_cov(e.get('cov'))
        picks = mne.pick_types(ds.info['raw'].info)
        whiten = mne.whiten_evoked(ds['epochs'][0], cov, picks, diag=False)
    
        fig = whiten.plot(picks=picks, unit=False, hline=[-2, 2])
        report.add_figs_to_section([fig], ['whiten data'], 'covariance')
    
        report.save(e.get('report-file', analysis='{s_e}_data_quality'),
                    open_browser=False)
    