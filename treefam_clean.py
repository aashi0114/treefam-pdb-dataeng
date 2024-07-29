import os
from tqdm import tqdm
from Bio import SeqIO
from Bio import Phylo
from Bio.Phylo import PhyloXML



aa = ['A', 'R', 'N', 'D', 'C', 'Q', 
        'E', 'G', 'H', 'I', 'L', 'K',
        'M', 'F', 'P', 'S', 'T', 'W', 
        'Y', 'V', '-']



def RemoveInvalids(recordslist):
    new_seqs = []
    bad_sequences = []
    for record in recordslist:
        badSeqBool = False
        for i in record.seq:
            if i not in aa:
                bad_sequences.append(record.id)
                badSeqBool = True
                break
        if badSeqBool != True:
            new_seqs.append(record)
                
    return new_seqs, bad_sequences





def RemoveClades(trees_input, bad_sequences):
    new_trees = []

    for tree in trees_input:        
        for clade in tree.find_clades():
            if clade.name in bad_sequences: # cleave tree clade ids that match with a bad sequences
                tree.prune(clade)
        new_trees.append(tree) 

    return new_trees
    


dir = "" # directory w/ data
newDir = "" # directory to save cleaned data


for filename in tqdm(os.listdir(dir)):
    header = ""
    f = os.path.join(dir, filename)
    for i in filename:
        if i != ".":
            header = header + i
        else:
            break
    
    if (header in f) and ("aa.fasta" in f) :
        records = list(SeqIO.parse(f, "fasta"))
        fasta = RemoveInvalids(records)[0]
        bad_seq = RemoveInvalids(records)[1]
        newFile = newDir + header + ".aa.cleaned.fasta"
        SeqIO.write(fasta, newFile, "fasta")
    

        for filename in os.listdir(dir):
            f = os.path.join(dir, filename)
            if (header in f) and (".xml" in f):
                trees = list(Phylo.parse(f, "phyloxml"))
                phylotree = RemoveClades(trees, bad_seq)
                cleaned = newDir + header + ".cleaned.xml"
                cleanedNewick = newDir + header + ".cleaned.txt"
                Phylo.write(phylotree, cleaned, "phyloxml")
                Phylo.convert(cleaned, "phyloxml", cleanedNewick, "newick")
                os.remove(cleaned)

names = newDir + "names.txt"
with open(names, 'w') as f:
    for name in seqNames:
        f.write(f"{name}\n")
    




