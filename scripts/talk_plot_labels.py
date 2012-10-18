"""
Display ROI Labels
==================

Using PySurfer you can plot Freesurfer cortical labels on the surface
with a large amount of control over the visual representation.

"""
print __doc__

import os
from surfer import Brain

rois = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'talk', 'rois')
subject_id = "R0095"
hemi = "lh"
surf = "smoothwm"
brain = Brain(subject_id, hemi, surf)

#Plot rois
# If the label lives in the normal place in the subjects directory,
# you can plot it by just using the name
brain.add_label("fusiform", color = 'orchid')
brain.show_view('medial')
brain.save_imageset(os.path.join(rois, "fusiform"), ['medial', 'ventral'], 'png')


brain = Brain(subject_id, hemi, surf)
brain.add_label("parstriangularis", color = 'coral')
brain.show_view('lateral')
brain.save_image(os.path.join(rois, "pars_triangulars.png" ))

brain = Brain(subject_id, hemi, surf)
brain.add_label("medialorbitofrontal", color = 'salmon')
brain.show_view('medial')
brain.save_image(os.path.join(rois, "medial_orbitofrontal.png" ))

#Export images
brain = Brain(subject_id, hemi, surf)
brain.add_label("parstriangularis", color = 'coral')
brain.add_label("medialorbitofrontal", color = 'salmon')

brain.show_view('lateral')
brain.save_image(os.path.join(rois, "rois_lateral.png" ))

brain.show_view('medial')
brain.save_image(os.path.join(rois, "rois_medial.png" ))