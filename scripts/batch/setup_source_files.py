'''
Created on Oct 25, 2012

@author: teon
'''
import basic.process as process

root = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG')
log_file = os.path.join(root, 'results', 'logs', 'group_proj_log.txt')


e = process.NMG()
#e.exclude = {'subject': ['R0576', 'R0580']}
for _ in e.iter_vars(['subject']):
#    e.make_proj(overwrite = True)
    e.make_cov(overwrite=True)
#    e.make_fwd(overwrite=True)
e.print_log(log_file)