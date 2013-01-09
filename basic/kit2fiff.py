'''
Created on Dec 27, 2012

@author: teon
Adapted from Yoshi's Meginfo2.cpp and sqdread's getdata.m
'''

from struct import unpack
import numpy as np

class sqd_params(object):
    '''
    classdocs
    '''


    def __init__(self, rawfile, lowpass=None, highpass=None):
        '''
        Constructor
        '''
        self.dynamic_range = 2 ** 12 / 2    # signed integer. range +/- 2048
        self.voltage_range = 5.
        self.rawfile = rawfile
        fid = open(rawfile, 'r')
        fid.seek(16)    # get offset of basic info
        basic_offset = unpack('i', fid.read(4))[0]  # integer are 4 bytes
        fid.seek(basic_offset)

        # basic info
        self.version = unpack('i', fid.read(4))[0]
        self.revision = unpack('i', fid.read(4))[0]
        self.sysid = unpack('i', fid.read(4))[0]
        self.sysname = unpack('128s', fid.read(128))[0].split('\n')[0]
        self.modelname = unpack('128s', fid.read(128))[0].split('\n')[0]
        self.nchan = unpack('i', fid.read(4))[0]
        self.ch_names = ['MEG %03d' % ch for ch in range(self.nchan)]
        self.lowpass = lowpass
        self.highpass = highpass

        # amplifier gain
        fid.seek(112)
        amp_offset = unpack('i', fid.read(4))[0]
        fid.seek(amp_offset)
        amp_data = unpack('i', fid.read(4))[0]
        input_gain_bit = 11    # stored in Bit-11 to 12
        input_gain_mask = 6144  # (0x1800)
        # input_gain: 0:x1, 1:x2, 2:x5, 3:x10
        input_gains = [1, 2, 5, 10]
        self.input_gain = input_gains[(input_gain_mask & amp_data)
                                      >> input_gain_bit]
        # 0:x1, 1:x2, 2:x5, 3:x10, 4:x20, 5:x50, 6:x100, 7:x200
        output_gains = [1, 2, 5, 10, 20, 50, 100, 200]
        output_gain_bit = 0    # stored in Bit-0 to 2
        output_gain_mask = 7   # (0x0007)
        self.output_gain = output_gains[(output_gain_mask & amp_data)
                                        >> output_gain_bit]

        # channel sensitivities
        # only channels 0-159 requires gain. the additional channels
        # (trigger channels, audio and voice channels) are passed 
        # through unaffected

        fid.seek(80)
        sens_offset = unpack('i', fid.read(4))[0]
        fid.seek(sens_offset)
        sens = np.fromfile(fid, dtype='d', count=self.nchan * 2)
        self._sensitivities = np.reshape(sens, (self.nchan, 2))
        self.sensor_gain = np.ones(self.nchan)
        self.sensor_gain[:160] = self._sensitivities[:160, 1]

        # sampling info
        fid.seek(128)
        acqcond_offset = unpack('i', fid.read(4))[0]
        fid.seek(acqcond_offset)
        acq_type = unpack('i', fid.read(4))[0]
        if acq_type == 1:
            self.sfreq = unpack('d', fid.read(8))[0]
            _ = fid.read(4) # initialized estimate of samples 
            self.nsamples = unpack('i', fid.read(4))[0]
        else:
            raise NotImplementedError

        # data offset info    
        fid.seek(144)
        self.data_offset = unpack('i', fid.read(4))[0]

    def get_data(self):
        fid = open(self.rawfile, 'r')
        fid.seek(self.data_offset)
        data = np.fromfile(fid, dtype='h', count=self.nsamples * self.nchan)
        data = np.reshape(data, (self.nsamples, self.nchan))
        # amplifier applies only to the sensor channels 0-159
        amp_gain = self.output_gain * self.input_gain
        self.sensor_gain[:160] = self.sensor_gain[:160] / amp_gain
        conv_factor = np.array((self.voltage_range / self.dynamic_range) *
                               self.sensor_gain, ndmin=2)
        self.x = (conv_factor * data).T

