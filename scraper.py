from bs4 import BeautifulSoup
import pickle
import re
import grequests
import signal
import collections
import sys
import csv
from os import path
from shared import *
from scraper_bounds import BASE_URL_FILE_NAME
SEEN_FILE_NAME = "seen_urls"
QUEUE_FILE_NAME= "url_queue"

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
def handler(signum, frame):
    running = False
    dumpout_struct(SEEN_FILE_NAME,seen)
    dumpout_struct(QUEUE_FILE_NAME,url_queue)
    sys.exit()

signal.signal(signal.SIGINT, handler)

seen,reading_seen = readin_struct(SEEN_FILE_NAME,set())
url_queue,readin_queue = readin_struct(QUEUE_FILE_NAME,collections.deque())
if not readin_queue:
    base_urls,readin_base = readin_struct(BASE_URL_FILE_NAME)
    for url in base_urls:
        url_queue.append(url)

url_ct = 0
completed = False
while (running and len(url_queue) > 0):
    print(len(url_queue))
    ctr = 0
    curr_urls = []
    while(ctr < 1000 and len(url_queue) > 0):
        curr = url_queue.popleft()
        if not seen.__contains__(curr):
            ctr += 1
            seen.add(curr)
            curr_urls.append(curr)

    indices = [url for i,url in enumerate(curr_urls)]
    rs = [grequests.get(u,timeout=3) for u in curr_urls]
    grequests.map(rs)
    for i,r in enumerate(rs):
        resp = r.response
        if resp is None or resp.status_code is None or resp.status_code != 200:
            print(f"REQUEUING {indices[i]}")
            url_queue.append(indices[i])
            seen.remove(indices[i])
            continue
        resp_url = r.response.url
        stripped_resp_url = strip_url(resp_url)
        url_ct += 1
        data = r.response.text
        matched_phrases = []
        if (is_valid(resp_url)):
            for phrase in preamble:
                if re.search(phrase, data, re.IGNORECASE):
                    matched_phrases.append(phrase)
        
        if len(matched_phrases) > 0:
            writer.writerow([f"\"{stripped_resp_url}\"",f"\"{matched_phrases}\""])
    csv_out.flush()
