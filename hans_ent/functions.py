import os
import platform

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

import pickle
import random
import time
import shutil


import pathlib
from pathlib import Path
import requests

from django.conf import settings
from django.db.models import Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from hans_ent.models import *
from webui.functions import * 
from hans_ent.tasks import *
from webui.serializers import *

# text handling
import re
import spacy              

from PIL import Image, ImageDraw, ImageFont






#############################################################################################################################################
# Mysettings 리셋하기
#############################################################################################################################################

# Mysettings Reset하기
def reset_hans_ent_actor_list(q_mysettings_hansent):
    data = {
        'actor_selected': None,
        # 'actor_pic_selected': None,
        'selected_category_actor': LIST_ACTOR_CATEGORY[0],
        'selected_field_actor': LIST_ACTOR_SORTING_FIELD[0],
        'selected_category_actor': LIST_ACTOR_CATEGORY[0][0],
        'check_field_ascending_actor': True,
        'count_page_number_actor': 1,
        'list_searched_actor_id': None,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    return True

def reset_hans_ent_picture_album_list(q_mysettings_hansent):
    data = {
        'picture_album_selected': None,
        'selected_category_picture': LIST_PICTURE_CATEGORY[0],
        'selected_field_picture': LIST_PICTURE_SORTING_FIELD[0],
        'selected_category_picture': LIST_PICTURE_CATEGORY[0][0],
        'check_field_ascending_picture': True,
        'count_page_number_picture': 1,
        'list_searched_picture_album_id': None,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    return True

def reset_hans_ent_manga_album_list(q_mysettings_hansent):
    data = {
        'manga_album_selected': None,
        'selected_category_manga': LIST_MANGA_CATEGORY[0],
        'selected_field_manga': LIST_MANGA_SORTING_FIELD[0],
        'selected_category_manga': LIST_MANGA_CATEGORY[0][0],
        'check_field_ascending_manga': True,
        'count_page_number_manga': 1,
        'list_searched_manga_album_id': None,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    return True

def reset_hans_ent_video_album_list(q_mysettings_hansent):
    data = {
        'video_album_selected': None,
        'selected_category_video': LIST_VIDEO_CATEGORY[0],
        'selected_field_video': LIST_VIDEO_SORTING_FIELD[0],
        'selected_category_video': LIST_VIDEO_CATEGORY[0][0],
        'check_field_ascending_video': True,
        'count_page_number_video': 1,
        'list_searched_video_album_id': None,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    return True

def reset_hans_ent_music_album_list(q_mysettings_hansent):
    data = {
        'music_album_selected': None,
        'selected_category_music': LIST_MUSIC_CATEGORY[0],
        'selected_field_music': LIST_MUSIC_SORTING_FIELD[0],
        'selected_category_music': LIST_MUSIC_CATEGORY[0][0],
        'check_field_ascending_music': True,
        'count_page_number_music': 1,
        'list_searched_music_album_id': None,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    return True



#############################################################################################################################################
# 쿼리 생성
##   !!!  Achtung   !!!   Default Setting (e.g. List Dict / Dict / List )을 Model에서 Import 안되는 경우가 있음. 그러면 파일 업로드시 Default 정보
#                       없이 장고기 Cache에 정보를 저장하고 계속 추가해서 정보를 주기 때문에 업로드시 리스트가 예전 정보를 계속 가져가서 중복 업로드가 됨.
#############################################################################################################################################


# Default 배우 쿼리 생성
def create_actor():
    hashcode = hashcode_generator()
        
    LIST_ACTOR_CATEGORY = (
        ('00', 'ALL'),
        ('01', 'ENTERTAINER'),
        ('02', 'SINGER'),
        ('04', 'ACTOR'),
        ('05', 'ACTOR_ADULT'),
        ('06', 'AMATUER'),
        ('07', 'AMATUER_ADULT'),
        ('08', 'MODEL'),
        ('09', 'MODEL_ADULT'), # 화보 모델, 맥심 모델
        ('10', 'SNS'),  # 관종
        ('11', 'BJ'), 
        ('12', 'PRIVITE'), # 개인소장 
        ('13', 'AI'), # 개인소장 

        ('15', 'DIRECTOR'),
        ('16', 'WRITER'),
        ('17', 'LECTURER'),
        ('19', 'ETC'),
    )

    DEFAULT_DICT_ACTOR_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
    DEFAULT_LIST_DICT_PROFILE_ALBUM = [{'id':0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "active":"true", "discard":"false", "source": "none"}]  # Source는 이미지 Original 파일을 사용
    DEFAULT_DICT_SCORE_HISTORY_ACTOR = {"favorite": "false", "rating": 0, "favorite_sum": 0, "total_visit_album": 0, "user_multiple": 1 }

    data = {
        'hashcode': hashcode,
        'dict_actor_album_cover':DEFAULT_DICT_ACTOR_ALBUM_COVER,
        'list_dict_profile_album':DEFAULT_LIST_DICT_PROFILE_ALBUM,
        'dict_score_history': DEFAULT_DICT_SCORE_HISTORY_ACTOR, 
    }
    q_actor = Actor.objects.create(**data)
    print('Actor 신규 생성!', q_actor)
    return q_actor

# Default Picture Album 쿼리 생성
def create_picture_album():
    hashcode = hashcode_generator()
        
    LIST_PICTURE_CATEGORY = (
        ('00', 'ALL'),
        ('01', '일상사진'),
        ('02', '일반화보'),
        ('03', '성인화보'),
        ('04', '일반기타'),
        ('05', '성인기타'),
    )
    
    DEFAULT_DICT_PICTURE_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
    DEFAULT_LIST_DICT_PICTURE_ALBUM = [{'id':0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "file_size":"unknown", "image_size":[],"active":"true", "discard":"false"}]
    DEFAULT_DICT_SCORE_HISTORY_PICTURE = {"favorite": "false", "rating": 0, "total_visit_album": 0, "user_multiple": 1 }

    data = {
        'hashcode': hashcode,
        'dict_picture_album_cover':DEFAULT_DICT_PICTURE_ALBUM_COVER,
        'list_dict_picture_album':DEFAULT_LIST_DICT_PICTURE_ALBUM,
        'dict_score_history': DEFAULT_DICT_SCORE_HISTORY_PICTURE, 
    }
    q_picture_album = Picture_Album.objects.create(**data)
    print('Picture Album 신규 생성!', q_picture_album)
    return q_picture_album


# Default Manga Album 쿼리 생성
def create_manga_album():
    hashcode = hashcode_generator()
        
    LIST_MANGA_CATEGORY = (
        ('00', 'ALL'),
        ('01', '국내성인'),
        ('02', '국내일반'),
        ('03', '해외성인'),
        ('04', '해외일반'),
        ('05', 'ETC'),
    )
    
    DEFAULT_DICT_MANGA_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
    DEFAULT_LIST_DICT_MANGA_ALBUM = [{'id':0, 'volume': 0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "active":"true", "discard":"false"}]
    DEFAULT_LIST_DICT_VOLUME_MANGA_INFO = [{"volume": 0, "title": "None", "date_released": "unknown", "list_id": [], "last": "true", "favorite":"false", "discard": "false"}]
    DEFAULT_DICT_SCORE_HISTORY_MANGA = {"favorite_sum": 0, "total_visit_album": 0, "user_multiple": 1 }

    data = {
        'hashcode': hashcode,
        'dict_manga_album_cover':DEFAULT_DICT_MANGA_ALBUM_COVER,
        'list_dict_manga_album':DEFAULT_LIST_DICT_MANGA_ALBUM,
        'list_dict_volume_manga': DEFAULT_LIST_DICT_VOLUME_MANGA_INFO,
        'dict_score_history': DEFAULT_DICT_SCORE_HISTORY_MANGA, 
    }
    q_manga_album = Manga_Album.objects.create(**data)
    print('Manga Album 신규 생성!', q_manga_album)
    return q_manga_album


# Default Video Album 쿼리 생성
def create_video_album():
    hashcode = hashcode_generator()

        
    LIST_VIDEO_CATEGORY = (
        ('00', 'ALL'),
        ('01', 'ENTERTAINMENT'),
        ('02', 'STUDY'),
        ('03', 'MOVIE'),
        ('04', 'DRAMA'),
        ('04', 'MUSIC'),
        ('05', 'DOCUMENTARY'),
        ('06', 'ADULT'),
        ('07', 'VR'),
        ('08', 'ETC'),
    ) 
    DEFAULT_DICT_VIDEO_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
    DEFAULT_LIST_DICT_PICTURE_ALBUM = [{'id':0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "file_size":"unknown", "image_size":[],"active":"true", "discard":"false", "streaming":"false"}]
    DEFAULT_LIST_DICT_VIDEO_ALBUM = [{"id":0, "video":"default.mp4", "original":"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "still":[{"time":1, "path":"default-s.png"}], "active":"true", "discard":"false", "streaming":"false"}]
    DEFAULT_DICT_SCORE_HISTORY_VIDEO = {"favorite_sum": 0, "total_visit_album": 0, "user_multiple": 1 }

    data = {
        'hashcode': hashcode,
        'dict_video_album_cover':DEFAULT_DICT_VIDEO_ALBUM_COVER,
        'list_dict_picture_album':DEFAULT_LIST_DICT_PICTURE_ALBUM,
        'list_dict_video_album': DEFAULT_LIST_DICT_VIDEO_ALBUM,
        'dict_score_history': DEFAULT_DICT_SCORE_HISTORY_VIDEO,
        'category': LIST_VIDEO_CATEGORY[6][0],
    }
    q_video_album = Video_Album.objects.create(**data)
    print(f'q_video_album 쿼리 생성: {q_video_album.id}, list_dict_video_album: {q_video_album.list_dict_video_album}')
    return q_video_album

# Default Music Album 쿼리 생성
def create_music_album():
    hashcode = hashcode_generator()

        
    LIST_MUSIC_CATEGORY = (
        ('00', 'ALL'),
        ('01', 'KPOP'),
        ('02', 'POP'),
        ('03', 'CLASSIC'),
        ('04', 'JAZZ'),
        ('05', 'ETC'),
    )
    
    DEFAULT_DICT_MUSIC_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
    DEFAULT_LIST_DICT_MUSIC_ALBUM = [{'id':0, "source":"default.mp3", "original":"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "active":"true", "discard":"false", "discard":"false"}]
    LIST_AUDIO_FILE_EXTENSIONS = ['mp3', 'mpeg', 'opus', 'ogg', 'oga', 'wav', 'aac', 'caf', 'm4a', 'mp4', 'weba', 'webm', 'dolby', 'flac']
    DEFAULT_DICT_SCORE_HISTORY_MUSIC = {"favorite_sum": 0, "total_visit_album": 0, "user_multiple": 1 }

    data = {
        'hashcode': hashcode,
        'dict_music_album_cover':DEFAULT_DICT_MUSIC_ALBUM_COVER,
        'list_dict_picture_album':DEFAULT_LIST_DICT_PICTURE_ALBUM,
        'list_dict_music_album': DEFAULT_LIST_DICT_MUSIC_ALBUM,
        'dict_score_history': DEFAULT_DICT_SCORE_HISTORY_MUSIC, 
    }
    q_music_album = Music_Album.objects.create(**data)
    print('Music Album 신규 생성!', q_music_album)
    return q_music_album





#############################################################################################################################################
# 앱 등록하기
#############################################################################################################################################


# 앨범 Tag 등록하기                    
def register_tags_to_album(q_xxx_album_selected, type_album, list_collected_tags):
    try:
        print('# file 이름에서 추출한 내용으로 tags에 저장')
        tags = q_xxx_album_selected.tags
        if tags is None:
            tags = []
        if list_collected_tags is not None and len(list_collected_tags) > 0:
            for item in list_collected_tags:
                if item not in tags:
                    print('item', item)
                    check_tag_available = True
                    # Tag으로 넣을 조건 Filtering
                    # 숫자들 제외
                    try:
                        item = int(item)
                        check_tag_available = False
                    except:
                        item = item
                    try:
                        if len(item) < 3: # 단어 하나당 길이가 2 이하인 것은 제외
                            check_tag_available = False
                    except:
                        pass

                    if check_tag_available == True:
                        tags.append(item)
            data = {
                'tags': tags,
            }
            if type_album == 'actor':
                Actor.objects.filter(id=q_xxx_album_selected.id).update(**data)
            elif type_album == 'picture':
                Picture_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            elif type_album == 'manga':
                Manga_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            elif type_album == 'video':
                Video_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            elif type_album == 'music':
                Music_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        return True
    except:
        print('tag 수집 실패')
        return False
    

# 앨범 Title 등록하기
def register_title_to_album(q_xxx_album_selected, type_album, title_item):  
    try:
        # title 저장
        if type_album == 'actor':
            # data = {
            #     'name': title_item
            # }        
            pass
        else:
            data = {
                'title': title_item
            }
        if type_album == 'actor':
            Actor.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'picture':
            Picture_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'manga':
            Manga_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'video':
            Video_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'music':
            Music_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
        return True
    except:
        print('이름 저장 실패')
        pass 
        return False



# 앨범 Synonyms 등록하기
def register_synonyms_to_album(q_xxx_album_selected, type_album, synonyms):  
    try:
        data = {
            'synonyms': synonyms
        }
        if type_album == 'actor':
            Actor.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'picture':
            Picture_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'manga':
            Manga_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'video':
            Video_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'music':
            Music_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
        return True
    except:
        print('synonyms 저장 실패')
        pass 
        return False



#############################################################################################################################################
# Hashcode 찾기
#############################################################################################################################################

def get_hashcode_from_selected_album(q_xxx_album_selected, type_album):
    try:
        hashcode = q_xxx_album_selected.hashcode
    except:
        hashcode = None
    if hashcode is None:
        print('No Hashcode!!')
        hashcode = hashcode_generator()
        data = {'hashcode': hashcode}

        if type_album == 'actor':
            Actor.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'picture':
            Picture_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'manga':
            Manga_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'video':
            Video_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'music':
            Music_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
    return hashcode 

#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Actor
#
#############################################################################################################################################
#############################################################################################################################################



def calculate_age(birth_date):
    # birth_date should be a datetime.date or datetime.datetime
    # For example: birth_date = datetime.date(1990, 5, 23)
    today = datetime.date.today()
    # Start with a base age difference
    age = today.year - birth_date.year
    # If today's month/day is before the birth month/day, subtract 1
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Picture
#
#############################################################################################################################################
#############################################################################################################################################

def title_string_convert_to_title_elements(title):
    list_title_element_remove_check = ['', ' ', 'and']
    list_title_element_contain_check = ['mb', 'photo', 'photos']
    title = title.lower()
    title = title.replace('[', ' ')
    title = title.replace(']', ' ')
    title = title.replace('(', ' ')
    title = title.replace(')', ' ')
    title = title.replace('+', ' ')
    title = title.replace('-', ' ')
    title = title.replace('_', ' ')
    title = title.replace('「', ' ')
    title = title.replace('」', ' ')
    title = title.replace('【', ' ')
    title = title.replace('】', ' ')
    title = title.replace('photos', ' ')
    list_title_element = title.split(' ')
    list_title_element_new = []
    for item in list_title_element:
        check_good = True
        item = item.strip()
        if len(item) <= 1:
            check_good = False
        if item.isdigit():
            check_good = False
        for check_item in list_title_element_remove_check:
            if item == check_item:
                check_good = False
        for check_item in list_title_element_contain_check:
            if check_item in item:
                check_good = False
        if check_good == True:
            list_title_element_new.append(item)
    return list_title_element_new


def find_keywords_based_on_picture_album_title(q_picture_album):
    list_title_element_all = []
    title = q_picture_album.title
    if title is not None:
        list_title_element_all = title_string_convert_to_title_elements(title)
    return list_title_element_all


def find_keywords_based_on_video_album_title(q_video_album):
    list_title_element_all = []
    title = q_video_album.title
    if title is not None:
        list_title_element_all = title_string_convert_to_title_elements(title)
    return list_title_element_all


def find_keywords_based_on_music_album_title(q_music_album):
    list_title_element_all = []
    title = q_music_album.title
    if title is not None:
        list_title_element_all = title_string_convert_to_title_elements(title)
    return list_title_element_all






# 비디오 앨범으로부터 Actor 프로필에 사용할 이미지 확보하기
def collect_images_from_registered_video_album_for_actor_profile_cover_image(q_actor):
    print('# 선택된 Video Album에 대표 이미지를 Actor Profile 사진으로 등록해주기')
    list_images_for_actor_profile = []
    qs_video_album_actor = Video_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_actor))
    if qs_video_album_actor is not None and len(qs_video_album_actor) > 0:
        for q_video_album_actor in qs_video_album_actor:
            # Actor로 옮겨갈 이미지 리스트 비디오 Picture Album에서 확보
            list_dict_picture_album = q_video_album_actor.list_dict_picture_album
            if list_dict_picture_album is not None and len(list_dict_picture_album) > 1:
                # print('# 하나 이상 비디오가 등록되었으면 해당 비디오 앨범에 등록된 Picture Image를 Actor의 Profile 이미지로 활용')
                for dict_picture_album in list_dict_picture_album:
                    if dict_picture_album["discard"] == 'false':
                        try:
                            picture_album_second_path = dict_picture_album['original']
                        except:
                            picture_album_second_path = None
                        if picture_album_second_path is not None:
                            list_images_for_actor_profile.append(picture_album_second_path)
    print('list_images_for_actor_profile', list_images_for_actor_profile)
    print('# 추출한 이미지 리스트를 q_actor의 프로필 앨범에 등록 및 저장')
    if q_actor is not None:
        hashcode = q_actor.hashcode
        list_dict_profile_album = q_actor.list_dict_profile_album
        
        # list_dict_profile_album 초기화
        if list_dict_profile_album is None:
            list_dict_profile_album = DEFAULT_LIST_DICT_PROFILE_ALBUM
        for dict_profile_album in list_dict_profile_album:
            if "source" not in dict_profile_album:
                dict_profile_album["source"] = "none"
            dict_profile_album['active'] = 'false' 
            if dict_profile_album['id'] == 0 :
                dict_profile_album['discard'] = 'true' 
        num_tot_original_images = len(list_dict_profile_album)

        # 복사해갈 이미지가 1개 이상 있으면:
        if len(list_images_for_actor_profile) > 0:
            for images_for_actor_profile in list_images_for_actor_profile:
                # 옮겨갈 파일이 실제 DB에 있는지 체크
                file_path_images_for_actor_profile = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, images_for_actor_profile)
                if os.path.exists(file_path_images_for_actor_profile):

                    # Actor의 Profile에 등록되어 있는지 중복체크
                    check_duplicated = False
                    for dict_profile_album in list_dict_profile_album:
                        if dict_profile_album["source"]== images_for_actor_profile :
                            check_duplicated = True
                            break 
                                
                    if check_duplicated == False:
                        # 중복이 없으면 새 이름 지정하기
                        file_extension = images_for_actor_profile.split('.')[-1]
                        image_name_original = f'{hashcode}-o-{num_tot_original_images}.{file_extension}'
                        image_name_cover = f'{hashcode}-c-{num_tot_original_images}.{file_extension}'
                        image_name_thumbnail = f'{hashcode}-t-{num_tot_original_images}.{file_extension}'
                        file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_original)
                        file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_cover)
                        file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_thumbnail)
                        # 파일 저장하기기
                        try:
                            image_pil = Image.open(file_path_images_for_actor_profile)
                            print('# 오리지널 이미지로부터 오리지널 이미지로 저장')
                            if os.path.exists(image_name_original):
                                print("오리지널 이미지 파일 이미 존재")
                                pass 
                            else:
                                try:
                                    print("오리지널 이미지 파일 저장하기")
                                    image_pil.save(file_path_original)
                                    print('# 리스트에 신규생성 이미지 등록하기')
                                    list_dict_profile_album.append({'id': num_tot_original_images, "original": image_name_original, "cover": image_name_cover, "thumbnail": image_name_thumbnail, "active": "false", "discard":"false", "source": images_for_actor_profile})
                                except:
                                    print('original_pil is None!')
                                    pass
                            # 오리지널 이미지로부터 커버 이미지 변환 및 저장
                            if os.path.exists(image_name_cover):
                                pass 
                            else:
                                cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
                                try:
                                    print("커버 이미지 파일 저장하기")
                                    cover_pil.save(file_path_cover)
                                except:
                                    print('cover_pil is None!')
                                    pass
                            # 오리지널 이미지로부터 썸네일 이미지 변환 및 저장
                            if os.path.exists(image_name_thumbnail):
                                pass 
                            else:
                                thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
                                try:
                                    print("썸네일 이미지 파일 저장하기")
                                    thumbnail_pil.save(file_path_thumbnail) 
                                except:
                                    print('thumbnail_pil is None!')
                                    pass
                        except:
                            print('error!')
                            pass
                    else:
                        print('중복 등록 방지 Skipped!')
                        pass
                else:
                    print('collected images from picture album does not exist!!')
                    pass
                num_tot_original_images = num_tot_original_images + 1
            
            print('완료') 
        else:
            print('등록할 신규 이미지가 없습니다.')     
            pass
    
        # 최종 상태 업데이트
        check_activated = False
        # 기등록된 item의 Activated된 이미지가 하나 이상 있는지 확인.
        for item in list_dict_profile_album:
            print(item['active'])
            if item['active'] == "true":
                check_activated = True
                break 
        
        if check_activated == False:
            if list_dict_profile_album[-1]["discard"] == "false":
                # print('# 기등록된 이미지가 하나도 Activated되지 않았다면, 마지막 이미지 discard 안되었다면 마지막 이미지를 Activation 시킨다.')
                list_dict_profile_album[0]["active"] = "false"
                list_dict_profile_album[0]["discard"] = "false"
                list_dict_profile_album[-1]["active"] = "true"
            else:
                # print('# 기등록된 이미지가 하나도 Activated되지 않았다면 default 이미지를 Activation 시킨다.')
                list_dict_profile_album[0]["active"] = "true"
                list_dict_profile_album[0]["discard"] = "false"
        else:
            # print('# 기등록된 이미지가 하나 이상 Activated 되었다면(Default 포함) 마자막 이미지를 Activation 시킨다.')
            list_dict_profile_album[0]["active"] = "false"
            list_dict_profile_album[0]["discard"] = "false"
            list_dict_profile_album[-1]["active"] = "true"

        data = {
            'list_dict_profile_album': list_dict_profile_album,
        }
        Actor.objects.filter(id=q_actor.id).update(**data)
        q_actor.refresh_from_db()
        print('마지막 이미지 Activation 완료')
    else:
        print('등록된 Actor가 없습니다.')
        pass 
    return True


# 사진 앨범으로부터 Actor 프로필에 사용할 이미지 확보하기
def collect_images_from_registered_picture_album_for_actor_profile_cover_image(q_actor):
    print('# 선택한 Picture Album에 대표 이미지를 Actor Profile 사진으로 등록해주기')
    print('# q_actor가 포함된 Album에서 가져올 이미지 추출출')
    list_images_for_actor_profile = []
    qs_picture_album_actor = Picture_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_actor))
    if qs_picture_album_actor is not None and len(qs_picture_album_actor) > 0:
        for q_picture_album_actor in qs_picture_album_actor:
            try:
                picture_album_second_path = q_picture_album_actor.list_dict_picture_album[1]['original']
            except:
                picture_album_second_path = None
            if picture_album_second_path is not None:
                list_images_for_actor_profile.append(picture_album_second_path)
    print('list_images_for_actor_profile', list_images_for_actor_profile)
    print('# 추출한 이미지 리스트를 q_actor의 프로필 앨범에 등록 및 저장')
    list_dict_profile_album = q_actor.list_dict_profile_album
    if list_dict_profile_album is None:
        list_dict_profile_album = DEFAULT_LIST_DICT_PROFILE_ALBUM 
    
    for dict_profile_album in list_dict_profile_album:
        if "source" not in dict_profile_album:
            dict_profile_album["source"] = "none"
        dict_profile_album["active"] = "false"
        if dict_profile_album['id'] == 0:
            dict_profile_album["discard"] = "true"
    num_tot_original_images = len(list_dict_profile_album)
    hashcode = q_actor.hashcode

    for images_for_actor_profile in list_images_for_actor_profile:
        # 옮겨갈 파일이 실제 DB에 있는지 체크
        file_path_images_for_actor_profile = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, images_for_actor_profile)
        if os.path.exists(file_path_images_for_actor_profile):
            
            # Actor의 Profile에 등록되어 있는지 중복체크
            check_duplicated = False
            for dict_profile_album in list_dict_profile_album:
                if dict_profile_album["source"] == images_for_actor_profile:
                    check_duplicated = True
                    break
            
            if check_duplicated == False:
                # 중복이 없으면 새 이름 지정하기
                file_extension = images_for_actor_profile.split('.')[-1]
                image_name_original = f'{hashcode}-o-{num_tot_original_images}.{file_extension}'
                image_name_cover = f'{hashcode}-c-{num_tot_original_images}.{file_extension}'
                image_name_thumbnail = f'{hashcode}-t-{num_tot_original_images}.{file_extension}'
                file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_original)
                file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_cover)
                file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_thumbnail)
                # 파일 저장하기기
                try:
                    image_pil = Image.open(file_path_images_for_actor_profile)
                    print('# 오리지널 이미지로부터 오리지널 이미지로 저장')
                    if os.path.exists(image_name_original):
                        print("오리지널 이미지 파일 이미 존재")
                        pass 
                    else:
                        try:
                            print("오리지널 이미지 파일 저장하기")
                            image_pil.save(file_path_original)
                            print('# 리스트에 신규생성 이미지 등록하기')
                            list_dict_profile_album.append({'id': num_tot_original_images, "original": image_name_original, "cover": image_name_cover, "thumbnail": image_name_thumbnail, "active": "false", "discard":"false", "source": images_for_actor_profile})
                        except:
                            print('original_pil is None!')
                            pass
                    # 오리지널 이미지로부터 커버 이미지 변환 및 저장
                    if os.path.exists(image_name_cover):
                        pass 
                    else:
                        cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
                        try:
                            print("커버 이미지 파일 저장하기")
                            cover_pil.save(file_path_cover)
                        except:
                            print('cover_pil is None!')
                            pass
                    # 오리지널 이미지로부터 썸네일 이미지 변환 및 저장
                    if os.path.exists(image_name_thumbnail):
                        pass 
                    else:
                        thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
                        try:
                            print("썸네일 이미지 파일 저장하기")
                            thumbnail_pil.save(file_path_thumbnail) 
                        except:
                            print('thumbnail_pil is None!')
                            pass
                except:
                    print('error!')
                    pass
            else:
                print('중복 등록 방지 Skipped!')
                pass
        else:
            print('collected images from picture album does not exist!!')
            pass
        num_tot_original_images = num_tot_original_images + 1
    
    # 최종 상태 업데이트
    check_activated = False
    for item in list_dict_profile_album:
        if item['active'] == "true":
            check_activated = True
            break 
    
    if check_activated == False:
        list_dict_profile_album[0]["active"] = "true"
        list_dict_profile_album[0]["discard"] = "false"
    else:
        list_dict_profile_album[0]["active"] = "false"
        list_dict_profile_album[0]["discard"] = "true"
        list_dict_profile_album[-1]["active"] = "true"

    data = {
        'list_dict_profile_album': list_dict_profile_album,
    }
    Actor.objects.filter(id=q_actor.id).update(**data)
    q_actor.refresh_from_db()
    print('완료')
    return True


# 선택한 이미지를 Actor 프로필로 복제하기
def copy_images_to_actor_profile(file_path_images_for_actor_profile, hashcode, num_tot_original_images, file_extension, list_dict_profile_album, images_for_actor_profile):
    # 중복이 없으면 새 이름 지정하기
    image_name_original = f'{hashcode}-o-{num_tot_original_images}.{file_extension}'
    image_name_cover = f'{hashcode}-c-{num_tot_original_images}.{file_extension}'
    image_name_thumbnail = f'{hashcode}-t-{num_tot_original_images}.{file_extension}'
    file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_original)
    file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_cover)
    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_thumbnail)
    # 파일 저장하기기
    try:
        image_pil = Image.open(file_path_images_for_actor_profile)
        # print('# 오리지널 이미지로부터 오리지널 이미지로 저장')
        if os.path.exists(image_name_original):
            # print("오리지널 이미지 파일 이미 존재")
            pass 
        else:
            try:
                # print("오리지널 이미지 파일 저장하기")
                image_pil.save(file_path_original)
                # print('# 리스트에 신규생성 이미지 등록하기')
                list_dict_profile_album.append({'id': num_tot_original_images, "original": image_name_original, "cover": image_name_cover, "thumbnail": image_name_thumbnail, "active": "false", "discard":"false", "source": images_for_actor_profile})
            except:
                # print('original_pil is None!')
                pass
        # 오리지널 이미지로부터 커버 이미지 변환 및 저장
        if os.path.exists(image_name_cover):
            pass 
        else:
            cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
            try:
                # print("커버 이미지 파일 저장하기")
                cover_pil.save(file_path_cover)
            except:
                # print('cover_pil is None!')
                pass
        # 오리지널 이미지로부터 썸네일 이미지 변환 및 저장
        if os.path.exists(image_name_thumbnail):
            pass 
        else:
            thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
            try:
                # print("썸네일 이미지 파일 저장하기")
                thumbnail_pil.save(file_path_thumbnail) 
            except:
                # print('thumbnail_pil is None!')
                pass
    except:
        print('error!')
        pass
    

# Actor가 등록된 사진앨범과 비디오앨범을 찾아서 Actor 프로필에 쓸만한 이미지 확보하기
def collect_images_from_registered_all_album_for_actor_profile_cover_image(q_actor):
    print('# 선택된 모든 Album에 대표 이미지를 Actor Profile 사진으로 등록해주기')
    dict_images_for_actor_profile = {"picture":[], "video":[]}
    # 사진 앨범에서 획득하기기
    qs_picture_album_actor = Picture_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_actor))
    if qs_picture_album_actor is not None and len(qs_picture_album_actor) > 0:
        for q_picture_album_actor in qs_picture_album_actor:
            try:
                picture_album_second_path = q_picture_album_actor.list_dict_picture_album[1]['original']
            except:
                picture_album_second_path = None
            if picture_album_second_path is not None:
                dict_images_for_actor_profile['picture'].append(picture_album_second_path)
    # 비디오 앨범에서 획득하기
    qs_video_album_actor = Video_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_actor))
    if qs_video_album_actor is not None and len(qs_video_album_actor) > 0:
        for q_video_album_actor in qs_video_album_actor:
            # Actor로 옮겨갈 이미지 리스트 비디오 Picture Album에서 확보
            list_dict_picture_album = q_video_album_actor.list_dict_picture_album
            if list_dict_picture_album is not None and len(list_dict_picture_album) > 1:
                # print('# 하나 이상 비디오가 등록되었으면 해당 비디오 앨범에 등록된 Picture Image를 Actor의 Profile 이미지로 활용')
                for dict_picture_album in list_dict_picture_album:
                    if dict_picture_album["discard"] == 'false':
                        try:
                            picture_album_second_path = dict_picture_album['original']
                        except:
                            picture_album_second_path = None
                        if picture_album_second_path is not None:
                            dict_images_for_actor_profile['video'].append(picture_album_second_path)
    
    # print('dict_images_for_actor_profile', dict_images_for_actor_profile)
    # print('# 추출한 이미지 리스트를 q_actor의 프로필 앨범에 등록 및 저장')
    if q_actor is not None:
        hashcode = q_actor.hashcode
        list_dict_profile_album = q_actor.list_dict_profile_album
        
        # list_dict_profile_album 초기화
        if list_dict_profile_album is None:
            list_dict_profile_album = DEFAULT_LIST_DICT_PROFILE_ALBUM
        for dict_profile_album in list_dict_profile_album:
            if "source" not in dict_profile_album:
                dict_profile_album["source"] = "none"
            dict_profile_album['active'] = 'false' 
            if dict_profile_album['id'] == 0 :
                dict_profile_album['discard'] = 'true' 
        num_tot_original_images = len(list_dict_profile_album)

        
        list_images_from_picture_album = dict_images_for_actor_profile["picture"]
        list_images_from_video_album = dict_images_for_actor_profile["video"]
        # 옮겨갈 파일이 실제 DB에 있는지 체크
        if len(list_images_from_picture_album) > 0:
            for images_for_actor_profile in list_images_from_picture_album:
                file_path_images_for_actor_profile = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, images_for_actor_profile)
                if os.path.exists(file_path_images_for_actor_profile):
                    check_duplicated = False
                    for dict_profile_album in list_dict_profile_album:
                        if dict_profile_album["source"]== images_for_actor_profile :
                            check_duplicated = True
                            break 
                    if check_duplicated == False:
                        file_extension = images_for_actor_profile.split('.')[-1]
                        copy_images_to_actor_profile(file_path_images_for_actor_profile, hashcode, num_tot_original_images, file_extension, list_dict_profile_album, images_for_actor_profile)
                        num_tot_original_images = num_tot_original_images + 1
                    else:
                        print('중복 등록 방지 Skipped!')
                        pass
                else:
                    print('원본 파일이 DB에 없음음!!')
                    pass
        else:
            print('사진 앨범에서 수집한 정보가 없음!!')
            pass
        if len(list_images_from_video_album) > 0:
            for images_for_actor_profile in list_images_from_video_album:
                file_path_images_for_actor_profile = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, images_for_actor_profile)
                if os.path.exists(file_path_images_for_actor_profile):
                    check_duplicated = False
                    for dict_profile_album in list_dict_profile_album:
                        if dict_profile_album["source"]== images_for_actor_profile :
                            check_duplicated = True
                            break 
                    if check_duplicated == False:
                        file_extension = images_for_actor_profile.split('.')[-1]
                        copy_images_to_actor_profile(file_path_images_for_actor_profile, hashcode, num_tot_original_images, file_extension, list_dict_profile_album, images_for_actor_profile)
                        num_tot_original_images = num_tot_original_images + 1
                    else:
                        print('중복 등록 방지 Skipped!')
                        pass
                else:
                    print('원본 파일이 DB에 없음음!!')
                    pass
        else:
            print('비디오 앨범에서 수집한 정보가 없음!!')
            pass
        print('완료') 
        
    
        # 최종 상태 업데이트
        check_activated = False
        # 기등록된 item의 Activated된 이미지가 하나 이상 있는지 확인.
        for item in list_dict_profile_album:
            print(item['active'])
            if item['active'] == "true":
                check_activated = True
                break 
        
        if check_activated == False:
            if list_dict_profile_album[-1]["discard"] == "false":
                # print('# 기등록된 이미지가 하나도 Activated되지 않았다면, 마지막 이미지 discard 안되었다면 마지막 이미지를 Activation 시킨다.')
                list_dict_profile_album[0]["active"] = "false"
                list_dict_profile_album[0]["discard"] = "false"
                list_dict_profile_album[-1]["active"] = "true"
            else:
                # print('# 기등록된 이미지가 하나도 Activated되지 않았다면 default 이미지를 Activation 시킨다.')
                list_dict_profile_album[0]["active"] = "true"
                list_dict_profile_album[0]["discard"] = "false"
        else:
            # print('# 기등록된 이미지가 하나 이상 Activated 되었다면(Default 포함) 마자막 이미지를 Activation 시킨다.')
            list_dict_profile_album[0]["active"] = "false"
            list_dict_profile_album[0]["discard"] = "false"
            list_dict_profile_album[-1]["active"] = "true"

        data = {
            'list_dict_profile_album': list_dict_profile_album,
        }
        Actor.objects.filter(id=q_actor.id).update(**data)
        q_actor.refresh_from_db()
        print('마지막 이미지 Activation 완료')
    else:
        print('등록된 Actor가 없습니다.')
        pass 
    return True




def get_youtube_video_info(video_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(video_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("meta", property="og:title")
    description = soup.find("meta", property="og:description")
    thumbnail = soup.find("meta", property="og:image")
    channel = soup.find("link", itemprop="name")

    return {
        "title": title["content"] if title else None,
        "description": description["content"] if description else None,
        "thumbnail": thumbnail["content"] if thumbnail else None,
        "channel": channel["content"] if channel else None,
    }
























#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#
#                                                           File Save
#
""" 
입력값은 PIL object. 그러면 알아서 커버이미지, 썸네일이미지 두가지 모두 출력
    PIL image, 
    커버이미지 == Landscape 비율
    썸네일이미지 == Portrait 비율
            
    Width	Height	Name
    640	    360	    nHD
    854	    480	    FWVGA
    960	    540	    qHD
    1024	576	    WSVGA
    1280	720	    HD
    1366	768	    FWXGA
    1600	900	    HD+
    1920	1080	Full HD
    2560	1440	QHD
    3200	1800	QHD+
    3840	2160	4K UHD
    5120	2880	5K
    7680	4320	8K UHD
"""

"""
    image naming $ size rules
    thumbnail image: hashcode-t.xxx  // size: 260px by 320px
    cover image: hashcode-c.xxx  // size: 520px by 640px
    original image: hashcode-o.xxx  // size: 그대로
    still image: hashcode-s-<order number>.xxx  // size: 65px by 80px
"""    

#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################





#----------------------------------------------------------------------------------------------------------------------------------------
# 파일 저장 유틸리티
#----------------------------------------------------------------------------------------------------------------------------------------

# 파일 포맷별 타입 지정
def f_check_what_format_is_this_file(file_extension):
    file_extension = file_extension.lower()
    if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'tiff', 'eps']:
        return 'image'
    elif file_extension in ['mp4', 'mov', 'avi', 'wmv', 'mkv', 'webm', 'mpeg2', ]:
        return 'video'
    elif file_extension in ['mp3', 'wma', 'flac', 'wav', 'ogg', 'aac', 'pcm', 'dsd']:
        return 'audio'
    else:
        return 'unknown'



# 오디오 메타 데이터 확보
def get_audio_metadata(file_music_path):
    tag = TinyTag.get(file_music_path)
    duration_str = str(datetime.timedelta(seconds=int(tag.duration)))

    title_str = tag.title
    if title_str is None:
        title_str = "Unknown Title",
    else:
        title_str = file_name_cleaner(title_str)

    artist_str = tag.artist
    if artist_str is None:
        artist_str = "Unknown Artist",
    else:
        artist_str = file_name_cleaner(artist_str)

    album_str = tag.album
    if album_str is None:
        album_str = "Unknown Album",
    else:
        album_str = file_name_cleaner(artist_str)

    dict_metadata = {
        "title": title_str,
        "artist": artist_str,
        "album": album_str,
        "duration_sec": tag.duration,  # In seconds
        "duration_str": duration_str,
    }
    return dict_metadata


# 암호화 하기
def hashcode_generator():
    # Generate a random UUID
    random_uuid = uuid.uuid4()
    # Convert it to a string (this will give you a 32-character hexadecimal string)
    hash_code = str(random_uuid)
    print("UUID4 Hash:", hash_code)
    return hash_code

#----------------------------------------------------------------------------------------------------------------------------------------




        


# 수동으로 Video Album Still image 저장하기
def save_video_album_video_still_images(q_video_album_selected, dict_video_album):
    print('# Video Album Still image 저장하기', dict_video_album)
    # get base info
    hashcode = q_video_album_selected.hashcode
    if hashcode is None:
        hashcode = hashcode_generator()
        data = {'hashcode': hashcode}
        Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
        q_video_album_selected.refresh_from_db()
    file_video_name = dict_video_album["video"]
    file_video_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, file_video_name)
    video_id = dict_video_album["id"]

    # Function to resize and pad the frame
    def resize_and_pad(frame, target_width, target_height, pad_color):
        # Get the original dimensions
        original_height, original_width = frame.shape[:2]
        # Compute the scaling factor and new dimensions
        scale_width = target_width / original_width
        scale_height = target_height / original_height
        scale = min(scale_width, scale_height)
        # Compute the new width and height to maintain aspect ratio
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        # Resize the frame
        resized_frame = cv2.resize(frame, (new_width, new_height))
        # Compute the padding for top/bottom and left/right
        pad_left = (target_width - new_width) // 2
        pad_right = target_width - new_width - pad_left
        pad_top = (target_height - new_height) // 2
        pad_bottom = target_height - new_height - pad_top
        # Add padding
        padded_frame = cv2.copyMakeBorder(
            resized_frame,
            pad_top,
            pad_bottom,
            pad_left,
            pad_right,
            cv2.BORDER_CONSTANT,
            value=pad_color
        )
        return padded_frame

    def still_image_save(j, unit_frame, hashcode, video_id, fps):
        cap.set(cv2.CAP_PROP_POS_FRAMES, unit_frame*j)
        ret, frame = cap.read()
        # Padding color (black in this case)
        pad_color = (255, 255, 255)  # (B, G, R)
        target_width = 640
        target_height = 360
        # Resize and pad the frame
        frame = resize_and_pad(frame, target_width, target_height, pad_color)
        # Save
        if ret:
            # Save the frame as an image file
            try:
                video_still_path = f'{hashcode}-s-{video_id}-{j}.jpg'
                file_still_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_still_path)
                # save Frame
                cv2.imwrite(file_still_path, frame)
                timestamp = (j*unit_frame) // fps
                return {"time":timestamp, "path":video_still_path}
            except:
                return None
        else:
            return None
        
    # Still 이미지 확보
    list_still = []
    cap = cv2.VideoCapture(file_video_path)
    if cap.isOpened():
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        try:
            duration_seconds = total_frames / fps
            duration_seconds = round(duration_seconds, 2)
        except:
            duration_seconds = 0 
        if duration_seconds > 0:
            duration_str = str(datetime.timedelta(seconds=int(duration_seconds)))
        else:
            duration_str = 'None'

        if "duration_second" in dict_video_album:
            dict_video_album["duration_second"] = duration_seconds
        else:
            dict_video_album.update({'duration_second':duration_seconds})
        
        if "duration_str" in dict_video_album:
            dict_video_album["duration_str"] = duration_str
        else:
            dict_video_album.update({'duration_str':duration_str})
        
        if duration_seconds < 600: # 10 min under == 5 cut
            unit_frame = total_frames // 10
            print('5 unit_frame ', unit_frame)
            j = 1
            while j < 11:
                print('j', j)
                try:
                    return_value = still_image_save(j, unit_frame, hashcode, video_id, fps)
                except:
                    pass
                if return_value is not None:
                    list_still.append(return_value)
                j = j + 1
        elif duration_seconds >= 600 and duration_seconds < 3000: # 10 ~ 30 min  == 10 cut
            unit_frame = total_frames // 15
            print('10 unit_frame ', unit_frame)
            j = 1
            while j < 16:
                print('j', j)
                try:
                    return_value = still_image_save(j, unit_frame, hashcode, video_id, fps)
                except:
                    pass
                if return_value is not None:
                    list_still.append(return_value)
                j = j + 1
        elif duration_seconds >= 3000 and duration_seconds < 9000: # 30 ~ 90 min  == 15 cut
            unit_frame = total_frames // 20
            print('15 unit_frame ', unit_frame)
            j = 1
            while j < 21:
                print('j', j)
                try:
                    return_value = still_image_save(j, unit_frame, hashcode, video_id, fps)
                except:
                    pass
                if return_value is not None:
                    list_still.append(return_value)
                j = j + 1
        else: # 90 min ~ Over == 20 cut
            unit_frame = total_frames // 25
            print('20 unit_frame ', unit_frame)
            j = 1
            while j < 26:
                print('j', j)
                try:
                    return_value = still_image_save(j, unit_frame, hashcode, video_id, fps)
                except:
                    pass
                if return_value is not None:
                    list_still.append(return_value)
                j = j + 1

    # Dict_video_album 업데이트
    
    dict_video_album["thumbnail"] = list_still[0]["path"]
    dict_video_album["still"] = list_still
    
    return dict_video_album


# 앨범 대표 사진을 디폴트 이미지로 변경
def save_file_to_replace_default_image(q_xxx_album_selected, files, type_album):
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    selected_vault = q_systemsettings_hansent.selected_vault
    print('save_file_to_replace_default_image', )
    print('################################  q_xxx_album_selected, , : ', q_xxx_album_selected)
    print('################################  , files, : ', files)
    print('################################  , , type_album: ', type_album)
    # Get Hashcode
    hashcode = q_xxx_album_selected.hashcode
    if hashcode is None:
        print('No Hashcode!!')
        hashcode = hashcode_generator()
        data = {'hashcode': hashcode}
        if type_album == 'actor':
            Actor.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'picture':
            Picture_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'manga':
            Manga_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'video':
            Video_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        elif type_album == 'music':
            Music_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()

    if type_album == 'actor':
        dict_xxx_album_cover = q_xxx_album_selected.dict_actor_album_cover 
        list_dict_xxx_album = q_xxx_album_selected.list_dict_profile_album
        save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR)
    elif type_album == 'picture':
        dict_xxx_album_cover = q_xxx_album_selected.dict_picture_album_cover 
        list_dict_xxx_album = q_xxx_album_selected.list_dict_picture_album
        save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
    elif type_album == 'manga':
        dict_xxx_album_cover = q_xxx_album_selected.dict_manga_album_cover 
        list_dict_xxx_album = q_xxx_album_selected.list_dict_manga_album
        save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA)
    elif type_album == 'video':
        dict_xxx_album_cover = q_xxx_album_selected.dict_video_album_cover 
        list_dict_xxx_album = q_xxx_album_selected.list_dict_picture_album
        save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
    elif type_album == 'music':
        dict_xxx_album_cover = q_xxx_album_selected.dict_music_album_cover 
        list_dict_xxx_album = q_xxx_album_selected.list_dict_picture_album
        save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC)

    for file in files:  
        file_name = file.name
        if '.webp' in file_name:
            file_name = file_name.replace('.webp', '.jpg')
        file_extension = file_name.split('.')[-1]
        file_format = f_check_what_format_is_this_file(file_extension)  ## image / video / audio / unknown
        print('file_extension', file_extension)
        print('file_format', file_format)
        if file_format != 'unknown':
            print('# Save Images in tmp folder')
            
            if file_format == 'image':
                image_name_original = f'{hashcode}-o-{0}.{file_extension}'
                image_name_cover = f'{hashcode}-c-{0}.{file_extension}'
                image_name_thumbnail = f'{hashcode}-t-{0}.{file_extension}'
                print('image_name_original', image_name_original)
                
                for dict_xxx_album in list_dict_xxx_album:
                    if dict_xxx_album['id'] == 0:
                        print('dict_xxx_album', dict_xxx_album)
                        dict_xxx_album['original'] = image_name_original
                        dict_xxx_album['cover'] = image_name_cover
                        dict_xxx_album['thumbnail'] = image_name_thumbnail

                dict_xxx_album_cover['original'] = image_name_original
                dict_xxx_album_cover['cover'] = image_name_cover
                dict_xxx_album_cover['thumbnail'] = image_name_thumbnail

                if type_album == 'actor':
                    temp_file_path = default_storage.save(os.path.join(f'{selected_vault}/actor', image_name_original), ContentFile(file.read()))
                elif type_album == 'picture':
                    temp_file_path = default_storage.save(os.path.join(f'{selected_vault}/picture', image_name_original), ContentFile(file.read()))
                elif type_album == 'manga':
                    print('manga')
                    temp_file_path = default_storage.save(os.path.join(f'{selected_vault}/manga', image_name_original), ContentFile(file.read()))
                elif type_album == 'video':
                    temp_file_path = default_storage.save(os.path.join(f'{selected_vault}/video', image_name_original), ContentFile(file.read()))
                elif type_album == 'music':
                    temp_file_path = default_storage.save(os.path.join(f'{selected_vault}/music', image_name_original), ContentFile(file.read()))
                
                print('temp_file_path', temp_file_path)
                original_file_path = os.path.join(save_dir, image_name_original)
                print('image_name_original', image_name_original)
                image_pil = Image.open(original_file_path)
                print('image_pil', image_pil)

                if type_album == 'actor':
                    file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_cover)
                    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_thumbnail)
                elif type_album == 'picture':
                    file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
                    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)
                elif type_album == 'manga':
                    file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA, image_name_cover)
                    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA, image_name_thumbnail)
                elif type_album == 'video':
                    file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_cover)
                    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_thumbnail)
                elif type_album == 'music':
                    file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_cover)
                    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_thumbnail)
                
                # Resize Original Image for Thumbnail, Cover
                
                cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
                thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
                
                # 커버이미지 저장
                cover_pil.save(file_path_cover)
                # 썸네일 이미지 저장
                thumbnail_pil.save(file_path_thumbnail)
        

    if type_album == 'actor':
        data = {
            'dict_actor_album_cover': dict_xxx_album_cover,
            'list_dict_profile_album':list_dict_xxx_album,
        }
        Actor.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
    elif type_album == 'picture':
        data = {
            'dict_picture_album_cover': dict_xxx_album_cover,
            'list_dict_picture_album':list_dict_xxx_album,
        }
        Picture_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
    elif type_album == 'manga':
        data = {
            'dict_manga_album_cover': dict_xxx_album_cover,
            'list_dict_manga_album':list_dict_xxx_album,
        }
        Manga_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
    elif type_album == 'video':
        data = {
            'dict_video_album_cover': dict_xxx_album_cover,
            'list_dict_picture_album':list_dict_xxx_album,
        }
        Video_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
    elif type_album == 'music':
        data = {
            'dict_music_album_cover': dict_xxx_album_cover,
            'list_dict_picture_album':list_dict_xxx_album,
        }
        Music_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()

    return True
    

# 사진 파일 리사이즈하기  (현재 사용하는 함수가 없음. 확인 후 삭제)
def resize_image(input_path, output_path, size):
    # cover_pil = resize_with_padding(image_pil, 520, 640) 
    # thumbnail_pil = resize_with_padding(image_pil, 260, 320)
    # size = (325, 410) 
    """
    Resizes an image to the specified size and saves it to the output path.

    :param input_path: Path to the input image.
    :param output_path: Path where the resized image will be saved.
    :param size: Tuple specifying the desired size (width, height).
    """
    try:
        # Open the input image
        with Image.open(input_path) as img:
            print(f"Original image size: {img.size}")  # (width, height)

            # Resize the image
            resized_img = img.resize(size, Image.ANTIALIAS)
            print(f"Resized image size: {resized_img.size}")

            # Save the resized image
            resized_img.save(output_path)
            print(f"Image saved as: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


# 사진 파일 리사이즈 및 크롭하기
def resize_and_crop(input_path, output_path, target_size):
    """
    Resizes and crops an image to the target size without padding.
    target_size for cover =(520, 640)
    target_size for thumbnail = (260, 320)

    :input_path: Path to the original image.
    :output_path: Path where the resized and cropped image will be saved.
    :target_size: Desired size as a tuple (width, height).
    """
    print('input_path', input_path)
    print('output_path', output_path)
    print('target_size', target_size)
    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        resample_filter = Image.ANTIALIAS


    try:
        with Image.open(input_path) as img:
            original_width, original_height = img.size
            target_width, target_height = target_size

            print(f"Original image size: {original_width}x{original_height}px")
            print(f"Target image size: {target_width}x{target_height}px")

            # Calculate aspect ratios
            original_ratio = original_width / original_height
            target_ratio = target_width / target_height

            # Determine scaling factor and size to resize
            if original_ratio > target_ratio:
                # Image is wider than target aspect ratio
                new_height = target_height
                new_width = int(new_height * original_ratio)
            else:
                # Image is taller than target aspect ratio
                new_width = target_width
                new_height = int(new_width / original_ratio)

            print(f"Resizing image to: {new_width}x{new_height}px")

            # Resize the image while maintaining aspect ratio
            img_resized = img.resize((new_width, new_height), resample_filter)

            # Calculate coordinates to crop the image to the target size
            left = (new_width - target_width) / 2
            top = (new_height - target_height) / 2
            right = left + target_width
            bottom = top + target_height

            print(f"Cropping image: left={left}, top={top}, right={right}, bottom={bottom}")

            # Crop the center of the image
            img_cropped = img_resized.crop((left, top, right, bottom))

            # Save the final image
            img_cropped.save(output_path)
            print(f"Resized and cropped image saved as: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")



# 모든 파일 저장하기 (앨범 무관)
"""
Album 파일 저장하기 함수 parameter 정보: 

q_xxx_album_selected : q_actor / q_picture_album_selected / q_video_album_selected / q_music_album_selected
type_album : 'actor' / 'picture' / 'manga' / 'video' / 'music' 
file_format : image / video / audio
"""
# Album 이미지/비디오/오디오 파일 저장하기 및 Postprocessing
# No multiprocessing but SAVE Original Files using Django default_storage ContentFile to SAVE FAST + background postprocessing
def save_files_in_list_dict_xxx_album(q_xxx_album_selected, files, type_album):
    """
        Picture Album은
        active: true 이면 대문(커버) 이미지로 할당한다는 의미
        discard: true 이면 삭제한다는 의미
        id == number of items로 표시, 
        item 삭제시 파일은 삭제하고 리스트에서는 discard=true만 설정하고 item을 삭제하지는 않는다. ID 변경되지 않게 하려고
    """
    print(f'# 모든 파일 저장하기 (앨범 무관) : q_video_album_selected id: {q_xxx_album_selected.id}, type_album: {type_album}')
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    selected_vault = q_systemsettings_hansent.selected_vault
    
    list_collected_video_album_id_for_still_image_post_processing = []

    # Multiprocessing으로 파일 저장하기 (백그라운드 수행)
    def f_save_files_in_parallel(list_temp_file_path, save_dir, type_album, list_file_name, list_title_item):
        print(f'# Save uploaded files w/ celery postprocessing: {list_temp_file_path}, {save_dir}, {type_album}, {list_file_name}, {list_title_item}')
        # 시작하는 ID 찾기
        if type_album == 'actor':
            i = num_profile_album_image
        elif type_album == 'picture':
            i = num_picture_album_image
        elif type_album == 'manga':
            i = num_manga_album_image
        elif type_album == 'video':
            i = num_picture_album_image
            j = num_video_album_video
        elif type_album == 'music':
            i = num_picture_album_image
            j = num_music_album_audio

        list_tasks = []
        q = 0 
        for temp_file_path in list_temp_file_path:
            file_name = list_file_name[q]
            title_item = list_title_item[q]
            
            # Title 길이 제한
            max_length = 50
            title_item = title_item[:max_length] + "..." if len(title_item) > max_length else title_item
            
            # print('i, temp_file ----------------------------------------------------------------', i, temp_file)
            file_extension = temp_file_path.split('.')[-1]
            # print('file_extension', file_extension)
            if file_extension == 'webp':
                file_extension = 'jpg'

            # # mkv file 변환 one by one
            # if file_extension == 'mkv':
            #     file_extension = 'mp4'
            #     input_file_path = temp_file_path
            #     output_file_path = temp_file_path.replace('.mkv', '.mp4')
            #     import subprocess
            #     command = [
            #         "ffmpeg", "-i", input_file_path,
            #         "-c:v", "libx264",  # Convert video to H.264
            #         "-c:a", "aac",       # Convert audio to AAC
            #         "-strict", "experimental",
            #         output_file_path
            #     ]
            #     subprocess.run(command, check=True)
            #     print(f"Conversion complete: {output_file_path}")
            #     temp_file_path = output_file_path

            
            file_format = f_check_what_format_is_this_file(file_extension)  ## image / video / audio / unknown
            # print('file_format', file_format)
            if file_format != 'unknown':
                # file_name = temp_file_path.split('/')[-1]
                image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                image_name_cover = f'{hashcode}-c-{i}.{file_extension}'
                image_name_thumbnail = f'{hashcode}-t-{i}.{file_extension}'
                if type_album == 'video':
                    video_name_original = f'{hashcode}-v-{j}.{file_extension}'
                if type_album == 'music':
                    music_name_original = f'{hashcode}-m-{j}.{file_extension}'
                original_file_path = os.path.join(save_dir, image_name_original)
                list_tasks.append((temp_file_path, original_file_path, file_extension))

                if type_album == 'music':
                    # print('# 음원 metadata 획득')
                    if file_format == 'audio':
                        dict_metadata = {}
                        try:
                            dict_metadata = get_audio_metadata(temp_file_path)
                            title_str = dict_metadata['title']
                            title_str = str(title_str)
                            title_str = title_str.lower()
                            if 'unknown' in title_str:
                                title_str = file_name.replace(file_extension, '')
                                title_str = title_str.replace('.', '')
                                dict_metadata['title'] = title_str
                        except:
                            dict_metadata = {'title': 'unknown', 'album': 'unknown', 'artist':'unknown', 'duration_str':'unknown'}

                # List 업데이트
                if type_album == 'actor':
                    if file_format == 'image':
                        list_dict_profile_album.append({"id": i, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false"})
                        if len(list_dict_profile_album) > 1:
                            list_dict_profile_album[-2]["active"] = "false"
                            list_dict_profile_album[0]["discard"] = "true"
                        list_dict_profile_album[-1]["active"] = "true"
                        i = i + 1
                        # print('i', i)
                elif type_album == 'picture':
                    if file_format == 'image':
                        list_dict_picture_album.append({"id": i, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false"})
                        if len(list_dict_picture_album) > 1:
                            list_dict_picture_album[-2]["active"] = "false"
                            list_dict_picture_album[0]["discard"] = "true"
                        list_dict_picture_album[-1]["active"] = "true"
                        i = i + 1
                        # print('i', i)
                elif type_album == 'manga':
                    if file_format == 'image':
                        list_dict_manga_album.append({"id": i, 'volume': volume, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false"})
                        if len(list_dict_manga_album) > 1:
                            list_dict_manga_album[-2]["active"] = "false"
                            list_dict_manga_album[0]["discard"] = "true"
                        list_dict_manga_album[-1]["active"] = "true"
                        list_id_manga_in_volume.append(i)
                        i = i + 1
                        # print('i', i)
                elif type_album == 'video':
                    print('3-1')
                    if file_format == 'image':
                        list_dict_picture_album.append({"id": i, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false" })
                        if len(list_dict_picture_album) > 1:
                            list_dict_picture_album[-2]["active"] = "false"
                            list_dict_picture_album[0]["discard"] = "true"
                        list_dict_picture_album[-1]["active"] = "true"
                        print('i', i, 'image_name_original', image_name_original)
                        print(f'list_dict_picture_album: {list_dict_picture_album} - 1')
                        i = i + 1

                    elif file_format == 'video':
                        list_dict_video_album.append({"id": j, "title": title_item,  'filename': file_name, "video": video_name_original, "duration_second":0, "duration_str": "None",  "thumbnail":"default-t.png", "still":[{"time":0, "path":"default-t.png"}], "active":"false", "discard":"false"})
                        if len(list_dict_video_album) > 1:
                            list_dict_video_album[-2]["active"] = "false"
                            list_dict_video_album[0]["discard"] = "true"
                        list_dict_video_album[-1]["active"] = "true"
                        # print('j', j)
                        j = j + 1
                    print(f'List 업데이트 list_dict_video_album: {list_dict_video_album}')
                elif type_album == 'music':
                    if file_format == 'image':
                        list_dict_picture_album.append({"id": i, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false"})
                        if len(list_dict_picture_album) > 1:
                            list_dict_picture_album[-2]["active"] = "false"
                            list_dict_picture_album[0]["discard"] = "true"
                        list_dict_picture_album[-1]["active"] = "true"
                        # print('i', i)
                        i = i + 1
                    elif file_format == 'audio':
                        list_dict_music_album.append({"id": j, 'favorite': 'false', 'filename': file_name, "source": music_name_original, 'format': file_extension, 'title': dict_metadata['title'], 'album': dict_metadata['album'], 'artist': dict_metadata['artist'], 'duration': dict_metadata['duration_str'], "thumbnail":"default-t.png", "active":"false", "discard":"false"})
                        if len(list_dict_music_album) > 1:
                            list_dict_music_album[-2]["active"] = "false"
                            list_dict_music_album[0]["discard"] = "true"
                        list_dict_music_album[-1]["active"] = "true"
                        # print('j', j)
                        j = j + 1
                else:
                    pass
                
                # Postprocessing Celery Background 수행
                try:
                    saved_image_postprocessing_in_background.delay(file_format, type_album, temp_file_path, image_name_cover, image_name_thumbnail)
                except:
                    print('error!! saved_image_postprocessing_in_background')
                    pass
            q = q + 1



    # Get Title
    try:
        title = q_xxx_album_selected.title
    except:
        title = None

    # Get Hashcode
    hashcode = get_hashcode_from_selected_album(q_xxx_album_selected, type_album)
    
    # 1 앨범에 등록된 파일 리스트 확보
    if type_album == 'actor':
        # print("actor process")
        # print('q_xxx_album_selected.list_dict_profile_album', q_xxx_album_selected.list_dict_profile_album)
        DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR)
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR)
        RELATIVE_PATH_XXX = RELATIVE_PATH_ACTOR
        list_dict_profile_album = q_xxx_album_selected.list_dict_profile_album
        list_dict_picture_album = None
        list_dict_Manga_album = None
        list_dict_video_album = None
        list_dict_music_album = None
        if list_dict_profile_album is not None and len(list_dict_profile_album) > 0:
            for dict_profile_album in list_dict_profile_album:
                dict_profile_album["active"] = "false"
            data = {'list_dict_profile_album': list_dict_profile_album,}
            Actor.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        else:
            list_dict_profile_album = DEFAULT_LIST_DICT_PROFILE_ALBUM
        num_profile_album_image = len(list_dict_profile_album)

    elif type_album == 'picture':
        # print("picture process")
        DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
        RELATIVE_PATH_XXX = RELATIVE_PATH_PICTURE
        list_dict_profile_album = None
        list_dict_picture_album = q_xxx_album_selected.list_dict_picture_album
        list_dict_Manga_album = None
        list_dict_video_album = None
        list_dict_music_album = None
        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
            for dict_picture_album in list_dict_picture_album:
                dict_picture_album["active"] = "false"
            data = {'list_dict_picture_album': list_dict_picture_album,}
            print(f'list_dict_picture_album: {list_dict_picture_album} - 8')
            Picture_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        else:
            list_dict_picture_album = DEFAULT_LIST_DICT_PICTURE_ALBUM
        num_picture_album_image = len(list_dict_picture_album)

    elif type_album == 'manga':
        # print("manga process")
        DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA)
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA)
        RELATIVE_PATH_XXX = RELATIVE_PATH_MANGA
        list_dict_profile_album = None
        list_dict_picture_album = None
        list_dict_manga_album = q_xxx_album_selected.list_dict_manga_album
        list_dict_video_album = None
        list_dict_music_album = None
        if list_dict_manga_album is not None and len(list_dict_manga_album) > 0:
            for dict_manga_album in list_dict_manga_album:
                dict_manga_album["active"] = "false"
            data = {'list_dict_manga_album': list_dict_manga_album,}
            Manga_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        else:
            list_dict_manga_album = DEFAULT_LIST_DICT_MANGA_ALBUM
        num_manga_album_image = len(list_dict_manga_album)

        volume = q_xxx_album_selected.volume
        list_dict_volume_manga = q_xxx_album_selected.list_dict_volume_manga
        date_released = q_xxx_album_selected.date_released
        if date_released is not None:
            try:
                date_released_str = str(date_released.strftime("%Y-%m-%d"))
            except:
                date_released_str = 'unknown'
        else:
            date_released_str = 'unknown'
        list_id_manga_in_volume = []

    elif type_album == 'video':
        # print("video process")
        DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
        RELATIVE_PATH_XXX = RELATIVE_PATH_VIDEO
        list_dict_profile_album = None
        list_dict_picture_album = q_xxx_album_selected.list_dict_picture_album
        list_dict_Manga_album = None
        list_dict_video_album = q_xxx_album_selected.list_dict_video_album
        print(f'list_dict_picture_album: {list_dict_picture_album}')
        print(f'list_dict_video_album: {list_dict_video_album}')
        list_dict_music_album = None
        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
            for dict_picture_album in list_dict_picture_album:
                dict_picture_album["active"] = "false"
            data = {'list_dict_picture_album': list_dict_picture_album,}
            print(f'list_dict_picture_album: {list_dict_picture_album} - 9')
            Video_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        else:
            list_dict_picture_album = DEFAULT_LIST_DICT_PICTURE_ALBUM 
        num_picture_album_image = len(list_dict_picture_album)
        if list_dict_video_album is not None and len(list_dict_video_album) > 0:
            for dict_video_album in list_dict_video_album:
                dict_video_album["active"] = "false"
            data = {'list_dict_video_album': list_dict_video_album,}
            Video_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        else:
            list_dict_video_album = DEFAULT_LIST_DICT_VIDEO_ALBUM
        num_video_album_video = len(list_dict_video_album)
        print(f'len(list_dict_video_album) 1: {len(list_dict_video_album)}')

    elif type_album == 'music':
        # print("music process")
        DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC)
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC)
        RELATIVE_PATH_XXX = RELATIVE_PATH_MUSIC
        list_dict_profile_album = None
        list_dict_picture_album = q_xxx_album_selected.list_dict_picture_album
        list_dict_Manga_album = None
        list_dict_video_album = None
        list_dict_music_album = q_xxx_album_selected.list_dict_music_album
        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
            for dict_picture_album in list_dict_picture_album:
                dict_picture_album["active"] = "false"
            data = {'list_dict_picture_album': list_dict_picture_album,}
            Music_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        else:
            list_dict_picture_album = DEFAULT_LIST_DICT_PICTURE_ALBUM
        num_picture_album_image = len(list_dict_picture_album)
        if list_dict_music_album is not None and len(list_dict_music_album) > 0:
            for dict_music_album in list_dict_music_album:
                dict_music_album["active"] = "false"
            data = {'list_dict_music_album': list_dict_music_album,}
            Music_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        else:
            list_dict_music_album = DEFAULT_LIST_DICT_MUSIC_ALBUM
        num_music_album_audio = len(list_dict_music_album)
    
    else:
        RELATIVE_PATH_XXX = None
        list_dict_profile_album = None
        list_dict_picture_album = None
        list_dict_Manga_album = None
        list_dict_video_album = None
        list_dict_music_album = None

    total_num_files = len(files)
    print('total_num_files', total_num_files)

    # Timestamp for checking processing time
    timestamp_start = time.perf_counter()
    
    # 시작하는 ID 찾기
    if type_album == 'actor':
        i = num_profile_album_image
    elif type_album == 'picture':
        i = num_picture_album_image
    elif type_album == 'manga':
        i = num_manga_album_image
    elif type_album == 'video':
        i = num_picture_album_image
        j = num_video_album_video
    elif type_album == 'music':
        i = num_picture_album_image
        j = num_music_album_audio
    
    
    # 파일 저장하기
    # 1 Image 파일을 Django Default_Storage에 빠르게 임시 저장하고 Path정보 획득 (multiprocessing argument로 넘기기 위해)
    # Original Image Processing
    tot_num_image = 0
    tot_num_video = 0
    tot_num_audio = 0
    list_temp_file_path = []
    list_file_name = []
    list_title_item = []
    p = 0

    for file in files:  
        file_name = file.name
        print(f'p: {p},  raw file_name: {file_name}')
        if '.webp' in file_name:
            file_name = file_name.replace('.webp', '.jpg')
        list_file_name.append(file_name)
        file_extension = file_name.split('.')[-1]

        # 파일 포맷별 타입 지정
        file_format = f_check_what_format_is_this_file(file_extension)  ## image / video / audio / unknown
        print(f'file_format: {file_format}')
        
        # 타이틀 지정, 저장하기
        try:
            if title:
                print('# 사용자 입력 title이 있는 경우, 등록된 앨범 개수 + 1을 title 뒤에 추가하여 파일이름을 강제설정')
                if type_album == 'actor':
                    list_dict_xxx_album = q_xxx_album_selected.list_dict_profile_album
                elif type_album == 'picture':
                    list_dict_xxx_album = q_xxx_album_selected.list_dict_picture_album
                elif type_album == 'manga':
                    list_dict_xxx_album = q_xxx_album_selected.list_dict_manga_album
                elif type_album == 'video':
                    list_dict_xxx_album = q_xxx_album_selected.list_dict_video_album
                elif type_album == 'music':
                    list_dict_xxx_album = q_xxx_album_selected.list_dict_music_album

                num_album_item = len(list_dict_xxx_album)    
                title_item = f'{title}-{num_album_item + p}'
                # 앨범 Title 등록하기
                register_title_to_album(q_xxx_album_selected, type_album, title_item)
                print('title_item', title_item)
            else:
                print('# 사용자 입력 title이 없는 경우, 파일 이름에서 Title로 쓸만한 단어 조합')
                # 텍스트 뭉치 클리닝
                file_name_cleaned = text_cleaning(file_name)  

                # 클리닝된 텍스트 뭉치에서 단어 분리 => 단어 리스트화
                list_file_name_split = text_to_list_word(file_name_cleaned)
                
                # 단어 리스트에서 Title 변환
                title_item = list_word_joining_for_title(list_file_name_split)

                # 앨범 Title 등록하기
                register_title_to_album(q_xxx_album_selected, type_album, title_item)
                
                # 단어 리스트에서 Tag으로 쓸만한 단어 수집
                list_collected_tags = collect_tag_element_from_text(list_file_name_split)

                # 앨범 Tag 등록하기
                register_tags_to_album(q_xxx_album_selected, type_album, list_collected_tags)
        except:
            print('이름보정 실패')
            title_item = 'none'
            pass
        # 보정된 file이름을 List에 담는다.
        list_title_item.append(title_item)

        print(f'file_extension: {file_extension}')
        print(f'file_format: {file_format}')
        
        # File Storage에 저장하기
        if file_format != 'unknown':
            print('# Save Images in tmp folder')
            if type_album == 'actor':
                if file_format == 'image':
                    image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                    temp_file_path = default_storage.save(os.path.join(f'{selected_vault}/actor', image_name_original), ContentFile(file.read()))
                    i = i + 1
                    tot_num_image = tot_num_image + 1
                else:
                    temp_file_path = None
            elif type_album == 'picture':
                if file_format == 'image':
                    image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                    temp_file_path = default_storage.save(os.path.join(f'{selected_vault}/picture', image_name_original), ContentFile(file.read()))
                    i = i + 1
                    tot_num_image = tot_num_image + 1
                else:
                    temp_file_path = None
            elif type_album == 'manga':
                if file_format == 'image':
                    image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                    temp_file_path = default_storage.save(os.path.join(f'{selected_vault}/manga', image_name_original), ContentFile(file.read()))
                    i = i + 1
                    tot_num_image = tot_num_image + 1
                else:
                    temp_file_path = None

            elif type_album == 'video':
                if file_format == 'image':
                    image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                    file_path = os.path.join(f'{selected_vault}/video', image_name_original)
                    # 기존 파일이 존재하면 삭제
                    if default_storage.exists(file_path):
                        default_storage.delete(file_path)
                    with file.open('rb') as f:
                        temp_file_path = default_storage.save(file_path, ContentFile(file.read()))
                        print(f'image file 저장 완료): {temp_file_path}')
                    i = i + 1
                    tot_num_image = tot_num_image + 1
                elif file_format == 'video':
                    video_name_original = f'{hashcode}-v-{j}.{file_extension}'
                    file_path = os.path.join(f'{selected_vault}/video', video_name_original)
                    # 기존 파일이 존재하면 삭제
                    if default_storage.exists(file_path):
                        default_storage.delete(file_path)
                    with file.open('rb') as f:
                        temp_file_path = default_storage.save(file_path, ContentFile(file.read()))
                        print(f'video file 저장 완료): {temp_file_path}')
                    j = j + 1
                    tot_num_video = tot_num_video + 1
                else:
                    temp_file_path = None
                    print(f'video file 저장 실패')

            elif type_album == 'music':
                if file_format == 'image':
                    image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                    temp_file_path = default_storage.save(os.path.join(f'{selected_vault}/music', image_name_original), ContentFile(file.read()))
                    i = i + 1
                    tot_num_image = tot_num_image + 1
                elif file_format == 'audio':
                    music_name_original = f'{hashcode}-m-{j}.{file_extension}'
                    temp_file_path = default_storage.save(os.path.join(f'{selected_vault}/music', music_name_original), ContentFile(file.read()))
                    j = j + 1
                    tot_num_audio = tot_num_audio + 1
                else:
                    temp_file_path = None
            else:
                print('type 지정 실패')
                pass

            if temp_file_path is not None:
                path = default_storage.path(temp_file_path)
                list_temp_file_path.append(path)
        p = p + 1
        
    # Process images in parallel
    f_save_files_in_parallel(list_temp_file_path, save_dir, type_album, list_file_name, list_title_item)
    
    timestamp_finish = time.perf_counter()
    # print(f'########################################################################## Finished in {round(timestamp_finish - timestamp_start, 2)} second(s) !!')

    # List_dict_XXX_album default 이미지 discard 하기 default에 하나 이상 item이 추가된 경우.
    if type_album == 'actor':
        list_dict_profile_album[-1]["active"] = 'true'
        data = {
            'list_dict_profile_album': list_dict_profile_album,
        }
        Actor.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
    elif type_album == 'picture':
        list_dict_picture_album[-1]["active"] = 'true'
        print(f'list_dict_picture_album: {list_dict_picture_album} - 2')
        data = {
            'list_dict_picture_album': list_dict_picture_album,
        }
        Picture_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
    elif type_album == 'manga':
        list_dict_manga_album[-1]["active"] = 'true'
        for dict_volume_manga in  list_dict_volume_manga:
            if dict_volume_manga['volume'] == volume:
                list_id_manga_in_volume_old = dict_volume_manga['list_id']
                # print('list_id_manga_in_volume_old', list_id_manga_in_volume_old)
                # print('list_id_manga_in_volume', list_id_manga_in_volume)
                in_first = set(list_id_manga_in_volume_old)
                in_second = set(list_id_manga_in_volume)
                in_second_but_not_in_first  = in_second - in_first 
                list_id_manga_in_volume = list_id_manga_in_volume_old + list(in_second_but_not_in_first)
                dict_volume_manga['list_id'] = list_id_manga_in_volume
                dict_volume_manga['date_released'] = date_released_str
                dict_volume_manga['title'] = q_xxx_album_selected.title
        data = {
            'list_dict_manga_album': list_dict_manga_album,
            'list_dict_volume_manga': list_dict_volume_manga,
        }
        Manga_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
    elif type_album == 'video':
        # print(f'%%%%%%%%%%%%%%%%%%%%%%%%% len(list_dict_video_album) 2: {len(list_dict_video_album)}')
        list_dict_picture_album[-1]["active"] = 'true'
        list_dict_video_album[-1]["active"] = 'true'
        print(f'list_dict_picture_album: {list_dict_picture_album} - 3')
        data = {
            'list_dict_picture_album': list_dict_picture_album,
            'list_dict_video_album': list_dict_video_album,
        }
        Video_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()
        list_collected_video_album_id_for_still_image_post_processing.append(q_xxx_album_selected.id)
    elif type_album == 'music':
        list_dict_picture_album[-1]["active"] = 'true'
        list_dict_music_album[-1]["active"] = 'true'
        data = {
            'list_dict_picture_album': list_dict_picture_album,
            'list_dict_music_album': list_dict_music_album,
        }
        Music_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
        q_xxx_album_selected.refresh_from_db()

    if len(list_collected_video_album_id_for_still_image_post_processing) > 0:
        print('video still image processing in background')
        save_video_album_video_still_images_in_task.delay(list_collected_video_album_id_for_still_image_post_processing)

    return q_xxx_album_selected
    


























#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#
#                                                  Folder 통으로 신규생성 저장하기기
#


"""
Folder Tree 구조

{
  "folders": {
    "test_f0": {
      "files": [
        "test_f0-1.jpg",
        "test_f0-1.mp4",
        "test_f0-2.mp4",
        "test_f0-2.jpg"
      ],
      "folders": {
        "test_f2": {
          "files": [
            "test_f2.jpg",
            "test_f2.mp4"
          ],
          "folders": {
            "test_f2_subfolder": {
              "files": [
                "test_f2_subfolder_1.jpg",
                "test_f2_subfolder_2.jpg"
              ]
            }
          }
        },
        "test_f1": {
          "files": [
            "test_f1.jpg",
            "test_f1.mp4"
          ]
        }
      }
    }
  }
}

"""
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################

# Tree 구조의 path 정보를 앨범으로 등록하기 쉽도록 List dictionary 형태로 반환
def convert_tree_to_list_dict_for_album_register(tree):
    """ 
    [
        {'folder_name': 폴더명1, 'contents': [파일이름1, 파일이름2 ... ], 'type_album': 'picture'}, 
        {'folder_name': 폴더명2, 'contents': [파일이름1, 파일이름2 ... ], 'type_album': 'picture'}, 
        {'folder_name': 폴더명1, 'contents': [파일이름1, 파일이름2 ... ], 'type_album': 'video'}, 
        {'folder_name': 폴더명2, 'contents': [파일이름1, 파일이름2 ... ], 'type_album': 'video'}, 
        {'folder_name': 폴더명3, 'contents': [파일이름1, 파일이름2 ... ], 'type_album': 'music'}, 
        {}, ...
    ]
    """
    """
                
        list_folder_file_for_album: 
        [
            {'folder_name': 'test_f0', 'contents': ['test_f0-1.jpg', 'test_f0-2.jpg'], 'album_type': 'picture'}, 
            {'folder_name': 'test_f0', 'contents': ['test_f0-1.mp4', 'test_f0-2.mp4'], 'album_type': 'video'}, 
            {'folder_name': 'test_f0', 'contents': [], 'album_type': 'music'}, 
            {'folder_name': 'test_f2', 'contents': ['test_f2.jpg'], 'album_type': 'picture'}, 
            {'folder_name': 'test_f2', 'contents': ['test_f2.mp4'], 'album_type': 'video'}, 
            {'folder_name': 'test_f2', 'contents': [], 'album_type': 'music'}, 
            {'folder_name': 'test_f2_subfolder', 'contents': ['test_f2_subfolder_1.jpg', 'test_f2_subfolder_2.jpg'], 'album_type': 'picture'}, 
            {'folder_name': 'test_f2_subfolder', 'contents': [], 'album_type': 'video'}, 
            {'folder_name': 'test_f2_subfolder', 'contents': [], 'album_type': 'music'}, 
            {'folder_name': 'test_f1', 'contents': ['test_f1.jpg'], 'album_type': 'picture'}, 
            {'folder_name': 'test_f1', 'contents': ['test_f1.mp4'], 'album_type': 'video'}, 
            {'folder_name': 'test_f1', 'contents': [], 'album_type': 'music'}
        ]
    """
    list_folder_file_for_album = []  
    folders = tree['folders']
    for k0, v0 in folders.items():
        # k0 = 최외곽 폴더 이름 == Actor Name으로 활용, 하지만 folder_name을 따로 받아서 Step 1 에서 미리 프로세싱 했음.
        # v0 = 최외곽 폴더 내 두 컨텐츠,  files, folders
        for k1, v1 in v0.items():
            # print(f'k1, {k1}')
            if k1 == 'files':
                # 최외곽 폴더에 포함된 파일
                list_file_picture = []
                list_file_video = []
                list_file_music = []
                for file_name in v1:
                    file_extension = file_name.split('.')[-1]
                    file_format = f_check_what_format_is_this_file(file_extension)  ## image / video / audio / unknown
                    if file_format == 'image':
                        list_file_picture.append(file_name)
                    elif file_format == 'video':
                        list_file_video.append(file_name)
                    elif file_format == 'audio':
                        list_file_music.append(file_name)
                    else:
                        pass
                list_folder_file_for_album.append({'folder_name': k0, 'contents': list_file_picture, 'type_album': 'picture'})
                list_folder_file_for_album.append({'folder_name': k0, 'contents': list_file_video, 'type_album': 'video'})
                list_folder_file_for_album.append({'folder_name': k0, 'contents': list_file_music, 'type_album': 'music'})

            if k1 == 'folders':
                for k2, v2 in v1.items():
                    # print(f'v2, {v2}')
                    if 'files' in v2:
                        files2 = v2['files']
                        # 최외곽 폴더에 포함된 파일
                        list_file_picture = []
                        list_file_video = []
                        list_file_music = []
                        for file_name in files2:
                            file_extension = file_name.split('.')[-1]
                            file_format = f_check_what_format_is_this_file(file_extension)  ## image / video / audio / unknown
                            if file_format == 'image':
                                list_file_picture.append(file_name)
                            elif file_format == 'video':
                                list_file_video.append(file_name)
                            elif file_format == 'audio':
                                list_file_music.append(file_name)
                            else:
                                pass
                        list_folder_file_for_album.append({'folder_name': k2, 'contents': list_file_picture, 'type_album': 'picture'})
                        list_folder_file_for_album.append({'folder_name': k2, 'contents': list_file_video, 'type_album': 'video'})
                        list_folder_file_for_album.append({'folder_name': k2, 'contents': list_file_music, 'type_album': 'music'})

                    if 'folders' in v2:
                        folders2 = v2['folders']    
                    
                        for k3, v3 in folders2.items():
                            # print(f'k3, {k3}')
                            # print(f'v3, {v3}')
                            if 'files' in v3:
                                files3 = v3['files']
                                # 최외곽 폴더에 포함된 파일
                                list_file_picture = []
                                list_file_video = []
                                list_file_music = []
                                for file_name in files3:
                                    file_extension = file_name.split('.')[-1]
                                    file_format = f_check_what_format_is_this_file(file_extension)  ## image / video / audio / unknown
                                    if file_format == 'image':
                                        list_file_picture.append(file_name)
                                    elif file_format == 'video':
                                        list_file_video.append(file_name)
                                    elif file_format == 'audio':
                                        list_file_music.append(file_name)
                                    else:
                                        pass
                                list_folder_file_for_album.append({'folder_name': k3, 'contents': list_file_picture, 'type_album': 'picture'})
                                list_folder_file_for_album.append({'folder_name': k3, 'contents': list_file_video, 'type_album': 'video'})
                                list_folder_file_for_album.append({'folder_name': k3, 'contents': list_file_music, 'type_album': 'music'})
                            
                            if 'folders' in v3:
                                folders3 = v3['folders']
                                for k4, v4 in folders3.items():
                                    # print(f'k4, {k4}')
                                    # print(f'v4, {v4}')
                                    if 'files' in v4:
                                        files4 = v4['files']
                                        # 최외곽 폴더에 포함된 파일
                                        list_file_picture = []
                                        list_file_video = []
                                        list_file_music = []
                                        for file_name in files4:
                                            file_extension = file_name.split('.')[-1]
                                            file_format = f_check_what_format_is_this_file(file_extension)  ## image / video / audio / unknown
                                            if file_format == 'image':
                                                list_file_picture.append(file_name)
                                            elif file_format == 'video':
                                                list_file_video.append(file_name)
                                            elif file_format == 'audio':
                                                list_file_music.append(file_name)
                                            else:
                                                pass
                                        list_folder_file_for_album.append({'folder_name': k4, 'contents': list_file_picture, 'type_album': 'picture'})
                                        list_folder_file_for_album.append({'folder_name': k4, 'contents': list_file_video, 'type_album': 'video'})
                                        list_folder_file_for_album.append({'folder_name': k4, 'contents': list_file_music, 'type_album': 'music'})

    print(f'list_folder_file_for_album: {list_folder_file_for_album}')
    return list_folder_file_for_album



# 파일 정보를 DB Album Table에 저장
def f_save_file_info_to_db_album(list_dict_file_info_for_post_processing_in_parallel):

    """
    list_dict_file_info_for_post_processing_in_parallel = [
        {
            'id': q,
            'q_actor_id': q_actor.id,
            'q_xxx_album_id': q_xxx_album.id,
            'file_name': file_name,
            'title_item': title_item, 
            'type_album': type_album,
            'file_extension': file_extension,
            'file_format': file_format,
            'default_storage_path': default_storage_path,
            'image_name_original': image_name_original,
            'image_name_cover': image_name_cover,
            'image_name_thumbnail': image_name_thumbnail,
            'video_name_original': video_name_original,
            'music_name_original': music_name_original,
            'original_image_file_path': original_image_file_path,
        }
    ]
    """

    
    list_collected_video_album_id_for_still_image_post_processing = []
    i = 0
    j = 0
    q = 0
    for dict_file_info_for_post_processing_in_parallel in list_dict_file_info_for_post_processing_in_parallel:
        id = dict_file_info_for_post_processing_in_parallel['id']
        q_actor_id = dict_file_info_for_post_processing_in_parallel['q_actor_id']
        q_xxx_album_id = dict_file_info_for_post_processing_in_parallel['q_xxx_album_id']
        file_name = dict_file_info_for_post_processing_in_parallel['file_name']
        title_item = dict_file_info_for_post_processing_in_parallel['title_item']
        type_album = dict_file_info_for_post_processing_in_parallel['type_album']
        file_extension = dict_file_info_for_post_processing_in_parallel['file_extension']
        file_format = dict_file_info_for_post_processing_in_parallel['file_format']
        default_storage_path = dict_file_info_for_post_processing_in_parallel['default_storage_path']
        image_name_original = dict_file_info_for_post_processing_in_parallel['image_name_original']
        image_name_cover = dict_file_info_for_post_processing_in_parallel['image_name_cover']
        image_name_thumbnail = dict_file_info_for_post_processing_in_parallel['image_name_thumbnail']
        video_name_original = dict_file_info_for_post_processing_in_parallel['video_name_original']
        music_name_original = dict_file_info_for_post_processing_in_parallel['music_name_original']
        original_image_file_path = dict_file_info_for_post_processing_in_parallel['original_image_file_path']


        if type_album == 'music':
            # print('# 음원 metadata 획득')
            if file_format == 'audio':
                dict_metadata = {}
                try:
                    dict_metadata = get_audio_metadata(default_storage_path)
                    title_str = dict_metadata['title']
                    title_str = str(title_str)
                    title_str = title_str.lower()
                    if 'unknown' in title_str:
                        title_str = file_name.replace(file_extension, '')
                        title_str = title_str.replace('.', '')
                        dict_metadata['title'] = title_str
                except:
                    dict_metadata = {'title': 'unknown', 'album': 'unknown', 'artist':'unknown', 'duration_str':'unknown'}

        # List 업데이트
        if type_album == 'picture':
            q_xxx_album = Picture_Album.objects.get(id=q_xxx_album_id)
            list_dict_picture_album = q_xxx_album.list_dict_picture_album
            if file_format == 'image':
                list_dict_picture_album.append({"id": id, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false"})
                if len(list_dict_picture_album) > 1:
                    list_dict_picture_album[-2]["active"] = "false"
                    list_dict_picture_album[0]["discard"] = "true"
                list_dict_picture_album[-1]["active"] = "true"
                i = i + 1
                # print('i', i)
        elif type_album == 'manga':
            q_xxx_album = Manga_Album.objects.get(id=q_xxx_album_id)
            volume = q_xxx_album.volume
            date_released = q_xxx_album.date_released
            if date_released is not None:
                try:
                    date_released_str = str(date_released.strftime("%Y-%m-%d"))
                except:
                    date_released_str = 'unknown'
            else:
                date_released_str = 'unknown'
            list_dict_manga_album = q_xxx_album.list_dict_manga_album
            list_dict_volume_manga = q_xxx_album.list_dict_volume_manga
            if file_format == 'image':
                list_dict_manga_album.append({"id": id, 'volume': volume, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false"})
                if len(list_dict_manga_album) > 1:
                    list_dict_manga_album[-2]["active"] = "false"
                    list_dict_manga_album[0]["discard"] = "true"
                list_dict_manga_album[-1]["active"] = "true"
                list_id_manga_in_volume.append(i)
                i = i + 1
                # print('i', i)
        elif type_album == 'video':
            q_xxx_album = Video_Album.objects.get(id=q_xxx_album_id)
            list_dict_picture_album = q_xxx_album.list_dict_picture_album
            list_dict_video_album = q_xxx_album.list_dict_video_album
            if file_format == 'image':
                list_dict_picture_album.append({"id": id, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false" })
                if len(list_dict_picture_album) > 1:
                    list_dict_picture_album[-2]["active"] = "false"
                    list_dict_picture_album[0]["discard"] = "true"
                list_dict_picture_album[-1]["active"] = "true"
                # print('i', i, 'image_name_original', image_name_original)
                # print(f'list_dict_picture_album: {list_dict_picture_album} - 1')
                i = i + 1
            elif file_format == 'video':
                list_dict_video_album.append({"id": id, "title": title_item,  'filename': file_name, "video": video_name_original, "duration_second":0, "duration_str": "None",  "thumbnail":"default-t.png", "still":[{"time":0, "path":"default-t.png"}], "active":"false", "discard":"false"})
                if len(list_dict_video_album) > 1:
                    list_dict_video_album[-2]["active"] = "false"
                    list_dict_video_album[0]["discard"] = "true"
                list_dict_video_album[-1]["active"] = "true"
                # print('j', j)
                j = j + 1
        elif type_album == 'music':
            q_xxx_album = Music_Album.objects.get(id=q_xxx_album_id)
            list_dict_picture_album = q_xxx_album.list_dict_picture_album
            list_dict_music_album = q_xxx_album.list_dict_music_album
            if file_format == 'image':
                list_dict_picture_album.append({"id": id, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false"})
                if len(list_dict_picture_album) > 1:
                    list_dict_picture_album[-2]["active"] = "false"
                    list_dict_picture_album[0]["discard"] = "true"
                list_dict_picture_album[-1]["active"] = "true"
                # print('i', i)
                i = i + 1
            elif file_format == 'audio':
                list_dict_music_album.append({"id": id, 'favorite': 'false', 'filename': file_name, "source": music_name_original, 'format': file_extension, 'title': dict_metadata['title'], 'album': dict_metadata['album'], 'artist': dict_metadata['artist'], 'duration': dict_metadata['duration_str'], "thumbnail":"default-t.png", "active":"false", "discard":"false"})
                if len(list_dict_music_album) > 1:
                    list_dict_music_album[-2]["active"] = "false"
                    list_dict_music_album[0]["discard"] = "true"
                list_dict_music_album[-1]["active"] = "true"
                # print('j', j)
                j = j + 1
        else:
            pass

        # DB Album에 저장하기
        q_actor = Actor.objects.get(id=q_actor_id)
        if type_album == 'picture':
            list_dict_picture_album[-1]["active"] = 'true'
            data = {
                'main_actor': q_actor,
                'list_dict_picture_album': list_dict_picture_album,
            }
            Picture_Album.objects.filter(id=q_xxx_album.id).update(**data)
            q_xxx_album.refresh_from_db()
        elif type_album == 'manga':
            list_dict_manga_album[-1]["active"] = 'true'
            for dict_volume_manga in  list_dict_volume_manga:
                if dict_volume_manga['volume'] == volume:
                    list_id_manga_in_volume_old = dict_volume_manga['list_id']
                    in_first = set(list_id_manga_in_volume_old)
                    in_second = set(list_id_manga_in_volume)
                    in_second_but_not_in_first  = in_second - in_first 
                    list_id_manga_in_volume = list_id_manga_in_volume_old + list(in_second_but_not_in_first)
                    dict_volume_manga['list_id'] = list_id_manga_in_volume
                    dict_volume_manga['date_released'] = date_released_str
                    dict_volume_manga['title'] = q_xxx_album.title
            data = {
                'list_dict_manga_album': list_dict_manga_album,
                'list_dict_volume_manga': list_dict_volume_manga,
            }
            Manga_Album.objects.filter(id=q_xxx_album.id).update(**data)
            q_xxx_album.refresh_from_db()
        elif type_album == 'video':
            list_dict_picture_album[-1]["active"] = 'true'
            list_dict_video_album[-1]["active"] = 'true'
            data = {
                'main_actor': q_actor,
                'list_dict_picture_album': list_dict_picture_album,
                'list_dict_video_album': list_dict_video_album,
            }
            Video_Album.objects.filter(id=q_xxx_album.id).update(**data)
            q_xxx_album.refresh_from_db()
            list_collected_video_album_id_for_still_image_post_processing.append(q_xxx_album.id)
        elif type_album == 'music':
            list_dict_picture_album[-1]["active"] = 'true'
            list_dict_music_album[-1]["active"] = 'true'
            data = {
                'main_actor': q_actor,
                'list_dict_picture_album': list_dict_picture_album,
                'list_dict_music_album': list_dict_music_album,
            }
            Music_Album.objects.filter(id=q_xxx_album.id).update(**data)
            q_xxx_album.refresh_from_db()
        q = q + 1

    print(f'list_collected_video_album_id_for_still_image_post_processing: {list_collected_video_album_id_for_still_image_post_processing}')
    return list_collected_video_album_id_for_still_image_post_processing




# 폴더 + 하위폴더 통짜로 자동 Actor 및 Album 생성
def save_folder_in_list_dict_xxx_album(q_actor, files, tree, folder_name_str, file_upload_option_str):
    random_sec = random.uniform(3, 4)
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    selected_vault = q_systemsettings_hansent.selected_vault

    total_num_files = len(files)
    print(f'total_num_files": {total_num_files}')

    # Get Title
    try:
        title = q_actor.title
    except:
        title = None

    # Get Hashcode
    hashcode = q_actor.hashcode

    # Step 1 -----------------------------------------------------------------------------------------------------
    # 최상위 폴더 이름으로 Actor 이름 및 동의어 지정/저장
    if q_actor.name is None:
        # 신규 생성한 Actor이면 최상위 폴더명으로 이름 작성 및 저장
        actor_name = folder_name_str 
        file_name_cleaned = text_cleaning(actor_name)  
        # 클리닝된 텍스트 뭉치에서 단어 분리 => 단어 리스트화
        list_name = text_to_list_name(file_name_cleaned)
        # 이름 리스트에서 Name과 Synonyms 반환
        name, synonyms = classify_name_and_synonyms_from_list_word(list_name)
        # 앨범 Title 등록하기
        register_title_to_album(q_actor, 'actor', name)
        # 앨범 Synonyms 등록하기
        if synonyms is not None:
            register_synonyms_to_album(q_actor, 'actor', synonyms)

    # Step 2 -----------------------------------------------------------------------------------------------------
    # 앨범별 파일 리스트 분류하기: 폴더, 하위폴더 구조 파악하여 폴더명 = 앨범명, 폴더내 파일 = 앨범 컨텐츠 로 정리하여 앨범생성시 활용하기
    list_folder_file_for_album = convert_tree_to_list_dict_for_album_register(tree)

    # Step 3 -----------------------------------------------------------------------------------------------------
    # 파일을 분류된 앨범별 파일 리스트 활용하여
    # 1. File Storage로 파일 저장하기 + 
    # 2. DB Album Table에 정보 등록 위한 정보 리스트화 + 
    # 3. Image File / Video Still image post processing

    list_dict_file_info_for_post_processing_in_parallel = [] 
    
    tot_num_image = 0
    tot_num_video = 0
    tot_num_audio = 0
    
    for dict_item in list_folder_file_for_album:
        # 루프 한 번 돌 때마다 하나의 앨범을 생성함. 
        # 하나의 앨범에는 하나의 타입과 여러개의 파일들(폴더 내)이 포함됨. 
        # 하위폴더는 따로 각각의 폴더로 각각의 앨범을 만듬.

        folder_name = dict_item['folder_name']
        contents = dict_item['contents']
        type_album = dict_item['type_album']

        if contents is not None and len(contents) > 0:
            # 텍스트 뭉치 클리닝
            file_name_cleaned = text_cleaning(folder_name)  
            # 클리닝된 텍스트 뭉치에서 단어 분리 => 단어 리스트화
            list_file_name_split = text_to_list_word(file_name_cleaned)
            # 단어 리스트에서 Title 변환
            folder_name = list_word_joining_for_title(list_file_name_split)

            if type_album == 'picture':
                q_xxx_album = create_picture_album()
                data = {
                    'title': folder_name
                }
                Picture_Album.objects.filter(id=q_xxx_album.id).update(**data)
            elif type_album == 'manga':
                q_xxx_album = create_manga_album()
                data = {
                    'title': folder_name
                }
                Manga_Album.objects.filter(id=q_xxx_album.id).update(**data)
            elif type_album == 'video':
                q_xxx_album = create_video_album()
                data = {
                    'title': folder_name
                }
                Video_Album.objects.filter(id=q_xxx_album.id).update(**data)
            elif type_album == 'music':
                q_xxx_album = create_music_album()
                data = {
                    'title': folder_name
                }
                Music_Album.objects.filter(id=q_xxx_album.id).update(**data)
            else:
                q_xxx_album = None 

            if q_xxx_album is not None:
                hashcode = q_xxx_album.hashcode
                p = 0
                i = 0
                j = 0
                q = 0
                
                print(f'contents: {contents}, p, i, j, q: {p}, {i}, {j}, {q}')
                for content in contents:
                    for file in files:  
                        file_name = file.name
                        if content == file_name:
                            print(f'id: {q},  matched file name: {file_name}')
                            if '.webp' in file_name:
                                file_name = file_name.replace('.webp', '.jpg')
                            image_name_original = None
                            image_name_cover = None
                            image_name_thumbnail = None
                            video_name_original = None
                            music_name_original = None

                            # 텍스트 뭉치 클리닝
                            file_name_cleaned = text_cleaning(file_name)  
                            # 클리닝된 텍스트 뭉치에서 단어 분리 => 단어 리스트화
                            list_file_name_split = text_to_list_word(file_name_cleaned)
                            # 단어 리스트에서 Title 변환
                            title_item = list_word_joining_for_title(list_file_name_split)
                            
                            file_extension = file_name.split('.')[-1]
                            file_format = f_check_what_format_is_this_file(file_extension)  ## image / video / audio / unknown

                            # File Storage에 저장하기 (원본만 저장하고 resize 이미지는 postprocessing 한다.)
                            if file_format != 'unknown':
                                if type_album == 'picture':
                                    DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
                                    if not os.path.exists(DOWNLOAD_DIR):
                                        os.makedirs(DOWNLOAD_DIR)
                                    save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
                                    if file_format == 'image':
                                        image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                                        image_name_cover = f'{hashcode}-c-{i}.{file_extension}'
                                        image_name_thumbnail = f'{hashcode}-t-{i}.{file_extension}'
                                        file_path = os.path.join(f'{selected_vault}/picture', image_name_original)
                                        # 기존 파일이 존재하면 삭제
                                        if default_storage.exists(file_path):
                                            default_storage.delete(file_path)
                                        with file.open('rb') as f:
                                            temp_file_path = default_storage.save(file_path, ContentFile(file.read()))
                                        i = i + 1
                                        q = q + 1
                                        tot_num_image = tot_num_image + 1
                                    else:
                                        temp_file_path = None
                                elif type_album == 'manga':
                                    DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA)
                                    if not os.path.exists(DOWNLOAD_DIR):
                                        os.makedirs(DOWNLOAD_DIR)
                                    save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA)
                                    if file_format == 'image':
                                        image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                                        image_name_cover = f'{hashcode}-c-{i}.{file_extension}'
                                        image_name_thumbnail = f'{hashcode}-t-{i}.{file_extension}'
                                        file_path = os.path.join(f'{selected_vault}/manga', image_name_original)
                                        # 기존 파일이 존재하면 삭제
                                        if default_storage.exists(file_path):
                                            default_storage.delete(file_path)
                                        with file.open('rb') as f:
                                            temp_file_path = default_storage.save(file_path, ContentFile(file.read()))
                                        i = i + 1
                                        q = q + 1
                                        tot_num_image = tot_num_image + 1
                                    else:
                                        temp_file_path = None
                                elif type_album == 'video':
                                    DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
                                    if not os.path.exists(DOWNLOAD_DIR):
                                        os.makedirs(DOWNLOAD_DIR)
                                    save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
                                    if file_format == 'image':
                                        image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                                        image_name_cover = f'{hashcode}-c-{i}.{file_extension}'
                                        image_name_thumbnail = f'{hashcode}-t-{i}.{file_extension}'
                                        file_path = os.path.join(f'{selected_vault}/video', image_name_original)
                                        # 기존 파일이 존재하면 삭제
                                        if default_storage.exists(file_path):
                                            default_storage.delete(file_path)
                                        with file.open('rb') as f:
                                            temp_file_path = default_storage.save(file_path, ContentFile(file.read()))
                                        i = i + 1
                                        q = q + 1
                                        tot_num_image = tot_num_image + 1
                                    elif file_format == 'video':
                                        video_name_original = f'{hashcode}-v-{j}.{file_extension}'
                                        file_path = os.path.join(f'{selected_vault}/video', video_name_original)
                                        # 기존 파일이 존재하면 삭제
                                        if default_storage.exists(file_path):
                                            default_storage.delete(file_path)
                                        with file.open('rb') as f:
                                            temp_file_path = default_storage.save(file_path, ContentFile(file.read()))
                                        j = j + 1
                                        q = q + 1
                                        tot_num_video = tot_num_video + 1
                                    else:
                                        temp_file_path = None
                                elif type_album == 'music':
                                    DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC)
                                    if not os.path.exists(DOWNLOAD_DIR):
                                        os.makedirs(DOWNLOAD_DIR)
                                    save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC)
                                    if file_format == 'image':
                                        image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                                        image_name_cover = f'{hashcode}-c-{i}.{file_extension}'
                                        image_name_thumbnail = f'{hashcode}-t-{i}.{file_extension}'
                                        file_path = os.path.join(f'{selected_vault}/music', image_name_original)
                                        # 기존 파일이 존재하면 삭제
                                        if default_storage.exists(file_path):
                                            default_storage.delete(file_path)
                                        with file.open('rb') as f:
                                            temp_file_path = default_storage.save(file_path, ContentFile(file.read()))
                                        i = i + 1
                                        q = q + 1
                                        tot_num_image = tot_num_image + 1
                                    elif file_format == 'audio':
                                        music_name_original = f'{hashcode}-m-{j}.{file_extension}'
                                        file_path = os.path.join(f'{selected_vault}/music', music_name_original)
                                        # 기존 파일이 존재하면 삭제
                                        if default_storage.exists(file_path):
                                            default_storage.delete(file_path)
                                        with file.open('rb') as f:
                                            temp_file_path = default_storage.save(file_path, ContentFile(file.read()))
                                        j = j + 1
                                        q = q + 1
                                        tot_num_audio = tot_num_audio + 1
                                    else:
                                        temp_file_path = None
                                else:
                                    save_dir = None 

                                # Path 생성
                                if temp_file_path is not None:
                                    default_storage_path = default_storage.path(temp_file_path)
                                else:
                                    default_storage_path = None

                                # original_image_file_path 생성성
                                if save_dir is not None and image_name_original is not None:
                                    original_image_file_path = os.path.join(save_dir, image_name_original)
                                else:
                                    original_image_file_path = None

                                # 정보 모으기
                                list_dict_file_info_for_post_processing_in_parallel.append(
                                    {
                                        'id': q,
                                        'q_actor_id': q_actor.id,
                                        'q_xxx_album_id': q_xxx_album.id,
                                        'file_name': file_name,
                                        'title_item': title_item, 
                                        'type_album': type_album,
                                        'file_extension': file_extension,
                                        'file_format': file_format,
                                        'default_storage_path': default_storage_path,
                                        'image_name_original': image_name_original,
                                        'image_name_cover': image_name_cover,
                                        'image_name_thumbnail': image_name_thumbnail,
                                        'video_name_original': video_name_original,
                                        'music_name_original': music_name_original,
                                        'original_image_file_path': original_image_file_path,
                                    }
                                )
                p = p + 1

    print(f'tot_num_image: {tot_num_image}')
    print(f'tot_num_video: {tot_num_video}')
    print(f'tot_num_audio: {tot_num_audio}')
    print('list_dict_file_info_for_post_processing_in_parallel', list_dict_file_info_for_post_processing_in_parallel)

    # Step 4 -----------------------------------------------------------------------------------------------------
    # DB Album Table에 정보 등록 위한 정보 리스트 활용하여 DB 업데이트트     
    if len(list_dict_file_info_for_post_processing_in_parallel) > 0:
        # print(f'list_dict_file_info_for_post_processing_in_parallel: {len(list_dict_file_info_for_post_processing_in_parallel)}')
        list_collected_video_album_id_for_still_image_post_processing = f_save_file_info_to_db_album(list_dict_file_info_for_post_processing_in_parallel)

        # Step 5 -----------------------------------------------------------------------------------------------------
        # 이미지 Post processing in Parallel (백그라운드 수행)
        saved_image_postprocessing_in_background_v2.delay(list_dict_file_info_for_post_processing_in_parallel)

        # Step 6 -----------------------------------------------------------------------------------------------------
        # 영상 Post processing in Parallel (백그라운드 수행)
        # print('list_collected_video_album_id_for_still_image_post_processing', list_collected_video_album_id_for_still_image_post_processing)
        if len(list_collected_video_album_id_for_still_image_post_processing) > 0:
            save_video_album_video_still_images_in_task.delay(list_collected_video_album_id_for_still_image_post_processing)

    # Step 7 -----------------------------------------------------------------------------------------------------
    # Actor에 등록된 앨범들에서 프로필로 사용할 이미지 획득
    time.sleep(random_sec)

    collect_images_from_registered_all_album_for_actor_profile_cover_image(q_actor)

    return True
    





























#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#
#                                                           File Delete
#
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################


"""
Album 파일 삭제하기 함수 parameter 정보: 

q_xxx_album_selected : q_actor / q_picture_album_selected / q_video_album_selected / q_music_album_selected
type_album : 'actor' / 'picture' / 'manga' / 'video' / 'music' 
type_list : 'all' / 'profile' / 'image' / 'video' / 'audio' 
id_delete : 'all' / int(selected_dict_id)

"""




# Album별 삭제함수
def delete_profile_item(dict_profile_album, RELATIVE_PATH_XXX):
    # print('delete_profile_item', dict_profile_album)
    image_name_original = dict_profile_album["original"]
    image_name_cover = dict_profile_album["cover"]
    image_name_thumbnail = dict_profile_album["thumbnail"]
    if image_name_original != 'default-o.png' :
        if image_name_original not in LIST_DEFAULT_IMAGES:
            file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_original)
            if os.path.exists(file_path_o):
                try:
                    os.remove(file_path_o)
                except:
                    pass
    if image_name_cover != 'default-c.png':
        if image_name_cover not in LIST_DEFAULT_IMAGES:
            file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_cover)
            if os.path.exists(file_path_c):
                try:
                    os.remove(file_path_c)
                except:
                    pass
    if image_name_thumbnail != 'default-t.png':
        if image_name_thumbnail not in LIST_DEFAULT_IMAGES:
            file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_thumbnail)
            if os.path.exists(file_path_t):
                try:
                    os.remove(file_path_t)
                except:
                    pass
    # 리스트에서 discard 처리하기

def delete_picture_item(dict_picture_album, RELATIVE_PATH_XXX):
    # print('delete_picture_item', dict_picture_album)
    image_name_original = dict_picture_album["original"]
    image_name_cover = dict_picture_album["cover"]
    image_name_thumbnail = dict_picture_album["thumbnail"]
    if image_name_original != 'default-o.png' :
        if image_name_original not in LIST_DEFAULT_IMAGES:
            file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_original)
            if os.path.exists(file_path_o):
                try:
                    os.remove(file_path_o)
                except:
                    pass
    if image_name_cover != 'default-c.png':
        if image_name_cover not in LIST_DEFAULT_IMAGES:
            file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_cover)
            if os.path.exists(file_path_c):
                try:
                    os.remove(file_path_c)
                except:
                    pass
    if image_name_thumbnail != 'default-t.png':
        if image_name_thumbnail not in LIST_DEFAULT_IMAGES:
            file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_thumbnail)
            if os.path.exists(file_path_t):
                try:
                    os.remove(file_path_t)
                except:
                    pass

def delete_manga_item(dict_manga_album, RELATIVE_PATH_XXX):
    # print('delete_manga_item', dict_manga_album)
    image_name_original = dict_manga_album["original"]
    image_name_cover = dict_manga_album["cover"]
    image_name_thumbnail = dict_manga_album["thumbnail"]
    if image_name_original != 'default-o.png' :
        if image_name_original not in LIST_DEFAULT_IMAGES:
            file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_original)
            if os.path.exists(file_path_o):
                try:
                    os.remove(file_path_o)
                except:
                    pass
    if image_name_cover != 'default-c.png':
        if image_name_cover not in LIST_DEFAULT_IMAGES:
            file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_cover)
            if os.path.exists(file_path_c):
                try:
                    os.remove(file_path_c)
                except:
                    pass
    if image_name_thumbnail != 'default-t.png':
        if image_name_thumbnail not in LIST_DEFAULT_IMAGES:
            file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_thumbnail)
            if os.path.exists(file_path_t):
                try:
                    os.remove(file_path_t)
                except:
                    pass

def delete_video_item(dict_video_album, RELATIVE_PATH_XXX):
    # print('delete_video_item', dict_video_album)
    try:
        image_name_original = dict_video_album["original"]
    except:
        image_name_original = None 
    try:
        image_name_cover = dict_video_album["cover"]
    except:
        image_name_cover = None 
    try:
        image_name_thumbnail = dict_video_album["thumbnail"]
    except:
        image_name_thumbnail = None
    if image_name_original is not None:
        if image_name_original != 'default-o.png':
            if image_name_original not in LIST_DEFAULT_IMAGES:
                file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_original)
                if os.path.exists(file_path_o):
                    try:
                        os.remove(file_path_o)
                    except:
                        pass
    if image_name_cover is not None:
        if image_name_cover != 'default-c.png':
            if image_name_cover not in LIST_DEFAULT_IMAGES:
                file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_cover)
                if os.path.exists(file_path_c):
                    try:
                        os.remove(file_path_c)
                    except:
                        pass
    if image_name_thumbnail is not None:
        if image_name_thumbnail != 'default-t.png':
            if image_name_thumbnail not in LIST_DEFAULT_IMAGES:
                file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_thumbnail)
                if os.path.exists(file_path_t):
                    try:
                        os.remove(file_path_t)
                    except:
                        pass
    # video file 삭제
    file_name_xxx = dict_video_album["video"]
    if file_name_xxx is not None:
        file_path_xxx = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, file_name_xxx)
        if os.path.exists(file_path_xxx):
            try:
                os.remove(file_path_xxx)
            except:
                pass
    # 스틸컷 이미지 삭제
    list_dict_file_name_still = dict_video_album["still"]
    for dict_file_name_still in list_dict_file_name_still:
        if dict_file_name_still not in LIST_DEFAULT_IMAGES:
            file_name_still = dict_file_name_still["path"]
            file_path_still = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, file_name_still)
            if os.path.exists(file_path_still):
                try:
                    os.remove(file_path_still)
                except:
                    pass
    
def delete_music_item(dict_music_album, RELATIVE_PATH_XXX):
    # print('delete_music_item', dict_music_album)
    image_name_original = dict_music_album["original"]
    image_name_cover = dict_music_album["cover"]
    image_name_thumbnail = dict_music_album["thumbnail"]
    if 'default' not in image_name_original:
        if image_name_original not in LIST_DEFAULT_IMAGES:
            file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_original)
            if os.path.exists(file_path_o):
                try:
                    os.remove(file_path_o)
                except:
                    pass
    if 'default' not in image_name_cover:
        if image_name_cover not in LIST_DEFAULT_IMAGES:
            file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_cover)
            if os.path.exists(file_path_c):
                try:
                    os.remove(file_path_c)
                except:
                    pass
    if 'default' not in image_name_thumbnail:
        if image_name_thumbnail not in LIST_DEFAULT_IMAGES:
            file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, image_name_thumbnail)
            if os.path.exists(file_path_t):
                try:
                    os.remove(file_path_t)
                except:
                    pass
    # Music 파일 삭제
    file_name_xxx = dict_music_album["source"]
    if file_name_xxx is not None:
        file_path_xxx = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_XXX, file_name_xxx)
        if os.path.exists(file_path_xxx):
            try:
                os.remove(file_path_xxx)
            except:
                pass


            
# Album 파일 삭제하기 함수
def delete_files_in_list_dict_xxx_album(q_xxx_album_selected, type_album, type_list, id_delete):
    print('################################################### Album 파일 삭제하기 함수')
    """ 
    q_xxx_album_selected: 선택한 앨범 쿼리
    type_album: 앨범 타입
    type_list: 수행할 List 종류, 'all' 이면 모두 삭제
    id_delete: 삭제할 아이템 ID, 'all' 이면 모두 삭제
    """
    print('q_xxx_album_selected', q_xxx_album_selected)
    print('album type', type_album)
    print('id_delete', id_delete)

    if id_delete != 'all':
        try:
            id_delete = int(id_delete)
        except:
            id_delete = None
    
    # 1 앨범에 등록된 cover 이미지 삭제하기
    if type_album == 'actor':
        RELATIVE_PATH_XXX = RELATIVE_PATH_ACTOR
        list_dict_profile_album = q_xxx_album_selected.list_dict_profile_album
        list_dict_picture_album = None
        list_dict_manga_album = None
        list_dict_video_album = None
        list_dict_music_album = None
        # print('list_dict_profile_album', list_dict_profile_album)
    elif type_album == 'picture':
        RELATIVE_PATH_XXX = RELATIVE_PATH_PICTURE
        list_dict_profile_album = None
        list_dict_picture_album = q_xxx_album_selected.list_dict_picture_album
        list_dict_manga_album = None
        list_dict_video_album = None
        list_dict_music_album = None
        # print('list_dict_picture_album', list_dict_picture_album)
    elif type_album == 'manga':
        RELATIVE_PATH_XXX = RELATIVE_PATH_MANGA
        list_dict_profile_album = None
        list_dict_picture_album = None
        list_dict_manga_album = q_xxx_album_selected.list_dict_manga_album
        list_dict_video_album = None
        list_dict_music_album = None
        # print('list_dict_manga_album', list_dict_manga_album)
    elif type_album == 'video':
        RELATIVE_PATH_XXX = RELATIVE_PATH_VIDEO
        list_dict_profile_album = None
        list_dict_picture_album = q_xxx_album_selected.list_dict_picture_album
        list_dict_manga_album = None
        list_dict_video_album = q_xxx_album_selected.list_dict_video_album
        list_dict_music_album = None
        print(f'list_dict_picture_album: {list_dict_picture_album} - 4')
        # print('list_dict_video_album', list_dict_video_album)
    elif type_album == 'music':
        RELATIVE_PATH_XXX = RELATIVE_PATH_MUSIC
        list_dict_profile_album = None
        list_dict_picture_album = q_xxx_album_selected.list_dict_picture_album
        list_dict_manga_album = None
        list_dict_video_album = None
        list_dict_music_album = q_xxx_album_selected.list_dict_music_album
        # print('list_dict_picture_album', list_dict_picture_album)
        # print('list_dict_music_album', list_dict_music_album)
    else:
        RELATIVE_PATH_XXX = None
        print('no path defined')

    if id_delete is not None:
        if RELATIVE_PATH_XXX is not None:
            # Actor 파일 제거
            if type_album == 'actor' and list_dict_profile_album is not None and len(list_dict_profile_album) > 1:
                if type_list == 'all' or type_list == 'profile':
                    for dict_profile_album in list_dict_profile_album:
                        print(dict_profile_album['id'])
                        if int(dict_profile_album["id"]) != 0:
                            if id_delete == 'all':
                                print('# Default 이미지가 아닌 경우 삭제')
                                delete_profile_item(dict_profile_album, RELATIVE_PATH_XXX)
                                # 리스트에서 discard 처리하기
                                dict_profile_album['active'] = 'false'
                                dict_profile_album['discard'] = 'true'
                            else:
                                if int(dict_profile_album["id"]) == id_delete:
                                    print('# 지정한 ID만 삭제')
                                    delete_profile_item(dict_profile_album, RELATIVE_PATH_XXX)
                                    # 리스트에서 discard 처리하기
                                    dict_profile_album['active'] = 'false'
                                    dict_profile_album['discard'] = 'true'
            # picture 파일 제거
            if list_dict_picture_album is not None and len(list_dict_picture_album) > 1:
                if type_list == 'all' or type_list == 'image':
                    for dict_picture_album in list_dict_picture_album :
                        print(dict_picture_album['id'])
                        if int(dict_picture_album["id"]) != 0:
                            if id_delete == 'all':
                                # Default 이미지가 아닌 경우 삭제
                                delete_picture_item(dict_picture_album, RELATIVE_PATH_XXX)
                                # 리스트에서 discard 처리하기
                                dict_picture_album['active'] = 'false'
                                dict_picture_album['discard'] = 'true'
                            else:
                                if int(dict_picture_album["id"]) == id_delete:
                                    # 지정한 ID만 삭제
                                    delete_picture_item(dict_picture_album, RELATIVE_PATH_XXX)
                                    # 리스트에서 discard 처리하기
                                    dict_picture_album['active'] = 'false'
                                    dict_picture_album['discard'] = 'true'
            # manga 파일 제거
            if list_dict_manga_album is not None and len(list_dict_manga_album) > 1:
                if type_list == 'all' or type_list == 'image':
                    for dict_manga_album in list_dict_manga_album :
                        print(dict_manga_album['id'])
                        if int(dict_manga_album["id"]) != 0:
                            if id_delete == 'all':
                                # Default 이미지가 아닌 경우 삭제
                                delete_manga_item(dict_manga_album, RELATIVE_PATH_XXX)
                                # 리스트에서 discard 처리하기
                                dict_manga_album['active'] = 'false'
                                dict_manga_album['discard'] = 'true'
                            else:
                                if int(dict_manga_album["id"]) == id_delete:
                                    # 지정한 ID만 삭제
                                    delete_manga_item(dict_manga_album, RELATIVE_PATH_XXX)
                                    # 리스트에서 discard 처리하기
                                    dict_manga_album['active'] = 'false'
                                    dict_manga_album['discard'] = 'true'
            # Video 파일 제거
            if list_dict_video_album is not None and len(list_dict_video_album) > 1:
                if type_list == 'all' or type_list == 'video':
                    for dict_video_album in list_dict_video_album :
                        print(dict_video_album['id'])
                        if int(dict_video_album["id"]) != 0:
                            if id_delete == 'all':
                                # Default 이미지가 아닌 경우 삭제
                                delete_video_item(dict_video_album, RELATIVE_PATH_XXX)
                                # 리스트에서 discard 처리하기
                                dict_video_album['active'] = 'false'
                                dict_video_album['discard'] = 'true'
                            else:
                                if int(dict_video_album["id"]) == id_delete:
                                    # 지정한 ID만 삭제
                                    delete_video_item(dict_video_album, RELATIVE_PATH_XXX)
                                    # 리스트에서 discard 처리하기
                                    dict_video_album['active'] = 'false'
                                    dict_video_album['discard'] = 'true'
            # Audio 파일 제거
            if list_dict_music_album is not None and len(list_dict_music_album) > 1:
                if type_list == 'all' or type_list == 'audio':
                    for dict_music_album in list_dict_music_album :
                        print(dict_music_album['id'])
                        if int(dict_music_album["id"]) != 0:
                            if id_delete == 'all':
                                delete_music_item(dict_music_album, RELATIVE_PATH_XXX)
                                # 리스트에서 discard 처리하기
                                dict_music_album['active'] = 'false'
                                dict_music_album['discard'] = 'true'
                            else:
                                if int(dict_music_album["id"]) == id_delete:
                                    # 지정한 ID만 삭제
                                    delete_music_item(dict_music_album, RELATIVE_PATH_XXX)
                                    # 리스트에서 discard 처리하기
                                    dict_music_album['active'] = 'false'
                                    dict_music_album['discard'] = 'true'

            
        # Active 최소 1개 유지, 마지막 이미지를 Activate시킨다. 모두 discard되었으면 default를 되살린다.
        if id_delete != 'all':
            if list_dict_profile_album is not None:
                count = sum(1 for d in list_dict_profile_album if d.get('active') == 'true')
                if count == 0:
                    for dict_profile_album in list_dict_profile_album[::-1]:
                        if dict_profile_album['discard'] == 'false':
                            dict_profile_album['active'] = 'true'
                            break
                        if dict_profile_album['id'] == 0:
                            dict_profile_album['active'] = 'true'
                            dict_profile_album['discard'] = 'false'
            if list_dict_picture_album is not None:
                count = sum(1 for d in list_dict_picture_album if d.get('active') == 'true')
                if count == 0:
                    for dict_picture_album in list_dict_picture_album[::-1]:
                        if dict_picture_album['discard'] == 'false':
                            dict_picture_album['active'] = 'true'
                            break
                        if dict_picture_album['id'] == 0:
                            dict_picture_album['active'] = 'true'
                            dict_picture_album['discard'] = 'false'
            if list_dict_manga_album is not None:
                count = sum(1 for d in list_dict_manga_album if d.get('active') == 'true')
                if count == 0:
                    for dict_manga_album in list_dict_manga_album[::-1]:
                        if dict_manga_album['discard'] == 'false':
                            dict_manga_album['active'] = 'true'
                            break
                        if dict_manga_album['id'] == 0:
                            dict_manga_album['active'] = 'true'
                            dict_manga_album['discard'] = 'false'
            if list_dict_music_album is not None:
                count = sum(1 for d in list_dict_music_album if d.get('active') == 'true')
                if count == 0:
                    for dict_music_album in list_dict_music_album[::-1]:
                        if dict_music_album['discard'] == 'false':
                            dict_music_album['active'] = 'true'
                            break
                        if dict_music_album['id'] == 0:
                            dict_music_album['active'] = 'true'
                            dict_music_album['discard'] = 'false'
                        
        # Query 저장 프로세스
        if type_album == 'actor':
            if id_delete == 'all':
                data = {
                    'list_dict_profile_album': list_dict_profile_album,
                    'check_discard': True,
                    }
            else:
                data = {
                    'list_dict_profile_album': list_dict_profile_album,
                    'check_discard': False,
                    }
            Actor.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
            # Actor 등록된 앨범에서 Actor 삭제
            qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_xxx_album_selected))
            qs_video_album = Video_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_xxx_album_selected))
            qs_music_album = Music_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_xxx_album_selected))
            if type_list == 'profile':
                pass
            elif type_list == 'all':
                data = {'main_actor': None}
                if qs_picture_album is not None and len(qs_picture_album) > 0:
                    for q_picture_album in qs_picture_album:
                        Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                if qs_video_album is not None and len(qs_video_album) > 0:
                    for q_video_album in qs_video_album:
                        Video_Album.objects.filter(id=q_video_album.id).update(**data)
                if qs_music_album is not None and len(qs_music_album) > 0:
                    for q_music_album in qs_music_album:
                        Music_Album.objects.filter(id=q_music_album.id).update(**data)
            else:
                pass
            
        elif type_album == 'picture':
            if id_delete == 'all':
                data = {
                    'list_dict_picture_album': list_dict_picture_album,
                    'check_discard': True,
                    }
            else:
                data = {
                    'list_dict_picture_album': list_dict_picture_album,
                    'check_discard': False,
                    }
            Picture_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        elif type_album == 'manga':
            if id_delete == 'all':
                data = {
                    'list_dict_manga_album': list_dict_manga_album,
                    'check_discard': True,
                    }
            else:
                data = {
                    'list_dict_manga_album': list_dict_manga_album,
                    'check_discard': False,
                    }
            Manga_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        elif type_album == 'video':
            if id_delete == 'all':
                data = {
                    'list_dict_picture_album': list_dict_picture_album,
                    'list_dict_video_album': list_dict_video_album,
                    'check_discard': True,
                    }
                print(f'list_dict_picture_album: {list_dict_picture_album} - 7')
            else:
                data = {
                    'list_dict_picture_album': list_dict_picture_album,
                    'list_dict_video_album': list_dict_video_album,
                    'check_discard': False,
                    }
                print(f'list_dict_picture_album: {list_dict_picture_album} - 8')
            Video_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        elif type_album == 'music':
            if id_delete == 'all':
                data = {
                    'list_dict_picture_album': list_dict_picture_album,
                    'list_dict_music_album': list_dict_music_album,
                    'check_discard': True,
                    }
            else:
                data = {
                    'list_dict_picture_album': list_dict_picture_album,
                    'list_dict_music_album': list_dict_music_album,
                    'check_discard': False,
                    }
            Music_Album.objects.filter(id=q_xxx_album_selected.id).update(**data)
            q_xxx_album_selected.refresh_from_db()
        else:
            print('no path defined')
    else:
        print('id_delete is not valid')
    return True
    

















