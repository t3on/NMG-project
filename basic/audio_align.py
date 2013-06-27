import subprocess
import os
import fnmatch


testing = ['test']

subjects = ['R0095', 'R0224', 'R0498', 'R0499', 'R0504']



root = os.path.join(os.path.expanduser('~'), 'data', 'NMG')


os.environ['PATH'] = ':'.join([os.getenv('PATH'), '/Applications/p2fa', '/Applications/htk'])



for subject in subjects:
    audio_dir = os.path.join(root, subject, 'rawdata', 'behavioral', 'audio')
    transcripts_dir = os.path.join(root, 'stims', 'transcripts')
    textgrids_dir = os.path.join(audio_dir, 'textgrids')
    if not os.path.lexists(textgrids_dir):
        os.mkdir(textgrids_dir)


    tmp_dir = os.path.join(audio_dir, './tmp')
    if not os.path.lexists(tmp_dir):
        os.mkdir(tmp_dir)
    files = os.listdir(audio_dir)
    files = fnmatch.filter(files, '*.wav')
    ctime = []
    trials = []

    for FILE in files:
        title, ext = os.path.splitext(FILE)
        time = title.split('_')
        word = time.pop(0)

        trials.append(word)

        time = map(int,time[-3:])
        scale = np.array([3600,60,1])
        tsec = sum(scale*time)
        ctime.append(tsec)
        
        cmd = ['/opt/local/bin/sox', os.path.join(audio_dir, file), '-r 11025',  '-c 1', os.path.join(tmp_dir, 'temp.wav')]
        cwd = '/Applications/p2fa/'
        sp = subprocess.call(cmd, cwd = cwd)
        cmd = ['python', 'align.py', os.path.join(tmp_dir, 'temp.wav'), 
               os.path.join(transcripts_dir, word+'.txt'),
            os.path.join(textgrids_dir, title+'.TextGrid')]

        sp = subprocess.Popen(cmd, cwd=cwd,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = sp.communicate()

        if stderr:
            print '\n> ERROR:'
            print '%s\n%s' %(stderr, stdout)
    

    audio_out = os.path.abspath(os.path.join(audio_dir, '..', '%s_%s.txt' % (subject, 'audio_timestamp')))

    with open(audio_out, 'w') as FILE:
            [FILE.write('%s\t%s%s' % (a, b, os.linesep)) for a, b in zip(trials, ctime)]
    
    os.remove(os.path.join(tmp_dir, 'temp.wav'))
    os.removedirs(tmp_dir)