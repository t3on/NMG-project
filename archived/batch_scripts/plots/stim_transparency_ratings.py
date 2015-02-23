import basic.process as process


e = process.NMG()
stim_ds = process.read_stim_info(e.get('stims_info')

# first constituent
idx = stim_ds['c1_rating'] != 0
idy = ~np.isnan(stim_ds['c1_rating'])
st = stim_ds[idx*idy]['c1_rating']
mpl.pyplot.hist(st)

# second constituent
idx = stim_ds['c2_rating'] != 0
idy = ~np.isnan(stim_ds['c2_rating'])
st = stim_ds[idx*idy]['c2_rating']
mpl.pyplot.hist(st)

# compound
stim_ds['st'] = stim_ds['c1_rating'].x + stim_ds['c2_rating'].x
idx = stim_ds['st'] != 0
idy = ~np.isnan(stim_ds['st'])
st = stim_ds[idx*idy]['st']
mpl.pyplot.hist(st)