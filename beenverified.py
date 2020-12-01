from selenium import webdriver
from time import sleep
import datetime
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from bs4 import BeautifulSoup
from flask import Flask, g
from flask_restful import reqparse, Api, Resource
from selenium.webdriver.firefox.options import Options
import os

fp = webdriver.FirefoxProfile()
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 9150
fp.set_preference("network.proxy.type", 1)
fp.set_preference("network.proxy.socks", PROXY_HOST)
fp.set_preference("network.proxy.socks_port", PROXY_PORT)
fp.set_preference("network.proxy.socks_remote_dns", True)
fp.accept_untrusted_certs = True
firefox_capabilities = DesiredCapabilities.FIREFOX
firefox_capabilities['marionette'] = True
options = Options()
options.add_argument('-headless')


app = Flask(__name__)
api = Api(app)

parser_put = reqparse.RequestParser()
parser_put.add_argument("name", type=str, required=True, help="need full name data")
parser_put.add_argument("state", type=str, required=False, help="need state name (optional)")

origin_data = {}
result = []

# put your geckodriver path at here

executable_path = r'C:\Users\spider\Desktop\geckodriver.exe'

def restartfirefox():
    os.system('taskkill /IM firefox.exe')
    os.system('taskkill /IM tor.exe')
    sleep(3)
    # pur your tor path at here
    os.popen('''"C:\\Users\\spider\\Desktop\\Start Tor Browser.lnk" | more''')
    sleep(5)


def save_content_beenverified(soup, name):
    global result
    extractedValues = {'query_name': name, 'platform': 'Beenverified', 'name': 'None', 'age': 'None',
                       'city': 'None', 'state': 'None', 'address': 'None', 'phone_num': 'None',
                       'relatives': 'None', 'email': 'None', 'previous_location': 'None', 'job_title': 'None'}
    try:
        list = soup.find('div', {'class': "list"})
        items = list.find_all('div', {'class': "search-result card"})
        for eachone in items:
            try:
                name_location = eachone.find('div', {'class': 'search-result__title'}).text
                name_location_list = name_location.split("|")
                name = name_location_list[0].strip(" ")
                location = name_location_list[1]
                city_state = location.split(", ")
                city = city_state[0]
                state = city_state[1]
                extractedValues['name'] = name.replace('\n', '')
                extractedValues['city'] = city.replace('\n', '')
                extractedValues['state'] = state.replace('\n', '')
                print("1")
            except Exception as err:
                print(str(err))
                pass
            result.append(extractedValues)
    except Exception as err:
        print(str(err))
        result.append("No records in Beenverfied")
        return


def save_content_mylife(soup, name):
    global result
    extractedValues = {'query_name': name, 'platform': 'MyLife', 'name': name, 'age': 'None',
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
                result.append(extractedValues)
        except Exception as err:
            print(str(err))
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
        extractedValues['description'] = des
        if ',' in extractedValues['description']:
            extractedValues['description'] = extractedValues['description'].replace(', ', '-')
    except:
        pass
    result.append(extractedValues)


restartfirefox()


def get_url(name, state):
    global browser
    print(datetime.datetime.now())
    browser = webdriver.Firefox(firefox_profile=fp, capabilities=firefox_capabilities, options=options,
                                executable_path=executable_path)
    browser.delete_all_cookies()
    browser.set_page_load_timeout(30)
    browser.set_script_timeout(30)
    if state == '':
        url_mylife = 'https://www.mylife.com/{}/'.format(name.replace(" ", "-"))
        url_beenverified = 'https://www.beenverified.com/people/{}/'.format(name.replace(" ", "-"))
    else:
        url_mylife = 'https://www.mylife.com/people-search/{0}/find/{1}'.format(state, name.replace(" ", "-"))
        url_beenverified = 'https://www.beenverified.com/people/{1}/{0}/'.format(state, name.replace(" ", "-"))
    for i in range(50):
        time.sleep(3)
        try:
            browser.get(url_mylife)
            curPageSource_mylife = BeautifulSoup(browser.page_source, 'html.parser')
            browser.close()

            firefox = webdriver.Firefox(executable_path=executable_path)
            firefox.get(url_beenverified)
            curPageSource_beenverified = BeautifulSoup(firefox.page_source, 'html.parser')
            firefox.close()
        except Exception as err:
            print(str(err))
            if 'Connection a' in str(err):
                continue
            if 'Connection b' in str(err):
                continue
            restartfirefox()
            browser = webdriver.Firefox(firefox_profile=fp, capabilities=firefox_capabilities, options=options,
                                        executable_path=executable_path)
            browser.delete_all_cookies()
            browser.set_page_load_timeout(30)
            browser.set_script_timeout(30)
            continue
        save_content_mylife(curPageSource_mylife, name)
        save_content_beenverified(curPageSource_beenverified, name)
        print(result)
        return result
        break

def to_do(name, state):
    return get_url(name, state)


# (post / get) action
class TodoList(Resource):
    def post(self):
        """
        add a new user: curl http://127.0.0.1:5000/users -X POST -d "name=Justin&state=az" -H "Authorization: token justin"
        """
        args = parser_put.parse_args()
        # create a new user
        name = args['name']
        state = args['state']
        info = {"info": to_do(name, state)}
        return info, 201


api.add_resource(TodoList, "/users")

if __name__ == "__main__":
    app.run(debug=True)
