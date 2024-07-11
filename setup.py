import os

# creating the treefam-pdb
if not os.path.isdir('treefam-pdb'):
    os.mkdir("treefam-pdb")

if not os.path.isdir('treefam-pdb/treefam-alignments-and-trees'):
    os.mkdir("treefam-pdb/treefam-alignments-and-trees")

if not os.path.isdir('treefam-pdb/pdb-structure-files'):
    os.mkdir("treefam-pdb/pdb-structure-files")

if not os.path.isdir('treefam-pdb/contact-matrices'):
    os.mkdir("treefam-pdb/contact-matrices")

if not os.path.isdir('treefam-pdb/treefam-pdb-mappings'):
    os.mkdir("treefam-pdb/treefam-pdb-mappings")

open("treefam-pdb/summary.txt", "w+")