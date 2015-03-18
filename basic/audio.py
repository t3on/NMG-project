'''
Created on Oct 19, 2012

@author: teon
'''

import numpy as np
from scipy.io.wavfile import read, write
import os
import subprocess
import fnmatch
import eelbrain as E
from glob import glob
from basic import process
from pyphon import pyphon as pyp


def order_textgrids(subject, data_sdir):
    script_dir = os.path.join(data_sdir, '../../../group/transcripts')
    textgrids = glob(os.path.join(data_sdir, '*.TextGrid'))
    grids = [os.path.splitext(os.path.basename(grid))[0] for grid in textgrids] 
    grids = [grid.split('_') for grid in grids]
    if grids[0][0].isdigit():
        words = [grid[-1] for grid in grids]
        timestamp = [grid[:-1] for grid in grids]
    elif len(grids[0][0]) == 0:
        words = [grid[-1] for grid in grids]
        timestamps = [grid[1:-1] for grid in grids]
    else:
        words = [grid[0] for grid in grids]
        timestamps = [grid[1:] for grid in grids]
    
    timestamps = [timestamp[3:] for timestamp in timestamps]
    timestamps = [map(int, time) for time in timestamps]
    timestamps = [time[0]*60*60 + time[1]*60 + time[2] for time in timestamps]
    ordered_textgrids = zip(timestamps, range(len(timestamps)), words, textgrids)
    ordered_textgrids.sort()
    
    parts = []
    for case in ordered_textgrids:
        word = case[-2]
        trans_file = os.path.join(script_dir, word + '.txt')
        transcript = open(trans_file, 'r').readlines()
        parts.append([a.strip() for a in transcript])

    word1s, word2s = zip(*parts)
    times, order, words, textgrids = zip(*ordered_textgrids)

    ds = E.Dataset()
    ds['time'] = E.Var(times)
    ds['order'] = E.Var(order)
    ds['word'] = E.Factor(words)
    ds['word1'] = E.Factor(word1s)
    ds['word2'] = E.Factor(word2s)
    ds['textgrid'] = E.Factor(textgrids)
    
    e = process.NMG(subject)
    dataset = e.load_events(edf=False, drop_bad_chs=False)
    dataset = dataset[dataset['target'] == 'target']
    if all(ds['word'] == dataset['word']):
        dataset.update(ds)
    else:
        raise ValueError("Words don't match up.")
    
    return dataset
    


def make_transcripts(audio_sdir, script_dir, data_sdir, name):
    ds = load_soundfiles(audio_sdir, script_dir)
    for blocknum in np.unique(ds['block']):
        filename = '_'.join((name, 'block-' + str(blocknum), 'concatenated.txt'))
        filename = os.path.join(data_sdir, filename)
        idx = ds['block'] == blocknum
        ds[idx, ('word1', 'word2')].save_txt(path = filename, 
                                             delim = os.linesep, 
                                             header = False)

    # for d in targets.itercases():
    #     if d['orthotype'] == 'ortho-2':
    #         transcript = d['word'][:-len(d['c2'])]+'\n'+d['c2']
    #     else:
    #         transcript = d['c1']+'\n'+d['word'][len(d['c1']):]
    #     f = open('/Users/teon/Desktop/transcripts/'+d['word']+'.txt', 'w')
    #     f.write(transcript)
    #     f.close()


def force_align(data_sdir):
    group_dir = '/Volumes/GLYPH-1 TB/Experiments/NMG/data/group'
    os.environ['PATH'] = ':'.join([os.getenv('PATH'), '/Applications/p2fa', 
                                   '/Applications/htk'])
    data_sdir = os.path.join(data_sdir, 'behavioral', 'audio')
    import tempfile
    tmp_dir = tempfile.mkdtemp()
    files = os.listdir(data_sdir)
    files = fnmatch.filter(files, '*.wav')

    for FILE in files:    
        lab = os.path.splitext(FILE)[0] 
        lab = lab.split('_')
        if lab[0].isdigit():
            word = lab[-1]
        elif len(lab[0]) == 0:
            word = lab[-1]
        else:
            word = lab[0]
            timestamp = lab[1:]
        title, _ = os.path.splitext(FILE)
        transcript = word + '.txt'
        textgrid = title + '.TextGrid'
        
        if word.lower() in ['practice', 'is', 'very', 'important', 'no', 'name']:
            continue
        else:
            cmd = ['/usr/local/Cellar/sox/14.4.1_1/bin/sox', os.path.join(data_sdir, FILE), 
                   '-r 11025',  '-c 1', 
                   os.path.join(tmp_dir, 'temp.wav')]        
            cwd = '/Applications/packages/p2fa/'
            sp = subprocess.call(cmd, cwd = cwd)
        
            cmd = ['python', 'align.py', os.path.join(tmp_dir, 'temp.wav'), 
                   os.path.join(group_dir, 'transcripts', transcript),
                   os.path.join(data_sdir, textgrid)]

            sp = subprocess.Popen(cmd, cwd=cwd,
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
            stdout, stderr = sp.communicate()

            if stderr:
                print '\n> ERROR:'
                print '%s\n%s' %(stderr, stdout)


def get_word_duration(dataset):
    ds = []
    for d in dataset.itercases():
        grid = pyp.Textgrid(d['textgrid'])
        ds.append(grid.export_durs())
    ds = E.combine(ds)
    dataset.update(ds['c1_dur', 'c2_dur'])

    return dataset

    
