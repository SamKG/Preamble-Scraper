from bs4 import BeautifulSoup
import pickle
import re
import grequests
import signal
import collections
import sys
import csv
from os import path
import os
from shared import *
from scraper_bounds import BASE_URL_FILE_NAME
SEEN_FILE_NAME = "seen_urls"

preamble = [x.strip() for x in """We the People of the United States, 
            in Order to form a more perfect Union, 
            establish Justice, 
            insure domestic Tranquility, 
            provide for the common defence, 
            promote the general Welfare, 
            and secure the Blessings of Liberty to ourselves and our Posterity, 
            do ordain and establish this Constitution for the United States of America,
            We the People,
            blessings of liberty,
            ourselves and our posterity,
            and their posterity,
            ordain and establish,
            preamble of the constitution of the united states,
            preamble of the constitution,
            preamble to the constitution,
            ensure domestic Tranquility,
            more perfect union""".split(",")]


print("Preamble terms:",preamble)

csv_fields = ['url','preamble_matched_terms']
if not path.exists('cases.csv'):
    csv_out = open('cases.csv', 'w+')
    writer = csv.writer(csv_out)
    writer.writerow(csv_fields)

csv_out = open('cases.csv','a')
writer = csv.writer(csv_out)

running = True

url_ct = 0
completed = False
files = [i for i in os.listdir("page_data")]
for file in files:
    page_data = readin_struct(file,folder="page_data")[0]
    print(file,len(page_data))
    for url,data in page_data.items():
        stripped_url = strip_url(url)
        matched_phrases = []
        if (is_valid(url)):
            for phrase in preamble:
                if re.search(phrase, data, re.IGNORECASE):
                    matched_phrases.append(phrase)
        
        if len(matched_phrases) > 0:
            writer.writerow([f"\"{stripped_url}\"",f"\"{matched_phrases}\""])
    csv_out.flush()
