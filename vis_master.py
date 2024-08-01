import shutil
import os

#Preparing the pml_script.py file for execution in PyMOL

def prepareDefaults(ref_structure, file_destination, key_aln, key_cnt, key_var, color='red'):
    #Set destination for the pml_script.py
    oFile = os.path.join(file_destination, 'pml_script.py')
    
    if os.path.isfile(oFile):
        raise ValueError ('There an existing PyMOL script at the target location')
    
    #Copy pml_script.py template within repository
    shutil.copyfile(__file__.replace('vis_master.py', 'pml_script.py'), oFile)
    
    #Edit visual information within executable
    with open (oFile, 'r') as f:
        lines = f.read().split('\n')
        line_1 = 'name = {}'.format("'" + ref_structure + "'")
        line_2 = 'alnAreas = {}'.format(key_aln)
        line_3 = 'cntAreas = {}'.format(key_cnt)
        line_4 = 'varAreas = {}'.format(key_var)
        line_5 = 'color = {}'.format("'" + color + "'")
        
        new_file = '\n'.join([line_1] + [line_2] + [line_3] + [line_4] + [line_5] + lines[5:])
    
    with open(oFile, 'w') as f:
        f.write(new_file)
        
#Example Usage:       
#prepareDefaults('1jnx', '/Users/krishna/Projects', ["1667-1741", "1771-1800"], ["1667-1741", "1771-1800"], ["1667-1741", "1771-1800"])