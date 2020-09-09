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
#     sleep(3)
# restartTor()

def start():
    result_folder = 'D:/PII/checkmate/TorMarket_5k/'
    print(datetime.datetime.now())
    global browser
    # os.system('start D:\\NordVPN\\NordVPN.exe')
    browser = webdriver.Firefox(firefox_profile=fp, capabilities=firefox_capabilities,
                                executable_path=r'C:\Users\qq550\OneDrive\Desktop\demo\geckodriver.exe')
    browser.delete_all_cookies()
    browser.set_page_load_timeout(120)
    browser.set_script_timeout(120)
    f = open('D:/PII/data_ssn/TorMarket_5k_sample.csv', 'r')
    next(f)
    log_index = -1
    for line in f:
        log_index += 1
        if (log_index < 747):
            continue
        infos = str(line).split(',')
        name = infos[3].strip('\"')
        linkname = name.replace(' ', '-')
        file_name = name.replace(' ', '_')
        print(log_index)
        try:
            flag = False
            for page in range(1, 20):
                if flag:
                    continue
                browser.get('https://www.instantcheckmate.com/people/' + linkname + '/' + '?page=' + str(page))
                curPageSource = BeautifulSoup(browser.page_source, 'lxml')
                title = curPageSource.title.text
                if '404 Not Found' in title:
                    flag = True
                    continue
                if 'Error' in title:
                    flag = True
                    continue
                with open(result_folder + str(page) + '_' + name + '_' + 'checkmate' + '.html', 'wb') as writer:
                    writer.write(browser.page_source.encode('utf-8'))
                print("Page Saved : " + name + ' - ' + str(page))
        except:
            browser.delete_all_cookies()
            continue


if __name__ == "__main__":
    start()
    print("end")
