'''
Created on Sept 4, 2012

@author: teon
'''

import os
from surfer import Brain

rois = os.path.join(os.path.expanduser('~'), 'Dropbox', 
                    'Experiments', 'NMG', 'results', 'rois')
subject_id = "00"
hemi = "lh"
surf = "white"
brain = Brain(subject_id, hemi, surf)

# Plot rois

brain.add_label("fusiform", color = 'orchid')
brain.add_label("LATL", color = 'steelblue')
brain.add_label("vmPFC", color = 'coral')
brain.add_label("LPTL", color = 'crimson')
brain.add_label("inferiortemporal", color = 'salmon')


#Export images
brain.show_view('lateral')
brain.save_image(os.path.join(rois, "ROIs_lateral.pdf" ))

brain.show_view('medial')
brain.save_image(os.path.join(rois, "ROIs_medial.pdf" ))

brain.show_view('ventral')
brain.save_image(os.path.join(rois, "ROIs_ventral.pdf" ))