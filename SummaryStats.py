"""SummaryStats.ipynb

Automatically generated by Colab.

Author: Vignesh Rajagopalan (High School Intern)

"""

#Import libraries
import numpy as np
import pandas as pd
from google.colab import drive

#Since I used google colab for this code, the next eight lines have to be changed
drive.mount('/content/drive/',force_remount=True)
!cp drive/My\ Drive/Colab\ Notebooks/'names.txt' .
!cp drive/My\ Drive/Colab\ Notebooks/'TF101001.aa.cleaned.fasta' .
!cp drive/My\ Drive/Colab\ Notebooks/'TF101002.aa.cleaned.fasta' .
!cp drive/My\ Drive/Colab\ Notebooks/'TF101003.aa.cleaned.fasta' .
!cp drive/My\ Drive/Colab\ Notebooks/'TF101004.aa.cleaned.fasta' .
!cp drive/My\ Drive/Colab\ Notebooks/'TF101005.aa.cleaned.fasta' .
!cp drive/My\ Drive/Colab\ Notebooks/'TF101001.phyloxml.xml' .
!cp drive/My\ Drive/Colab\ Notebooks/'PDBToUnicode.txt' .
!cp drive/My\ Drive/Colab\ Notebooks/'TreeFamToPDB.txt' .
!cp drive/My\ Drive/Colab\ Notebooks/'TF300415.fa' .
!cp drive/My\ Drive/Colab\ Notebooks/'TF315028.fa' .

#Imports AlignIO from the Bio package to open the multiple sequence allignment file
!pip install Bio
from Bio import AlignIO
from Bio import SeqIO

#Opens the file names.txt in read mode
input = open('names.txt',mode = 'r')
#Opens the file, SUMMARY.txt, in write mode
outDataFile = open('SUMMARY.txt',mode = 'w')
outDataFile.write('SUMMARY STATISTICS')

#Returns the number of proteins in the data
def numProtein(data):
  return len(data)

#Returns the mean, median, standard deviation, max and min of the columns and rows as a tuple
def AlignmentStats(data):
  #Replaces '-' with Nan and removes the last column
  data.replace('-', np.nan, inplace=True)

  #Replace NaNs with 0s and other values with 1s
  binarydata = data.notna().astype(int)

  #Calculate the sum of each row and column
  row_sums = binarydata.sum(axis=1)
  column_sums = binarydata.sum(axis=0)

  var1 = stats(row_sums)
  var2 = stats(column_sums)
  return var1,var2

#Returns the mean, median, standard deviation, max and min of a dataset
def stats(dataset):
  numVal = np.array(dataset)
  meanVal = np.mean(numVal)
  medianVal = np.median(numVal)
  stdVal = np.std(numVal)
  maxVal = np.max(numVal)
  minVal = np.min(numVal)
  return meanVal,medianVal,stdVal,maxVal,minVal

#Prints the mean, median, standard deviation, max and min of a dataset
def printStats(var):
  outDataFile.write('     - Mean : ' + str(var[0])+'\n')
  outDataFile.write('     - Median : ' + str(var[1])+'\n')
  outDataFile.write('     - Standard Deviation : ' + str(var[2])+'\n')
  outDataFile.write('     - Max : ' + str(var[3])+'\n')
  outDataFile.write('     - Min : ' + str(var[4])+'\n')

from scipy.stats import entropy
#Finds the column Entropy from the dataFrame and finds the mean, median, standard deviation, max, min
def perColEntropy(data):
  valueCount = pd.DataFrame(data.apply(pd.Series.value_counts))
  valueCount.replace(np.nan,0,inplace=True)
  sums = valueCount.sum(axis=0)
  valueCount = valueCount.loc[:, sums != 0]
  num = entropy(valueCount,base=20)
  var = stats(num)
  outDataFile.write(' - Entropy Data\n')
  printStats(var)


numFamily = 0 #Keeps count of the number of families
#proteinRecord = [record.id for record in SeqIO.parse('TF101001.aa.fasta', "fasta")] #The protein names
#print(proteinRecord)
proteinval = [] #The number of proteins for each of the families
MSAval = [] #The MSA widths for each of the families
while True:
  #Reading each of the names of the files
  line = input.readline()
  if not line:
    break
  line = line.strip()
  outDataFile.write('\nFor family '+str(line))
  line = line + '.aa.cleaned.fasta'
  sequences = list(SeqIO.parse(line, "fasta")) #Gets the sequences for each of the protein families
  data = pd.DataFrame(sequences)
  val = AlignmentStats(data)
  proteinval.append(numProtein(data)) #Appends the number of proteins in the family to proteinval
  MSAval.append(val[0][3]) #Appends the MSA maximum width per family to proteinval
  numFamily = numFamily+1
  outDataFile.write('\n - Number of proteins: '+str(numProtein(data)))

  #Alignment statistics for the data in each family
  value = AlignmentStats(data)

  outDataFile.write('\n - Maximum width of MSA: '+ str(value[0][3]))
  outDataFile.write('\n - Alignment sizes \n')
  outDataFile.write('   - Rows\n')
  printStats(value[0])
  outDataFile.write('   - Columns\n')
  printStats(value[1])

  perColEntropy(data) #Gives entropy data for each family

#Returns the version of the tree used
def versionInfo(file_path):
  versionArr = None
  with open(file_path, 'r') as file:
    lines = file.readlines()
    for line in lines:
      if line.startswith('#') or line.startswith(';') or line.startswith('<'):
        if 'version' in line.lower():
          versionArr = line.strip()
  return versionArr.split('version="')[1].split('"')[0]

input.close()
#Prints the necessary details to the file
outDataFile.write('\n')
valuesInfo = versionInfo('TF101001.phyloxml.xml')
outDataFile.write('Version: '+str(valuesInfo))
outDataFile.write('\n\n')
outDataFile.write('Number of families: '+str(numFamily))
outDataFile.write('\n')
outDataFile.write(' - Protein Data per Family\n')
var = stats(proteinval)
printStats(var)
outDataFile.write(' - MSA Data per Family\n')
var = stats(MSAval)
printStats(var)
outDataFile.close()
!cp 'SUMMARY.txt' drive/My\ Drive/Colab\ Notebooks/

#NAME MAPPINGS

#ALGORITHM USED IN NAME MAPPINGS
#1) Getting the PDB names
#  a) Using a command given from Biopython, the names of all the proteins were saved into a list.
#  b) Using that list and the UniProt link for generating name mappings, the name mappings
#     from PDB to UniProt KB were generated and saved into a file
#  c) The UniProt proteins were then mapped to PDB proteins in a dataframe so that there is one PDB per
#     UniProt protein
#2) Getting the TreeFam names
#  a) There is a file on TreeFam that contains all the TreeFam families that are mapped
#     with UniProt. This is the link: http://www.treefam.org/static/download/uniprotACC2treefam.txt
#  b) The code directly reads the file from the internet using requests and is saved into a dataframe
#  c) Using those 600k+ names, the number of names was shortened by only keeping the name mappings where
#     the UniProt KB protein names in this dataframe were all present in the UniProt and PDB name mappings.
#  d) The proteins in the family were obtained through requests from this url: 'http://www.treefam.org/family/{familyName}/alignment'
#     which has all the individual proteins in fasta file.
#  e) Using SeqIO, the names of the TreeFam proteins were mapped to the UniProt proteins.
#3) Getting the name mappings
#  a) The two dataframes were merged.

#IMPORTANT NOTE: This whole algorithm will take a very long time to run especially at step 2d. Testing was done with the first
#few, and they work.


import requests
from io import StringIO
url = 'https://www.treefam.org/static/download/uniprotACC2treefam.txt'
response = requests.get(url, verify=False)
response.raise_for_status()
fileContent = StringIO(response.text)
data = pd.read_csv(fileContent, delimiter='\t', header=0)
fileNamesVal = pd.DataFrame({'UniProt': data['external_db_id'],'TreeFamFamily': data['gene_tree_stable_id']})
#print(fileNamesVal)


dataVals = pd.read_csv('PDBToUnicode.txt', delim_whitespace=True, header=0)
pdbPfam = dict(zip(dataVals['To'], dataVals['From']))
pdbUni = pd.DataFrame([(uni, pdb) for uni, pdbs in pdbPfam.items() for pdb in pdbs], columns=['UniProt', 'PDB'])
pdbUni = pdbUni.groupby('UniProt')['PDB'].apply(lambda x: ' '.join(x)).reset_index()


common_uniprot = set(fileNamesVal['UniProt']).intersection(pdbUni['UniProt'])
filtered_df = fileNamesVal[fileNamesVal['UniProt'].isin(common_uniprot)]
resultData = filtered_df[['UniProt', 'TreeFamFamily']].reset_index(drop=True)
resultData = resultData.head(3) #Used for testing purposes
#print(resultData)

def fetchProteinSequences(familyName):
  url = f'http://www.treefam.org/family/{familyName}/alignment'
  try:
    response = requests.get(url)
    response.raise_for_status()
    sequences = SeqIO.parse(StringIO(response.text), 'fasta')
    return [(seq.id, str(seq.seq)) for seq in sequences]
  except Exception as e:
    print(f"Error fetching data for {familyName}: {e}")
    return []


def mapSequences(row):
  sequences = fetchProteinSequences(row['TreeFamFamily'])
  return [(row['UniProt'], seq_id, seq) for seq_id, seq in sequences]

sequencesData = resultData.apply(mapSequences, axis=1)
flattenedSequences = [item for sublist in sequencesData for item in sublist]
sequencesName = pd.DataFrame(flattenedSequences, columns=['UniProt', 'SequenceID', 'ProteinSequence'])
sequencesName = sequencesName.drop(columns=['ProteinSequence'])
#print(sequencesName)

dataNameVal = pd.read_csv('TreeFamToPDB.txt', delim_whitespace=True, header=0)
fileNames = dataNameVal['To'] + '.fa'

def extractProteinNames(file_name):
  return [record.id for record in SeqIO.parse(file_name, "fasta")]


proteinNames = pd.Series(fileNames).apply(extractProteinNames)
proteinNamesDictionary = dict(zip(fileNames, proteinNames))
newKeys = dataNameVal['From']
proteinNamesDictionary = dict(zip(newKeys, proteinNames))
flattenedData = [(key, name) for key, names in proteinNamesDictionary.items() for name in names]
proteinNames = pd.DataFrame(flattenedData, columns=['UniProt', 'TreeFam'])


def removeSpace(s):
  return ''.join(s.split())
pdbUni['PDB'] = pdbUni['PDB'].apply(removeSpace)
#print(pdbUni)

dataVals = pd.read_csv('PDBToUnicode.txt', delim_whitespace=True, header=0)
pdbProt = dict(zip(dataVals['To'], dataVals['From']))
treeUni = sequencesName
pdbUni = pd.DataFrame([(pfam, pdb) for pfam, pdbs in pdbProt.items() for pdb in pdbs], columns=['UniProt', 'PDB'])
pdbUni = pdbUni.groupby('UniProt')['PDB'].apply(lambda x: ' '.join(x)).reset_index()


pdbUni['PDB'] = pdbUni['PDB'].apply(removeSpace)
mergedData = pd.merge(treeUni, pdbUni, on='UniProt')
mergedData = mergedData.drop(columns=['UniProt'])
#print(mergedData)
mergedData.to_csv('nameMappings.csv', index=False)
!cp 'nameMappings.csv' drive/My\ Drive/Colab\ Notebooks/