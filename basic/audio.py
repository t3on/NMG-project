'''
Created on Oct 19, 2012

@author: teon
'''

import numpy as np
import os
import shutil

def make_transcripts(audio_dir, script_dir):
    files = os.listdir(audio_dir)
    audio_dict = {}
    for FILE in files:
        if os.path.splitext(FILE)[1] == '.wav': 
            lab = os.path.splitext(FILE)[0] 
            lab = lab.split('_')
            if lab[0].isdigit() or (len(lab[0]) == 0):
                lab = lab[-1]
            else:
                lab = lab[0]
#             if lab.lower() in ['practice', 'is', 'very', 'important', 'no', 'name']:
#                 continue
#             else:
            lab = lab  + '.txt'
            audio_dict[FILE] = os.path.join(script_dir, lab)
    
    for entry in audio_dict:
        trans = os.path.splitext(entry)[0] + '.lab'
        trans = os.path.join(audio_dir, trans)
        shutil.copy(audio_dict[entry], trans) 
            
def del_transcripts(audio_dir):
    files = os.listdir(audio_dir)
    for FILE in files:
        if os.path.splitext(FILE)[1] == '.wav':
            lab = os.path.splitext(FILE)[0] 
            lab = lab.split('_')
            if lab[0].isdigit() or (len(lab[0]) == 0):
                lab = lab[-1]
            else:
                lab = lab[0] 
            if lab.lower() in ['practice', 'is', 'very', 'important', 'no', 'name']:
                lab = os.path.join(audio_dir, FILE) 
                os.remove(lab)
    

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
    
