import requests
from bs4 import BeautifulSoup
import time as time
import urllib.request
import random
from getpass import getpass
import os
from collections import defaultdict
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

class Insta_Crawl:
    SCROLL_NUM = 5
    
    def __init__(self, driver_loc):
        self.__USERNAME = input("Input Instagram ID : ")
        self.__PASSWORD = getpass("Input Password : ")
        self.SCROLL_NUM = 10
        
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(executable_path=driver_loc, options = options)

        self.login()


    def login(self):
        self.driver.get("https://www.instagram.com/accounts/login/")

        if self.driver.current_url == "https://www.instagram.com/":
            print("You already loged in")
            return None
        
        username_form = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
        username_form.send_keys(self.__USERNAME)

        password_form = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
        password_form.send_keys(self.__PASSWORD)

        login_button = self.driver.find_element(By.XPATH, "//button[@class='sqdOP  L3NKy   y3zKF     ']")
        login_button.click()
        
        print("로그인 완료")

        self.driver.implicitly_wait(10)

        # 로그인 정보 저장 팝업 스킵
        time.sleep(5)
        # if self.driver.current_url == "https://www.instagram.com/accounts/onetap/?next=%2F":
        #     print("로그인 정보 저장 팝업 스킵")
        #     skip_save_button = self.driver.find_element(By.XPATH, "//button[@class='sqdOP yWX7d    y3zKF     ' or contains(text(), '나중에 하기')]")
        #     skip_save_button.click()

        # # # 알림 설정 팝업 스킵
        # try:
        #     print("알림 설정 팝업 스킵")
        #     skip_alarm_button = driver.find_element(By.XPATH, "//button[@class='aOOlW   HoLwm ' or contains(text(), '나중에 하기')]")
        #     skip_alarm_button.click()
        # except NoSuchElementException:
        #     pass

        search_bar = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class=' QY4Ed P0xOK']")))
        

    
    def search_tag(self, tag):
        # 검색
        self.driver.get(f"https://www.instagram.com/tags/{tag}/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div/h1[@class='_7UhW9       fKFbl yUEEX    KV-D4           uL8Hv         ']")))

        # 스크롤
        for _ in range(self.SCROLL_NUM):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)

        # 게시물 post들의 url 수집
        post_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '/p/')]")
        post_urls = [x.get_attribute("href") for x in post_elems]

        return list(set(post_urls))
    


    # 이미지 url
    def collect_img_urls(self):
        self.img_urls = []
        while True:
            img_elems = self.driver.find_elements(By.XPATH, "//div[@class='KL4Bh']/img")
            self.img_urls.extend([x.get_attribute("src") for x in img_elems])

            # 한 포스트에 사진이 여러개 있는 경우 오른쪽 버튼을 눌러 사진 수집
            # slide_right_button = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//button[@class='  _6CZji   ']")))
            slide_right_button = self.driver.find_elements(By.XPATH, "//button[@class='  _6CZji    ']") # 존재하지 않는 Element를 찾을 때 시간이 오래걸림..
            if len(slide_right_button) != 0:
                slide_right_button[0].click()
            else:
                break
        
        self.img_urls = list(set(self.img_urls))

        return self.img_urls



    def collect_text(self):
        text_dict = defaultdict(list)
        # 작성자 이름
        writer_name = self.driver.find_element(By.XPATH, "//a[@class='sqdOP yWX7d     _8A5w5   ZIAjV ']").text

        # 작성글
        try:
            post_body = self.driver.find_element(By.XPATH, "//div[@class='MOdxS ']/span").text
        except:
            post_body = None

        # 좋아요
        try:
            like = self.driver.find_element(By.XPATH, "//div[@class='_7UhW9   xLCgt        qyrsm KV-D4               fDxYl    T0kll ']/span").text
        except:
            like = None

        # 날짜
        post_date = self.driver.find_element(By.XPATH, "//time[@class='_1o9PC']").get_attribute("datetime")

        text_dict["writer_name"] = writer_name
        text_dict["post_body"] = post_body
        text_dict["like"] = like
        text_dict["post_date"] = post_date

        return text_dict



    def save_images(self, img_urls, img_names, img_dir = "./image/"):
        
        if img_dir is None:
            img_dir = f"./image/"
        
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        self.error_list = []
        for img_url, img_name in zip(img_urls, img_names):
            # image 저장
            try:
                img_rq = requests.get(img_url, verify = True)
                with open(f"{img_dir}/{img_name}", "wb") as f:
                    f.write(img_rq.content)
            except Exception as e: 
                print(e)
                self.error_list.append(img_name)
                print(img_name)



    def collect_insta(self, tags, img_dir = None):
        if not isinstance(tags, list):
            self.tags = [tags]
        else:
            self.tags = tags
        
        
        self.text_dict = defaultdict(list)
        # Tag가 여러개 들어오면 1개씩 Loop로 수집
        for tag in self.tags:

            img_dir = os.path.join("./image", tag)
            post_urls = self.search_tag(tag)
            print(f"Tag : {tag}, # of URL : {len(post_urls)}")
            # 각 Post마다 방문해서 이미지 링크 수집
            for i, url in enumerate(post_urls):
                print(i, end = ",")
                self.driver.get(url)

                # 이미지 url 수집
                img_urls = self.collect_img_urls()
                # 이미지가 없으면 해당 게시물은 skip (동영상인 경우도 스킵)
                if len(img_urls) == 0:
                    continue
                
                # post 내의 텍스트 수집
                self.texts_in_post = self.collect_text()

                self.text_dict["tag"].append(tag)
                self.text_dict["writer_name"].append(self.texts_in_post["writer_name"])
                self.text_dict["post_body"].append(self.texts_in_post["post_body"])
                self.text_dict["like"].append(self.texts_in_post["like"])
                self.text_dict["post_date"].append(self.texts_in_post["post_date"])
                self.text_dict["url"].append(url)

                img_names = [f"{tag}_{self.texts_in_post['writer_name']}_{self.texts_in_post['post_date'].split('T')[0]}_img_{str(n+1)}.jpg" for n in range(len(img_urls))]
                self.text_dict["images"].append(img_names)

                self.save_images(img_urls, img_names, img_dir)

            print("", end = "\n")
            # Excel로 저장                    
            pd.DataFrame(self.text_dict).to_excel(f"{tag}.xlsx", index = False, encoding = "CP949")

        return self.text_dict