from torrequest import TorRequest
import os, random
import time
import threading
import queue as Queue
from bs4 import BeautifulSoup
import mysql.connector

cnx = mysql.connector.connect(user='root', password='SaTc!2020',
                            host='localhost', database='pii')
agents = []
cookies = []
headers = {}
tor = TorRequest(password='satc2020')


#
# class myThread(threading.Thread):
#     def __init__(self, name, queue):
#         threading.Thread.__init__(self)
#         self.name = name
#         self.queue = queue
#
#     def run(self):
#         while True:
#             try:
#                 save_content(self.name, self.queue)
#             except Exception as err:
#                 print("Exception from thread run", self.getName(), ': ', err)
#                 break


def init():
    global cookies
    global headers
    global agents

    with open('/home/spider/pii/mylife/config/useragents', 'r') as f:
        lines = f.readlines()
    agents = [i.replace('\n', '') for i in lines]
    f.close()

    with open('/home/spider/pii/mylife/config/cookies', 'r') as f:
        lines = f.readlines()
    cookies = [i.replace('\n', '') for i in lines]

    headers = {
        'Cookie': '{:}'.format("JSESSIONID=5141585B5B11424B1E1844BA37080E85; mylife_marketing_channel=SEO; "
                               "_ga=GA1.2.1122882368.1592191143; _gid=GA1.2.127403464.1592191143; "
                               "_gcl_au=1.1.1916513121.1592191143; "
                               "__CG=u%3A541777163072038900%2Cs%3A1856218148%2Ct%3A1592191176820%2Cc%3A3%2Ck%3Awww"
                               ".mylife.com%2F47%2F47%2F393%2Cf%3A1%2Ci%3A1; _gat_UA-73309658-5=1; "
                               "_gat_UA-73309658-1=1; _dc_gtm_UA-73309658-5=1; _fbp=fb.1.1592191147079.1966496629; "
                               "_uetsid=ec60c5c1-9592-bcc2-f7c1-634e8c69c61c; "
                               "_uetvid=b67ddb1d-17f5-28c9-ae59-061ed0e3118e"),
        'User-Agent': '{}'.format(random.choice(agents))
    }
    f.close()
    tor_reset()


def tor_reset():
    global tor
    tor.close()
    tor = TorRequest(password='satc2020')
    time.sleep(2)
    try:
        tor.reset_identity()
    except:
        tor.close()
        tor = TorRequest(password='satc2020')
        tor.reset_identity()
    response = tor.get('http://ipecho.net/plain')
    print("---------Ip Address has changed: ", response.text + '---------')


def insert_post(post_record):
    print("saved to mysql")


def visit_page(infors):
    global headers
    global tor

    items = infors.split(',')
    print(str(items))
    query_name = items[0]
    query_city = items[1]
    url = items[2].strip('\n')
    print(url)
    try:
        request = tor.get(url, headers=headers, timeout=(2, 5))
    except Exception as err:

        with open('/home/spider/pii/mylife/config/err_log', 'a') as f:
            f.write(str(err) + '\n')
        if 'read' in str(err):
            print('---------Read timeout---------' + '\n')
        f.close()
        init()
        tor_reset()
        return

    if request.status_code == 200:
        soup = BeautifulSoup(request.text, 'lxml', from_encoding='utf8')
        save_content(soup, query_name, query_city)
    else:
        with open('/home/spider/pii/mylife/config/err_log', 'a') as f:
            f.write(str(request.status_code) + '\n')
        f.close()
        init()
        tor_reset()
        soup = BeautifulSoup(request.content, 'html.parser')
        save_content(soup, query_name, query_city)


def save_content(soup, query_name, query_city):
    global tor
    extractedValues = {'query_name': query_name, 'query_city': query_city, 'platform': 'MyLife', 'name': 'None', 'age': 'None',
                       'city': 'None', 'state': 'None', 'address': 'None', 'reputation': 'None',
                       'neighbors': 'None', 'associated_Names': 'None', 'description': 'None'}
    try:
        section = soup.find('div', {'class': 'vcard-first-section'})
        name_age_list = section.find('h2', {'class': 'profile-information-name-age'}).text
        name_age = name_age_list.split(', ')
        name = name_age[0]
        age = name_age[1].rstrip()
        extractedValues['name'] = name
        extractedValues['aga'] = age
        print("1")
    except Exception as err:
        print(str(err))
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
                    city = temp_lit[0].replace('\n', '').replace('\n', '')
                    state = temp_lit[1]
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
            return
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
        print('5')
        des = soup.find('div', {'class': 'profile-bio-container'}).text
        des = des.replace('Summary:', '')
        extractedValues['relatives'] = des
        if ',' in extractedValues['relatives']:
            extractedValues['relatives'] = extractedValues['relatives'].replace(', ', '-')
    except Exception as err:
        print(str(err) + '1')
        pass

    print(extractedValues['name'])
    insert_post(extractedValues)


if __name__ == '__main__':
    init()
    tor_reset()
    with open('/home/spider/pii/mylife/config/stop_point', 'r') as f:
        line = f.readline()
    start_point = int(line.replace('\n', ''))
    f.close()

    with open('/home/spider/pii/config/saved_url_senior', 'r') as f:
        lines = f.readlines()
    url_list = [i.replace('\n', '') for i in lines]
    url_list = url_list[1:]
    f.close()

    num = start_point
    print("Start from : " + str(start_point) + "\n" + "End at : " + str(len(url_list)))
    for item in url_list:
        visit_page(item)
        print(str(num))
        num += 1
        if num % 70 == 0:
            with open('/home/spider/pii/mylife/config/stop_point', 'w') as f:
                f.write(str(num))
            f.close()
    print("End")