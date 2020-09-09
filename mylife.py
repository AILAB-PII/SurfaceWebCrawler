import time
import re
import os
import mysql.connector
import os
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import os
ua = UserAgent()
import random

cnx = mysql.connector.connect(user='root', password='SaTc!2020', port='3306',
                              host='localhost', database='pii')

cookies = ["usid=16f5f1f5-2044-4359-93cf-2d44798a5ec0; _ga=GA1.2.1698856021.1590412612; _gcl_au=1.1.2089394219.1590412616; _fbp=fb.1.1590412651061.1189641472; __qca=P0-408544037-1590412638078; _vwo_uuid_v2=D2A5D16C364D42F1C72D48F8F7E4B6FCF|6963da2a9f99ad05b8f285de39a6255c; _vwo_uuid=D2A5D16C364D42F1C72D48F8F7E4B6FCF; _vwo_ds=3%3Aa_0%2Ct_0%3A0%241590417434%3A66.03864482%3A%3A%3A580_0%2C579_0%3A0; _gid=GA1.2.1652181498.1593520665; vid=47785db4-b8b0-480d-b957-515e13bdbca8; mylife_marketing_channel=SEO; _uetsid=bec46db2-23ff-9aac-ce34-31b70e76c1b0; _uetvid=a4320d0f-2b12-c607-f738-333938b5cfbe; _vis_opt_s=3%7C; __CG=u%3A5591615376685201000%2Cs%3A59803990%2Ct%3A1593525069730%2Cc%3A1%2Ck%3Awww.mylife.com%2F23%2F23%2F64%2Cf%3A1%2Ci%3A1",
           "vid=46d8be60-ab29-4077-bc91-28d288ad4a10; JSESSIONID=0E0143DAB84D7588A5E3E8C289B832D1; _ga=GA1.2.69545783.1593366819; __CG=u%3A1618761288383912000%2Cs%3A1269236637%2Ct%3A1593541852019%2Cc%3A3%2Ck%3Awww.mylife.com%2F34%2F34%2F216%2Cf%3A1%2Ci%3A1; _fbp=fb.1.1593366820877.28531669; _gid=GA1.2.1503793198.1593522374; mylife_marketing_channel=SEO; _gat_UA-73309658-1=1; _dc_gtm_UA-73309658-5=1; _gat_UA-73309658-5=1; _uetsid=06f1330d-1a84-0a6e-daee-432a2781ef3e; _uetvid=588c6ba5-3c57-5a50-2e2f-899ebbd84cb8",
           "usid=16f5f1f5-2044-4359-93cf-2d44798a5ec0; _ga=GA1.2.1698856021.1590412612; _gcl_au=1.1.2089394219.1590412616; _fbp=fb.1.1590412651061.1189641472; __qca=P0-408544037-1590412638078; _vwo_uuid_v2=D2A5D16C364D42F1C72D48F8F7E4B6FCF|6963da2a9f99ad05b8f285de39a6255c; _vwo_uuid=D2A5D16C364D42F1C72D48F8F7E4B6FCF; _vwo_ds=3%3Aa_0%2Ct_0%3A0%241590417434%3A66.03864482%3A%3A%3A580_0%2C579_0%3A0; _gid=GA1.2.1652181498.1593520665; vid=47785db4-b8b0-480d-b957-515e13bdbca8; mylife_marketing_channel=SEO; _vis_opt_s=3%7C; JSESSIONID=27E93AE9B4C617730985E7D0AA49B0FF; _gat_UA-73309658-1=1; _dc_gtm_UA-73309658-5=1; _uetsid=bec46db2-23ff-9aac-ce34-31b70e76c1b0; _uetvid=a4320d0f-2b12-c607-f738-333938b5cfbe; _gat_UA-73309658-5=1; __CG=u%3A5591615376685201000%2Cs%3A1193746585%2Ct%3A1593541920829%2Cc%3A2%2Ck%3Awww.mylife.com%2F47%2F47%2F393%2Cf%3A1%2Ci%3A1"]

def get_tor_session():
    time.sleep(6)
    session = requests.session()
    session.proxies = {'http': 'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def insert_post(post_record):
    query = '''INSERT INTO mylife_email_new
                (query_name, query_city, platform, name, age, city, state, address, reputation, relatives, alias, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
    if 'None' in post_record['name']:
        return

    args = (post_record['query_name'], post_record['query_city'], post_record['platform'], post_record['name'],
            post_record['age'], post_record['city'], post_record['state'], post_record['address'],
            post_record['reputation'],
            post_record['associated_Names'], post_record['alias'], post_record['description'])

    if ',' in post_record['address']:
        post_record['address'] = post_record['address'].replace(',', '-')

    if '•' in post_record['address']:
        post_record['address'] = post_record['address'].replace('•', '-')

    if ',' in post_record['associated_Names']:
        post_record['associated_Names'] = post_record['associated_Names'].replace(',', '---')

    if '•' in post_record['associated_Names']:
        post_record['associated_Names'] = post_record['associated_Names'].replace('•', '---')

    cnx.cursor().execute(query, args)
    cnx.commit()
    cnx.cursor().close()
    print("saved to mysql")


def save_content(soup, query_name, query_city):
    global tor
    extractedValues = {'query_name': query_name, 'query_city': query_city, 'platform': 'MyLife', 'name': 'None',
                       'age': 'None',
                       'city': 'None', 'state': 'None', 'address': 'None', 'reputation': 'None',
                       'alias': 'None', 'associated_Names': 'None', 'description': 'None'}
    try:
        section = soup.find('div', {'class': 'vcard-container'})
        name_age_list = section.find('h2', {'class': 'profile-information-name-age'}).text
        name_age = name_age_list.split(', ')
        name = name_age[0]
        age = name_age[1].rstrip()
        extractedValues['name'] = name
        extractedValues['aga'] = age
    except:
        pass
    if 'None' in extractedValues['name']:
        try:
            items = soup.find_all('div', {'class': 'profile-card'})
            for eachone in items:
                try:
                    name_age_location = eachone.find('div', {'class': 'name-age-location'})
                    name = name_age_location.find('h2', {'itemprop': 'name'}).text
                    name = name.replace('\n', '').strip(' ')
                    try:
                        age = name_age_location.find('a', {'class': 'age'}).text
                        age = age.replace('\n', '')
                        if ', ' in age:
                            age = age.replace(', ', '')
                        extractedValues['age'] = age
                    except:
                        pass
                    city_state = name_age_location.find('span', {'class': 'location'}).text
                    if 'Lives in ' in city_state:
                        city_state = city_state.replace('Lives in ', '')
                    temp_lit = city_state.split('\n')
                    city = temp_lit[0].replace('\n', '')
                    state = temp_lit[1].replace(' ', '')
                    extractedValues['name'] = name
                    extractedValues['city'] = city
                    extractedValues['state'] = state
                except Exception as err:
                    continue
                try:
                    related = eachone.find('div', {'class': 'related'}).text
                    related = related.replace('\nRelated to:', '')
                    related = related.replace('\n', '')
                    if ',' in related:
                        relateds = related.split(',')
                    x = ''
                    for i in relateds:
                        i = i.strip(' ')
                        x += i + '-'
                    extractedValues['associated_Names'] = x
                except Exception as err:
                    pass

                try:
                    akaList = eachone.find('div', {'class': 'aka'}).text.split('\n\n')
                    aka = akaList[0].replace('AKA:', '').strip('\n')
                    if ',' in aka:
                        aka = aka.replace(',', '')
                    extractedValues['alias'] = aka
                except Exception as err:
                    pass

                try:
                    score = eachone.find('div', {'class': 'score'}).text
                    score = score.replace('AKA:', '')
                    score = score.replace('\n', '')
                    score = score.replace(' ', '')
                    if ',' in score:
                        score = score.replace(',', '')
                    extractedValues['reputation'] = score
                except Exception as err:
                    pass
                print('-----------------------------------------------------------------')
                print(extractedValues['name'])
                insert_post(extractedValues)
        except Exception as err:
            return
    try:
        location = soup.find('h2', {'class': 'profile-information-location'}).text
        if ',' in location:
            ci_list = location.split(', ')
            extractedValues['city'] = ci_list[0]
            extractedValues['state'] = ci_list[1]
        else:
            extractedValues['city'] = location
    except Exception as err:
        pass

    try:
        aka = soup.find('div', {'class': 'profile-details-container profile-aka-container'}).text
        aka = aka.replace('AKA:', '')
        aka = aka.replace(', ', '-')
        extractedValues['alias'] = aka
    except Exception as err:
        pass

    try:
        des = soup.find('div', {'class': 'profile-details-container profile-associates-container'}).text
        des = des.replace('Associates:', '')
        extractedValues['relatives'] = des
        if ',' in extractedValues['relatives']:
            extractedValues['relatives'] = extractedValues['relatives'].replace(', ', '-')
        if 'Associates:' in extractedValues['relatives']:
            extractedValues['relatives'] = 'None'
    except Exception as err:
        pass

    try:
        des = soup.find('div', {'class': 'profile-bio-container'}).text
        des = des.replace('Summary:', '')
        extractedValues['relatives'] = des
        if ',' in extractedValues['relatives']:
            extractedValues['relatives'] = extractedValues['relatives'].replace(', ', '-')
    except:
        pass

    print(extractedValues['name'])
    insert_post(extractedValues)


if __name__ == '__main__':
    with open('/home/spider/pii/mylife/config/stop_point', 'r') as f:
        line = f.readline()
    start_point = int(line.replace('\n', ''))
    f.close()

    with open('/home/spider/pii/config/saved_url', 'r') as f:
        lines = f.readlines()
    piis = [i.replace('\n', '') for i in lines]
    piis = piis[1:]
    f.close()
    lines.clear()
    print('------Beg------')

    print("Start from : " + str(start_point) + "\n" + "End at : " + str(len(piis)))
    tor = get_tor_session()
    user_agent = {'User-agent': '{}'.format(ua.random),
                  'Cookie': '{:}'.format(random.choice(cookies))}
    ip = tor.get('http://ipecho.net/plain', headers=user_agent, timeout=(10, 10))
    print("---------Ip Address is: ", ip.text + '---------')
    num = 0
    for pii in piis:
        num += 1
        print(str(num))
        if  num < int(len(piis)*1/10):
            pass
        else:
            continue
        # if num < start_point:
        #     continue
        # else:
        #     pass
        if num % 100 == 0:
            with open('/home/spider/pii/mylife/config/stop_point', 'w') as f:
                f.write(str(num) + '\n')
            f.close()
        infor = pii.split(',')
        query_name = infor[0]
        query_city = infor[1]
        url = infor[2]
        try:
            print(url)
            response = tor.get(url, headers=user_agent, timeout=(10, 10))
            soup = BeautifulSoup(response.text, 'lxml', from_encoding='utf8')
        except Exception as err:
            if 'Connection a' in str(err):
                continue
            if 'Connection b' in str(err):
                continue
            if 'SOCKSHTTPSConnectionPool(host=\'www.mylife.com\', port=443): Read timed out.' in str(err):
                os.system('sudo /etc/init.d/tor restart')
            print(str(err))
            tor = get_tor_session()
            user_agent = {'User-agent': '{}'.format(ua.random),
                          'Cookie': '{:}'.format(random.choice(cookies))}
            ip = tor.get('http://ipecho.net/plain', headers=user_agent, timeout=(10, 10))
            print("---------Ip Address is: ", ip.text + '---------')
            continue
        if response.status_code == 200:
            save_content(soup, query_name, query_city)
        else:
            print(response.status_code)
            user_agent = {'User-agent': '{}'.format(ua.random),
                          'Cookie': '{:}'.format(random.choice(cookies))}
            tor = get_tor_session()
            ip = tor.get('http://ipecho.net/plain', headers=user_agent, timeout=(10, 10))
            print("---------Ip Address is: ", ip.text + '---------')
            continue
