'''
Created on Jul 24, 2014

@author: teon
'''
import basic.process as process


e = process.NMG(None, '{external_dir}')
e.exclude = {}

layout_path = '/Applications/packages/mne-python/mne/layouts'
lout = mne.layouts.read_layout('KIT-157.lout', path=layout_path)

s_e = 'Empty_Room_Noise_910am_7.26.12_calm'
raw = mne.io.kit.read_raw_kit(os.path.join(e.get('group_dir'), 'empty room data', 'calm',
                                           s_e +'.sqd'), preload=True)
proj = mne.compute_proj_raw(raw, n_mag=2)
p = mne.viz.plot_projs_topomap(proj, layout=lout)
p.savefig(e.get('proj_plot', s_e=s_e))
mne.write_proj(os.path.join(e.get('group_dir'), 'empty room data', 'mne',
                            e.get('s_e') + '-proj.fif'), proj)

s_e = 'Empty_Room_Noise_950am_8.6.12_calm'
raw = mne.io.kit.read_raw_kit(os.path.join(e.get('group_dir'), 'empty room data', 'calm',
                                           s_e + '.sqd'), preload=True)
proj = mne.compute_proj_raw(raw, n_mag=2)
p = mne.viz.plot_projs_topomap(proj, layout=lout)
p.savefig(e.get('proj_plot', s_e=s_e))
mne.write_proj(os.path.join(e.get('group_dir'), 'empty room data', 'mne', 
                            e.get('s_e') + '-proj.fif'), proj)


#for _ in e:
#    proj = e.make_proj(write=False)
#    p = mne.viz.plot_projs_topomap(proj, layout=mne.layouts.read_layout('KIT-157.lout', 
#                                                                        path=path))
#    p.savefig(e.get('plot-file', analysis='pca', datatype='meg'))
