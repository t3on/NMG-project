'''
Created on Oct 19, 2012

@author: teon
'''

import numpy as np


class Sound


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

