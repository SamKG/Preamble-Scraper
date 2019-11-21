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

BASE_URL_FILE_NAME = "base_urls"

if __name__ == '__main__':
    url_ct = 0
    ct = 0


    seen = set()
    url_list = []
    L = collections.deque()
    for i in range(1,589):
        L.append("https://supreme.justia.com/cases/federal/us/"+str(i))

    while (len(L) > 0):
        print(len(L))
        ctr = 0
        curr_urls = []
        while(ctr < 100 and len(L) > 0):
            curr = L.popleft()
            if not seen.__contains__(curr):
                ctr += 1
                seen.add(curr)
                curr_urls.append(curr)

        indices = [url for i,url in enumerate(curr_urls)]
        rs = [grequests.get(u,timeout=3) for u in curr_urls]
        grequests.map(rs)
        for r in rs:
            resp = r.response
            if resp is None or resp.status_code is None or resp.status_code != 200:
                print(f"REQUEUING {indices[i]}")
                L.append(indices[i])
                seen.remove(indices[i])
                continue
            resp_url = r.response.url
            stripped_resp_url = strip_url(resp_url)
            url_ct += 1
            data = r.response.text
            soup = BeautifulSoup(data, "lxml")
            for link in soup.find_all('a'):
                if link.has_attr('href'):
                    url = link.get('href')
                    url = strip_url(url)
                    if is_valid(url) and not seen.__contains__(url):
                        seen.add(url)
                        url_list += [url]
                        ct = ct+1
                        print(ct,url)

    dumpout_struct(BASE_URL_FILE_NAME,url_list)