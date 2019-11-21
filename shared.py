import re
import pickle
from os import path

def is_valid(url):
    validity_check = r"/year"
    if len(re.findall(validity_check,url))>0:
        return False
    return url.startswith("https://supreme.justia.com/cases/federal/us")

def strip_url(url):
    if not url.startswith('http'):
        url = "https://supreme.justia.com" + url
    endings = [r"/\w*.html",r"/\w*.pdf"]
    for end in endings:
        url = re.split(end,url)[0]
    if url[-1] == '/':
        url = url[:-1]
    return url

PICKLE_EXTENSION = ".pickle"
def dumpout_struct(name,struct,folder="data"):
    output_file = open(f'{folder}/{name}{PICKLE_EXTENSION}', 'wb+')
    pickle.dump(struct,output_file)

def readin_struct(name,default=None,folder="data"):
    if not path.exists(f'{folder}/{name}{PICKLE_EXTENSION}'):
        if default is None:
            raise Exception(f"File {name} does not exist, and no default provided!")
        return default,False
    struct_file = open(f'{folder}/{name}{PICKLE_EXTENSION}','rb')
    return pickle.load(struct_file),True
    