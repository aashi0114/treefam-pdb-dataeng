import numpy as np
import pandas as pd
import json
from json import JSONEncoder

#Convrt numpy to csv with Pandas dataframes
def numpy2csv(array, name):
    DF = pd.DataFrame(array)
    DF.to_csv(name)

#Convert csv to numpy with delimiters
def csv2numpy(csv):
    raw = np.genfromtxt(csv, delimiter=',')
    return (raw[1:raw.shape[0], 1:raw.shape[1]])

# Extend the json module's JSONEncoder encoding scope by overriding default()
class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

# Dump JSON from Numpy using custom encoders
def numpy2json(npArray, jFile):
    data = {'array': npArray}
    with open(jFile, "w") as write_file:
        json.dump(data, write_file, cls=NumpyArrayEncoder)

#Read and decode JSON files
def json2numpy(jFile):
    with open(jFile, "r") as read_file:
        decoded = json.load(read_file)
        return(np.asarray(decoded['array']))

#Cleaning for outputs of 'Key Segment' functions, preppingg for visualization
def cleanUp(keySegs_array, minL):
    newArray = []
    for segment in keySegs_array:
        if len(segment) != 0 and len(segment) > minL:
            newArray.append(str(segment[0] + 1) + '-' + str(segment[-1] + 1))
    return newArray
    