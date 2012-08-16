PyShell 0.9.5 - The Flakiest Python Shell
Python 2.7.2 |EPD 7.2-2 (32-bit)| (default, Sep  7 2011, 09:16:50) 
[GCC 4.0.1 (Apple Inc. build 5493)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
Startup script executed: /Users/christian/Documents/eelbrain/startup
>>> 5 /4
1
>>> type(5)
<type 'int'>
>>> type(5.)
<type 'float'>
>>> 5 / 4.
1.25
>>> 5. /4
1.25
>>> from __future__ import division
>>> 5/4
1.25
>>> dir()
['A', 'AEDesc', 'B', 'EventTypeSpec', 'V', '__builtins__', '__doc__', '__file__', '__name__', '__package__', '_app', '_app_module', '_argv_emulation', '_chdir_resource', '_ctypes_setup', '_path_inject', '_reset_sys_path', '_run', '_run_argvemulator', '_site_packages', 'attach', 'ctypes', 'detach', 'division', 'gui', 'help', 'mnel', 'mpl', 'np', 'os', 'pickle', 'plot', 'plt', 'print_function', 'printdict', 'printlist', 'shell', 'sp', 'struct', 'sys', 'time']
>>> A
<module 'eelbrain.analyze' from '/Users/christian/Documents/Eclipse/EELBRAIN RELOADED/EELBRAIN/eelbrain/analyze/__init__.pyo'>
>>> numpy
Traceback (most recent call last):
  File "<input>", line 1, in <module>
NameError: name 'numpy' is not defined
>>> import numpy
>>> numpy
<module 'numpy' from '/Library/Frameworks/Python.framework/Versions/7.2/lib/python2.7/site-packages/numpy/__init__.py'>
>>> numpy.all
<function all at 0x27720f0>
>>> import numpy as np
>>> a=1
>>> a='dsa'
>>> a
'dsa'
>>> a.capitalize()
'Dsa'
>>> a.endswith('s')
False
>>> a.endswith('a')
True
>>> a.upper()
'DSA'
>>> 'dsa'
'dsa'
>>> a = [1, 2, 3, 'dsa']
>>> a
[1, 2, 3, 'dsa']
>>> a[4]
Traceback (most recent call last):
  File "<input>", line 1, in <module>
IndexError: list index out of range
>>> a[3]
'dsa'
>>> range(9)
[0, 1, 2, 3, 4, 5, 6, 7, 8]
>>> range(1, 10)
[1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> for i in range(9):
...     print i+1
...     
1
2
3
4
5
6
7
8
9
>>> d = {'a': 3, 'e': 7}
>>> d
{'a': 3, 'e': 7}
>>> {'a': 3, 'e': 7}
{'a': 3, 'e': 7}
>>> d
{'a': 3, 'e': 7}
>>> d['a']
3
>>> a = [1, 2, 3]
>>> a
[1, 2, 3]
>>> d={2: a}
>>> d
{2: [1, 2, 3]}
>>> a
[1, 2, 3]
>>> a[1] = 7
>>> a
[1, 7, 3]
>>> d
{2: [1, 7, 3]}
>>> d['a']
Traceback (most recent call last):
  File "<input>", line 1, in <module>
KeyError: 'a'
>>> d = {'a': 3, 'e': 7}
>>> d['a']
3
>>> d['a'] = 8
>>> d
{'a': 8, 'e': 7}
>>> d
{'a': 8, 'e': 7}
>>> for key, value in d.iteritems():
...     print '%s: %s' % (key, value)
...     
a: 8
e: 7
>>> d['d'] = 'dsa'
>>> d
{'a': 8, 'e': 7, 'd': 'dsa'}
>>> for key, value in d.iteritems():
...     print '%s: %s' % (key, value)
...     
a: 8
e: 7
d: dsa
>>> {1, 2, 3}
set([1, 2, 3])
>>> {1, 2, 7, 3}
set([1, 2, 3, 7])
>>> np.array([1, 2, 3, 4, 2])
array([1, 2, 3, 4, 2])
>>> a = np.array([1, 2, 3, 4, 2])
>>> a
array([1, 2, 3, 4, 2])
>>> l = [1, 2, 3, 4, 2]
>>> a = np.array(l)
>>> a
array([1, 2, 3, 4, 2])
>>> plt
<module 'matplotlib.pyplot' from '/Library/Frameworks/Python.framework/Versions/7.2/lib/python2.7/site-packages/matplotlib/pyplot.py'>
>>> plt
<module 'matplotlib.pyplot' from '/Library/Frameworks/Python.framework/Versions/7.2/lib/python2.7/site-packages/matplotlib/pyplot.py'>
>>> import matplotlib.pyplot as plt
>>> plt.plot(a)
[<matplotlib.lines.Line2D object at 0x1aa52610>]
>>> dir()

>>> dir(plt)

>>> from pylab import *
>>> dir()

>>> plot(a)
[<matplotlib.lines.Line2D object at 0x20669c70>]
>>> sin
<ufunc 'sin'>
>>> mnel
<module 'eelbrain.utils.mne_link' from '/Users/christian/Documents/Eclipse/EELBRAIN RELOADED/EELBRAIN/eelbrain/utils/mne_link.pyo'>
>>> '%s nfdsn ds' % 'dsa'
'dsa nfdsn ds'
>>> '%s nfdsn ds' % a
'[1 2 3 4 2] nfdsn ds'
>>> '{ga} hjklhkl'.format(ga=a)
'[1 2 3 4 2] hjklhkl'
>>> '{ga} hjklhkl'.format(ga=a, hjkl='ew')
'[1 2 3 4 2] hjklhkl'
>>> hjkl
Traceback (most recent call last):
  File "<input>", line 1, in <module>
NameError: name 'hjkl' is not defined
>>> def fun():
...     return 5
...     
>>> fun()
5
>>> fun() + 1
6
>>> def fun(x):
...     return x+5
...     
>>> fun()
Traceback (most recent call last):
  File "<input>", line 1, in <module>
TypeError: fun() takes exactly 1 argument (0 given)
>>> fun(4)
9
>>> def fun(x=7):
...     return x+5
...     
>>> fun()
12
>>> fun(2)
7
>>> fun(x=2)
7
>>> fun(x=3)
8
>>> def fun(y, x=7):
...     return y * x + 5
...     
>>> fun(2)
19
>>> a=4
>>> a
4
>>> class A:
...     pass
...     
>>> A
<class __main__.A at 0x2120fea0>
>>> A()
<__main__.A instance at 0x204fb2d8>
>>> a = A()
>>> a
<__main__.A instance at 0x212214b8>
>>> a
<__main__.A instance at 0x212214b8>
>>> a.__class__
<class __main__.A at 0x2120fea0>
>>> class A:
...     def __init__(self):
...         pass
...     
>>> class A:
...     def __init__(self):
...         self.value = 6
...     
>>> a = A()
>>> a
<__main__.A instance at 0x212215f8>
>>> a.value
6
>>> class A:
...     def __init__(self, value):
...         self.value = value
...     
>>> a = A(4)
>>> a
<__main__.A instance at 0x21221648>
>>> a.value
4
>>> class A:
...     def __init__(self, value):
...         self.value = value
...     def show_the_value(self):
...         print "it is %s" % self.value
...     
>>> A
<class __main__.A at 0x21202f48>
>>> a = A()
Traceback (most recent call last):
  File "<input>", line 1, in <module>
TypeError: __init__() takes exactly 2 arguments (1 given)
>>> a = A(4)
>>> a
<__main__.A instance at 0x21221468>
>>> a.show_the_value()
it is 4
>>> class A:
...     def __init__(self, value):
...         self.value = value
...     def show_the_value(self):
...         return "it is %s" % self.value
...     
>>> a = A()
Traceback (most recent call last):
  File "<input>", line 1, in <module>
TypeError: __init__() takes exactly 2 arguments (1 given)
>>> a = A(6)
>>> a.show_the_value()
'it is 6'
>>> t = a.show_the_value()
>>> t
'it is 6'
>>> mnel.kit2fiff(meg_sdir=u'/Volumes/server/MORPHLAB/Teon/experiment/meg/R0447', experiment='naming', sfreq=1000, aligntol=25, mrk=(u'/Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/parameters/R0447_MARKER-PRETEST_3.26.12-coregis.txt',), elp=('{param_dir}', '{subject}.elp'), hsp=('{param_dir}', '{subject}.hsp'), sns=('~/Documents/Eclipse/Eelbrain\\ Reloaded/aux_files/sns.txt',), raw=('{meg_sdir}', 'raw', 'R0447_NAMING_3.26.12-export.txt'), out=('{meg_sdir}', 'myfif', '{subject}_{experiment}_raw.fif'), stim=xrange(168, 160, -1))
>COMMAND:
mne_kit2fiff --raw /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/raw/R0447_NAMING_3.26.12-export.txt --hsp /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/parameters/R0447.hsp --stim 168:167:166:165:164:163:162:161 --sns ~/Documents/Eclipse/Eelbrain\ Reloaded/aux_files/sns.txt --aligntol 25 --elp /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/parameters/R0447.elp --sfreq 1000 --hpi /var/folders/i1/i1ypyFthF1C1O9FkPskdLk+++U2/-Tmp-/tmpI6kg0Jhpi --out /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/myfif/R0447_naming_raw.fif
>OUT:

>ERROR:

mne_kit2fiff version 1.5 compiled at Jan  7 2011 02:26:43

elp file                     : /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/parameters/R0447.elp
hpi file                     : /var/folders/i1/i1ypyFthF1C1O9FkPskdLk+++U2/-Tmp-/tmpI6kg0Jhpi
HPI coil alignment tolerance :   25.0 mm
head shape file              : /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/parameters/R0447.hsp
raw data file                : /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/raw/R0447_NAMING_3.26.12-export.txt
sfreq                        : 1000.0 Hz
bandpass                     :    0.0 ...  200.0 Hz
stimulus channels            : 168:167:166:165:164:163:162:161
threshold                    : 1
output file                : /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/myfif/R0447_naming_raw.fif

Transformed 5 locations to the Neuromag head coordinate frame.
Transformed 5000 head shape points to the Neuromag head coordinate frame.
5 HPI coils in /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/parameters/R0447.elp
5 HPI coil positions read from /var/folders/i1/i1ypyFthF1C1O9FkPskdLk+++U2/-Tmp-/tmpI6kg0Jhpi
Procrustes matching (desired vs. transformed) :
	 -76.70   -5.09    2.41 mm <->  -83.68   -1.93    2.81 mm diff =    7.670 mm
	  66.62   -1.56   -1.77 mm <->   75.57   -1.29   -0.58 mm diff =    9.026 mm
	 -13.00  100.50   50.39 mm <->  -12.88  100.64   50.77 mm diff =    0.427 mm
	 -50.77   83.37   46.72 mm <->  -51.56   81.11   48.13 mm diff =    2.778 mm
	  30.32   91.99   51.85 mm <->   29.02   90.68   48.46 mm diff =    3.861 mm

160 MEG channels and 32 other channels read from /Users/christian/Documents/Eclipse/Eelbrain Reloaded/aux_files/sns.txt

Coordinate transformation: CTF/4D/KIT head -> head
	 0.025199 -0.999682  0.000000	  -2.44 mm
	 0.999682  0.025199  0.000000	   0.00 mm
	-0.000000 -0.000000  1.000000	  -0.00 mm
	 0.000000  0.000000  0.000000     1.00
Coordinate transformation: MEG device -> head
	 0.998025  0.060251  0.017773	  -6.59 mm
	-0.045674  0.501763  0.863799	  33.96 mm
	-0.043127  0.862905 -0.503524	 -32.62 mm
	 0.000000  0.000000  0.000000     1.00

The output file will contain a total of 158 channels including the synthetic STI 014
Writing meas info...done.
Writing raw data.................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................[done]
Closing file..[Done]
Adding directory to /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/myfif/R0447_naming_raw.fif...[done]
/Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/myfif/R0447_naming_raw.fif ready

Thank you for stopping by.


>>> ds = V.load.fiff_events(u'/Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/myfif/R0447_naming_raw.fif')
Opening raw data file /Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/myfif/R0447_naming_raw.fif...
    Range : 0 ... 624999 =      0.000 ...   624.999 secs
Ready.
Reading 0 ... 624999  =      0.000 ...   624.999 secs...  [done]
>>> print ds
eventID   i_start
-----------------
45        59587  
146       60166  
210       60749  
25        61799  
146       62399  
210       62999  
6         63799  
139       64399  
203       64999  
14        66033  
...     (use .as_table() method to see the whole dataset)
>>> ds['eventID']
var([45.00, 146.00, 210.00, 25.00, 146.00, ... n=720], name='eventID')
>>> ds['eventID'] < 60

>>> index = ds['eventID'] < 60
>>> index

>>> ds.name
u'R0447_naming_raw.fif'
>>> ds.N
720
>>> ds
<dataset u'R0447_naming_raw.fif' N=720: 'eventID'(V), 'i_start'(V)>
>>> ds.subset(index)
<dataset 'R0447_naming_raw.fif' N=237: 'eventID'(V), 'i_start'(V)>
>>> index = ds['eventID'] <= 60
>>> ds.subset(index)
Traceback (most recent call last):
  File "<input>", line 1, in <module>
  File "/Users/christian/Documents/Eclipse/EELBRAIN RELOADED/EELBRAIN/eelbrain/vessels/data.py", line 1775, in subset
    return dataset(name=name, info=info, **items)
  File "/Users/christian/Documents/Eclipse/EELBRAIN RELOADED/EELBRAIN/eelbrain/vessels/data.py", line 1426, in __init__
    self.__setitem__(name, item, overwrite=False)
  File "/Users/christian/Documents/Eclipse/EELBRAIN RELOADED/EELBRAIN/eelbrain/vessels/data.py", line 1493, in __setitem__
    self.N = len(item)
TypeError: object of type 'numpy.int32' has no len()
>>> ds.subset(index)
Traceback (most recent call last):
  File "<input>", line 1, in <module>
  File "/Users/christian/Documents/Eclipse/EELBRAIN RELOADED/EELBRAIN/eelbrain/vessels/data.py", line 1775, in subset
    return dataset(name=name, info=info, **items)
  File "/Users/christian/Documents/Eclipse/EELBRAIN RELOADED/EELBRAIN/eelbrain/vessels/data.py", line 1426, in __init__
    self.__setitem__(name, item, overwrite=False)
  File "/Users/christian/Documents/Eclipse/EELBRAIN RELOADED/EELBRAIN/eelbrain/vessels/data.py", line 1493, in __setitem__
    self.N = len(item)
TypeError: object of type 'numpy.int32' has no len()
>>> index = ds['eventID'] <= 60
>>> np.sum(index)
0
>>> index
False
>>> ds
<dataset u'R0447_naming_raw.fif' N=720: 'eventID'(V), 'i_start'(V)>
>>> ds['eventID'] <= 60
False
>>> ds['eventID'] < 60

>>> ds['eventID'] < 61

>>> index = ds['eventID'] < 61
>>> index.sum()
240
>>> ds = ds.subset(index)
>>> ds
<dataset 'R0447_naming_raw.fif' N=240: 'eventID'(V), 'i_start'(V)>
>>> ds
<dataset 'R0447_naming_raw.fif' N=240: 'eventID'(V), 'i_start'(V)>
>>> ds
<dataset 'R0447_naming_raw.fif' N=240: 'eventID'(V), 'i_start'(V)>
>>> print ds
eventID   i_start
-----------------
45        59587  
25        61799  
6         63799  
14        66033  
25        68282  
22        70716  
26        73065  
15        75382  
42        78015  
27        80215  
...     (use .as_table() method to see the whole dataset)
>>> V
<module 'eelbrain.vessels' from '/Users/christian/Documents/Eclipse/EELBRAIN RELOADED/EELBRAIN/eelbrain/vessels/__init__.pyo'>
>>> V.load.fiff_epochs(ds)

>>> print ds
eventID   i_start
-----------------
45        59587  
25        61799  
6         63799  
14        66033  
25        68282  
22        70716  
26        73065  
15        75382  
42        78015  
27        80215  
...     (use .as_table() method to see the whole dataset)
>>> ds
<dataset 'R0447_naming_raw.fif' N=240: >'MEG'<(Vnd), 'eventID'(V), 'i_start'(V)>
>>> attach(ds)
attached: ['eventID', 'MEG', 'i_start']
>>> eventID
var([45.00, 25.00, 6.00, 14.00, 25.00, ... n=240], name='eventID')
>>> detach()
>>> eventID
Traceback (most recent call last):
  File "<input>", line 1, in <module>
NameError: name 'eventID' is not defined
>>> gui.pca(ds)
/Library/Frameworks/Python.framework/Versions/7.2/lib/python2.7/site-packages/mdp/utils/covariance.py:17: MDPWarning: You have summed 1.922400e+05 entries in the covariance matrix.
As you are using dtype 'float32', you are probably getting severe round off
errors. See CovarianceMatrix docstring for more information.
  warnings.warn(wr, mdp.MDPWarning)
<eelbrain.wxgui.MEG.pca; proxy of <Swig Object of type 'wxFrame *' at 0x29c0e00> >
>>> gui.select_cases_butterfly(ds)
<eelbrain.wxgui.MEG.select_cases_butterfly; proxy of <Swig Object of type 'wxFrame *' at 0x2476f200> >
>>> print ds
eventID   i_start   reject
--------------------------
45        59587     0     
25        61799     1     
6         63799     0     
14        66033     1     
25        68282     0     
22        70716     0     
26        73065     0     
15        75382     0     
42        78015     0     
27        80215     0     
...     (use .as_table() method to see the whole dataset)
>>> print ds.as_table()>>> print ds.as_table(count=True)
    
>>> MEG
Traceback (most recent call last):
  File "<input>", line 1, in <module>
NameError: name 'MEG' is not defined
>>> plot.topo
Traceback (most recent call last):
  File "<input>", line 1, in <module>
AttributeError: 'function' object has no attribute 'topo'
>>> import eelbrain.plot as plot
>>> attach(ds)
attached: ['eventID', 'MEG', 'reject', 'i_start']
>>> plot.topo.butterfly([MEG])
<eelbrain.plot.topo.butterfly; proxy of <Swig Object of type 'wxFrame *' at 0x1a19ec00> >
>>> exec <u'/Users/christian/Documents/eelbrain/startup', lines 22 - 23>
>>> A
<module 'eelbrain.analyze' from '/Users/christian/Documents/Eclipse/EELBRAIN RELOADED/EELBRAIN/eelbrain/analyze/__init__.pyo'>
>>> a = 5
>>> exec <'Untitled:4'>
5
>>> exec <'Untitled:4'>
5
>>> a
7
>>> exec <'Untitled:4', line 1>
>>> ds
<dataset 'R0447_naming_raw.fif' N=240: >'MEG'<(Vnd), 'eventID'(V), 'i_start'(V), 'reject'(V)>
>>> f = V.data.factor(['A']*240, name='Factor')
>>> f
factor([0, 0, 0, 0, 0, ...n=240], name="Factor", random=False, labels={0: 'A'})
>>> f.x
array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=uint8)
>>> ds.add(f)
>>> print ds
Factor   eventID   i_start   reject
-----------------------------------
A        45        59587     0     
A        25        61799     1     
A        6         63799     0     
A        14        66033     1     
A        25        68282     0     
A        22        70716     0     
A        26        73065     0     
A        15        75382     0     
A        42        78015     0     
A        27        80215     0     
...    (use .as_table() method to see the whole dataset)
>>> [3, 2] * 4
[3, 2, 3, 2, 3, 2, 3, 2]
>>> Y = V.data.var([16,  7, 11,  9, 10, 11,  8,  8,
...               16, 10, 13, 10, 10, 14, 11, 12,
...               24, 29, 10, 22, 25, 28, 22, 24], 'Y')
>>> Y
var([16.00, 7.00, 11.00, 9.00, 10.00, ... n=24], name='Y')
>>> Y.x
array([16,  7, 11,  9, 10, 11,  8,  8, 16, 10, 13, 10, 10, 14, 11, 12, 24,
       29, 10, 22, 25, 28, 22, 24])
>>> AA = V.data.factor(np.array([1, 2, 3]).repeat(8), name='A')
>>> AA
factor([0, 0, 0, 0, 0, ...n=24], name="A", random=False, labels={0: '1', 1: '2', 2: '3'})
>>> A.glm.anova(Y, AA)
anova(Y, A)
>>> print A.glm.anova(Y, AA)
             SS      df    MS         F         p   
----------------------------------------------------
A           784.00    2   392.00   25.10***   < .001
Residuals   328.00   21    15.62                    
----------------------------------------------------
Total         1112   23
>>> ds
<dataset 'R0447_naming_raw.fif' N=240: 'Factor'(F), >'MEG'<(Vnd), 'eventID'(V), 'i_start'(V), 'reject'(V)>
>>> tt = A.testnd.ttest(ds, Y='MEG', X='Factor', c1='A', c2=0)
>>> plot.topo.butterfly(tt.all)
<eelbrain.plot.topo.butterfly; proxy of <Swig Object of type 'wxFrame *' at 0x1e97800> >
>>> plot.topo.array(tt.all)
<plot.topo.array ([['A', 'p']])>
>>> 

ds = V.load.fiff_events(u'/Volumes/server/MORPHLAB/Teon/experiment/meg/R0447/myfif/R0447_naming_raw.fif')
item = []
for v in ds['eventID']:
    if v < 61:
        item.append(v)
itemx = np.repeat(item, 3)
variable = V.data.factor(itemx, name='item')
ds.add(variable)
