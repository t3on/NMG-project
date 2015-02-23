'''
Created on Jul 30, 2014

@author: teon
'''

import eelbrain as E
import os
import basic.process as process
import pickle
from mne.viz import plot_bem, plot_trans, plot_evoked
from mne.report import Report

# raw data parameters
raw = 'calm_fft_hp1_lp40'
tmin = -0.1
tmax = 0.6
reject = {'mag': 4e-12}
proj = 'group_proj'

# analysis parameters
e_type = 'epochs'

# experiment parameters
e = process.NMG()
#e = process.NMG(None, '{glyph_drive}')
e.set(raw=raw)
e.set(analysis='_'.join((e_type, raw, str(tmin), str(tmax), proj)))
e.set(datatype='meg')


root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
plots_dir = os.path.join(root, 'results', 'meg', 'qualitative')


group_ds = []

report = Report()

 # plot noise projection
if proj:
    group_proj = mne.read_proj(e.get('group_proj'))
    lout = mne.layouts.read_layout('KIT-157.lout')
    p = mne.viz.plot_projs_topomap(group_proj, layout=lout)
    report.add_section(p, 'Empty Room Noise', 'group')

for _ in e:
   subj = e.get('subject')
   print subj

   if subj not in e.scaled_subjects:
       # plot brains
       p1 = plot_bem(subject=subj, orientation='axial', show=False)
       p2 = plot_bem(subject=subj, orientation='sagittal', show=False)
       p3 = plot_bem(subject=subj, orientation='coronal', show=False)
       report.add_section([p1, p2, p3], [subj +' bem axial', subj +' bem sagittal',
                                         subj + ' bem coronal'], 'bems')
   ds = e.load_events(proj=proj)
   index = ds['target'].isany('prime', 'target')
   ds = ds[index]

   #add epochs to the dataset after excluding bad channels
   ds = e.make_epochs(ds, tmin=tmin, tmax=tmax, reject=reject, name=subj)
   if ds.info['use']:
       ds = ds.aggregate(ds['target'], drop_bad=True)
       # Append to group level datasets
       group_ds.append(ds)

       # plot grandavg
       p = mne.viz.plot_evoked(ds[ds['target'] == 'prime'][subj][0], show=False)
       report.add_section(p, subj + ' primes evoked', 'primes evoked')
       p = mne.viz.plot_evoked(ds[ds['target'] == 'target'][subj][0], show=False)
       report.add_section(p, subj + ' targets evoked', 'targets evoked')

   # plot coreg trans: needs support
#    p = plot_trans(ds.info['raw'].info, trans_fname=e.get('trans'), subject=e.subject,
#                   source='head')
#    report.add_section(p, 'trans', e.subject)

prime = []
target = []

#creates indices for prime and target
for i, _ in enumerate(group_ds):
   subject = group_ds[i]['subject'][0]
   if subject in group_ds[i]:
       idx = group_ds[i]['target'] == 'prime'
       prime.append(group_ds[i][idx][subject])
       idx = group_ds[i]['target'] == 'target'
       target.append(group_ds[i][idx][subject])

# prime
p = E.plot.Butterfly(prime)
report.add_section(p.figure, 'Group primes comparison', 'group')
# target
p = E.plot.Butterfly(target)
report.add_section(p.figure, 'Group targets comparison', 'group')

report.save(e.get('report-file', analysis='group_data_quality_%s_proj' % reject['mag']))

