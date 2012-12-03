'''
Created on Nov 11, 2012

@author: teon
'''
from scipy import interpolate
import scipy.stats.mstats as mstats
import numpy as np
import eelbrain.eellab as E

class FASTER:
    def __init__(self, data, threshold = 3, hurst = .7):
        return
    return
      
def channel_var(data, threshold):
    threshold = threshold
    data_var = np.var(data, axis = 1)
    data_var_z = mstats.zscore(data_var)
    idx = data_var_z > threshold
    bad_channels = data[idx]
    
    return bad_channels, idx

def channel_corr(data, threshold):
    threshold = threshold
    data_corr = np.corrcoef(data)
    data_mean_corr = np.mean(data_corr, axis = 1)
    data_mean_corr_z = mstats.zscore(data_mean_corr)
    idx = data_mean_corr_z > threshold
    bad_channels = data[idx]
    
    return bad_channels, idx

def hurst_exp(data, hurst = .7):
    """
    http://en.wikipedia.org/wiki/Hurst_exponent
    """
    N = np.size(data, axis = 1) 
    hurst = hurst
    data_mean = np.mean(data, axis = 1)
    data_dev = data - data_mean
    cumsum = np.cumsum(data_dev, axis = 1)
    ranges = []
    devs = []
    ns = []
    for i in range(8,0,-1):
        n = N/i
        logn = np.log(n)
        ns.append(logn)
        ranges.append(np.max(cumsum[:,n], axis = 1) - 
                      np.min(cumsum[:,n], axis = 1))
        devs.append(np.std(data[:,n], axis = 1))
    log_ratios = [np.log(data_range/data_dev) 
                  for data_range,data_dev in zip(ranges,devs)]

#    log_ratios = H*logn + c
    H_channels = []
    for channel in log_ratios:
        H, _ = np.linalg.lstsq(np.vstack(np.array([ns,np.ones(len(ns))])).T,
                               np.array(channel))
        H_channels.append(H)
    H_channels_z = mstats.zscore(H_channels)
    idx = H_channels_z > hurst
    bad_channels = H_channels_z[idx]
    
    return bad_channels, idx
    
    
    
    


def interpolate(data, bad_channels, idx):
    sensors = E.load.fiff.sensor_net(data.info['raw']).getLocs2d()
    interpolate.interp2d(x = sensors[:,0], y = sensors[:,1], z = data)
    
    
     
    