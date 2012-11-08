import osfrom surfer import Brain

rois = os.path.join(os.path.expanduser('~'), 'Dropbox', 'Experiments', 'NMG', 'talk', 'rois')subject_id = "R0095"hemi = "lh"surf = "smoothwm"brain = Brain(subject_id, hemi, surf)

brain.add_label("LATL", color = 'orchid')
