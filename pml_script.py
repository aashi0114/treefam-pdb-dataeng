name = ''
alnAreas = []
cntAreas = []
varAreas = []
color = ''

#! THIS IS A SELF-CONTAINED, PORTABLE, AND SELF-DEPENDENT SCRIPT: DO NOT CHANGE LINES BEFORE THIS POINT

# Don't worry about 'module not found' in code editor
# The code will be run within the PyMOL toolkit
from pymol import cmd 

#*
#* PyMOL Constructor =============================================================================================
#*


cmd.fetch(name)
cmd.orient()

cmd.hide('all')
cmd.show('cartoon')

cmd.set('cartoon_color', color)
cmd.set('cartoon_fancy_helices')
cmd.set('cartoon_highlight_color', 'grey75')

cmd.bg_color('black')

#Construct commands to highlight important segments using PyMOL selections

alnCommand = ""
for i, seg in enumerate(alnAreas):
    alnCommand += ("resi " + seg + " ")
    if i != (len(alnAreas) -1):
        alnCommand += ("or ")
        
cntCommand = ""
for i, seg in enumerate(cntAreas):
    cntCommand += ("resi " + seg + " ")
    if i != (len(cntAreas) -1):
        cntCommand += ("or ")

varCommand = ""
for i, seg in enumerate(varAreas):
    varCommand += ("resi " + seg + " ")
    if i != (len(varAreas) -1):
        varCommand += ("or ")

cmd.select("key_alignment_locations", alnCommand)
cmd.select("key_contact_locations", cntCommand)
cmd.select("key_variation_locations", varCommand)

cmd.set('ray_trace_mode', '1')
cmd.ray()
