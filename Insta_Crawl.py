import requests
# from bs4 import BeautifulSoup
import time as time
import urllib.request
import random
from getpass import getpass
import os
from collections import defaultdict
import pandas as pd
import numpy as np
from datetime import datetime


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

        login_button = self.driver.find_elements(By.XPATH, "//div[contains(text(), '로그인')]")[0]
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


    def get_feed_urls_from_search_result(self):
        feed_urls = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        retry_count = 0  # 로딩이 되지 않을 때 사용할 카운트
        MAX_RETRIES = 3  # 새로고침 전 시도 횟수

        while True:
            # 스크롤을 맨 아래로 내림
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # 10초 대기, 페이지 로딩 대기
            time.sleep(2)
            
            # 새로운 페이지 높이를 확인하여 스크롤이 끝났는지 체크
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # 새로운 콘텐츠가 로드되지 않았을 때
            if new_height == last_height:
                retry_count += 1
                
                if retry_count >= MAX_RETRIES:
                    # 최대 시도 횟수를 넘었으면 페이지 새로고침
                    print("최대 시도 횟수 도달, 페이지를 새로고침합니다.")
                    self.driver.refresh()
                    time.sleep(1)  # 새로고침 후 페이지 로드 대기
                    # feed_urls = []  # URL 리스트 초기화
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                    retry_count = 0  # 시도 카운트 초기화
                    continue
                else:
                    # 잠깐 위로 스크롤했다가 다시 아래로 스크롤
                    print("로딩되지 않음, 살짝 위로 스크롤 후 다시 아래로.")
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
                    time.sleep(1)  # 잠시 대기
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # 다시 로딩 대기
            else:
                retry_count = 0  # 로딩이 성공적으로 되었으므로 시도 카운트 초기화

            last_height = new_height
            
            # 새로운 피드 요소 찾기
            feed_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '/p/')]")
            
            # 중복된 URL이 있을 수 있으므로 리스트에 추가하기 전에 필터링
            for elem in feed_elems:
                url = elem.get_attribute("href")
                if url not in feed_urls:
                    feed_urls.append(url)

        return feed_urls
    

    # 이미지 url
    def collect_img_urls(self):
        self.img_urls = []
        while True:
            img_elems = self.driver.find_elements(By.XPATH, "//div[@class='KL4Bh']/img")
            self.img_urls.extend([x.get_attribute("src") for x in img_elems])

            # 한 포스트에 사진이 여러개 있는 경우 오른쪽 버튼을 눌러 사진 수집
            # slide_right_button = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//button[@class='  _6CZji   ']")))
            # self.driver.find_elements(By.XPATH, f"//button[@aria-label='돌아가기']")[0]
            slide_right_button = self.driver.find_elements(By.XPATH, f"//button[@aria-label='다음']")[0] # 존재하지 않는 Element를 찾을 때 시간이 오래걸림..
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
    
    
    
class Insta_Selenium:
    def __init__(self):
        self.__USERNAME = input("Input Instagram ID : ")
        self.__PASSWORD = getpass("Input Password : ")
        # self.SCROLL_NUM = 10
        
        chrome_options = webdriver.chrome.options.Options()
        # chrome_options.add_argument("--headless")  # GUI 없이 실행하려면 이 옵션을 추가
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")


        self.driver = webdriver.Chrome(options=chrome_options)
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

        login_button = self.driver.find_element(By.XPATH, "//div[contains(text(), '로그인')]")
        login_button.click()
        
        print("로그인 완료")

        self.driver.implicitly_wait(10)

        # 로그인 정보 저장 팝업 스킵
        time.sleep(5)
        
        
        
        
class Insta_Element_Extractor(Insta_Selenium):
    BASE_URL1 = "https://www.instagram.com/p/DBaGhj_zFHyIK6HrI8opezoT7b5Y5sWqN06qNI0/" # single_images
    BASE_URL2 = "https://www.instagram.com/p/DBaNfq0zVFNYtwOlTz6yeZ09AqL-fNPhEO1qgM0" # multi_images
    BASE_URL3 = "https://instagram.com/p/BmixoeJhHqP/" # video
    
    def __init__(self):
        super().__init__()
        
    
    def extract_nickname_elements(self):
        self.driver.get(self.BASE_URL1)
        nickname_elems = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'goodmytoy')]")
        nickname_classnames = [elem.get_attribute("class") for elem in nickname_elems if elem.text == "goodmytoy"]
        if len(set(nickname_classnames)) == 1:
            nickname_classname = nickname_classnames[0]
            
        # tag_name = nickname_elems[0].tag_name
        tag_name = "span"
            
        return {"tag_name" : tag_name, "classname" : nickname_classname}
    
    def extract_contents_elements(self):
        self.driver.get(self.BASE_URL1)
        contents_elems = self.driver.find_elements(By.XPATH, "//span[contains(text(), '사슴이')]")
        contents_classnames = [elem.get_attribute("class") for elem in contents_elems if elem.text == "사슴이"]
        if len(set(contents_classnames)) == 1:
            contents_classname = contents_classnames[0]       
            
        tag_name = "span"
        
        return {"tag_name" : tag_name, "classname" : contents_classname}
    
    def extract_like_count_elements(self):
        self.driver.get(self.BASE_URL1)
        like_count_elems = self.driver.find_elements(By.XPATH, "//span[contains(text(), '좋아요')]")
        if len(like_count_elems) > 0:
            like_count_classname = [elem.get_attribute("class") for elem in like_count_elems][0]
            tag_name = "span"
        
        return {"tag_name" : tag_name, "classname" : like_count_classname}
    
    def extract_view_count_elements(self):
        self.driver.get(self.BASE_URL3)
        view_count_elems = self.driver.find_elements(By.XPATH, "//span[contains(text(), '조회')]")
        
        if len(view_count_elems) > 0:
            view_count_classname = [elem.get_attribute("class") for elem in view_count_elems][0]
            view_count_tag_name = "span"
            
            view_count_elems[0].click()
            
            like_count_elems = self.driver.find_elements(By.XPATH, "//div[contains(text(), '좋아요')]")
            
            if len(like_count_elems) > 0:
                like_count_classname = [elem.get_attribute("class") for elem in like_count_elems][0]
                like_count_tag_name = "div"
            
        return {"view_tag_name" : view_count_tag_name, "view_classname" : view_count_classname,
                "like_tag_name" : like_count_tag_name, "like_classname" : like_count_classname}
    
    
    def extract_datetime_elements(self):
        self.driver.get(self.BASE_URL1)
        datetime_elems = self.driver.find_elements(By.XPATH, "//time[contains(@datetime, '2024-10-22T01:23:21.000Z')]")
        
        if len(datetime_elems) > 0:
            datetime_classname = datetime_elems[0].get_attribute("class")
            datetime_tag_name = "time"
        
        return {"tag_name" : datetime_tag_name, "classname" : datetime_classname}
    
    def extract_image_elements(self):
        self.driver.get(self.BASE_URL2)
        image_elems = self.driver.find_elements(By.XPATH, f"//img[@alt='Photo by Goodmytoy on October 21, 2024. 사진 설명이 없습니다..']")[0]
        image_classname = image_elems.get_attribute("class")
        image_parent_classname = image_elems.find_elements(By.XPATH, "../../../..")[0].get_attribute("class")
        image_parent_tag_name = "div"
        image_tag_name = "img"
        
        return {"parent_tag_name": image_parent_tag_name, "parent_classname":image_parent_classname,
                "tag_name" : image_tag_name, "classname" : image_classname}
        
    
    
    def extract(self):
        self.driver.get(self.BASE_URL1)
        nickname_elements = self.extract_nickname_elements()
        contents_elements = self.extract_contents_elements()
        like_count_elements = self.extract_like_count_elements()
        datetime_elements = self.extract_datetime_elements()
        image_elements = self.extract_image_elements()
        view_count_elements = self.extract_view_count_elements()
        
        return {"nickname" : nickname_elements,
                "contents" : contents_elements,
                "like_count" : like_count_elements,
                "view_count" : view_count_elements,
                "datetime" : datetime_elements,
                "image" : image_elements}
        
    def close(self):
        self.driver.close()
        
        
class Insta_Tag_Feed_Crawler(Insta_Selenium):
    def __init__(self, insta_elements):
        super().__init__()
        self.insta_elements = insta_elements
        
    def search_tag(self, tag):
        # 검색
        self.driver.get(f"https://www.instagram.com/tags/{tag}/")
    
    def get_feed_urls_from_search_result(self, tag):
        self.search_tag(tag = tag)
        
        self.feed_urls = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        retry_count = 0  # 로딩이 되지 않을 때 사용할 카운트
        MAX_RETRIES = 3  # 새로고침 전 시도 횟수
        END_FLAG = False
        SCROLL_COUNT = 0
        
        while True:
            
            # 새로운 피드 요소 찾기
            
            feed_elems = self.driver.find_elements(By.XPATH, "//*[contains(@href, '/p/')]")
            
            # 중복된 URL이 있을 수 있으므로 리스트에 추가하기 전에 필터링
            for elem in feed_elems:
                url = elem.get_attribute("href")
                if url not in self.feed_urls:
                    self.feed_urls.append(url)
                else:
                    if (self.feed_urls.index(url) == 0) & (SCROLL_COUNT > 3):
                        END_FLAG = True
                    
            # print(SCROLL_COUNT)
            # if SCROLL_COUNT > 5:
            #     break
            
            if END_FLAG:
                break
                            
            # 스크롤을 맨 아래로 내림
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # 10초 대기, 페이지 로딩 대기
            time.sleep(2)
            
            # 새로운 페이지 높이를 확인하여 스크롤이 끝났는지 체크
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # 새로운 콘텐츠가 로드되지 않았을 때
            if new_height == last_height:
                retry_count += 1
                
                if retry_count >= MAX_RETRIES:
                    # 최대 시도 횟수를 넘었으면 페이지 새로고침
                    print("최대 시도 횟수 도달, 페이지를 새로고침합니다.")
                    self.driver.refresh()
                    time.sleep(1)  # 새로고침 후 페이지 로드 대기
                    # feed_urls = []  # URL 리스트 초기화
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                    retry_count = 0  # 시도 카운트 초기화
                    continue
                else:
                    # 잠깐 위로 스크롤했다가 다시 아래로 스크롤
                    print("로딩되지 않음, 살짝 위로 스크롤 후 다시 아래로.")
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
                    time.sleep(1)  # 잠시 대기
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # 다시 로딩 대기
            else:
                retry_count = 0  # 로딩이 성공적으로 되었으므로 시도 카운트 초기화

            last_height = new_height
            SCROLL_COUNT += 1
                    
        return self.feed_urls
    
    def _get_feed_nickname(self):
        tag_name = self.insta_elements.get("nickname").get("tag_name")
        classname = self.insta_elements.get("nickname").get("classname")
        
        nickname = self.driver.find_element(
            By.XPATH, 
            f"//{tag_name}[@class='{classname}']"
        ).text
        
        return nickname
    
    def _get_feed_contents(self):
        tag_name = self.insta_elements.get("contents").get("tag_name")
        classname = self.insta_elements.get("contents").get("classname")
        
        contents_elems = self.driver.find_elements(
            By.XPATH, 
            f"//{tag_name}[@class='{classname}']"
        )
        
        if len(contents_elems) > 0:
            contents = contents_elems[0].text
        else:
            contents = None
        
        return contents
    
    def _define_view_like_type(self):
        view_like_type = None
        
        like_count_elems = self.driver.find_elements(By.XPATH, "//span[contains(text(), '좋아요')]")
        if len(like_count_elems) > 0:
            view_like_type = "like"
        
        else:
            view_count_elems = self.driver.find_elements(By.XPATH, "//span[contains(text(), '조회')]")
            if len(view_count_elems) > 0:
                view_like_type = "view_like"
            else:
                view_like_type = "like"
        
        return view_like_type
            
    def _get_like_count(self):
        tag_name = self.insta_elements.get("like_count").get("tag_name")
        classname = self.insta_elements.get("like_count").get("classname")
        
        like_elems = self.driver.find_elements(
            By.XPATH, 
            f"//{tag_name}[@class='{classname}']"
        )
        
        if len(like_elems) > 0:
            like_count_text = like_elems[0].text
            like_count = like_count_text.replace("좋아요 ", "").replace("개", "")
        else:
            like_count = 0
            
        try:
            like_count = int(like_count)
        except:
            like_count = None
        
        return like_count
    
    
    def _get_view_like_count(self):
        like_count_tag_name = self.insta_elements.get("view_count").get("like_tag_name")
        like_count_classname = self.insta_elements.get("view_count").get("like_classname")
        view_count_tag_name = self.insta_elements.get("view_count").get("view_tag_name")
        view_count_classname = self.insta_elements.get("view_count").get("view_classname")
        
        view_elems = self.driver.find_elements(By.XPATH, "//span[contains(text(), '조회')]")
        if len(view_elems) > 0:
            view_elems[0].click()
            
            like_elems = self.driver.find_elements(By.XPATH, f"//{like_count_tag_name}[@class='{like_count_classname}']")
            
            if len(like_elems) > 0:
                view_count = view_elems[0].find_elements(By.XPATH, "span")[0].text
                like_count = like_elems[0].find_elements(By.XPATH, "span")[0].text
                
        return {"view_count" : view_count, "like_count" : like_count}
        
    
    def _get_feed_datetime(self):
        tag_name = self.insta_elements.get("datetime").get("tag_name")
        classname = self.insta_elements.get("datetime").get("classname")
        
        feed_datetime = self.driver.find_element(
            By.XPATH, 
            f"//{tag_name}[@class='{classname}']"
        ).get_attribute("datetime")
        
        return feed_datetime
    
    # 이미지 url
    def _get_image_urls(self):
        tag_name = self.insta_elements.get("image").get("tag_name")
        classname = self.insta_elements.get("image").get("classname")
        parent_tag_name = self.insta_elements.get("image").get("parent_tag_name")
        parent_classname = self.insta_elements.get("image").get("parent_classname")
        
        
        image_urls = []
        while True:
            
            image_elems = self.driver.find_elements(
                By.XPATH, 
                f"//{parent_tag_name}[@class='{parent_classname}']//{tag_name}[@class='{classname}']"
            )
            self.image_elems = image_elems
            
            for image_elem in image_elems:
                try:
                    image_src = image_elem.get_attribute("src")
                except:
                    continue
                
                if image_src in image_urls:
                    continue
                else:
                    image_urls.append(image_src)
            
            
                    
            # 한 포스트에 사진이 여러개 있는 경우 오른쪽 버튼을 눌러 사진 수집
            slide_right_button = self.driver.find_elements(By.XPATH, f"//button[@aria-label='다음']")
            if len(slide_right_button) != 0:
                slide_right_button[0].click()
            else:
                break

        return image_urls
        
    
    def get_feed_info(self, feed_url):
        
        feed_info = defaultdict(list)
        
        self.driver.get(feed_url)
        
        # start = datetime.now()
        nickname = self._get_feed_nickname()
        # print(f"nickname : {datetime.now() - start}")
        
        # start = datetime.now()
        contents = self._get_feed_contents()
        # print(f"contents : {datetime.now() - start}")
        
        # start = datetime.now()
        feed_datetime = self._get_feed_datetime()
        # print(f"feed_datetime : {datetime.now() - start}")
        
        # start = datetime.now()
        image_urls = self._get_image_urls()
        # print(f"image_urls : {datetime.now() - start}")
        
        # start = datetime.now()
        view_like_type = self._define_view_like_type()
        # print(f"_define_view_like_type : {datetime.now() - start}")
        print(f"view_like_type  : {view_like_type}")
        
        # start = datetime.now()
        if view_like_type == "like":
            like_count = self._get_like_count()
            view_count = None
        elif view_like_type == "view_like":
            view_like_count = self._get_view_like_count()
            view_count = view_like_count.get("view_count")
            like_count = view_like_count.get("like_count")
        # print(f"view_like_type : {datetime.now() - start}")
        
        
        feed_info["feed_url"] = feed_url
        feed_info["nickname"] = nickname
        feed_info["pocontentsst_body"] = contents
        feed_info["like_count"] = like_count
        feed_info["view_count"] = view_count
        feed_info["datetime"] = feed_datetime
        feed_info["image_urls"] = image_urls

        return feed_info        
    
    
    def get_feed_infos(self, feed_urls):    
        self.feed_infos = []
        for feed_url in feed_urls:
            self.feed_url = feed_url
            feed_info = self.get_feed_info(feed_url = feed_url)
            self.feed_infos.append(feed_info)
            
        return self.feed_infos
    
    def crawl(self, tags:list):
        if not isinstance(tags, list):
            self.tags = [tags]
        else:
            self.tags = tags
            
        
        for tag in tags:
            feed_urls = self.get_feed_urls_from_search_result(tag = tag)
        
        feed_infos = []
        for feed_url in feed_urls:
            feed_info = self.get_feed_info(feed_url = feed_url)
            feed_infos.append(feed_info)
            
        return feed_infos
            
        
            
            