#source.py
#A collections of methods used to take data from sensor space to source space
##Teon Brooks
##July 26, 2012

#1. make proj
#2. noise covariance
#3. make fwd
#4. make_stc_epochs

import os
import mne
import numpy as np
import eelbrain.eellab as E
import subprocess

__hide__ = ['os', 'np', 'subprocess', 'mne']



def make_proj(meg_ds, write=True):
#add the projections to this object by using 

	meg_ds_fix = meg_ds[meg_ds['experiment'] == 'fixation']
	epochs = E.load.fiff.mne_Epochs(meg_ds_fix, tstart= -0.2, tstop=.6, baseline=(None, 0), reject={'mag':1.5e-11})
	proj = mne.proj.compute_proj_epochs(epochs, n_grad=0, n_mag=5, n_eeg=0)


	if write == True:
		first_proj = [proj[0]]
		mne.write_proj(meg_ds.info['proj'], first_proj)
		print 'Projection written to file'


	pc = [proj[0]]

	return pc



def make_cov(meg_ds, write=True):
# create covariance matrix

	index = meg_ds['experiment'] == 'fixation'
	meg_ds_fix = meg_ds[index]

	meg_ds_fix = make_proj(meg_ds_fix, write=False)

	epochs = E.load.fiff.mne_Epochs(meg_ds_fix, baseline=(None, 0), reject={'mag':2e-12}, tstart= -.2, tstop=.2)
	cov = mne.cov.compute_covariance(epochs)

	if write == True:
		cov.save(meg_ds.info['cov'])
		print 'Covariance Matrix written to file'

	return cov



def make_fwd(meg_ds, fromfile=True, overwrite=False):
# create the forward solution
	#os.environ['SUBJECTS_DIR'] = mri_dir
	if fromfile:
		cov = meg_ds.info['cov']
	else:
		cov = make_cov(meg_ds, write=False)

# this is added to create the correct fwd model for the subjects without MRIs.
	if meg_ds.info['hasMRI'] == False:
		subject = '00'
	else:
		subject = meg_ds.info['subname']

	src = meg_ds.info['src']
	trans = meg_ds.info['trans']
	bem = meg_ds.info['bem']
	fwd = meg_ds.info['fwd']
	mri_sdir = meg_ds.info['mridir']
	rawfif = meg_ds.info['rawfif']

	cwd = meg_ds.info['mne_bin']
	cmd = ['mne_do_forward_solution',
	   '--subject', subject,
	   '--src', src,
	   '--bem', bem,
	   '--mri', trans, # MRI description file containing the MEG/MRI coordinate transformation.
	   '--meas', rawfif, # provides sensor locations and coordinate transformation between the MEG device coordinates and MEG head-based coordinates.
	   '--fwd', fwd, #'--destdir', target_file_dir, # optional 
	   '--megonly']

	if overwrite:
		cmd.append('--overwrite')
	elif os.path.exists(fwd):
		raise IOError("fwd file at %r already exists" % fwd)

	sp = subprocess.Popen(cmd, cwd=cwd,
						  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = sp.communicate()

	if stderr:
		print '\n> ERROR:'
		print stderr

	if os.path.exists(fwd):
		return fwd
		print 'Forward Solution written to file'

	else:
		err = "fwd-file not created"
		err = os.linesep.join([err, "command out:", stdout])
		raise RuntimeError(err)


def make_stc_epochs(meg_ds, tstart= -0.2, tstop=0.4, reject=3e-12, label='label', label2=None, force_fixed=True):
#creates a dataset with all the epochs given from the meg_ds

	if from_file:
		cov = mne.read_cov(meg_ds.info['cov'])

	fwd = mne.read_forward_solution(meg_ds.info['fwd'], force_fixed=force_fixed) #there is currently no solution for creating the fwd as an object.

	# create the inverse solution
	inv = mne.minimum_norm.make_inverse_operator(meg_ds['epochs'].info, fwd, cov, loose=None)
	roi = mne.read_label(os.path.join(meg_ds.info['labeldir'], label + '.label'))
	if label2:
		roi2 = mne.read_label(os.path.join(meg_ds.info['labeldir'], label2 + '.label'))
		roi = roi + roi2
	stcs = mne.minimum_norm.apply_inverse_epochs(meg_ds['epochs'], inv, lambda2=1. / 9, label=roi) #a list of lists of all sources within label per epoch.

	if label2:
		labelname = '%s+%s' % (label, label2)
	else:
		labelname = label

	if meg_ds.info['hasMRI']:
		meg_ds[labelname] = E.load.fiff.stcs_ndvar(stcs, subject=meg_ds.info['subname'])
	else:
		meg_ds[labelname] = E.load.fiff.stcs_ndvar(stcs, subject='00')

	meg_ds.info['erfs'] = os.path.join(meg_ds.info['datadir'], '%s_%s_erfs.txt' % (meg_ds.info['subname'], meg_ds.info['expname']))
	
	return meg_ds

def export_erfs(ds):

	#for a given time region
	ds['m170'] = ds['stc'].summary(time=(.12, .22))
	ds['m250'] = ds['stc'].summary(time=(.2, .3))
	ds['m350'] = ds['stc'].summary(time=(.3, .4))

	ds.export(fn=ds.info['erfs'])

	print 'Export completed'

#deprecated
def _export_stcs(ds):
	timetemp = np.around(ds['stc'].time.x, decimals=3) * 1000 #header to be represented in milliseconds
	timetemp = map(str, timetemp)
	time = []
	for point in timetemp:
		time.append(point + 'ms')

	np.savetxt(ds.info['stc'], np.vstack((time, ds['stc'].x)), fmt='%s', delimiter='\t', newline='\n')
	ds.export(ds.info['stc_ds'])

	print 'Export completed'

#deprecated
def _combine_group_stcs(exp='NMG', label='label'):
	expdir = os.path.join(os.path.expanduser('~'), 'data', exp)
	list = os.listdir(expdir)
	subjects = []
	for item in list:
		if item.startswith('R'):
			subjects.append(item)

	files = []
	for subject in subjects:
		files.append(os.path.join(expdir, subject, 'data', '_'.join((subject, label, 'erfs.txt'))))

	exportfile = open(os.path.join(expdir, 'group', '%s_group_%s_erfs.txt' % (exp, label)), 'w')

	for iter, file in enumerate(files):
		if os.path.lexists(file) and not(open(file).read().endswith('\r\n')): # or open(file).read().endswith('\r')):
			if iter == 0:
				exportfile.write(open(file).read() + '\r\n')
			else:
				exportfile.write('\r\n'.join((open(file).read().split('\r\n')[1:])) + '\r\n')
		elif os.path.lexists(file) and open(file).read().endswith('\r\n'):
			if iter == 0:
				exportfile.write(open(file).read())
			else:
				exportfile.write('\r\n'.join((re.split('\r\n', open(file).read())[1:])))

	exportfile.close()



