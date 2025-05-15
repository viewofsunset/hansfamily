import multiprocessing
import time
import os 
import cv2
import signal
import uuid
import io
import datetime
import platform
import pickle
import random
import requests
import urllib

from django.db.models import Q, F, Func
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import close_old_connections
from django.db import connections

import pathlib
from pathlib import Path
from PIL import Image
from PIL import ImageSequence
from pdf2image import convert_from_path

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import pandas as pd

from celery import Celery
from celery import shared_task
from celery.schedules import crontab
# from celery.signals import worker_process_init
from billiard import Pool, TimeoutError 

app = Celery()

from study.models import *




"""
Paper 검색 -> 저장 -> 표시 -> 학습 -> 질의응답


<< 검색 Request에서 바로 생성 >>
pubmed 서치시 저장되는 list_dict_paper_info_from_pubmed 내용 중 1번째
    Model: Paper_Search_Google_and_PubMed 
    Field: list_dict_paper_info_from_pubmed =
    [
        {
            "id": 0, 
            "doi": "10.1186/s12961-021-00801-2", 
            "pmcid": "PMC8743061", 
            "title": "“There hasn’t been a career structure to step into”: a qualitative study on perceptions of allied health clinician researcher careers", 
            "keyword": "career researchers pathways", 
            "pdf_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8743061/pdf/12961_2021_Article_801.pdf", 
            "article_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8743061/?report=classic", 
            "abstract_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8743061/?report=abstract", 
            "journal_name": "Health Res Policy Syst. 2022; 20: 6.  Published online 2022 Jan 9. doi: 10.1186/s12961-021-00801-2", 
            "publication_year": 2022, 
            "full_author_name": "Caitlin Brandenburg, Elizabeth C. Ward"
        }, 
        {},{},{}.
    ]

    
<< Celery Task A 코스 >>
pubmed 서치 결과에 대해 background paper 쿼리 생성시 저장되는 내용
    Model: Paper
    {
        'hashcode': hashcode, 
        'title': title, 
        'doi': doi, 
        'doi_url': doi_url, 
        'pmcid': pmcid, 
        'pmid': None,
        'first_author_name': None, 
        'first_author_url': None, 
        'file_path_xml': None, 
        'file_path_pdf': pdf_name, 
        'publication_year': publication_year,
        'dict_paper_info': {
            "keyword": "career researchers pathways", 
            "pdf_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10019401/pdf/10775_2023_Article_9590.pdf", 
            "article_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10019401/?report=classic", 
            "abstract_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10019401/?report=abstract", 
            "pmc_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10019401",
            "pubmed_url": , 
            "journal_name": "Int J Educ Vocat Guid. 2023 Mar 16 : 1–26.  doi: 10.1007/s10775-023-09590-2 [Epub ahead of print]", 
            "publication_year": publication_year,
            "full_author_name": full_author_name,
        }
    }

    
<< Celery Task B 코스 >>
이후 리스트 중 하나의 Paper 선택하면 선택된 해당 Paper에 대한 다양한 정보 수집 
    # Paper Query 생성시 필요 데이터 포맷:  (Reference, Relevant, Author Paper 생성시 B 모두 코스에서 생성)
        hashcode            <- A 코스에서 획득
        title               <- A 코스에서 획득
        doi                 <- A 코스에서 획득
        doi_url             <- A 코스에서 획득
        pmcid               <- A 코스에서 획득
        pmid                <- B 코스에서 획득
        first_author_name   <- B 코스에서 획득
        first_author_url    <- B 코스에서 획득
        file_path_xml *      
        file_path_pdf       <- A 코스에서 획득
        publication_year    <- A 코스에서 획득 
        dict_paper_info **  <- A, B 모두 획득
        
        # dict_paper_info에 들어가는 포맷
            dict_paper_info['title'] = title 
            dict_paper_info['parsing_url'] = parsing_url
            dict_paper_info['list_dict_author_info'] = list_dict_author_info
                # Author 정보
                list_dict_author_info = [{
                    'author_name': author_name,
                    'author_url': author_url,
                }]
            dict_paper_info['pmid'] = pmid
            dict_paper_info['pubmed_url'] = pubmed_url  # Pubmed 기사 실린 곳 url
            dict_paper_info['pmcid'] = pmcid
            dict_paper_info['pubmed_free_url'] = pubmed_free_url  # PMC 기사 실린 곳 url
            dict_paper_info['abstract_html'] = abstract_html # Abstract 정보는 HTML Tag 포함 Raw 데이터 저장
            dict_paper_info['abstract_text'] = abstract_text # 순수 TEXT
            dict_paper_info['pdf_url'] = pdf_url  # PDF 다운로드 URL
            dict_paper_info['journal_name'] = journal_name
            dict_paper_info['article_url'] = article_url  # paper가 실린 곳 Journal의 기사 url
            dict_paper_info['publisher_name'] = publisher_name
            dict_paper_info['full_author_name'] = full_author_name
        
        # list_dict_reference_paper에 들어가는 포맷 
            list_dict_reference_paper 정보는 검색된 Paper를 정보 수집 버튼을 눌렀을 때 1차 수집되는 정보(Paper와 연결된 Reference 정보) 포맷
            list_dict_reference_paper.append({
                'id': n,
                'q_paper_id': None,
                'cite': r_cite,
                'doi': r_doi_link,
                'pubmed_url': r_pubmed_link,
                'pubmed_free_url': r_pubmed_free_link,
                'google_scholar_url': r_google_scholar_link,
            })

        # list_dict_author_paper 들어가는 포맷 
            dict_paper_info['list_dict_author_paper'] = list_dict_author_paper
                # list_dict_author_paper 정보는 ...
                list_dict_author_paper.append({
                    'id': n,
                    'q_paper_id': None,
                    'cite': r_cite,
                    'doi': r_doi_link,
                    'pubmed_url': r_pubmed_link,
                    'pubmed_free_url': r_pubmed_free_link,
                    'google_scholar_url': r_google_scholar_link,
                })

        # list_dict_relevant_paper 들어가는 포맷 
            dict_paper_info['list_dict_relevant_paper'] = list_dict_relevant_paper
                # list_dict_relevant_paper 정보는 ...
                list_dict_relevant_paper.append({
                    'id': n,
                    'q_paper_id': None,
                    'cite': r_cite,
                    'doi': r_doi_link,
                    'pubmed_url': r_pubmed_link,
                    'pubmed_free_url': r_pubmed_free_link,
                    'google_scholar_url': r_google_scholar_link,
                })

"""
# Get Random Info for Chrome Driver Header 
def get_random_header():
    list_browser_headers = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Referer": "https://pmc.ncbi.nlm.nih.gov/",
        },
        {
            "User-Agent": "Mozilla/5.0(Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.3",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Referer": "https://pmc.ncbi.nlm.nih.gov/",
        },
        {
            "User-Agent": "Mozilla/5.0(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Referer": "https://pmc.ncbi.nlm.nih.gov/",
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Connection": "keep-alive",
            "Referer": "https://pmc.ncbi.nlm.nih.gov/",
        },
    ]

    num_browser_headers = len(list_browser_headers)
    num_header_selected = random.randint(1, num_browser_headers) - 1
    header_selected = list_browser_headers[num_header_selected]
    return header_selected


# Get Proxy 
def get_proxy():
    proxy_port = random.randint(10001, 11000)
    proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{proxy_port}"

    # # Fine proxy (Factory)
    # proxy_port = LIST_PORT_FINEPROXY[n]
    # proxy = f"http://{FINEPROXY_USER_NAME}:{FINEPROXY_USER_PASSWORD}@FINEPROXY.XYZ:{proxy_port}"

    return proxy


# Chrome Driver 띄우기
def boot_google_chrome_driver_in_study_tasks(check_proxy):
    print(f'# Chrome Driver 띄우기, Proxy: {check_proxy}')
    os_name = platform.system()
    # Check if the OS is Linux or Windows
    if os_name == 'Linux':
        # print("The operating system is Linux.")
        CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
        
        service = Service(executable_path=CHROME_DRIVER_PATH)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        if check_proxy == True:
            proxy = get_proxy()
            chrome_options.add_argument(f'--proxy-server={proxy}')
        driver = webdriver.Chrome(service=service, options=chrome_options)
    elif os_name == 'Windows':
        # print("The operating system is Windows.")
        driver = webdriver.Chrome()
    return driver 


# Chrome Driver 띄우기
def boot_google_chrome_driver(n, check_proxy):
    print(f'# Chrome Driver 띄우기, number of n: {n}')
    os_name = platform.system()
  
    # Check if the OS is Linux or Windows
    if os_name == 'Linux':
        # print("The operating system is Linux.")
        CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
        service = Service(executable_path=CHROME_DRIVER_PATH)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        if check_proxy == True:
            proxy = get_proxy(n)
            chrome_options.add_argument(f'--proxy-server={proxy}')

        driver = webdriver.Chrome(service=service, options=chrome_options)
    elif os_name == 'Windows':
        # print("The operating system is Windows.")
        driver = webdriver.Chrome()
    return driver 


# Default Picture Album 쿼리 생성
def create_paper_in_task():
    random_uuid = uuid.uuid4()
    hashcode = str(random_uuid)
    data = {
        'hashcode': hashcode,
    }
    q_paper = Paper.objects.create(**data)
    print('q_paper 신규 생성!')
    return q_paper


# Define timeout exception
class TimeoutException_paper_download(Exception):
    print('timeout occurred. 1')
    pass


# Define the timeout handler
def timeout_handler_paper_download(signum, frame):
    print('timeout occurred. 2' )
    # raise TimeoutException_paper_download("Timeout: f_a exceeded the time limit.")
    return False


def get_soup_using_various_try(parsing_url, site_name, n):
    # parsing_url : target URL
    # site_name : PMC / Pubmed / Google
    # n : Proxy Port Index

    random_sec = random.uniform(3, 5)
    check_driver = False
    site_available = False
    
    # check site is working
    def check_availability_site_parsing(site_name, check_proxy):
        if site_name == 'pubmed_free':
            TEST_URL = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7596871/'
        elif site_name == 'pubmed':
            TEST_URL = 'https://pubmed.ncbi.nlm.nih.gov/38550700/'
        elif site_name == 'google_scholar':
            TEST_URL = "https://scholar.google.com/scholar_lookup?journal=J.%20Am.%20Chem.%20Soc.&title=Solid%20phase%20peptide%20synthesis.%20I.%20The%20synthesis%20of%20a%20tetrapeptide&author=R.%20B.%20Merrifield&volume=85&issue=14&publication_year=1963&pages=2149-2154&doi=10.1021/ja00897a025&"
        else:
            return False, False
        check_driver = False
        site_available = False
        # 1. Test용 Soup 확보하기
        headers = get_random_header()
        if check_proxy == True:
            # try proxy server
            PROXY_PORT = LIST_PORT_SMARTPROXY[n]
            proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{PROXY_PORT}"
            response = requests.get(TEST_URL, proxies={
                'http': proxy,
                'https': proxy
            })
        else:
            response = requests.get(TEST_URL, headers=headers)
        time.sleep(random_sec)
        if response.status_code == 200:
            source = response.content
            soup = BeautifulSoup(source, 'html.parser')
        else:
            driver = boot_google_chrome_driver(n, check_proxy)
            time.sleep(random_sec)
            driver.get(TEST_URL)
            time.sleep(random_sec)
            source = driver.page_source
            soup = BeautifulSoup(source, 'html.parser')
            check_driver = True
            
        # 2. PDF URL 확보여부로 사이트 이용가능 여부 판단. (Test용 Soup 확보한 상태)
        pdf_url = None
        if site_name == 'pubmed_free':
            try:
                pdf_element = soup.find('section', class_='pmc-sidenav__container')
                pdf_url_elements = pdf_element.find_all('a', class_='usa-button')
                for pdf_url_element in pdf_url_elements:
                    try:
                        pdf_url_text = pdf_url_element['href']
                    except:
                        pdf_url_text = None 
                    if pdf_url_text is not None and 'pdf' in pdf_url_text:
                        pdf_url = True
                        break
            except:
                pass
        if site_name == 'pubmed':
            pdf_site_url = None
            list_dict_pdf_link_url = []
            pdf_element = soup.find('div', class_='full-text-links-list')
            pdf_link_elements = pdf_element.find_all('a', class_='link-item')
            for pdf_link_element in pdf_link_elements:
                pdf_link_text = pdf_link_element.get_text().strip()
                pdf_link_url = pdf_link_element['href']
                list_dict_pdf_link_url.append({'site_name': pdf_link_text, 'site_url': pdf_link_url})
            if len(list_dict_pdf_link_url) > 0:
                for dict_pdf_link_url in list_dict_pdf_link_url:
                    if dict_pdf_link_url['site_name'] == 'Free PMC article':
                        pdf_site_url = dict_pdf_link_url['site_url']
            if pdf_site_url is not None:
                # PDF 정보가 있는 사이트 Source 확보하기
                headers = get_random_header()
                if check_proxy == True:
                    # try proxy server
                    PROXY_PORT = LIST_PORT_SMARTPROXY[n]
                    proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{PROXY_PORT}"
                    response = requests.get(pdf_site_url, proxies={
                        'http': proxy,
                        'https': proxy
                    })
                else:
                    response = requests.get(pdf_site_url, headers=headers)
                time.sleep(random_sec)
                if response.status_code == 200:
                    source = response.content
                    soup = BeautifulSoup(source, 'html.parser')
                else:
                    driver = boot_google_chrome_driver(n, check_proxy)
                    time.sleep(random_sec)
                    driver.get(pdf_site_url)
                    time.sleep(random_sec)
                    source = driver.page_source
                    soup = BeautifulSoup(source, 'html.parser')
                    check_driver = True
                
                # Get PMC PDF Downlaod URL
                pdf_element = soup.find('section', class_='pmc-sidenav__container')
                pdf_url_elements = pdf_element.find_all('a', class_='usa-button')
                for pdf_url_element in pdf_url_elements:
                    try:
                        pdf_url_text = pdf_url_element['href']
                    except:
                        pdf_url_text = None 
                    if pdf_url_text is not None and '.pdf' in pdf_url_text:
                        pdf_url = True 
                        break
        if site_name == 'google_scholar':
            try:
                pdf_element = soup.find('div', class_='gs_or_ggsm')
                pdf_element_text = pdf_element.get_text()
                if '[PDF]' in pdf_element_text:
                    pdf_element_text = pdf_element_text.replace('[PDF]', '')
                pdf_url_text = pdf_element.find('a')['href']
            except:
                pdf_url_text = None
            if pdf_url_text is not None and '.pdf' in pdf_url_text:
                pdf_url = True 
        if pdf_url == True:
            site_available = True
        return site_available, check_driver

    # Check Site Availability
    site_available, check_driver = check_availability_site_parsing(site_name, False) 
    if site_available == False:
        site_available, check_driver = check_availability_site_parsing(site_name, True) 

    # Get Target URL SOUP
    if site_available == True:
        if check_driver == False:
            # get Target site Source
            headers = get_random_header()
            response = requests.get(parsing_url, headers=headers)
            time.sleep(random_sec)
            if response.status_code == 200:
                source = response.content
                soup = BeautifulSoup(source, 'html.parser')
            else:
                driver = boot_google_chrome_driver_in_study_tasks(n)
                time.sleep(random_sec)
                driver.get(parsing_url)
                time.sleep(random_sec)
                source = driver.page_source
                soup = BeautifulSoup(source, 'html.parser')
                check_driver = True
        else:
            driver.get(parsing_url)
            time.sleep(random_sec)
            source = driver.page_source
            soup = BeautifulSoup(source, 'html.parser')
    else:
        soup = None
    if check_driver == True:
        driver.quit()
    return soup


    # if response.status_code != 200:
    #     PROXY_PORT = LIST_PORT_FINEPROXY[n]
    #     proxy = f"http://{FINEPROXY_USER_NAME}:{FINEPROXY_USER_PASSWORD}@FINEPROXY.XYZ:{PROXY_PORT}"
    #     response = requests.get(parsing_url, proxies={
    #         'http': proxy,
    #         'https': proxy
    #     })
    #     if response.status_code != 200:
    #         PROXY_PORT = LIST_PORT_SMARTPROXY[n]
    #         proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{PROXY_PORT}"
    #         response = requests.get(parsing_url, proxies={
    #             'http': proxy,
    #             'https': proxy
    #         })
            
    #         else:
    #             # Smartproxy request
    #             print(f" Success in Smartproxy Request Status code: {response.status_code}")
    #             source = response.content
    #             soup = BeautifulSoup(source, 'html.parser')
    #         print(f"Failed to access given article url using Fineproxy Request. Status code: {response.status_code}")
    #     else:
    #         # Fineproxy request
    #         print(f" Success in Fineproxy Request Status code: {response.status_code}")
    #         source = response.content
    #         soup = BeautifulSoup(source, 'html.parser')
    #     print(f"Failed to access given article url using Ordinary Request. Status code: {response.status_code}")
    # else:
    #     # Ordinary request
    #     print(f" Success in Ordinary Request Status code: {response.status_code}")
    #     source = response.content
    #     soup = BeautifulSoup(source, 'html.parser')
    

def get_soup_using_url_only(parsing_url):
    random_sec = random.uniform(5, 7)
    # Source Type 2
    headers = get_random_header()
    response = requests.get(parsing_url, headers=headers)
    time.sleep(random_sec)
    if response.status_code == 200:
        print('Done Requests')
        source = response.content
        soup = BeautifulSoup(source, 'html.parser')
    else:
        print('forbidden by Requests')
        try:
            proxy_port = random.randint(10001, 11000)
            proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{proxy_port}"
            response = requests.get(parsing_url, proxies = {
                'http': proxy,
                'https': proxy
            })
            if response.status_code == 200:
                print('Done Proxy Requests')
                source = response.content
                soup = BeautifulSoup(source, 'html.parser')
            else:
                print('forbidden by Proxy Requests')
                soup = None
        except:
            soup = None
    return soup

#############################################################################################################################################
#############################################################################################################################################
#
#                                           A-1: 키워드 활용, PubMed Free(PMC)에서 검색 정보 획득 
#
#############################################################################################################################################
#############################################################################################################################################


#--------------------------------------------------------------------------------------------------------------------------------------
# A-1. keyword_str 활용 Pubmed 검색하기
#--------------------------------------------------------------------------------------------------------------------------------------
@shared_task(time_limit=20000, soft_time_limit=19800)
def paper_keyword_search_on_pubmed(q_paper_search_id, keyword_str):
    """
        list_dict_paper_info_from_pubmed = {
            dict_paper_info_from_pubmed['id'] = i
            dict_paper_info_from_pubmed['keyword'] = keyword_str
            dict_paper_info_from_pubmed['title'] = title 
            dict_paper_info_from_pubmed['doi'] = doi 
            dict_paper_info_from_pubmed['doi_url'] = doi_url 
            dict_paper_info_from_pubmed['pmcid'] = pmcid 
            dict_paper_info_from_pubmed['journal_name'] = journal_name 
            dict_paper_info_from_pubmed['publication_year'] = publication_year 
            dict_paper_info_from_pubmed['first_author_name'] = first_author_name 
            dict_paper_info_from_pubmed['abstract_url'] = abstract_url
            dict_paper_info_from_pubmed['article_url'] = article_url
            dict_paper_info_from_pubmed['pdf_url'] = pdf_url
            dict_paper_info_from_pubmed['check_parsing'] = False
        }
    """
    print('# keyword_str 활용 senenium 이용한 Data Scraping on PubMed 시작')

    q_paper_search = Paper_Search_Google_and_PubMed.objects.get(id=q_paper_search_id)
    if q_paper_search is None:
        print('q_paper_search is None')
        return False
    else:
        list_dict_paper_info_from_pubmed = q_paper_search.list_dict_paper_info_from_pubmed
        if list_dict_paper_info_from_pubmed is None:
            list_dict_paper_info_from_pubmed = []

    # A-1-1. Pubmed Free에서 검색내용 Parsing, list_dict_paper_info_from_pubmed 생성
    if len(list_dict_paper_info_from_pubmed) == 0:
        print('# 2. 키워드 활용, PubMed Free(PMC)에서 검색 정보 획득 A-1 : 시작')
        start_time = time.time()  # Record the start time
        last_page = 1

        driver = boot_google_chrome_driver_in_study_tasks(None)
        random_sec = random.uniform(2, 4)
        DESTINATION_URL = 'https://pmc.ncbi.nlm.nih.gov/'
        # time.sleep(random_sec)

        driver.get(DESTINATION_URL)
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')
        # Find the search box using the name attribute and type the search query
        search_input = driver.find_element(By.ID, "pmc-search")
        # search_box = driver.find_element("class", "usa-input")  # The "q" is the name attribute of the Google search box
        search_input.send_keys(keyword_str)  # Enter your search query
        # Simulate pressing the Enter key to submit the search
        search_input.send_keys(Keys.RETURN)
        
        # 검색결과 소스확보
        time.sleep(random_sec)
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')   

        # Find the input tag and extract the "last" attribute
        input_tag = soup.find('input', {'id': 'pageno2'})
        last_page = input_tag['last']
        if last_page is not None:
            try:
                last_page_int = int(last_page)
            except:
                last_page_int = 1

        # 검색 첫 페이지 결과내용 파싱
        results = soup.find_all(class_="rprt")
        # time.sleep(random_sec)
        n = 0
        n, list_dict_paper_info_from_pubmed = collect_search_result_on_pubmed_free(n, results, list_dict_paper_info_from_pubmed, DESTINATION_URL, keyword_str)

        if last_page_int > 5:
            last_page_to_parse = 5
        else:
            last_page_to_parse = last_page_int
        
        p = 2
        while p < last_page_to_parse + 1:
            try:
                # Wait until the "Next" button is available and clickable
                wait = WebDriverWait(driver, 4)
                next_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'next')))
                # Click the "Next" button
                next_button.click()
                # Wait for 1 second to allow the next page to load
                time.sleep(1)
                # Get the page source after the click
                source = driver.page_source
                soup = BeautifulSoup(source, 'html.parser')   
                # 검색 첫 페이지 결과내용 파싱
                results = soup.find_all(class_="rprt")
                n, list_dict_paper_info_from_pubmed = collect_search_result_on_pubmed_free(n, results, list_dict_paper_info_from_pubmed, DESTINATION_URL, keyword_str)
                n = n + 1
            except Exception as e:
                print(f"Error: {e}")
            p = p + 1
        driver.quit()
        end_time = time.time()  # Record the end time
        processing_time = end_time - start_time  # Calculate the time difference
        print(f"Paper Search on PubMed Processed in {processing_time:.4f} seconds") 
    else:
        print('# 2. 키워드 활용, PubMed Free(PMC)에서 검색 정보 획득 A-1 : 완료')
        pass 
    
    # A-1-2. Pubmed 논문 검색 결과를 이용한 논문 PDF 다운로드 및 Paper 쿼리 생성
    if len(list_dict_paper_info_from_pubmed) > 0:
        data = {    
            'list_dict_paper_info_from_pubmed': list_dict_paper_info_from_pubmed,
        }
        Paper_Search_Google_and_PubMed.objects.filter(id=q_paper_search_id).update(**data)
        q_paper_search.refresh_from_db()
        
        download_paper_info_from_search_result_on_pubmed(q_paper_search_id, list_dict_paper_info_from_pubmed)
    else:
        print('# Pubmed Free 서치 결과가 없습니다.')



#--------------------------------------------------------------------------------------------------------------------------------------
# A-1-1. Pubmed Free에서 검색내용 Parsing
""" 
BASE_URL_PMC = 'https://www.ncbi.nlm.nih.gov/'

<div class="rprt">
    <div class="rprtnum">
        <label class="ui-helper-hidden-accessible" for="UidCheckBox8743061">Select item 8743061</label>
        <input id="UidCheckBox8743061" name="EntrezSystem2.PEntrez.PMC.Pmc_ResultsPanel.Pmc_RVDocSum.uid" sid="1" type="checkbox" value="8743061"/>
        <span>1.</span>
    </div>
    <div class="rslt">
        <div class="title">
            <a class="view" href="/pmc/articles/PMC8743061/" ref="ordinalpos=1&amp;ncbi_uid=8743061&amp;link_uid=8743061&amp;linksrc=docsum_title">
                “There hasn’t been a <b>career</b> structure to step into”: a qualitative study on perceptions of allied health clinician researcher careers
            </a>
        </div>
        <div class="supp">
            <div class="desc">
                Caitlin Brandenburg, Elizabeth C. Ward
            </div>
            <div class="details">
                Health Res Policy Syst. <span class="citation-publication-date">2022; </span>20: 6.  <span class="">Published online 2022 Jan 9. </span><span class="doi"><span>doi: </span>10.1186/s12961-021-00801-2</span>
            </div>
        </div>
        <div class="aux">
            <div class="resc">
                <dl class="rprtid"><dt>PMCID: </dt><dd>PMC8743061</dd></dl>
            </div>
        </div>
        <div class="aux">
            <div class="links">
                <a class="view" href="/pmc/articles/PMC8743061/?report=abstract" ref="ordinalpos=1&amp;ncbi_uid=8743061&amp;link_uid=8743061&amp;linksrc=docsum_title">
                    Abstract
                </a>
                <a class="view" href="/pmc/articles/PMC8743061/?report=classic" ref="ordinalpos=1&amp;ncbi_uid=8743061&amp;link_uid=8743061&amp;linksrc=docsum_title">
                    Article
                </a>

            </div>
        </div>
    </div>
</div>

"""
#--------------------------------------------------------------------------------------------------------------------------------------
def collect_search_result_on_pubmed_free(n, results, list_dict_paper_info_from_pubmed, DESTINATION_URL, keyword_str):
    print('# A-1-1. Pubmed Free에서 검색내용 Parsing, list_dict_paper_info_from_pubmed 생성')
    
    i = n
    for result in results:
        # print(i, result)
        dict_paper_info_from_pubmed = {}
        # Extract the title
        try:
            title_element = result.find('div', class_='title').find('a')
            title = title_element.text.strip()
        except:
            title = None
        # Extract Journal info
        try:
            journal_element = result.find('div', class_='details')
            journal_name = journal_element.text.strip()
        except:
            journal_name = None
        # Extract the publication year
        try:
            publication_element = result.find('span', class_='citation-publication-date')
            publication_year = int(publication_element.text.replace(';', '').strip())
        except:
            publication_year = None
        # Extract Author info
        try:
            author_element = result.find('div', class_='desc')
            full_author_name = author_element.text.strip()
        except:
            full_author_name = None
        # Extract the DOI
        try:
            doi_element = result.find('span', class_='doi')
            doi_text = doi_element.get_text()
            doi_text2 = doi_text.replace('doi:', '')
            doi_text3 = doi_text2.strip()
            doi = doi_text3
            doi_url = BASE_URL_DOI + doi
        except:
            doi = None
            doi_url = None
        # print(f'doi: {doi}, doi_url: {doi_url}')

        # Extract the PMCID
        try:
            pmcid_element = result.find('dl', class_='rprtid').find('dd')
            pmcid = pmcid_element.text.strip()
        except:
            pmcid = None
        # Extract the URLs (abstract, article, PDF)
        try:
            abstract_url = result.find('a', href=True, text='Abstract')['href']
            abstract_url = abstract_url.split('/pmc/')[-1]
        except:
            abstract_url = None
        try:
            article_url = result.find('a', href=True, text='Article')['href']
            article_url = article_url.split('/pmc/')[-1]
        except: 
            article_url = None
        # try:
        #     pdf_url = result.find('a', href=True, text=lambda t: 'PDF' in t)['href']
        #     pdf_url = pdf_url.split('/pmc/')[-1]
        # except TypeError:
        #     pdf_url = None  # Handle cases where the PDF link is missing
        try:
            a_tags = result.find_all('a', class_='view')
            pdf_url = None
            for a_tag in a_tags:
                if 'PDF' in a_tag.text:
                    pdf_url = a_tag['href']
                    pdf_url = pdf_url.split('/pmc/')[-1]
                    break
        except:
            pdf_url = None
        base_url = DESTINATION_URL
        if abstract_url is not None:
            abstract_url = base_url + abstract_url
        if article_url is not None:
            if base_url not in article_url:
                article_url = base_url + article_url
            else:
                article_url = article_url
        if pdf_url is not None:
            if base_url not in pdf_url:
                pdf_url = base_url + pdf_url
            else:
                pdf_url = pdf_url
        dict_paper_info_from_pubmed['id'] = i
        dict_paper_info_from_pubmed['keyword'] = keyword_str
        dict_paper_info_from_pubmed['title'] = title 
        dict_paper_info_from_pubmed['doi'] = doi 
        dict_paper_info_from_pubmed['doi_url'] = doi_url 
        dict_paper_info_from_pubmed['pmcid'] = pmcid 
        dict_paper_info_from_pubmed['journal_name'] = journal_name 
        dict_paper_info_from_pubmed['publication_year'] = publication_year 
        dict_paper_info_from_pubmed['full_author_name'] = full_author_name 
        dict_paper_info_from_pubmed['abstract_url'] = abstract_url
        dict_paper_info_from_pubmed['article_url'] = article_url
        dict_paper_info_from_pubmed['pdf_url'] = pdf_url
        dict_paper_info_from_pubmed['check_parsing'] = False
        list_dict_paper_info_from_pubmed.append(dict_paper_info_from_pubmed)
        i = i + 1

    return i, list_dict_paper_info_from_pubmed
        



#--------------------------------------------------------------------------------------------------------------------------------------
# A-1-2 Pubmed 논문 검색 결과를 이용한 논문 PDF 다운로드 및 Paper 쿼리 생성
"""
    << A 코스 - PMC >>
        list_dict_paper_info_from_pubmed = {
            dict_paper_info_from_pubmed['id'] = i
            dict_paper_info_from_pubmed['keyword'] = keyword_str
            dict_paper_info_from_pubmed['title'] = title 
            dict_paper_info_from_pubmed['doi'] = doi 
            dict_paper_info_from_pubmed['doi_url'] = doi_url 
            dict_paper_info_from_pubmed['pmcid'] = pmcid 
            dict_paper_info_from_pubmed['journal_name'] = journal_name 
            dict_paper_info_from_pubmed['publication_year'] = publication_year 
            dict_paper_info_from_pubmed['first_author_name'] = first_author_name 
            dict_paper_info_from_pubmed['abstract_url'] = abstract_url
            dict_paper_info_from_pubmed['article_url'] = article_url
            dict_paper_info_from_pubmed['pdf_url'] = pdf_url
            dict_paper_info_from_pubmed['check_parsing'] = False
        }
    
    list_dict_paper_info_from_pubmed
        Pubmed 키워드 검색된 논문별 획득한 정보 (pubmed 검색쿼리에 저장됨) 바탕으로 Paper 쿼리 생성
        {
            "id": 0, 
            "doi": "10.1186/s12961-021-00801-2", 
            "doi_url": "https://doi.org/10.1186/s12961-021-00801-2", 
            "pmcid": "PMC8743061", 
            "title": "“There hasn’t been a career structure to step into”: a qualitative study on perceptions of allied health clinician researcher careers", 
            "keyword": "career researchers pathways", 
            "pdf_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8743061/pdf/12961_2021_Article_801.pdf", 
            "article_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8743061/?report=classic", 
            "abstract_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8743061/?report=abstract", 
            "journal_name": "Health Res Policy Syst. 2022; 20: 6.  Published online 2022 Jan 9. doi: 10.1186/s12961-021-00801-2", 
            "publication_year": 2022, 
            "first_author_name": "Caitlin Brandenburg, Elizabeth C. Ward"
        }
"""
#--------------------------------------------------------------------------------------------------------------------------------------
def download_paper_info_from_search_result_on_pubmed(q_paper_search_id, list_dict_paper_info_from_pubmed):
    print('# A-1-2 Pubmed 논문 검색 결과를 이용한 논문 PDF 다운로드 및 Paper 쿼리 생성')

    q_paper_search = Paper_Search_Google_and_PubMed.objects.get(id=q_paper_search_id)
    if q_paper_search is not None:
        list_paper_id_from_pubmed = q_paper_search.list_paper_id_from_pubmed
        if list_paper_id_from_pubmed is None:
            list_paper_id_from_pubmed = []
    
    start_time = time.time()  # Record the start time
    max_processor = 50
    timeout_sec = 200
    req_processor = len(list_dict_paper_info_from_pubmed)
    # 실제 사용할 프로세서 개수 정하기
    if max_processor > req_processor:
        final_processor = req_processor
    else:
        final_processor = max_processor
    print(f'최종 사용 core 개수 : {final_processor}')
    random_sec = random.uniform(2, 4)

    print('# Multiprocessing용 Job List 생성')
    list_job=[]
    n = 1
    for dict_paper_info_from_pubmed in list_dict_paper_info_from_pubmed:
        try:
            doi = dict_paper_info_from_pubmed['doi']
        except:
            doi = None
        try:
            doi_url = dict_paper_info_from_pubmed['doi_url']
        except:
            doi_url = None
        try:
            pmcid = dict_paper_info_from_pubmed['pmcid']
        except:
            pmcid = None
        try:
            title = dict_paper_info_from_pubmed['title']
        except:
            title = None
        try:
            pdf_url = dict_paper_info_from_pubmed['pdf_url']
        except:
            pdf_url = None
        
        if doi is not None:
            q_paper = Paper.objects.filter(doi=doi).last()
        else:
            if pmcid is not None:
                q_paper = Paper.objects.filter(pmcid=pmcid).last()
            else:
                if title is not None:
                    q_paper = Paper.objects.filter(title=title).last()
                else:
                    q_paper = None

        # print(f'매칭되는 paper 쿼리 찾기 : {q_paper}')
        if q_paper is None:
            # print(f'신규 q_paper 쿼리 생성')
            q_paper = create_paper_in_task()
            hashcode = q_paper.hashcode
            dict_paper_info_from_pubmed['hashcode'] = hashcode
            data = {
                'title': title,
                'doi': doi,
                'doi_url': doi_url,
                'pmcid': pmcid,
                'dict_paper_info_from_pubmed': dict_paper_info_from_pubmed
            }
            Paper.objects.filter(id=q_paper.id).update(**data)
            q_paper.refresh_from_db()
        else:
            # print(f'기존 q_paper 쿼리 업데이트')
            hashcode = q_paper.hashcode
            dict_paper_info = q_paper.dict_paper_info
            if dict_paper_info is None or len(dict_paper_info) == 0:
                dict_paper_info_from_pubmed['hashcode'] = hashcode
                data = {
                    'title': title,
                    'doi': doi,
                    'doi_url': doi_url,
                    'pmcid': pmcid,
                    'dict_paper_info_from_pubmed': dict_paper_info_from_pubmed
                }
                Paper.objects.filter(id=q_paper.id).update(**data)
            else:
                for k2, v2 in dict_paper_info_from_pubmed.items():
                    if k2 in dict_paper_info:
                        try:
                            v1 = dict_paper_info[k2]
                            v0 = v1 + v2
                            dict_paper_info[k2] = v0 
                        except:
                            k3 = f'{k2}_2'
                            dict_paper_info[k3] = v0 
                    else:
                        dict_paper_info[k2] = v2 
                dict_paper_info['hashcode'] = hashcode
                data = {
                    'dict_paper_info_from_pubmed': dict_paper_info_from_pubmed
                }
                Paper.objects.filter(id=q_paper.id).update(**data)
        if n != 999 :
            list_job.append((q_paper.id, hashcode, pdf_url))
        n = n + 1 

    # D-1-1. PDF 다운받기 및 Paper 쿼리 업데이트
    if list_job is not None and len(list_job) > 0:
        print(f'# len(list_job) : {len(list_job)}')
        # Set the timeout handler for the SIGALRM signal
        
        list_result = []
        for job in list_job:
            result = f_create_pdf_name_and_file_path_using_hashcode(job[0], job[1], job[2])
            list_result.append(result)
        
        #######################################################################################
        #  1. 멀티프로세싱 활용시 함수 안에 함수 쓰지 말 것. 멀티프로세싱 함수 안에서 다 끝낼 것.
        #######################################################################################
        # signal.signal(signal.SIGALRM, timeout_handler_paper_download)
        # try:
        #     signal.alarm(timeout_sec)
        #     print('# 1. 멀티프로세싱 활용 이미지 저장 With WITH 함수, 빠름(2배정도). (중간에 뻗음?)')
        #     with b_Pool(processes=final_processor) as pool:
        #         list_result = pool.starmap(f_create_pdf_name_and_file_path_using_hashcode, list_job)
        #     signal.alarm(0)
        # except TimeoutException_paper_download:   
        #     print('# 2. 멀티프로세싱 활용 이미지 저장 Without WITH 함수 but pool.close(), pool.join(). 느림. 안정적(?)')
        #     pool = b_Pool(processes=final_processor)
        #     list_result = pool.starmap(f_create_pdf_name_and_file_path_using_hashcode, list_job)
        #     pool.close()
        #     pool.join()
        # except Exception as e:
        #     print(f"An error occurred: {e}")
        #     for job in list_job:
        #         result = f_create_pdf_name_and_file_path_using_hashcode(job)
        #         list_result.append(result)
        
        print(f'# Paper 쿼리 생성하기 len(list_result):  {len(list_result)}')
        try:
            for result in list_result:
                print(f'result: {result}')
                if result is not None:
                    q_paper = Paper.objects.filter(hashcode=result).last()
                    if q_paper is not None:
                        list_paper_id_from_pubmed.append(q_paper.id)
        except Exception as e:
            print(f"Failed to get result 1: {e}")
        
        print('# Search 결과 업데이트')
        if q_paper_search is not None:
            print(f'# Search 결과 list_paper_id_from_pubmed 업데이트 len(list_paper_id_from_pubmed): {len(list_paper_id_from_pubmed)}')
            if len(list_paper_id_from_pubmed) > 0:
                data = {
                    'list_paper_id_from_pubmed': list_paper_id_from_pubmed
                }
                Paper_Search_Google_and_PubMed.objects.filter(id=q_paper_search.id).update(**data)
            else:
                pass
        else:
            print('q_paper_search is None')
    else:
        print('저장할 검색 결과 내용이 없습니다.')
        pass
    end_time = time.time()  # Record the end time
    processing_time = end_time - start_time  # Calculate the time difference
    print(f"Paper Download on PubMed Processed in {processing_time:.4f} seconds") 
    return True







#############################################################################################################################################
#############################################################################################################################################
#
#                                           A-2: 키워드 활용, Google Scholar에서 검색 정보 획득 
#
#############################################################################################################################################
#############################################################################################################################################


#--------------------------------------------------------------------------------------------------------------------------------------
# A-2. keyword_str 활용 Google Scholar 검색하기
"""
    A-2-1
        list_dict_paper_info_from_google 
        예: 
        [
            {
                'id': id, 
                'pdf_url': None, 
                'title': 'Clinician researcher career pathway for registered nurses and midwives: a proposal', 
                'title_url': 'https://onlinelibrary.wiley.com/doi/abs/10.1111/ijn.12640', 
                'journal_name': ' International journal of\xa0…', 
                'publisher_name': ' Wiley Online Library', 
                'publication_year': 2018, 
                'list_dict_author': [{'author_name': 'S Smith', 'author_url': 'https://scholar.google.com/citations?user=VRVbc6gAAAAJ&hl=en&oi=sra'}, {'author_name': 'J Gullick', 'author_url': 'https://scholar.google.com/citations?user=xo1hoNcAAAAJ&hl=en&oi=sra'}, {'author_name': 'J Ballard…', 'author_url': None}], 
                'first_author_url': 'https://scholar.google.com/citations?user=VRVbc6gAAAAJ&hl=en&oi=sra',
            }, 
            {}, 
            {},
        ]
"""
#--------------------------------------------------------------------------------------------------------------------------------------
@shared_task(time_limit=20000, soft_time_limit=19800)
def paper_keyword_search_on_google_scholar(q_paper_search_id, keyword_str):
    
    q_paper_search = Paper_Search_Google_and_PubMed.objects.get(id=q_paper_search_id)
    if q_paper_search is None:
        print('q_paper_search is None')
        return False
    else:
        list_dict_paper_info_from_google = q_paper_search.list_dict_paper_info_from_google
        if list_dict_paper_info_from_google is None:
            list_dict_paper_info_from_google = []


    # A-2-1. Google Scholar 검색내용 Parsing, list_dict_paper_info_from_google 생성
    if len(list_dict_paper_info_from_google) == 0:
        print('# 2. 키워드 활용, Google Scholar에서 검색 정보 획득 A-2 : 시작')
        start_time = time.time()  # Record the start time
        driver = boot_google_chrome_driver_in_study_tasks(None)
        time.sleep(3)
        
        if driver:
            list_dict_paper_info_from_google  = collect_search_result_on_google_scholar(driver, keyword_str)
        driver.quit() 
    else:
        print('# 2. 키워드 활용, Google Scholar에서 검색 정보 획득 A-2 : 완료')

    # A-2-2. Google 논문 검색 결과를 이용한 논문 PDF 다운로드 및 Paper 쿼리 생성
    if len(list_dict_paper_info_from_google) > 0:
        data = {    
            'list_dict_paper_info_from_google': list_dict_paper_info_from_google,
        }
        Paper_Search_Google_and_PubMed.objects.filter(id=q_paper_search_id).update(**data)
        q_paper_search.refresh_from_db()

        download_paper_info_from_search_result_on_google(q_paper_search_id, list_dict_paper_info_from_google)
    else:
        print('# Google Scholar 서치 결과가 없습니다.')



#--------------------------------------------------------------------------------------------------------------------------------------
# A-2-1. Google Scholar에서 검색내용 Parsing
#--------------------------------------------------------------------------------------------------------------------------------------
def collect_search_result_on_google_scholar(driver, keyword_str):
    random_sec = random.uniform(2, 4)
    
    keyword_str = keyword_str.strip()
    keyword_str = keyword_str.replace(',', ' ')
    keyword_str = keyword_str.replace('  ', ' ')
    keyword_sum = keyword_str.replace(' ', '+')
    
    list_page = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]

    list_dict_paper_info = []
    num_id = 0
    for page in list_page:
        keyword_search_result_url = f'https://scholar.google.com/scholar?start={page}&q={keyword_sum}&hl=en&as_sdt=0,5'
        print(f'keyword_search_result_url, {keyword_search_result_url}')
        driver.get(keyword_search_result_url)
        time.sleep(random_sec)
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')

        article_elements = soup.find_all('div',  class_='gs_r')
        
        i = 0
        for article_element in article_elements:
            dict_paper_info = {}
            dict_paper_info['id'] = num_id
            dict_paper_info['keyword'] = keyword_str
            # PDF Download Availability Check
            pdf_element = article_element.find('div', class_='gs_ggsd')
            if pdf_element:
                try:
                    pdf_url = pdf_element.find('a')['href']
                except:
                    pdf_url = None
            else:
                pdf_url = None 
            # print('pdf_url', pdf_url)
            dict_paper_info['pdf_url'] = pdf_url

            # h3 element
            h3_element = article_element.find('h3')
            try:
                title = h3_element.get_text().strip()
            except:
                title = None
            try:
                title_url = h3_element.find('a')['href']
            except:
                title_url = None
            print(title, title_url)
            dict_paper_info['title'] = title
            dict_paper_info['title_url'] = title_url

            # Organization
            list_author_name = []
            list_dict_author = []
            list_collected_author_name = []
            cite_element = article_element.find('div', class_="gs_a")
            try:
                cite_text = cite_element.get_text()
                list_cite_item = cite_text.split('-')
                authors_text = list_cite_item[0]
                list_author_name_raw = authors_text.split(',')
            except:
                list_author_name_raw = None
            if list_author_name_raw is not None and len(list_author_name_raw) > 0:
                for author_name_raw in list_author_name_raw:
                    list_author_name.append(author_name_raw.strip())

            if len(list_cite_item) > 1:
                organization_item = list_cite_item[1]
                # print('organization_name', organization_item)
                if ',' in organization_item:
                    list_organization_name = organization_item.split(',')
                    journal_name = list_organization_name[0]
                    publication_year = list_organization_name[-1]
                    publication_year = publication_year.strip()
                    
                    if publication_year:
                        try:
                            publication_year = int(publication_year)
                        except:
                            publication_year = None
                    else:
                        publication_year = None
                else:
                    journal_name = None
                    publication_year = None 

                if len(list_cite_item) > 2:
                    publisher_name = list_cite_item[2]
                else:
                    publisher_name = None 
            else:
                journal_name = None
                publication_year = None
                publisher_name = None

            dict_paper_info['journal_name'] = journal_name
            dict_paper_info['publication_year'] = publication_year
            dict_paper_info['publisher_name'] = publisher_name
            
            
            try:
                list_cite_href = cite_element.find_all('a')
            except:
                list_cite_href = None 
            if list_cite_href is not None and len(list_cite_href) > 0:
                for cite_href in list_cite_href:
                    dict_author = {}
                    try:
                        cite_href_text = cite_href.get_text()
                    except:
                        cite_href_text = None
                    try:
                        cite_href_url = cite_href['href']
                    except:
                        cite_href_url = None
                    
                    if cite_href_text is not None:
                        cite_href_text = cite_href_text.strip()
                        dict_author['author_name'] = cite_href_text
                    
                    if cite_href_url is not None:
                        cite_href_url = cite_href_url.strip()
                        dict_author['author_url'] = BASE_URL_GOOGLE_SCHOLAR + cite_href_url

                    list_dict_author.append(dict_author)
                    list_collected_author_name.append(cite_href_text)
            
            first_author_url = None
            first_author_name = None
            if list_author_name is not None and len(list_author_name) > 0:
                j = 0
                for author_name in list_author_name:
                    if author_name not in list_collected_author_name:
                        dict_author = {}
                        dict_author['author_name'] = author_name
                        dict_author['author_url'] = None
                        list_dict_author.append(dict_author)
                    else:
                        if j == 0:
                            for dict_author in list_dict_author:
                                if author_name == dict_author['author_name']:
                                    first_author_url = dict_author['author_url']
                                    first_author_name = author_name
                    j = j + 1
            
            dict_paper_info['list_dict_author'] = list_dict_author
            dict_paper_info['first_author_url'] = first_author_url
            dict_paper_info['first_author_name'] = first_author_name

            list_dict_paper_info.append(dict_paper_info)

            i = i + 1
            num_id = num_id + 1
            

    print(f'len(list_dict_paper_info), {len(list_dict_paper_info)}')
    return list_dict_paper_info



#--------------------------------------------------------------------------------------------------------------------------------------
# A-2-2. Google Scholar에서 논문 검색 결과를 이용한 논문 PDF 다운로드 및 Paper 쿼리 생성
""" 
    list_dict_paper_info_from_google 
        예: 
        [
            {
                'id': id, 
                'pdf_url': None, 
                'title': 'Clinician researcher career pathway for registered nurses and midwives: a proposal', 
                'title_url': 'https://onlinelibrary.wiley.com/doi/abs/10.1111/ijn.12640', 
                'journal_name': ' International journal of\xa0…', 
                'publisher_name': ' Wiley Online Library', 
                'publication_year': 2018, 
                'list_dict_author': [{'author_name': 'S Smith', 'author_url': 'https://scholar.google.com/citations?user=VRVbc6gAAAAJ&hl=en&oi=sra'}, {'author_name': 'J Gullick', 'author_url': 'https://scholar.google.com/citations?user=xo1hoNcAAAAJ&hl=en&oi=sra'}, {'author_name': 'J Ballard…', 'author_url': None}], 
                'first_author_url': 'https://scholar.google.com/citations?user=VRVbc6gAAAAJ&hl=en&oi=sra',
            }, 
            {}, 
            {},
        ]
    """
#--------------------------------------------------------------------------------------------------------------------------------------
def download_paper_info_from_search_result_on_google(q_paper_search_id, list_dict_paper_info_from_google):
    print('# A-2-2 Google Scholar 논문 검색 결과를 이용한 논문 PDF 다운로드 및 Paper 쿼리 생성')

    q_paper_search = Paper_Search_Google_and_PubMed.objects.get(id=q_paper_search_id)
    if q_paper_search is not None:
        list_paper_id_from_google = q_paper_search.list_paper_id_from_google
        if list_paper_id_from_google is None:
            list_paper_id_from_google = []

    start_time = time.time()  # Record the start time
    max_processor = 50
    timeout_sec = 200
    req_processor = len(list_dict_paper_info_from_google)
    # 실제 사용할 프로세서 개수 정하기
    if max_processor > req_processor:
        final_processor = req_processor
    else:
        final_processor = max_processor
    print(f'최종 사용 core 개수 : {final_processor}')
    random_sec = random.uniform(2, 4)

    print('# Multiprocessing용 Job List 생성')
    list_job=[]
    n = 1

    for dict_paper_info_from_google in list_dict_paper_info_from_google:
        try:
            title = dict_paper_info_from_google['title']
        except:
            title = None
        try:
            pdf_url = dict_paper_info_from_google['pdf_url']
        except:
            pdf_url = None
        
        if title is not None:
            q_paper = Paper.objects.filter(title=title).last()
        else:
            q_paper = None

        # print(f'매칭되는 paper 쿼리 찾기 : {q_paper}')
        if q_paper is None:
            q_paper = create_paper_in_task()
            hashcode = q_paper.hashcode
            dict_paper_info_from_google['hashcode'] = hashcode
            data = {
                'title': title,
                'dict_paper_info_from_google': dict_paper_info_from_google
            }
            Paper.objects.filter(id=q_paper.id).update(**data)
            q_paper.refresh_from_db()
        else:
            hashcode = q_paper.hashcode
            dict_paper_info_from_google_original = q_paper.dict_paper_info_from_google
            if dict_paper_info_from_google_original is None or len(dict_paper_info_from_google_original) == 0:
                dict_paper_info_from_google['hashcode'] = hashcode
                data = {
                    'title': title,
                    'dict_paper_info_from_google': dict_paper_info_from_google
                }
                Paper.objects.filter(id=q_paper.id).update(**data)
            else:
                for k2, v2 in dict_paper_info_from_google.items():
                    if k2 in dict_paper_info_from_google_original:
                        try:
                            v1 = dict_paper_info_from_google_original[k2]
                            v0 = v1 + v2
                            dict_paper_info_from_google_original[k2] = v0 
                        except:
                            k3 = f'{k2}_2'
                            dict_paper_info_from_google_original[k3] = v0 
                    else:
                        dict_paper_info_from_google_original[k2] = v2 
                dict_paper_info_from_google_original['hashcode'] = hashcode
                data = {
                    'dict_paper_info_from_google': dict_paper_info_from_google_original
                }
                Paper.objects.filter(id=q_paper.id).update(**data)

        list_job.append((q_paper.id, hashcode, pdf_url))
        n = n + 1 

    if list_job is not None and len(list_job) > 0:
        print(f'# len(list_job) : {len(list_job)}')
        # Set the timeout handler for the SIGALRM signal
        
        list_result = []
        for job in list_job:
            result = f_create_pdf_name_and_file_path_using_hashcode(job[0], job[1], job[2])
            list_result.append(result)

        #######################################################################################
        #  1. 멀티프로세싱 활용시 함수 안에 함수 쓰지 말 것. 멀티프로세싱 함수 안에서 다 끝낼 것.
        #######################################################################################
        # signal.signal(signal.SIGALRM, timeout_handler_paper_download)
        # try:
        #     signal.alarm(timeout_sec)
        #     print('# 1. 멀티프로세싱 활용 이미지 저장 With WITH 함수, 빠름(2배정도). (중간에 뻗음?)')
        #     with b_Pool(processes=final_processor) as pool:
        #         list_result = pool.starmap(f_create_pdf_name_and_file_path_using_hashcode, list_job)
        #     signal.alarm(0)
        # except TimeoutException_paper_download:   
        #     print('# 2. 멀티프로세싱 활용 이미지 저장 Without WITH 함수 but pool.close(), pool.join(). 느림. 안정적(?)')
        #     pool = b_Pool(processes=final_processor)
        #     list_result = pool.starmap(f_create_pdf_name_and_file_path_using_hashcode, list_job)
        #     pool.close()
        #     pool.join()
        # except Exception as e:
        #     print(f"An error occurred: {e}")
        #     list_result = []
        
        print(f'# Paper 쿼리 생성하기 len(list_result):  {len(list_result)}')
        try:
            for result in list_result:
                print(f'result: {result}')
                if result is not None:
                    q_paper = Paper.objects.filter(hashcode=result).last()
                    if q_paper is not None:
                        list_paper_id_from_google.append(q_paper.id)
        except Exception as e:
            print(f"Failed to get result 1: {e}")
        
        print('# Search 결과 업데이트')
        if q_paper_search is not None:
            print(f'# Search 결과 list_paper_id_from_google 업데이트 len(list_paper_id_from_google): {len(list_paper_id_from_google)}')
            data = {
                'list_paper_id_from_google': list_paper_id_from_google
            }
            Paper_Search_Google_and_PubMed.objects.filter(id=q_paper_search.id).update(**data)
        else:
            print('q_paper_search is None')
    else:
        print('저장할 검색 결과 내용이 없습니다.')
        pass
    end_time = time.time()  # Record the end time
    processing_time = end_time - start_time  # Calculate the time difference
    print(f"Paper Download on Google Processed in {processing_time:.4f} seconds") 
    return True








#############################################################################################################################################
#############################################################################################################################################
#
#                              B-1: Pubmed 검색리스트에서 선택한 Paper의 추가정보 PubMed Free(PMC)에서 검색 및 정보 획득 
#
#   1. 선택한 Paper의 PMC url로 기본정보 및 Reference / Relevant / Author Paper 기본정보 획득
#   2. 획득한 Reference / Relevant / Author 기본정보를 Multiprocessing용 List_job으로 세팅
#   3. Reference / Relevant / Author Paper 다운로드
#   4. 선택한 Paper 정보 업데이트
#
#############################################################################################################################################
#############################################################################################################################################


# 검색 결과 리스트에서 선택한 논문에 대한 자세한 정보 수집
#--------------------------------------------------------------------------------------------------------------------------------------
# B-1 Pubmed 검색결과에서 선택한 Paper에 관련된 추가정보 수집 (Reference 논문들, First Author 논문들, 비슷한 주제 논문들 정보 수집, 신규 Paper 쿼리 생성 및 PDF 다운로드)
#--------------------------------------------------------------------------------------------------------------------------------------
@shared_task(time_limit=20000, soft_time_limit=19800)
def parsing_selected_paper_detail_info_on_pubmed(parsing_url, doi, pmcid, q_paper_id):
    print(f"Start B-1 {parsing_url}, {doi}, {q_paper_id}, {pmcid}")
    # print(f"Paper Query ID:  {q_paper_id}")
    random_sec = random.uniform(2, 4)
    max_processor = 50
    # max_processor = len(LIST_PORT_SMARTPROXY)
    timeout_sec = 100
    doi_url = BASE_URL_DOI + doi
    pm_url_instance = f'{BASE_URL_PUBMED}/{pmcid}'

    
    q_paper_selected = Paper.objects.get(id=q_paper_id)
    if q_paper_selected is not None:
        list_dict_reference_paper = q_paper_selected.list_dict_reference_paper
        if list_dict_reference_paper is None:
            list_dict_reference_paper = [] 
        list_dict_author_paper = q_paper_selected.list_dict_author_paper
        if list_dict_author_paper is None:
            list_dict_author_paper = [] 
        list_dict_relevant_paper = q_paper_selected.list_dict_relevant_paper
        if list_dict_relevant_paper is None:
            list_dict_relevant_paper = [] 
    else:
        q_paper_selected = None    
    
    if q_paper_selected is None:
        print('q_paper_selected is None')
        return False
    else:
        print(f'START Parsing! q_paper_selected.id: {q_paper_selected.id}')
        pmid = q_paper_selected.pmid

        # Start Reference Paper Parsing
        #--------------------------------------------------------------------------------------------------------------------------------------
        # 1. 선택한 Paper의 PMC url로 기본정보 및 Reference / Relevant / Author Paper 기본정보 획득
        """
            선택한 논문으로 더 디테일한 정보 획득 (선택한 논문의 Reference 논문들의 기본 정보들)
            list_dict_reference_paper = [
                {
                    'id': id,
                    'q_paper_id': None,
                    'cite': cite,
                    'doi': doi,
                    'doi_url': doi_link,
                    'pubmed_url': pubmed_url,
                    'pubmed_free_url': pubmed_free_url,
                    'google_scholar_url': google_scholar_url,    
                    'other_url': other_url,
                }
            ]
            list_dict_relevent_paper = [
                {
                    'id': id,
                    'title': title,
                    'pubmed_url': pubmed_url,
                    'journal': journal,
                    'doi': doi,
                    'doi_url': doi_url,
                    'pmid': pmid,
                }
            ]
            list_dict_author_paper = [
                {
                    'id': id,
                    'title': title,
                    'pubmed_url': pubmed_url,
                    'journal': journal,
                    'doi': doi,
                    'doi_url': doi_url,
                    'pmid': pmid,
                }
            ]
        """
        #--------------------------------------------------------------------------------------------------------------------------------------
        if len(list_dict_reference_paper) > 0:
            print('# B-2 선택한 논문 Reference Paper 정보를 이미 확보하였습니다.')
            pmid = get_pmid_on_pmc_site(parsing_url, q_paper_selected.id)
            pass 
        else:
            # B-1-1. 선택한 Paper의 Reference 정보 획득 시작
            dict_paper_info = scraping_reference_paper_info_on_pmc_or_pubmed(parsing_url)
            dict_paper_info_new = {}
            pmcid = dict_paper_info['pmcid']
            title = dict_paper_info['title']
            abstract = dict_paper_info['abstract']
            first_author_name = dict_paper_info['first_author_name']
            first_author_url = dict_paper_info['first_author_url']
            list_dict_author_info = dict_paper_info['list_dict_author_info']
            doi = dict_paper_info['doi']
            doi_url = dict_paper_info['doi_url']
            pmid = dict_paper_info['pmid']
            pmid_url = dict_paper_info['pmid_url']
            pdf_url = dict_paper_info['pdf_url']
            list_dict_reference_paper = dict_paper_info['list_dict_reference_paper']
            
            dict_paper_info_new['pubmed_free_url'] = parsing_url
            dict_paper_info_new['pubmed_url'] = pmid_url
            dict_paper_info_new['list_dict_author_info'] = list_dict_author_info
            data = {
                'title': title,
                'abstract': abstract,
                'first_author_name': first_author_name,
                'first_author_url': first_author_url,
                'doi': doi,
                'doi_url': doi_url,
                'pmcid': pmcid,
                'pmid': pmid,
                'pdf_url': pdf_url,
                'list_dict_reference_paper': list_dict_reference_paper,
                'dict_paper_info': dict_paper_info_new,
            }
            Paper.objects.filter(id=q_paper_selected.id).update(**data)
            q_paper_selected.refresh_from_db()
        
        
        # list_dict_relevant_paper
        if len(list_dict_relevant_paper) > 0:
            print('# B-2 선택한 논문 Relevant Paper 정보를 이미 확보하였습니다.')
            pass 
        else:
            # B-1-2. 선택한 Paper의 Relevant Paper 정보 획득 시작
            max_page_for_similar = 10
            max_page_for_cited = 10
            list_dict_similar_paper_info_from_pubmed = scraping_similar_paper_info_on_pubmed(pmid, max_page_for_similar)
            time.sleep(random_sec)
            list_dict_cited_paper_info_from_pubmed = scraping_cited_paper_info_on_pubmed(pmid, max_page_for_cited)
            time.sleep(random_sec)
            if list_dict_similar_paper_info_from_pubmed is None:
                list_dict_similar_paper_info_from_pubmed = []
            if list_dict_cited_paper_info_from_pubmed is None:
                list_dict_cited_paper_info_from_pubmed = []
            list_dict_relevant_paper = list_dict_similar_paper_info_from_pubmed + list_dict_cited_paper_info_from_pubmed
            if len(list_dict_relevant_paper) > 0:
                i = 1
                for dict_relevant_paper in list_dict_relevant_paper:
                    dict_relevant_paper['id'] = i
                    i = i + 1
                data = {
                    'list_dict_relevant_paper': list_dict_relevant_paper,
                }
                Paper.objects.filter(id=q_paper_selected.id).update(**data)
                q_paper_selected.refresh_from_db()
            print(f'확보한 Relevant Paper 개수 len(list_dict_relevant_paper): {len(list_dict_relevant_paper)}')


        if len(list_dict_author_paper) > 0:
            print('# B-2 선택한 논문 First Author Paper 정보를 이미 확보하였습니다.')
            pass 
        else:
            # B-1-3. 선택한 Paper의 First Author Paper 정보 획득 시작
            max_page_for_first_author = 10
            list_dict_first_author_paper_info_from_pubmed = scraping_first_author_paper_info_on_pubmed(q_paper_id, pmid, max_page_for_first_author)
            time.sleep(random_sec)
            if list_dict_first_author_paper_info_from_pubmed is None:
                list_dict_first_author_paper_info_from_pubmed = []
            list_dict_author_paper = list_dict_first_author_paper_info_from_pubmed
            if len(list_dict_author_paper) > 0:
                i = 1
                for dict_author_paper in list_dict_author_paper:
                    dict_author_paper['id'] = i
                    i = i + 1
                data = {
                    'list_dict_author_paper': list_dict_author_paper,
                }
                Paper.objects.filter(id=q_paper_selected.id).update(**data)
                q_paper_selected.refresh_from_db()
            print(f'확보한 First Author Paper 개수 len(list_dict_author_paper): , {len(list_dict_author_paper)}')

        #--------------------------------------------------------------------------------------------------------------------------------------
        # B-1-1-x. 선택 논문의 Reference Paper 디테일 정보 수집 및 PDF 다운로드 (w/o Multiprocessing)
        #--------------------------------------------------------------------------------------------------------------------------------------
        if len(list_dict_reference_paper) > 0:
            print(f'print(len(list_dict_reference_paper)), {len(list_dict_reference_paper)}')
            # B-1-1-1. 멀티프로세싱을 위한 정보 세팅 : 수집한 reference url로 부터 Paper 정보 수집 및 PDF 다운로드 (1, 2, 3 방법론 중 하나만 만족해서 다운받으면 됨. 우선순위는 1, 2, 3번 순), 
            """ 
            list_job = (q_paper_id, rel_id, article_url, doi, site_name, related_type, dict_paper_rel_info, n)
            """
            list_job = []
            list_result = []

            list_job = get_list_job_for_parsing_selected_paper_reference_data(q_paper_id, list_dict_reference_paper)
            print(f'len(list_job), {len(list_job)}')
            print(f'print(len(list_dict_reference_paper)), {len(list_dict_reference_paper)}')

 
            # B-1-1-2. Reference Paper 정보 수집 (w/ Multiprocessing)
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # 1. Multiprocssing 함수 내에서 DB에 접속해서 데이터 가져오지 말고 Json 형식으로 미리 함수로 보내라
            # 2. Multiprocssing 끝나고 Json으로 돌려받은 데이터로 쿼리(DB) 업데이트 하라
            # 
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            req_processor = len(list_job)
            # 실제 사용할 프로세서 개수 정하기
            if max_processor > req_processor:
                final_processor = req_processor
            else:
                final_processor = max_processor
            print(f'작업해야할 개수: {len(list_job)},  최종 사용 core 개수 : {final_processor}')
            
            # Use multiprocessing Pool
            with Pool(processes=final_processor) as pool:
                # Submit all jobs to the pool simultaneously
                async_results = [
                    pool.apply_async(f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf, args=job)
                    for job in list_job
                ]
                # Collect results
                for i, async_result in enumerate(async_results):
                    try:
                        # Wait for the result with a timeout of 30 seconds
                        result = async_result.get(timeout=30)
                        list_result.append(result)
                    except TimeoutError:
                        # Handle timeout for the specific task
                        print(f"Task with arguments {list_job[i]} exceeded the 30-second time limit.")
                        list_result.append(None)
            print(f'list_result, {len(list_result)}')
           
            """
            dict_result = {
                'title': title, 
                'doi': doi, 
                'doi_url': doi_url, 
                'pmid': pmid, 
                'pmcid': pmcid, 
                'first_author_name': first_author_name, 
                'first_author_url': first_author_url, 
                'publication_year': publication_year, 
                'dict_paper_info': dict_paper_info, 
                'list_dict_reference_paper': list_dict_reference_paper, 
                'pdf_url': pdf_url
            }
            """
            
            # Update Paper query
            if len(list_result) > 0:
                list_reference_paper_id = q_paper_selected.list_reference_paper_id
                if list_reference_paper_id is None:
                    list_reference_paper_id = []

                for dict_result in list_result:
                    if dict_result is not None:
                        try:
                            title = dict_result['title']
                        except:
                            title = None
                        try:
                            doi = dict_result['doi']
                        except:
                            doi = None
                        try:
                            doi_url = dict_result['doi_url']
                        except:
                            doi_url = None
                        try:
                            pmid = dict_result['pmid']
                        except:
                            pmid = None
                        try:
                            pmcid = dict_result['pmcid']
                        except:
                            pmcid = None
                        try:
                            pdf_url = dict_result['pdf_url']
                        except:
                            pdf_url = None
                        try:
                            dict_paper_info = dict_result['dict_paper_info']
                        except:
                            dict_paper_info = None
                        if dict_paper_info is not None:
                            try:
                                rel_id = dict_paper_info['rel_id']
                            except:
                                rel_id = None
                            try:
                                article_url = None
                                list_dict_pdf_link_url = dict_paper_info['list_dict_pdf_link_url']
                                if list_dict_pdf_link_url is not None and len(list_dict_pdf_link_url) > 0:
                                    for dict_pdf_link_url in list_dict_pdf_link_url:
                                        if dict_pdf_link_url['site_name'] != 'Free PMC article':
                                            article_url = dict_pdf_link_url['site_url']
                                            break 
                            except:
                                article_url = None
                            try:
                                journal_info = dict_paper_info['journal']
                            except:
                                journal_info = None
                        else:
                            rel_id = None
                            article_url = None
                            journal_info = None
                        dict_result['article_url'] = article_url
                        dict_result['journal_info'] = journal_info
                        
                        if doi is not None:
                            q_paper_rel = Paper.objects.filter(doi=doi).last()
                        else:
                            if pmcid is not None:
                                q_paper_rel = Paper.objects.filter(pmcid=pmcid).last()
                            else:
                                if pmid is not None:
                                    q_paper_rel = Paper.objects.filter(pmid=pmid).last()
                                else:
                                    if title is not None:
                                        q_paper_rel = Paper.objects.filter(title=title).last()

                        if q_paper_rel is None:
                            random_uuid = uuid.uuid4()
                            hashcode = str(random_uuid)
                            dict_result['hashcode'] = hashcode
                            q_paper_rel = Paper.objects.create(**dict_result)
                            print(f'신규 Paper 쿼리 생성 완료 {q_paper_rel.id}')
                        else:
                            Paper.objects.filter(id=q_paper_rel.id).update(**dict_result)
                            q_paper_rel.refresh_from_db()
                            print(f'ID: {q_paper_rel.id} 논문은 이미 저장되어 있습니다. Update 하였습니다.')
                        
                        # Update Related Paper
                        dict_paper_info['q_paper_id'] = q_paper_rel.id  # 사용자 선택한 paper에 등록된 Reference Paper id
                        if q_paper_rel.id not in list_reference_paper_id:
                            list_reference_paper_id.append(q_paper_rel.id)
                        data = {
                            'dict_paper_info': dict_paper_info,
                        }
                        Paper.objects.filter(id=q_paper_rel.id).update(**data)
                        q_paper_rel.refresh_from_db()
                        
                        # PDF Download Single Processor
                        try:
                            hashcode = q_paper_rel.hashcode
                        except:
                            hashcode = None
                        if hashcode is not None:
                            file_extension = 'pdf'
                            pdf_name = f'paper-{hashcode}.{file_extension}'
                            file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER, pdf_name)
                        else:
                            file_path = None
                        if file_path is not None and pdf_url is not None:    
                            try:
                                check_download_pdf = f_download_pdf_using_requests(pdf_url, file_path)
                            except:
                                check_download_pdf = False
                        else:
                            check_download_pdf = False
                        if check_download_pdf == True:
                            file_path_pdf = BASE_DIR_STUDY_PAPER + pdf_name
                        else:
                            file_path_pdf = None 
                        data = {
                            'check_download_pdf': check_download_pdf,
                            'file_path_pdf': file_path_pdf,
                        }
                        Paper.objects.filter(id=q_paper_rel.id).update(**data)
                        q_paper_rel.refresh_from_db()
                        
                        # Parent Paper 업데이트하기
                        try:
                            first_author_name = q_paper_rel.first_author_name
                        except:
                            first_author_name = None 
                        try:
                            first_author_url = q_paper_rel.first_author_url
                        except:
                            first_author_url = None
                        try:
                            list_dict_pdf_link_url = dict_paper_info['list_dict_pdf_link_url']
                            if list_dict_pdf_link_url is not None and len(list_dict_pdf_link_url) > 0:
                                for dict_pdf_link_url in list_dict_pdf_link_url:
                                    if dict_pdf_link_url['site_name'] != 'Free PMC article':
                                        article_url = dict_pdf_link_url['site_url']
                                        break 
                        except:
                            article_url = None

                        list_dict_reference_paper_new = []
                        for dict_xxx_paper in list_dict_reference_paper:
                            if rel_id == dict_xxx_paper['id']:
                                dict_xxx_paper_new = dict_xxx_paper
                                dict_xxx_paper_new['doi'] = doi
                                dict_xxx_paper_new['doi_url'] = doi_url
                                dict_xxx_paper_new['pmid'] = pmid
                                dict_xxx_paper_new['pmcid'] = pmcid
                                dict_xxx_paper_new['title'] = title
                                dict_xxx_paper_new['q_paper_id'] = q_paper_rel.id
                                dict_xxx_paper_new['file_path_pdf'] = file_path_pdf
                                dict_xxx_paper_new['first_author_name'] = first_author_name
                                dict_xxx_paper_new['first_author_url'] = first_author_url
                                dict_xxx_paper_new['dict_paper_info'] = dict_paper_info
                                dict_xxx_paper_new['article_url'] = article_url
                                try:
                                    pubmed_free_url = dict_xxx_paper_new['pubmed_free_url'] 
                                    if 'http' not in pubmed_free_url:
                                        pubmed_free_url = f'{BASE_URL_PUBMED_FREE}{pubmed_free_url}'
                                        dict_xxx_paper_new['pubmed_free_url'] = pubmed_free_url
                                except:
                                    pass
                                dict_xxx_paper.update(dict_xxx_paper_new)
                            list_dict_reference_paper_new.append(dict_xxx_paper)
                        # Update Parent Paper list_dict_reference_paper
                        data = {
                            'list_dict_reference_paper': list_dict_reference_paper_new
                        }
                        Paper.objects.filter(id=q_paper_selected.id).update(**data)
                        q_paper_selected.refresh_from_db()
                
                # Update Parent Paper     
                data = {
                    'list_reference_paper_id': list_reference_paper_id
                }
                Paper.objects.filter(id=q_paper_selected.id).update(**data)
                q_paper_selected.refresh_from_db()

                
                

        #--------------------------------------------------------------------------------------------------------------------------------------
        # B-1-2-x. 선택 논문의 Relevant Paper 디테일 정보 수집 및 PDF 다운로드  (w/o Multiprocessing)
        #--------------------------------------------------------------------------------------------------------------------------------------
        if len(list_dict_relevant_paper) > 0:
            list_job = []
            list_result = []
            
            # B-1-2-1. 멀티프로세싱을 위한 정보 세팅 : 수집한 Relevant url로 부터 Paper 정보 수집 및 PDF 다운로드 
            list_job = get_list_job_for_parsing_selected_paper_relevant_data(q_paper_id, list_dict_relevant_paper)
            print(f'len(list_job), {len(list_job)}')

            # B-1-2-2. Relevant Paper 정보 수집 (w/ Multiprocessing)
            req_processor = len(list_job)
            # 실제 사용할 프로세서 개수 정하기
            if max_processor > req_processor:
                final_processor = req_processor
            else:
                final_processor = max_processor
            print(f'작업해야할 개수: {len(list_job)},  최종 사용 core 개수 : {final_processor}')

            # Use multiprocessing Pool
            with Pool(processes=final_processor) as pool:
                # Submit all jobs to the pool simultaneously
                async_results = [
                    pool.apply_async(f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf, args=job)
                    for job in list_job
                ]
                # Collect results
                for i, async_result in enumerate(async_results):
                    try:
                        # Wait for the result with a timeout of 30 seconds
                        result = async_result.get(timeout=30)
                        list_result.append(result)
                    except TimeoutError:
                        # Handle timeout for the specific task
                        print(f"Task with arguments {list_job[i]} exceeded the 30-second time limit.")
                        list_result.append(None)
            print(f'list_result, {len(list_result)}')
            
            # Update Paper query
            if len(list_result) > 0:
                list_relevant_paper_id = q_paper_selected.list_relevant_paper_id
                if list_relevant_paper_id is None:
                    list_relevant_paper_id = []

                # Paper Query Create or Update
                print('# Paper Query Create or Update')
                for dict_result in list_result:
                    """ 
                    dict_result = {
                        'hashcode': hashcode, 
                        'title': title, 
                        'doi': doi, 
                        'doi_url': doi_url, 
                        'pmid': pmid, 
                        'pmcid': pmcid, 
                        'first_author_name': first_author_name, 
                        'first_author_url': first_author_url, 
                        'publication_year': publication_year, 
                        'file_path_pdf': file_path_pdf, 
                        'check_download_pdf': check_download_pdf, 
                        'dict_paper_info': dict_paper_info, 
                        'list_dict_reference_paper': list_dict_reference_paper,
                    }
                    """
                    if dict_result is not None:
                        try:
                            title = dict_result['title']
                        except:
                            title = None
                        try:
                            doi = dict_result['doi']
                        except:
                            doi = None
                        try:
                            rel_id = dict_result['rel_id']
                        except:
                            rel_id = None
                        try:
                            pmid = dict_result['pmid']
                        except:
                            pmid = None
                        try:
                            pmcid = dict_result['pmcid']
                        except:
                            pmcid = None
                        try:
                            pdf_url = dict_result['pdf_url']
                        except:
                            pdf_url = None
                        try:
                            dict_paper_info = dict_result['dict_paper_info']
                        except:
                            dict_paper_info = None
                        if dict_paper_info is not None:
                            try:
                                rel_id = dict_paper_info['rel_id']
                            except:
                                rel_id = None
                            try:
                                list_dict_pdf_link_url = dict_paper_info['list_dict_pdf_link_url']
                                if list_dict_pdf_link_url is not None and len(list_dict_pdf_link_url) > 0:
                                    for dict_pdf_link_url in list_dict_pdf_link_url:
                                        if dict_pdf_link_url['site_name'] != 'Free PMC article':
                                            article_url = dict_pdf_link_url['site_url']
                                            break 
                            except:
                                article_url = None
                            try:
                                journal_info = dict_paper_info['journal']
                            except:
                                journal_info = None
                        else:
                            rel_id = None
                            article_url = None
                            journal_info = None
                        dict_result['article_url'] = article_url
                        dict_result['journal_info'] = journal_info
                        
                        if doi is not None:
                            q_paper_rel = Paper.objects.filter(doi=doi).last()
                        else:
                            if pmcid is not None:
                                q_paper_rel = Paper.objects.filter(pmcid=pmcid).last()
                            else:
                                if pmid is not None:
                                    q_paper_rel = Paper.objects.filter(pmid=pmid).last()
                                else:
                                    if title is not None:
                                        q_paper_rel = Paper.objects.filter(title=title).last()
                        
                        if q_paper_rel is None:
                            random_uuid = uuid.uuid4()
                            hashcode = str(random_uuid)
                            dict_result['hashcode'] = hashcode
                            q_paper_rel = Paper.objects.create(**dict_result)
                            print(f'신규 Paper 쿼리 생성 완료 {q_paper_rel.id}')
                        else:
                            Paper.objects.filter(id=q_paper_rel.id).update(**dict_result)
                            q_paper_rel.refresh_from_db()
                            print(f'ID: {q_paper_rel.id} 논문은 이미 저장되어 있습니다. Update 하였습니다.')
                        
                        # Update Related Paper
                        dict_paper_info['q_paper_id'] = q_paper_rel.id  # 사용자 선택한 paper에 등록된 Reference Paper id
                        if q_paper_rel.id not in list_reference_paper_id:
                            list_reference_paper_id.append(q_paper_rel.id)
                        data = {
                            'dict_paper_info': dict_paper_info,
                        }
                        Paper.objects.filter(id=q_paper_rel.id).update(**data)
                        q_paper_rel.refresh_from_db()

                        # PDF Download Single Processor
                        try:
                            hashcode = q_paper_rel.hashcode
                        except:
                            hashcode = None
                        if hashcode is not None:
                            file_extension = 'pdf'
                            pdf_name = f'paper-{hashcode}.{file_extension}'
                            file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER, pdf_name)
                        else:
                            file_path = None
                        if file_path is not None and pdf_url is not None:    
                            try:
                                check_download_pdf = f_download_pdf_using_requests(pdf_url, file_path)
                            except:
                                check_download_pdf = False
                        else:
                            check_download_pdf = False
                        if check_download_pdf == True:
                            file_path_pdf = BASE_DIR_STUDY_PAPER + pdf_name
                        else:
                            file_path_pdf = None 
                        data = {
                            'check_download_pdf': check_download_pdf,
                            'file_path_pdf': file_path_pdf,
                        }
                        Paper.objects.filter(id=q_paper_rel.id).update(**data)
                        q_paper_rel.refresh_from_db()

                        # Parent Paper 업데이트하기
                        try:
                            first_author_name = q_paper_rel.first_author_name
                        except:
                            first_author_name = None 
                        try:
                            first_author_url = q_paper_rel.first_author_url
                        except:
                            first_author_url = None
                        try:
                            list_dict_pdf_link_url = dict_paper_info['list_dict_pdf_link_url']
                            if list_dict_pdf_link_url is not None and len(list_dict_pdf_link_url) > 0:
                                for dict_pdf_link_url in list_dict_pdf_link_url:
                                    if dict_pdf_link_url['site_name'] != 'Free PMC article':
                                        article_url = dict_pdf_link_url['site_url']
                                        break 
                        except:
                            article_url = None
                            
                        list_dict_relevant_paper_new = []
                        for dict_xxx_paper in list_dict_relevant_paper:
                            if rel_id == dict_xxx_paper['id']:
                                dict_xxx_paper_new = dict_xxx_paper
                                dict_xxx_paper_new['doi'] = doi
                                dict_xxx_paper_new['doi_url'] = doi_url
                                dict_xxx_paper_new['pmid'] = pmid
                                dict_xxx_paper_new['pmcid'] = pmcid
                                dict_xxx_paper_new['title'] = title
                                dict_xxx_paper_new['q_paper_id'] = q_paper_rel.id
                                dict_xxx_paper_new['file_path_pdf'] = file_path_pdf
                                dict_xxx_paper_new['first_author_name'] = first_author_name
                                dict_xxx_paper_new['first_author_url'] = first_author_url
                                dict_xxx_paper_new['dict_paper_info'] = dict_paper_info
                                dict_xxx_paper_new['article_url'] = article_url
                                try:
                                    pubmed_free_url = dict_xxx_paper_new['pubmed_free_url'] 
                                    if 'http' not in pubmed_free_url:
                                        pubmed_free_url = f'{BASE_URL_PUBMED_FREE}{pubmed_free_url}'
                                        dict_xxx_paper_new['pubmed_free_url'] = pubmed_free_url
                                except:
                                    pass
                                dict_xxx_paper.update(dict_xxx_paper_new)
                            list_dict_relevant_paper_new.append(dict_xxx_paper)
                        # Update Parent Paper list_dict_relevant_paper
                        data = {
                            'list_dict_relevant_paper': list_dict_relevant_paper_new
                        }
                        Paper.objects.filter(id=q_paper_selected.id).update(**data)
                        q_paper_selected.refresh_from_db()
                
                # Update Parent Paper     
                data = {
                    'list_relevant_paper_id': list_relevant_paper_id
                }
                Paper.objects.filter(id=q_paper_selected.id).update(**data)
                q_paper_selected.refresh_from_db()

        #--------------------------------------------------------------------------------------------------------------------------------------
        # B-1-3-x. 선택 논문의 Author Paper 디테일 정보 수집 및 PDF 다운로드 (w/o Multiprocessing)
        #--------------------------------------------------------------------------------------------------------------------------------------
        if len(list_dict_author_paper) > 0:
            list_job = []
            list_result = []
            
            # B-1-3-1. 멀티프로세싱을 위한 정보 세팅 : 수집한 Relevant url로 부터 Paper 정보 수집 및 PDF 다운로드 
            list_job = get_list_job_for_parsing_selected_paper_author_data(q_paper_id, list_dict_author_paper)
            print(f'len(list_job), {len(list_job)}')

            # B-1-3-2. Author Paper 정보 수집 (w/ Multiprocessing)
            req_processor = len(list_job)
            # 실제 사용할 프로세서 개수 정하기
            if max_processor > req_processor:
                final_processor = req_processor
            else:
                final_processor = max_processor
            print(f'작업해야할 개수: {len(list_job)},  최종 사용 core 개수 : {final_processor}')

            # Use multiprocessing Pool
            with Pool(processes=final_processor) as pool:
                # Submit all jobs to the pool simultaneously
                async_results = [
                    pool.apply_async(f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf, args=job)
                    for job in list_job
                ]

                # Collect results
                for i, async_result in enumerate(async_results):
                    try:
                        # Wait for the result with a timeout of 30 seconds
                        result = async_result.get(timeout=30)
                        list_result.append(result)
                    except TimeoutError:
                        # Handle timeout for the specific task
                        print(f"Task with arguments {list_job[i]} exceeded the 30-second time limit.")
                        list_result.append(None)
            print(f'list_result, {len(list_result)}')
                        
            # Update Paper query
            if len(list_result) > 0:
                list_author_paper_id = q_paper_selected.list_author_paper_id
                if list_author_paper_id is None:
                    list_author_paper_id = []

                for dict_result in list_result:
                    if dict_result is not None:
                        try:
                            title = dict_result['title']
                        except:
                            title = None
                        try:
                            doi = dict_result['doi']
                        except:
                            doi = None
                        try:
                            rel_id = dict_result['rel_id']
                        except:
                            rel_id = None
                        try:
                            pmid = dict_result['pmid']
                        except:
                            pmid = None
                        try:
                            pmcid = dict_result['pmcid']
                        except:
                            pmcid = None
                        try:
                            pdf_url = dict_result['pdf_url']
                        except:
                            pdf_url = None
                        try:
                            dict_paper_info = dict_result['dict_paper_info']
                        except:
                            dict_paper_info = None
                        if dict_paper_info is not None:
                            try:
                                rel_id = dict_paper_info['rel_id']
                            except:
                                rel_id = None
                            try:
                                list_dict_pdf_link_url = dict_paper_info['list_dict_pdf_link_url']
                                if list_dict_pdf_link_url is not None and len(list_dict_pdf_link_url) > 0:
                                    for dict_pdf_link_url in list_dict_pdf_link_url:
                                        if dict_pdf_link_url['site_name'] != 'Free PMC article':
                                            article_url = dict_pdf_link_url['site_url']
                                            break 
                            except:
                                article_url = None
                            try:
                                journal_info = dict_paper_info['journal']
                            except:
                                journal_info = None
                        else:
                            rel_id = None
                            article_url = None
                            journal_info = None
                        dict_result['article_url'] = article_url
                        dict_result['journal_info'] = journal_info

                        if doi is not None:
                            q_paper_rel = Paper.objects.filter(doi=doi).last()
                        else:
                            if pmcid is not None:
                                q_paper_rel = Paper.objects.filter(pmcid=pmcid).last()
                            else:
                                if pmid is not None:
                                    q_paper_rel = Paper.objects.filter(pmid=pmid).last()
                                else:
                                    if title is not None:
                                        q_paper_rel = Paper.objects.filter(title=title).last()

                        if q_paper_rel is None:
                            random_uuid = uuid.uuid4()
                            hashcode = str(random_uuid)
                            dict_result['hashcode'] = hashcode
                            q_paper_rel = Paper.objects.create(**dict_result)
                            print(f'신규 Paper 쿼리 생성 완료 {q_paper_rel.id}')
                        else:
                            Paper.objects.filter(id=q_paper_rel.id).update(**dict_result)
                            q_paper_rel.refresh_from_db()
                            print(f'ID: {q_paper_rel.id} 논문은 이미 저장되어 있습니다. Update 하였습니다.')
                        
                        # PDF Download Single Processor
                        try:
                            hashcode = q_paper_rel.hashcode
                        except:
                            hashcode = None
                        if hashcode is not None:
                            file_extension = 'pdf'
                            pdf_name = f'paper-{hashcode}.{file_extension}'
                            file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER, pdf_name)
                        else:
                            file_path = None
                        if file_path is not None and pdf_url is not None:    
                            try:
                                check_download_pdf = f_download_pdf_using_requests(pdf_url, file_path)
                            except:
                                check_download_pdf = False
                        else:
                            check_download_pdf = False
                        if check_download_pdf == True:
                            file_path_pdf = BASE_DIR_STUDY_PAPER + pdf_name
                        else:
                            file_path_pdf = None 
                        data = {
                            'check_download_pdf': check_download_pdf,
                            'file_path_pdf': file_path_pdf,
                        }
                        Paper.objects.filter(id=q_paper_rel.id).update(**data)
                        q_paper_rel.refresh_from_db()
                        # Parent Paper 업데이트하기
                        try:
                            first_author_name = q_paper_rel.first_author_name
                        except:
                            first_author_name = None 
                        try:
                            first_author_url = q_paper_rel.first_author_url
                        except:
                            first_author_url = None
                        try:
                            list_dict_pdf_link_url = dict_paper_info['list_dict_pdf_link_url']
                            if list_dict_pdf_link_url is not None and len(list_dict_pdf_link_url) > 0:
                                for dict_pdf_link_url in list_dict_pdf_link_url:
                                    if dict_pdf_link_url['site_name'] != 'Free PMC article':
                                        article_url = dict_pdf_link_url['site_url']
                                        break 
                        except:
                            article_url = None

                        list_dict_author_paper_new = []
                        for dict_xxx_paper in list_dict_author_paper:
                            if rel_id == dict_xxx_paper['id']:
                                dict_xxx_paper_new = dict_xxx_paper
                                dict_xxx_paper_new['doi'] = doi
                                dict_xxx_paper_new['doi_url'] = doi_url
                                dict_xxx_paper_new['pmid'] = pmid
                                dict_xxx_paper_new['pmcid'] = pmcid
                                dict_xxx_paper_new['title'] = title
                                dict_xxx_paper_new['q_paper_id'] = q_paper_rel.id
                                dict_xxx_paper_new['file_path_pdf'] = file_path_pdf
                                dict_xxx_paper_new['first_author_name'] = first_author_name
                                dict_xxx_paper_new['first_author_url'] = first_author_url
                                dict_xxx_paper_new['dict_paper_info'] = dict_paper_info
                                dict_xxx_paper_new['article_url'] = article_url
                                try:
                                    pubmed_free_url = dict_xxx_paper_new['pubmed_free_url'] 
                                    if 'http' not in pubmed_free_url:
                                        pubmed_free_url = f'{BASE_URL_PUBMED_FREE}{pubmed_free_url}'
                                        dict_xxx_paper_new['pubmed_free_url'] = pubmed_free_url
                                except:
                                    pass
                                dict_xxx_paper.update(dict_xxx_paper_new)
                            list_dict_author_paper_new.append(dict_xxx_paper)
                        # Update Parent Paper list_dict_author_paper
                        data = {
                            'list_dict_author_paper': list_dict_author_paper_new
                        }
                        Paper.objects.filter(id=q_paper_selected.id).update(**data)
                        q_paper_selected.refresh_from_db()
                
                # Update Parent Paper     
                data = {
                    'list_author_paper_id': list_author_paper_id
                }
                Paper.objects.filter(id=q_paper_selected.id).update(**data)
                q_paper_selected.refresh_from_db()

                

        #--------------------------------------------------------------------------------------------------------------------------------------
        print(f'Selected Paper ({q_paper_selected.id}) Parsing End')
        #--------------------------------------------------------------------------------------------------------------------------------------
        return True
    




#--------------------------------------------------------------------------------------------------------------------------------------
# PMID 획득하기
#--------------------------------------------------------------------------------------------------------------------------------------
def get_pmid_on_pmc_site(parsing_url, q_paper_selected_id):
    list_dict_author_info = []
    n = random.randint(0, 9)
    headers = get_random_header()
    response = requests.get(parsing_url, headers=headers)
    if response.status_code != 200:
        PROXY_PORT = LIST_PORT_FINEPROXY[n]
        proxy = f"http://{FINEPROXY_USER_NAME}:{FINEPROXY_USER_PASSWORD}@FINEPROXY.XYZ:{PROXY_PORT}"
        response = requests.get(parsing_url, proxies={
            'http': proxy,
            'https': proxy
        })
        if response.status_code != 200:
            PROXY_PORT = LIST_PORT_SMARTPROXY[n]
            proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{PROXY_PORT}"
            response = requests.get(parsing_url, proxies={
                'http': proxy,
                'https': proxy
            })
            if response.status_code != 200:
                # selenium
                print(f" Tryed Selenium Status code: {response.status_code}")
                driver = boot_google_chrome_driver_in_study_tasks(n)
                driver.get(parsing_url)
                source = driver.page_source
                soup = BeautifulSoup(source, 'html.parser')
                print(f"Failed to access given article url using Smartproxy Request. Status code: {response.status_code}")
            else:
                # Smartproxy request
                print(f" Success in Smartproxy Request Status code: {response.status_code}")
                source = response.content
                soup = BeautifulSoup(source, 'html.parser')
            print(f"Failed to access given article url using Fineproxy Request. Status code: {response.status_code}")
        else:
            # Fineproxy request
            print(f" Success in Fineproxy Request Status code: {response.status_code}")
            source = response.content
            soup = BeautifulSoup(source, 'html.parser')
        print(f"Failed to access given article url using Ordinary Request. Status code: {response.status_code}")
    else:
        # Ordinary request
        print(f" Success in Ordinary Request Status code: {response.status_code}")
        source = response.content
        soup = BeautifulSoup(source, 'html.parser')
        


    results = soup.find('section', class_='front-matter')
    author_elements = results.find_all('a', class_='usa-link')
    pmid = None
    i = 0
    for author_element in author_elements:
        # print('author_element', author_element)
        dict_author_info = {}
        # print("///////////////////////////////////////////////////////////////////")
        author_name = author_element.get_text()
        # print(author_name)
        author_url = author_element['href']
        # print(author_url)
        if author_name not in LIST_NOT_AUTHOR_NAME:
            if 'http' not in author_name:
                dict_author_info['author_name'] = author_name 
                dict_author_info['author_url'] = author_url 
                if dict_author_info not in list_dict_author_info:
                    try:
                        author_name_int = int(author_name)
                        pmid = author_name_int 
                    except:
                        pass
        i = i + 1
    if q_paper_selected_id is not None:
        data = {
            'pmid': pmid,
        }
        Paper.objects.filter(id=q_paper_selected_id).update(**data)
    return pmid

































#############################################################################################################################################
#
#                                             Parsing Selected Paper Basic info 
#
#############################################################################################################################################


#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-1. 선택한 Paper의 PMC url로 기본정보 및 Reference / Relevant / Author Paper 기본정보 획득
#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-1-1. Reference Paper Parsing on PMC or Pubmed: 선택한 Paper의 Similar Paper 정보 긁어오기 
#--------------------------------------------------------------------------------------------------------------------------------------
def scraping_reference_paper_info_on_pmc_or_pubmed(parsing_url):
    random_sec = random.uniform(1, 2)
    time.sleep(random_sec)
    soup = get_soup_using_url_only(parsing_url)

    if soup is None:
        return None

    print('# reference url info 수집 (PMC 에서)')
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Selected Paper Citation Parsing
    """ 
    <section class="front-matter">
        <div class="ameta p font-secondary font-xs">
            <hgroup>
                <h1>
                    Identifying stakeholder preferences for communicating impact from medical research: a mixed methods study
                </h1>
            </hgroup>
            <div class="cg p">
                <a href="https://pubmed.ncbi.nlm.nih.gov/?term=%22Pitrolino%20K%22%5BAuthor%5D" class="usa-link" aria-describedby="id1" aria-expanded="false">
                    <span class="name western">
                        Katherine Pitrolino
                    </span>
                </a>
                <div hidden="hidden" id="id1">
                    <h3>
                        <span class="name western">
                            Katherine Pitrolino
                        </span>
                    </h3>
                    <div class="p">
                        <sup>
                            1
                        </sup>
                        College of Science and Engineering, University of Derby, Derby, DE22 1GB UK 
                    </div>
                    <div class="p">
                        Find articles by 
                        <a href="https://pubmed.ncbi.nlm.nih.gov/?term=%22Pitrolino%20K%22%5BAuthor%5D" class="usa-link">
                            <span class="name western">
                                Katherine Pitrolino
                            </span>
                        </a>
                    </div>
                </div>
                <sup>
                    1,
                </sup>
                <sup>
                    ✉
                </sup>
                ,
                <a href="https://pubmed.ncbi.nlm.nih.gov/?term=%22Samarasinghe%20B%22%5BAuthor%5D" class="usa-link" aria-describedby="id2" aria-expanded="false">
                    <span class="name western">
                        Buddhini Samarasinghe
                    </span>
                </a>
                <div hidden="hidden" id="id2">
                    <h3>
                        <span class="name western">
                            Buddhini Samarasinghe
                        </span>
                    </h3>
                    <div class="p">
                        <sup>
                            2
                        </sup>
                        Evaluation and Analysis Team, Medical Research Council, Swindon, SN2 1FL UK 
                    </div>
                    <div class="p">
                        Find articles by 
                        <a href="https://pubmed.ncbi.nlm.nih.gov/?term=%22Samarasinghe%20B%22%5BAuthor%5D" class="usa-link">
                            <span class="name western">
                                Buddhini Samarasinghe
                            </span>
                        </a>
                    </div>
                </div>
                <sup>
                    2
                </sup>
                ,
                <a href="https://pubmed.ncbi.nlm.nih.gov/?term=%22Pringle%20A%22%5BAuthor%5D" class="usa-link" aria-describedby="id3" aria-expanded="false">
                    <span class="name western">
                        Andy Pringle
                    </span>
                </a>
                <div hidden="hidden" id="id3">
                    <h3>
                        <span class="name western">
                            Andy Pringle
                        </span>
                    </h3>
                    <div class="p">
                        <sup>
                            1
                        </sup>
                        College of Science and Engineering, University of Derby, Derby, DE22 1GB UK 
                    </div>
                    <div class="p">
                        Find articles by 
                        <a href="https://pubmed.ncbi.nlm.nih.gov/?term=%22Pringle%20A%22%5BAuthor%5D" class="usa-link">
                            <span class="name western">
                                Andy Pringle
                            </span>
                        </a>
                    </div>
                </div>
                <sup>
                    1
                </sup>
                , 
                <a href="https://pubmed.ncbi.nlm.nih.gov/?term=%22Viney%20I%22%5BAuthor%5D" class="usa-link" aria-describedby="id4" aria-expanded="false">
                    <span class="name western">
                        Ian Viney
                    </span>
                </a>
                <div hidden="hidden" id="id4">
                    <h3>
                        <span class="name western">
                            Ian Viney
                        </span>
                    </h3>
                    <div class="p">
                        <sup>
                            2
                        </sup>
                        Evaluation and Analysis Team, Medical Research Council, Swindon, SN2 1FL UK 
                    </div>
                    <div class="p">
                        Find articles by 
                        <a href="https://pubmed.ncbi.nlm.nih.gov/?term=%22Viney%20I%22%5BAuthor%5D" class="usa-link">
                            <span class="name western">
                                Ian Viney
                            </span>
                        </a>
                    </div>
                </div>
                <sup>
                    2
                </sup>
            </div>
            <ul class="d-buttons inline-list">
                <li>
                    <button class="d-button" aria-controls="aip_a" aria-expanded="false">
                        Author information
                    </button>
                </li>
                <li>
                    <button class="d-button" aria-controls="anp_a" aria-expanded="false">
                        Article notes
                    </button>
                </li>
                <li>
                    <button class="d-button" aria-controls="clp_a" aria-expanded="false">
                        Copyright and License information
                    </button>
                </li>
            </ul>
            <div class="d-panels font-secondary-light">
                <div id="aip_a" class="d-panel p" style="display: none">
                    <div class="p" id="Aff1">
                        <sup>
                            1
                        </sup>
                        College of Science and Engineering, University of Derby, Derby, DE22 1GB UK 
                    </div>
                    <div id="Aff2">
                        <sup>
                            2
                        </sup>
                        Evaluation and Analysis Team, Medical Research Council, Swindon, SN2 1FL UK 
                    </div>
                    <div class="author-notes p"><div class="fn" id="_fncrsp93pmc__">
                        <sup>
                            ✉
                        </sup>
                        <p class="display-inline">
                            Corresponding author.
                        </p>
                    </div>
                </div>
            </div>
            <div id="anp_a" class="d-panel p" style="display: none">
                <div class="notes p">
                    <section id="historyarticle-meta1" class="history">
                        <p>
                            Received 2024 Mar 20; Accepted 2024 Sep 26; Collection date 2024.
                        </p>
                    </section>
                </div>
            </div>
            <div id="clp_a" class="d-panel p" style="display: none">
                <div>
                    © The Author(s) 2024
                </div>
                <p>
                    <strong>
                        Open Access
                    </strong> 
                    This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit 
                    <a href="https://creativecommons.org/licenses/by/4.0/" class="usa-link usa-link--external" data-ga-action="click_feat_suppl" target="_blank" rel="noopener noreferrer">
                        http://creativecommons.org/licenses/by/4.0/
                    </a>
                    .
                </p>
                <div class="p">
                    <a href="/about/copyright/" class="usa-link">
                        PMC Copyright notice
                    </a>
                </div>
            </div>
        </div>
            <div>
                PMCID: PMC11520885&nbsp;&nbsp;PMID: 
                <a href="https://pubmed.ncbi.nlm.nih.gov/39472931/" class="usa-link">
                    39472931
                </a>
            </div>
        </div>
    </section>
    """
    #--------------------------------------------------------------------------------------------------------------------------------------
    dict_paper_info = {}
    try:
        pmcid = parsing_url.replace('https://pmc.ncbi.nlm.nih.gov/articles/', '')
        pmcid = pmcid.replace('/', '')
    except:
        pmcid = None
    dict_paper_info['pmcid'] = pmcid
    
    # Title
    results = soup.find('section', class_='front-matter')
    title_multi_line = results.find('h1').get_text()
    try:
        title = ' '.join(title_multi_line.split())
    except:
        title = title_multi_line
    dict_paper_info['title'] = title
    
    # Author
    list_dict_author_info = []
    author_elements = results.find_all('a', class_='usa-link')
    pmid = None
    pmid_url = None
    first_author_name = None
    first_author_url = None
    i = 0
    for author_element in author_elements:
        # print('author_element', author_element)
        dict_author_info = {}
        # print("///////////////////////////////////////////////////////////////////")
        author_name = author_element.get_text()
        # print(author_name)
        author_url = author_element['href']
        # print(author_url)
        if author_name not in LIST_NOT_AUTHOR_NAME:
            if 'http' not in author_name:
                dict_author_info['author_name'] = author_name 
                dict_author_info['author_url'] = author_url 
                if dict_author_info not in list_dict_author_info:
                    try:
                        author_name_int = int(author_name)
                        pmid = author_name_int 
                        pmid_url = author_url
                    except:
                        if i == 0:
                            first_author_name  = dict_author_info['author_name']
                            first_author_url = dict_author_info['author_url']
                        list_dict_author_info.append(dict_author_info)
        i = i + 1
    
    dict_paper_info['first_author_name'] = first_author_name
    dict_paper_info['first_author_url'] = first_author_url
    dict_paper_info['list_dict_author_info'] = list_dict_author_info
    dict_paper_info['pmid'] = pmid
    dict_paper_info['pmid_url'] = pmid_url
    
    # DOI
    citation_element = soup.find('section', class_='pmc-layout__citation')
    doi_link = citation_element.find('a', class_='usa-link usa-link--external')
    doi = doi_link.get_text()
    doi_url = doi_link['href'] if doi_link else None
    dict_paper_info['doi'] = doi
    dict_paper_info['doi_url'] = doi_url

    # Abstract
    abstract_text = None
    abstract_element = soup.find('section', class_='abstract')
    abstract_text_elements = abstract_element.find_all('p')
    for abstract_text_element in abstract_text_elements:
        abstract_text = abstract_text_element.get_text()
        if abstract_text is not None and abstract_text != '':
            # Convert to a single line
            abstract_text = ' '.join(abstract_text.split())
    dict_paper_info['abstract'] = abstract_text

    # 4. PDF Donwnload
    pdf_url = None
    try:
        pdf_element = soup.find('section', class_='pmc-sidenav__container')
        pdf_url_elements = pdf_element.find_all('a', class_='usa-button')
        for pdf_url_element in pdf_url_elements:
            try:
                pdf_url = pdf_url_element['href']
            except:
                pdf_url = None 
            if '.pdf' in pdf_url:
                pdf_url = parsing_url + pdf_url 
    except:
        pass
    dict_paper_info['pdf_url'] = pdf_url

    # Reference Parsing
    """ 
    <li id="ref19">
        <span class="label">
            19.
        </span>
        <cite>
            Olander A, Bremer A, Sundler AJ, Hagiwara MA, Andersson H. Assessment of patients with suspected sepsis in ambulance services: a qualitative interview study. BMC Emerg Med. 2021 Apr 09;21(1):45. doi: 10.1186/s12873-021-00440-4. 
            <a href="https://bmcemergmed.biomedcentral.com/articles/10.1186/s12873-021-00440-4" class="usa-link usa-link--external" data-ga-action="click_feat_suppl" target="_blank" rel="noopener noreferrer">
                https://bmcemergmed.biomedcentral.com/articles/10.1186/s12873-021-00440-4
            </a>
            .10.1186/s12873-021-00440-4
        </cite> 
        [
            <a href="https://doi.org/10.1186/s12873-021-00440-4" class="usa-link usa-link--external" data-ga-action="click_feat_suppl" target="_blank" rel="noopener noreferrer">
                DOI
            </a>
        ] 
        [
            <a href="/articles/PMC8033740/" class="usa-link">
                PMC free article
            </a>
        ] 
        [
            <a href="https://pubmed.ncbi.nlm.nih.gov/33836665/" class="usa-link">
                PubMed
            </a>
        ] 
        [
            <a href="https://scholar.google.com/scholar_lookup?journal=BMC%20Emerg%20Med&amp;title=Assessment%20of%20patients%20with%20suspected%20sepsis%20in%20ambulance%20services:%20a%20qualitative%20interview%20study&amp;author=A%20Olander&amp;author=A%20Bremer&amp;author=AJ%20Sundler&amp;author=MA%20Hagiwara&amp;author=H%20Andersson&amp;volume=21&amp;issue=1&amp;publication_year=2021&amp;pages=45&amp;pmid=33836665&amp;doi=10.1186/s12873-021-00440-4&amp;" class="usa-link usa-link--external" data-ga-action="click_feat_suppl" target="_blank" rel="noopener noreferrer">
                Google Scholar
            </a>
        ]
    </li>
    """
    list_dict_reference_paper = []
    result = soup.find('section', class_="ref-list")
    sub_resluts = result.find_all('li')
    n = 1
    for sub_reslut in sub_resluts:
        other_url = None
        pmid = None
        try:
            cite = sub_reslut.find('cite').text
        except:
            cite = None
        # Extract the DOI link
        try:
            doi_link = sub_reslut.find('a', string='DOI')['href']
            if 'https://doi.org/' in doi_link:
                doi = doi_link.replace('https://doi.org/', '')
            else:
                if 'doi.org/' in doi_link:
                    doi = doi_link.split('doi.org/')[-1]
                else:
                    doi = doi_link
        except:
            doi = None
            doi_link = None 
        # Extract the PubMed link
        try:
            pubmed_link = sub_reslut.find('a', string='PubMed')['href']
            pubmed_url = pubmed_link
            if pubmed_url is not None:
                if BASE_URL_PUBMED in pubmed_url:
                    pmid_text = pubmed_url.replace(BASE_URL_PUBMED, '')
                    if '/' in pmid_text:
                        pmid_text = pmid_text.replace('/', '')
                        try:
                            pmid = int(pmid_text)
                        except:
                            pmid = None
        except:
            pubmed_url = None
        # Extract the PubMed free article link
        try:
            pubmed_free_link = sub_reslut.find('a', string='PMC free article')['href']
            pubmed_free_url = BASE_URL_PUBMED_FREE + pubmed_free_link
            if pmid is None:
                pmid = get_pmid_on_pmc_site(pubmed_free_url, None)
        except:
            pubmed_free_url = None
        # Extract the Google Scholar link
        try:
            google_scholar_url = sub_reslut.find('a', string='Google Scholar')['href']
        except:
            google_scholar_url = None
        # 선택된 Paper에 Reference 정보 등록
        dict_reference_paper = {
            'id': n,
            'q_paper_id': None,
            'cite': cite,
            'doi': doi,
            'doi_url': doi_link,
            'pmid': pmid,
            'pubmed_url': pubmed_url,
            'pubmed_free_url': pubmed_free_url,
            'google_scholar_url': google_scholar_url,
            'other_url': other_url,
        }
        # print(f'dict_reference_paper, {dict_reference_paper}')
        if dict_reference_paper not in list_dict_reference_paper:
            list_dict_reference_paper.append(dict_reference_paper)
        n = n + 1
    dict_paper_info['list_dict_reference_paper'] = list_dict_reference_paper
    
    return dict_paper_info


#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-1. 선택한 Paper의 PMC url로 기본정보 및 Reference / Relevant / Author Paper 기본정보 획득
#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-1-2. Similar Paper Parsing on pubmed: 선택한 Paper의 Similar Paper 정보 긁어오기 
"""
    <article class="full-docsum" data-rel-pos="1">
        <div class="item-selector-wrap selectors-and-actions first-selector">
            <input aria-labelledby="result-selector-label" class="search-result-selector" id="select-29204457" name="search-result-selector-29204457" type="checkbox" value="29204457"/>
            <label class="search-result-position" for="select-29204457">
                <span class="position-number">
                    1
                </span>
            </label>
            <div class="result-actions-bar side-bar">
                <div class="cite dropdown-block">
                    <button aria-haspopup="true" class="cite-search-result trigger result-action-trigger citation-dialog-trigger" data-all-citations-url="/29204457/citations/" data-citation-style="nlm" data-ga-action="cite" data-ga-category="save_share" data-ga-label="open" data-pubmed-format-link="/29204457/export/">
                        Cite
                    </button>
                </div>
                <div class="share dropdown-block">
                    <button aria-haspopup="true" class="share-search-result trigger result-action-trigger share-dialog-trigger" data-facebook-url="http://www.facebook.com/sharer/sharer.php?u=https%3A//pubmed.ncbi.nlm.nih.gov/29204457/" data-permalink-url="https://pubmed.ncbi.nlm.nih.gov/29204457/" data-twitter-url="http://twitter.com/intent/tweet?text=Employing%20a%20Qualitative%20Description%20Approach%20in%20Health%20Care%20Research.%20https%3A//pubmed.ncbi.nlm.nih.gov/29204457/">
                        Share
                    </button>
                </div>
            </div>
        </div>

        <div class="docsum-wrap">
            <div class="docsum-content">
                <a class="docsum-title" data-article-id="29204457" data-full-article-url="from_linkname=pubmed_pubmed&amp;from_from_uid=29204457&amp;from_pos=1" data-ga-action="1" data-ga-category="result_click" data-ga-label="29204457" href="/29204457/" ref="linksrc=docsum_link&amp;article_id=29204457&amp;ordinalpos=1&amp;page=1">
                    Employing a Qualitative Description Approach in Health Care Research.
                </a>
                <div class="docsum-citation full-citation">
                    <span class="docsum-authors full-authors">
                        Bradshaw C, Atkinson S, Doody O.
                    </span>
                    <span class="docsum-authors short-authors">
                        Bradshaw C, et al.
                    </span>
                    <span class="docsum-journal-citation full-journal-citation">
                        Glob Qual Nurs Res. 2017 Nov 24;4:2333393617742282. doi: 10.1177/2333393617742282. eCollection 2017 Jan-Dec.
                    </span>
                    <span class="docsum-journal-citation short-journal-citation">
                        Glob Qual Nurs Res. 2017.
                    </span>
                    <span class="citation-part">
                        PMID: 
                        <span class="docsum-pmid">
                            29204457
                        </span>
                    </span>
                    <span class="free-resources spaced-citation-item citation-part">
                        Free PMC article.
                    </span>
                </div>
                <div class="docsum-snippet">
                    <div class="full-view-snippet">
                    </div>
                    <div class="short-view-snippet">
                    </div>
                </div>
            </div>
            <div class="result-actions-bar bottom-bar">
                <div class="cite dropdown-block">
                    <button aria-haspopup="true" class="cite-search-result trigger result-action-trigger citation-dialog-trigger" data-all-citations-url="/29204457/citations/" data-citation-style="nlm" data-ga-action="cite" data-ga-category="save_share" data-ga-label="open" data-pubmed-format-link="/29204457/export/">
                        Cite
                    </button>
                </div>
                <div class="share dropdown-block">
                    <button aria-haspopup="true" class="share-search-result trigger result-action-trigger share-dialog-trigger" data-facebook-url="http://www.facebook.com/sharer/sharer.php?u=https%3A//pubmed.ncbi.nlm.nih.gov/29204457/" data-permalink-url="https://pubmed.ncbi.nlm.nih.gov/29204457/" data-twitter-url="http://twitter.com/intent/tweet?text=Employing%20a%20Qualitative%20Description%20Approach%20in%20Health%20Care%20Research.%20https%3A//pubmed.ncbi.nlm.nih.gov/29204457/">
                        Share
                    </button>
                </div>
                <div class="in-clipboard-label" hidden="hidden">
                    Item in Clipboard
                </div>
            </div>
        </div>
    </article>
"""
#--------------------------------------------------------------------------------------------------------------------------------------
def scraping_similar_paper_info_on_pubmed(pmid_paper, max_page):
    print(f'# PMID 활용 Similar Paper Scraping on PubMed 시작, {pmid_paper}')
    list_dict_similar_paper_info_from_pubmed = []
    random_sec = random.uniform(2, 4)
    last_page = 1
    
    # check Total Page
    page = 1
    parsing_url = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed&from_uid={pmid_paper}&page={page}'
    soup = get_soup_using_url_only(parsing_url)
    
    if soup is not None:
        try:
            total_page_element = soup.find('label', class_="of-total-pages").get_text(strip=True)
            print(f'total_page_element: {total_page_element}')
            try:
                total_page = int(total_page_element.split('of')[-1])
            except:
                total_page = None

            if total_page is not None:
                if total_page > max_page:
                    last_page = max_page
                else:
                    last_page = total_page
        except:
            total_page = None
    else:
        return None
    
    print(f'total_page: {total_page}')
    if total_page == None:
        return None

    # Parsing Similar Paper Basic Info on Pubmed
    page = 1
    while page <= last_page:
        print(f'page: {page}')
        parsing_url = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed&from_uid={pmid_paper}&page={page}'
        soup = get_soup_using_url_only(parsing_url)
        if soup is not None:
            article_elements = soup.find_all('article', class_="full-docsum")
            i = 1
            for article_element in article_elements:
                dict_similar_paper_info_from_pubmed = {}
                # Title
                title_element = article_element.find('a', class_="docsum-title")
                title_href = title_element['href']
                title_href = BASE_URL_PUBMED + title_href
                title_text = title_element.get_text().strip()
                dict_similar_paper_info_from_pubmed['title'] = title_text
                dict_similar_paper_info_from_pubmed['pubmed_url'] = title_href
                # Citation
                citation_element = article_element.find('div', class_="docsum-citation")
                # Author Info
                author_element = citation_element.find('span', class_='docsum-authors full-authors')
                if author_element:
                    full_authors_text = author_element.get_text(strip=True)
                else:
                    full_authors_text = None 
                dict_similar_paper_info_from_pubmed['full_authors_name'] = full_authors_text
                # Journal info and DOI
                journal_element = citation_element.find('span', class_='docsum-journal-citation full-journal-citation')
                if journal_element:
                    # Get the text inside the span and strip any leading/trailing whitespace
                    full_journal_text = journal_element.get_text(strip=True)
                    if 'doi' in full_journal_text:
                        doi_text = full_journal_text.split('doi: ')[-1]
                        doi_text = doi_text.split('. ')[0]
                        doi_text = doi_text.rstrip('.')
                        doi_full_text = 'doi: ' + doi_text + '.'
                        if doi_full_text in full_journal_text:
                            journal_text = full_journal_text.replace(doi_full_text, '')
                        else:
                            journal_text = full_journal_text
                    else:
                        doi_text = None
                        journal_text = full_journal_text
                else:
                    journal_text = None 
                    doi_text = None
                dict_similar_paper_info_from_pubmed['journal'] = journal_text
                dict_similar_paper_info_from_pubmed['doi'] = doi_text
                if doi_text is not None:
                    dict_similar_paper_info_from_pubmed['doi_url'] = BASE_URL_DOI + doi_text
                else:
                    dict_similar_paper_info_from_pubmed['doi_url'] = None
                # PMID
                site_citation_element = citation_element.find('span', class_='citation-part')
                if site_citation_element:
                    site_citation_text = site_citation_element.get_text(strip=True)
                    if 'PMID:' in site_citation_text:
                        pmid_text = site_citation_text.replace('PMID:', '')
                        try:
                            pmid = int(pmid_text)
                        except:
                            pmid = None 
                    else:
                        pmid = None
                else:
                    pmid = None
                dict_similar_paper_info_from_pubmed['pmid'] = pmid
                if dict_similar_paper_info_from_pubmed not in list_dict_similar_paper_info_from_pubmed:
                    list_dict_similar_paper_info_from_pubmed.append(dict_similar_paper_info_from_pubmed)
                i = i + 1
        page = page + 1

    # driver.quit()
    print(f'len(list_dict_similar_paper_info_from_pubmed), {len(list_dict_similar_paper_info_from_pubmed)}')
    return list_dict_similar_paper_info_from_pubmed


#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-1. 선택한 Paper의 PMC url로 기본정보 및 Reference / Relevant / Author Paper 기본정보 획득
#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-1-3. Cited by Other Paper Parsing on pubmed: 선택한 Paper를 Citation한 Paper 정보 긁어오기 
#--------------------------------------------------------------------------------------------------------------------------------------
def scraping_cited_paper_info_on_pubmed(pmid_paper, max_page):
    print(f'# PMID 활용 Cited Paper Scraping on PubMed 시작, {pmid_paper}')
    list_dict_cited_paper_info_from_pubmed = []
    random_sec = random.uniform(2, 4)
    last_page = 1
    
    # check Total Page
    page = 1
    parsing_url = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid={pmid_paper}&page={page}'
    soup = get_soup_using_url_only(parsing_url)

    if soup is not None:
        try:
            total_page_element = soup.find('label', class_="of-total-pages").get_text(strip=True)
            print(f'total_page_element: {total_page_element}')
            try:
                total_page = int(total_page_element.split('of')[-1])
            except:
                total_page = None

            if total_page is not None:
                if total_page > max_page:
                    last_page = max_page
                else:
                    last_page = total_page
        except:
            total_page = None
    else:
        return None
    
    print(f'total_page: {total_page}')
    if total_page == None:
        return None

    # Parsing Similar Paper Basic Info on Pubmed
    page = 1
    while page <= last_page:
        print(f'page: {page}')
        parsing_url = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid={pmid_paper}&page={page}'
        soup = get_soup_using_url_only(parsing_url)
        if soup is not None:
            article_elements = soup.find_all('article', class_="full-docsum")
            i = 0
            for article_element in article_elements:
                dict_cited_paper_info_from_pubmed = {}
                # Title
                title_element = article_element.find('a', class_="docsum-title")
                title_href = title_element['href']
                title_href = BASE_URL_PUBMED + title_href
                title_text = title_element.get_text().strip()
                dict_cited_paper_info_from_pubmed['title'] = title_text
                dict_cited_paper_info_from_pubmed['pubmed_url'] = title_href
                # Citation
                citation_element = article_element.find('div', class_="docsum-citation")
                # Author Info
                author_element = citation_element.find('span', class_='docsum-authors full-authors')
                if author_element:
                    full_authors_text = author_element.get_text(strip=True)
                else:
                    full_authors_text = None 
                dict_cited_paper_info_from_pubmed['full_authors_name'] = full_authors_text
                # Journal info and DOI
                journal_element = citation_element.find('span', class_='docsum-journal-citation full-journal-citation')
                if journal_element:
                    # Get the text inside the span and strip any leading/trailing whitespace
                    full_journal_text = journal_element.get_text(strip=True)
                    if 'doi' in full_journal_text:
                        doi_text = full_journal_text.split('doi: ')[-1]
                        doi_text = doi_text.split('. ')[0]
                        doi_text = doi_text.rstrip('.')
                        doi_full_text = 'doi: ' + doi_text + '.'
                        if doi_full_text in full_journal_text:
                            journal_text = full_journal_text.replace(doi_full_text, '')
                        else:
                            journal_text = full_journal_text
                    else:
                        doi_text = None
                        journal_text = full_journal_text
                else:
                    journal_text = None 
                    doi_text = None
                dict_cited_paper_info_from_pubmed['journal'] = journal_text
                dict_cited_paper_info_from_pubmed['doi'] = doi_text
                if doi_text is not None:
                    dict_cited_paper_info_from_pubmed['doi_url'] = BASE_URL_DOI + doi_text
                else:
                    dict_cited_paper_info_from_pubmed['doi_url'] = None
                # PMID
                site_citation_element = citation_element.find('span', class_='citation-part')
                if site_citation_element:
                    site_citation_text = site_citation_element.get_text(strip=True)
                    if 'PMID:' in site_citation_text:
                        pmid_text = site_citation_text.replace('PMID:', '')
                        try:
                            pmid = int(pmid_text)
                        except:
                            pmid = None 
                    else:
                        pmid = None
                else:
                    pmid = None
                dict_cited_paper_info_from_pubmed['pmid'] = pmid
                if dict_cited_paper_info_from_pubmed not in list_dict_cited_paper_info_from_pubmed:
                    list_dict_cited_paper_info_from_pubmed.append(dict_cited_paper_info_from_pubmed)
                i = i + 1
        page = page + 1

    # driver.quit()
    print(f'len(list_dict_cited_paper_info_from_pubmed), {len(list_dict_cited_paper_info_from_pubmed)}')
    return list_dict_cited_paper_info_from_pubmed


#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-1. 선택한 Paper의 PMC url로 기본정보 및 Reference / Relevant / Author Paper 기본정보 획득
#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-1-4. First Author Paper Parsing on pubmed: 선택한 Paper의 주저자 Paper 정보 긁어오기 
#--------------------------------------------------------------------------------------------------------------------------------------
def scraping_first_author_paper_info_on_pubmed(q_paper_id, pmid_paper, max_page):
    print(f'# PMID 활용 First Author Paper Scraping on PubMed 시작, {pmid_paper}')
    list_dict_first_author_paper_info_from_pubmed = []
    random_sec = random.uniform(2, 4)
    last_page = 1

    q_paper_selected = Paper.objects.get(id=q_paper_id)
    first_author_name = q_paper_selected.first_author_name
    try:
        list_first_author_name = first_author_name.split(' ')
    except:
        list_first_author_name = None

    # check Total Page
    if list_first_author_name is not None:
        page = 1
        first_name = list_first_author_name[0]
        last_name = list_first_author_name[-1]
        print(f'first_name: {first_name}, last_name: {last_name}')
        parsing_url = f'https://pubmed.ncbi.nlm.nih.gov/?term=%22{first_name}%20{last_name}%22%5BAuthor%5D&page={page}'
        soup = get_soup_using_url_only(parsing_url)
        
        if soup is not None:
            try:
                total_page_element = soup.find('label', class_="of-total-pages").get_text(strip=True)
                print(f'total_page_element: {total_page_element}')
                try:
                    total_page = int(total_page_element.split('of')[-1])
                except:
                    total_page = None

                if total_page is not None:
                    if total_page > max_page:
                        last_page = max_page
                    else:
                        last_page = total_page
            except:
                total_page = None
        else:
            return None
    else:
        return None
    
    print(f'total_page: {total_page}')
    if total_page == None:
        return None

    # Parsing Similar Paper Basic Info on Pubmed
    page = 1
    while page <= last_page:
        print(f'page: {page}')
        parsing_url = f'https://pubmed.ncbi.nlm.nih.gov/?term=%22{first_name}%20{last_name}%22%5BAuthor%5D&page={page}'
        soup = get_soup_using_url_only(parsing_url)
        if soup is not None:
            article_elements = soup.find_all('article', class_="full-docsum")
            i = 0
            for article_element in article_elements:
                dict_first_author_paper_info_from_pubmed = {}
                # Title
                title_element = article_element.find('a', class_="docsum-title")
                title_href = title_element['href']
                title_href = BASE_URL_PUBMED + title_href
                title_text = title_element.get_text().strip()
                dict_first_author_paper_info_from_pubmed['title'] = title_text
                dict_first_author_paper_info_from_pubmed['pubmed_url'] = title_href
                # Citation
                citation_element = article_element.find('div', class_="docsum-citation")
                # Author Info
                author_element = citation_element.find('span', class_='docsum-authors full-authors')
                if author_element:
                    full_authors_text = author_element.get_text(strip=True)
                else:
                    full_authors_text = None 
                dict_first_author_paper_info_from_pubmed['full_authors_name'] = full_authors_text
                # Journal info and DOI
                journal_element = citation_element.find('span', class_='docsum-journal-citation full-journal-citation')
                if journal_element:
                    # Get the text inside the span and strip any leading/trailing whitespace
                    full_journal_text = journal_element.get_text(strip=True)
                    if 'doi' in full_journal_text:
                        doi_text = full_journal_text.split('doi: ')[-1]
                        doi_text = doi_text.split('. ')[0]
                        doi_text = doi_text.rstrip('.')
                        doi_full_text = 'doi: ' + doi_text + '.'
                        if doi_full_text in full_journal_text:
                            journal_text = full_journal_text.replace(doi_full_text, '')
                        else:
                            journal_text = full_journal_text
                    else:
                        doi_text = None
                        journal_text = full_journal_text
                else:
                    journal_text = None 
                    doi_text = None
                dict_first_author_paper_info_from_pubmed['journal'] = journal_text
                dict_first_author_paper_info_from_pubmed['doi'] = doi_text
                if doi_text is not None:
                    dict_first_author_paper_info_from_pubmed['doi_url'] = BASE_URL_DOI + doi_text
                else:
                    dict_first_author_paper_info_from_pubmed['doi_url'] = None
                # PMID
                site_citation_element = citation_element.find('span', class_='citation-part')
                if site_citation_element:
                    site_citation_text = site_citation_element.get_text(strip=True)
                    if 'PMID:' in site_citation_text:
                        pmid_text = site_citation_text.replace('PMID:', '')
                        try:
                            pmid = int(pmid_text)
                        except:
                            pmid = None 
                    else:
                        pmid = None
                else:
                    pmid = None
                dict_first_author_paper_info_from_pubmed['pmid'] = pmid
                if dict_first_author_paper_info_from_pubmed not in list_dict_first_author_paper_info_from_pubmed:
                    list_dict_first_author_paper_info_from_pubmed.append(dict_first_author_paper_info_from_pubmed)
                i = i + 1
        page = page + 1

    # driver.quit()
    print(f'len(list_dict_first_author_paper_info_from_pubmed), {len(list_dict_first_author_paper_info_from_pubmed)}')
    return list_dict_first_author_paper_info_from_pubmed














































#############################################################################################################################################
#
#                                                List Job for Multiprocessing
#
#############################################################################################################################################

def get_list_job_for_downloading_pdf(pdf_url, file_path):
    list_job = []
    return list_job

#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-2. 획득한 Reference / Relevant / Author 기본정보를 Multiprocessing용 List_job으로 세팅
#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-2-1. 멀티프로세싱을 위한 정보 세팅 : 수집한 reference url로 부터 Paper 정보 수집 및 PDF 다운로드 (1, 2, 3 방법론 중 하나만 만족해서 다운받으면 됨. 우선순위는 1, 2, 3번 순), 
"""
(q_paper_id, rel_id, article_url, doi, site_name, n)
"""
#--------------------------------------------------------------------------------------------------------------------------------------
def get_list_job_for_parsing_selected_paper_reference_data(q_paper_id, list_dict_reference_paper):
    related_type = 'reference'
    list_job = []
    list_job_pubmed_free = []
    list_job_pubmed = []
    list_job_google_scholar = []
    list_job_not_big_3 = []
    print(f' total list ref item : {len(list_dict_reference_paper)}')

    n = 0
    for dict_reference_paper in list_dict_reference_paper:
        try:
            rel_id = dict_reference_paper['id']
        except:
            rel_id = None 
        try:
            doi = dict_reference_paper['doi']
        except:
            doi = None
        if doi is not None:
            try:
                q_paper_rel = Paper.objects.filter(doi=doi).last()
            except:
                q_paper_rel = None
        else:
            q_paper_rel = None
        try:
            pubmed_free_url = dict_reference_paper['pubmed_free_url']
        except:
            pubmed_free_url = None 
        try:
            pubmed_url = dict_reference_paper['pubmed_url']
        except:
            pubmed_url = None
        try:
            google_scholar_url = dict_reference_paper['google_scholar_url']
        except:
            google_scholar_url = None

        
        # Conditions to add job in the list
        check_add_job_in_list = False
        if q_paper_rel is None and pubmed_free_url is not None and 'http' in pubmed_free_url:
            check_add_job_in_list = True 
        if q_paper_rel is None and  pubmed_url is not None and 'http' in pubmed_url:
            check_add_job_in_list = True 
        if q_paper_rel is None and google_scholar_url is not None and 'http' in google_scholar_url:
            check_add_job_in_list = True 
        if q_paper_rel is not None and q_paper_rel.check_download_pdf == False:
            check_add_job_in_list = True 

        # Add Job in List
        if check_add_job_in_list == True:
            if rel_id != 9999:
                if pubmed_free_url is not None and 'http' in pubmed_free_url:
                    site_name = 'pubmed_free'
                    list_job.append((q_paper_id, rel_id, pubmed_free_url, doi, site_name, related_type, dict_reference_paper, n))
                    list_job_pubmed_free.append(True)
                else:
                    if pubmed_url is not None and 'http' in pubmed_url:
                        site_name = 'pubmed'
                        list_job.append((q_paper_id, rel_id, pubmed_url, doi, site_name, related_type, dict_reference_paper, n))
                        list_job_pubmed.append(True)
                    else:
                        if google_scholar_url is not None and 'http' in google_scholar_url: 
                            site_name = 'google_scholar'
                            list_job.append((q_paper_id, rel_id, google_scholar_url, doi, site_name, related_type, dict_reference_paper, n))
                            list_job_google_scholar.append(True)
                        else:
                            list_job_not_big_3.append(True)
                            pass
                n = n + 1
                if n // 10 > 0:
                    n = 0
    

    num_list_dict_xxx_paper = len(list_dict_reference_paper)
    num_total_job = len(list_job_pubmed_free) + len(list_job_pubmed) + len(list_job_google_scholar) 
    print(f'total_list for Reference : {num_list_dict_xxx_paper}, total_job , {num_total_job}, pubmed_free : {len(list_job_pubmed_free)}, pubmed : {len(list_job_pubmed)}, google_scholar : {len(list_job_google_scholar)}, not_big_3 : {len(list_job_not_big_3)}')
    return list_job


#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-2. 획득한 Reference / Relevant / Author 기본정보를 Multiprocessing용 List_job으로 세팅
#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-2-2. 멀티프로세싱을 위한 정보 세팅 : 수집한 relevant url로 부터 Paper 정보 수집 및 PDF 다운로드 (1, 2, 3 방법론 중 하나만 만족해서 다운받으면 됨. 우선순위는 1, 2, 3번 순), 
""" 
list_dict_relevent_paper = [
    {
        "id": 1,
        "doi": "10.1021/acs.chemrev.4c00055", 
        "pmid": 39137296, 
        "title": "Self-Driving Laboratories for Chemistry and Materials Science.", 
        "doi_url": "https://doi.org/10.1021/acs.chemrev.4c00055", 
        "journal": "Chem Rev. 2024 Aug 28;124(16):9633-9732.  Epub 2024 Aug 13.", 
        "pubmed_url": "https://pubmed.ncbi.nlm.nih.gov/39137296/", 
        "full_authors_name": "Tom G, Schmid SP, Baird SG, Cao Y, Darvish K, Hao H, Lo S, Pablo-García S, Rajaonson EM, Skreta M, Yoshikawa N, Corapi S, Akkoc GD, Strieth-Kalthoff F, Seifrid M, Aspuru-Guzik A."
    },
    {},
    {},
]
"""
#--------------------------------------------------------------------------------------------------------------------------------------
def get_list_job_for_parsing_selected_paper_relevant_data(q_paper_id, list_dict_relevant_paper):
    related_type = 'relevant'
    site_name = 'pubmed'
    list_job = []
    n = 0
    for dict_relevant_paper in list_dict_relevant_paper:
        try:
            doi = dict_relevant_paper['doi']
        except:
            doi = None 
        if doi is not None:
            try:
                q_paper_rel = Paper.objects.filter(doi=doi).last()
            except:
                q_paper_rel = None
        else:
            q_paper_rel = None
        try:
            rel_id = dict_relevant_paper['id']
        except:
            rel_id = None 
        try:
            pubmed_url = dict_relevant_paper['pubmed_url']
        except:
            pubmed_url = None 

        # Conditions to add job in the list
        check_add_job_in_list = False
        # check_add_job_in_list = True
        if q_paper_rel is None and pubmed_url is not None and 'http' in pubmed_url:
            check_add_job_in_list = True 
        if q_paper_rel is not None and q_paper_rel.check_download_pdf == False and pubmed_url is not None and 'http' in pubmed_url:
            check_add_job_in_list = True 

        # Add Job in List
        if check_add_job_in_list == True:
            if rel_id != 9999:
                list_job.append((q_paper_id, rel_id, pubmed_url, doi, site_name, related_type, dict_relevant_paper, n))
                n = n + 1
                if n // 10 > 0:
                    n = 0

    num_tot_job = len(list_job)
    print(f'num_tot_job for Relevant : {num_tot_job}')
    return list_job


#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-2. 획득한 Reference / Relevant / Author 기본정보를 Multiprocessing용 List_job으로 세팅
#--------------------------------------------------------------------------------------------------------------------------------------
# B-1-2-3. 멀티프로세싱을 위한 정보 세팅 : 수집한 author url로 부터 Paper 정보 수집 및 PDF 다운로드 (1, 2, 3 방법론 중 하나만 만족해서 다운받으면 됨. 우선순위는 1, 2, 3번 순), 
""" 
list_dict_author_paper = [
    {
        'id': id,
        'doi': doi,
        'pmid': pmid,
        'title': title,
        'doi_url': doi_url,
        'journal': journal,
        'pubmed_url': pubmed_url,
    }
]
"""
#--------------------------------------------------------------------------------------------------------------------------------------
def get_list_job_for_parsing_selected_paper_author_data(q_paper_id, list_dict_author_paper):
    related_type = 'author'
    site_name = 'pubmed'
    list_job = []
    n = 0
    for dict_author_paper in list_dict_author_paper:
        try:
            doi = dict_author_paper['doi']
        except:
            doi = None 
        
        if doi is not None:
            try:
                q_paper_rel = Paper.objects.filter(doi=doi).last()
            except:
                q_paper_rel = None
        else:
            q_paper_rel = None
        try:
            rel_id = dict_author_paper['id']
        except:
            rel_id = None 
        try:
            pubmed_url = dict_author_paper['pubmed_url']
        except:
            pubmed_url = None 

        # Conditions to add job in the list
        check_add_job_in_list = False
        if q_paper_rel is None and pubmed_url is not None and 'http' in pubmed_url:
            check_add_job_in_list = True 
        if q_paper_rel is not None and q_paper_rel.check_download_pdf == False and pubmed_url is not None and 'http' in pubmed_url:
            check_add_job_in_list = True 

        # Add Job in List
        if check_add_job_in_list == True:
            if rel_id != 9999:
                list_job.append((q_paper_id, rel_id, pubmed_url, doi, site_name, related_type, dict_author_paper, n))
                n = n + 1
                if n // 10 > 0:
                    n = 0

    num_tot_job = len(list_job)
    print(f'num_tot_job for Author : {num_tot_job}')
    return list_job






















#############################################################################################################################################
#############################################################################################################################################
#
#                              B-2: Google Scholar 검색리스트에서 선택한 Paper의 추가정보를 여러 저널 사이트에서 검색 및 정보 획득 
#
#   1. 선택한 Paper의 저널 사이트 확인 및 각 저널 사이트별 기본정보 획득 
#   2. 각 저널 사이트에서 Reference / Relevant / Author Paper 다운로드
#   3. 선택한 Paper 정보 업데이트
#
#############################################################################################################################################
#############################################################################################################################################


#--------------------------------------------------------------------------------------------------------------------------------------
# B-2 선택한 Paper에 관련된 추가정보 수집 (Reference 논문들, First Author 논문들, 비슷한 주제 논문들 정보 수집, 신규 Paper 쿼리 생성 및 PDF 다운로드)
""" 
    <div class="gsc_prf_il">
        <a href="/citations?view_op=view_org&amp;hl=en&amp;org=9499157965008867783" class="gsc_prf_ila">
            University of Adelaide
        </a>
    </div>

    <div class="gsc_prf_il" id="gsc_prf_ivh">
        Verified email at adelaide.edu.au
    </div>
    <div class="gsc_prf_il" id="gsc_prf_int">
        <a href="/citations?view_op=search_authors&amp;hl=en&amp;mauthors=label:lung" class="gsc_prf_inta gs_ibl">
            lung
        </a>
        <a href="/citations?view_op=search_authors&amp;hl=en&amp;mauthors=label:sleep_and_heart_health" class="gsc_prf_inta gs_ibl">
            sleep and heart health
        </a>
        <a href="/citations?view_op=search_authors&amp;hl=en&amp;mauthors=label:service_redesign" class="gsc_prf_inta gs_ibl">
            service redesign
        </a>
        <a href="/citations?view_op=search_authors&amp;hl=en&amp;mauthors=label:symptom_management" class="gsc_prf_inta gs_ibl">
            symptom management
        </a>
        <a href="/citations?view_op=search_authors&amp;hl=en&amp;mauthors=label:health_technology" class="gsc_prf_inta gs_ibl">
            health technology
        </a>
    </div>
"""
#--------------------------------------------------------------------------------------------------------------------------------------
@shared_task(time_limit=20000, soft_time_limit=19800)
def parsing_selected_paper_detail_info_on_google_scholar(q_paper_id):
    # B-2-1. 구글에서 획득한 정보로 각각의 사이트 접속해서 PDF 다운경로 획득 및 논문 관련 정보 획득'
    q_paper_selected = Paper.objects.get(id=q_paper_id)
    if q_paper_selected is not None:
        dict_paper_info_from_google = q_paper_selected.dict_paper_info_from_google
        if dict_paper_info_from_google is None or len(dict_paper_info_from_google) == 0:
            return None
    else:
        return False 
    
    random_sec = random.uniform(2, 4)
    driver = boot_google_chrome_driver_in_study_tasks(None)

    title_url = dict_paper_info_from_google['title_url'] 
    first_author_url = dict_paper_info_from_google['first_author_url'] 
    
    LIST_AUTHOR_NAME_PURIFIER = ['Professor']
    # B-2-2. First Author Paper Detail 정보 수집 및 PDF 다운로드
    if first_author_url:
        driver.get(first_author_url)
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')

        first_author_elements = soup.find('div', id='gsc_prf')
        # print('first_author_elements', first_author_elements)

        first_author_full_name = first_author_elements.find('div', id='gsc_prf_in').get_text()
        for ITEM in LIST_AUTHOR_NAME_PURIFIER:
            if ITEM in first_author_full_name:
                first_author_full_name = first_author_full_name.replace(ITEM, '')
                first_author_full_name = first_author_full_name.strip()
        # print('first_author_full_name', first_author_full_name)
        
        first_author_verified_elements = first_author_elements.find('div', id='gsc_prf_ivh')
        # print('first_author_verified_elements', first_author_verified_elements)
        first_author_verified_text = first_author_verified_elements.get_text()
        # print('first_author_verified_text', first_author_verified_text)

        list_first_author_interest = []
        first_author_interest_element = first_author_elements.find('div', id='gsc_prf_int')
        list_first_author_interest_element = first_author_interest_element.find_all('a')
        for first_author_interest in list_first_author_interest_element:
            first_author_interest_name = first_author_interest.get_text()
            first_author_interest_url = first_author_interest['href']
            list_first_author_interest.append({'first_author_interest_name': first_author_interest_name, 'first_author_interest_url': BASE_URL_GOOGLE_SCHOLAR + first_author_interest_url})
        # print('list_first_author_interest', list_first_author_interest)

        # First Author Papper 
        list_dict_first_author_paper = []
        first_author_paper_elements = soup.find_all('tr', class_='gsc_a_tr')
        for first_author_paper_element in first_author_paper_elements:
            dict_first_author_paper = {}
            # print('first_author_paper_element', first_author_paper_element)
            first_author_paper_element_td = first_author_paper_element.find('td', class_='gsc_a_t')
            try:
                first_author_paper_title_name = first_author_paper_element_td.find('a', class_='gsc_a_at').get_text()
            except:
                first_author_paper_title_name = None
            try:
                
                first_author_paper_title_url = first_author_paper_element_td.find('a')['href']
            except:
                first_author_paper_title_url = None
            try:
                published_year = first_author_paper_element_td.find('span', class_='gs_oph').get_text()
                published_year = published_year.replace(',', '')
                published_year = published_year.strip()
                published_year = int(published_year)
            except:
                published_year = None
            try:
                first_author_paper_author_elements = first_author_paper_element_td.find_all('div', class_='gs_gray')
                w = 0
                for first_author_paper_author_element in first_author_paper_author_elements:
                    first_author_paper_author_element_text = first_author_paper_author_element.get_text()
                    if w == 0:
                        list_first_author_paper_author_name = []
                        list_first_author_paper_author_name_raw = first_author_paper_author_element_text.split(',')
                        if list_first_author_paper_author_name_raw is not None and len(list_first_author_paper_author_name_raw) > 0:
                            for first_author_paper_author_name in list_first_author_paper_author_name_raw:
                                first_author_paper_author_name = first_author_paper_author_name.strip()
                                list_first_author_paper_author_name.append(first_author_paper_author_name)
                    if w == 1:
                        first_author_paper_author_publish_info = first_author_paper_author_element_text
                    w = w + 1
            except:
                list_first_author_paper_author_name = None 
                first_author_paper_author_publish_info = None
            
            dict_first_author_paper['first_author_paper_title_name'] = first_author_paper_title_name
            dict_first_author_paper['first_author_paper_title_url'] = BASE_URL_GOOGLE_SCHOLAR + first_author_paper_title_url
            dict_first_author_paper['published_year'] = published_year
            dict_first_author_paper['list_first_author_paper_author_name'] = list_first_author_paper_author_name
            dict_first_author_paper['first_author_paper_author_publish_info'] = first_author_paper_author_publish_info

    else:
        first_author_full_name = None
        list_first_author_interest = None

    dict_paper_info_from_google['first_author_full_name'] = first_author_full_name
    dict_paper_info_from_google['list_first_author_interest'] = list_first_author_interest
    dict_paper_info_from_google['list_dict_first_author_paper'] = list_dict_first_author_paper
    


        
    driver.quit() 
    return True


























#############################################################################################################################################
#############################################################################################################################################
#
#                                         C: 사이트별 정보 파싱 및 PDF 다운로드
#
#############################################################################################################################################
#############################################################################################################################################



#--------------------------------------------------------------------------------------------------------------------------------------
# C-0. Parsing Router : Paper Detail Info
#--------------------------------------------------------------------------------------------------------------------------------------
def f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf(q_paper_id, rel_id, parsing_url, doi, site_name, related_type, dict_paper_rel_info, n):
    
    if site_name == 'pubmed_free':
        return_value = parsing_paper_info_on_pubmed_free(q_paper_id, rel_id, parsing_url, related_type, dict_paper_rel_info)
    elif site_name == 'pubmed':
        return_value = parsing_paper_info_on_pubmed(q_paper_id, rel_id, parsing_url, related_type, dict_paper_rel_info)
    elif site_name == 'google_scholar':
        return_value = parsing_paper_info_on_google_scholar(q_paper_id, rel_id, parsing_url, related_type, dict_paper_rel_info)
    else:
        return_value = None
    if return_value is not None:
        print(f'rel_id: {rel_id} return_value is True')
    else:
        print(f'rel_id: {rel_id} return_value is None')
    return return_value
    






#--------------------------------------------------------------------------------------------------------------------------------------
# C-1. pubmed_free에서 선택한 Paper의 정보 긁어오기 및 PDF 저장
#--------------------------------------------------------------------------------------------------------------------------------------
def parsing_paper_info_on_pubmed_free(q_paper_id, rel_id, parsing_url, related_type, dict_paper_rel_info):
    print(f'C-1. q_paper_id: {q_paper_id},  rel_id: {rel_id},  parsing_url: {parsing_url}, related_type: {related_type}')
    
    random_sec = random.uniform(7, 10)
    dict_result = {}
    list_dict_reference_paper = []
    dict_paper_info = {}
    dict_paper_info['q_paper_parent_id'] = q_paper_id
    dict_paper_info['rel_id'] = rel_id
    dict_paper_info['parsing_url'] = parsing_url
    dict_paper_info['related_type'] = related_type

    article_url = None
    publisher_name = None
    dict_paper_info['article_url'] = article_url  # paper가 실린 곳 Journal의 기사 url
    dict_paper_info['publisher_name'] = publisher_name

    try:
        pmcid = dict_paper_rel_info['pmcid']
    except:
        pmcid = None
    try:
        pmid = dict_paper_rel_info['pmid']
    except:
        pmid = None
    try:
        doi = dict_paper_rel_info['doi']
    except:
        doi = None 
    try:
        doi_url = dict_paper_rel_info['doi_url']
    except:
        doi_url = None
    try:
        pdf_name = dict_paper_rel_info['pdf_name']
    except:
        pdf_name = None
    try:
        journal_name = dict_paper_rel_info['journal_name']
    except:
        journal_name = None
    try:
        publication_year = dict_paper_rel_info['pmcipublication_yeard']
    except:
        publication_year = None
    try:
        first_author_name = dict_paper_rel_info['first_author_name']
    except:
        first_author_name = None
    try:
        first_author_url = dict_paper_rel_info['first_author_url']
    except:
        first_author_url = None
          
    soup = get_soup_using_url_only(parsing_url)
    if soup is None:
        return None
    
    # 1. doi
    try:
        results = soup.find('section', class_='pmc-layout__citation')
        journal_name = results.find('div', class_="display-inline-block").get_text()
        doi_element = results.find('a', class_='usa-link')
        doi = doi_element.get_text()
        doi_url = doi_element['href']
    except:
        journal_name = None
        doi = None 
        doi_url = None 
    dict_paper_info['journal_name'] = journal_name
    dict_paper_info['doi'] = doi
    dict_paper_info['doi_url'] = doi_url
    dict_paper_info['doi'] = doi

    # 2. Title and Author
    try:
        results = soup.find('section', class_='front-matter')
        title = results.find('h1').get_text()
    except:
        title = None
    dict_paper_info['title'] = title
    # print(f'title: {title}')


    """ 
    results >>> 

    <a aria-describedby="id1" aria-expanded="false" class="usa-link" href="https://pubmed.ncbi.nlm.nih.gov/?term=%22Ozdemir%20BA%22%5BAuthor%5D">
        <span class="name western">
            Baris A Ozdemir
        </span>
    </a>
    <div hidden="hidden" id="id1">
        <h3><span class="name western">Baris A Ozdemir</span></h3>
        <div class="p">
            <sup>1</sup>
            Department of Outcomes Research, St George’s Vascular Institute, London, United Kingdom
        </div>
        <div class="p">
            Find articles by 
            <a class="usa-link" href="https://pubmed.ncbi.nlm.nih.gov/?term=%22Ozdemir%20BA%22%5BAuthor%5D">
                <span class="name western">
                    Baris A Ozdemir
                </span>
            </a>
        </div>
    </div>
    <sup>1,</sup>
    <sup>*</sup>, 
    """
    # Author
    list_dict_author_info = []
    pmid = None
    pubmed_url = None
    pmcid = parsing_url.split('/')[-2]
    pubmed_free_url = parsing_url
    try:
        author_elements = results.find_all('a', class_='usa-link')
        i = 0
        for author_element in author_elements:
            dict_author_info = {}
            author_name = author_element.get_text()
            author_url = author_element['href']
            if author_name not in LIST_NOT_AUTHOR_NAME:
                if 'http' not in author_name:
                    dict_author_info['author_name'] = author_name 
                    dict_author_info['author_url'] = author_url 
                    if dict_author_info not in list_dict_author_info:
                        try:
                            author_name_int = int(author_name)
                            pmid = author_name_int 
                            pubmed_url = author_url
                        except:
                            list_dict_author_info.append(dict_author_info)
            if i == 0:
                first_author_name = author_name
                first_author_url = author_url
            i = i + 1
    except:
        pass
    dict_paper_info['list_dict_author_info'] = list_dict_author_info
    dict_paper_info['pmid'] = pmid
    dict_paper_info['pubmed_url'] = pubmed_url
    dict_paper_info['pmcid'] = pmcid
    dict_paper_info['pubmed_free_url'] = pubmed_free_url
    
    # 3. Abstract
    try:
        abstract_element = soup.find('section', class_='abstract')  # HTML 택 포함해서 통채로 저장
        abstract_html = str(abstract_element)
    except:
        abstract_html = None
    try:
        abstract_text = abstract_element.get_text()
    except:
        abstract_text = None
    dict_paper_info['abstract_html'] = abstract_html
    dict_paper_info['abstract_text'] = abstract_text

    # 4. PDF Donwnload
    pdf_url = None
    try:
        pdf_element = soup.find('section', class_='pmc-sidenav__container')
        pdf_url_elements = pdf_element.find_all('a', class_='usa-button')
        for pdf_url_element in pdf_url_elements:
            try:
                pdf_url_text = pdf_url_element.get_test()
            except:
                pdf_url_text = None 
            try:
                pdf_url = pdf_url_element['href']
            except:
                pdf_url = None 
            if 'pdf' in pdf_url:
                pdf_url = parsing_url + pdf_url 
    except:
        pass
    dict_paper_info['pdf_url'] = pdf_url
    
    # 5. Reference Data Collect
    try:
        reference_elements = soup.find_all(class_="ref-list")
        # print(i, result)
        for reference_element in reference_elements:
            sub_resluts = reference_element.find_all('li')
            # print(sub_resluts)
            r_n = 1
            for sub_reslut in sub_resluts:
                dict_reference_paper = {}
                try:
                    r_cite = sub_reslut.find('cite').text
                except:
                    r_cite = None
                # Extract the DOI link
                try:
                    r_doi_link = sub_reslut.find('a', string='DOI')['href']
                except:
                    r_doi_link = None 
                # Extract the PubMed link
                try:
                    r_pubmed_link = sub_reslut.find('a', string='PubMed')['href']
                except:
                    r_pubmed_link = None
                # Extract the PubMed free article link
                try:
                    r_pubmed_free_link = sub_reslut.find('a', string='PMC free article')['href']
                except:
                    r_pubmed_free_link = None
                # Extract the Google Scholar link
                try:
                    r_google_scholar_link = sub_reslut.find('a', string='Google Scholar')['href']
                except:
                    r_google_scholar_link = None
                # 선택된 Paper에 Reference 정보 등록
                dict_reference_paper = {
                    'id': r_n,
                    'q_paper_id': None,
                    'cite': r_cite,
                    'doi_url': r_doi_link,
                    'pubmed_url': r_pubmed_link,
                    'pubmed_free_url': r_pubmed_free_link,
                    'google_scholar_url': r_google_scholar_link,
                }
                if dict_reference_paper not in list_dict_reference_paper:
                    list_dict_reference_paper.append(dict_reference_paper)
                r_n = r_n + 1
    except:
        list_dict_reference_paper = None
    dict_paper_info['list_dict_reference_paper'] = list_dict_reference_paper

    # Data Merge (기본 정보 획득시 + 디테일 정보 획득시)
    if related_type == 'reference':
        try:
            id_rel = dict_paper_rel_info['id']
        except:
            id_rel = None
        try:
            cite_rel = dict_paper_rel_info['cite']
        except:
            cite_rel = None
        try:
            doi_rel = dict_paper_rel_info['doi']
        except:
            doi_rel = None
        try:
            doi_url_rel = dict_paper_rel_info['doi_url']
        except:
            doi_url_rel = None
        try:
            pmid_rel = dict_paper_rel_info['pmid']
        except:
            pmid_rel = None
        try:
            pubmed_url_rel = dict_paper_rel_info['pubmed_url']
        except:
            pubmed_url_rel = None
        try:
            pubmed_free_url_rel = dict_paper_rel_info['pubmed_free_url']
        except:
            pubmed_free_url_rel = None
        try:
            google_scholar_url_rel = dict_paper_rel_info['google_scholar_url']
        except:
            google_scholar_url_rel = None
        try:
            other_url_rel = dict_paper_rel_info['other_url']
        except:
            other_url_rel = None
        if doi is None:
            doi = doi_rel
        if doi_url is None:
            doi_url = doi_url_rel
        if pmid is None:
            pmid = pmid_rel 
        if doi_url is None:
            doi_url = doi_url_rel
        try:
            cite = dict_paper_info['cite']
        except:
            cite = None 
        if cite is None:
            dict_paper_info['cite'] = cite_rel
        try:
            pubmed_url = dict_paper_info['pubmed_url']
        except:
            pubmed_url = None 
        if pubmed_url is None:
            dict_paper_info['pubmed_url'] = pubmed_url_rel
        try:
            pubmed_free_url = dict_paper_info['pubmed_free_url']
        except:
            pubmed_free_url = None 
        if pubmed_free_url is None:
            dict_paper_info['pubmed_free_url'] = pubmed_free_url_rel
        try:
            google_scholar_url = dict_paper_info['google_scholar_url']
        except:
            google_scholar_url = None 
        if google_scholar_url is None:
            dict_paper_info['google_scholar_url'] = google_scholar_url_rel
        try:
            other_url = dict_paper_info['other_url']
        except:
            other_url = None 
        if other_url is None:
            dict_paper_info['other_url'] = other_url_rel
        
    elif related_type == 'relevant':
        try:
            id_rel = dict_paper_rel_info['id']
        except:
            id_rel = None
        try:
            title_rel = dict_paper_rel_info['title']
        except:
            title_rel = None
        try:
            doi_rel = dict_paper_rel_info['doi']
        except:
            doi_rel = None
        try:
            doi_url_rel = dict_paper_rel_info['doi_url']
        except:
            doi_url_rel = None
        try:
            pmid_rel = dict_paper_rel_info['pmid']
        except:
            pmid_rel = None
        try:
            pubmed_url_rel = dict_paper_rel_info['pubmed_url']
        except:
            pubmed_url_rel = None
        try:
            journal_rel = dict_paper_rel_info['journal']
        except:
            journal_rel = None
        if doi is None:
            doi = doi_rel
        if doi_url is None:
            doi_url = doi_url_rel
        if pmid is None:
            pmid = pmid_rel 
        if title is None:
            title = title_rel
        if doi_url is None:
            doi_url = doi_url_rel
        try:
            pubmed_url = dict_paper_info['pubmed_url']
        except:
            pubmed_url = None 
        if pubmed_url is None:
            dict_paper_info['pubmed_url'] = pubmed_url_rel
        try:
            journal = dict_paper_info['journal']
        except:
            journal = None 
        if journal is None:
            dict_paper_info['journal'] = journal_rel
        
    elif related_type == 'author':
        try:
            id_rel = dict_paper_rel_info['id']
        except:
            id_rel = None
        try:
            title_rel = dict_paper_rel_info['title']
        except:
            title_rel = None
        try:
            doi_rel = dict_paper_rel_info['doi']
        except:
            doi_rel = None
        try:
            doi_url_rel = dict_paper_rel_info['doi_url']
        except:
            doi_url_rel = None
        try:
            pmid_rel = dict_paper_rel_info['pmid']
        except:
            pmid_rel = None
        try:
            pubmed_url_rel = dict_paper_rel_info['pubmed_url']
        except:
            pubmed_url_rel = None
        try:
            journal_rel = dict_paper_rel_info['journal']
        except:
            journal_rel = None
        if doi is None:
            doi = doi_rel
        if doi_url is None:
            doi_url = doi_url_rel
        if pmid is None:
            pmid = pmid_rel 
        if title is None:
            title = title_rel
        if doi_url is None:
            doi_url = doi_url_rel
        try:
            pubmed_url = dict_paper_info['pubmed_url']
        except:
            pubmed_url = None 
        if pubmed_url is None:
            dict_paper_info['pubmed_url'] = pubmed_url_rel
        try:
            journal = dict_paper_info['journal']
        except:
            journal = None 
        if journal is None:
            dict_paper_info['journal'] = journal_rel
   
    dict_result = {'title': title, 'doi': doi, 'doi_url': doi_url, 'pmid': pmid, 'pmcid': pmcid, 'first_author_name': first_author_name, 'first_author_url': first_author_url, 'publication_year': publication_year, 'dict_paper_info': dict_paper_info, 'list_dict_reference_paper': list_dict_reference_paper, 'pdf_url': pdf_url}
    return dict_result


   

#--------------------------------------------------------------------------------------------------------------------------------------
# C-2. pubmed에서 선택한 Paper의 정보 긁어오기 및 PDF 저장 
# - Pubmed는 Chrome Driver로 실행해야 함.
# - Pubmed는 headless chrome driver로는 forbidden 당함.
#--------------------------------------------------------------------------------------------------------------------------------------
def parsing_paper_info_on_pubmed(q_paper_id, rel_id, parsing_url, related_type, dict_paper_rel_info):
    print(f'C-2. q_paper_id: {q_paper_id},  rel_id: {rel_id},  parsing_url: {parsing_url}, related_type: {related_type}')

    random_sec = random.uniform(7, 10)
    dict_result = {}
    list_dict_reference_paper = []
    dict_paper_info = {}
    dict_paper_info['q_paper_parent_id'] = q_paper_id
    dict_paper_info['rel_id'] = rel_id
    dict_paper_info['parsing_url'] = parsing_url
    dict_paper_info['related_type'] = related_type
        
    article_url = None
    publisher_name = None
    dict_paper_info['article_url'] = article_url  # paper가 실린 곳 Journal의 기사 url
    dict_paper_info['publisher_name'] = publisher_name

    try:
        pmcid = dict_paper_rel_info['pmcid']
    except:
        pmcid = None
    try:
        pmid = dict_paper_rel_info['pmid']
    except:
        pmid = None
    try:
        doi = dict_paper_rel_info['doi']
    except:
        doi = None 
    try:
        doi_url = dict_paper_rel_info['doi_url']
    except:
        doi_url = None
    try:
        pdf_name = dict_paper_rel_info['pdf_name']
    except:
        pdf_name = None
    try:
        journal_name = dict_paper_rel_info['journal_name']
    except:
        journal_name = None
    try:
        publication_year = dict_paper_rel_info['pmcipublication_yeard']
    except:
        publication_year = None
    try:
        first_author_name = dict_paper_rel_info['first_author_name']
    except:
        first_author_name = None
    try:
        first_author_url = dict_paper_rel_info['first_author_url']
    except:
        first_author_url = None

    soup = get_soup_using_url_only(parsing_url)
    if soup is None:
        return None

    # Get Hidden Reference List
    # 1-1. Title
    try:
        results = soup.find('header', class_='heading')
        title = results.find('h1', class_='heading-title').get_text().strip()
    except:
        title = None 
    dict_paper_info['title'] = title

    # 1-2. Journal
    try:
        article_element = soup.find('div', class_='article-source')
        journal_element = article_element.find('div', class_="journal-actions")
        journal_name = journal_element.get_text()
        cite_element = article_element.find('span', class_="cit")
        cite = cite_element.get_text()
    except:
        journal_name = None
        cite = None
    dict_paper_info['journal_name'] = journal_name
    dict_paper_info['cite'] = cite

    # 2 Author
    list_dict_author_info = []
    """
        <div class="authors-list">
            <span class="authors-list-item">
                <a class="full-name" data-ga-action="author_link" data-ga-category="search" data-ga-label="Baris A Ozdemir" href="/?term=Ozdemir+BA&amp;cauthor_id=25719608" ref="linksrc=author_name_link">
                    Baris A Ozdemir
                </a>
                <sup class="affiliation-links">
                    <span class="author-sup-separator">
                    </span>
                    <a class="affiliation-link" href="#full-view-affiliation-1" ref="linksrc=author_aff" title="Department of Outcomes Research, St George's Vascular Institute, London, United Kingdom.">
                                1
                    </a>
                </sup>
                <span class="comma">
                    ,
                </span>
            </span>

            <span class="authors-list-item">
                <a class="full-name" data-ga-action="author_link" data-ga-category="search" data-ga-label="Alan Karthikesalingam" href="/?term=Karthikesalingam+A&amp;cauthor_id=25719608" ref="linksrc=author_name_link">
                    Alan Karthikesalingam
                </a>
                <sup class="affiliation-links">
                    <span class="author-sup-separator"> 
                    </span>
                    <a class="affiliation-link" href="#full-view-affiliation-1" ref="linksrc=author_aff" title="Department of Outcomes Research, St George's Vascular Institute, London, United Kingdom.">
                        1
                    </a>
                </sup>
                <span class="comma">
                    ,
                </span>
            </span>
            ...
        </div>
    """
    try:
        author_elements = results.find_all('span', class_='authors-list-item')
        i = 0
        for author_element in author_elements:
            dict_author_info = {}
            try:
                author_name = author_element.find('a', class_='full-name').get_text()
            except:
                author_name = None
            try:
                author_url = author_element.find('a', class_='full-name')['href']
                author_url = BASE_URL_PUBMED + author_url
            except:
                author_url = None
            if author_name not in LIST_NOT_AUTHOR_NAME:
                if 'http' not in author_name:
                    dict_author_info['author_name'] = author_name
                    dict_author_info['author_url'] = author_url
                    if dict_author_info not in list_dict_author_info:
                        list_dict_author_info.append(dict_author_info)
            if i == 0:
                first_author_name = author_name
                first_author_url = author_url
            i = i + 1
    except:
        list_dict_author_info = None
        pass
    dict_paper_info['list_dict_author_info'] = list_dict_author_info
    # print(f'dict_paper_info 2, {dict_paper_info}')


    # 3. IDs
    """ 
    <ul class="identifiers" id="full-view-identifiers">
        <li>
            <span class="identifier pubmed">
                <span class="id-label">
                    PMID:
                </span>
                <strong class="current-id" title="PubMed ID">
                    25719608
                </strong>
            </span>
        </li>
        <li>
            <span class="identifier pmc">
                <span class="id-label">
                        PMCID:
                </span>
                <a class="id-link" data-ga-action="PMCID" data-ga-category="full_text" href="http://www.ncbi.nlm.nih.gov/pmc/articles/pmc4342017/" ref="linksrc=article_id_link&amp;article_id=PMC4342017&amp;id_type=PMC" rel="noopener" target="_blank">
                    PMC4342017
                </a>
            </span>
        </li>
        <li>
            <span class="identifier doi">
                <span class="id-label">
                    DOI:
                </span>
                <a class="id-link" data-ga-action="DOI" data-ga-category="full_text" href="https://doi.org/10.1371/journal.pone.0118253" ref="linksrc=article_id_link&amp;article_id=10.1371/journal.pone.0118253&amp;id_type=DOI" rel="noopener" target="_blank">
                    10.1371/journal.pone.0118253
                </a>
            </span>
        </li>
        ...
    </ul>
    """
    pmid = None
    pmcid = None
    pubmed_url = None
    pubmed_free_url = None
    doi_url = None
    try:
        id_element = results.find('ul', class_='identifiers')
        identifier_elements = id_element.find_all('span', class_='identifier')
        i = 0
        for identifier_element in identifier_elements:
            id_text = None 
            id_url = None
            id_type = identifier_element.find('span', class_='id-label').get_text().strip()
            if ':' in id_type:
                id_type = id_type.replace(':', '')
            try:
                id_text = identifier_element.find('strong', class_='current-id').get_text().strip()
            except:
                pass 
            try:
                id_text = identifier_element.find('a', class_='id-link').get_text().strip()
            except:
                pass 
            try:
                id_url = identifier_element.find('a', class_='id-link')['href']
            except:
                pass 
            if 'PMID' in id_type:
                pmid = id_text
                pubmed_url = BASE_URL_PUBMED +'/'+ pmid
                dict_paper_info['pmid'] = pmid
                dict_paper_info['pubmed_url'] = pubmed_url
            if 'PMCID' in id_type:
                pmcid = id_text
                pubmed_free_url = id_url
                dict_paper_info['pmcid'] = pmcid
                dict_paper_info['pubmed_free_url'] = pubmed_free_url
            if 'DOI' in id_type:
                doi = id_text
                doi_url = id_url
                dict_paper_info['doi'] = doi
                dict_paper_info['doi_url'] = doi_url
            i = i + 1
    except:
        dict_paper_info['pmid'] = pmid
        dict_paper_info['pubmed_url'] = pubmed_url
        dict_paper_info['pmcid'] = pmcid
        dict_paper_info['pubmed_free_url'] = pubmed_free_url
        dict_paper_info['doi'] = doi
        dict_paper_info['doi_url'] = doi_url
        pass
    # print(f'dict_paper_info 3, {dict_paper_info}')

    # 4. Abstract
    try:
        abstract_element = soup.find('div', class_='abstract')  # HTML 택 포함해서 통채로 저장
        abstract_html = str(abstract_element)  # html 택은 string으로 변환해야 JSON Field에 저장 가능
    except:
        abstract_html = None
    dict_paper_info['abstract_html'] = abstract_html
    try:
        abstract_text = abstract_element.find('div', class_="abstract-content").get_text()
    except:
        abstract_text = None 
    dict_paper_info['abstract_text'] = abstract_text
    # print(f'dict_paper_info 4, {dict_paper_info}')


    # 5. Reference Data Collect
    """
    <ol class="references-and-notes-list">
        <li class="skip-numbering" value="1">
            Ward V, House A, Hamer S. Developing a framework for transferring knowledge into action: a thematic analysis of the literature. J Health Serv Res Policy. 2009;14: 156–164. 10.1258/jhsrp.2009.008120
            -
            <a class="reference-link" data-ga-action="10.1258/jhsrp.2009.008120" data-ga-category="reference" href="https://doi.org/10.1258/jhsrp.2009.008120" ref="linksrc=references_link&amp;ordinalpos=1">
                DOI
            </a>
            -
            <a class="reference-link" data-ga-action="PMC2933505" data-ga-category="reference" href="http://www.ncbi.nlm.nih.gov/pmc/articles/pmc2933505/" ref="linksrc=references_link&amp;ordinalpos=2">
                PMC
            </a>
                -
            <a class="reference-link" data-ga-action="19541874" data-ga-category="reference" href="/19541874/" ref="linksrc=references_link&amp;ordinalpos=3">
                PubMed
            </a>
        </li>
    </ol>
    <ol class="references-and-notes-list">
        <li class="skip-numbering" value="1">
            National Institute for Health Research website. Eligibility Criteria for NIHR CRN support. Available: <a href="http://www.crn.nihr.ac.uk/wp-content/uploads/About%20the%20CRN/Eligibility%20Criteria%20for%20NIHRCRN%20support.pdf.Accessed" rel="noopener nofollow" target="_blank" title="External link: http://www.crn.nihr.ac.uk/wp-content/uploads/About%20the%20CRN/Eligibility%20Criteria%20for%20NIHRCRN%20support.pdf.Accessed">http://www.crn.nihr.ac.uk/wp-content/uploads/About%20the%20CRN/Eligibili...</a> 17 July 2014.
        </li>
    </ol>
    ...
    """
    list_dict_reference_paper = []
    try:
        reference_element = soup.find('div', class_='refs-list')
        reference_element_items = reference_element.find_all('ol', class_='references-and-notes-list')
        r_n = 1
        for reference_element_item in reference_element_items:
            r_doi_url = None
            r_pubmed_link = None
            r_pubmed_free_link = None
            r_google_scholar_link = None
            r_other_url = None
            try:
                ref_info_text = str(reference_element_item.find('li', class_="skip-numbering"))
                if 'Available:' in ref_info_text:
                    r_other_url = ref_info_text.split('<a href="')[-1]
                    r_other_url = r_other_url.split('"')[0]
                r_cite = ref_info_text.split('<a')[0]
                r_cite = r_cite.split('>')[-1]
                r_cite = r_cite.replace('-', '')
                r_cite = r_cite.strip()
            except:
                r_cite = None
            try:
                items = reference_element_item.find_all('a', class_="reference-link")
                for item in items:
                    try:
                        ref_id_text = item.get_text().strip()
                    except:
                        ref_id_text = None 
                    try:
                        ref_id_url = item['href']
                    except:
                        ref_id_url = None 
                    if ref_id_text is not None:
                        if 'DOI' in ref_id_text:
                            r_doi_url = ref_id_url
                        if 'PubMed' in ref_id_text:
                            if '/0/' not in ref_id_url :
                                r_pubmed_link = BASE_URL_PUBMED + ref_id_url
                            else:
                                r_pubmed_link = None
                        if 'PMC' in ref_id_text:
                            r_pubmed_free_link = ref_id_url
            except:
                ref_id_text = None
            dict_reference_paper = {
                'id': r_n,
                'q_paper_id': None,
                'cite': r_cite,
                'doi_url': r_doi_url,
                'pubmed_url': r_pubmed_link,
                'pubmed_free_url': r_pubmed_free_link,
                'google_scholar_url': r_google_scholar_link,
                'other_url': r_other_url,
            }
            if dict_reference_paper not in list_dict_reference_paper:
                list_dict_reference_paper.append(dict_reference_paper)
            r_n = r_n + 1
    except:
        list_dict_reference_paper = None
    dict_paper_info['list_dict_reference_paper'] = list_dict_reference_paper    
    if list_dict_reference_paper is not None:
        # print(f'len(list_dict_reference_paper): , {len(list_dict_reference_paper)}')
        pass


    # 6 Get PDF URL    
    """ 
    <div class="full-text-links-list">
        <a class="link-item dialog-focus" data-ga-action="Public Library of Science" data-ga-category="full_text" data-ga-label="25719608" href="https://dx.plos.org/10.1371/journal.pone.0118253" ref="linksrc=fulltextorjournal_fulltext&amp;is_pmc=False&amp;PrId=4656&amp;itool=Abstract-def&amp;log$=linkouticon&amp;uid=25719608&amp;db=pubmed&amp;nlmid=101285081" rel="noopener" target="_blank" title="See full text options at Public Library of Science"><img alt="full text provider logo" src="https://cdn.ncbi.nlm.nih.gov/corehtml/query/egifs/https:--journals.plos.org-resource-img-external-pone_120x30.png"/>
            <span class="text">
                Public Library of Science
            </span>
        </a>
        <a class="link-item pmc" data-ga-action="PMC" data-ga-category="full_text" data-ga-label="25719608" href="https://www.ncbi.nlm.nih.gov/pmc/articles/pmid/25719608/" ref="linksrc=fulltextorjournal_fulltext&amp;is_pmc=True&amp;PrId=3494&amp;itool=Abstract-def&amp;log$=linkouticon&amp;uid=25719608&amp;db=pubmed&amp;nlmid=101285081" rel="noopener" target="_blank" title="Free full text at PubMed Central">
            <span class="text">
                Free PMC article
            </span>
        </a>
    </div>
    """
    list_dict_pdf_link_url = []
    try:
        pdf_element = soup.find('div', class_='full-text-links-list')
        pdf_link_elements = pdf_element.find_all('a', class_='link-item')
        for pdf_link_element in pdf_link_elements:
            pdf_link_text = pdf_link_element.get_text().strip()
            pdf_link_url = pdf_link_element['href']
            list_dict_pdf_link_url.append({'site_name': pdf_link_text, 'site_url': pdf_link_url})
        
    except:
        list_dict_pdf_link_url = None
    dict_paper_info['list_dict_pdf_link_url'] = list_dict_pdf_link_url

        
    """
    1순위: Free PMC article (PMC)
    2순위: Public Library of Science (PLOS)
    """
    pdf_url = None
    if list_dict_pdf_link_url is not None and len(list_dict_pdf_link_url) > 0:
        # PMC 있으면 우선 실행
        for dict_pdf_link_url in list_dict_pdf_link_url:
            # print('dict_pdf_link_url', dict_pdf_link_url)
            if dict_pdf_link_url['site_name'] == 'Free PMC article':
                pdf_site_url = dict_pdf_link_url['site_url']
                soup = get_soup_using_url_only(pdf_site_url)
                if soup is not None:
                    # Get PMC PDF Downlaod URL
                    try:
                        pdf_element = soup.find('section', class_='pmc-sidenav__container')
                        pdf_url_elements = pdf_element.find_all('a', class_='usa-button')
                        # print('pdf_url_elements', pdf_url_elements)
                        for pdf_url_element in pdf_url_elements:
                            try:
                                pdf_url_raw = pdf_url_element['href']
                            except:
                                pdf_url_raw = None 
                            if 'pdf' in pdf_url_raw:
                                pdf_url = pdf_site_url + pdf_url_raw 
                            if pdf_url is not None and '.pdf' in pdf_url:
                                print('PMC pdf_url', pdf_url)
                                break
                    except:
                        pass
            else:
                # print("not PMC")
                pass
        
        # PMC 없는 경우 나머지 실행
        if pdf_url is None:
            for dict_pdf_link_url in list_dict_pdf_link_url:
                if dict_pdf_link_url['site_name'] == 'Public Library of Science':
                    pdf_site_url = dict_pdf_link_url['site_url']
                    soup = get_soup_using_url_only(pdf_site_url)
                    if soup is not None:
                        try:
                            pdf_download_element = soup.find('div', class_='dload-pdf')
                            pdf_download_url = pdf_download_element.find('a')['href']
                            pdf_url = BASE_URL_PLOS + pdf_download_url
                            if pdf_url is not None and '.pdf' in pdf_url:
                                print('PLoS pdf_url', pdf_url)
                                break
                        except:
                            pass
                else:
                    # print('not PLoS')
                    pass
            
                if dict_pdf_link_url['site_name'] == 'Elsevier Science':
                    pdf_site_url = dict_pdf_link_url['site_url']
                    soup = get_soup_using_url_only(pdf_site_url)
                    if soup is not None:
                        # Find the input element with id="redirectURL"
                        redirect_input = soup.find('input', {'id': 'redirectURL'})
                        if redirect_input:
                            encoded_url = redirect_input.get('value')
                            decoded_url = urllib.parse.unquote(encoded_url)
                            if decoded_url is not None and 'http' in decoded_url:
                                dict_paper_info['other_url'] = decoded_url
                    
    dict_paper_info['pdf_url'] = pdf_url  
    print(f'pdf_url , {pdf_url}')

    # Data Merge (기본 정보 획득시 + 디테일 정보 획득시)
    if related_type == 'reference':
        # try:
        #     rel_id = dict_paper_rel_info['id']
        #     dict_paper_info['rel_id'] = rel_id
        # except:
        #     rel_id = None
        #     dict_paper_info['rel_id'] = None
        try:
            cite_rel = dict_paper_rel_info['cite']
        except:
            cite_rel = None
        try:
            doi_rel = dict_paper_rel_info['doi']
        except:
            doi_rel = None
        try:
            doi_url_rel = dict_paper_rel_info['doi_url']
        except:
            doi_url_rel = None
        try:
            pmid_rel = dict_paper_rel_info['pmid']
        except:
            pmid_rel = None
        try:
            pubmed_url_rel = dict_paper_rel_info['pubmed_url']
        except:
            pubmed_url_rel = None
        try:
            pubmed_free_url_rel = dict_paper_rel_info['pubmed_free_url']
        except:
            pubmed_free_url_rel = None
        try:
            google_scholar_url_rel = dict_paper_rel_info['google_scholar_url']
        except:
            google_scholar_url_rel = None
        try:
            other_url_rel = dict_paper_rel_info['other_url']
        except:
            other_url_rel = None
        if doi is None:
            doi = doi_rel
        if doi_url is None:
            doi_url = doi_url_rel
        if pmid is None:
            pmid = pmid_rel 
        if doi_url is None:
            doi_url = doi_url_rel
        try:
            cite = dict_paper_info['cite']
        except:
            cite = None 
        if cite is None:
            dict_paper_info['cite'] = cite_rel
        try:
            pubmed_url = dict_paper_info['pubmed_url']
        except:
            pubmed_url = None 
        if pubmed_url is None:
            dict_paper_info['pubmed_url'] = pubmed_url_rel
        try:
            pubmed_free_url = dict_paper_info['pubmed_free_url']
        except:
            pubmed_free_url = None 
        if pubmed_free_url is None:
            dict_paper_info['pubmed_free_url'] = pubmed_free_url_rel
        try:
            google_scholar_url = dict_paper_info['google_scholar_url']
        except:
            google_scholar_url = None 
        if google_scholar_url is None:
            dict_paper_info['google_scholar_url'] = google_scholar_url_rel
        try:
            other_url = dict_paper_info['other_url']
        except:
            other_url = None 
        if other_url is None:
            dict_paper_info['other_url'] = other_url_rel
        
    elif related_type == 'relevant':
        try:
            id_rel = dict_paper_rel_info['id']
        except:
            id_rel = None
        try:
            title_rel = dict_paper_rel_info['title']
        except:
            title_rel = None
        try:
            doi_rel = dict_paper_rel_info['doi']
        except:
            doi_rel = None
        try:
            doi_url_rel = dict_paper_rel_info['doi_url']
        except:
            doi_url_rel = None
        try:
            pmid_rel = dict_paper_rel_info['pmid']
        except:
            pmid_rel = None
        try:
            pubmed_url_rel = dict_paper_rel_info['pubmed_url']
        except:
            pubmed_url_rel = None
        try:
            journal_rel = dict_paper_rel_info['journal']
        except:
            journal_rel = None
        if doi is None:
            doi = doi_rel
        if doi_url is None:
            doi_url = doi_url_rel
        if pmid is None:
            pmid = pmid_rel 
        if title is None:
            title = title_rel
        if doi_url is None:
            doi_url = doi_url_rel
        try:
            pubmed_url = dict_paper_info['pubmed_url']
        except:
            pubmed_url = None 
        if pubmed_url is None:
            dict_paper_info['pubmed_url'] = pubmed_url_rel
        try:
            journal = dict_paper_info['journal']
        except:
            journal = None 
        if journal is None:
            dict_paper_info['journal'] = journal_rel
        
    elif related_type == 'author':
        try:
            id_rel = dict_paper_rel_info['id']
        except:
            id_rel = None
        try:
            title_rel = dict_paper_rel_info['title']
        except:
            title_rel = None
        try:
            doi_rel = dict_paper_rel_info['doi']
        except:
            doi_rel = None
        try:
            doi_url_rel = dict_paper_rel_info['doi_url']
        except:
            doi_url_rel = None
        try:
            pmid_rel = dict_paper_rel_info['pmid']
        except:
            pmid_rel = None
        try:
            pubmed_url_rel = dict_paper_rel_info['pubmed_url']
        except:
            pubmed_url_rel = None
        try:
            journal_rel = dict_paper_rel_info['journal']
        except:
            journal_rel = None
        if doi is None:
            doi = doi_rel
        if doi_url is None:
            doi_url = doi_url_rel
        if pmid is None:
            pmid = pmid_rel 
        if title is None:
            title = title_rel
        if doi_url is None:
            doi_url = doi_url_rel
        try:
            pubmed_url = dict_paper_info['pubmed_url']
        except:
            pubmed_url = None 
        if pubmed_url is None:
            dict_paper_info['pubmed_url'] = pubmed_url_rel
        try:
            journal = dict_paper_info['journal']
        except:
            journal = None 
        if journal is None:
            dict_paper_info['journal'] = journal_rel
    
    dict_result = {'title': title, 'doi': doi, 'doi_url': doi_url, 'pmid': pmid, 'pmcid': pmcid, 'first_author_name': first_author_name, 'first_author_url': first_author_url, 'publication_year': publication_year, 'dict_paper_info': dict_paper_info, 'list_dict_reference_paper': list_dict_reference_paper, 'pdf_url': pdf_url}
    # if check_driver == True:
    #     driver.quit()
    return dict_result 

       

#--------------------------------------------------------------------------------------------------------------------------------------
# C-3. google_scholar에서 선택한 Paper의 정보 긁어오기 및 PDF 저장
#--------------------------------------------------------------------------------------------------------------------------------------
def parsing_paper_info_on_google_scholar(q_paper_id, rel_id, parsing_url, related_type, dict_paper_rel_info):
    print(f'C-3. q_paper_id: {q_paper_id},  rel_id: {rel_id},  parsing_url: {parsing_url}, related_type: {related_type}')

    random_sec = random.uniform(7, 10)
    dict_result = {}
    list_dict_reference_paper = []
    dict_paper_info = {}
    dict_paper_info['q_paper_parent_id'] = q_paper_id
    dict_paper_info['rel_id'] = rel_id
    dict_paper_info['parsing_url'] = parsing_url
    dict_paper_info['related_type'] = related_type

    article_url = None
    publisher_name = None
    dict_paper_info['article_url'] = article_url  # paper가 실린 곳 Journal의 기사 url
    dict_paper_info['publisher_name'] = publisher_name

    try:
        pmcid = dict_paper_rel_info['pmcid']
    except:
        pmcid = None
    try:
        pmid = dict_paper_rel_info['pmid']
    except:
        pmid = None
    try:
        doi = dict_paper_rel_info['doi']
    except:
        doi = None 
    try:
        doi_url = dict_paper_rel_info['doi_url']
    except:
        doi_url = None
    try:
        pdf_name = dict_paper_rel_info['pdf_name']
    except:
        pdf_name = None
    try:
        journal_name = dict_paper_rel_info['journal_name']
    except:
        journal_name = None
    try:
        publication_year = dict_paper_rel_info['pmcipublication_yeard']
    except:
        publication_year = None
    try:
        first_author_name = dict_paper_rel_info['first_author_name']
    except:
        first_author_name = None
    try:
        first_author_url = dict_paper_rel_info['first_author_url']
    except:
        first_author_url = None
    
    soup = get_soup_using_url_only(parsing_url)
    if soup is None:
        return None

    # PDF URL
    list_dict_pdf_link_url = []
    pdf_url = None
    try:
        pdf_element = soup.find('div', class_='gs_or_ggsm')
        pdf_element_text = pdf_element.get_text()
        if '[PDF]' in pdf_element_text:
            pdf_element_text = pdf_element_text.replace('[PDF]', '')
        pdf_element_url = pdf_element.find('a')['href']
        pdf_url = pdf_element_url
    except:
        pdf_element_text = None
        pdf_element_url = None
    list_dict_pdf_link_url.append({'site_name': pdf_element_text, 'site_url': pdf_element_url})
    dict_paper_info['list_dict_pdf_link_url'] = list_dict_pdf_link_url    
    dict_paper_info['pdf_url'] = pdf_url
    
    # Paper Info Parsing
    paper_element = soup.find('div', class_='gs_ri')
    # print('paper_element', paper_element)

    # title
    try:
        title_element = paper_element.find('h3')
        title = title_element.get_text()
        article_url = title_element.find('a')['href']
    except:
        title = None
        article_url = None 
    dict_paper_info['title'] = title
    dict_paper_info['article_url'] = article_url

    # author 
    list_dict_author_info = []
    try:
        author_element = paper_element.find('div', class_="gs_fmaa")
        # print('author_element', author_element)
        list_author_name = []
        author_element_authors = author_element.find_all('a')
        i = 0
        for author_element_author in author_element_authors:
            dict_author_info = {}
            author_element_author_name = author_element_author.get_text()
            list_author_name.append(author_element_author_name)
            author_element_author_url = author_element_author['href']
            author_element_author_url = BASE_URL_GOOGLE_SCHOLAR + author_element_author_url
            if i == 0:
                first_author_name = author_element_author_name 
                first_author_url = author_element_author_url 
            dict_author_info['author_name'] = author_element_author_name
            dict_author_info['author_url'] = author_element_author_url
            list_dict_author_info.append(dict_author_info)
            i = i + 1
    except:
        list_dict_author_info = None
    dict_paper_info['list_dict_author_info'] = list_dict_author_info

    # Organization
    try:
        organization_element = paper_element.find('div', class_="gs_a")
        organization_element_text = organization_element.get_text()
        for author_name in list_author_name:
            if author_name in organization_element_text:
                organization_element_text = organization_element_text.replace(author_name, '')
        # print('organization_element', organization_element_text)
        # print('organization_element_text', organization_element_text)
        list_journal_name_and_publisher_name = []
        list_organization_element_text = organization_element_text.split('-')
        for organization_element_text in list_organization_element_text:
            organization_element_text = organization_element_text.strip()
            # print(organization_element_text)
            if organization_element_text != ',':
                list_journal_name_and_publisher_name.append(organization_element_text.strip())
        try:
            journal_name = list_journal_name_and_publisher_name[0]
        except:
            journal_name = None
        try:
            publisher_name = list_journal_name_and_publisher_name[1]
        except:
            publisher_name = None
    except:
        journal_name = None
        publisher_name = None
    dict_paper_info['journal_name'] = journal_name
    dict_paper_info['publisher_name'] = publisher_name
    
    # Abstract 
    try:
        abstract_element = soup.find('div', class_="gs_fma_abs")
        abstract_text = abstract_element.get_text()
    except:
        abstract_text = None
    dict_paper_info['abstract_text'] = abstract_text
    dict_paper_info['abstract_html'] = None

    # Data Merge (기본 정보 획득시 + 디테일 정보 획득시)
    if related_type == 'reference':
        try:
            id_rel = dict_paper_rel_info['id']
        except:
            id_rel = None
        try:
            cite_rel = dict_paper_rel_info['cite']
        except:
            cite_rel = None
        try:
            doi_rel = dict_paper_rel_info['doi']
        except:
            doi_rel = None
        try:
            doi_url_rel = dict_paper_rel_info['doi_url']
        except:
            doi_url_rel = None
        try:
            pmid_rel = dict_paper_rel_info['pmid']
        except:
            pmid_rel = None
        try:
            pubmed_url_rel = dict_paper_rel_info['pubmed_url']
        except:
            pubmed_url_rel = None
        try:
            pubmed_free_url_rel = dict_paper_rel_info['pubmed_free_url']
        except:
            pubmed_free_url_rel = None
        try:
            google_scholar_url_rel = dict_paper_rel_info['google_scholar_url']
        except:
            google_scholar_url_rel = None
        try:
            other_url_rel = dict_paper_rel_info['other_url']
        except:
            other_url_rel = None
        if doi is None:
            doi = doi_rel
        if doi_url is None:
            doi_url = doi_url_rel
        if pmid is None:
            pmid = pmid_rel 
        if doi_url is None:
            doi_url = doi_url_rel
        try:
            cite = dict_paper_info['cite']
        except:
            cite = None 
        if cite is None:
            dict_paper_info['cite'] = cite_rel
        try:
            pubmed_url = dict_paper_info['pubmed_url']
        except:
            pubmed_url = None 
        if pubmed_url is None:
            dict_paper_info['pubmed_url'] = pubmed_url_rel
        try:
            pubmed_free_url = dict_paper_info['pubmed_free_url']
        except:
            pubmed_free_url = None 
        if pubmed_free_url is None:
            dict_paper_info['pubmed_free_url'] = pubmed_free_url_rel
        try:
            google_scholar_url = dict_paper_info['google_scholar_url']
        except:
            google_scholar_url = None 
        if google_scholar_url is None:
            dict_paper_info['google_scholar_url'] = google_scholar_url_rel
        try:
            other_url = dict_paper_info['other_url']
        except:
            other_url = None 
        if other_url is None:
            dict_paper_info['other_url'] = other_url_rel
        
    elif related_type == 'relevant':
        try:
            id_rel = dict_paper_rel_info['id']
        except:
            id_rel = None
        try:
            title_rel = dict_paper_rel_info['title']
        except:
            title_rel = None
        try:
            doi_rel = dict_paper_rel_info['doi']
        except:
            doi_rel = None
        try:
            doi_url_rel = dict_paper_rel_info['doi_url']
        except:
            doi_url_rel = None
        try:
            pmid_rel = dict_paper_rel_info['pmid']
        except:
            pmid_rel = None
        try:
            pubmed_url_rel = dict_paper_rel_info['pubmed_url']
        except:
            pubmed_url_rel = None
        try:
            journal_rel = dict_paper_rel_info['journal']
        except:
            journal_rel = None
        if doi is None:
            doi = doi_rel
        if doi_url is None:
            doi_url = doi_url_rel
        if pmid is None:
            pmid = pmid_rel 
        if title is None:
            title = title_rel
        if doi_url is None:
            doi_url = doi_url_rel
        try:
            pubmed_url = dict_paper_info['pubmed_url']
        except:
            pubmed_url = None 
        if pubmed_url is None:
            dict_paper_info['pubmed_url'] = pubmed_url_rel
        try:
            journal = dict_paper_info['journal']
        except:
            journal = None 
        if journal is None:
            dict_paper_info['journal'] = journal_rel
        
    elif related_type == 'author':
        try:
            id_rel = dict_paper_rel_info['id']
        except:
            id_rel = None
        try:
            title_rel = dict_paper_rel_info['title']
        except:
            title_rel = None
        try:
            doi_rel = dict_paper_rel_info['doi']
        except:
            doi_rel = None
        try:
            doi_url_rel = dict_paper_rel_info['doi_url']
        except:
            doi_url_rel = None
        try:
            pmid_rel = dict_paper_rel_info['pmid']
        except:
            pmid_rel = None
        try:
            pubmed_url_rel = dict_paper_rel_info['pubmed_url']
        except:
            pubmed_url_rel = None
        try:
            journal_rel = dict_paper_rel_info['journal']
        except:
            journal_rel = None
        if doi is None:
            doi = doi_rel
        if doi_url is None:
            doi_url = doi_url_rel
        if pmid is None:
            pmid = pmid_rel 
        if title is None:
            title = title_rel
        if doi_url is None:
            doi_url = doi_url_rel
        try:
            pubmed_url = dict_paper_info['pubmed_url']
        except:
            pubmed_url = None 
        if pubmed_url is None:
            dict_paper_info['pubmed_url'] = pubmed_url_rel
        try:
            journal = dict_paper_info['journal']
        except:
            journal = None 
        if journal is None:
            dict_paper_info['journal'] = journal_rel

    dict_result = {'title': title, 'doi': doi, 'doi_url': doi_url, 'pmid': pmid, 'pmcid': pmcid, 'first_author_name': first_author_name, 'first_author_url': first_author_url, 'publication_year': publication_year, 'dict_paper_info': dict_paper_info, 'list_dict_reference_paper': list_dict_reference_paper, 'pdf_url': pdf_url}
    return dict_result





#--------------------------------------------------------------------------------------------------------------------------------------
# C-4. Nature에서 선택한 Paper의 정보 긁어오기 및 PDF 저장
"""
    예:
    [
        {
            'pdf_download_full_url': 'https://www.nature.com/articles/s41467-024-50779-y.pdf',
            'pdf_title': 's41467-024-50779-y.pdf',
            'paper_title': 'PatCID: an open-access dataset of chemical structures in patent documents',
            'dict_first_author_info': {
                'first_author_name': 'Lucas Morin',
                'main_author_url': 'https://www.nature.com/articles/s41467-024-50779-y#auth-Lucas-Morin-Aff1-Aff2',
                'main_author_orcid_url': 'http://orcid.org/0000-0002-5829-5118'
            },
            'dict_paper_detail_info': {
                'journal_name': 'Nature Communications',
                'journal_url': 'https://www.nature.com/ncomms',
                'journal_volume': 'volume15',
                'article_number': '6532',
                'publication_year': '2024'
            },
            'abstract': 'The automatic analysis of patent publications has potential to accelerate research across various domains, including drug discovery and material science. Within patent documents, crucial information often resides in visual depictions of molecule structures. PatCID (Patent-extracted Chemical-structure Images database for Discovery) allows to access such information at scale. It enables users to search which molecules are displayed in which documents. PatCID contains 81M chemical-structure images and 14M unique chemical structures. Here, we compare PatCID with state-of-the-art chemical patent-databases. On a random set, PatCID retrieves 56.0% of molecules, which is higher than automatically-created databases, Google Patents (41.5%) and SureChEMBL (23.5%), as well as manually-created databases, Reaxys (53.5%) and SciFinder (49.5%). Leveraging state-of-the-art methods of document understanding, PatCID high-quality data outperforms currently available automatically-generated patent-databases. PatCID even competes with proprietary manually-created patent-databases. This enables promising applications for automatic literature review and learning-based molecular generation methods. The dataset is freely accessible for download.',
            'references': [
                {
                    'reference_title': 'Ohms, J. Current methodologies for chemical compound searching in patents: a case study.',
                    'doi': '10.1016/j.wpi.2021.102055',
                    'doi_url': 'https://doi.org/10.1016%2Fj.wpi.2021.102055',
                    'google_scholar_url': 'http://scholar.google.com/scholar_lookup?&title=Current%20methodologies%20for%20chemical%20compound%20searching%20in%20patents%3A%20a%20case%20study&journal=World%20Patent%20Inf.&doi=10.1016%2Fj.wpi.2021.102055&volume=66&publication_year=2021&author=Ohms%2CJ'
                }, {}, {},
            'doi': 'https://doi.org/10.1038/s41467-024-50779-y'     
            ]
        }, {}, {},
    ]
"""    
#--------------------------------------------------------------------------------------------------------------------------------------
def parsing_paper_data_from_nature(soup, list_dict_paper_info, base_url, article_url):
    
    # 논문 PDF 다운 url 획득
    list_pdf_url_dup_check = []
    
    results = soup.find_all(class_="c-pdf-download")
    for result in results:
        # print(result)
        tags = result.find_all('a')
        for tag in tags:
            # print(tag)
            pdf_download_url = tag.get('href')
            pdf_title = pdf_download_url.split('/')[-1]
            pdf_download_full_url = base_url + pdf_download_url
            if pdf_download_full_url not in list_pdf_url_dup_check:
                list_pdf_url_dup_check.append(pdf_title)
                list_pdf_url_dup_check.append(pdf_download_full_url)
    if len(list_pdf_url_dup_check) > 0:
        pdf_title = list_pdf_url_dup_check[0]
        pdf_download_full_url = list_pdf_url_dup_check[1]
        list_dict_paper_info['pdf_download_full_url'] = pdf_download_full_url
        list_dict_paper_info['pdf_title'] = pdf_title
    
    # 논문 Title 추출
    list_title_dup_check = []
    results = soup.find_all(class_="c-article-title")
    i = 0
    for result in results:
        paper_title = result.text
        if paper_title not in list_title_dup_check:
            list_title_dup_check.append(paper_title)
    if len(list_title_dup_check) > 0:
        paper_title = list_title_dup_check[0]
    else:
        paper_title = None
    list_dict_paper_info['paper_title'] = paper_title

    # 논문 주저자 추출
    dict_first_author_info = {}
    # Find the author name and URL
    try:
        author_tag = soup.find('a', {'data-test': 'author-name'})
    except:
        author_tag = None
    try:
        author_name = author_tag.get_text(strip=True)  # Extract the author's name
    except:
        author_name = None
    try:
        author_url = author_tag['href']  # Extract the author's link    
    except:
        author_url = None

    # Find the ORCID link (if available)
    try:
        orcid_tag = soup.find('a', {'class': 'js-orcid'})
    except:
        orcid_tag = None
    try:
        orcid_url = orcid_tag['href'] if orcid_tag else None
    except:
        orcid_url = None

    dict_first_author_info['first_author_name'] = author_name
    try:
        dict_first_author_info['first_author_url'] = article_url + author_url
    except:
        dict_first_author_info['first_author_url'] = None
    dict_first_author_info['first_author_orcid_url'] = orcid_url
    list_dict_paper_info['dict_first_author_info'] = dict_first_author_info
    
    
    # 논문 세부 정보 추출
    dict_paper_detail_info = {}
    # Extract journal name
    try:
        journal_name = soup.find('i', {'data-test': 'journal-title'}).get_text()
    except:
        journal_name = None
    # Extract journal URL
    try:
        journal_url = soup.find('a', {'data-test': 'journal-link'})['href']
    except: 
        journal_url = None
    # Extract journal volume
    try:
        journal_volume = soup.find('b', {'data-test': 'journal-volume'}).get_text(strip=True).split()[-1]  # Extracts the number part
    except:
        journal_volume = None
    # Extract article number
    try:
        article_number = soup.find('span', {'data-test': 'article-number'}).get_text()
    except:
        article_number = None
    # Extract publication year
    try:
        publication_year = soup.find('span', {'data-test': 'article-publication-year'}).get_text()
    except:
        publication_year = None

    dict_paper_detail_info['journal_name'] = journal_name
    try:
        dict_paper_detail_info['journal_url'] = base_url + journal_url
    except:
        dict_paper_detail_info['journal_url'] = None
    dict_paper_detail_info['journal_volume'] = journal_volume
    dict_paper_detail_info['article_number'] = article_number
    dict_paper_detail_info['publication_year'] = publication_year
    list_dict_paper_info['dict_paper_detail_info'] = dict_paper_detail_info

    # 논문 Abstract 추출
    # Find the <div> tag with id="Abs1-content"
    abstract_div = soup.find('div', {'id': 'Abs1-content'})
    if abstract_div:
        # Find the <p> tag within the div
        abstract_paragraph = abstract_div.find('p')
        if abstract_paragraph:
            abstract_text = abstract_paragraph.get_text(strip=True)
            print("Abstract:")
            list_dict_paper_info['abstract'] = abstract_text
        else:
            print("Abstract paragraph not found.")
    else:
        print("Abstract div not found.")

    # 논문 Reference 추출
    reference_items = soup.find_all('li', class_='c-article-references__item')
    extracted_references = []
    for ref in reference_items:
        reference_data = {}
        # Extract the reference text
        ref_text_p = ref.find('p', class_='c-article-references__text')
        if ref_text_p:
            # To get the text before the <i> tag
            # Iterate through the contents and collect text until <i> tag
            title = ""
            for content in ref_text_p.contents:
                if content.name == 'i':
                    break
                if isinstance(content, str):
                    title += content.strip()
                else:
                    title += content.get_text(strip=True)
            reference_data['reference_title'] = title
        else:
            reference_data['reference_title'] = 'N/A'
        # Extract the doi and doi URL
        links_p = ref.find('p', class_='c-article-references__links')
        if links_p:
            doi_a = links_p.find('a', attrs={'data-track-action': 'article reference'})
            if doi_a:
                reference_data['doi'] = doi_a.get('data-doi', 'N/A')
                reference_data['doi_url'] = doi_a.get('href', 'N/A')
            else:
                reference_data['doi'] = 'N/A'
                reference_data['doi_url'] = 'N/A'
            # Extract Google Scholar URL
            gs_a = links_p.find('a', attrs={'data-track-action': 'google scholar reference'})
            if gs_a:
                reference_data['google_scholar_url'] = gs_a.get('href', 'N/A')
            else:
                reference_data['google_scholar_url'] = 'N/A'
        else:
            reference_data['doi'] = 'N/A'
            reference_data['doi_url'] = 'N/A'
            reference_data['google_scholar_url'] = 'N/A'
        
        extracted_references.append(reference_data)
    list_dict_paper_info['references'] = extracted_references
    
    # Doi 획득
    results = soup.find_all('span', class_='c-bibliographic-information__value')
    doi = 'null'
    for result in results:
        if 'doi' in result.text:
            doi = result.text.strip()
    list_dict_paper_info['doi'] = doi
    # Nature 정보 획득 종료
    return list_dict_paper_info



















#############################################################################################################################################
#############################################################################################################################################
#
#                                                     D: PDF 다운받기
#
#############################################################################################################################################
#############################################################################################################################################

#--------------------------------------------------------------------------------------------------------------------------------------
# D-1. PDF 다운받기 및 Paper 쿼리 업데이트
#--------------------------------------------------------------------------------------------------------------------------------------
def f_create_pdf_name_and_file_path_using_hashcode(q_paper_id, hashcode, pdf_url):
    import requests
    print(f'Paper ID: {q_paper_id}, hashcode: {hashcode}, pdf_url: {pdf_url}')
    DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER)

    random_sec_2 = random.uniform(1, 3)
    time.sleep(random_sec_2)
    
    file_extension = 'pdf'
    pdf_name = f'paper-{hashcode}.{file_extension}'
    file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER, pdf_name)
    check_download_pdf = False

    # PDF Download using request
    if pdf_url is not None and file_path is not None:
        # 디렉토리가 없으면 생성한다.
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        # 파일이 이미 저장되어 있으면 저장하지 않고 건너뛴다.
        if os.path.exists(file_path):
            print(f'동일한 파일이 존재합니다.')
            check_download_pdf = True
        else:
            print(f'동일한 파일이 없습니다. PDF 다운로드합니다.')
            headers = get_random_header()
            session = requests.Session()
            response = session.get(pdf_url, headers=headers)
            
            # Proxy 사용할 경우
            # n = random.randint(0, 9)
            # PROXY_PORT = LIST_PORT_FINEPROXY[n]
            # proxy = f"http://{FINEPROXY_USER_NAME}:{FINEPROXY_USER_PASSWORD}@FINEPROXY.XYZ:{PROXY_PORT}"
            # PROXY_PORT = LIST_PORT_SMARTPROXY[n]
            # proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{PROXY_PORT}"
            # # response = requests.get(pdf_url, headers=headers, proxies={
            # response = requests.get(pdf_url, proxies={
            #     'http': proxy,
            #     'https': proxy
            # })

            if response.status_code == 200:
                try:
                    with open(file_path, "wb") as file:
                        file.write(response.content)
                        print('# Saved the PDF to a file')
                    check_download_pdf = True
                except:
                    print('failed save pdf')
            else:
                print(f"Failed to download PDF. Status code: {response.status_code}")
        
    if q_paper_id is not None:
        data = {
            'file_path_pdf': pdf_name,
            'pdf_url': pdf_url,
            'check_download_pdf': check_download_pdf,
        }
        Paper.objects.filter(id=q_paper_id).update(**data)
    else:
        print('Error, q_paper is None')
    return hashcode



#--------------------------------------------------------------------------------------------------------------------------------------
# D-2-1. PDF 다운받기
#--------------------------------------------------------------------------------------------------------------------------------------
def f_download_pdf_using_requests_for_paper(q_paper_rel_id, pdf_url, file_path, pdf_name):
    check_download_pdf = f_download_pdf_using_requests(pdf_url, file_path)
    return q_paper_rel_id, pdf_name, check_download_pdf

#--------------------------------------------------------------------------------------------------------------------------------------
# D-2-2. PDF 다운받기
#--------------------------------------------------------------------------------------------------------------------------------------
def f_download_pdf_using_requests(pdf_url, file_path):
    print(f'Paper PDF Downlad하기 시작,  pdf_url: {pdf_url}, file_path: {file_path}')
    DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER)
    check_download_pdf = False

    # Ensure the directory exists and has the right permissions
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    
    # PDF Download using request
    if pdf_url is not None and file_path is not None:
        # 디렉토리가 없으면 생성한다.
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        # 파일이 이미 저장되어 있으면 저장하지 않고 건너뛴다.
        if os.path.exists(file_path):
            print(f'동일한 파일이 존재합니다.')
            check_download_pdf = True
        else:
            print(f'동일한 파일이 없습니다. PDF 다운로드합니다.')
            try:
                headers = get_random_header()
                session = requests.Session()
                response = session.get(pdf_url, headers=headers)
                if response.status_code == 200:
                    print('response status 200')
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    check_download_pdf = True
                else:
                    proxy_port = random.randint(10001, 11000)
                    proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{proxy_port}"
                    response = requests.get(pdf_url, proxies={
                        'http': proxy,
                        'https': proxy
                    })
                    if response.status_code == 200:
                        print('response Proxy status 200')
                        with open(file_path, 'wb') as file:
                            file.write(response.content)
                        check_download_pdf = True
                    else:
                        print(f"Failed to download PDF. Status code: {response.status_code}")
            except:
                print('failed trying PDF downloading')
                pass
        
    return check_download_pdf


#--------------------------------------------------------------------------------------------------------------------------------------
# D-3. Sci-Hub에서 PDF 다운받기
#--------------------------------------------------------------------------------------------------------------------------------------
def download_paper_pdf_on_sci_hub(doi_url, file_path):
    # get pdf_url on Sci-Hub
    if 'https://' in doi_url:
        doi_url = doi_url.replace('https://', '')
    if 'http://' in doi_url:
        doi_url = doi_url.replace('http://', '')

    pdf_url = BASE_URL_SCI_HUB + doi_url
    if '//' in pdf_url:
        pdf_url = pdf_url.replace('//', '/')
    pdf_url= f'https://{pdf_url}'
    
    if os.path.exists(file_path):
        # 파일이 이미 저장되어 있으면 저장하지 않고 건너뛴다.
        return True 
    else:
        # PDF파일 저장하기
        return_value = f_download_pdf_using_requests(pdf_url, file_path)
        return return_value
    









   

#############################################################################################################################################
#############################################################################################################################################
#
#                                                     PDF Screenshot
#
#############################################################################################################################################
#############################################################################################################################################

@shared_task
def convert_pdf_to_images_in_task(q_paper_selected_id, pdf_file_name, output_folder_path, file_extension):
    print(f'DATA Received! q_paper_selected_id: {q_paper_selected_id}, pdf_file_name: {pdf_file_name}, output_folder_path: {output_folder_path}, file_extension: {file_extension}')
    q_paper_selected = Paper.objects.get(id=q_paper_selected_id)
    hashcode = q_paper_selected.hashcode
    list_dict_paper_image = q_paper_selected.list_dict_paper_image
    if list_dict_paper_image is None:
        list_dict_paper_image = []
    print(f'hashcode: {hashcode}')
    try:
        print(f'len(list_dict_paper_image): {len(list_dict_paper_image)}')
    except:
        print(f'list_dict_paper_image is None')

    # Convert PDF to images
    file_path_pdf = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER, pdf_file_name)
    print(f'file_path_pdf: {file_path_pdf}')
    
    if not os.path.exists(file_path_pdf):
        print('file does not exist')
        return False
    images = convert_from_path(file_path_pdf, dpi=200, fmt='png')
    print(f'length of images: {len(images)}')
    
    
    q_paper_selected.refresh_from_db()
    list_dict_paper_image = q_paper_selected.list_dict_paper_image
    if list_dict_paper_image is None:
        list_dict_paper_image = []
    if len(list_dict_paper_image) == 0:
        for i, image in enumerate(images, start=1):
            check_dup = False
            image_filename = f"paper_{hashcode}_image_{i}.{file_extension}"
            # print(f'{i} image_filename: {image_filename}')
            image_path = os.path.join(output_folder_path, image_filename)
            image.save(image_path, file_extension)
            for item in list_dict_paper_image:
                if item.get('id') == i:
                    check_dup = True
            if check_dup == False:
                list_dict_paper_image.append({'id': i, 'filename': image_filename, 'discard': 'false'})
                data = {
                    'list_dict_paper_image': list_dict_paper_image,
                }
                Paper.objects.filter(id=q_paper_selected_id).update(**data)
                q_paper_selected.refresh_from_db()
        
        # q_paper_selected.refresh_from_db()
        # list_dict_paper_image = q_paper_selected.list_dict_paper_image
        # if list_dict_paper_image is None:
        #     list_dict_paper_image = [] 
        # for item in list_dict_paper_image:
        #     if item.get('id') == 1:
        #         check_dup = True
        # if check_dup == False:
        #     data = {
        #         'list_dict_paper_image': list_dict_paper_image,
        #     }
        #     Paper.objects.filter(id=q_paper_selected_id).update(**data)
        #     q_paper_selected.refresh_from_db()
        print(f'# paper screenshot 저장 종료료, {len(list_dict_paper_image)}장 저장')
    else:
        print('저장중 !!! ')
        pass
    return True













































































# PDF Download Multi Processor
                # # Get List Job for PDF Download
                # print(f'# PDF Download, len(list_dict_paper_pdf_download): {len(list_dict_paper_pdf_download)}')
                # list_job_paper_download = []
                # list_result_paper_download = []
                # if list_dict_paper_pdf_download is not None and len(list_dict_paper_pdf_download) > 0:
                #     for dict_paper_pdf_download in list_dict_paper_pdf_download:
                #         try:
                #             q_paper_rel_id = dict_paper_pdf_download['id']
                #         except:
                #             q_paper_rel_id = None
                #         try:
                #             pdf_url = dict_paper_pdf_download['pdf_url']
                #         except:
                #             pdf_url = None
                #         try:
                #             file_path = dict_paper_pdf_download['file_path']
                #         except:
                #             file_path = None
                #         try:
                #             pdf_name = dict_paper_pdf_download['pdf_name']
                #         except:
                #             pdf_name = None
                        
                #         if q_paper_rel_id is not None:
                #             if file_path is not None and pdf_url is not None:    
                #                 list_job_paper_download.append((q_paper_rel_id, pdf_url, file_path, pdf_name))
                # # Multiprocessing for PDF Download
                # if list_job_paper_download is not None and len(list_job_paper_download) > 0:
                #     req_processor = len(list_job_paper_download)
                #     # 실제 사용할 프로세서 개수 정하기
                #     if max_processor > req_processor:
                #         final_processor = req_processor
                #     else:
                #         final_processor = max_processor
                #     print(f'작업해야할 개수: {len(list_job_paper_download)},  최종 사용 core 개수 : {final_processor}')
                #     # Use multiprocessing Pool
                #     with Pool(processes=final_processor) as pool:
                #         # Submit all jobs to the pool simultaneously
                #         async_results = [
                #             pool.apply_async(f_download_pdf_using_requests_for_paper, args=job)
                #             for job in list_job_paper_download
                #         ]
                #         # Collect results
                #         for i, async_result in enumerate(async_results):
                #             try:
                #                 # Wait for the result with a timeout of 30 seconds
                #                 result = async_result.get(timeout=30)
                #                 list_result_paper_download.append(result)
                #             except TimeoutError:
                #                 # Handle timeout for the specific task
                #                 print(f"Task with arguments {list_job_paper_download[i]} exceeded the 30-second time limit.")
                #                 list_result_paper_download.append(None)
                #     print(f'list_result_paper_download, {len(list_result_paper_download)}')
                # # Update rel Paper
                # if list_result_paper_download is not None and len(list_result_paper_download) > 0:
                #     for result_paper_download in list_result_paper_download:
                #         q_paper_rel_id = result_paper_download[0]
                #         pdf_name = result_paper_download[1]
                #         check_download_pdf = result_paper_download[2]

                #         if check_download_pdf == True:
                #             file_path_pdf = BASE_DIR_STUDY_PAPER + pdf_name
                #             data = {
                #                 'check_download_pdf': check_download_pdf,
                #                 'file_path_pdf': file_path_pdf,
                #             }
                #             Paper.objects.filter(id=q_paper_rel_id).update(**data)

                #             # Parent Paper의 list_dict_relevant_paper 업데이트
                #             list_dict_xxx_paper_new = []
                #             q_paper_selected.refresh_from_db()
                #             list_dict_reference_paper = q_paper_selected.list_dict_reference_paper
                #             for dict_xxx_paper in list_dict_reference_paper:
                #                 if q_paper_rel_id == dict_xxx_paper['id']:
                #                     print(f'matched q_paper_rel_id: {q_paper_rel_id}')
                #                     dict_xxx_paper_new = dict_xxx_paper
                #                     dict_xxx_paper_new['file_path_pdf'] = file_path_pdf
                #                     dict_xxx_paper.update(dict_xxx_paper_new)
                #                 list_dict_xxx_paper_new.append(dict_xxx_paper)
                #             data = {
                #                 'list_dict_reference_paper': list_dict_xxx_paper_new
                #             }
                #             Paper.objects.filter(id=q_paper_id).update(**data)
                #             q_paper_selected.refresh_from_db()





           # # B-1-1-2. Reference Paper 정보 수집 (w/o Multiprocessing)           
            # list_reference_paper_id = []
            # i = 1
            # for job in list_job:
            #     print(f'///////////////////////////////  i: {i} / {len(list_job)} /////////////////////////////////')
            #     print(f'job: {job}')
            #     rel_id = job[1]
            #     article_url = job[2]
            #     doi = job[3]
            #     site_name = job[4]
            #     related_type = job[5]
            #     dict_paper_rel_info = job[6]
            #     # n = job[7]    # for Multiprocessing (get proxy )
            #     n = None        # for Singleprocessing
            #     if i != 999:
            #         return_value = f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf(q_paper_id, rel_id, article_url, doi, site_name, related_type, dict_paper_rel_info, n)
            #         if return_value is not None:
            #             if return_value not in list_reference_paper_id:
            #                 list_reference_paper_id.append(return_value)
            #     i = i + 1
            # print(f'Total Collected Reference Paper: {list_reference_paper_id}, Number: {len(list_reference_paper_id)}')
            


            # # Set the timeout handler for the SIGALRM signal
            # signal.signal(signal.SIGALRM, timeout_handler_paper_download)
            # try:
            #     signal.alarm(timeout_sec)
            #     print('# 1. 멀티프로세싱 활용 이미지 저장 With WITH 함수, 빠름(2배정도). (중간에 뻗음?)')
            #     with b_Pool(processes=final_processor) as pool:
            #         list_result = pool.starmap(f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf, list_job)
            #     signal.alarm(0)
            # except TimeoutException_paper_download:   
            #     print(f'Time Limit Triggered {timeout_sec} Sec')
            #     pass
            #     # print('# 2. 멀티프로세싱 활용 이미지 저장 Without WITH 함수 but pool.close(), pool.join(). 느림. 안정적(?)')
            #     # pool = b_Pool(processes=final_processor)
            #     # list_result = pool.starmap(f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf, list_job)
            #     # pool.close()
            #     # pool.join()
            # except Exception as e:
            #     print(f"An error occurred: {e}")
            
            # print(f'list_result, {list_result}')




    # random_sec = random.uniform(2, 4)
    # DESTINATION_URL = 'https://www.google.com/'
    # time.sleep(random_sec)

    # driver.get(DESTINATION_URL)
    # source = driver.page_source
    # soup = BeautifulSoup(source)
    # # Find the search box using the name attribute and type the search query
    # search_box = driver.find_element("name", "q")  # The "q" is the name attribute of the Google search box
    # search_box.send_keys(keyword_str)  # Enter your search query
    # # Simulate pressing the Enter key to submit the search
    # search_box.send_keys(Keys.RETURN)
    # time.sleep(random_sec)

    # source = driver.page_source
    # soup = BeautifulSoup(source)    
    # results = soup.find_all(class_="yuRUbf")

    # list_dict_paper_info_from_google  = []
    # list_title_dup_check = []

    # time.sleep(random_sec)
    # i = 0
    # for result in results:
    #     # print(result)
    #     tags = result.find_all('a')
    #     for tag in tags:
    #         # print(tag)
    #         dict_paper_info_from_google = {}

    #         try:
    #             title = tag.text
    #             title = str(title.split('https://')[0])
    #         except:
    #             title = 'null'

    #         try:
    #             text = tag.text
    #             text = result.text
    #             text = text.split('http')[-1]
    #             text = text.split(' ')[0]
    #             text = f'http{text}' 
    #             base_url = str(text)
    #         except:
    #             base_url = 'null'

    #         try:
    #             article_url = str(tag.get('href'))
    #         except:
    #             article_url = 'null'

    #         if title not in list_title_dup_check and title != '' and 'https://' in article_url:
    #             dict_paper_info_from_google['id'] = i
    #             dict_paper_info_from_google['title'] = title
    #             dict_paper_info_from_google['base_url'] = base_url
    #             dict_paper_info_from_google['article_url'] = article_url
    #             list_dict_paper_info_from_google .append(dict_paper_info_from_google)
            
    #         list_title_dup_check.append(title) # 중복등록 방지용
    #     i = i + 1

    # # print('list_dict_paper_info_from_google ', list_dict_paper_info_from_google )
    # driver.quit()
    # return list_dict_paper_info_from_google 









        # if len(list_dict_pdf_link_url) > 0:
        #     for dict_pdf_link_url in list_dict_pdf_link_url:
        #         if dict_pdf_link_url['site_name'] == 'Free PMC article':
        #             pdf_site_url = dict_pdf_link_url['site_url']
        #             try:
        #                 headers = get_random_header()
        #                 response = requests.get(pdf_site_url, headers=headers)
        #                 if response.status_code != 200:
        #                     PROXY_PORT = LIST_PORT_FINEPROXY[n]
        #                     proxy = f"http://{FINEPROXY_USER_NAME}:{FINEPROXY_USER_PASSWORD}@FINEPROXY.XYZ:{PROXY_PORT}"
        #                     response = requests.get(pdf_site_url, proxies={
        #                         'http': proxy,
        #                         'https': proxy
        #                     })
        #                     if response.status_code != 200:
        #                         PROXY_PORT = LIST_PORT_SMARTPROXY[n]
        #                         proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{PROXY_PORT}"
        #                         response = requests.get(pdf_site_url, proxies={
        #                             'http': proxy,
        #                             'https': proxy
        #                         })
        #                         if response.status_code != 200:
        #                             # selenium
        #                             print(f" Tryed Selenium Status code: {response.status_code}")
        #                             driver = boot_google_chrome_driver_in_study_tasks(n)
        #                             driver.get(pdf_site_url)
        #                             source = driver.page_source
        #                             soup = BeautifulSoup(source, 'html.parser')
        #                             print(f"Failed to access given article url using Smartproxy Request. Status code: {response.status_code}")
        #                         else:
        #                             # Smartproxy request
        #                             print(f" Success in Smartproxy Request Status code: {response.status_code}")
        #                             source = response.content
        #                             soup = BeautifulSoup(source, 'html.parser')
        #                         print(f"Failed to access given article url using Fineproxy Request. Status code: {response.status_code}")
        #                     else:
        #                         # Fineproxy request
        #                         print(f" Success in Fineproxy Request Status code: {response.status_code}")
        #                         source = response.content
        #                         soup = BeautifulSoup(source, 'html.parser')
        #                     print(f"Failed to access given article url using Ordinary Request. Status code: {response.status_code}")
        #                 else:
        #                     # Ordinary request
        #                     print(f" Success in Ordinary Request Status code: {response.status_code}")
        #                     source = response.content
        #                     soup = BeautifulSoup(source, 'html.parser')

        #                 # Get PMC PDF Downlaod URL
        #                 pdf_element = soup.find('section', class_='pmc-sidenav__container')
        #                 pdf_url_elements = pdf_element.find_all('a', class_='usa-button')
        #                 for pdf_url_element in pdf_url_elements:
        #                     try:
        #                         pdf_url_text = pdf_url_element.get_test()
        #                     except:
        #                         pdf_url_text = None 
        #                     try:
        #                         pdf_url = pdf_url_element['href']
        #                     except:
        #                         pdf_url = None 
        #                     if 'pdf' in pdf_url:
        #                         pdf_url = pdf_site_url + pdf_url 
        #             except:
        #                 pass
        #         else:
        #             if dict_pdf_link_url['site_name'] == 'Public Library of Science':
        #                 pdf_site_url = dict_pdf_link_url['site_url']
                        
        #                 try:
        #                     headers = get_random_header()
        #                     response = requests.get(pdf_site_url, headers=headers)
        #                     if response.status_code != 200:
        #                         PROXY_PORT = LIST_PORT_FINEPROXY[n]
        #                         proxy = f"http://{FINEPROXY_USER_NAME}:{FINEPROXY_USER_PASSWORD}@FINEPROXY.XYZ:{PROXY_PORT}"
        #                         response = requests.get(pdf_site_url, proxies={
        #                             'http': proxy,
        #                             'https': proxy
        #                         })
        #                         if response.status_code != 200:
        #                             PROXY_PORT = LIST_PORT_SMARTPROXY[n]
        #                             proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{PROXY_PORT}"
        #                             response = requests.get(pdf_site_url, proxies={
        #                                 'http': proxy,
        #                                 'https': proxy
        #                             })
        #                             if response.status_code != 200:
        #                                 # selenium
        #                                 print(f" Tryed Selenium Status code: {response.status_code}")
        #                                 driver = boot_google_chrome_driver_in_study_tasks(n)
        #                                 driver.get(pdf_site_url)
        #                                 source = driver.page_source
        #                                 soup = BeautifulSoup(source, 'html.parser')
        #                                 print(f"Failed to access given article url using Smartproxy Request. Status code: {response.status_code}")
        #                             else:
        #                                 # Smartproxy request
        #                                 print(f" Success in Smartproxy Request Status code: {response.status_code}")
        #                                 source = response.content
        #                                 soup = BeautifulSoup(source, 'html.parser')
        #                             print(f"Failed to access given article url using Fineproxy Request. Status code: {response.status_code}")
        #                         else:
        #                             # Fineproxy request
        #                             print(f" Success in Fineproxy Request Status code: {response.status_code}")
        #                             source = response.content
        #                             soup = BeautifulSoup(source, 'html.parser')
        #                         print(f"Failed to access given article url using Ordinary Request. Status code: {response.status_code}")
        #                     else:
        #                         # Ordinary request
        #                         print(f" Success in Ordinary Request Status code: {response.status_code}")
        #                         source = response.content
        #                         soup = BeautifulSoup(source, 'html.parser')
        #                     pdf_url = None
        #                     pdf_download_element = soup.find('div', class_='dload-pdf')
        #                     pdf_download_url = pdf_download_element.find('a')['href']
        #                     pdf_url = BASE_URL_PLOS + pdf_download_url
        #                 except:
        #                     pass
        #             else:
        #                 pass





        

            # with Pool(processes=final_processor) as pool:
            #     list_result = pool.starmap(f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf, list_job)
            # print(f'list_result, {len(list_result)}')

            # with Pool(processes=final_processor) as pool:
            #     try:
            #         # Submit the task asynchronously with apply_async
            #         list_result = pool.starmap(f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf, list_job).get(timeout=120)
            #         # Wait for the result with a timeout of 120 seconds
            #     except TimeoutError:
            #         print("Task exceeded the 120-second time limit.")
            #         # Optional: Terminate the pool if needed
            #         pool.terminate()
            #     # finally:
            #     #     # Ensure all workers are cleaned up properly
            #     #     pool.join()

            
            # # Set the timeout handler for the SIGALRM signal
            # signal.signal(signal.SIGALRM, timeout_handler_paper_download)
            # try:
            #     signal.alarm(timeout_sec)
            #     print('# 1. 멀티프로세싱 활용 이미지 저장 With WITH 함수, 빠름(2배정도). (중간에 뻗음?)')
            #     with b_Pool(processes=final_processor) as pool:
            #         list_result = pool.starmap(f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf3, list_job)
            #     signal.alarm(0)
            # except TimeoutException_paper_download:   
            #     print(f'Time Limit Triggered {timeout_sec} Sec')
            #     pass
            #     print('# 2. 멀티프로세싱 활용 이미지 저장 Without WITH 함수 but pool.close(), pool.join(). 느림. 안정적(?)')
            #     pool = b_Pool(processes=final_processor)
            #     list_result = pool.starmap(f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf3, list_job)
            #     pool.close()
            #     pool.join()
            # except Exception as e:
            #     print(f"An error occurred: {e}")


            # with Pool(processes=final_processor) as pool:
            #     for job in list_job:
            #         # Submit job to the pool
            #         async_result = pool.apply_async(f_router_pmc_pubmed_google_to_save_related_paper_info_and_pdf, args=job)
            #         try:
            #             # Wait for the result with a timeout of 120 seconds
            #             result = async_result.get(timeout=120)
            #             list_result.append(result)
            #         except TimeoutError:
            #             # If the task exceeds the timeout, handle it here
            #             print(f"Task with arguments {job} exceeded the 120-second time limit.")
            #             async_result.terminate()  # Terminate the task (optional)
            #             list_result.append(f"Task with {job} terminated due to timeout.")
            




# n = random.randint(0, 9)
    # headers = get_random_header()
    # response = requests.get(parsing_url, headers=headers)
    # if response.status_code != 200:
    #     PROXY_PORT = LIST_PORT_FINEPROXY[n]
    #     proxy = f"http://{FINEPROXY_USER_NAME}:{FINEPROXY_USER_PASSWORD}@FINEPROXY.XYZ:{PROXY_PORT}"
    #     response = requests.get(parsing_url, proxies={
    #         'http': proxy,
    #         'https': proxy
    #     })
    #     if response.status_code != 200:
    #         PROXY_PORT = LIST_PORT_SMARTPROXY[n]
    #         proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{PROXY_PORT}"
    #         response = requests.get(parsing_url, proxies={
    #             'http': proxy,
    #             'https': proxy
    #         })
    #         if response.status_code != 200:
    #             # selenium
    #             print(f" Tryed Selenium Status code: {response.status_code}")
    #             driver = boot_google_chrome_driver_in_study_tasks(n)
    #             driver.get(parsing_url)
    #             source = driver.page_source
    #             soup = BeautifulSoup(source, 'html.parser')
    #             print(f"Failed to access given article url using Smartproxy Request. Status code: {response.status_code}")
    #         else:
    #             # Smartproxy request
    #             print(f" Success in Smartproxy Request Status code: {response.status_code}")
    #             source = response.content
    #             soup = BeautifulSoup(source, 'html.parser')
    #         print(f"Failed to access given article url using Fineproxy Request. Status code: {response.status_code}")
    #     else:
    #         # Fineproxy request
    #         print(f" Success in Fineproxy Request Status code: {response.status_code}")
    #         source = response.content
    #         soup = BeautifulSoup(source, 'html.parser')
    #     print(f"Failed to access given article url using Ordinary Request. Status code: {response.status_code}")
    # else:
    #     # Ordinary request
    #     print(f" Success in Ordinary Request Status code: {response.status_code}")
    #     source = response.content
    #     soup = BeautifulSoup(source, 'html.parser')


















    



# #------------------------------------------------------------------------------------------------------------------------------------------
# # B-1-1. 선택한 Paper의 PMC url로 기본정보 및 Reference / Relevant / Author Paper 기본정보 획득
# #--------------------------------------------------------------------------------------------------------------------------------------
# # B-1-1-2. Similar Paper Parsing on pubmed: 선택한 Paper의 Similar Paper 정보 긁어오기 
# """
#     <article class="full-docsum" data-rel-pos="1">
#         <div class="item-selector-wrap selectors-and-actions first-selector">
#             <input aria-labelledby="result-selector-label" class="search-result-selector" id="select-29204457" name="search-result-selector-29204457" type="checkbox" value="29204457"/>
#             <label class="search-result-position" for="select-29204457">
#                 <span class="position-number">
#                     1
#                 </span>
#             </label>
#             <div class="result-actions-bar side-bar">
#                 <div class="cite dropdown-block">
#                     <button aria-haspopup="true" class="cite-search-result trigger result-action-trigger citation-dialog-trigger" data-all-citations-url="/29204457/citations/" data-citation-style="nlm" data-ga-action="cite" data-ga-category="save_share" data-ga-label="open" data-pubmed-format-link="/29204457/export/">
#                         Cite
#                     </button>
#                 </div>
#                 <div class="share dropdown-block">
#                     <button aria-haspopup="true" class="share-search-result trigger result-action-trigger share-dialog-trigger" data-facebook-url="http://www.facebook.com/sharer/sharer.php?u=https%3A//pubmed.ncbi.nlm.nih.gov/29204457/" data-permalink-url="https://pubmed.ncbi.nlm.nih.gov/29204457/" data-twitter-url="http://twitter.com/intent/tweet?text=Employing%20a%20Qualitative%20Description%20Approach%20in%20Health%20Care%20Research.%20https%3A//pubmed.ncbi.nlm.nih.gov/29204457/">
#                         Share
#                     </button>
#                 </div>
#             </div>
#         </div>

#         <div class="docsum-wrap">
#             <div class="docsum-content">
#                 <a class="docsum-title" data-article-id="29204457" data-full-article-url="from_linkname=pubmed_pubmed&amp;from_from_uid=29204457&amp;from_pos=1" data-ga-action="1" data-ga-category="result_click" data-ga-label="29204457" href="/29204457/" ref="linksrc=docsum_link&amp;article_id=29204457&amp;ordinalpos=1&amp;page=1">
#                     Employing a Qualitative Description Approach in Health Care Research.
#                 </a>
#                 <div class="docsum-citation full-citation">
#                     <span class="docsum-authors full-authors">
#                         Bradshaw C, Atkinson S, Doody O.
#                     </span>
#                     <span class="docsum-authors short-authors">
#                         Bradshaw C, et al.
#                     </span>
#                     <span class="docsum-journal-citation full-journal-citation">
#                         Glob Qual Nurs Res. 2017 Nov 24;4:2333393617742282. doi: 10.1177/2333393617742282. eCollection 2017 Jan-Dec.
#                     </span>
#                     <span class="docsum-journal-citation short-journal-citation">
#                         Glob Qual Nurs Res. 2017.
#                     </span>
#                     <span class="citation-part">
#                         PMID: 
#                         <span class="docsum-pmid">
#                             29204457
#                         </span>
#                     </span>
#                     <span class="free-resources spaced-citation-item citation-part">
#                         Free PMC article.
#                     </span>
#                 </div>
#                 <div class="docsum-snippet">
#                     <div class="full-view-snippet">
#                     </div>
#                     <div class="short-view-snippet">
#                     </div>
#                 </div>
#             </div>
#             <div class="result-actions-bar bottom-bar">
#                 <div class="cite dropdown-block">
#                     <button aria-haspopup="true" class="cite-search-result trigger result-action-trigger citation-dialog-trigger" data-all-citations-url="/29204457/citations/" data-citation-style="nlm" data-ga-action="cite" data-ga-category="save_share" data-ga-label="open" data-pubmed-format-link="/29204457/export/">
#                         Cite
#                     </button>
#                 </div>
#                 <div class="share dropdown-block">
#                     <button aria-haspopup="true" class="share-search-result trigger result-action-trigger share-dialog-trigger" data-facebook-url="http://www.facebook.com/sharer/sharer.php?u=https%3A//pubmed.ncbi.nlm.nih.gov/29204457/" data-permalink-url="https://pubmed.ncbi.nlm.nih.gov/29204457/" data-twitter-url="http://twitter.com/intent/tweet?text=Employing%20a%20Qualitative%20Description%20Approach%20in%20Health%20Care%20Research.%20https%3A//pubmed.ncbi.nlm.nih.gov/29204457/">
#                         Share
#                     </button>
#                 </div>
#                 <div class="in-clipboard-label" hidden="hidden">
#                     Item in Clipboard
#                 </div>
#             </div>
#         </div>
#     </article>
# """

# def f_scraping_paper_info_on_pubmed_by_multiprocessing(parsing_url):
#     soup = get_soup_using_url_only(parsing_url)
#     if soup is not None:
#         list_dict_similar_paper_info_from_pubmed = []
#         article_elements = soup.find_all('article', class_="full-docsum")
#         i = 1
#         for article_element in article_elements:
#             dict_similar_paper_info_from_pubmed = {}
#             # Title
#             title_element = article_element.find('a', class_="docsum-title")
#             title_href = title_element['href']
#             title_href = BASE_URL_PUBMED + title_href
#             title_text = title_element.get_text().strip()
#             dict_similar_paper_info_from_pubmed['title'] = title_text
#             dict_similar_paper_info_from_pubmed['pubmed_url'] = title_href
#             # Citation
#             citation_element = article_element.find('div', class_="docsum-citation")
#             # Author Info
#             author_element = citation_element.find('span', class_='docsum-authors full-authors')
#             if author_element:
#                 full_authors_text = author_element.get_text(strip=True)
#             else:
#                 full_authors_text = None 
#             dict_similar_paper_info_from_pubmed['full_authors_name'] = full_authors_text
#             # Journal info and DOI
#             journal_element = citation_element.find('span', class_='docsum-journal-citation full-journal-citation')
#             if journal_element:
#                 # Get the text inside the span and strip any leading/trailing whitespace
#                 full_journal_text = journal_element.get_text(strip=True)
#                 if 'doi' in full_journal_text:
#                     doi_text = full_journal_text.split('doi: ')[-1]
#                     doi_text = doi_text.split('. ')[0]
#                     doi_text = doi_text.rstrip('.')
#                     doi_full_text = 'doi: ' + doi_text + '.'
#                     if doi_full_text in full_journal_text:
#                         journal_text = full_journal_text.replace(doi_full_text, '')
#                     else:
#                         journal_text = full_journal_text
#                 else:
#                     doi_text = None
#                     journal_text = full_journal_text
#             else:
#                 journal_text = None 
#                 doi_text = None
#             dict_similar_paper_info_from_pubmed['journal'] = journal_text
#             dict_similar_paper_info_from_pubmed['doi'] = doi_text
#             if doi_text is not None:
#                 dict_similar_paper_info_from_pubmed['doi_url'] = BASE_URL_DOI + doi_text
#             else:
#                 dict_similar_paper_info_from_pubmed['doi_url'] = None
#             # PMID
#             site_citation_element = citation_element.find('span', class_='citation-part')
#             if site_citation_element:
#                 site_citation_text = site_citation_element.get_text(strip=True)
#                 if 'PMID:' in site_citation_text:
#                     pmid_text = site_citation_text.replace('PMID:', '')
#                     try:
#                         pmid = int(pmid_text)
#                     except:
#                         pmid = None 
#                 else:
#                     pmid = None
#             else:
#                 pmid = None
#             dict_similar_paper_info_from_pubmed['pmid'] = pmid
#             list_dict_similar_paper_info_from_pubmed.append(dict_similar_paper_info_from_pubmed)
#     return list_dict_similar_paper_info_from_pubmed
    
    
# #--------------------------------------------------------------------------------------------------------------------------------------
# def scraping_similar_paper_info_on_pubmed(pmid_paper, max_page):
#     print(f'# PMID 활용 Similar Paper Scraping on PubMed 시작, {pmid_paper}')
    
#     random_sec = random.uniform(2, 4)
#     last_page = 1
    
#     # check Total Page
#     page = 1
#     parsing_url = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed&from_uid={pmid_paper}&page={page}'
#     soup = get_soup_using_url_only(parsing_url)
    
#     if soup is not None:
#         try:
#             total_page_element = soup.find('label', class_="of-total-pages").get_text(strip=True)
#             print(f'total_page_element: {total_page_element}')
#             try:
#                 total_page = int(total_page_element.split('of')[-1])
#             except:
#                 total_page = None

#             if total_page is not None:
#                 if total_page > max_page:
#                     last_page = max_page
#                 else:
#                     last_page = total_page
#             else:
#                 last_page = None
#         except:
#             last_page = None
#     else:
#         return None
    
#     print(f'total_page: {total_page}')
#     if last_page == None:
#         return None

#     list_job = []
#     list_result = []
#     max_processor = 50

#     # Parsing Similar Paper Basic Info on Pubmed
#     page = 1
#     while page <= last_page:
#         # print(f'page: {page}')
#         parsing_url = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed&from_uid={pmid_paper}&page={page}'
#         list_job.append(parsing_url)

#     req_processor = len(list_job)
#     # 실제 사용할 프로세서 개수 정하기
#     if max_processor > req_processor:
#         final_processor = req_processor
#     else:
#         final_processor = max_processor
#     print(f'작업해야할 개수: {len(list_job)},  최종 사용 core 개수 : {final_processor}')
    
#     # Use multiprocessing Pool
#     with Pool(processes=final_processor) as pool:
#         # Submit all jobs to the pool simultaneously
#         async_results = [
#             pool.apply_async(f_scraping_paper_info_on_pubmed_by_multiprocessing, args=job)
#             for job in list_job
#         ]
#         # Collect results
#         for i, async_result in enumerate(async_results):
#             try:
#                 # Wait for the result with a timeout of 30 seconds
#                 result = async_result.get(timeout=30)
#                 list_result.append(result)
#             except TimeoutError:
#                 # Handle timeout for the specific task
#                 print(f"Task with arguments {list_job[i]} exceeded the 30-second time limit.")
#                 list_result.append(None)
#     print(f'Length of similar paper scraping list_result, {len(list_result)}')


#     # # Parsing Similar Paper Basic Info on Pubmed
#     # page = 1
#     # while page <= last_page:
#     #     print(f'page: {page}')
#     #     parsing_url = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed&from_uid={pmid_paper}&page={page}'
#     #     soup = get_soup_using_url_only(parsing_url)
#     #     if soup is not None:
#     #         article_elements = soup.find_all('article', class_="full-docsum")
#     #         i = 1
#     #         for article_element in article_elements:
#     #             dict_similar_paper_info_from_pubmed = {}
#     #             # Title
#     #             title_element = article_element.find('a', class_="docsum-title")
#     #             title_href = title_element['href']
#     #             title_href = BASE_URL_PUBMED + title_href
#     #             title_text = title_element.get_text().strip()
#     #             dict_similar_paper_info_from_pubmed['title'] = title_text
#     #             dict_similar_paper_info_from_pubmed['pubmed_url'] = title_href
#     #             # Citation
#     #             citation_element = article_element.find('div', class_="docsum-citation")
#     #             # Author Info
#     #             author_element = citation_element.find('span', class_='docsum-authors full-authors')
#     #             if author_element:
#     #                 full_authors_text = author_element.get_text(strip=True)
#     #             else:
#     #                 full_authors_text = None 
#     #             dict_similar_paper_info_from_pubmed['full_authors_name'] = full_authors_text
#     #             # Journal info and DOI
#     #             journal_element = citation_element.find('span', class_='docsum-journal-citation full-journal-citation')
#     #             if journal_element:
#     #                 # Get the text inside the span and strip any leading/trailing whitespace
#     #                 full_journal_text = journal_element.get_text(strip=True)
#     #                 if 'doi' in full_journal_text:
#     #                     doi_text = full_journal_text.split('doi: ')[-1]
#     #                     doi_text = doi_text.split('. ')[0]
#     #                     doi_text = doi_text.rstrip('.')
#     #                     doi_full_text = 'doi: ' + doi_text + '.'
#     #                     if doi_full_text in full_journal_text:
#     #                         journal_text = full_journal_text.replace(doi_full_text, '')
#     #                     else:
#     #                         journal_text = full_journal_text
#     #                 else:
#     #                     doi_text = None
#     #                     journal_text = full_journal_text
#     #             else:
#     #                 journal_text = None 
#     #                 doi_text = None
#     #             dict_similar_paper_info_from_pubmed['journal'] = journal_text
#     #             dict_similar_paper_info_from_pubmed['doi'] = doi_text
#     #             if doi_text is not None:
#     #                 dict_similar_paper_info_from_pubmed['doi_url'] = BASE_URL_DOI + doi_text
#     #             else:
#     #                 dict_similar_paper_info_from_pubmed['doi_url'] = None
#     #             # PMID
#     #             site_citation_element = citation_element.find('span', class_='citation-part')
#     #             if site_citation_element:
#     #                 site_citation_text = site_citation_element.get_text(strip=True)
#     #                 if 'PMID:' in site_citation_text:
#     #                     pmid_text = site_citation_text.replace('PMID:', '')
#     #                     try:
#     #                         pmid = int(pmid_text)
#     #                     except:
#     #                         pmid = None 
#     #                 else:
#     #                     pmid = None
#     #             else:
#     #                 pmid = None
#     #             dict_similar_paper_info_from_pubmed['pmid'] = pmid
#     #             if dict_similar_paper_info_from_pubmed not in list_dict_similar_paper_info_from_pubmed:
#     #                 list_dict_similar_paper_info_from_pubmed.append(dict_similar_paper_info_from_pubmed)
#     #             i = i + 1
#     #     page = page + 1

#     # driver.quit()
#     print(f'len(list_result), {len(list_result)}')
#     return list_result
