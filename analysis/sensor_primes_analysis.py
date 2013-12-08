'''
Created on Nov 30, 2012
 
@author: teon
'''
 
import eelbrain.eellab as E
import os
import basic.process as process
import pickle
 
# raw data parameters
raw = 'calm_iir_hp1_lp40'
tmin = -0.2
tmax = 0.6
reject = {'mag': 3e-12}
decim = 2
 
# experiment parameters
e = process.NMG()
e.set(datatype='meg')
e.set(raw=raw, analysis='sensor_primes_'+raw)
 
group_ds = []
 
for _ in e:
    print e.subject
    ds = e.load_events()
    index = ds['target'].isany('prime')
    ds = ds[index]
 
    #add epochs to the dataset after excluding bad channels
    ds = e.make_epochs(ds, tmin=tmin, tmax=tmax, baseline=(None, 0), 
                       reject=reject, decim=decim, evoked=True, model ='target',
                       mne=False)
    group_ds.append(ds) 
 
#Append to group level datasets
group_ds = E.combine(group_ds)
p = E.plot.Butterfly('meg', Xax='subject', ds=group_ds)
p.figure.savefig(e.get('plot-file'))
