import requests

from crack import CrackWeiboSlide


from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import random

from random import choice
import time
#months = ['31','28','31','30','31','30','31','31','30','31','30','31']
months = [31,28,31,30,31,30,31,31,30,31,30,31]
headers = {
}
def get_cookie_from_weibo(username, password):
    driver = webdriver.Chrome()
    driver.get('https://weibo.cn')
    assert "微博" in driver.title
    login_link = driver.find_element_by_link_text('登录')
    ActionChains(driver).move_to_element(login_link).click().perform()
    login_name = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "loginName"))
    )
    login_password = driver.find_element_by_id("loginPassword")
    login_name.send_keys(username)
    login_password.send_keys(password)
    login_button = driver.find_element_by_id("loginAction")
    login_button.click()
    cookie = driver.get_cookies()
    driver.close()
    return cookie

def crawl_weiboSearch():
    global headers
    global cookie_list
    global url_list
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Cookie' : choice(cookie_list).strip()
    }
    output_file = input('输出文件名(不需要后缀))：   ')
    output_file += '.csv'
    for crawl_url in url_list:
        start_time = crawl_url[crawl_url.find('starttime='):crawl_url.find('&endtime=')]
        end_time = crawl_url[crawl_url.find('endtime='):crawl_url.find('&sort=')]
        try:
            result = requests.get(crawl_url,headers = headers,timeout = 10)
            result.encoding = 'utf8'
            soup = BeautifulSoup(result.text,'html.parser')

            page_list = soup.select('#pagelist')[0]
            #print(page_list.text)
            flag_index = page_list.text.find(r'/')
            last_page = int(page_list.text[flag_index + 1:-1])
            time.sleep(0.5)
            i = 1
        except Exception as identifier:
            #url_list.append(crawl_url)
            i = 1
            last_page = 1
            pass
        while True:
            try:
                headers = {
                    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
                    'Cookie' : choice(cookie_list).strip()
                }
                print('-' * 10 + start_time + '-' * 10  + '正在抓取第' + str(i) + '页' + '-' * 10 + end_time + '-' * 10)
                page_result = requests.get(crawl_url + '&page=' + str(i) ,headers = headers, timeout = 10)
                page_result.encoding = 'utf8'
                page_soup = BeautifulSoup(page_result.text,'html.parser')
                div_array = page_soup.select('.c')
                #print(len(div_array))
                with open(output_file,'a+',encoding = 'utf_8_sig') as file:
                    for div in div_array:
                        div_str = str(div)
                        if 'id' in str(div):
                            id_index = div_str.find('id=')
                            if 'M_' in div_str[id_index : id_index + 10]:
                                Blogger = div.select('a')[0].text
                                span_array = div.select('span')
                                micro_blog = span_array[0].text.replace(',','-')[1:]
                                # for span in div.select('span'):
                                #     print(span.text)
                                Time_and_Blogger = span_array[len(span_array) - 1].text.strip().replace(',','-')
                                file.write(Blogger + ',' + micro_blog + ',' + Time_and_Blogger[:Time_and_Blogger.find('日') + 1] + ',' + Time_and_Blogger[Time_and_Blogger.find('日') + 1 : Time_and_Blogger.find('日') + 7] + ',')
                                print(Blogger)
                                #爬取 赞 转发 和评论数
                                a_array = div.select('a')
                                for a_label in a_array:
                                    if '赞' in a_label.text:
                                        file.write(a_label.text[a_label.text.find('赞') + 2 : -1] + ',')
                                    elif '转发' in a_label.text:
                                        file.write(a_label.text[a_label.text.find('转发') + 3 : -1] + ',')
                                    elif '评论' in a_label.text:
                                        file.write(a_label.text[a_label.text.find('评论') + 3 : -1] + '\n')
                i += 1
                if i > last_page:
                    break
                time.sleep(0.5)
                pass
            except Exception as identifier:
                print('-' * 40 + '抓取失败，正在重试!' + '-' * 40)
                time.sleep(0.5)
                continue
                pass
        #break

def Simulated_Loading():
    global headers
    global cookie_list
    global url_list
    cookie_str = ''
    while True:
        Username = input('输入微博账号:\t')
        Password = input('输入密码:\t')
        crack = CrackWeiboSlide(Username,Password)
        if crack.crack() == True:
            cookie = crack.browser.get_cookies()
            for domain in cookie:
                #print(domain['name'] + '=' + domain['value'] + ';')
                cookie_str += domain['name'] + '=' + domain['value'] + '; '
            break 
        else:
            print('登陆失败，请重新登陆！')
            continue
    cookie_list.append(cookie_str[:-2])
    return 
    # for url in url_list:
    #     crawl_weiboSearch(url)
    #     break
    #     pass


def acquire_cookies():
    global cookie_list
    bIsloadCoookie_Fromlocalfile = input('是否从本地文件读入cookies：   1 Yes   2 No :')
    if bIsloadCoookie_Fromlocalfile == '1':
        print('cookies文件路径为:Cookies/Cookies.txt(一个cookie占用一行) ')
        with open('Cookies/Cookies.txt','r') as file:
            lines = file.readlines()
            for line in lines:
                cookie_list.append(line)
        cookie_list = list(set(cookie_list))
        pass
    elif bIsloadCoookie_Fromlocalfile == '2':
        while True:
            print('正在模拟登陆' + '-' * 40)
            Simulated_Loading()
            if input('是否继续登陆微博账号: 1 Yes   2 No :') == '1':
                continue
            else:
                print('退出模拟登陆' + '-' * 40)
                if input('是否将录入的cookies写到本地文件: 1 Yes   2 No :') == '1':
                    cookie_list = list(set(cookie_list))
                    with open('Cookies/Cookies.txt','w') as file:
                        for cookie in cookie_list:
                            file.write(cookie.strip() + '\n')
                    pass
                else:
                    pass
                break
def get_crwalUrl():
    global url_list
    Keyword = input('输入搜索关键词:\n')
    startTime = input('输入起始日期(例20181001):\t')
    endTime = input('输入结束日期(例20181002):\t')
    bIshot = input('是否从热搜微博中筛选(默认为Yes,建议选择Yes)): 1 Yes     2 No  :')
    if bIshot == '' or bIshot == '1':
        bIshot = '1'
    pre_date = startTime
    cur_date = ''
    while True:
        P_Year = int(pre_date[0:4])
        P_Month = int(pre_date[4:6])
        P_Day = int(pre_date[6:])
        if (P_Year % 4 == 0 and P_Year % 100 != 0) == 1 or P_Year % 400 == 0:
            months[1] = 29
        else:
            months[1] = 28
        SearchUrl = 'https://weibo.cn/search/mblog?hideSearchFrame=&advancedfilter=1&keyword=' + Keyword + '&starttime=' + pre_date + '&endtime=' + pre_date
        if bIshot == '1':
            SearchUrl += '&sort=hot'
        url_list.append(SearchUrl)
        if pre_date == endTime:
            break
        P_Day += 1
        if P_Day > months[P_Month - 1]:
            P_Day = 1
            P_Month += 1
            if P_Month > 12:
                P_Month = 1
                P_Year += 1
        if P_Month < 10 and P_Day >= 10:
            pre_date = str(P_Year) + '0' + str(P_Month) + str(P_Day)
        elif P_Month < 10 and P_Day < 10:
            pre_date = str(P_Year)+ '0' + str(P_Month) + '0' +str(P_Day)
        elif P_Month >= 10 and P_Day < 10:
            pre_date = str(P_Year)+ str(P_Month) + '0' +str(P_Day)
        #pre_date = cur_date




if __name__ == '__main__':
    url_list = []
    cookie_list = []
    with open('Cookies/Cookies.txt','r') as file:
        for line in file.readlines():
            cookie_list.append(line)
    acquire_cookies()
    get_crwalUrl()
    crawl_weiboSearch()
    pass
    #url = 'https://weibo.cn/search/mblog?hideSearchFrame=&keyword=疫苗&advancedfilter=1&starttime=20180715&endtime=20180716&sort=hot'


'''
18435121887
fuyu19960203.
'''