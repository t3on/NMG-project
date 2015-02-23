import mne
from basic import process


e = process.NMG()
e.set(filter='iir_hp1_lp40')

for _ in e:
    raw = e.get('raw')
    ds = e.load_events(proj=False)
    fwd = mne.make_forward_solution(info=ds.info['raw'].info, 
                                    mri=e.get('trans'),
                                    src=e.get('src'), fwd=e.get('fwd'),
                                    bem=e.get('bem-sol', fmatch=True),
                                    ignore_ref=True, overwrite=True,
                                    meg=True, eeg=False)
