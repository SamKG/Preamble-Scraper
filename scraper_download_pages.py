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

page_data = {}
dump_ct = 0
while (running and len(url_queue) > 0):
    print(len(url_queue))
    ctr = 0
    curr_urls = []
    while(ctr < 100 and len(url_queue) > 0):
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
        page_data[resp_url] = data
        if (len(page_data) >= 500):
            dumpout_struct(f"page_data_{dump_ct}",page_data,"page_data")
            page_data = {}
            dump_ct += 1
            print(f"DUMPOUT {dump_ct}")
dumpout_struct(f"page_data_{dump_ct}",page_data,"page_data")