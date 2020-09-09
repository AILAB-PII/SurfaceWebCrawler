import os
from selenium import webdriver
from time import sleep
import datetime
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup

fp = webdriver.FirefoxProfile()
fp.accept_untrusted_certs = True
firefox_capabilities = DesiredCapabilities.FIREFOX
firefox_capabilities['marionette'] = True


def restartTor():
    sleep(3)


restartTor()


def start():
    result_folder = 'truepeoplesearch/'
    print(datetime.datetime.now())
    global browser
    os.system('start D:\\NordVPN\\NordVPN.exe')
    browser = webdriver.Firefox(firefox_profile=fp, capabilities=firefox_capabilities,
                                executable_path=r'C:\Users\qq550\OneDrive\Desktop\demo\geckodriver.exe')
    browser.delete_all_cookies()
    browser.set_page_load_timeout(120)
    browser.set_script_timeout(120)
    f = open('senior.csv', 'r')
    next(f)
    log_index = -1
    for line in f:
        log_index += 1
        if (log_index < 3000):
            continue
        record = line.split(',')
        ID = record[0]
        Name = record[1].strip('\"')
        t_name = Name.split(' ')
        first_name = t_name[0]
        first_name = first_name[:-1]
        last_name = t_name[1]
        Name = first_name + ' ' + last_name
        DOB_year = record[2]
        City = record[3]
        # State = record[4]
        Zip = record[5]
        try:
            # browser.get('https://www.google.com/search?hl=en&q=' + Name + ' ' + City + ' truepeoplesearch')
            browser.get('https://www.truepeoplesearch.com/find/' + first_name + '/' + last_name)
            curPageSource = BeautifulSoup(browser.page_source, 'html.parser')
            title = curPageSource.title
            if '404' in title or 'Captcha' in title:
                browser.delete_all_cookies()
                pass
            else:
                with open(result_folder + Name + '_' + '.html', 'wb') as writer:
                    writer.write(browser.page_source.encode('utf-8'))

        except:
            continue
            # result = curPageSource('div', {'id': 'recaptcha'})
        #     # if len(result) != 0:
        #         # restartTor()
        #         # os.system('start D:\\NordVPN\\NordVPN.exe')
        #         # sleep(10)
        #         # browser = webdriver.Firefox(firefox_profile=fp, capabilities=firefox_capabilities,
        #         #                             executable_path=r'C:\Users\qq550\OneDrive\Desktop\demo\geckodriver.exe')
        #         # browser.delete_all_cookies()
        #         # browser.set_page_load_timeout(120)
        #         # browser.set_script_timeout(120)
        #         # continue
        #     else:
        #         print(Name)
        #         ssearching = curPageSource.find_all('div', {'class': 'g'})
        #         links = [div.find('a') for div in ssearching]
        #         i = 0
        #         for link in links:
        #             link_href = link.get('href')
        #             link_lower = link_href.lower()
        #             temp = Name.split(' ')
        #             first_name = temp[0].lower()
        #             first_name = first_name[:-1]
        #             last_name = temp[1].lower()
        #             if 'truepeoplesearch' in link_lower and first_name in link_lower and last_name in link_lower:
        #                 browser.get(link_href)
        #                 with open(result_folder + str(i) + Name + '_' + '.html', 'wb') as writer:
        #                     writer.write(browser.page_source.encode('utf-8'))
        #                 print('Page saved')
        #                 browser.delete_all_cookies()
        #                 i += 1
        # except:
            # restartTor()
            # os.system('start D:\\NordVPN\\NordVPN.exe')
            # sleep(10)
            # browser = webdriver.Firefox(firefox_profile=fp, capabilities=firefox_capabilities,
            #                             executable_path=r'C:\Users\qq550\OneDrive\Desktop\demo\geckodriver.exe')
            # browser.delete_all_cookies()
            # browser.set_page_load_timeout(120)
            # browser.set_script_timeout(120)


if __name__ == "__main__":
    start()
    print("end")
