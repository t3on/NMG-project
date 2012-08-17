import eelbrain.eellab as E
import process

subjects = ['R0095', 'R0224', 'R0498', 'R0499', 'R0504']
datasets = []
for subject in subjects:
    meg_ds = process.load_meg_events(subname = subject)
    meg_ds = process.reject_blinks(meg_ds)
    meg_ds = datasets.append(meg_ds)

group_ds = E.combine(datasets)
group_ds.info = datasets[0].info
group_ds.export(os.path.join(group_ds.info['expdir'], 'group', '_'.join((group_ds.info['expname'], 'group', 'durations.txt'))))