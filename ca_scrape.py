import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd 
import sys


def scrape_ca_page(page_num):
    baseurl = 'https://www.wildlifecrossing.net'
    url = '/california/observations/latest?q=observations/latest&page={}'.format(page_num)
    source = urllib.request.urlopen(baseurl+url).read()
    soup = BeautifulSoup(source,'lxml')

    table = soup.find('table')
    table_rows = table.find_all('tr')

    data = {}
    for tr in table_rows[1:]:
        suburl = base_url+tr.find('a').get('href')
        obsID = int(suburl.split('/')[-1])
        td = tr.find_all('td')
        _, time, critter = [i.text for i in td]
        subsource = urllib.request.urlopen(suburl).read()
        subsoup = BeautifulSoup(subsource,'lxml')
        
        data[obsID] = {
            'time': pd.to_datetime(time.strip()),
            'animal': critter.strip(),
            'url': suburl
        }
        try:
            meta = subsoup.find('div', {'class': 'geolocation-location js-hide'}).find_all('meta')
            for i in meta:
                data[obsID][i['property']] = float(i['content'])
        except:
            data[obsID]['latitude'] = None
            data[obsID]['longitude'] = None
            
    df = pd.DataFrame(data).T
    df.to_json('data/CA_wildlife/{}.json'.format(str(page_num).rjust(4,'0')))

base_url = 'https://www.wildlifecrossing.net'

for page_num in range(1199, 1201):
	sys.stdout.write(", ".format(page_num))
	sys.stdout.flush()
	scrape_ca_page(page_num)
