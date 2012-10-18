import scipy.stats as stats
import matplotlib
import matplotlib.pyplot as pyplot
import eelbrain.eellab as E
import process

subjects = ['R0095', 'R0224', 'R0498', 'R0499', 'R0504']


for subject in subjects:
    process.kit2fiff(subname = subject)
    