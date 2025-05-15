# vim test.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import time
import random
import urllib.request
import requests
from PIL import Image
import PIL
import os
import pathlib
import platform

from webui.functions import *
from study.tasks import *
from study.models import *

from pdf2image import convert_from_path






#############################################################################################################################################
#############################################################################################################################################
#
#                                                       쿼리 생성 / 리셋
#
#############################################################################################################################################
#############################################################################################################################################



# Default Paper 쿼리 생성
def create_paper():
    hashcode = hashcode_generator()
    data = {
        'hashcode': hashcode,
    }
    q_paper = Paper.objects.create(**data)
    print('Paper 신규 생성!', q_paper)
    return q_paper



# Mysettings Reset하기
def reset_study_paper_list(q_mysettings_study):
    data = {
        # 'actor_selected': None,
        # 'actor_pic_selected': None,
        # 'selected_category_actor': LIST_ACTOR_CATEGORY[0],
        # 'selected_field_actor': LIST_ACTOR_SORTING_FIELD[0],
        # 'selected_category_actor': LIST_ACTOR_CATEGORY[0][0],
        # 'check_field_ascending_actor': True,
        # 'count_page_number_actor': 1,
        # 'list_searched_actor_id': None,
    }
    MySettings_Study.objects.filter(id=q_mysettings_study.id).update(**data)
    return True












#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Paper Parsing 하기
#
#############################################################################################################################################
#############################################################################################################################################


# Chrome Driver 띄우기
def boot_google_chrome_driver_in_study_functions():
    print('# 외부사이트 Update용 # Chrome Driver 띄우기')
    os_name = platform.system()
        
    # Check if the OS is Linux or Windows
    if os_name == 'Linux':
        print("The operating system is Linux.")
        CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
        service = Service(executable_path=CHROME_DRIVER_PATH)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        driver = webdriver.Chrome(service=service, options=chrome_options)
    elif os_name == 'Windows':
        print("The operating system is Windows.")
        driver = webdriver.Chrome()
    return driver 






def convert_pdf_to_images(q_paper_selected_id, file_path_pdf, output_folder_path, file_extension):
    q_paper_selected = Paper.objects.get(id=q_paper_selected_id)
    print('start paper screenshot save!', q_paper_selected.id)
    hashcode = q_paper_selected.hashcode
    list_dict_paper_image = q_paper_selected.list_dict_paper_image
    if list_dict_paper_image is None:
        list_dict_paper_image = []
        
    # Convert PDF to images
    images = convert_from_path(file_path_pdf, dpi=200, fmt='png')
    print('length of images', len(images))
    
    for i, image in enumerate(images, start=1):
        image_filename = f"paper_{hashcode}_image_{i}.{file_extension}"
        print(f'{i} image_filename: {image_filename}')
        image_path = os.path.join(output_folder_path, image_filename)
        image.save(image_path, file_extension)
        list_dict_paper_image.append({'id': i, 'filename': image_filename, 'discard': 'false'})

    data = {
        'list_dict_paper_image': list_dict_paper_image,
    }
    Paper.objects.filter(id=q_paper_selected_id).update(**data)
    q_paper_selected.refresh_from_db()
    print(f'# paper screenshot 저장 종료료, {len(list_dict_paper_image)}장 저장')
    return True




















# # keyword_str 활용 senenium 이용한 Data Scraping on PubMed
# def scraping_paper_info_on_pubmed(q_paper_search_id, keyword_str):
#     print('# keyword_str 활용 senenium 이용한 Data Scraping on PubMed 시작')
#     start_time = time.time()  # Record the start time
#     list_dict_paper_info_from_pubmed = []
#     last_page = 1

#     driver = boot_google_chrome_driver_in_study_functions()
#     random_sec = random.uniform(2, 4)
#     DESTINATION_URL = 'https://pmc.ncbi.nlm.nih.gov/'
#     # time.sleep(random_sec)

#     driver.get(DESTINATION_URL)
#     source = driver.page_source
#     soup = BeautifulSoup(source, 'html.parser')
#     # Find the search box using the name attribute and type the search query
#     search_input = driver.find_element(By.ID, "pmc-search")
#     # search_box = driver.find_element("class", "usa-input")  # The "q" is the name attribute of the Google search box
#     search_input.send_keys(keyword_str)  # Enter your search query
#     # Simulate pressing the Enter key to submit the search
#     search_input.send_keys(Keys.RETURN)
#     # time.sleep(random_sec)

    
#     source = driver.page_source
#     soup = BeautifulSoup(source, 'html.parser')   

#     # Find the input tag and extract the "last" attribute
#     input_tag = soup.find('input', {'id': 'pageno2'})
#     last_page = input_tag['last']
#     if last_page is not None:
#         try:
#             last_page_int = int(last_page)
#         except:
#             last_page_int = 1

#     # 검색 첫 페이지 결과내용 파싱
#     results = soup.find_all(class_="rprt")
#     # time.sleep(random_sec)
#     n = 0
#     n, list_dict_paper_info_from_pubmed = parse_pmc_search_result_from_source(n, results, list_dict_paper_info_from_pubmed, DESTINATION_URL, keyword_str)

#     if last_page_int > 5:
#         last_page_to_parse = 5
#     else:
#          last_page_to_parse = last_page_int
    
#     p = 2
#     while p < last_page_to_parse + 1:
#         try:
#             # Wait until the "Next" button is available and clickable
#             wait = WebDriverWait(driver, 10)
#             next_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'next')))

#             # Click the "Next" button
#             next_button.click()

#             # Wait for 1 second to allow the next page to load
#             time.sleep(1)

#             # Get the page source after the click
#             source = driver.page_source
#             soup = BeautifulSoup(source, 'html.parser')   

#             # 검색 첫 페이지 결과내용 파싱
#             results = soup.find_all(class_="rprt")
#             n, list_dict_paper_info_from_pubmed = parse_pmc_search_result_from_source(n, results, list_dict_paper_info_from_pubmed, DESTINATION_URL, keyword_str)
#             n = n + 1

#         except Exception as e:
#             print(f"Error: {e}")
#         p = p + 1

#     driver.quit()

#     end_time = time.time()  # Record the end time
#     processing_time = end_time - start_time  # Calculate the time difference
#     print(f"Paper Search on PubMed Processed in {processing_time:.4f} seconds") 
#     # PubMed 검색정보 활용 백그라운드 PDF 저장
#     return list_dict_paper_info_from_pubmed









# # keyword_str 활용 senenium 이용한 Data Scraping on Google
# """
#     list_dict_paper_info_from_google 
#     예: 
#     [
#         {
#             'id': 0, 
#             'title': 'PatCID: an open-access dataset of chemical structures in ...Nature', 
#             'base_url': 'https://www.nature.com', 
#             'article_url': 'https://www.nature.com/articles/s41467-024-50779-y'
#         }, {}, {},
#     ]
# """
# def scraping_paper_info_on_gogole(keyword_str):
#     driver = boot_google_chrome_driver_in_study_functions()
#     random_sec = random.uniform(2, 4)
#     DESTINATION_URL = 'https://www.google.com/'
#     time.sleep(random_sec)

#     driver.get(DESTINATION_URL)
#     source = driver.page_source
#     soup = BeautifulSoup(source)
#     # Find the search box using the name attribute and type the search query
#     search_box = driver.find_element("name", "q")  # The "q" is the name attribute of the Google search box
#     search_box.send_keys(keyword_str)  # Enter your search query
#     # Simulate pressing the Enter key to submit the search
#     search_box.send_keys(Keys.RETURN)
#     time.sleep(random_sec)

#     source = driver.page_source
#     soup = BeautifulSoup(source)    
#     results = soup.find_all(class_="yuRUbf")

#     list_dict_paper_info_from_google  = []
#     list_title_dup_check = []

#     time.sleep(random_sec)
#     i = 0
#     for result in results:
#         # print(result)
#         tags = result.find_all('a')
#         for tag in tags:
#             # print(tag)
#             dict_paper_info_from_google = {}

#             try:
#                 title = tag.text
#                 title = str(title.split('https://')[0])
#             except:
#                 title = 'null'

#             try:
#                 text = tag.text
#                 text = result.text
#                 text = text.split('http')[-1]
#                 text = text.split(' ')[0]
#                 text = f'http{text}' 
#                 base_url = str(text)
#             except:
#                 base_url = 'null'

#             try:
#                 article_url = str(tag.get('href'))
#             except:
#                 article_url = 'null'

#             if title not in list_title_dup_check and title != '' and 'https://' in article_url:
#                 dict_paper_info_from_google['id'] = i
#                 dict_paper_info_from_google['title'] = title
#                 dict_paper_info_from_google['base_url'] = base_url
#                 dict_paper_info_from_google['article_url'] = article_url
#                 list_dict_paper_info_from_google .append(dict_paper_info_from_google)
            
#             list_title_dup_check.append(title) # 중복등록 방지용
#         i = i + 1

#     # print('list_dict_paper_info_from_google ', list_dict_paper_info_from_google )
#     driver.quit()
#     return list_dict_paper_info_from_google 







# # 2. 구글에서 획득한 정보로 각각의 사이트 접속해서 PDF 다운경로 획득 및 논문 관련 정보 획득'
# """
#     list_dict_paper_info_from_etc 
#     예:
#     [
#         {
#             'pdf_download_full_url': 'https://www.nature.com/articles/s41467-024-50779-y.pdf',
#             'pdf_title': 's41467-024-50779-y.pdf',
#             'paper_title': 'PatCID: an open-access dataset of chemical structures in patent documents',
#             'dict_first_author_info': {
#                 'first_author_name': 'Lucas Morin',
#                 'main_author_url': 'https://www.nature.com/articles/s41467-024-50779-y#auth-Lucas-Morin-Aff1-Aff2',
#                 'main_author_orcid_url': 'http://orcid.org/0000-0002-5829-5118'
#             },
#             'dict_paper_detail_info': {
#                 'journal_name': 'Nature Communications',
#                 'journal_url': 'https://www.nature.com/ncomms',
#                 'journal_volume': 'volume15',
#                 'article_number': '6532',
#                 'publication_year': '2024'
#             },
#             'abstract': 'The automatic analysis of patent publications has potential to accelerate research across various domains, including drug discovery and material science. Within patent documents, crucial information often resides in visual depictions of molecule structures. PatCID (Patent-extracted Chemical-structure Images database for Discovery) allows to access such information at scale. It enables users to search which molecules are displayed in which documents. PatCID contains 81M chemical-structure images and 14M unique chemical structures. Here, we compare PatCID with state-of-the-art chemical patent-databases. On a random set, PatCID retrieves 56.0% of molecules, which is higher than automatically-created databases, Google Patents (41.5%) and SureChEMBL (23.5%), as well as manually-created databases, Reaxys (53.5%) and SciFinder (49.5%). Leveraging state-of-the-art methods of document understanding, PatCID high-quality data outperforms currently available automatically-generated patent-databases. PatCID even competes with proprietary manually-created patent-databases. This enables promising applications for automatic literature review and learning-based molecular generation methods. The dataset is freely accessible for download.',
#             'references': [
#                 {
#                     'reference_title': 'Ohms, J. Current methodologies for chemical compound searching in patents: a case study.',
#                     'doi': '10.1016/j.wpi.2021.102055',
#                     'doi_url': 'https://doi.org/10.1016%2Fj.wpi.2021.102055',
#                     'google_scholar_url': 'http://scholar.google.com/scholar_lookup?&title=Current%20methodologies%20for%20chemical%20compound%20searching%20in%20patents%3A%20a%20case%20study&journal=World%20Patent%20Inf.&doi=10.1016%2Fj.wpi.2021.102055&volume=66&publication_year=2021&author=Ohms%2CJ'
#                 }, {}, {},
#             'doi': 'https://doi.org/10.1038/s41467-024-50779-y'     
#             ]
#         }, {}, {},
#     ]
# """    
# def parsing_paper_data_from_nature(soup, list_dict_paper_info, base_url, article_url):
#     # 논문 PDF 다운 url 획득
#     list_pdf_url_dup_check = []
    
#     results = soup.find_all(class_="c-pdf-download")
#     for result in results:
#         # print(result)
#         tags = result.find_all('a')
#         for tag in tags:
#             # print(tag)
#             pdf_download_url = tag.get('href')
#             pdf_title = pdf_download_url.split('/')[-1]
#             pdf_download_full_url = base_url + pdf_download_url
#             if pdf_download_full_url not in list_pdf_url_dup_check:
#                 list_pdf_url_dup_check.append(pdf_title)
#                 list_pdf_url_dup_check.append(pdf_download_full_url)
#     if len(list_pdf_url_dup_check) > 0:
#         pdf_title = list_pdf_url_dup_check[0]
#         pdf_download_full_url = list_pdf_url_dup_check[1]
#         list_dict_paper_info['pdf_download_full_url'] = pdf_download_full_url
#         list_dict_paper_info['pdf_title'] = pdf_title
    
#     # 논문 Title 추출
#     list_title_dup_check = []
#     results = soup.find_all(class_="c-article-title")
#     i = 0
#     for result in results:
#         paper_title = result.text
#         if paper_title not in list_title_dup_check:
#             list_title_dup_check.append(paper_title)
#     if len(list_title_dup_check) > 0:
#         paper_title = list_title_dup_check[0]
#     else:
#         paper_title = None
#     list_dict_paper_info['paper_title'] = paper_title

#     # 논문 주저자 추출
#     dict_first_author_info = {}
#     # Find the author name and URL
#     try:
#         author_tag = soup.find('a', {'data-test': 'author-name'})
#     except:
#         author_tag = None
#     try:
#         author_name = author_tag.get_text(strip=True)  # Extract the author's name
#     except:
#         author_name = None
#     try:
#         author_url = author_tag['href']  # Extract the author's link    
#     except:
#         author_url = None

#     # Find the ORCID link (if available)
#     try:
#         orcid_tag = soup.find('a', {'class': 'js-orcid'})
#     except:
#         orcid_tag = None
#     try:
#         orcid_url = orcid_tag['href'] if orcid_tag else None
#     except:
#         orcid_url = None

#     dict_first_author_info['first_author_name'] = author_name
#     try:
#         dict_first_author_info['first_author_url'] = article_url + author_url
#     except:
#         dict_first_author_info['first_author_url'] = None
#     dict_first_author_info['first_author_orcid_url'] = orcid_url
#     list_dict_paper_info['dict_first_author_info'] = dict_first_author_info
    
    
#     # 논문 세부 정보 추출
#     dict_paper_detail_info = {}
#     # Extract journal name
#     try:
#         journal_name = soup.find('i', {'data-test': 'journal-title'}).get_text()
#     except:
#         journal_name = None
#     # Extract journal URL
#     try:
#         journal_url = soup.find('a', {'data-test': 'journal-link'})['href']
#     except: 
#         journal_url = None
#     # Extract journal volume
#     try:
#         journal_volume = soup.find('b', {'data-test': 'journal-volume'}).get_text(strip=True).split()[-1]  # Extracts the number part
#     except:
#         journal_volume = None
#     # Extract article number
#     try:
#         article_number = soup.find('span', {'data-test': 'article-number'}).get_text()
#     except:
#         article_number = None
#     # Extract publication year
#     try:
#         publication_year = soup.find('span', {'data-test': 'article-publication-year'}).get_text()
#     except:
#         publication_year = None

#     dict_paper_detail_info['journal_name'] = journal_name
#     try:
#         dict_paper_detail_info['journal_url'] = base_url + journal_url
#     except:
#         dict_paper_detail_info['journal_url'] = None
#     dict_paper_detail_info['journal_volume'] = journal_volume
#     dict_paper_detail_info['article_number'] = article_number
#     dict_paper_detail_info['publication_year'] = publication_year
#     list_dict_paper_info['dict_paper_detail_info'] = dict_paper_detail_info

#     # 논문 Abstract 추출
#     # Find the <div> tag with id="Abs1-content"
#     abstract_div = soup.find('div', {'id': 'Abs1-content'})
#     if abstract_div:
#         # Find the <p> tag within the div
#         abstract_paragraph = abstract_div.find('p')
#         if abstract_paragraph:
#             abstract_text = abstract_paragraph.get_text(strip=True)
#             print("Abstract:")
#             list_dict_paper_info['abstract'] = abstract_text
#         else:
#             print("Abstract paragraph not found.")
#     else:
#         print("Abstract div not found.")

#     # 논문 Reference 추출
#     reference_items = soup.find_all('li', class_='c-article-references__item')
#     extracted_references = []
#     for ref in reference_items:
#         reference_data = {}
#         # Extract the reference text
#         ref_text_p = ref.find('p', class_='c-article-references__text')
#         if ref_text_p:
#             # To get the text before the <i> tag
#             # Iterate through the contents and collect text until <i> tag
#             title = ""
#             for content in ref_text_p.contents:
#                 if content.name == 'i':
#                     break
#                 if isinstance(content, str):
#                     title += content.strip()
#                 else:
#                     title += content.get_text(strip=True)
#             reference_data['reference_title'] = title
#         else:
#             reference_data['reference_title'] = 'N/A'
#         # Extract the doi and doi URL
#         links_p = ref.find('p', class_='c-article-references__links')
#         if links_p:
#             doi_a = links_p.find('a', attrs={'data-track-action': 'article reference'})
#             if doi_a:
#                 reference_data['doi'] = doi_a.get('data-doi', 'N/A')
#                 reference_data['doi_url'] = doi_a.get('href', 'N/A')
#             else:
#                 reference_data['doi'] = 'N/A'
#                 reference_data['doi_url'] = 'N/A'
#             # Extract Google Scholar URL
#             gs_a = links_p.find('a', attrs={'data-track-action': 'google scholar reference'})
#             if gs_a:
#                 reference_data['google_scholar_url'] = gs_a.get('href', 'N/A')
#             else:
#                 reference_data['google_scholar_url'] = 'N/A'
#         else:
#             reference_data['doi'] = 'N/A'
#             reference_data['doi_url'] = 'N/A'
#             reference_data['google_scholar_url'] = 'N/A'
        
#         extracted_references.append(reference_data)
#     list_dict_paper_info['references'] = extracted_references
    
#     # Doi 획득
#     results = soup.find_all('span', class_='c-bibliographic-information__value')
#     doi = 'null'
#     for result in results:
#         if 'doi' in result.text:
#             doi = result.text.strip()
#     list_dict_paper_info['doi'] = doi

    
#     # Nature 정보 획득 종료
#     return list_dict_paper_info
