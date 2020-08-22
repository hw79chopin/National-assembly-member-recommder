# -*- coding: utf-8 -*- 
import numpy as np
import pandas as pd
import urllib.request
import json
import time
import glob, os
from tqdm.notebook import tqdm
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver

class Crawler():
    def __init__(self, driver_dir, file_dir):
        self.driver_dir = driver_dir
        self.file_dir = file_dir

    def crawl_bills_cont(self):   # 기존에 크롤링했던 파일이 있을 경우
        driver = webdriver.Chrome(r"{}".format(self.driver_dir))
        
        # 기존 데이터 확인하기
        os.chdir(self.file_dir)
        latest_file = glob.glob("*.json")[-1]
        with open(latest_file, "r") as f:
            past_data = json.load(f)
        
        # 가장 마지막으로 크롤링한 법안 확인하기
        latest_bill = next(iter(past_data))

        print("최근 파일과 마지막 법안",latest_file, latest_bill)
        # 의안정보시스템 접속
        driver.get('http://likms.assembly.go.kr/bill/main.do')

        # 의안 검색
        driver.find_element_by_xpath('//*[@id="srchForm"]/div/div[6]/button[1]').click()

        # 설정 100개로 변경
        driver.find_element_by_xpath('//*[@id="pageSizeOption"]').click()
        driver.find_element_by_xpath('//*[@id="pageSizeOption"]/option[4]').click()

        # 본격적인 크롤링하기
        dict_bills = {}
        done = False

        for page in range(1,20):
            if page == 1:
                pass
            elif page != 1:
                driver.find_element_by_xpath('//*[@id="pageListViewArea"]/a[' + str(page) + ']').send_keys(Keys.ENTER)
            
            # 법안 크롤링하기
            for num in tqdm(range(0,100)):
                temp_dict = {}
                temp_dict['bill_title'] = driver.find_elements_by_css_selector('div.pl25')[num].text
                
                # 법안 들어가기
                driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/div[2]/table/tbody/tr[' + str(num+1) + ']/td[2]/div[2]/a').send_keys(Keys.ENTER)
                window_bill = driver.window_handles[0]    # 법안창 선택하기
                bill_content = driver.find_elements_by_css_selector('body > div > div.contentWrap > div.subContents > div > div.contIn > div.tableCol01 > table > tbody > tr > td')
                if bill_content[0].text == latest_bill:     # 만약 마지막에 크롤링했던 법안까지 크롤링하면 크롤링 종료
                    done = True
                    break

                temp_dict['bill_num'] = bill_content[0].text
                temp_dict['propose_date'] = bill_content[1].text
                temp_dict['propose_session'] = bill_content[4].text
                content = driver.find_elements_by_css_selector('#summaryContentDiv')
                if len(content) == 0:
                    pass
                else:
                    temp_dict['bill_content'] = content[0].text.replace('\n', ' ')
                    
                # 제안자 클릭
                proposers_link = driver.find_elements_by_xpath('/html/body/div/div[2]/div[2]/div/div[3]/div[1]/table/tbody/tr/td[3]/a/img')
                if len(proposers_link) > 0:
                    proposers_link[0].click()
                    driver.implicitly_wait(1)
                    window_senators = driver.window_handles[1]
                    driver.switch_to.window(window_senators)    # window를 바꾼 다음
                    senators = driver.find_elements_by_css_selector('div.layerInScroll.coaTxtScroll > div > a')

                    list_temp = []
                    for senator in senators:
                        list_temp.append(senator.text)
                    temp_dict['proposed_senators'] = list_temp
                    driver.close() # 제안자 window는 없애고
                    driver.switch_to.window(window_bill)    # 다시 메인 window로 돌아와서
                dict_bills[bill_content[0].text]=temp_dict
                driver.back()
            
            # 마지막까지 크롤링한 법안에 이르면 끝
            if done == True:
                break
        
        driver.quit()

        # 과거 데이터랑 병합하기
        new_data = dict_bills.copy()
        new_data.update(past_data)   # 새로운 크롤링 데이터와 기존 크롤링 데이터 합쳐주기

        num = 0
        for i in new_data:
            num +=1 # 총 몇 개의 법안이 크롤링 되었는지 확인

        # 크롤링한 데이터 저장하기
        with open(self.file_dir + "/bills_" + str(num) + ".json", "w") as json_file:
            json.dump(new_data, json_file, indent="\t")


    def crawl_bills_new(self): # 처음 크롤링하는 경우
        driver = webdriver.Chrome(r"{}".format(self.driver_dir))

        # 의안정보시스템 접속
        driver.get('http://likms.assembly.go.kr/bill/main.do')

        # 의안 검색
        driver.find_element_by_xpath('//*[@id="srchForm"]/div/div[6]/button[1]').click()

        # 설정 100개로 변경
        driver.find_element_by_xpath('//*[@id="pageSizeOption"]').click()
        driver.find_element_by_xpath('//*[@id="pageSizeOption"]/option[4]').click()

        # 본격적인 크롤링하기
        dict_bills = {}
        done = False

        for page in range(1,20):
            if page == 1:
                pass
            elif page != 1:
                driver.find_element_by_xpath('//*[@id="pageListViewArea"]/a[' + str(page) + ']').send_keys(Keys.ENTER)
            
            # 법안 크롤링하기
            for num in tqdm(range(0,100)):
                temp_dict = {}
                temp_dict['bill_title'] = driver.find_elements_by_css_selector('div.pl25')[num].text
                
                # 법안 들어가기
                driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/div[2]/table/tbody/tr[' + str(num+1) + ']/td[2]/div[2]/a').send_keys(Keys.ENTER)
                window_bill = driver.window_handles[0]    # 법안창 선택하기
                bill_content = driver.find_elements_by_css_selector('body > div > div.contentWrap > div.subContents > div > div.contIn > div.tableCol01 > table > tbody > tr > td')
                if bill_content[0].text == latest_bill:     # 만약 마지막에 크롤링했던 법안까지 크롤링하면 크롤링 종료
                    done = True
                    break

                temp_dict['bill_num'] = bill_content[0].text
                temp_dict['propose_date'] = bill_content[1].text
                temp_dict['propose_session'] = bill_content[4].text
                content = driver.find_elements_by_css_selector('#summaryContentDiv')
                if len(content) == 0:
                    pass
                else:
                    temp_dict['bill_content'] = content[0].text.replace('\n', ' ')
                    
                # 제안자 클릭
                proposers_link = driver.find_elements_by_xpath('/html/body/div/div[2]/div[2]/div/div[3]/div[1]/table/tbody/tr/td[3]/a/img')
                if len(proposers_link) > 0:
                    proposers_link[0].click()
                    driver.implicitly_wait(1)
                    window_senators = driver.window_handles[1]
                    driver.switch_to.window(window_senators)    # window를 바꾼 다음
                    senators = driver.find_elements_by_css_selector('div.layerInScroll.coaTxtScroll > div > a')

                    list_temp = []
                    for senator in senators:
                        list_temp.append(senator.text)
                    temp_dict['proposed_senators'] = list_temp
                    driver.close() # 제안자 window는 없애고
                    driver.switch_to.window(window_bill)    # 다시 메인 window로 돌아와서
                dict_bills[bill_content[0].text]=temp_dict
                driver.back()
            
            # 마지막까지 크롤링한 법안에 이르면 끝
            if done == True:
                break
        
        driver.quit()

        # 과거 데이터랑 병합하기
        new_data = dict_bills.copy()

        num = 0
        for i in new_data:
            num +=1     # 총 몇 개의 법안이 크롤링 되었는지 확인

        # 크롤링한 데이터 저장하기
        with open(self.file_dir + "/bills_" + str(num) + ".json", "w") as json_file:
            json.dump(new_data, json_file, indent="\t")

    def crawl_senator_info(self):
        driver = webdriver.Chrome(r"{}".format(self.driver_dir))

        # 열러라 국회 의원 접속
        driver.get('http://watch.peoplepower21.org/?act=&mid=AssemblyMembers&vid=&mode=search&name=&party=&region=&sangim=&gender=&age=&elect_num=')

        # 크롤링 시작
        list_name = []
        list_party = []
        list_region = []
        list_elected_times = []
        list_committee = []
        list_education = []
        list_career = []
        list_tel = []
        list_email = []
        list_bill_count = []
        list_committee_attend = []
        list_meeting_attend = []
        list_property = []
        for page in range(1,11):
            if page != 1:
                driver.get('http://watch.peoplepower21.org/?mid=AssemblyMembers&mode=search&party=&region=&sangim=&gender=&elect_num=&page=' + str(page))
            for person in range(1, 31):
                driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[' + str(person) + ']/div').click()
                
                full_name = driver.find_elements_by_css_selector('#content > div > div > div > div.panel.panel-default > div.panel-body > h1')
                party = driver.find_elements_by_css_selector('div > div.col-md-9.col-lg-9 > table > tbody > tr:nth-child(1) > td:nth-child(2)')
                region = driver.find_elements_by_css_selector('#content > div > div > div > div.panel.panel-default > div.panel-body > div > div.col-md-9.col-lg-9 > table > tbody > tr:nth-child(2) > td:nth-child(2) > a')
                elected_times = driver.find_elements_by_css_selector('#content > div > div > div > div.panel.panel-default > div.panel-body > div > div.col-md-9.col-lg-9 > table > tbody > tr:nth-child(3) > td:nth-child(2)')
                committee = driver.find_elements_by_css_selector('#content > div > div > div > div.panel.panel-default > div.panel-body > div > div.col-md-9.col-lg-9 > table > tbody > tr:nth-child(4) > td:nth-child(2) > a')
                education = driver.find_elements_by_css_selector('#content > div > div > div > div.panel.panel-default > div.panel-body > div > div.col-md-9.col-lg-9 > table > tbody > tr:nth-child(5) > td:nth-child(2)')
                career = driver.find_elements_by_css_selector('#content > div > div > div > div.panel.panel-default > div.panel-body > div > div.col-md-9.col-lg-9 > table > tbody > tr:nth-child(6) > td:nth-child(2)')
                tel = driver.find_elements_by_css_selector('#content > div > div > div > div.panel.panel-default > div.panel-body > div > div.col-md-9.col-lg-9 > table > tbody > tr:nth-child(7) > td:nth-child(2)')
                email = driver.find_elements_by_css_selector('#content > div > div > div > div.panel.panel-default > div.panel-body > div > div.col-md-9.col-lg-9 > table > tbody > tr:nth-child(8) > td:nth-child(2) > a')
                bill_count = driver.find_elements_by_css_selector('#collapse1 > div > h3 > span')
                committee_attend = driver.find_elements_by_css_selector('#collapse2 > div > span > span > span > span')
                meeting_attend = driver.find_elements_by_css_selector('#collapse3 > div > p:nth-child(3) > span > span > span > span')
                property_ = driver.find_elements_by_css_selector('#collapse5 > div > table > tbody > tr.info')
                if len(committee) != 0:
                    list_committee.append(committee[0].text)
                else:
                    list_committee.append(np.nan)
                if len(committee_attend) != 0:
                    list_committee_attend.append(committee_attend[0].text)
                else:
                    list_committee_attend.append(np.nan)
                if len(property_) != 0:
                    list_property.append(property_[0].text)
                else:
                    list_property.append(np.nan)
                list_name.append(full_name[0].text)
                list_party.append(party[0].text.split(' ', 1)[-1])
                list_region.append(region[0].text)
                list_elected_times.append(elected_times[0].text)
                list_education.append(education[0].text.replace('\n', '/'))
                list_career.append(career[0].text.replace('\n', '/'))
                list_tel.append(tel[0].text)
                list_email.append(email[0].text)
                list_bill_count.append(bill_count[0].text)
                list_meeting_attend.append(meeting_attend[0].text)
                driver.back()

        driver.quit()

        # 데이터프레임으로 저장
        df = pd.DataFrame([list_name, list_party, list_region, list_elected_times, 
                   list_committee, list_education, list_career, list_tel,
                  list_email, list_bill_count, list_committee_attend,
                  list_meeting_attend, list_property]).T
        colNames = ['이름' ,'정당', '선거구', '당선횟수', '소속위원회', '학력', '주요경력',
                '연락처', '이메일', '대표발의법안수', '위원회 출석률', '본회의 출석률', '재산']
        df.columns = colNames
        df

        # csv 파일로 저장
        df.to_csv(self.file_dir + '/21st_assembly_members.csv', index=False)
    
    def download(URL, short_name):  # 국회의원 사진 크롤링하기 위한 함수
        list_temp = []
        short_name = short_name[0].text.split(' ',1)[-1]
        if short_name not in list_temp:
            list_temp.append(short_name)
            fullName = "images/" + short_name + ".jpg"
            urllib.request.urlretrieve(URL, fullName)   
        else:
            fullName = "images/" + short_name + " (2).jpg"
            urllib.request.urlretrieve(URL, fullName)   
    
    def crawl_senator_photo(self):
        # 열러라 국회 의원 접속
        driver.get('http://watch.peoplepower21.org/?act=&mid=AssemblyMembers&vid=&mode=search&name=&party=&region=&sangim=&gender=&age=&elect_num=')

        # 사진 다운받기
        for page in range(1,11):
            if page != 1:
                driver.get('http://watch.peoplepower21.org/?mid=AssemblyMembers&mode=search&party=&region=&sangim=&gender=&elect_num=&page=' + str(page))
            for person in range(2,32):
                short_name = driver.find_elements_by_css_selector('#content > div.col-md-8 > div:nth-child('+ str(person)+')> div > a:nth-child(2) > h4')
                image = driver.find_elements_by_tag_name('#content > div.col-md-8 > div:nth-child(' + str(person)+ ') > div > a:nth-child(1) > img')
                src = image[0].get_attribute('src')
                download(src, short_name)

        driver.quit()


# 시연        
crawler = Crawler(driver_dir = '/chromedriver', file_dir = '의안정보시스템 crawling/')        # 이 부분만 사용자에 맡게 바꾸고 Terminal에서 $ python3 cralwer.py 하면 됨
crawler.crawl_bills_cont()  # 이어서 할 경우
# crawler.crawl_bills_new()     # 새로 할 경우