bad_channels = {
                'R0370': [54],
                'R0560': [18,26],
                'R0562': [18],
                'R0575': [2,3,9,10,12,17,18],
                'R0605': [18],
                }
                
meg = lambda x: 'MEG %03d' %(x+1)

for entry in bad_channels.keys():
    bad_channels[entry] = [meg(x) for x in bad_channels[entry]]