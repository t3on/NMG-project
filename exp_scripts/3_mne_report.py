import mne
from mne.report import Report
import basic.process as process
import eelbrain as E
import os
from mayavi import mlab
mlab.options.offscreen = True

e = process.NMG(None, '{home}')
raw = 'calm_fft_hp1_lp40'
e.set(raw = raw)
e.set(analysis='data_quality')
# report = Report()

for subject in subjects:
# for _ in e:
    e.set(subject=subject)
    ds = e.load_events()
    ds = ds[ds['target'] == 'prime']
    ds = e.make_epochs(ds, tmin=-.2, tmax=.6, reject={'mag': 3e-12}, baseline=(None, 0))
    # covariance
    if 'epochs' in ds:
        ds = ds.aggregate('target', drop_bad=True)
        cov = e.get('cov', raw = raw + '_auto')
        if os.path.exists(cov):
            cov = mne.read_cov(e.get('cov', raw=raw + '_auto') )
            picks = mne.pick_types(ds['epochs'][0].info)
            evoked_white = mne.cov.whiten_evoked(ds['epochs'][0], cov, picks, diag=True)
            p = evoked_white.plot(picks=picks, unit=False, hline=[-2, 2], show=False)
            report.add_figs_to_section(p, [e.subject + '_cov'], 'Covariance')
    # coregistration
    p = mne.viz.plot_trans(ds.info['raw'].info, trans_fname=e.get('trans'),
                           subject=e.subject, subjects_dir=e.get('mri_dir'),
                           ch_type='meg', source='head')
    report.add_figs_to_section(p, [e.subject + '_coreg'], 'Coregistration')
    # bem
    p = mne.viz.plot_bem(e.subject, e.get('mri_dir'), 'coronal', show=False)
    report.add_figs_to_section(p, [e.subject + '_bem_coronal'], 'Bem Coronal')
    p = mne.viz.plot_bem(e.subject, e.get('mri_dir'), 'axial', show=False)
    report.add_figs_to_section(p, [e.subject + '_bem_axial'], 'Bem Axial')
    p = mne.viz.plot_bem(e.subject, e.get('mri_dir'), 'sagittal', show=False)
    report.add_figs_to_section(p, [e.subject + '_bem_tranverse'], 'Bem Sagittal')
    

report.save(e.get('report-file'), open_browser=False)