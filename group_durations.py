import eelbrain.eellab as E
import process

subjects = ['R0095', 'R0224', 'R0498', 'R0499', 'R0504']
datasets = []
for subject in subjects:
    meg_ds = process.load_meg_events(subname = subject)
    datasets.append(meg_ds)

group_ds = E.combine(datasets)
group_ds.info = meg_ds.info
group_ds.export(os.path.join(group_ds.info['expdir'], 'group', '_'.join((group_ds.info['expname'], 'group', 'durations.txt'))))