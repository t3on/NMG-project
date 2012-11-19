"""
Display ROI Labels
==================

Using PySurfer you can plot Freesurfer cortical labels on the surface
with a large amount of control over the visual representation.

"""
print __doc__

import os
from surfer import Brain

rois = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'results', 'rois')
subject_id = "R0095"
hemi = "lh"
surf = "smoothwm"
brain = Brain(subject_id, hemi, surf)

#Plot rois
# If the label lives in the normal place in the subjects directory,
# you can plot it by just using the name
brain.add_label("fusiform", color = 'orchid')
brain.add_label("temporalpole", color = 'steelblue')
brain.add_label("parstriangularis", color = 'coral')
brain.add_label("superiortemporal", color = 'crimson')
#brain.add_label("lateralorbitofrontal", color = 'olivedrab')
brain.add_label("medialorbitofrontal", color = 'salmon')


#Export images
brain.show_view('lateral')
brain.save_image(os.path.join(rois, "%s_lateral.png" % subject_id))

brain.show_view('medial')
brain.save_image(os.path.join(rois, "%s_medial.png" % subject_id))