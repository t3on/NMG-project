'''
Created on Dec 27, 2012

@author: teon
Adapted from Yoshi's Meginfo2.cpp and sqdread's getdata.m
'''

from mne.fiff.raw import Raw
from mne import verbose
from mne.fiff.constants import FIFF
from struct import unpack
import numpy as np
import time
import sys
import logging

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
        self.nmegchan = 157
        self.nrefchan = 3
        self.nmiscchan = self.nchan - self.nmegchan - self.nrefchan
        self.ch_names = ['MEG %03d' % ch for ch in range(self.nmegchan + 1)]
        self.ch_names.extend(['REF %03d' % ch for ch in range(self.nrefchan + 1)])
        self.ch_names.extend(['MISC %03d' % ch for ch in range(self.nmiscchan + 1)])
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






""" Import BTi / 4-D MagnesWH3600 data to fif file.


"""

logger = logging.getLogger('mne')

class RawKIT(Raw):
    """ Raw object from KIT SQD file
        Adapted from mne_bti2fiff.py

    Parameters
    ----------
    data_fname : str
        absolute path to the sqd file.
    hpi_fname : str
        absolute path to hpi marker coils file.
    elp_fname : str
        absolute path to elp digitizer points file.
    data : bool | array-like
        if array-like custom data matching the header info to be used
        instead of the data from data_fname
    verbose : bool, str, int, or None
        If not None, override default verbose level (see mne.verbose).

    Attributes & Methods
    --------------------
    See documentation for mne.fiff.Raw

    """
    @verbose
    def __init__(self, data_fname, hpi_fname, elp_fname, hsp_fname,
                 data=None, verbose=True):

        logger.info('Extracting SQD Parameters from %s...' % data_fname)
        self.params = sqd_params(data_fname)
        self._data_file = data_fname

        logger.info('Creating Raw.info structure ...')
        info = self._create_raw_info()
        self.verbose = verbose
        self._preloaded = True
        self.info = info

        logger.info('Reading raw data from %s...' % data_fname)
        self._data = self.params.get_data() if not data else data

        self.first_samp, self.last_samp = 0, self._data.shape[1] - 1
        assert len(self._data) == len(self.info['ch_names'])
        self._times = np.arange(self.first_samp, \
                                self.last_samp + 1) / info['sfreq']

        logger.info('    Range : %d ... %d =  %9.3f ... %9.3f secs' % (
                   self.first_samp, self.last_samp,
                   float(self.first_samp) / info['sfreq'],
                   float(self.last_samp) / info['sfreq']))

        # remove subclass helper attributes to create a proper Raw object.
        for attr in self.__dict__:
            if attr not in Raw.__dict__:
                del attr
        logger.info('Ready.')

    @verbose
    def _create_raw_info(self):
        """ Fills list of dicts for initializing empty fiff with 4D data
        """
        info = {}

        info['meas_id'] = None
        info['file_id'] = None
        info['meas_date'] = time.ctime()

        info['projs'] = []
        info['comps'] = []

        info['highpass'], info['lowpass'] = self.params.lowpass, self.params.highpass
        info['sfreq'] = float(self.params.sfreq)

        info['chs'] = self._create_chs()
        info['nchan'] = self.params.nchan
        info['ch_names'] = self.params.ch_names
        info['bads'] = []

        info['acq_pars'], info['acq_stim'] = None, None
        info['filename'] = None
        info['ctf_head_t'] = None
        info['dev_ctf_t'] = []
        info['filenames'] = []

        # ???
        # digitizer points
        info['dig']

        # dev-head transformation dict
        info['dev_head_t'] = {}
        info['dev_head_t']['from'] = FIFF.FIFFV_COORD_DEVICE
        info['dev_head_t']['to'] = FIFF.FIFFV_COORD_HEAD
        # ???
        # transformation matrix
        info['dev_head_t']['trans']

        logger.info('Done.')
        return info

    def _create_chs(self):
        logger.info('... Setting channel info structure.')
        chs = []
        for idx, ch_name in enumerate(self.params.ch_names, 1):
            chan_info = {}
            chan_info['cal'] = 1.0
            chan_info['coil_type'] = 6001
            chan_info['eeg_loc'] = None
            chan_info['logno'] = idx
            chan_info['scanno'] = idx
            chan_info['range'] = 1.0
            chan_info['unit_mul'] = 0 # default is 0 mne_manual p.273
            chan_info['ch_name'] = ch_name

            if ch_name.startswith('MEG'):
                chan_info['kind'] = FIFF.FIFFV_MEG_CH
                chan_info['coil_type'] = 6001
                chan_info['coord_frame'] = 1
                chan_info['unit'] = FIFF.FIFF_UNIT_T # 112 = T

            elif ch_name == 'STI 014':
                chan_info['kind'] = FIFF.FIFFV_STIM_CH

            chs.append(chan_info)

    def _create_stim_ch(self):
        stim_ch = 'STIM 014'
        self.ch_names.append(stim_ch)

        # create a synthetic channel




if __name__ == '__main__':
    raw = RawKIT(data_fname=data_fname, dev_head_t_fname=dev_head_t_fname,
                 head_shape_fname=head_shape_fname, data=data, verbose=verbose)
    raw.save(out_fname)
    raw.close()
    sys.exit(0)

