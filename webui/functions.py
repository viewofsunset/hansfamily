import uuid
import os
import io
import cv2

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from pathlib import Path
from PIL import Image
from PIL import ImageSequence
from tinytag import TinyTag

# text handling
import re
import spacy  
import datetime
import multiprocessing
import time
import pathlib
import shutil
import requests

from hans_ent.models import *
from hans_ent.tasks import *
from webui.models import LIST_STR_NONE_SERIES
from study.models import *



#############################################################################################################################################
#############################################################################################################################################
#
#                                                       시스템 유틸리티 (공통)
#
#############################################################################################################################################
#############################################################################################################################################


#----------------------------------------------------------------------------------------------------------------------------------------

# CPU 개수 파악
def get_cpu_count():
    cpu_count = os.cpu_count()
    if cpu_count is None:
        print("Unable to determine CPU count")
        cpu_count = 1  # Default to 1 if count cannot be determined
    print(f"Number of CPUs: {cpu_count}")
    return cpu_count


# Chrome Driver 띄우기
def boot_google_chrome_driver():
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



# Storage Monitoring
def storage_monitoring():
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    list_dict_stoage_status = q_systemsettings_hansent.list_dict_stoage_status
    if list_dict_stoage_status is None:
        list_dict_stoage_status = []

    for VAULT in LIST_VAULT:
        print(VAULT)
        path=f"/django-project/site/public/media/{VAULT}/"
        total, used, free = shutil.disk_usage(path)
        total_volume = round(total / (1024 ** 3), 1)
        used_volume = round(used / (1024 ** 3), 1)
        free_volume = round(free / (1024 ** 3), 1)
        occupant = round(used_volume/total_volume, 3)*100
        disk_info = {'name': VAULT, 'path': path, 'total_volume': total_volume, 'used_volume': used_volume, 'free_volume': free_volume, 'occupant': occupant}
        print('disk_info', disk_info)
        print(f"경로: {path}")
        print(f"총 용량: {total_volume:.2f} GB")
        print(f"사용 중: {used_volume:.2f} GB")
        print(f"남은 용량: {free_volume:.2f} GB")
        print(f"사용량: {occupant} %")

        if len(list_dict_stoage_status) > 0:
            check_vault_exist = False
            for dict_stoage_status in list_dict_stoage_status:
                if dict_stoage_status['name'] == VAULT:
                    dict_stoage_status['path'] = path
                    dict_stoage_status['total_volume'] = total_volume
                    dict_stoage_status['used_volume'] = used_volume
                    dict_stoage_status['free_volume'] = free_volume
                    dict_stoage_status['occupant'] = occupant
                    check_vault_exist = True
                    break 
            if check_vault_exist == False:
                list_dict_stoage_status.append(disk_info)
        else:
            list_dict_stoage_status.append(disk_info)

    data = {
        'list_dict_stoage_status': list_dict_stoage_status,
    }
    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
    return list_dict_stoage_status




#############################################################################################################################################
#############################################################################################################################################
#
#                                                       텍스트 핸들링 유틸리티 (공통)
#
#############################################################################################################################################
#############################################################################################################################################



#----------------------------------------------------------------------------------------------------------------------------------------
# Text 핸들링
#----------------------------------------------------------------------------------------------------------------------------------------
# Text가 영어인지 판독독
def is_english(text):
    try:
        # Try encoding the string to ASCII
        text.encode('ascii')
    except UnicodeEncodeError:
        # If there's a UnicodeEncodeError, the text is not ASCII (hence not English)
        return False
    return True


# 파일 이름 클리닝
def file_name_cleaner(file_name):
    try:
        print('1')
        file_name = str(file_name)
        if is_english(file_name):
            print('English')
            pass 
        else:
            print('not English')
            # file_name = file_name.encode('utf-8')
            try:
                file_name = file_name.encode('latin1').decode('euc-kr') 
            except:
                pass
            print('file_name', file_name)

        file_name = file_name.replace('.', '_')
        file_name = file_name.replace(',', '_')
        file_name = file_name.replace(' ', '')
        file_name = file_name.replace('(', '')
        file_name = file_name.replace(')', '')
        file_name = file_name.replace('"', '')
        file_name = file_name.replace("'", "")
        file_name = file_name.replace('/', '')
        file_name = file_name.replace('!', '')
        file_name = file_name.replace('$', '')
        file_name = file_name.replace('&', '')
        file_name = file_name.replace('%', '')
        file_name = file_name.replace('^', '')
        file_name = file_name.replace('*', '')
        file_name = file_name.replace('[', '')
        file_name = file_name.replace(']', '')
        file_name = file_name.replace('@', '')
        file_name = file_name.replace('#', '')
        file_name = file_name.replace('+', '')
        file_name = file_name.replace('~', '')
        file_name = file_name.replace('{', '')
        file_name = file_name.replace('}', '')
        file_name = file_name.replace('|', '')
        file_name = file_name.replace('?', '')
        file_name = file_name.replace('>', '')
        file_name = file_name.replace('=', '')
        file_name = file_name.replace('__', '_')
        if '_mp4' in file_name:
            file_name = file_name.replace('_mp4', '.mp4')
        elif '_mp3' in file_name:
            file_name = file_name.replace('_mp3', '.mp3')
        elif '_avi' in file_name:
            file_name = file_name.replace('_avi', '.avi')
        elif '_mkv' in file_name:
            file_name = file_name.replace('_mkv', '.mkv')
        elif '_srt' in file_name:
            file_name = file_name.replace('_srt', '.srt') 
        elif '_smi' in file_name:
            file_name = file_name.replace('_smi', '.smi')
        elif '_vtt' in file_name:
            file_name = file_name.replace('_vtt', '.vtt') 
        elif '_jpg' in file_name:
            file_name = file_name.replace('_jpg', '.jpg') 
        elif '_jpeg' in file_name:
            file_name = file_name.replace('_jpeg', '.jpeg')
        elif '_png' in file_name:
            file_name = file_name.replace('_png', '.png') 
        # elif '_gif' in file_name:
        #     file_name = file_name.replace('_gif', '.gif') 
        else:
            file_name = file_name
    except:
        print('9')
        file_name = 'unknown'
    return file_name


# 파일 이름 클리닝 for keywords
def file_name_cleaner_for_keywords(file_name):
    try:
        print('1')
        file_name = str(file_name)
        if is_english(file_name):
            print('English')
            pass 
        else:
            print('not English')
            # file_name = file_name.encode('utf-8')
            try:
                file_name = file_name.encode('latin1').decode('euc-kr') 
            except:
                pass
            print('file_name', file_name)
        file_name = file_name.replace('.', ' ')
        file_name = file_name.replace(', ', ' ')
        file_name = file_name.replace(',', ' ')
        file_name = file_name.replace('_', ' ')
        file_name = file_name.replace('__', ' ')
        
        file_name = file_name.replace('(', '')
        file_name = file_name.replace(')', '')
        file_name = file_name.replace('"', '')
        file_name = file_name.replace("'", "")
        file_name = file_name.replace('/', '')
        file_name = file_name.replace('!', '')
        file_name = file_name.replace('$', '')
        file_name = file_name.replace('&', '')
        file_name = file_name.replace('%', '')
        file_name = file_name.replace('^', '')
        file_name = file_name.replace('*', '')
        file_name = file_name.replace('[', '')
        file_name = file_name.replace(']', '')
        file_name = file_name.replace('@', '')
        file_name = file_name.replace('#', '')
        file_name = file_name.replace('+', '')
        file_name = file_name.replace('~', '')
        file_name = file_name.replace('{', '')
        file_name = file_name.replace('}', '')
        file_name = file_name.replace('|', '')
        file_name = file_name.replace('?', '')
        file_name = file_name.replace('>', '')
        file_name = file_name.replace('=', '')
        file_name = file_name.replace(':', '')
        file_name = file_name.replace(';', '')
        file_name = file_name.replace('`', '')
    except:
        print('9')
        file_name = None
    return file_name


# 텍스트 클리닝 하기
def text_cleaning(text):
    text = text.replace('.mp4', '')
    text = text.replace('.jpg', '')
    text = text.replace('.png', '')
    text = text.replace('.avi', '')
    text = text.replace('.', ' ')
    text = text.replace(',', ' ')
    text = text.replace('-', ' ')
    text = text.replace('_', ' ')
    text = text.replace('「', ' ')
    text = text.replace('」', ' ')
    text = text.replace('【', ' ')
    text = text.replace('】', ' ')
    text = text.replace('[', '')
    text = text.replace(']', '')
    text = text.replace('(', '')
    text = text.replace(')', '')
    text = text.replace('!', '')
    text = text.replace('@', '')
    text = text.replace('#', '')
    text = text.replace('$', '')
    text = text.replace('%', '')
    text = text.replace('^', '')
    text = text.replace('&', '')
    text = text.replace('*', '')
    text = text.replace('=', '')
    text = text.replace('+', '')
    text = text.replace('/', '')
    text = text.replace('~', '')
    
    # print('text', text)
    return text


# 클리닝된 텍스트 뭉치에서 단어 분리 => 단어 리스트화
def text_to_list_word(file_name_cleaned):
    list_file_name_split = file_name_cleaned.split(' ')
    list_file_name_split = [x for x in list_file_name_split if len(x) != 1] # 길이가 1개짜리 element 제거
    return list_file_name_split


# 클리닝된 텍스트 뭉치에서 이름름 분리 => 단어 리스트화
def text_to_list_name(file_name_cleaned):
    list_file_name_split = file_name_cleaned.split('aka')
    list_file_name_split = [x for x in list_file_name_split if len(x) != 1] # 길이가 1개짜리 element 제거
    return list_file_name_split


#----------------------------------------------------------------------------------------------------------------------------------------
# 한글 초성으로 Ordering 하기
def get_chosung(char):
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    code = ord(char) - 0xAC00
    if code < 0 or code > 11171:
        return char
    chosung = code // 588
    return CHOSUNG_LIST[chosung]


def sort_queryset_by_korean_title(queryset, field_ascending_str):
    if field_ascending_str == True:
        print('No reverse')
        return sorted(queryset, key=lambda obj: get_chosung(obj.title[0]))
    if field_ascending_str == False:
        print('Reverse')
        return sorted(queryset, key=lambda obj: get_chosung(obj.title[0]), reverse=True)
    

def sort_list_dict_by_chosung(list_dict):
    """한글 초성 기준으로 정렬"""
    return sorted(
        list_dict,
        key=lambda x: get_chosung(x['title'][0])
    )


#----------------------------------------------------------------------------------------------------------------------------------------

# 단어 리스트에서 Tag으로 쓸만한 단어 수집
def collect_tag_element_from_text(list_file_name_split):
    # 이름에서 Tag 수집
    list_collected_tags = []
    if list_file_name_split is not None and len(list_file_name_split) > 0:
        for item in list_file_name_split:
            # print('item', item)
            check_tag_available = True
            # 숫자들 제외
            try:
                item = int(item)
                check_tag_available = False
            except:
                item = item
            # 단어 하나당 길이가 2 이하인 것은 제외
            try:
                if len(item) < 3: 
                    check_tag_available = False
            except:
                pass

            if check_tag_available == True:
                list_collected_tags.append(item)
    return list_collected_tags



# 단어 개수 최대치 제한하기
def truncate_words_regex(text, max_words):
    import re
    try:
        match = re.match(r'^(\S+(?:\s+\S+){0,' + str(max_words-1) + r'})', text)
        return match.group(1) + '…' if match and len(match.group(1).split()) < len(text.split()) else text
    except:
        return None



# 단어 리스트에서 Title 반환
def list_word_joining_for_title(list_word):
    # print('# 사용자 입력 title이 없는 경우')
    # print('# file 이름이 하나의 의미없는 암화화된 긴 단어 형태이면 입력값 타이틀에서 차용한다.')
    list_word_short = []
    title_item = None
    # title로 쓰기 적합하게 길이 조정
    for item in list_word:
        if len(item) < 30: # 단어 하나당 길이가 30 이하인 것만
            list_word_short.append(item)
    # 길이 30 이하인 단어들을 활용하여 타이틀 선정
    try:
        if len(list_word_short) == 0:
            # print('# 단어길이 30 이하가 하나도 없는 경우 == 30 이상의 엄청 긴 길이의 단어로 이루어진 경우')
            # print('# 앨범 타이틀도 없고 파일 암호화이름인 경우, 처음 10 letter만 따온다.')
            text = list_word[0]
            # Extract only alphabetic characters
            letters = [char for char in text if char.isalpha()]
            # Join the first 30 letters
            title_item = ''.join(letters[:30])
            title_item = title_item + '…'
        else:
            # print('# 적절한 단어(단어길이 30 이하)가 하나 이상 있는 경우 == 타이틀로 쓸 단어가 1개 이상 있는 경우')
            # print('# 단어들끼리 스페이스 넣고 붙힌다.')
            # Convert all items to strings
            str_items = map(str, list_word_short)
            space_separator = ' '
            text = space_separator.join(str_items)
            # 단어 개수 최대치 제한하기
            title_item = truncate_words_regex(text, max_words=7)
    except:
        pass 
    return title_item
    

# 이름 리스트에서 Name과 Synonyms 반환
def classify_name_and_synonyms_from_list_word(list_word):
    synonyms = []
    list_word_short = []
    for item in list_word:
        if len(item) < 30: # 단어 하나당 길이가 30 이하인 것만
            list_word_short.append(item)
    i = 0
    for item in list_word_short:
        if i == 0:
            name = item
        else:
            synonyms(item)
    if len(synonyms) == 0:
        synonyms = None
    return name, synonyms 

#----------------------------------------------------------------------------------------------------------------------------------------


# #############################################################################################################################################
# #############################################################################################################################################
# #
# #                                                       Study 웹화면 기능 서포트
# #
# #############################################################################################################################################
# #############################################################################################################################################

def study_count_page_number_reset(q_mysettings_study):
    menu_selected = q_mysettings_study.menu_selected
    data = {}
    MySettings_Study.objects.filter(id=q_mysettings_study.id).update(**data)
    q_mysettings_study.refresh_from_db()
    return True


def hans_ent_count_page_number_reset(q_mysettings_hansent):
    print('reset')
    menu_selected = q_mysettings_hansent.menu_selected
    data = {
        'count_page_number_actor': 1,
        'count_page_number_picture': 1,
        'count_page_number_manga': 1,
        'count_page_number_video': 1,
        'count_page_number_music': 1,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    q_mysettings_hansent.refresh_from_db()
    return True





# #############################################################################################################################################
# #############################################################################################################################################
# #
# #                                                       Hans Ent 웹화면 기능 서포트
# #
# #############################################################################################################################################
# #############################################################################################################################################


def hans_ent_count_page_number_down(request, q_mysettings_hansent):
    menu_selected = q_mysettings_hansent.menu_selected
    count_page_number_str = request.POST.get('count_page_number')
    count_page_number_str = None if count_page_number_str in LIST_STR_NONE_SERIES else count_page_number_str
    if count_page_number_str is not None:
        count_page_number = int(count_page_number_str)
    else:
        count_page_number = None
    
    if count_page_number is not None and count_page_number > 1:
        count_page_number = int(count_page_number)
        if menu_selected == LIST_MENU_HANS_ENT[0][0]:
            data = {'count_page_number_actor': count_page_number - 1}
        elif menu_selected == LIST_MENU_HANS_ENT[1][0]:
            data = {'count_page_number_picture': count_page_number - 1}
        elif menu_selected == LIST_MENU_HANS_ENT[2][0]:
            data = {'count_page_number_manga': count_page_number - 1}
        elif menu_selected == LIST_MENU_HANS_ENT[3][0]:
            data = {'count_page_number_video': count_page_number - 1}
        elif menu_selected == LIST_MENU_HANS_ENT[4][0]:
            data = {'count_page_number_music': count_page_number - 1}
        MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
        q_mysettings_hansent.refresh_from_db()
    return True



def hans_ent_count_page_number_up(request, q_mysettings_hansent, total_num_registered_item):
    menu_selected = q_mysettings_hansent.menu_selected
    count_page_number_max = total_num_registered_item // LIST_NUM_DISPLAY_IN_PAGE
    count_page_number_max = count_page_number_max + 1
    
    count_page_number_str = request.POST.get('count_page_number')
    count_page_number_str = None if count_page_number_str in LIST_STR_NONE_SERIES else count_page_number_str
    if count_page_number_str is not None:
        count_page_number = int(count_page_number_str)
    else:
        count_page_number = None
    
    if count_page_number is not None and count_page_number < count_page_number_max:
        count_page_number = int(count_page_number)
        if menu_selected == LIST_MENU_HANS_ENT[0][0]:
            data = {'count_page_number_actor': count_page_number + 1}
        elif menu_selected == LIST_MENU_HANS_ENT[1][0]:
            data = {'count_page_number_picture': count_page_number + 1}
        elif menu_selected == LIST_MENU_HANS_ENT[2][0]:
            data = {'count_page_number_manga': count_page_number + 1}
        elif menu_selected == LIST_MENU_HANS_ENT[3][0]:
            data = {'count_page_number_video': count_page_number + 1}
        elif menu_selected == LIST_MENU_HANS_ENT[4][0]:
            data = {'count_page_number_music': count_page_number + 1}
        MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
        q_mysettings_hansent.refresh_from_db()
    return True



def get_score_album(album_type, dict_score_history):
    """
    # Picture Album의 favorite 점수 == Rating 1로 설정. Shot하면 Rating + 1
    # Manga Album의 favorite_sum 점수 == 앨범 안에 들어있는 Volume들이 받은 Favoite == True 개수의 합
    # Video Album의 favorite_sum 점수 == 앨범 안에 들어있는 Volume들이 받은 Favoite == True 개수의 합
    # Music Album의 favorite_sum 점수 == 앨범 안에 들어있는 Volume들이 받은 Favoite == True 개수의 합

    """
    if album_type == 'actor':
        try:
            score = (dict_score_history['rating'] * dict_score_history['total_visit_album'] * 0.1) * dict_score_history['user_multiple']
        except:
            score = 0
    elif album_type == 'picture':
        try:
            score = (dict_score_history['rating'] * dict_score_history['total_visit_album'] * 0.1) * dict_score_history['user_multiple']
        except:
            score = 0
    elif album_type == 'manga':
        try:
            score = (dict_score_history['favorite_sum'] * 1 + dict_score_history['total_visit_album'] * 0.1) * dict_score_history['rating'] * dict_score_history['user_multiple']
        except:
            score = 0
    elif album_type == 'video':
        try:
            score = (dict_score_history['favorite_sum'] + dict_score_history['total_visit_album']) * dict_score_history['user_multiple']
        except:
            score = 0
    elif album_type == 'music':
        try:
            score = (dict_score_history['favorite_sum'] + dict_score_history['total_visit_album']) * dict_score_history['user_multiple']
        except:
            score = 0
    else:
        score = 0
    score = round(score, 3)
    return score






# 두 배우 합치기
def merge_two_actor_into_one(q_actor, q_actor_s):
    hashcode = q_actor.hashcode
    hashcode_s = q_actor_s.hashcode
    synonyms = q_actor.synonyms
    date_birth = q_actor.date_birth 
    list_dict_info_url = q_actor.list_dict_info_url
    height = q_actor.height
    list_dict_profile_album = q_actor.list_dict_profile_album

    if synonyms is None:
        synonyms = []
    if list_dict_info_url is None:
        list_dict_info_url = []
    if list_dict_profile_album is None:
        list_dict_profile_album = []

    # 배우이름 합치기
    name_s = q_actor_s.name
    if name_s is not None:
        if name_s not in synonyms:
            synonyms.append(name_s)
    # 다른이름 합치기
    synonyms_s = q_actor_s.synonyms
    if synonyms_s is not None:
        for item in synonyms_s:
            if item not in synonyms:
                synonyms.append(item)
    # 생일 합치기
    if date_birth is None:
        date_birth_s = q_actor_s.date_birth
        if date_birth_s is not None:
            data_birth = date_birth_s
    # 배우정보사이트리스트 합치기
    list_dict_info_url_s = q_actor_s.list_dict_info_url
    if list_dict_info_url_s is not None:
        for item in list_dict_info_url_s:
            if item not in list_dict_info_url:
                list_dict_info_url.append(item)
    # 키 정보 합치기
    if height is None:
        height_s = q_actor_s.height
        if height_s is not None:
            height = height_s
    # 이미지 합치기 
    if list_dict_profile_album is not None:
        list_dict_profile_album_s = q_actor_s.list_dict_profile_album
        if list_dict_profile_album_s is not None:
            # 합쳐서 사라지는 쪽의 image hashcode를 남는쪽의 hashcode로 파일이름까지 변경해야 함.
            for dict_profile_album_s in list_dict_profile_album_s:
                # Find Path
                thumbnail_name_s = dict_profile_album_s["thumbnail"]
                thumbnail_name = thumbnail_name_s.replace(hashcode_s, hashcode)
                cover_name_s = dict_profile_album_s["cover"]
                cover_name = cover_name_s.replace(hashcode_s, hashcode)
                original_name_s = dict_profile_album_s["original"]
                original_name = original_name_s.replace(hashcode_s, hashcode)
                # Change File Path Name
                thumbnail_old_file = Path(f'{BASE_DIR_ACTOR}/{thumbnail_name_s}')
                thumbnail_new_file = Path(f'{BASE_DIR_ACTOR}/{thumbnail_name}')
                try:
                    os.rename(thumbnail_old_file, thumbnail_new_file)
                except FileNotFoundError:
                    print(f"Error: {thumbnail_old_file} not found.")
                cover_old_file = Path(f'{BASE_DIR_ACTOR}/{cover_name_s}')
                cover_new_file = Path(f'{BASE_DIR_ACTOR}/{cover_name}')
                try:
                    os.rename(cover_old_file, cover_new_file)
                except FileNotFoundError:
                    print(f"Error: {cover_old_file} not found.")
                original_old_file = Path(f'{BASE_DIR_ACTOR}/{original_name_s}')
                original_new_file = Path(f'{BASE_DIR_ACTOR}/{original_name}')
                try:
                    os.rename(original_old_file, original_new_file)
                except FileNotFoundError:
                    print(f"Error: {original_old_file} not found.")
                # List 업데이트
                list_dict_profile_album.appned({"thumbnail":thumbnail_name, "cover":cover_name, "original":original_name})
    # List turn None if no item in it.
    if len(synonyms) == 0:
        synonyms = None
    if len(list_dict_info_url) == 0:
        list_dict_info_url = None
    if len(list_dict_profile_album) == 0:
        list_dict_profile_album = None
    # Update Data
    data = {
        'synonyms': synonyms,
        'date_birth': date_birth,
        'height': height,
        'list_dict_info_url': list_dict_info_url,
        'list_dict_profile_album': list_dict_profile_album,
    }
    Actor.objects.filter(id=q_actor.id).update(**data)
    q_actor.refresh_from_db()
    return q_actor
    
























