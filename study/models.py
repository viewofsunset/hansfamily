from django.db import models
from django.contrib.auth.models import User 


BASE_URL_PUBMED_FREE = 'https://pmc.ncbi.nlm.nih.gov'
BASE_URL_PUBMED = 'https://pubmed.ncbi.nlm.nih.gov'
BASE_URL_GOOGLE_SCHOLAR = 'https://scholar.google.com'
BASE_URL_DOI = 'https://doi.org/'
BASE_URL_SCI_HUB = 'sci.bban.top/pdf/'
BASE_URL_PLOS = 'https://journals.plos.org'

IP_CHECK_SITE = 'https://api.ip.pe.kr/'

# PROXY Fineproxy
# https://fineproxy.org/

"""
proxy = {
'http': f'http://{username}:{password}@FINEPROXY.XYZ:3081
'https': f'socks5://{username}:{password}@FINEPROXY.XYZ:20
'https': http://{username}:{password}@FINEPROXY.XYZ:3081
}
# 다운로드 할 url
url = 'https://api.ip.pe.kr/'
response = requests.get(url, proxies=proxy)
print(response.status_code)
print(response.text)
"""
FINEPROXY_USER_NAME = 'PPR02AZKK2F'
FINEPROXY_USER_PASSWORD = 'hiDl62jue9fdQ6' 

LIST_PORT_FINEPROXY = [
    3081,
    3082,
    3083,
    3084,
    3085,
    3086,
    3087,
    3088,
    3089,
    3090,
    3091,
    3092,
    # 'FINEPROXY.XYZ:3081',
    # 'FINEPROXY.XYZ:3082',
    # 'FINEPROXY.XYZ:3083',
    # 'FINEPROXY.XYZ:3084',
    # 'FINEPROXY.XYZ:3085',
    # 'FINEPROXY.XYZ:3086',
    # 'FINEPROXY.XYZ:3087',
    # 'FINEPROXY.XYZ:3088',
    # 'FINEPROXY.XYZ:3089',
    # 'FINEPROXY.XYZ:3090',
    # 'FINEPROXY.XYZ:3091',
    # 'FINEPROXY.XYZ:3092',
]

# PROXY Smartproxy
# https://smartproxy.com/
""" 
    import requests
    url = 'https://ip.smartproxy.com/json'
    username = 'spc4smgi85'
    password = 'kP1zT8dVgatnJi4+4b'
    proxy = f"http://{username}:{password}@us.smartproxy.com:10001"
    result = requests.get(url, proxies = {
        'http': proxy,
        'https': proxy
    })
    print(result.text)
"""

SMARTPROXY_USER_NAME = 'spc4smgi85'
SMARTPROXY_USER_PASSWORD = 'kP1zT8dVgatnJi4+4b'
LIST_PORT_SMARTPROXY = [
    10001,
    10002,
    10003,
    10004,
    10005,
    10006,
    10007,
    10008, 
    10009,
    10010,

    # 'us.smartproxy.com:10001:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10002:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10003:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10004:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10005:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10006:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10007:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10008:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10009:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10010:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10011:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10012:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10013:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10014:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10015:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10016:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10017:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10018:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10019:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10020:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10021:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10022:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10023:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10024:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10025:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10026:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10027:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10028:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10029:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10030:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10031:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10032:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10033:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10034:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10035:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10036:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10037:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10038:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10039:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10040:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10041:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10042:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10043:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10044:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10045:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10046:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10047:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10048:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10049:spc4smgi85:kP1zT8dVgatnJi4+4b',
    # 'us.smartproxy.com:10050:spc4smgi85:kP1zT8dVgatnJi4+4b',
]


BASE_DIR_STUDY = '/media/vault1/study/'
BASE_DIR_STUDY_PAPER = '/media/vault1/study/paper/'
RELATIVE_PATH_STUDY_PAPER = 'vault1/study/paper/'
BASE_DIR_STUDY_PAPER_SCREENSHOT = '/media/vault1/study/paper/screenshot/'
RELATIVE_PATH_STUDY_PAPER_SCREENSHOT = 'vault1/study/paper/screenshot/'



class My_Study(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    check_discard = models.BooleanField(default=False)



class Conference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    check_discard = models.BooleanField(default=False)






class Paper_Search_Google_and_PubMed(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    keyword = models.TextField(null=True, blank=True)
    keyword_ordered = models.TextField(null=True, blank=True)

    list_dict_paper_info_from_pubmed = models.JSONField(null=True, blank=True)
    list_dict_paper_info_from_google = models.JSONField(null=True, blank=True)
    list_dict_paper_info_from_voronoi_db = models.JSONField(null=True, blank=True)
    list_dict_paper_info_from_my_favorite = models.JSONField(null=True, blank=True)
    list_dict_paper_info_from_etc = models.JSONField(null=True, blank=True)
            
    list_paper_id_from_pubmed = models.JSONField(null=True, blank=True)
    list_paper_id_from_google = models.JSONField(null=True, blank=True)
    list_paper_id_from_etc = models.JSONField(null=True, blank=True)
    list_paper_id_from_voronoi_db = models.JSONField(null=True, blank=True)
    list_paper_id_from_my_favorite = models.JSONField(null=True, blank=True)

    list_selected_search_options = models.JSONField(null=True, blank=True) # ['all']
    
    # system
    date_searched = models.DateField(auto_now_add=True)



LIST_NOT_AUTHOR_NAME = ['PMC Copyright notice']

class Paper(models.Model):
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    
    # Basic Info of Selected Paper
    title = models.TextField(null=True, blank=True)
    abstract = models.TextField(max_length=250, null=True, blank=True)
    doi = models.CharField(max_length=250, null=True, blank=True)
    pmid = models.CharField(max_length=250, null=True, blank=True)
    pmcid = models.CharField(max_length=250, null=True, blank=True)
    first_author_name = models.TextField(max_length=250, null=True, blank=True)
    first_author_url = models.TextField(max_length=250, null=True, blank=True)
    journal_info = models.TextField(max_length=250, null=True, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    
    # Selected Paper Downloaded Data path
    file_path_xml = models.TextField(max_length=250, null=True, blank=True)
    file_path_pdf = models.TextField(max_length=250, null=True, blank=True)
    check_download_pdf = models.BooleanField(default=False)

    doi_url = models.CharField(max_length=250, null=True, blank=True)
    pdf_url = models.TextField(max_length=250, null=True, blank=True)
    article_url = models.TextField(max_length=250, null=True, blank=True)

    # Selected Paper Info
    dict_paper_info = models.JSONField(null=True, blank=True) # 공통으로 필요한 정보
    dict_paper_info_from_pubmed = models.JSONField(null=True, blank=True) # Pubmed에서 수집한 정보
    dict_paper_info_from_google = models.JSONField(null=True, blank=True) # Google에서 수집한 정보
    list_dict_paper_image = models.JSONField(null=True, blank=True) # pdf page convert to image 정보
    
    # Selected Paper Related Paper info
        # Reference Papers
    list_dict_reference_paper = models.JSONField(null=True, blank=True)  # including reference paper info and downloaded PDF file path
    list_reference_paper_id = models.JSONField(null=True, blank=True)  # Reference Paper의 Paper Query ID
        # Relevant Papers
    list_dict_relevant_paper = models.JSONField(null=True, blank=True)  # including reference paper info and downloaded PDF file path
    list_relevant_paper_id = models.JSONField(null=True, blank=True)  # Reference Paper의 Paper Query ID
        # Author Papers
    list_dict_author_paper = models.JSONField(null=True, blank=True)  # including reference paper info and downloaded PDF file path
    list_author_paper_id = models.JSONField(null=True, blank=True)  # Reference Paper의 Paper Query ID
    
    # hierachy
    list_dict_paper_hierachy = models.JSONField(null=True, blank=True)  # Main Paper and related paper hiarachy == 주저자의 이전 논문들, 이후 논문들, 교신저자의 논문들, 현재 논문을 Citation한 타 논문들
    # Analysis Report
    list_report_dict_ref_paper_parsing_result = models.JSONField(null=True, blank=True)  # 선택 논문 기준으로 파싱한 레퍼런스, 주저자관련, 동일주제 관련 논문들 파싱 결과 리포트
    # User Customized    
    list_bookmarked_user_id = models.JSONField(null=True, blank=True)
    # system
    date_created = models.DateField(auto_now_add=True, null=True)
    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} Paper'
    




class Patent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    check_discard = models.BooleanField(default=False)



class Protocol(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    check_discard = models.BooleanField(default=False)



class FDA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    check_discard = models.BooleanField(default=False)



class Lecture(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    check_discard = models.BooleanField(default=False)




LIST_MENU_STUDY = (
    ('01', 'MY_STUDY'),
    ('02', 'CONFERENCE'),
    ('03', 'PAPER'),
    ('04', 'PATENT'),
    ('05', 'PROTOCOL'),
    ('06', 'FDA'),
    ('07', 'LECTURE'),
)
LIST_TABS_SEARCHED_PAPER = ['Pubmed', 'Google Scholar', 'Voronoi DB' ,'My Favorite']
LIST_TABS_COLLECTED_PAPER = ['Reference', 'Similar', 'First Author']

MAX_NUM_PAPER_SEARCH_HISTORY = 10
# LIST_TABS_COLLECTED_PAPER = (
#     ('01', 'Reference'),
#     ('02', 'Similar'),
#     ('03', 'First Author'),
# )



class MySettings_Study(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    menu_selected = models.CharField(choices=LIST_MENU_STUDY, default=LIST_MENU_STUDY[0][0], blank=True)
    # Paper
    active_tab_searched_paper = models.CharField(default=LIST_TABS_SEARCHED_PAPER[0], blank=True) # 검색화면 현재 선택된 탭
    list_selected_options_paper_search = models.JSONField(null=True, blank=True) # 검색시 수행할 DB들 
    active_tab_collected_paper = models.CharField(default=LIST_TABS_COLLECTED_PAPER[0], blank=True)
    
    paper_search_selected = models.ForeignKey(Paper_Search_Google_and_PubMed, on_delete=models.SET_NULL, null=True, blank=True)
    paper_selected = models.ForeignKey(Paper, on_delete=models.SET_NULL, null=True, blank=True)
    list_history_search_paper = models.JSONField(null=True, blank=True) # [{'id':xxx, 'paper_search_google_id':yyy, 'paper_search_keyword': 'zzz' , 'list_selected_options_paper_search': []}]
    list_bookmarked_paper_id = models.JSONField(null=True, blank=True) 
    
    check_discard = models.BooleanField(default=False)




class SystemSettings_Study(models.Model):
    check_discard = models.BooleanField(default=False)










# Step 1 - PubMed 키워드 검색

""" 
    Paper_Search_Google_and_PubMed 
        list_dict_paper_info_from_pubmed = 
        [
            {
                "id": 0, 
                "doi": "10.1186/s12961-021-00801-2", 
                "pmcid": "PMC8743061", 
                "title": "“There hasn’t been a career structure to step into”: a qualitative study on perceptions of allied health clinician researcher careers", 
                "doi_url": "https://doi.org/10.1186/s12961-021-00801-2", 
                "keyword": "career researchers pathways", 
                "pdf_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8743061/pdf/12961_2021_Article_801.pdf", 
                "article_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8743061/?report=classic", 
                "abstract_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8743061/?report=abstract", 
                "journal_name": "Health Res Policy Syst. 2022; 20: 6.  Published online 2022 Jan 9. doi: 10.1186/s12961-021-00801-2", 
                "publication_year": 2022, 
                "first_author_name": "Caitlin Brandenburg, Elizabeth C. Ward"
            },
            {}, 
            {}, ...
    ]
"""


# Step 2 -  Pubmed 논문 검색 결과 활용 자동으로 백그라운드 논문 PDF 다운로드 및 Paper 쿼리 생성

"""
    Paper
    {
        'file_path_pdf': pdf_name, 
        'hashcode': hashcode, 
        'title': title, 
        'doi': doi, 
        'doi_url': doi_url, 
        'pmcid': pmcid, 
        'first_author_name': first_author_name, 
        'dict_paper_info': {
            "keyword": "career researchers pathways", 
            "pdf_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10019401/pdf/10775_2023_Article_9590.pdf", 
            "article_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10019401/?report=classic", 
            "abstract_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10019401/?report=abstract", 
            "journal_name": "Int J Educ Vocat Guid. 2023 Mar 16 : 1–26.  doi: 10.1007/s10775-023-09590-2 [Epub ahead of print]", 
            "publication_year": null
        }
    }


"""

# Step 3 -  Pubmed 논문 검색 결과 리스트에서 사용자가 추가적인 데이터 확보를 위해 선택한 Paper에 대해 
#           추가정보 (레퍼런스 논문, 저자 논문, 선택논문과 연관성 높은 논문 등) 획득 Paper PDF 다운로드 및 Paper 쿼리 생성
"""
    Paper
    {
        list_dict_reference_paper: [
            {   
                'id': id,
                'q_paper_id': q_paper_id,
                'title': title,
                'cite': cite,
                'doi': doi,
                'doi_url': doi_link,
                'pubmed_url': pubmed_url,
                'pubmed_free_url': pubmed_free_url,
                'google_scholar_url': google_scholar_url,   
                'other_url': other_url,
            }
        ]
        list_dict_author_paper: [
            {

            }
        ]
        list_dict_relevant_paper: [
            {
            
            }
        ]
        list_reference_paper_id: [
            {
            
            }
        ]
        list_author_paper_id: list_author_paper_id
        list_relevant_paper_id: list_relevant_paper_id
        list_dict_paper_hierachy: list_dict_paper_hierachy
    }

"""
