import mne

raw = mne.io.Raw('/Volumes/GLYPH-1 TB/Experiments/NMG/data/group/empty_room_'
                 'data/mne/Empty_Room_Noise_910am_7.26.12_calm-raw.fif')
projs = mne.compute_proj_raw(raw, duration=None, n_grad=0)
layout = mne.layouts.find_layout(raw.info)

p = mne.viz.plot_projs_topomap(projs, layout=mne.layouts.find_layout(raw.info))
p.savefig('/Applications/packages/NMG-project/output/meg/projs/empty_room_proj.pdf')

mne.write_proj('/Volumes/GLYPH-1 TB/Experiments/NMG/data/group/empty_room_'
              'data/mne/empty_raw_noise-proj.fif', [projs[0]])
