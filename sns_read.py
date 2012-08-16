import numpy as np

locs = []
names = []
loc_file = []

for line in open('/Users/teon/Dropbox/Experiments/tools/scripts/eeg_sns.txt'):
    if line.startswith('ID'):
        continue
    id, label, x, y, z = line.split()
    locs.append((x,y,z))
    names.append(label)
    
#    loc_file.append('\t'.join((str(x),str(y),str(z), label)))

#a = open('/Users/teon/Dropbox/Experiments/tools/scripts/eeg_sns.txt', 'w')
#a.write(os.linesep.join(loc_file))
#a.close()


sensors = V.sensors.sensor_net(locs = locs, names = names, transform_2d = None)
