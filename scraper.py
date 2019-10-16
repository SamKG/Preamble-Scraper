from bs4 import BeautifulSoup
import pickle
import re
import grequests
import signal
import collections
import sys
import csv
from os import path
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
            preamble of the constitution of the united states""".split(",")]


print("Preamble terms:",preamble)


if path.exists('seen_sites.pickled'):
    seen = open('seen_sites.pickled', 'rb')
    seen = pickle.load(seen)
else:
    seen = set()

if path.exists('urlqueue.pickled'):
    L = open('urlqueue.pickled', 'rb')
    L = pickle.load(L)
else:
    L = collections.deque()
    L.append("https://supreme.justia.com/cases/federal/us/")

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
    seen_out = open('seen_sites.pickled', 'wb+')
    L_out = open('urlqueue.pickled', 'wb+')
    pickle.dump(seen, seen_out)
    pickle.dump(L, L_out)
    sys.exit()

signal.signal(signal.SIGINT, handler)

url_ct = 0
completed = False
while (running and len(L) > 0):
    ctr = 0
    curr_urls = []
    while(ctr < 50 and len(L) > 0):
        curr = L.popleft()
        if not seen.__contains__(curr):
            ctr += 1
            seen.add(curr)
            curr_urls.append(curr)

    rs = [grequests.get(u) for u in curr_urls]
    grequests.map(rs)
    for r in rs:
        url_ct += 1
        data = r.response.text
        print(url_ct)
        matched_phrases = []
        for phrase in preamble:
            if re.search(phrase, data, re.IGNORECASE):
                print(curr, " CONTAINS PREAMBLE PHRASE ", phrase)
                matched_phrases.append(phrase)
        
        if len(matched_phrases) > 0:
            writer.writerow([f"\"{r.url}\"",f"\"{matched_phrases}\""])
        soup = BeautifulSoup(data, "lxml")
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                url = link.get('href')
                if not url.startswith('http'):
                    url = "https://supreme.justia.com" + url
                if url.startswith("https://supreme.justia.com/cases/federal/us") and not seen.__contains__(url):
                    L.append(url)
