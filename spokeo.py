import os
import random
from time import sleep
import datetime
from bs4 import BeautifulSoup
import lxml
from torrequest import TorRequest
import requests
from lxml.html import fromstring

tor = TorRequest(password='satc2020')
header = {}
agents = []
piis = []


def read_data():
    global piis
    global agents

    print('----Beg to read----')
    with open('/home/spider/pii/spokeo/config/useragents', 'r') as f:
        uas = f.readlines()
    f.close()
    agents = [i.strip('\n') for i in uas]
    with open('/home/spider/pii/spokeo/config/spokeo_new_tormarket.csv', 'r') as f1:
        records = f1.readlines()
    f1.close()
    piis = [i.strip('\n') for i in records]
    len_pii = len(piis)
    piis = piis[:int(len_pii / 5)]
    print('----Read End----')


def tor_reset():
    global tor
    global header
    try:
        tor = TorRequest(password='satc2020')
        tor.reset_identity()
    except:
        tor.close()
        tor_1 = TorRequest(password='satc2020')
        tor = tor_1
        tor.reset_identity()
    response = tor.get('http://ipecho.net/plain')
    print("Ip Address has changed: ", response.text)


def get_mylife(url, name, city):
    if city == '':
        city = 'None'
    with open('/home/spider/pii/spokeo/config/saved_url', 'a') as f:
        f.write(name + ',' + city + ',' + str(url) + '\n')
    f.close()
    print('-----saved------')


def get_url(query, name, city):
    query = query.replace(' ', '%20')
    bing_url = 'https://www.bing.com/search?q=' + str(query) + '%20mylife' + '&qs=n&form=QBRE'
    print(bing_url)
    headers = {'User-Agent': '{}'.format(random.choice(agents)),
               'Cookie': '{:}'.format(
                   'SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=F8342D0A58BF4A8C97438C0D80DBCDC4&dmnchg=1; SRCHUSR=DOB=20200525&T=1591900091000; _EDGE_V=1; MUID=22E30E44290F65C10FD40091282164ED; SRCHHPGUSR=CW=1536&CH=156&DPR=1.25&UTC=-420&WTS=63727522966&HV=1591926169; MUIDB=22E30E44290F65C10FD40091282164ED; _RwBf=mtu=0&g=0&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2020-06-12T01:42:48.0031749+00:00; _HPVN=CS=eyJQbiI6eyJDbiI6MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyMC0wNi0xMlQwMDowMDowMFoiLCJJb3RkIjowLCJEZnQiOm51bGwsIk12cyI6MCwiRmx0IjowLCJJbXAiOjV9; ABDEF=V=0&ABDV=10&MRNB=1591900099874&MRB=0; _SS=SID=081690153F2A6BF013EF9EF23E816ACD&R=0&RB=0&GB=0&RG=200&RP=0; _EDGE_S=SID=081690153F2A6BF013EF9EF23E816ACD; ipv6=hit=1591929767011&t=6')}
    request = tor.get(bing_url, headers=headers, timeout=(1, 5))
    if request.status_code == 200:
        soup = BeautifulSoup(request.text, 'lxml')
        recaptcha = soup('div', {'id': 'recaptcha'})
        if len(recaptcha) != 0:
            tor_reset()
            with open('/home/spider/pii/spokeo/config/unsaved_bing', 'a') as f:
                f.write(str(bing_url) + '\n')
            f.close()
        else:
            try:
                no_result = soup('div', {'class': 'b_no'}).text
                if len(no_result) != 0:
                    print("No result")
                    return
            except:
                results = soup.find_all('li', {'class': 'b_algo'})
                links = [div.find('a') for div in results]
                i = 0
                for link in links:
                    link_href = link.get('href')
                    if 'mylife' in link_href.lower():
                        get_mylife(str(link_href), name, city)
                        i += 1


if __name__ == "__main__":
    read_data()
    tor_reset()
    time = 0
    with open('/home/spider/pii/spokeo/config/stop_point', 'r') as f:
        temp = f.readline()
    start_point = int(str(temp.replace('\n', '')))
    f.close()

    for pii in piis:
        info = str(pii).split('\"')
        name = info[11].strip('\"')
        if ' ' in info[23]:
            cities = info[23].strip('\"').split(' ')
            city = cities[0]
        elif 'None' in info[23]:
            city = ''
        else:
            city = info[23].strip('\"')
        query = name + '%20' + city
        get_url(query, name, city)
        time += 1
        if time < start_point:
            continue
        if time % 100 == 0:
            with open('/home/spider/pii/spokeo/config/stop_point', 'w') as f:
                f.write(str(time) + '\n')
            f.close()
