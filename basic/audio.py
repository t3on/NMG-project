'''
Created on Oct 19, 2012

@author: teon
'''

import numpy as np
from scipy.io.wavfile import read, write
import os
import subprocess
import fnmatch
import eelbrain.eellab as E


def load_soundfiles(audio_sdir, script_dir):
    files = os.listdir(audio_sdir)
    exp = []
#     times = []
#     words = []
#     files = []
    for FILE in files:
        if os.path.splitext(FILE)[1] == '.wav':
            lab = os.path.splitext(FILE)[0] 
            lab = lab.split('_')
            if lab[0].isdigit():
                word = lab[-1]
                timestamp = lab[:-1]
            elif len(lab[0]) == 0:
                word = lab[-1]
                timestamp = lab[1:-1]
            else:
                word = lab[0]
                timestamp = lab[1:] 
            if word.lower() in ['practice', 'is', 'very', 'important', 'no', 'name']:
                continue
            else:
#                 date = timestamp[:3]
                time = timestamp[3:]
                time = map(int, time)
                time = (time[0]*60*60   # hours to secs
                        + time[1]*60    # minutes to secs
                        + time[2])      # secs
                
                trans_file = os.path.join(script_dir, word + '.txt')
                transcript = open(trans_file, 'r').readlines()
                word1, word2 = [a.strip() for a in transcript]
                
                FILE = os.path.join(audio_sdir, FILE)
                
                exp.append([time, word, word1, word2, FILE])
    exp.sort()

    times, words, word1s, word2s, files = zip(*exp)
    ds = E.dataset()
    ds['time'] = E.var(times)
    ds['word'] = E.factor(words)
    ds['file'] = E.factor(files)
    ds['word1'] = E.factor(word1s)
    ds['word2'] = E.factor(word2s)
    p = -1
    block = []
    for i in xrange(ds.n_cases):
        if i%240 == 0:
            p += 1
        block.append(p)
    ds['block'] = E.var(block)
        
    
    return ds


def make_transcripts(audio_sdir, script_dir, data_sdir, name):
    ds = load_soundfiles(audio_sdir, script_dir)
    for blocknum in np.unique(ds['block']):
        filename = '_'.join((name, 'block-' + str(blocknum), 'concatenated.txt'))
        filename = os.path.join(data_sdir, filename)
        idx = ds['block'] == blocknum
        ds[idx, ('word1', 'word2')].save_txt(path = filename, 
                                             delim = os.linesep, 
                                             header = False)


def cat_soundfiles(audio_sdir, script_dir, data_sdir, name):
    ds = load_soundfiles(audio_sdir, script_dir)
    for blocknum in np.unique(ds['block']):
        filename = '_'.join((name, 'block-' + str(blocknum), 'concatenated.wav'))
        filename = os.path.join(data_sdir, filename)
        idx = ds['block'] == blocknum
        cat_list = ds['file'][idx]
        cat_soundfile = []
        rates = []
        for FILE in cat_list:
            rate, data = read(FILE)
            cat_soundfile.append(data)
            rates.append(rate)
        if all(rate == rates[0] for rate in rates):
            if cat_soundfile[0].ndim == 1:
                cat_soundfile = np.hstack(cat_soundfile)
            elif cat_soundfile[0].ndim == 2:
                cat_soundfile = np.vstack(cat_soundfile)
            else:
                raise TypeError('Not a proper soundfile!')
            write(filename, rate, cat_soundfile)


def force_align(data_sdir):

    os.environ['PATH'] = ':'.join([os.getenv('PATH'), '/Applications/p2fa', 
                                   '/Applications/htk'])
    
    import tempfile
    tmp_dir = tempfile.mkdtemp()
    files = os.listdir(data_sdir)
    files = fnmatch.filter(files, '*.wav')

    for FILE in files:
        title, _ = os.path.splitext(FILE)
        transcript = title + '.txt'
        textgrid = title + '.TextGrid'
        
        cmd = ['/opt/local/bin/sox', os.path.join(data_sdir, FILE), 
               '-r 11025',  '-c 1', 
               os.path.join(tmp_dir, 'temp.wav')]        
        cwd = '/Applications/p2fa/'
        sp = subprocess.call(cmd, cwd = cwd)
        
        cmd = ['python', 'align.py', os.path.join(tmp_dir, 'temp.wav'), 
               os.path.join(data_sdir, transcript),
               os.path.join(data_sdir, textgrid)]

        sp = subprocess.Popen(cmd, cwd=cwd,
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
        stdout, stderr = sp.communicate()

        if stderr:
            print '\n> ERROR:'
            print '%s\n%s' %(stderr, stdout)
    

class Sound:


    def wav(soundfile):
        rate, data = read(soundfile)
        return rate, data
    
    def window_rms(soundfile, window_size):
        rate, data = wav(soundfile)
        data2 = np.power(data, 2)

    #This is done to in order for the convolution to be the mean of the squared sound pressure    
        window = np.ones(window_size) / float(window_size)
    
    #The padding added is 2(w-1)    
    #This returns an array A, that is A.N - w (window size).
    #The sqrt finishes the RMS
        return np.sqrt(np.convolve(data2, window, 'valid'))
    

    def detect_onset(soundfile, window_size, threshold):
        rms_data = window_rms(soundfile, window_size)
        index = rms_data > threshold
        exceed = np.flatnonzero(index)[0]
    
