#Krishna Bhatt @ Holmes Lab (UC Berkeley) 2024
#Integrated Pipeline Product

#! INCOMPLETE TESTING
# Code may not work as expected as full pipeline testing has not been completed

#*
#* Imports =======================================================================================================
#*

import os
import numpy as np

from Bio import AlignIO, Align
from Bio.PDB import PDBParser, Superimposer
from Bio.SeqUtils import seq1 as three2one

from utils import numpy2json, json2numpy
from utils import cleanUp

#*
#* Data Loading ==================================================================================================
#*

# Loading TreeFam multiple sequence alignments
def load_treefam_alignment(alignment_file):
    return AlignIO.read(alignment_file, "fasta")

# Loading PDB family (headers, structures, residue sequences)
def load_pdb_family(fam_directory):
    parser = PDBParser()
    pdb_family = []
    
    #Looping through the protein family directory and isolating protein structures and sequences
    for filename in os.listdir(fam_directory):
        pdb_file = os.path.join(fam_directory, filename)
        structure = parser.get_structure("protein", pdb_file)
        
        #CA atoms as residue indicators
        ca_atoms = [atom for atom in structure.get_atoms() if atom.name == "CA"] 
        res_sequence = "".join([three2one(atom.get_parent().get_resname()) for atom in ca_atoms])
        
        pdb_family.append((parser.get_header("protein", pdb_file), structure, res_sequence))

    return pdb_family

# Load distance matrices from JSON files
def load_distances(dist_directory):
    dist_family = []
    
    for filename in os.listdir(dist_directory):
        dist_file = os.path.join(dist_directory, filename)
        distance_matrix = json2numpy(dist_file)
        dist_family.append(distance_matrix)
    
    return dist_family

#*
#* Emergent Data =================================================================================================
#*

# Convert distance matrices to contact matrices
def dist2contacts (dist_matrix, dist_thresh=8):
    contacts = np.zeros(dist_matrix.shape)
    
    #Loop through and develop contacts based on threshold (default 8 Angstrom)
    for i in range(0, dist_matrix.shape[0]):
        for j in range(0, dist_matrix.shape[1]):
            if dist_matrix[i][j] < dist_thresh:
                contacts[i][j] = contacts[j][i] = 1
    
    return contacts

# Superimpose protein structures on reference (Similar to Residue Alignments)
def imposeStructure(pdb_structures, ref_index):
    ref_structure = pdb_structures[ref_index] #Reference structure to align to
    aligner = Superimposer()
    
    for structure in pdb_structures[1:]:
        ref_atoms = [atom for atom in ref_structure.get_atoms() if atom.name == 'CA']
        atoms = [atom for atom in structure.get_atoms() if atom.name == 'CA']
        
        aligner.set_atoms(ref_atoms, atoms)
        aligner.apply(structure.get_atoms())
    
    return pdb_structures

# Calculate variance per residue in PDB structures
def calcVariance(imposed_structures):
    #Find the shortest protein sequence to eliminate inhomegenous variance matrices
    min_ca_atoms = min(sum(1 for atom in structure.get_atoms() if atom.name == 'CA') 
                       for structure in imposed_structures)

    #Find all coordinates of residues in proteins
    all_coords = []
    for structure in imposed_structures:
        coords = [atom.coord for atom in structure.get_atoms() if atom.name == 'CA'][:min_ca_atoms]
        all_coords.append(coords)

    #Calculating variance and convert 3D array (seqs, res, coord) into 2D (res, coords)
    all_coords = np.array(all_coords)
    variance = np.var(all_coords, axis=0)
    
    #Convert to 1D matrix of variance in each residue
    return np.mean(variance, axis=1), all_coords


#*
#* Distance Matrices to Alignment Mapping ========================================================================
#*
       
# Create a dictionary mapping from each PDB residue to corresponding TreeFam columns
def pdb2tree_mapping(pdb_seq, tree_seq, match_threshold=1.5):
    
    #Align TreeFam Protein Sequence to PDB-derived protein sequence to confirm a match
    aligner = Align.PairwiseAligner()
    aligner.mode = 'local'
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -10
    aligner.extend_gap_score = -0.5
    
    pdbtree_aln = aligner.align(pdb_seq, str(tree_seq.seq))[0]
    score = pdbtree_aln.score / len(pdb_seq)
    
    if score > match_threshold:
        pdb2tree = {}
        aligned_pdb, aligned_treefam = pdbtree_aln.aligned
        tree_start = aligned_treefam[0][0]
        
        #Mapping each PDB sequence residue to a residue in the provided treefam sequence
        for (pdb_slice, tree_slice) in zip(aligned_pdb, aligned_treefam):
            for i, j in zip(range(pdb_slice[0], pdb_slice[1]), range(tree_slice[0], tree_slice[1])):
                pdb2tree[i] = j - tree_start
        
        return pdb2tree, score
    else:
        raise ValueError("PDB Structure Sequence does not sufficiently match the TreeFam MSA Sequence")

# Mapping distance matrix to treeFam alignment shape
def dist2tree_mapping(dist_matrix, pdb2tree_map, treeSeq_length):
    tree_contacts = np.full((treeSeq_length, treeSeq_length), -1)
    
    #Utilize Alignment Shape to Construct Distance Matrix
    for i in range(dist_matrix.shape[0]):
        for j in range(dist_matrix.shape[1]):
            if i in pdb2tree_map and j in pdb2tree_map:
                aln_i = pdb2tree_map[i]
                aln_j = pdb2tree_map[j]
                tree_contacts[aln_i, aln_j] = dist_matrix[i, j]
                
    return tree_contacts

#*
#* Key Segment Determination =====================================================================================
#*

# Determine key segments with similar residue sequences w/ diminishing scores (Thresholds might need some fiddling)
def keyAlnAreas(alignment, numMatches_thresh=0.9, strictness=2, minL=5):
    score = 0
    keySegs = [[]]
    
    #Looping through the length of the aliggnment, and adding scores to resmatches based on similarity
    for i in range(len(alignment[0].seq)):
        resMatches = {}
        passed = False
        
        for j in range(len(alignment)):
            if (alignment[j].seq)[i] in resMatches:
                resMatches[(alignment[j].seq)[i]] += 1
            else:
                resMatches[(alignment[j].seq)[i]] = 1
        
        #Reseting score if no. of the most similar residue surpases numMatches_thresh
        for res in resMatches:
            if resMatches[res] > numMatches_thresh * len(alignment):
                score = strictness
                passed = True
            
        #Diminish Score if no match    
        if not passed: score -= 1
        
        #Add to key locations if the score is above 0        
        if score > 0:
            keySegs[-1].append(i)
        elif len(keySegs[-1]) != 0:
            keySegs.append([])
    
    return cleanUp(keySegs, minL)

# Determine key segments with high contact density w/ diminishing scores (Thresholds might need some fiddling)
# Inputs: seqDist_thresh (How far a residue has to be from each residue to be counted a contact), numContact_thresh (How many contacts a residue must have to be considered key)
def keyContactAreas (contact_matrices, seqDist_thresh=5, numContact_thresh=20, strictness=2, minL=5):
    score = 0
    contactSegs = [[]]
    
    for i in range(contact_matrices.shape[1]):
        resContacts = 0
        
        # Loop through contact matrices and columns to find residues with high number of contacts which are a sertain distance away from itself in the sequence
        for g in range(contact_matrices.shape[0]):
            for j in range(contact_matrices.shape[2]):
                if contact_matrices[g][i][j] == 1 and abs(i - j) > seqDist_thresh:
                    resContacts += 1
        
        #Reseting score if no. of contacts on residue surpases numContact_thresh
        if (resContacts > numContact_thresh):
            score = strictness
        
        #Diminish Score
        else: score -= 1
        
        #Add to key locations if the score is above 0        
        if score > 0:
            contactSegs[-1].append(i)
        elif len(contactSegs[-1]) != 0:
            contactSegs.append([])
    
    return cleanUp(contactSegs, minL)

# Determine key segments of low structural variance w/ diminishing scores (Thresholds might need some fiddling)
def keyVarAreas(variance, var_thresh=0.5, strictness=2, minL=5):
    score = 0
    keySegs = [[]]
    
    #Loop through all variance per residue and reseting if below a threshold
    for i, var in enumerate(variance):
        if var < var_thresh:
            score = strictness
        
        #Diminishing Score
        else: score -= 1
        
        #Add to key locations if the score is above 0
        if score > 0:
            keySegs[-1].append(i)
        elif len(keySegs[-1]) != 0:
            keySegs.append([])
    
    return cleanUp(keySegs, minL)

