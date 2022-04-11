import json
import unidecode
def writeJsonFile(data:dict,fileName:str, mode:str = 'w'):
    with open(fileName,mode) as file:
        file.write(json.dumps(data,indent=4))

def try_or(fnc,default = None):
    try:
        return fnc
    except:
        return default

def normalizeString(string:str):
    return unidecode.unidecode(string)
    
if __name__=='__main__':
    print(normalizeString('2 habitaci\u00f3n/es (Individual) disponible/s'))