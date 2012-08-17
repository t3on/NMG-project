import os
import fnmatch


subjects = ['R0095', 'R0224', 'R0498', 'R0499', 'R0504']

root = os.path.join(os.path.expanduser('~'), 'data', 'NMG')

header = '\t'.join(('word', 'tsec', 's1', 's1_dur', 's2', 's2_dur'))+os.linesep



for subject in subjects:
    lines = []
    behavioral_dir = os.path.join(root, subject, 'rawdata', 'behavioral')
    audio_dir = os.path.join(behavioral_dir, 'audio')
    transcripts_dir = os.path.join(root, 'stims', 'transcripts')
    textgrids_dir = os.path.join(audio_dir, 'textgrids')


    files = os.listdir(textgrids_dir)
    files = fnmatch.filter(files, '*.TextGrid')
    
    durations_out = os.path.join(root, subject, 'data', '%s_%s.txt' %(subject, 'durations'))
    
    for file in files:
        title, ext = os.path.splitext(file)

        
        time = title.split('_')
        word = time.pop(0)
        
        time = map(int,time[-3:])
        scale = np.array([3600,60,1])
        tsec = sum(scale*time)

        transcript = open(os.path.join(transcripts_dir, word+'.txt')).read().split('\n')
        textgrid = open(os.path.join(textgrids_dir, file)).read().split('\n')
        


        durations = []
        for segment in transcript:
            try:
                i = textgrid.index(str('"%s"'%segment.upper()))-2
                points = map(float, textgrid[i:i+2])
                duration = points[1] - points[0]
                durations.append(duration)
            except ValueError:
                durations.append('NaN')
        line = '\t'.join(map(str, (word, tsec, transcript[0], durations[0], transcript[1], durations[1])))+os.linesep

        lines.append(line)    


    with open(durations_out, 'w') as FILE:
        FILE.write(header)
        [FILE.write(line) for line in lines]