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


# def restartTor():
#     os.system('taskkill /IM firefox.exe')
#     os.system('taskkill /IM NordVPN.exe')
#
#     sleep(3)


# restartTor()


def start():
    result_folder = 'D:/PII/senior_sample/voterrecords/'
    print(datetime.datetime.now())
    global browser
    # os.system('start D:\\NordVPN\\NordVPN.exe')
    browser = webdriver.Firefox(firefox_profile=fp, capabilities=firefox_capabilities,
                                executable_path=r'C:\Users\qq550\OneDrive\Desktop\demo\geckodriver.exe')
    browser.delete_all_cookies()
    browser.set_page_load_timeout(120)
    browser.set_script_timeout(120)
    f = open('D:/PII/senior.csv', 'r')
    next(f)
    log_index = -1
    for line in f:
        log_index += 1
        if (log_index < 0):
            continue
        infos = str(line).split(',')
        name = infos[1].strip('\"')
        temp_state = infos[4].strip('\"')
        print(log_index)
        try:
            browser.get('https://cn.bing.com/search?q=' + name + " " + temp_state + " "+ '%20voterrecords' + '&ensearch=1')
            curPageSource = BeautifulSoup(browser.page_source, 'lxml')
            result = curPageSource('div', {'id': 'recaptcha'})
            if len(result) != 0:
                # restartTor()
                # os.system('start D:\\NordVPN\\NordVPN.exe')
                # sleep(10)
                # browser = webdriver.Firefox(firefox_profile=fp, capabilities=firefox_capabilities,
                #                             executable_path=r'C:\Users\qq550\OneDrive\Desktop\demo\geckodriver.exe')
                browser.delete_all_cookies()
                browser.set_page_load_timeout(120)
                browser.set_script_timeout(120)
                pass
            else:
                try:
                    noresult = curPageSource('div', {'class': 'b_no'}).text
                    if len(noresult) != 0:
                        continue
                except:
                    ssearching = curPageSource.find_all('li', {'class': 'b_algo'})
                    links = [div.find('a') for div in ssearching]
                    i = 0
                    for link in links:
                        link_href = link.get('href')
                        link_lower = link_href.lower()
                        # if "https://www.peekyou.com/" == link_lower:
                            # continue
                        if 'voterrecords' in link_lower:
                            browser.get(link_href)
                            with open(result_folder + str(i) + '_' + name + '_' + 'peekyou' + '.html', 'wb') as writer:
                                writer.write(browser.page_source.encode('utf-8'))
                            print('Page saved')
                            i += 1
        except:
            # restartTor()
            # os.system('start D:\\NordVPN\\NordVPN.exe')
            # sleep(10)
            # browser = webdriver.Firefox(firefox_profile=fp, capabilities=firefox_capabilities,
            #                             executable_path=r'C:\Users\qq550\OneDrive\Desktop\demo\geckodriver.exe')
            browser.delete_all_cookies()
            browser.set_page_load_timeout(120)
            browser.set_script_timeout(120)
            continue


if __name__ == "__main__":
    start()
    print("end")
