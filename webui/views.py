from django.shortcuts import render, redirect, reverse 
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, F, Func, Count
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Collate

from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import multiprocessing 
import time
import datetime 
import ast

import json
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view

from pdf2image import convert_from_path



from django.conf import settings
from webui.forms import user_register_form, user_update_form, profile_update_form
from webui.models import *
from webui.serializers import *
from webui.functions import *
from hans_ent.models import *
from hans_ent.functions import *
from hans_ent.tasks import *


from study.models import *
from study.functions import *
from study.tasks import *



#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Home
#
#############################################################################################################################################
#############################################################################################################################################

def create_user_settings(request):
    q_user = request.user
    print('q_user', q_user, type(q_user))
    q_mysettings_hansent = MySettings_HansEnt.objects.filter(Q(check_discard=False) & Q(user=q_user)).last()
    if q_mysettings_hansent is None:
        data = {'user':q_user}
        MySettings_HansEnt.objects.create(**data)
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(Q(check_discard=False)).last()
    if q_systemsettings_hansent is None:
        data = {}
        SystemSettings_HansEnt.objects.create(**data)

    q_mysettings_study = MySettings_Study.objects.filter(Q(check_discard=False) & Q(user=q_user)).last()
    if q_mysettings_study is None:
        data = {'user':q_user}
        MySettings_Study.objects.create(**data)
    q_systemsettings_study = SystemSettings_Study.objects.filter(Q(check_discard=False)).last()
    if q_systemsettings_study is None:
        data = {}
        SystemSettings_Study.objects.create(**data)

    q_authorization = Authorization.objects.filter(Q(check_discard=False) & Q(user=q_user)).last()
    if q_authorization is None:
        Authorization.objects.create(**data)

def f_check_authority(request, page_category):
    create_user_settings(request)
    q_user = request.user 
    list_allowed = q_user.authorization.list_allowed
    if page_category in list_allowed:
        return True 
    else:
        return False


@ensure_csrf_cookie
@require_http_methods(['GET'])
def set_csrf_token(request):
    """
    We set the CSRF cookie on the frontend.
    """
    return JsonResponse({'message': 'CSRF cookie set'})



@login_required
def index(request):
    page_category = 'home'
    # Storage check
    list_dict_stoage_status = storage_monitoring()
    

    template = 'home.html'
    context={
        'key1': 'Good!',
        'list_dict_stoage_status': list_dict_stoage_status,
    }
    return render(request, template, context)



#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Family
#
#############################################################################################################################################
#############################################################################################################################################

@login_required
def family(request):
    page_category = 'family'
    check_authority = f_check_authority(request, page_category)
    if check_authority:
        template = 'family.html'
    else:
        template = 'users/unauthorized.html'
    context={'key1': 'Good!'}
    return render(request, template, context)


#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Study
#
#############################################################################################################################################
#############################################################################################################################################

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def study(request):
    print("study VIEW")
    page_category = 'study'
    check_authority = f_check_authority(request, page_category)
    if check_authority:
        template = 'study.html'
        q_user = request.user
        create_user_settings(request)
        q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    else:
        q_mysettings_study = None
        template = 'users/unauthorized.html'

    context={
        'LIST_MENU_STUDY': LIST_MENU_STUDY,
        'q_mysettings_study': q_mysettings_study,
        }
    
    if request.method == 'GET':
        return render(request, template, context)
    
    if request.method == 'POST':
        menu_selected = request.POST.get('button-switch-study-home-menu')
        if menu_selected is not None:
            data = {
                'menu_selected': menu_selected
            }
            MySettings_Study.objects.filter(id=q_mysettings_study.id).update(**data)
        study_count_page_number_reset(q_mysettings_study)
        return redirect('study')


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def study_refresh_router(request):
    print('======================= study_refresh_router START')
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
   
    if request.method == 'GET':
        # selected_serialized_data_mysettings = Mysettings_Hans_Ent_Serializer(q_mysettings_hansent, many=False)
        menu_selected = q_mysettings_study.menu_selected
        jsondata = {
            # 'selected_serialized_data_mysettings': selected_serialized_data_mysettings,
            'menu_selected': menu_selected,
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)

    if request.method == 'POST':
        jsondata = {}
        return JsonResponse(jsondata, safe=False)






#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def study_mystudy(request):
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    
    if request.method == 'GET':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 

    if request.method == 'POST':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def study_conference(request):
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    
    if request.method == 'GET':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 

    if request.method == 'POST':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def study_paper(request):
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    study_type = 'paper'

    if request.method == 'GET':
        print('study_paper GET')
        list_serialized_data_paper_searched = []
        list_serializsed_data_paper_voronoi = []
        list_serializsed_data_paper_bookmarked = []
        serialized_data_paper_searched = {}
        serialized_data_mysettings_study = {}

        q_paper_search_selected = q_mysettings_study.paper_search_selected
        print('q_paper_search_selected', q_paper_search_selected)
        qs_paper_search_mine = Paper_Search_Google_and_PubMed.objects.filter(Q(user=q_user)).order_by('id')[:10]
        
        # Data Serialization
        if q_paper_search_selected is not None:
            print('q_paper_search_selected id:', q_paper_search_selected.id)
            serialized_data_paper_searched = Paper_Search_Google_and_PubMed_Serializer(q_paper_search_selected, many=False).data
        else:
            print('# q_paper_search_selected is None')
            # voronoi DB 
            qs_paper_voronoi = Paper.objects.filter(Q(check_discard=False) & Q(title__isnull=False)).order_by('-id')[:100]
            if qs_paper_voronoi is not None and len(qs_paper_voronoi) > 0:
                list_serializsed_data_paper_voronoi = List_Paper_Serializer(qs_paper_voronoi, many=True).data 
            print('len(list_serializsed_data_paper_voronoi)', len(list_serializsed_data_paper_voronoi))
            # my favorite DB
            list_bookmarked_paper_id = q_mysettings_study.list_bookmarked_paper_id
            if list_bookmarked_paper_id is not None and len(list_bookmarked_paper_id) > 0:
                qs_paper_bookmarked = Paper.objects.filter(id__in=list_bookmarked_paper_id)
                if qs_paper_bookmarked is not None and len(qs_paper_bookmarked) > 0:
                    list_serializsed_data_paper_bookmarked = List_Paper_Serializer(qs_paper_bookmarked, many=True).data 
            print('len(list_serializsed_data_paper_bookmarked)', len(list_serializsed_data_paper_bookmarked))

        if qs_paper_search_mine is not None and len(qs_paper_search_mine) > 0:
            list_serialized_data_paper_searched_mine = Paper_Search_Google_and_PubMed_Mine_Serializer(qs_paper_search_mine, many=True).data

        serialized_data_mysettings_study = MySettings_Study_Serializer(q_mysettings_study, many=False).data
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!  list_dict_paper_info_from_voronoi_db', serialized_data_paper_searched)
        jsondata = {
            'LIST_TABS_SEARCHED_PAPER': LIST_TABS_SEARCHED_PAPER,
            'LIST_TABS_COLLECTED_PAPER': LIST_TABS_COLLECTED_PAPER,
            'BASE_URL_PUBMED_FREE': BASE_URL_PUBMED_FREE,
            'BASE_URL_PUBMED': BASE_URL_PUBMED,
            'BASE_URL_GOOGLE_SCHOLAR': BASE_URL_GOOGLE_SCHOLAR,
            'BASE_URL_DOI': BASE_URL_DOI,
            'BASE_URL_SCI_HUB': BASE_URL_SCI_HUB,
            'BASE_URL_PLOS': BASE_URL_PLOS,
            'BASE_DIR_STUDY': BASE_DIR_STUDY,
            'BASE_DIR_STUDY_PAPER': BASE_DIR_STUDY_PAPER,
            'BASE_DIR_STUDY_PAPER_SCREENSHOT': BASE_DIR_STUDY_PAPER_SCREENSHOT,

            'serialized_data_paper_searched': serialized_data_paper_searched,
            'list_serialized_data_paper_searched_mine': list_serialized_data_paper_searched_mine,
            'list_serializsed_data_paper_voronoi': list_serializsed_data_paper_voronoi,
            'list_serializsed_data_paper_bookmarked': list_serializsed_data_paper_bookmarked,
            'serialized_data_mysettings_study': serialized_data_mysettings_study,
        }
        # print('serialized_data_paper_searched: ', serialized_data_paper_searched)
        return JsonResponse(jsondata, safe=False) 

    if request.method == 'POST':
        print('study_paper POST')
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 







"""
키워드(논문제목)로 구글 검색 한 뒤 검색과 연결된 논문을 찾아서 정보 수집하고 리스트를 보여줌
리스트에서 사용자는 자신이 찾고자 하는 논문을 1개 선택함
선택한 논문과 관련된 추가적인 레퍼런스 논문들을 수집함
수집한 논문을 리스트로 선택논문 아래에 다시 다운받을수 있도록 보여주고
수집한 레퍼런스 논문 자료를 GPT 모델에 학습시키고 기본적인 질문을 던져서 답변을 받아 리스트 하단에 질문:답변 리스트를 보여줌
추가질문을 받을 수 있는 입력창 및 비슷한 추천논문 링크 표시

PatCID: an open-access dataset of chemical structures in patent documents

"""

@login_required 
def study_paper_search_form(request):
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    study_type = 'paper'
    
    if request.method == 'GET':
        print('study_paper_search_form GET =========================================================================== 1')
        print(request.GET,)
        print('======================================================================================================= 2')
        
        random_sec = random.uniform(1, 2)
        
        list_selected_options_paper_search = q_mysettings_study.list_selected_options_paper_search
        if list_selected_options_paper_search is None:
            list_selected_options_paper_search = []
        print('list_selected_options_paper_search', list_selected_options_paper_search)

        
        serialized_data_paper_searched = {}
        list_dict_paper_info_from_pubmed = []
        list_dict_paper_info_from_google = []
        list_serializsed_data_paper_voronoi = []
        list_serializsed_data_paper_bookmarked = []
        
        q_paper_search = None
        keyword = None 
        keyword_ordered = None
        list_keyword = []
        list_keyword_ordered = []

        keyword_str = request.GET.get('keyword')
        keyword_str = None if keyword_str in LIST_STR_NONE_SERIES else keyword_str
        
        if keyword_str is not None:
            keyword_str = keyword_str.strip()
            keyword_str = keyword_str.lower()
            keyword = file_name_cleaner_for_keywords(keyword_str)
            if keyword is not None:
                list_keyword = keyword.split(' ')
                list_keyword_ordered = sorted(list_keyword)
                # Combine all items with a single space
                keyword_ordered = ' '.join(list_keyword_ordered)
        print('keyword', keyword)
        print('keyword_ordered', keyword_ordered)

        # 1. 키워드(논문 제목) 활용, PubMed / 구글에서 관련 사이트 정보 획득
        if keyword is not None:
            q_paper_search = Paper_Search_Google_and_PubMed.objects.filter(keyword_ordered=keyword_ordered).last()
            if q_paper_search is None:
                # 키워드 입력 단어가 1개인 경우
                q_paper_search = Paper_Search_Google_and_PubMed.objects.filter(keyword=keyword).last()
            print('검색된 q_paper_search', q_paper_search)
            

            if q_paper_search is None:
                print('# 1-1. 키워드 저장 및 검색 쿼리 생성')
                data = {
                    'user': request.user,
                    'keyword': keyword,
                    'keyword_ordered': keyword_ordered,
                    'list_selected_search_options': list_selected_options_paper_search,
                }
                q_paper_search = Paper_Search_Google_and_PubMed.objects.create(**data)
            else:
                print('# 1-2. 키워드 저장 및 검색 쿼리 업데이트')
                data = {
                    'user': request.user,
                    'keyword': keyword,
                    'keyword_ordered': keyword_ordered,
                    'list_selected_search_options': list_selected_options_paper_search,
                }
                Paper_Search_Google_and_PubMed.objects.filter(id=q_paper_search.id).update(**data)
                q_paper_search.refresh_from_db()
            print('신규 생성한 q_paper_search', q_paper_search)
            
            """
            LIST_TABS_SEARCHED_PAPER = 
            [
                'Pubmed', 
                'Google Scholar', 
                'Voronoi DB',
                'My Favorite',
            ]
            """

            #--------------------------------------------------------------------------------------------------------------------------------------
            # Pubmed
            if LIST_TABS_SEARCHED_PAPER[0] in list_selected_options_paper_search or 'all' in list_selected_options_paper_search:
                print('# Pubmed 검색')
                list_dict_paper_info_from_pubmed = q_paper_search.list_dict_paper_info_from_pubmed
                if list_dict_paper_info_from_pubmed is not None and len(list_dict_paper_info_from_pubmed) > 0:
                    print('# 2. 키워드 활용, PubMed Free(PMC)에서 검색 정보 획득 A-1 : 완료')
                    # paper_keyword_search_on_pubmed.delay(q_paper_search.id, keyword)
                    pass
                else:
                    print('# 2. 키워드 활용, PubMed Free(PMC)에서 검색 정보 획득 A-1 : 시작')
                    paper_keyword_search_on_pubmed.delay(q_paper_search.id, keyword)
            else:
                print(f'{LIST_TABS_SEARCHED_PAPER[0]}을 검색옵션으로 선택하지 않았습니다.')

            #--------------------------------------------------------------------------------------------------------------------------------------
            # Google Scholar
            if LIST_TABS_SEARCHED_PAPER[1] in list_selected_options_paper_search or 'all' in list_selected_options_paper_search:
                print('# Google Scholar 검색')
                list_dict_paper_info_from_google = q_paper_search.list_dict_paper_info_from_google
                if list_dict_paper_info_from_google is not None and len(list_dict_paper_info_from_google) > 0:
                    print('# 3. 키워드 활용, Google Scholar에서 검색 정보 획득 A-2 : 완료')
                    # paper_keyword_search_on_google_scholar.delay(q_paper_search.id, keyword)
                    pass
                else:
                    print('# 3. 키워드 활용, Google Scholar에서 검색 정보 획득 A-2 : 시작')
                    paper_keyword_search_on_google_scholar.delay(q_paper_search.id, keyword)
            else:
                print(f'{LIST_TABS_SEARCHED_PAPER[1]}을 검색옵션으로 선택하지 않았습니다.')

            #--------------------------------------------------------------------------------------------------------------------------------------
            # Voronoi DB
            if LIST_TABS_SEARCHED_PAPER[2] in list_selected_options_paper_search or 'all' in list_selected_options_paper_search:            
                print('# Voronoi DB 검색')
                qs_paper_searched = Paper.objects.filter(Q(doi=keyword) | Q(doi_url=keyword))
                if qs_paper_searched is None or len(qs_paper_searched) == 0:
                    print('# DOI 결과가 없으면 Title 검색')
                    if list_keyword_ordered is not None and len(list_keyword_ordered) > 0:
                        list_dict_searched_paper_id_score = []
                        list_dict_searched_paper_id_score_sorted = []
                        for item in list_keyword_ordered:
                            qs_paper_searched = Paper.objects.filter(Q(title__icontains=item))
                            if qs_paper_searched is not None and len(qs_paper_searched) > 0:
                                for q_paper_searched in qs_paper_searched:
                                    check_matched_id = False
                                    for dict_searched_paper_id_score in list_dict_searched_paper_id_score:
                                        if dict_searched_paper_id_score['id'] == q_paper_searched.id:
                                            check_matched_id = True 
                                    if check_matched_id == True:
                                        current_score = dict_searched_paper_id_score['score']
                                        added_score = current_score + 1
                                        dict_searched_paper_id_score['score'] = added_score
                                    else:
                                        list_dict_searched_paper_id_score.append({'id': q_paper_searched.id, 'score': 1 })
                        print(f' 검색스코어 결과 개수: {len(list_dict_searched_paper_id_score)}')
                        if len(list_dict_searched_paper_id_score) > 0:
                            print('# Title 결과값이 있으면 높은 스코어 우선으로 정렬')
                            list_dict_searched_paper_id_score_sorted = sorted(list_dict_searched_paper_id_score, key=lambda x: x['score'], reverse=True)
                    if len(list_dict_searched_paper_id_score_sorted) > 0:
                        print('Data Seiralization w/ score sorted')
                        i = 0
                        for dict_searched_paper_id_score_sorted in list_dict_searched_paper_id_score_sorted:
                            paper_id_score_sorted = dict_searched_paper_id_score_sorted['id']
                            q_paper_score_sorted = Paper.objects.get(id=paper_id_score_sorted)
                            data = {
                                'id': q_paper_score_sorted.id,
                                'title': q_paper_score_sorted.title,
                                'doi': q_paper_score_sorted.doi,
                                'pmcid': q_paper_score_sorted.pmcid,
                                'first_author_name': q_paper_score_sorted.first_author_name,
                                'first_author_url': q_paper_score_sorted.first_author_url,
                                'file_path_xml': q_paper_score_sorted.file_path_xml,
                                'file_path_pdf': q_paper_score_sorted.file_path_pdf,
                                # 'dict_paper_info': q_paper_score_sorted.dict_paper_info,
                                'publication_year': q_paper_score_sorted.publication_year,
                                'doi_url': q_paper_score_sorted.doi_url,
                                'article_url': q_paper_score_sorted.article_url,
                                'pdf_url': q_paper_score_sorted.pdf_url,
                            }
                            list_serializsed_data_paper_voronoi.append(data)
                            # if i == 3:
                            #     break
                            i = i + 1
                # Data serialization    
                if len(list_serializsed_data_paper_voronoi) == 0:
                    print('Data Seiralization Normal')
                    if qs_paper_searched is not None and len(qs_paper_searched) > 0:
                        list_serializsed_data_paper_voronoi = List_Paper_Serializer(qs_paper_searched, many=True).data 
                print(f'# 4. 키워드 활용, Voronoi DB 검색 정보 획득: {len(qs_paper_searched)}')
                data = {
                    'list_dict_paper_info_from_voronoi_db': list_serializsed_data_paper_voronoi,
                }
                Paper_Search_Google_and_PubMed.objects.filter(id=q_paper_search.id).update(**data)
                q_paper_search.refresh_from_db()

                # jsondata = {
                #     'list_serializsed_data_paper_voronoi': list_serializsed_data_paper_voronoi,
                # }
                # return JsonResponse(jsondata, safe=False) 
            else:
                print(f'{LIST_TABS_SEARCHED_PAPER[2]}을 검색옵션으로 선택하지 않았습니다.')

            #--------------------------------------------------------------------------------------------------------------------------------------
            # My Favorite
            if LIST_TABS_SEARCHED_PAPER[3] in list_selected_options_paper_search or 'all' in list_selected_options_paper_search:
                print('# My Favorite 검색')
                list_bookmarked_paper_id = q_mysettings_study.list_bookmarked_paper_id
                if list_bookmarked_paper_id is not None and len(list_bookmarked_paper_id) > 0:
                    qs_paper_searched = Paper.objects.filter(Q(id__in=list_bookmarked_paper_id) & (Q(doi=keyword) | Q(doi_url=keyword)))
                    if qs_paper_searched is None:
                        qs_paper_searched = Paper.objects.filter(Q(id__in=list_bookmarked_paper_id) & Q(title__icontains=keyword))
                    if qs_paper_searched is not None and len(qs_paper_searched) > 0:
                        list_serializsed_data_paper_bookmarked = List_Paper_Serializer(qs_paper_searched, many=True).data 
                print(f'# 5. 키워드 활용, My Favorite 검색 정보 획득: {len(qs_paper_searched)}')
                data = {
                    'list_dict_paper_info_from_my_favorite': list_serializsed_data_paper_bookmarked,
                }
                Paper_Search_Google_and_PubMed.objects.filter(id=q_paper_search.id).update(**data)
                q_paper_search.refresh_from_db()
            else:
                print(f'{LIST_TABS_SEARCHED_PAPER[3]}을 검색옵션으로 선택하지 않았습니다.')

            #--------------------------------------------------------------------------------------------------------------------------------------
            

        if q_paper_search is not None:
            print('저장하는 q_paper_search', q_paper_search.id)
            data = {
                'paper_search_selected':q_paper_search,
            }
            MySettings_Study.objects.filter(id=q_mysettings_study.id).update(**data)
        
        # # Jsondata 패키지 (refresh하여 study_paper 로부터 dataset을 가져감)
        jsondata = {
            # 'list_serializsed_data_paper_voronoi': list_serializsed_data_paper_voronoi,
            # 'list_serializsed_data_paper_bookmarked': list_serializsed_data_paper_bookmarked,
        }
        return JsonResponse(jsondata, safe=False) 
        

    if request.method == 'POST':
        print('study_paper_search_form POST =========================================================================== 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        serialized_data_mysettings_study = {}
        list_dict_paper_info_from_etc = []

        if request.POST.get('button') == 'test':
            print('test button excuted!')
            file_extension = 'pdf'
            qs_paper = Paper.objects.filter(check_discard=False)
            
            if qs_paper is not None and len(qs_paper) > 0:
                num_paper = len(qs_paper)
                for q_paper in qs_paper:
                    print('num_paper', num_paper)
                    hashcode = q_paper.hashcode
                    pdf_name = f'paper-{hashcode}.{file_extension}'
                    file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER, pdf_name)
                    if os.path.exists(file_path):
                        data = {
                            'file_path_pdf':pdf_name,
                            'check_download_pdf': True,
                        }
                        Paper.objects.filter(id=q_paper.id).update(**data)
                        print('updated!!')
                    num_paper = num_paper - 1
            # # input_text = ' Galantamine Is Not a Positive Allosteric Modulator' 
            # input_text = 'Fully Oxygen-Tolerant Polymerization'
            # qs_paper_test = Paper.objects.filter(title__icontains=input_text)
            # print('len(qs_paper_test)', len(qs_paper_test))
            # if qs_paper_test is not None and len(qs_paper_test) > 0:
            #     for q_paper_test in qs_paper_test:
            #         print(q_paper_test.id)

            # doi = '10.5966/sctm.2012-0106'
            # qs_paper_test = Paper.objects.filter(doi=doi)
            # print('len(qs_paper_test)', len(qs_paper_test))
            # if qs_paper_test is not None and len(qs_paper_test) > 0:
            #     for q_paper_test in qs_paper_test:
            #         print(q_paper_test.id)
            
            # # id_selected = 2089
            # id_selected = 3129
            # q_paper_test_selected = Paper.objects.get(id=2089)
            # # list_dict_xxx_paper = q_paper_test_selected.list_dict_reference_paper
            # # print('list_dict_reference_paper', len(list_dict_xxx_paper))
            # list_dict_xxx_paper = q_paper_test_selected.list_dict_relevant_paper
            # print('list_dict_relevant_paper', len(list_dict_xxx_paper))

            # list_doi_count = []
            # list_paper_doi_count = []
            # list_paper_doi_pdf_count = []
            # for dict_xxx_paper in list_dict_xxx_paper:
            #     doi = dict_xxx_paper['doi']
            #     pubmed_url = dict_xxx_paper['pubmed_url']
            #     # print('doi', doi)
            #     if doi != None:
            #         list_doi_count.append(doi) 
            #         q_paper_doi = Paper.objects.filter(doi=doi).last()
            #         if q_paper_doi is not None:
            #             list_paper_doi_count.append(q_paper_doi.id)
            #             if q_paper_doi.check_download_pdf == True:
            #                 list_paper_doi_pdf_count.append(True)

            # print('list_dict_xxx_paper에 doi 정보가 있는 경우 : ', len(list_doi_count))
            # print('있는 doi로 매칭된 Paper 쿼리 개수 : ', len(list_paper_doi_count))
            # print('매칭된 쿼리 paper에 pdf download True 경우: ', len(list_paper_doi_pdf_count))

            # # list_xxx_paper_id = q_paper_test_selected.list_reference_paper_id
            # list_xxx_paper_id = q_paper_test_selected.list_relevant_paper_id
            # qs_paper_id_in = Paper.objects.filter(id__in=list_xxx_paper_id)
            # print('list_paper_id로 매칭된 paper 쿼리 개수: ', len(qs_paper_id_in))
            # list_paper_id_matched_id = []
            # if qs_paper_id_in is not None and len(qs_paper_id_in) > 0:
            #     for q_paper_id_in in qs_paper_id_in:
            #         # print(q_paper_id_in.doi)
            #         if q_paper_id_in.doi is not None:
            #             list_paper_id_matched_id.append(q_paper_id_in.id)

            # list_duplicated_items = list(set(list_paper_doi_count) & set(list_paper_id_matched_id))
            # list_difference_doi = [item for item in list_paper_doi_count if item not in list_paper_id_matched_id]
            # list_difference_id = [item for item in list_paper_id_matched_id if item not in list_paper_doi_count]

            # print('있는 doi로 매칭된 Paper id : ', list_paper_doi_count)
            # print('list_paper_id로 매칭된 paper id: ', list_paper_id_matched_id)
            # print('list_duplicated_items', list_duplicated_items)
            # print('list_difference_doi', list_difference_doi)
            # print('list_difference_id', list_difference_id)

            # q_paper_selected_for_test = Paper.objects.get(id=2093)
            # list_dict_reference_paper = q_paper_selected_for_test.list_dict_reference_paper
            # list_dict_relevant_paper = q_paper_selected_for_test.list_dict_relevant_paper
            # print('len(list_dict_reference_paper)', len(list_dict_reference_paper))
            # print('len(list_dict_relevant_paper)', len(list_dict_relevant_paper))

            # list_reference_paper_id = q_paper_selected_for_test.list_reference_paper_id
            # list_relevant_paper_id = q_paper_selected_for_test.list_relevant_paper_id
            # print('len(list_reference_paper_id)', len(list_reference_paper_id))
            # print('len(list_relevant_paper_id)', len(list_relevant_paper_id))

            # list_duplicated_items = list(set(list_reference_paper_id) & set(list_relevant_paper_id))
            # list_difference_ref = [item for item in list_reference_paper_id if item not in list_relevant_paper_id]
            # list_difference_rel = [item for item in list_relevant_paper_id if item not in list_reference_paper_id]
            # print('list_duplicated_items', list_duplicated_items)
            # print('list_difference_ref', list_difference_ref)
            # print('list_difference_rel', list_difference_rel)


        if request.POST.get('button') == 'search_paper_checkbox_update':
            list_selected_options_paper_search = request.POST.getlist('list_selected_options_paper_search[]')
            selected_option_paper_search = request.POST.get('selected_option_paper_search')
            print('list_selected_options_paper_search', list_selected_options_paper_search)
            print('selected_option_paper_search', selected_option_paper_search)
            if len(list_selected_options_paper_search) > 1:
                if 'all' in list_selected_options_paper_search:
                    if selected_option_paper_search == 'all':
                        list_selected_options_paper_search = ['all']
                    else:
                        list_selected_options_paper_search.remove('all')
            data = {
                'list_selected_options_paper_search': list_selected_options_paper_search
            }
            MySettings_Study.objects.filter(id=q_mysettings_study.id).update(**data)
            q_mysettings_study.refresh_from_db()


        if request.POST.get('button') == 'set_active_tab_searched_paper':
            active_tab_searched_paper_str = request.POST.get('active_tab_searched_paper')
            active_tab_searched_paper_str = None if active_tab_searched_paper_str in LIST_STR_NONE_SERIES else active_tab_searched_paper_str
            print('active_tab_searched_paper_str', active_tab_searched_paper_str)
            if active_tab_searched_paper_str is not None:
                data = {
                    'active_tab_searched_paper': active_tab_searched_paper_str
                }
                MySettings_Study.objects.filter(id=q_mysettings_study.id).update(**data)
                q_mysettings_study.refresh_from_db()

        
        if request.POST.get('button') == 'reset_search_result':
            data = {
                'paper_search_selected': None,
            }
            MySettings_Study.objects.filter(id=q_mysettings_study.id).update(**data)
            q_mysettings_study.refresh_from_db()
            
        if request.POST.get('button') == 'search_history_select':
            paper_search_google_id_str = request.POST.get('paper_search_google_id')
            paper_search_google_id_str = None if paper_search_google_id_str in LIST_STR_NONE_SERIES else paper_search_google_id_str

            if paper_search_google_id_str is not None:
                print('paper_search_google_id_str', paper_search_google_id_str)
                paper_search_google_id = int(paper_search_google_id_str)
                q_paper_search_google = Paper_Search_Google_and_PubMed.objects.get(id=paper_search_google_id)
                data = {
                    'paper_search_selected': q_paper_search_google,
                }
                MySettings_Study.objects.filter(id=q_mysettings_study.id).update(**data)

        # 4. 사용자가 추출한 PDF 정보 리스트 중 택 1 하면 관련 Paper 내용 다운로드 저장
        if request.POST.get('button') == 'select_paper_site':

            if len(list_dict_paper_info_from_etc) > 0:
                # Paper 쿼리 생성하기 ################################################################
                q_paper = create_paper()
                hashcode = q_paper.hashcode
                data = {
                    'list_dict_paper_info_from_etc': list_dict_paper_info_from_etc,
                }
                Paper.objects.filter(id=q_paper.id).update(**data)
                q_paper.refresh_from_db()

            if q_paper is not None:
                file_extension = 'pdf'
                paper_name = f'{hashcode}-pdf-{n}.{file_extension}'
                
                file_path_paper = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER, paper_name)
                
                # File 저장하기 ######################################################################
                # Send an HTTP GET request to the URL
                try:
                    response = requests.get(pdf_url)

                    # Check if the request was successful
                    if response.status_code == 200:
                        # Open the file in write-binary mode
                        with open(file_path_paper, "wb") as f:
                            f.write(response.content)
                        print("PDF downloaded successfully!")
                    else:
                        print(f"Failed to download the PDF. Status code: {response.status_code}")
                except:
                    pass

        serialized_data_mysettings_study = MySettings_Study_Serializer(q_mysettings_study, many=False).data
        jsondata = {
            'serialized_data_mysettings_study': serialized_data_mysettings_study,
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False) 
    

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required 
def study_paper_selected_paper_data_collection(request):
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    study_type = 'paper'
    
    if request.method == 'GET':
        print('study_paper_selected_paper_data_collection GET =========================================================================== 1')
        print(request.GET,)
        print('======================================================================================================= 2')
        # Jsondata 패키지
        jsondata = {
            'message': 'hi'
            # 'serialized_data_paper_searched': serialized_data_paper_searched,
            # 'serialized_data_mysettings_study': serialized_data_mysettings_study,
        }
        print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False) 
   
    if request.method == 'POST':
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
        print('study_paper_selected_paper_data_collection GET =========================================================================== 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        serialized_data_paper = {}
        serialized_data_paper_searched = {}
        serialized_data_paper_searched_selected = {}
        list_serialized_data_paper_reference = []
        list_serialized_data_paper_author = []
        list_serialized_data_paper_relevant = []

        check_selected_paper_bookmarked = False 
        q_paper_selected = None 
        q_paper_search_google_pubmed = None


        
        selected_data_paper_id_str = request.POST.get('selected_data_paper_id') # Paper 테이블 쿼리 ID
        selected_data_paper_searched_id_str = request.POST.get('selected_data_paper_searched_id') # Paper_Search_Google_and_PubMed 테이블 쿼리 ID
        selected_data_paper_searched_selected_id_str = request.POST.get('selected_data_paper_searched_selected_id') # 검색한 Paper_Search_Google_and_PubMed에서 선택한 Paper ID
        
        selected_data_paper_id_str = None if selected_data_paper_id_str in LIST_STR_NONE_SERIES else selected_data_paper_id_str
        selected_data_paper_searched_id_str = None if selected_data_paper_searched_id_str in LIST_STR_NONE_SERIES else selected_data_paper_searched_id_str
        selected_data_paper_searched_selected_id_str = None if selected_data_paper_searched_selected_id_str in LIST_STR_NONE_SERIES else selected_data_paper_searched_selected_id_str

        print('selected_data_paper_id_str', selected_data_paper_id_str)
        print('selected_data_paper_searched_id_str', selected_data_paper_searched_id_str)
        print('selected_data_paper_searched_selected_id_str', selected_data_paper_searched_selected_id_str)


        if selected_data_paper_id_str is not None:
            selected_data_paper_id = int(selected_data_paper_id_str)
            try:
                q_paper_selected = Paper.objects.get(id=selected_data_paper_id)
            except:
                q_paper_selected = None
        else:
            q_paper_selected = None
        print('1. q_paper_selected : ', q_paper_selected)
        

        if selected_data_paper_searched_id_str is not None:
            selected_data_paper_searched_id = int(selected_data_paper_searched_id_str)
            try:
                q_paper_search_google_pubmed = Paper_Search_Google_and_PubMed.objects.get(id=selected_data_paper_searched_id)
            except:
                q_paper_search_google_pubmed = None
        print('2. q_paper_search_google_pubmed ', q_paper_search_google_pubmed)
        

        if selected_data_paper_searched_selected_id_str is not None: 
            selected_data_paper_searched_selected_id = int(selected_data_paper_searched_selected_id_str)
        else:
            selected_data_paper_searched_selected_id = None
        print('3. selected_data_paper_searched_selected_id', selected_data_paper_searched_selected_id)
                
        # Pubmed에서 Data Parsing 하면서 모달창 열기
        if request.POST.get('button') == 'pubmed':
            print('# 4. pubmed 서치 결과 리스트에서 선택한 논문 데이터 수집 시작')
            # pubmed 서치 결과 리스트에서 선택한 논문 데이터 수집 시작
            if q_paper_search_google_pubmed is not None:
                list_dict_paper_info_from_pubmed = q_paper_search_google_pubmed.list_dict_paper_info_from_pubmed
                if list_dict_paper_info_from_pubmed is not None and len(list_dict_paper_info_from_pubmed) > 0 and selected_data_paper_searched_selected_id is not None:
                    for dict_paper_info_from_pubmed in list_dict_paper_info_from_pubmed:
                        if dict_paper_info_from_pubmed['id'] == selected_data_paper_searched_selected_id:
                            print(dict_paper_info_from_pubmed['id'])
                            try:
                                article_url = dict_paper_info_from_pubmed['article_url']
                            except:
                                article_url = None 
                            try:
                                doi = dict_paper_info_from_pubmed['doi']
                            except:
                                doi = None 
                            try:
                                pmcid = dict_paper_info_from_pubmed['pmcid']
                            except:
                                pmcid = None 
                            try:
                                title = dict_paper_info_from_pubmed['title']
                            except:
                                title = None
                            print(article_url, doi, pmcid, title)

                            if doi is not None:
                                q_paper_selected = Paper.objects.filter(doi=doi).last()
                                if q_paper_selected is None:
                                    if pmcid is not None:
                                        q_paper_selected = Paper.objects.filter(pmcid=pmcid).last()
                                        if q_paper_selected is None:
                                            if title is not None:
                                                q_paper_selected = Paper.objects.filter(title=title).last()
                                            else:
                                                q_paper_selected = None

                            dict_paper_info_from_pubmed['check_parsing'] = True
                            # dict_paper_info_from_pubmed['check_parsing'] = False
                            data = {
                                'list_dict_paper_info_from_pubmed': list_dict_paper_info_from_pubmed
                            }
                            Paper_Search_Google_and_PubMed.objects.filter(id=q_paper_search_google_pubmed.id).update(**data)
                            print('end update pubmed')
                                    
            print('//////////////////////////////// 1 q_paper', q_paper_selected)
            if q_paper_selected is not None:
                q_paper_id = q_paper_selected.id
                try:
                    pmcid = q_paper_selected.pmcid
                except:
                    pmcid = None 
                try:
                    doi = q_paper_selected.doi
                except:
                    doi = None 
                if pmcid is not None:
                    try:
                        article_url = f'{BASE_URL_PUBMED_FREE}/articles/{pmcid}'
                    except:
                        article_url = None
                else:
                    article_url = None
            else:
                q_paper_id = None
            if article_url is not None and q_paper_id is not None:
                # background task로 선택한 paper의 Reference 정보 수집하기
                parsing_selected_paper_detail_info_on_pubmed.delay(article_url, doi, pmcid, q_paper_id)
            

        # Google Scholar에서 Data Parsing 하면서 모달창 열기(다양한 곳에서 Parsing 해야 함)
        if request.POST.get('button') == 'google':
            print('# 5. google에서 선택한 논문 데이터 수집 시작')
            # google에서 선택한 논문 데이터 수집 시작
            if q_paper_search_google_pubmed is not None:
                list_dict_paper_info_from_google = q_paper_search_google_pubmed.list_dict_paper_info_from_google
                if list_dict_paper_info_from_google is not None and len(list_dict_paper_info_from_google) > 0 and selected_data_paper_searched_selected_id is not None:
                    for dict_paper_info_from_google in list_dict_paper_info_from_google:
                        if dict_paper_info_from_google['id'] == selected_data_paper_searched_selected_id:
                            print(dict_paper_info_from_google['id'])
                            try:
                                hashcode = dict_paper_info_from_google['hashcode']
                            except:
                                hashcode = None 
                            if hashcode is not None:
                                q_paper_selected = Paper.objects.filter(hashcode=hashcode).last()
                            else:
                                q_paper_selected = None 
                            if q_paper_selected is not None:
                                q_paper_id = q_paper_selected.id
                            else:
                                q_paper_id = None
                            # background task로 선택한 paper의 Reference 정보 수집하기
                            parsing_selected_paper_detail_info_on_google_scholar.delay(q_paper_id)
                            
                            dict_paper_info_from_google['check_parsing'] = True
                            data = {
                                'list_dict_paper_info_from_google': list_dict_paper_info_from_google
                            }
                            Paper_Search_Google_and_PubMed.objects.filter(id=q_paper_search_google_pubmed.id).update(**data)
                            print('end update pubmed')


        # 선택한 Paper 모달창 Data update 하기
        if request.POST.get('button') == 'update_paper_id':
            
            print('# 6-1. 추가 정보 paper ID 리스트 업')
            if q_paper_search_google_pubmed is not None:
                serialized_data_paper_searched = Paper_Search_Google_and_PubMed_Serializer(q_paper_search_google_pubmed, many=False).data
                list_dict_paper_info_from_pubmed = q_paper_search_google_pubmed.list_dict_paper_info_from_pubmed
                if list_dict_paper_info_from_pubmed is not None and len(list_dict_paper_info_from_pubmed) > 0 and selected_data_paper_searched_selected_id is not None:
                    for dict_paper_info_from_pubmed in list_dict_paper_info_from_pubmed:
                        if dict_paper_info_from_pubmed['id'] == selected_data_paper_searched_selected_id:
                            try:
                                ss_doi = dict_paper_info_from_pubmed["doi"]
                            except:
                                ss_doi = None
                            try:
                                ss_pmcid = dict_paper_info_from_pubmed["pmcid"]
                            except:
                                ss_pmcid = None
                            try:
                                ss_title = dict_paper_info_from_pubmed["title"]
                            except:
                                ss_title = None
                            
                            if ss_doi is not None:
                                q_paper_selected = Paper.objects.filter(doi=ss_doi).last()
                                if q_paper_selected is None:
                                    if ss_pmcid is not None:
                                        q_paper_selected = Paper.objects.filter(pmcid=ss_pmcid).last()
                                        if q_paper_selected is None:
                                            if ss_title is not None:
                                                q_paper_selected = Paper.objects.filter(title=ss_title).last()
                                            else:
                                                q_paper_selected = None
                
            print('# 6-2. q_paper_selected :', q_paper_selected)
            if q_paper_selected is not None:
                list_reference_paper_id = q_paper_selected.list_reference_paper_id
                if list_reference_paper_id is None:
                    list_reference_paper_id = []
                list_author_paper_id = q_paper_selected.list_author_paper_id
                if list_author_paper_id is None:
                    list_author_paper_id = []
                list_relevant_paper_id = q_paper_selected.list_relevant_paper_id
                if list_relevant_paper_id is None:
                    list_relevant_paper_id = []

                # Reference Paper Update
                list_dict_reference_paper = q_paper_selected.list_dict_reference_paper
                if list_dict_reference_paper is not None and len(list_dict_reference_paper) > 0:
                    for dict_reference_paper in list_dict_reference_paper:
                        try:
                            ss_doi = dict_reference_paper["doi"]
                        except:
                            ss_doi = None
                        if ss_doi is not None:
                            q_paper_ref = Paper.objects.filter(doi=ss_doi).last()
                        else:
                            q_paper_ref = None
                        if q_paper_ref is not None:
                            if q_paper_ref.id not in list_reference_paper_id:
                                list_reference_paper_id.append(q_paper_ref.id)
                # Author Paper Update
                list_dict_author_paper = q_paper_selected.list_dict_author_paper
                if list_dict_author_paper is not None and len(list_dict_author_paper) > 0:
                    for dict_author_paper in list_dict_author_paper:
                        try:
                            ss_doi = dict_author_paper["doi"]
                        except:
                            ss_doi = None
                        if ss_doi is not None:
                            q_paper_author = Paper.objects.filter(doi=ss_doi).last()
                        else:
                            q_paper_author = None
                        if q_paper_author is not None:
                            if q_paper_author.id not in list_author_paper_id:
                                list_author_paper_id.append(q_paper_author.id)
                # Relevant Paper Update
                list_dict_relevant_paper = q_paper_selected.list_dict_relevant_paper
                if list_dict_relevant_paper is not None and len(list_dict_relevant_paper) > 0:
                    for dict_relevant_paper in list_dict_relevant_paper:
                        try:
                            ss_doi = dict_relevant_paper["doi"]
                        except:
                            ss_doi = None
                        if ss_doi is not None:
                            q_paper_relevant = Paper.objects.filter(doi=ss_doi).last()
                        else:
                            q_paper_relevant = None
                        if q_paper_relevant is not None:
                            if q_paper_relevant.id not in list_relevant_paper_id:
                                list_relevant_paper_id.append(q_paper_relevant.id)
                data = {
                    'list_reference_paper_id': list_reference_paper_id,
                    'list_author_paper_id': list_author_paper_id,
                    'list_relevant_paper_id': list_relevant_paper_id,
                }
                Paper.objects.filter(id=q_paper_selected.id).update(**data)

                # Reference Paper Data Serialize
                if list_reference_paper_id is not None and len(list_reference_paper_id) > 0:
                    qs_paper_reference = Paper.objects.filter(id__in=list_reference_paper_id)
                    list_serialized_data_paper_reference = List_Paper_Serializer(qs_paper_reference, many=True).data
                # Reference Paper Data Serialize
                if list_author_paper_id is not None and len(list_author_paper_id) > 0:
                    qs_paper_author = Paper.objects.filter(id__in=list_author_paper_id)
                    list_serialized_data_paper_author = List_Paper_Serializer(qs_paper_author, many=True).data
                # Reference Paper Data Serialize
                if list_relevant_paper_id is not None and len(list_relevant_paper_id) > 0:
                    qs_paper_relevant = Paper.objects.filter(id__in=list_relevant_paper_id)
                    list_serialized_data_paper_relevant = List_Paper_Serializer(qs_paper_relevant, many=True).data

            print('# 6-3. 선택한 Paper 모달창 Data update 하기')
            if q_paper_selected is not None:
                print('# paper screenshot 저장하기')
                list_dict_paper_image = q_paper_selected.list_dict_paper_image
                pdf_file_name = q_paper_selected.file_path_pdf 
                print('pdf_file_name', pdf_file_name)
                # file_path_pdf = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER, pdf_file_name)
                # print('file_path_pdf', file_path_pdf)
                output_folder_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER_SCREENSHOT)
                if pdf_file_name is not None and list_dict_paper_image is None:
                    print('background에서 image 추출 시작하기')
                    file_extension='png'
                    # convert_pdf_to_images(q_paper_selected.id, file_path_pdf, output_folder_path, file_extension)
                    convert_pdf_to_images_in_task.delay(q_paper_selected.id, pdf_file_name, output_folder_path, file_extension)
                else:
                    print('Paper screenshot image 추출 완료')
                    pass
        
        
        if q_paper_search_google_pubmed is not None:
            print('# 7. q_paper_search_google_pubmed에서 데이터 추출')
            serialized_data_paper_searched = Paper_Search_Google_and_PubMed_Serializer(q_paper_search_google_pubmed, many=False).data
            list_dict_paper_info_from_pubmed = q_paper_search_google_pubmed.list_dict_paper_info_from_pubmed
            if list_dict_paper_info_from_pubmed is not None and len(list_dict_paper_info_from_pubmed) > 0 and selected_data_paper_searched_selected_id is not None:
                for dict_paper_info_from_pubmed in list_dict_paper_info_from_pubmed:
                    if dict_paper_info_from_pubmed['id'] == selected_data_paper_searched_selected_id:
                        try:
                            ss_id = dict_paper_info_from_pubmed["id"]
                        except:
                            ss_id = None
                        try:
                            ss_doi = dict_paper_info_from_pubmed["doi"]
                        except:
                            ss_doi = None
                        try:
                            ss_pmcid = dict_paper_info_from_pubmed["pmcid"]
                        except:
                            ss_pmcid = None
                        try:
                            ss_title = dict_paper_info_from_pubmed["title"]
                        except:
                            ss_title = None
                        try:
                            ss_doi_url = dict_paper_info_from_pubmed["doi_url"]
                        except:
                            ss_doi_url = None
                        try:
                            ss_keyword = dict_paper_info_from_pubmed["keyword"]
                        except:
                            ss_keyword = None
                        try:
                            ss_pdf_url = dict_paper_info_from_pubmed["pdf_url"]
                        except:
                            ss_pdf_url = None
                        try:
                            ss_article_url = dict_paper_info_from_pubmed["article_url"]
                        except:
                            ss_article_url = None
                        try:
                            ss_abstract_url = dict_paper_info_from_pubmed["abstract_url"]
                        except:
                            ss_abstract_url = None
                        try:
                            ss_journal_name = dict_paper_info_from_pubmed["journal_name"]
                        except:
                            ss_journal_name = None
                        try:
                            ss_publication_year = dict_paper_info_from_pubmed["publication_year"]
                        except:
                            ss_publication_year = None
                        try:
                            ss_first_author_name = dict_paper_info_from_pubmed["first_author_name"]
                        except:
                            ss_first_author_name = None
                        serialized_data_paper_searched_selected = {
                            'id': ss_id,
                            'doi': ss_doi,
                            'pmcid': ss_pmcid,
                            'title': ss_title,
                            'doi_url': ss_doi_url,
                            'keyword': ss_keyword,
                            'pdf_url': ss_pdf_url,
                            'article_url': ss_article_url,
                            'abstract_url': ss_abstract_url,
                            'journal_name': ss_journal_name,
                            'publication_year': ss_publication_year,
                            'first_author_name': ss_first_author_name,
                        }   

                        if ss_doi is not None:
                            q_paper_selected = Paper.objects.filter(doi=ss_doi).last()
                            if q_paper_selected is None:
                                if ss_pmcid is not None:
                                    q_paper_selected = Paper.objects.filter(pmcid=ss_pmcid).last()
                                    if q_paper_selected is None:
                                        if ss_title is not None:
                                            q_paper_selected = Paper.objects.filter(title=ss_title).last()
                                        else:
                                            q_paper_selected = None
                        
            list_dict_paper_info_from_google = q_paper_search_google_pubmed.list_dict_paper_info_from_google
            if list_dict_paper_info_from_google is not None and len(list_dict_paper_info_from_google) > 0:
                pass 
            # print('serialized_data_paper_searched_selected', serialized_data_paper_searched_selected)    
            
        # Data Serialization
        if q_paper_selected is not None:
            print('# 8. q_paper_selected Data Serialization 시작')
            serialized_data_paper = Paper_Serializer(q_paper_selected, many=False).data

        list_bookmarked_paper_id = q_mysettings_study.list_bookmarked_paper_id
        if list_bookmarked_paper_id is not None and len(list_bookmarked_paper_id) > 0:
            if q_paper_selected is not None:
                if q_paper_selected.id in list_bookmarked_paper_id:
                    check_selected_paper_bookmarked = True
        print('len(list_serialized_data_paper_reference)', len(list_serialized_data_paper_reference))
        # print('list_serialized_data_paper_relevant', len(list_serialized_data_paper_relevant), list_serialized_data_paper_relevant)
        jsondata = {
            'serialized_data_paper': serialized_data_paper,
            'serialized_data_paper_searched': serialized_data_paper_searched,
            'serialized_data_paper_searched_selected': serialized_data_paper_searched_selected,
            'list_serialized_data_paper_reference': list_serialized_data_paper_reference,
            'list_serialized_data_paper_author': list_serialized_data_paper_author,
            'list_serialized_data_paper_relevant': list_serialized_data_paper_relevant,
            'check_selected_paper_bookmarked': check_selected_paper_bookmarked,
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False) 



#--------------------------------------------------------------------------------------------------------------------------------------
@login_required 
def study_paper_selected_paper_modal_action(request):
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    study_type = 'paper'
    
    if request.method == 'GET':
        print('study_paper_selected_paper_data_collection GET =========================================================================== 1')
        print(request.GET,)
        print('======================================================================================================= 2')
        # Jsondata 패키지
        jsondata = {
            'message': 'hi'
            # 'serialized_data_paper_searched': serialized_data_paper_searched,
            # 'serialized_data_mysettings_study': serialized_data_mysettings_study,
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False) 


    if request.method == 'POST':
        print('study_paper_selected_paper_data_collection GET =========================================================================== 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        serialized_data_paper = {}
        check_selected_paper_bookmarked = False 

        selected_data_paper_id_str = request.POST.get('selected_data_paper_id') # Paper 테이블 쿼리 ID
        selected_data_paper_id_str = None if selected_data_paper_id_str in LIST_STR_NONE_SERIES else selected_data_paper_id_str
        print('selected_data_paper_id_str', selected_data_paper_id_str)
        if selected_data_paper_id_str is not None:
            selected_data_paper_id = int(selected_data_paper_id_str)
            try:
                q_paper_selected = Paper.objects.get(id=selected_data_paper_id)
            except:
                q_paper_selected = None
        else:
            q_paper_selected = None
        print('q_paper_selected ', q_paper_selected)

        if request.POST.get('button') == 'check_bookmark':
            # on the Paper
            list_bookmarked_paper_id = q_mysettings_study.list_bookmarked_paper_id
            if list_bookmarked_paper_id is None:
                list_bookmarked_paper_id = []
            if q_paper_selected.id in list_bookmarked_paper_id:
                list_bookmarked_paper_id.remove(q_paper_selected.id)
            else:
                list_bookmarked_paper_id.append(q_paper_selected.id)
            data = {
                'list_bookmarked_paper_id': list_bookmarked_paper_id,
            }
            MySettings_Study.objects.filter(id=q_mysettings_study.id).update(**data)

            # on the Mysettings_Study
            list_bookmarked_user_id = q_paper_selected.list_bookmarked_user_id
            if list_bookmarked_user_id is None:
                list_bookmarked_user_id = []
            q_mysettings_study.refresh_from_db()
            if q_user.id in list_bookmarked_user_id:
                list_bookmarked_user_id.remove(q_user.id)
            else:
                list_bookmarked_user_id.append(q_user.id)
            data = {
                'list_bookmarked_user_id': list_bookmarked_user_id
            }
            Paper.objects.filter(id=q_paper_selected.id).update(**data)
            q_paper_selected.refresh_from_db()
            
        list_bookmarked_paper_id = q_mysettings_study.list_bookmarked_paper_id
        if list_bookmarked_paper_id is not None and len(list_bookmarked_paper_id) > 0:
            if q_paper_selected is not None:
                if q_paper_selected.id in list_bookmarked_paper_id:
                    check_selected_paper_bookmarked = True
                else:
                    check_selected_paper_bookmarked = False
        if q_paper_selected is not None:
            serialized_data_paper = Paper_Serializer(q_paper_selected, many=False).data
        
        print('check_selected_paper_bookmarked', check_selected_paper_bookmarked)
        jsondata = {
            'serialized_data_paper': serialized_data_paper,
            'check_selected_paper_bookmarked': check_selected_paper_bookmarked,
        }
        return JsonResponse(jsondata, safe=False) 




#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def study_patent(request):
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    
    if request.method == 'GET':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 

    if request.method == 'POST':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def study_protocol(request):
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    
    if request.method == 'GET':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 

    if request.method == 'POST':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 



#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def study_fda(request):
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    
    if request.method == 'GET':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 

    if request.method == 'POST':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 



#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def study_lecture(request):
    q_user = request.user
    q_mysettings_study = MySettings_Study.objects.get(user=q_user)
    
    if request.method == 'GET':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 

    if request.method == 'POST':
        jsondata = {}
        return JsonResponse(jsondata, safe=False) 






































#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#
#                                                          Entertainment
#
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################


@login_required
def entertainment(request):
    page_category = 'entertainment'
    print("entertainment VIEW")
    page_category = 'entertainment'
    check_authority = f_check_authority(request, page_category)
    if check_authority:
        template = 'entertainment.html'
        q_user = request.user
        q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    else:
        q_mysettings_hansent = None
        template = 'users/unauthorized.html'

    context={
        'key1': 'Good!',
        'q_mysettings_hansent': q_mysettings_hansent,
        }
    
    if request.method == 'GET':
        return render(request, template, context)
    


#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Hans Ent
#
#############################################################################################################################################
#############################################################################################################################################

@login_required
def hans_ent(request):
    print("hans_ent VIEW")
    page_category = 'hans_ent'
    check_authority = f_check_authority(request, page_category)
    if check_authority:
        template = 'hans_ent.html'
        q_user = request.user
        create_user_settings(request)
        q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
        q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    else:
        q_mysettings_hansent = None
        q_systemsettings_hansent = None
        template = 'users/unauthorized.html'

    context={
        'key1': 'Good!',
        'LIST_MENU_HANS_ENT': LIST_MENU_HANS_ENT,
        'q_mysettings_hansent': q_mysettings_hansent,
        'q_systemsettings_hansent': q_systemsettings_hansent,
        }
    
    if request.method == 'GET':
        return render(request, template, context)
    
    if request.method == 'POST':
        menu_selected = request.POST.get('button-switch-hans-ent-home-menu')
        if menu_selected is not None:
            data = {
                'menu_selected': menu_selected
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
        hans_ent_count_page_number_reset(q_mysettings_hansent)
        return redirect('hans-ent')



def hans_ent_refresh_router(request):
    print('======================= hans_ent_refresh_router START')
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
    if request.method == 'GET':
        # selected_serialized_data_mysettings = Mysettings_Hans_Ent_Serializer(q_mysettings_hansent, many=False)
        menu_selected = q_mysettings_hansent.menu_selected
        jsondata = {
            # 'selected_serialized_data_mysettings': selected_serialized_data_mysettings,
            'menu_selected': menu_selected,
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)

    if request.method == 'POST':
        jsondata = {}
        return JsonResponse(jsondata, safe=False)



#############################################################################################################################################
#############################################################################################################################################



def hans_ent_test_function(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()

    if request.method == 'GET':
        # selected_serialized_data_mysettings = Mysettings_Hans_Ent_Serializer(q_mysettings_hansent, many=False)
        menu_selected = q_mysettings_hansent.menu_selected
        jsondata = {
            # 'selected_serialized_data_mysettings': selected_serialized_data_mysettings,
            'menu_selected': menu_selected,
        }
        print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)

    if request.method == 'POST':
        print('#############################', request.POST)        
        if request.POST.get('button') == 'one':
            print('11111111111111111')
            
        
        
        # Picture
        if request.POST.get('button') == 'picture_1':
            print('************ 4KHD image URL Scraping')
            parsing_picture_start_page_reverse_count_str = request.POST.get('parsing_picture_start_page_reverse_count') 
            parsing_picture_start_page_reverse_count_str = None if parsing_picture_start_page_reverse_count_str in LIST_STR_NONE_SERIES else parsing_picture_start_page_reverse_count_str
            if parsing_picture_start_page_reverse_count_str is not None:
                parsing_picture_start_page_reverse_count = int(parsing_picture_start_page_reverse_count_str)
                data = {
                    'parsing_picture_start_page_reverse_count': parsing_picture_start_page_reverse_count,
                }
                SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
            # update_all_4khd_img_url_data_to_db.delay()
            update_latest_4khd_data_to_db.delay()

        if request.POST.get('button') == 'picture_2':
            print('************ 4KHD image Download')
            download_image_using_url_w_multiprocessing1.delay()

        if request.POST.get('button') == 'picture_3':
            print('************ Check Downloaded image')
            check_picture_album_defect_and_correct.delay()
        
        if request.POST.get('button') == 'picture_4':
            print('************ Update Missing File to List')
            update_missing_files_in_list_dict_picture_album.delay()

        if request.POST.get('button') == 'picture_5':
            print('************ Update File Download Status')
            qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False))
            tot_num_check = len(qs_picture_album)

            list_pic_downloaded_id = []
            list_pic_not_downloaded_but_img_url_exist_id = []
            list_pic_not_downloaded_no_img_url_but_gallery_url_exist_id = []
            list_pic_not_downloaded_no_img_url_no_gallery_url_id = []

            for q_picture_album in qs_picture_album:
                # 다운받은 이미지 파일이 존재하는지 체크
                hashcode = q_picture_album.hashcode
                DOWNLOAD_PICTURE_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
                test_file_name = f'{hashcode}-o-1.jpg'
                test_file_path = os.path.join(DOWNLOAD_PICTURE_DIR, test_file_name)
                if os.path.exists(test_file_path):
                    # print(f'이미 다운받았습니다.')
                    data = {
                        'check_url_downloaded': True
                    }
                    Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                    list_pic_downloaded_id.append(q_picture_album.id)
                else:
                    list_picture_url_album = q_picture_album.list_picture_url_album
                    if list_picture_url_album is not None and len(list_picture_url_album) > 0:
                        data = {
                            'list_dict_picture_album': None,
                            'check_url_downloaded': False
                        }
                        Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                        list_pic_not_downloaded_but_img_url_exist_id.append(q_picture_album.id)
                        # print(f'이미지 URL 정보가 있습니다.')
                    else:
                        dict_gallery_info = q_picture_album.dict_gallery_info
                        if dict_gallery_info is not None:
                            try:
                                dict_gallery_info = q_picture_album.dict_gallery_info
                            except:
                                dict_gallery_info = None
                            if dict_gallery_info is not None:
                                try:
                                    gallery_url = dict_gallery_info['url']
                                except:
                                    gallery_url = None 
                            else:
                                gallery_url = None
                            if  gallery_url is None:
                                # print(f'앨범 다운 정보 없음. 폐기처분')
                                data = {
                                    'check_discard': True
                                }
                                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                                list_pic_not_downloaded_no_img_url_no_gallery_url_id.append(q_picture_album.id)
                            else:
                                # print(f'gallery_url 정보가 있습니다.')
                                data = {
                                    'list_dict_picture_album': None,
                                    'check_url_downloaded': False
                                }
                                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                                list_pic_not_downloaded_no_img_url_but_gallery_url_exist_id.append(q_picture_album.id)
                        else:
                            # print(f'앨범 다운 정보 없음. 폐기처분')
                            data = {
                                'check_discard': True
                            }
                            Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                            list_pic_not_downloaded_no_img_url_no_gallery_url_id.append(q_picture_album.id)

                if tot_num_check > 0:
                    tot_num_check = tot_num_check - 1 
                    # print(f'remained tasks {tot_num_check}')
                else:
                    # print('done')
                    pass
            
            print(f'list_pic_downloaded_id, {len(list_pic_downloaded_id)}')
            print(f'list_pic_not_downloaded_but_img_url_exist_id, {len(list_pic_not_downloaded_but_img_url_exist_id)}')
            print(f'list_pic_not_downloaded_no_img_url_but_gallery_url_exist_id, {len(list_pic_not_downloaded_no_img_url_but_gallery_url_exist_id)}')
            print(f'list_pic_not_downloaded_no_img_url_no_gallery_url_id, {len(list_pic_not_downloaded_no_img_url_no_gallery_url_id)}')


        if request.POST.get('button') == 'picture_6':        
            print('************ Hashcode Path Dup Remove')
            qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False) & Q(check_url_downloaded=True))
            tot_num_check = len(qs_picture_album)
            print(f'tot_num_check : {tot_num_check}')
            for q_picture_album in qs_picture_album:
                print('q_picture_album: ', q_picture_album.id)
                list_dict_picture_album = q_picture_album.list_dict_picture_album
                if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                    print(len(list_dict_picture_album))
                    list_dict_picture_album_dup_check = []
                    list_dict_picture_album_new = []
                    for dict_picture_album in list_dict_picture_album:
                        try:
                            id_pic = dict_picture_album['id']
                            # print('id_pic: ', id_pic)
                            if id_pic not in list_dict_picture_album_dup_check:
                                dict_picture_album['active'] = "false"
                                if id_pic == 0:
                                    dict_picture_album['discard'] = "true"
                                list_dict_picture_album_dup_check.append(id_pic)
                                list_dict_picture_album_new.append(dict_picture_album)
                        except:
                            pass
                    print(len(list_dict_picture_album_new))
                    sorted_list_dict_picture_album_new = sorted(list_dict_picture_album_new, key=lambda x: x["id"])
                    dict_picture_album_last = sorted_list_dict_picture_album_new[-1]
                    if dict_picture_album_last['id'] != 0:
                        dict_picture_album_last['active'] = 'true'
                    data = {
                        'list_dict_picture_album': sorted_list_dict_picture_album_new
                    }
                    Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                if tot_num_check > 0:
                    tot_num_check = tot_num_check - 1 
                    print(f'remained tasks {tot_num_check}')
                else:
                    print('done')
            pass


        if request.POST.get('button') == 'picture_7':
            print('************ get title tag parsing')
            # num_id = 11923
            # q_picture_album = Picture_Album.objects.get(id=num_id)
            # tags = find_keywords_based_on_picture_album_title(q_picture_album)
            # print(f'tags: {tags}')

            qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False) & Q(tags__isnull=False))
            num_tasks = len(qs_picture_album)
            print('total num_tasks', num_tasks)
            for q_picture_album in qs_picture_album:
                title = q_picture_album.title
                tags = title_string_convert_to_title_elements(title)
                # tags = find_keywords_based_on_picture_album_title(q_picture_album)
                print(f'num_tasks: {num_tasks}')
                # print('tags: ', tags)
                data = {
                    'tags': tags,
                }
                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                num_tasks = num_tasks - 1
            






        # Manga
        if request.POST.get('button') == 'manga_1':
            qs_manga = Manga_Album.objects.filter(Q(check_discard=False))
            for q_manga in qs_manga:
                dict_manga_album_cover = {"cover": "default-c.png", "original": "default-o.png", "thumbnail": "default-t.png"}
                data = {
                    'dict_manga_album_cover': dict_manga_album_cover,
                    'list_dict_manga_album': None,
                    'list_dict_volume_manga': None,
                }
                Manga_Album.objects.filter(id=q_manga.id).update(**data)
            print('manga_1 Done')
            
        if request.POST.get('button') == 'manga_2':
            pass
        
        if request.POST.get('button') == 'manga_3':
            pass
            


        # Video
        if request.POST.get('button') == 'video_1':
            print('################################ video #1')
            update_latest_javdatabase_data_to_db.delay()

        if request.POST.get('button') == 'video_2':
            print('################################ video #2')
            qs_video_album = Video_Album.objects.filter(Q(check_discard=False) & Q(title__isnull=True))
            print(len(qs_video_album))
            if qs_video_album is not None and len(qs_video_album) > 0:
                for q_video_album in qs_video_album:
                    if q_video_album.code is not None:
                        data = {
                            'title': q_video_album.code
                        }
                        Video_Album.objects.filter(id=q_video_album.id).update(**data)


        if request.POST.get('button') == 'video_3':
            print('################################ video #3')
            qs_video_album = Video_Album.objects.filter(Q(check_discard=False))
            tot_mission_num = len(qs_video_album)
            print(f'total mission number : {tot_mission_num}')
            
            for q_video_album in qs_video_album:
                tags_new = []
                title = q_video_album.title
                tags = q_video_album.tags
                list_dict_video_album = q_video_album.list_dict_video_album

                if title is not None:
                    title = text_cleaning(title)
                    list_word = text_to_list_word(title)
                    title = list_word_joining_for_title(list_word)
                                   

                if tags is not None and len(tags) > 0:
                    for tag in tags:
                        # 텍스트 뭉치 클리닝
                        tag_cleaned = text_cleaning(tag)  
                        tags_new.append(tag_cleaned)

                if list_dict_video_album is not None and len(list_dict_video_album) > 0:
                    for dict_video_album in list_dict_video_album:
                        try:
                            dict_title = dict_video_album['title']
                            dict_title = text_cleaning(dict_title)
                            dict_list_word = text_to_list_word(dict_title)
                            dict_title = list_word_joining_for_title(dict_list_word)
                            dict_video_album['title'] = dict_title
                        except:
                            pass


                data = {
                    'title': title,
                    'tags': tags_new,
                    'list_dict_video_album': list_dict_video_album,
                }
                Video_Album.objects.filter(id=q_video_album.id).update(**data) 
                        
                print(tot_mission_num)
                tot_mission_num = tot_mission_num - 1

            # keyword = '자위'
            # qs_video_album_searched = Video_Album.objects.filter(Q(check_discard=False) & (Q(title__icontains=keyword) | Q(tags__in=keyword)) & Q(main_actor__isnull=True))
            # print('len', len(qs_video_album_searched))
            # if qs_video_album_searched is not None and len(qs_video_album_searched) > 0:
            #     for q_video_album_searched in qs_video_album_searched:
            #         print(q_video_album_searched.id)

            input_text_name_str = '77777'
            # input_text_name_str = 'donggeuran'
            q_actor = Actor.objects.filter(Q(check_discard=False) & (Q(name=input_text_name_str) | Q(synonyms__contains=input_text_name_str))).last()
            try:
                print(q_actor.id)
            except:
                print('none')
                
        
        
        if request.POST.get('button') == 'video_4':
            print('################################ video #4')
            qs_video_album = Video_Album.objects.filter(Q(check_discard=False))
            tot_mission_num = len(qs_video_album)
            print(f'total mission number : {tot_mission_num}')
            
            root_dir = "/django-project/site/public/media/vault1/video/"
            # Collect all file names
            file_names = []
            for root, dirs, files in os.walk(root_dir):
                for file in files:
                    file_names.append(os.path.join(root, file))
            print(f'len(file_names): {len(file_names)}')

            i = 0
            for q_video_album in qs_video_album:
                hashcode = q_video_album.hashcode
                # 검색할 디렉토리와 문자열
                

                list_matched_file_names = []
                # Print all file paths
                if len(file_names) > 0:
                    for name in file_names:
                        try:
                            name_str = str(name)
                        except:
                            name_str = None 
                        if name_str is not None and hashcode in name_str:
                            list_matched_file_names.append(name_str)
                
                if len(list_matched_file_names) == 0:
                    # print('i', i)
                    # print('q_video_album delete', q_video_album.id)
                    delete_files_in_list_dict_xxx_album(q_video_album, 'video', 'all', 'all') 
                    i = i + 1
            print('i', i)

        jsondata = {
            'message': 'Good!'
        }
        return JsonResponse(jsondata, safe=False)





#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#
#                                                              Actor
#
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
    
# @login_required
def hans_ent_actor_list(request):
    print('hans_ent_actor_list VIEW')
    import datetime
    ls_today = datetime.date.today()
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    album_type = 'actor'
    if request.method == 'GET':
        total_num_registered_item = Actor.objects.count()
        # Searching 결과값 찾기
        list_searched_xxx_id = q_mysettings_hansent.list_searched_actor_id
        if list_searched_xxx_id is not None:
            total_num_searched_item = len(list_searched_xxx_id)
        else:
            total_num_searched_item = 0
        # Sorting Submenu 조건
        selected_field_sorting_str = q_mysettings_hansent.selected_field_actor
        # Category Filtering
        selected_category_actor_str = q_mysettings_hansent.selected_category_actor
        # selected_category_actor_str = ast.literal_eval(selected_category_actor_str)[0]
        # Acending or Decending?
        field_ascending_str = q_mysettings_hansent.check_field_ascending_actor
        if field_ascending_str == False:
            if selected_field_sorting_str == 'score':
                selected_field_sorting = selected_field_sorting_str
            else:
                selected_field_sorting = f'-{selected_field_sorting_str}'
        else:
            if selected_field_sorting_str == 'score':
                selected_field_sorting = f'-{selected_field_sorting_str}'
            else:
                selected_field_sorting = selected_field_sorting_str
        # 화면에 표시할 아이템 개수 지정
        count_page_number = q_mysettings_hansent.count_page_number_actor
        count_page_number_min = (count_page_number - 1) * LIST_NUM_DISPLAY_IN_PAGE
        count_page_number_max = count_page_number * LIST_NUM_DISPLAY_IN_PAGE
        # 쿼리 필터링
        if list_searched_xxx_id is not None and len(list_searched_xxx_id) > 0:
            if selected_category_actor_str == '00':
                print('1')
                qs_xxx = Actor.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
            else:
                print('2')
                qs_xxx = Actor.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id) & Q(category=selected_category_actor_str)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        else:
            if selected_category_actor_str == '00':
                print('3')
                qs_xxx = Actor.objects.filter(Q(check_discard=False)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
            else:
                print('4')
                qs_xxx = Actor.objects.filter(Q(check_discard=False) & Q(category=selected_category_actor_str)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        print('len(qs_xxx)', len(qs_xxx))

        # Score 계산
        for q_xxx in qs_xxx:
            dict_score_history = q_xxx.dict_score_history
            score = get_score_album(album_type, dict_score_history)
            data = {
                'score': score,
            }
            Picture_Album.objects.filter(id=q_xxx.id).update(**data)

        # Data Serialization            
        list_serialized_data_actor = Actor_Serializer(qs_xxx, many=True).data
        
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_PICTURE': BASE_DIR_PICTURE,
            'BASE_DIR_MANGA': BASE_DIR_MANGA,
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'BASE_DIR_MUSIC': BASE_DIR_MUSIC,
            'LIST_ACTOR_CATEGORY': LIST_ACTOR_CATEGORY,
            'LIST_ACTOR_SORTING_FIELD': LIST_ACTOR_SORTING_FIELD,
            'LIST_DICT_SITE_ACTOR_INFO': LIST_DICT_SITE_ACTOR_INFO,
            'list_serialized_data_actor': list_serialized_data_actor,
            'total_num_registered_item': total_num_registered_item,
            'total_num_searched_item': total_num_searched_item,
            'list_count_page_number': [count_page_number_min, count_page_number_max, count_page_number],
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        # print(request.POST)
        if request.POST.get('button') == 'sorting_items':
            selected_sorting_field_str = request.POST.get('sort_by')
            selected_field_actor = q_mysettings_hansent.selected_field_actor
            check_field_ascending_actor = q_mysettings_hansent.check_field_ascending_actor
            if selected_sorting_field_str == selected_field_actor:
                if check_field_ascending_actor == True:
                    check_field_ascending_actor = False 
                else:
                    check_field_ascending_actor = True 
            data = {
                'selected_field_actor':selected_sorting_field_str, 
                'check_field_ascending_actor': check_field_ascending_actor,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            print('Sorting 조건 확정 및 저장')
            return redirect('hans-ent-actor-list')
        
        if request.POST.get('button') == 'category_filtering':
            selected_category_str = request.POST.get('selected_category')
            print('selected_category_str', selected_category_str)
            data = {
                'selected_category_actor': selected_category_str,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            return redirect('hans-ent-actor-list')


        if request.POST.get('button') == 'page_number_min':
            hans_ent_count_page_number_down(request, q_mysettings_hansent)
            return redirect('hans-ent-actor-list')
        
        if request.POST.get('button') == 'page_number_max':
            total_num_registered_item = Actor.objects.count()
            hans_ent_count_page_number_up(request, q_mysettings_hansent, total_num_registered_item)
            return redirect('hans-ent-actor-list')

        
        # Selected Album Delete (선택 앨범 모두 삭제하기)
        if request.POST.get('button') == 'delete_selected_actor':
            print('# Selected Actor Delete (선택 앨범 모두 삭제하기) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            list_actor_id_for_checkbox_selection_str = request.POST.getlist('list_actor_id_for_checkbox_selection[]')
            list_actor_id_for_checkbox_selection = list(map(int, list_actor_id_for_checkbox_selection_str))
            qs_actor = Actor.objects.filter(id__in=list_actor_id_for_checkbox_selection)
            if qs_actor is not None and len(qs_actor) > 0:
                for q_actor_selected in qs_actor:
                    delete_files_in_list_dict_xxx_album(q_actor_selected, 'actor', 'all', 'all')  ## album 종류(actor, picture, video, music 중 택 1), 싱글 쿼리, 삭제종류('all' or int(id)) 
               
        
       

        jsondata = {}
        return JsonResponse(jsondata, safe=False)




#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_actor_list_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == 'GET':
        print('##############################################################', request.GET,)
        
        keyword_str = request.GET.get('keyword')
        qs_xxx = Actor.objects.filter(Q(check_discard=False) & (Q(name__icontains=keyword_str) | Q(synonyms__icontains=keyword_str)))
        print('qs_xxx', qs_xxx)
        list_searched_actor_id = []
        if qs_xxx is not None and len(qs_xxx) > 0:
            for q_xxx in qs_xxx:
                list_searched_actor_id.append(q_xxx.id)
        data = {
            'list_searched_actor_id': list_searched_actor_id, 
        }
        MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
        return redirect('hans-ent-actor-list')
    
    if request.method == 'POST':
        keyword_str = request.POST.get('button')
        if keyword_str == 'reset':
            reset_hans_ent_actor_list(q_mysettings_hansent)
        return redirect('hans-ent-actor-list')


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_actor_profile_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    album_type='actor'

    if request.method == "GET":
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)
    
    if request.method == "POST":
        """
        Actor 관련 정보 + Actor가 참여한 모든 앨범(Picture, Video, Music, Anything) 정보를 표시
        """
        print('hans_ent_actor_profile_modal POST ======================================================= 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        selected_serialized_data_actor = {}
        selected_serialized_data_picture_album = {}
        selected_serialized_data_video_album = {}
        selected_serialized_data_music_album = {}
        
        list_serialized_data_picture_album_by_actor = []
        list_serialized_data_video_album_by_actor = []
        list_serialized_data_music_album_by_actor = []

        list_serialized_data_picture_album_collected = []
        serialized_data_picture_album_collected = {}
        list_collected_keywords_from_title = []
        check_selected_actor_favorite = False
        
        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_picture_album_id_str = request.POST.get('selected_picture_album_id')
        selected_video_album_id_str = request.POST.get('selected_video_album_id')
        selected_music_album_id_str = request.POST.get('selected_music_album_id')
        
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        selected_picture_album_id_str = None if selected_picture_album_id_str in LIST_STR_NONE_SERIES else selected_picture_album_id_str
        selected_video_album_id_str = None if selected_video_album_id_str in LIST_STR_NONE_SERIES else selected_video_album_id_str
        selected_music_album_id_str = None if selected_music_album_id_str in LIST_STR_NONE_SERIES else selected_music_album_id_str
        
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        print('selected actor: ', q_actor)
        
        if selected_picture_album_id_str is not None and selected_picture_album_id_str != '':
            selected_picture_album_id = int(selected_picture_album_id_str)
            q_picture_album = Picture_Album.objects.get(id=selected_picture_album_id)
            if q_picture_album is not None:
                q_actor = q_picture_album.main_actor
        else:
            q_picture_album = None
        print('q_picture_album: ', q_picture_album)
        
        if selected_video_album_id_str is not None and selected_video_album_id_str != '':
            selected_video_album_id = int(selected_video_album_id_str)
            q_video_album = Video_Album.objects.get(id=selected_video_album_id)
            if q_video_album is not None:
                q_actor = q_video_album.main_actor
        else:
            q_video_album = None
        print('q_video_album: ', q_video_album)
        
        if selected_music_album_id_str is not None and selected_music_album_id_str != '':
            selected_music_album_id = int(selected_music_album_id_str)
            q_music_album = Music_Album.objects.get(id=selected_music_album_id)
            if q_music_album is not None:
                q_actor = q_music_album.main_actor
        else:
            q_music_album = None
        print('q_music_album: ', q_music_album)

        # Actor Age update 하기
        if q_actor is not None:
            date_birth = q_actor.date_birth
            if date_birth is not None:
                age = calculate_age(date_birth)
                data = {
                    'age': age,
                }
                Actor.objects.filter(id=q_actor.id).update(**data)
                q_actor.refresh_from_db()

        # Favorite 상태 변경하기
        if request.POST.get('button') == 'status_favorite_change':
            print('status_favorite_change')
            if q_actor is not None:
                dict_score_history = q_actor.dict_score_history
                if dict_score_history is None:
                    dict_score_history = DEFAULT_DICT_SCORE_HISTORY_ACTOR
                    check_selected_actor_favorite = True
                else:
                    if 'favorite' in dict_score_history:
                        if dict_score_history['favorite'] == 'true':
                            dict_score_history['favorite'] = 'false'
                            check_selected_actor_favorite = False
                        else:
                            dict_score_history['favorite'] = 'true'
                            check_selected_actor_favorite = True
                    else:
                        dict_score_history['favorite'] = 'true'
                        check_selected_actor_favorite = True
                data = {
                    'dict_score_history': dict_score_history,
                }
                Actor.objects.filter(id=q_actor.id).update(**data)
                q_actor.refresh_from_db()
        
        # Rating 점수 상향
        if request.POST.get('button') == 'add_rating_score':
            if q_actor is not None:
                dict_score_history = q_actor.dict_score_history
                if dict_score_history is None:
                    dict_score_history = DEFAULT_DICT_SCORE_HISTORY_ACTOR
                else:
                    if 'rating' in dict_score_history:
                        rating = dict_score_history['rating']
                        rating = rating + 1
                        dict_score_history['rating'] = rating
                    else:
                        dict_score_history['rating'] = 1
                dict_score_history['favorite'] = 'true'
                check_selected_actor_favorite = True
                data = {
                    'dict_score_history': dict_score_history,
                }
                Actor.objects.filter(id=q_actor.id).update(**data)
                q_actor.refresh_from_db()

        # 선택한 Favorite 상태 확인하기 및 스코어링
        if q_actor is not None:
            dict_score_history = q_actor.dict_score_history
            if dict_score_history is None:
                dict_score_history = DEFAULT_DICT_SCORE_HISTORY_ACTOR
                check_selected_actor_favorite = False
            else:
                if 'rating' not in dict_score_history:
                    dict_score_history['rating'] = 0
                if dict_score_history['favorite'] == 'true':
                    if dict_score_history['rating'] == 0:
                        dict_score_history['rating'] = 1
                    check_selected_actor_favorite = True
                else:
                    check_selected_actor_favorite = False
            # 방문 점수 카운트
            total_visit_album = dict_score_history['total_visit_album']
            total_visit_album = total_visit_album + 1
            dict_score_history['total_visit_album'] = total_visit_album
            # Score 업데이트             
            score = get_score_album(album_type, dict_score_history)
            print('score', score)
            data = {
                'score': score,
                'dict_score_history': dict_score_history,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()
        
        # 보내야 하는 정보 수집하기 ###############################################################
        print('selected actor: ', q_actor)
        if q_actor is not None:
            print('보내는 Data 수집')
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data
            print("selected_serialized_data_actor", len(selected_serialized_data_actor))
            qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_actor))
            qs_video_album = Video_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_actor))
            qs_music_album = Music_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_actor))


            ##############################################################################################################
            # thumbnail 만 보내라. 모든 정보 보내지 말고
            # picture 앨범은 다운로드 받았는지 못받았는지 정보를 보내라
            #
            if qs_picture_album is not None and len(qs_picture_album) > 0:
                # list_serialized_data_picture_album_by_actor = Picture_Album_Serializer(qs_picture_album, many=True).data
                for q_picture_album in qs_picture_album:
                    list_dict_picture_album = q_picture_album.list_dict_picture_album
                    thumbnail = None
                    if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                        for dict_picture_album in list_dict_picture_album:
                            if dict_picture_album['active'] == 'true':
                                thumbnail = dict_picture_album['thumbnail']
                    data = {
                        'id': q_picture_album.id,
                        'title': q_picture_album.title,
                        'code': q_picture_album.code, 
                        'check_url_downloaded': q_picture_album.check_url_downloaded,
                        'check_4k_uploaded': q_picture_album.check_4k_uploaded,
                        'score': q_picture_album.score,
                        'rating': q_picture_album.rating,
                        'thumbnail': thumbnail,
                    }
                    list_serialized_data_picture_album_by_actor.append(data)
                print("list_serialized_data_picture_album_by_actor", len(list_serialized_data_picture_album_by_actor))
            if qs_video_album is not None and len(qs_video_album) > 0:
                list_serialized_data_video_album_by_actor = Video_Album_Serializer(qs_video_album, many=True).data
                print("list_serialized_data_video_album_by_actor", len(list_serialized_data_video_album_by_actor))
            if qs_music_album is not None and len(qs_music_album) > 0:
                list_serialized_data_music_album_by_actor = Music_Album_Serializer(qs_video_album, many=True).data
                print("list_serialized_data_music_album_by_actor", len(list_serialized_data_music_album_by_actor))

            if q_picture_album:
                selected_serialized_data_picture_album = Picture_Album_Serializer(q_picture_album, many=False).data
            if q_video_album:
                selected_serialized_data_video_album = Video_Album_Serializer(q_video_album, many=False).data
            if q_music_album:
                selected_serialized_data_music_album = Music_Album_Serializer(q_music_album, many=False).data
            print('check_selected_actor_favorite', check_selected_actor_favorite)
            jsondata = {
                'check_response': 'true',
                'check_selected_actor_favorite': check_selected_actor_favorite,
                'selected_serialized_data_actor': selected_serialized_data_actor,
                'selected_serialized_data_picture_album': selected_serialized_data_picture_album,
                'selected_serialized_data_video_album': selected_serialized_data_video_album,
                'selected_serialized_data_music_album': selected_serialized_data_music_album,
                'list_serialized_data_picture_album_by_actor': list_serialized_data_picture_album_by_actor,
                'list_serialized_data_video_album_by_actor': list_serialized_data_video_album_by_actor,
                'list_serialized_data_music_album_by_actor': list_serialized_data_music_album_by_actor,
            }
            # print('jsondata', jsondata)
            return JsonResponse(jsondata, safe=False)
        else:
            print('q_actor가 없는 경우')
            if q_picture_album:
                print('q_picture_album', q_picture_album)
                list_collected_keywords_from_title = find_keywords_based_on_picture_album_title(q_picture_album)
                selected_serialized_data_picture_album = Picture_Album_Serializer(q_picture_album, many=False).data
                
                dict_picture_album = {}
                list_dict_picture_album = q_picture_album.list_dict_picture_album
                if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                    for dict_item in list_dict_picture_album:
                        if dict_item['active'] == 'true' and dict_item['discard'] == 'false':
                            dict_picture_album = dict_item
                list_picture_url_album = q_picture_album.list_picture_url_album
                if list_picture_url_album is not None and len(list_picture_url_album) > 0:
                    picture_url = list_picture_url_album[0]
                else:
                    picture_url = None
                serialized_data_picture_album_collected = {
                    'id': q_picture_album.id,
                    'title': q_picture_album.title,
                    'dict_picture_album': dict_picture_album,
                    'picture_url': picture_url,
                }
                
            if q_video_album:
                print('q_video_album', q_video_album)
                list_collected_keywords_from_title = find_keywords_based_on_video_album_title(q_video_album)
                selected_serialized_data_video_album = Video_Album_Serializer(q_video_album, many=False).data

            if q_music_album:
                print('q_music_album', q_music_album)
                list_collected_keywords_from_title = find_keywords_based_on_music_album_title(q_music_album)
                selected_serialized_data_music_album = Music_Album_Serializer(q_music_album, many=False).data

            print('serialized_data_picture_album_collected', serialized_data_picture_album_collected)
            jsondata = {
                'check_response': 'false',
                'message': '선택하신 Album에 등록된 Actor가 없습니다.',
                'list_collected_keywords_from_title': list_collected_keywords_from_title,
                'selected_serialized_data_picture_album': selected_serialized_data_picture_album,
                'selected_serialized_data_video_album': selected_serialized_data_video_album,
                'selected_serialized_data_music_album': selected_serialized_data_music_album,
                'serialized_data_picture_album_collected': serialized_data_picture_album_collected,
            }
            # print('jsondata', jsondata)
            return JsonResponse(jsondata, safe=False)
        



#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_actor_update_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    
    if request.method == "GET":
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)
    if request.method == "POST":

        print('hans_ent_actor_update_modal ========================================================================== 1')
        print(request.POST,)
        print('======================================================================================================= ')
        selected_serialized_data_actor = {}
        list_serialized_data_picture_album_collected = [] 
        list_serialized_data_manga_album_collected = []
        list_serialized_data_video_album_collected = []
        list_serialized_data_music_album_collected = []
        list_selected_picture_album_for_actor_create = []
        list_selected_video_album_for_actor_create = []
        list_selected_music_album_for_actor_create = []
        list_images_for_actor_profile = []
        q_actor = None
        check_found_actor_by_synonyms = False

        # Request 정보 획득
        selected_actor_id_str = request.POST.get('selected_actor_id') # 기 선택되어 있는 배우, Merge시 사라지는 모델
        sacrificial_actor_id_str = request.POST.get('sacrificial_actor_id') # 새로 선택한 배우, Merge 하고 나서 살아남는 모델
        selected_profile_album_picture_id_str = request.POST.get('selected_profile_album_picture_id')
        input_text_name_str = request.POST.get('input_text_name')
        input_text_synonyms_str = request.POST.get('input_text_synonyms')
        input_date_birthday_str = request.POST.get('input_date_birthday')
        input_number_height_str = request.POST.get('input_number_height')
        input_info_site_name_str = request.POST.get('input_info_site_name')
        input_info_site_url_str = request.POST.get('input_info_site_url')
        selected_site_name_actor_info_str = request.POST.get('selected_site_name_actor_info')
        input_text_tag_str = request.POST.get('input_text_tag')
        selected_filtering_category_id_str = request.POST.get('selected_filtering_category_id')
        list_selected_picture_album_for_actor_create_str = request.POST.get('list_selected_picture_album_for_actor_create')
        list_selected_video_album_for_actor_create_str = request.POST.get('list_selected_video_album_for_actor_create')
        list_selected_music_album_for_actor_create_str = request.POST.get('list_selected_music_album_for_actor_create')


        # Request 정보 필터링 String화
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        sacrificial_actor_id_str = None if sacrificial_actor_id_str in LIST_STR_NONE_SERIES else sacrificial_actor_id_str
        selected_profile_album_picture_id_str = None if selected_profile_album_picture_id_str in LIST_STR_NONE_SERIES else selected_profile_album_picture_id_str
        input_text_name_str = None if input_text_name_str in LIST_STR_NONE_SERIES else input_text_name_str
        input_text_synonyms_str = None if input_text_synonyms_str in LIST_STR_NONE_SERIES else input_text_synonyms_str
        input_date_birthday_str = None if input_date_birthday_str in LIST_STR_NONE_SERIES else input_date_birthday_str
        input_number_height_str = None if input_number_height_str in LIST_STR_NONE_SERIES else input_number_height_str
        input_info_site_name_str = None if input_info_site_name_str in LIST_STR_NONE_SERIES else input_info_site_name_str
        input_info_site_url_str = None if input_info_site_url_str in LIST_STR_NONE_SERIES else input_info_site_url_str
        selected_site_name_actor_info_str = None if selected_site_name_actor_info_str in LIST_STR_NONE_SERIES else selected_site_name_actor_info_str
        input_text_tag_str = None if input_text_tag_str in LIST_STR_NONE_SERIES else input_text_tag_str
        selected_filtering_category_id_str = None if selected_filtering_category_id_str in LIST_STR_NONE_SERIES else selected_filtering_category_id_str
        list_selected_picture_album_for_actor_create_str = None if list_selected_picture_album_for_actor_create_str in LIST_STR_NONE_SERIES else list_selected_picture_album_for_actor_create_str
        list_selected_video_album_for_actor_create_str = None if list_selected_video_album_for_actor_create_str in LIST_STR_NONE_SERIES else list_selected_video_album_for_actor_create_str
        list_selected_music_album_for_actor_create_str = None if list_selected_music_album_for_actor_create_str in LIST_STR_NONE_SERIES else list_selected_music_album_for_actor_create_str
        
        # 선택된 Picture 앨범에서 Actor 찾기 및 앨범 별 대표 이미지 확보
        if list_selected_picture_album_for_actor_create_str is not None:
            list_selected_picture_album_for_actor_create = list_selected_picture_album_for_actor_create_str.split(',')
            list_selected_picture_album_for_actor_create = list(map(int, list_selected_picture_album_for_actor_create))
            qs_picture_album_actor = Picture_Album.objects.filter(id__in=list_selected_picture_album_for_actor_create) 
            if qs_picture_album_actor is not None and len(qs_picture_album_actor) > 0:
                print(f'len(qs_picture_album_actor): {len(qs_picture_album_actor)}')
                for q_picture_album_actor in qs_picture_album_actor:
                    try:
                        picture_album_second_path = q_picture_album_actor.list_dict_picture_album[1]['original']
                    except:
                        picture_album_second_path = None
                    if picture_album_second_path is not None:
                        list_images_for_actor_profile.append(picture_album_second_path)
                for q_picture_album_actor in qs_picture_album_actor:
                    q_actor = q_picture_album_actor.main_actor
                    if q_actor is not None:
                        # 앨범에 등록된 Actor 찾았음
                        break
                print(f'앨범에 등록된 actor는: {q_actor}')

        # 선택된 Video 앨범에서 Actor 찾기
        if list_selected_video_album_for_actor_create_str is not None:
            list_selected_video_album_for_actor_create = list_selected_video_album_for_actor_create_str.split(',')
            list_selected_video_album_for_actor_create = list(map(int, list_selected_video_album_for_actor_create))
            qs_video_album_actor = Video_Album.objects.filter(id__in=list_selected_video_album_for_actor_create) 
            if qs_video_album_actor is not None and len(qs_video_album_actor) > 0:
                for q_video_album_actor in qs_video_album_actor:
                    q_actor = q_video_album_actor.main_actor
                    if q_actor is not None:
                        break
        # 선택된 Music 앨범에서 Actor 찾기
        if list_selected_music_album_for_actor_create_str is not None:
            list_selected_music_album_for_actor_create = list_selected_music_album_for_actor_create_str.split(',')
            list_selected_music_album_for_actor_create = list(map(int, list_selected_music_album_for_actor_create))
            qs_music_album_actor = Music_Album.objects.filter(id__in=list_selected_music_album_for_actor_create) 
            if qs_music_album_actor is not None and len(qs_music_album_actor) > 0:
                for q_music_album_actor in qs_music_album_actor:
                    q_actor = q_music_album_actor.main_actor
                    if q_actor is not None:
                        break

        folder_name_str = request.POST.get('folder_name')
        folder_name_str = None if folder_name_str in LIST_STR_NONE_SERIES else folder_name_str
        
        # 선택된 배우 쿼리 찾기
        print('selected_actor_id_str', selected_actor_id_str)
        print('input_text_name_str', input_text_name_str)

        if q_actor is None:
            print('선택된 Actor 쿼리리가 없는 경우')
            if selected_actor_id_str is not None and selected_actor_id_str != '':
                print('선택된 Actor ID가 있는 경우')
                selected_actor_id = int(selected_actor_id_str)
                q_actor = Actor.objects.get(id=selected_actor_id)
            else:
                print('# 선택된 Actor 쿼리도 ID도 모두 없음. Actor 쿼리 생성하기')
                if request.POST.get('button') == 'create_or_update':
                    if input_text_name_str is not None:
                        print('***************** input_text_name_str', input_text_name_str)
                        q_actor = Actor.objects.filter(Q(check_discard=False) & Q(name__iexact=input_text_name_str)).last()
                        if q_actor is None:
                            q_actor = Actor.objects.filter(Q(check_discard=False) & Q(synonyms__icontains=input_text_name_str)).last()
                            if q_actor is not None:
                                check_found_actor_by_synonyms = True
                                print(' synonyms matched !')
                                pass
                            else:
                                print('no matched')
                                pass
                        else:
                            print('name matched !')
                            pass
                    else:
                        print('입력된 actor 이름 없음')
                        q_actor = create_actor()
        print('q_actor', q_actor)
        
        # Actor Profile Image 수집하기
        if request.POST.get('button') == 'collect_images_for_actor_profile':
            print('Actor Profile Image 수집하기')
            # collect_images_from_registered_picture_album_for_actor_profile_cover_image(q_actor)
            # collect_images_from_registered_video_album_for_actor_profile_cover_image(q_actor)
            collect_images_from_registered_all_album_for_actor_profile_cover_image(q_actor)
            pass

        # 각 Picture 앨범으로 부터 수집된 프로필 사진을 Actor의 profile 리스트에 등록하기
        if q_actor is not None and len(list_images_for_actor_profile) > 0:
            print('Actor Profile Image 수집하기')
            # collect_images_from_registered_picture_album_for_actor_profile_cover_image(q_actor)
            # collect_images_from_registered_video_album_for_actor_profile_cover_image(q_actor)
            collect_images_from_registered_all_album_for_actor_profile_cover_image(q_actor)
            pass


        # 앨범 커버 이미지 변경하기
        if request.POST.get('button') == 'change_profile_album_cover_image':
            if selected_profile_album_picture_id_str is not None and selected_profile_album_picture_id_str != '':
                selected_profile_album_picture_id = int(selected_profile_album_picture_id_str)
                print('selected_profile_album_picture_id', selected_profile_album_picture_id)
                if q_actor is not None:
                    print('1')
                    list_dict_profile_album = q_actor.list_dict_profile_album
                    # acitve 모두 false 변경
                    for dict_profile_album in list_dict_profile_album:
                        if dict_profile_album['id'] == selected_profile_album_picture_id:
                            dict_profile_album['active'] = 'true'
                            print('bingo')
                        else:
                            dict_profile_album['active'] = 'false'
                    data = {'list_dict_profile_album': list_dict_profile_album}
                    Actor.objects.filter(id=q_actor.id).update(**data)
                    q_actor.refresh_from_db()
                else:
                    print('2')
                    pass
        
        # 모델 선택 이미지 삭제하기
        if request.POST.get('button') == 'remove_profile_album_picture':
            print('# 앨범 이미지 삭제하기')
            if selected_profile_album_picture_id_str is not None and selected_profile_album_picture_id_str != '':
                selected_profile_album_picture_id = int(selected_profile_album_picture_id_str)
                print('delete options selected 1:', q_actor)
                print('delete options selected 2:', 'actor')
                print('delete options selected 3:', 'profile')
                print('delete options selected 4:', selected_profile_album_picture_id)
                if q_actor is not None:
                    delete_files_in_list_dict_xxx_album(q_actor, 'actor', 'profile', selected_profile_album_picture_id)
        
        # 모델 통으로 삭제하기
        if request.POST.get('button') == 'remove_actor':
            print('# 앨범 통으로 삭제하기', q_actor)
            if q_actor is not None:
                delete_files_in_list_dict_xxx_album(q_actor, 'actor', 'all', 'all')  ## album 종류(actor, picture, video, music 중 택 1), 싱글 쿼리, 삭제종류('all' or int(id)) 
            
            data = {
                'actor_selected': None,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            q_mysettings_hansent.refresh_from_db() 
            return redirect('hans-ent-actor-list')

        # Merge 위해 새로 선택한 모델 정보 획득
        if sacrificial_actor_id_str is not None and sacrificial_actor_id_str != '':
            if q_actor is not None:
                sacrificial_actor_id = int(sacrificial_actor_id_str)
                q_actor_s = Actor.objects.get(id=sacrificial_actor_id)
            else:
                q_actor_s = None 
        
        # Merge 하기, 선택된 모델에 검색된 모델을 합치기(선택된 모델이 살아남는다.)
        if request.POST.get('button') == 'select_to_merge':
            if q_actor is None:
                q_actor = create_actor()
            q_actor = merge_two_actor_into_one(q_actor, q_actor_s)
            # 기존 모델의 엘범 Main actor 변경하기
            qs_album_picture_s = Picture_Album.objects.filter(main_actor=q_actor_s)
            if qs_album_picture_s is not None and len(qs_album_picture_s) > 0:
                for q_album_picture_s in qs_album_picture_s:
                    data = {'main_actor': q_actor,}
                    Picture_Album.objects.filter(id=q_album_picture_s.id).update(**data)
            qs_album_video_s = Video_Album.objects.filter(main_actor=q_actor_s)
            if qs_album_video_s is not None and len(qs_album_video_s) > 0:
                for q_album_video_s in qs_album_video_s:
                    data = {'main_actor': q_actor,}
                    Video_Album.objects.filter(id=q_album_video_s.id).update(**data)
            # 기존 모델 삭제하기
            data = {"check_discard": True}
            Actor.objects.filter(id=q_actor_s.id).update(**data)
            q_actor_s.refresh_from_db()
        
        # Actor 이름 저장하기
        if input_text_name_str is not None and input_text_name_str != '':
            print('# Actor 이름 저장하기', 'check_found_actor_by_synonyms', check_found_actor_by_synonyms)
            if q_actor is None:
                q_actor = create_actor()
            if check_found_actor_by_synonyms == False:
                data = {
                    'name': input_text_name_str,
                }
                Actor.objects.filter(id=q_actor.id).update(**data)
                q_actor.refresh_from_db()

        # Actor 동의어 저장하기
        if input_text_synonyms_str is not None and input_text_synonyms_str != '':
            print('# Actor 동의어 저장하기')
            if q_actor is None:
                q_actor = create_actor()
            synonyms = q_actor.synonyms
            if synonyms is None:
                synonyms = []
            list_input_text_synonyms_str = []
            if ',' in input_text_synonyms_str:
                list_input_text_synonyms_str = input_text_synonyms_str.split(',')
            else:
                list_input_text_synonyms_str.append(input_text_synonyms_str)
            for item in list_input_text_synonyms_str:
                if item not in synonyms:
                    synonyms.append(item)
            data = {
                'synonyms': synonyms,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()
        
        # 생일 정보 저장하기
        if input_date_birthday_str is not None and input_date_birthday_str != '':
            print('# 생일 정보 저장하기', input_date_birthday_str)
            if q_actor is None:
                q_actor = create_actor()
            date_string = str(input_date_birthday_str)
            date_format = '%Y-%m-%d'
            import datetime
            date_object = datetime.datetime.strptime(date_string, date_format).date()
            data = {
                'date_birth': date_object,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()
        
        # 키 저장하기
        if input_number_height_str is not None and input_number_height_str != '':
            print('# 키 저장하기')
            if q_actor is None:
                q_actor = create_actor()
            input_number_height_int = int(input_number_height_str)
            data = {
                'height': input_number_height_int,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()

        # 카테고리 저장하기
        if selected_filtering_category_id_str is not None and selected_filtering_category_id_str != '':
            print('# 카테고리 저장하기')
            if q_actor is None:
                q_actor = create_actor()
            data = {
                'category': selected_filtering_category_id_str,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()
        
        # Website 등록
        # print('input_info_site_name_str', input_info_site_name_str)
        # print('input_info_site_url_str', input_info_site_url_str)
        # print('selected_site_name_actor_info_str', selected_site_name_actor_info_str)
        if input_info_site_url_str is not None:
            if q_actor is None:
                q_actor = create_actor()
            list_dict_info_url = q_actor.list_dict_info_url
            if list_dict_info_url is None:
                list_dict_info_url = []
                
            if selected_site_name_actor_info_str is not None and selected_site_name_actor_info_str != 'blank':
                # preset에서 선택한 경우
                for DICT_SITE_ACTOR_INFO in LIST_DICT_SITE_ACTOR_INFO:
                    if DICT_SITE_ACTOR_INFO['key'] == selected_site_name_actor_info_str:
                        site_name = DICT_SITE_ACTOR_INFO['name']
                list_dict_info_url.append({"key":input_info_site_name_str, 'name': site_name, "url":input_info_site_url_str})
                data = {
                    'list_dict_info_url': list_dict_info_url,
                }
                Actor.objects.filter(id=q_actor.id).update(**data)
                q_actor.refresh_from_db()
            
            elif input_info_site_name_str is not None:
                # site 이름 직접 입력한 경우
                site_key = None
                for DICT_SITE_ACTOR_INFO in LIST_DICT_SITE_ACTOR_INFO:
                    if DICT_SITE_ACTOR_INFO['name'] == input_info_site_name_str:
                        site_key = DICT_SITE_ACTOR_INFO['key']
                        break 
                if site_key is None:
                    # 이름으로 key 생성
                    site_key = input_info_site_name_str.strip()
                    site_key = site_key.replace(' ', '')
                    site_key = site_key.lower() 
                list_dict_info_url.append({"key":site_key, 'name': input_info_site_name_str, "url":input_info_site_url_str})
                data = {
                    'list_dict_info_url': list_dict_info_url,
                }
                Actor.objects.filter(id=q_actor.id).update(**data)
                q_actor.refresh_from_db()
            else:
                pass 
              
        # Tag 저장하기
        if input_text_tag_str is not None and input_text_tag_str != '':
            print('# Tag 저장하기')
            if q_actor is None:
                q_actor = create_actor()
            tags = q_actor.tags
            if tags is None:
                tags = []
            list_input_text_tag_str = []
            if ',' in input_text_tag_str:
                list_input_text_tag_str = input_text_tag_str.split(',')
            else:
                list_input_text_tag_str.append(input_text_tag_str)
            for item in list_input_text_tag_str:
                if item not in tags:
                    tags.append(item)
            data = {
                'tags': tags,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()

       # Actor Title Keyword 선택하기 (관련 키워드에 해당하는 앨범 표시용 데이터 모집)
        if request.POST.get('button') == 'select_keyword':
            # data = json.loads(request.body)  # parse JSON body
            # list_x = data.get('list_collected_keywords_from_title_selected', [])
            # print(list_x)

            list_collected_keywords_from_title_selected = []
            list_collected_keywords_from_title_selected = request.POST.getlist('list_collected_keywords_from_title_selected[]')
            print('list_collected_keywords_from_title_selected', list_collected_keywords_from_title_selected)
            list_collected_picture_album_id = []
            list_collected_manga_album_id = []
            list_collected_video_album_id = []
            list_collected_music_album_id = []
            if len(list_collected_keywords_from_title_selected) > 0:
                for keyword in list_collected_keywords_from_title_selected:
                    qs_picture_album_searched = Picture_Album.objects.filter(Q(check_discard=False) & (Q(title__icontains=keyword) | Q(tags__contains=keyword)) & Q(main_actor__isnull=True))
                    if qs_picture_album_searched is not None and len(qs_picture_album_searched) > 0:
                        for q_picture_album_searched in qs_picture_album_searched:
                            if q_picture_album_searched.id not in list_collected_picture_album_id:
                                list_collected_picture_album_id.append(q_picture_album_searched.id)
                    qs_video_album_searched = Video_Album.objects.filter(Q(check_discard=False) & (Q(title__icontains=keyword) | Q(tags__contains=keyword)) & Q(main_actor__isnull=True))
                    if qs_video_album_searched is not None and len(qs_video_album_searched) > 0:
                        for q_video_album_searched in qs_video_album_searched:
                            if q_video_album_searched.id not in list_collected_video_album_id:
                                list_collected_video_album_id.append(q_video_album_searched.id)
                    qs_music_album_searched = Music_Album.objects.filter(Q(check_discard=False) & (Q(title__icontains=keyword) | Q(tags__contains=keyword)) & Q(main_actor__isnull=True))
                    if qs_music_album_searched is not None and len(qs_music_album_searched) > 0:
                        for q_music_album_searched in qs_music_album_searched:
                            if q_music_album_searched.id not in list_collected_music_album_id:
                                list_collected_music_album_id.append(q_music_album_searched.id)

            if len(list_collected_picture_album_id) > 0:
                qs_picture_album_collected = Picture_Album.objects.filter(id__in=list_collected_picture_album_id)
                print('qs_picture_album_collected length', len(qs_picture_album_collected))
                if qs_picture_album_collected is not None and len(qs_picture_album_collected) > 0:
                    for q_picture_album_collected in qs_picture_album_collected:
                        dict_picture_album = {}
                        list_dict_picture_album = q_picture_album_collected.list_dict_picture_album
                        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                            for dict_item in list_dict_picture_album:
                                if dict_item['active'] == 'true' and dict_item['discard'] == 'false':
                                    dict_picture_album = dict_item
                        list_picture_url_album = q_picture_album_collected.list_picture_url_album
                        if list_picture_url_album is not None and len(list_picture_url_album) > 0:
                            picture_url = list_picture_url_album[0]
                        else:
                            picture_url = None
                        list_serialized_data_picture_album_collected.append(
                            {
                                'id': q_picture_album_collected.id,
                                'title': q_picture_album_collected.title,
                                'dict_picture_album': dict_picture_album,
                                'picture_url': picture_url,
                            }
                        )
                print(f'len(list_serialized_data_picture_album_collected): {len(list_serialized_data_picture_album_collected)}')

            if len(list_collected_video_album_id) > 0:
                qs_video_album_collected = Video_Album.objects.filter(id__in=list_collected_video_album_id)
                print('qs_video_album_collected length', len(qs_video_album_collected))
                if qs_video_album_collected is not None and len(qs_video_album_collected) > 0:
                    for q_video_album_collected in qs_video_album_collected:
                        dict_picture_album = {}
                        list_dict_picture_album = q_video_album_collected.list_dict_picture_album
                        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                            for dict_item in list_dict_picture_album:
                                if dict_item['active'] == 'true' and dict_item['discard'] == 'false':
                                    dict_picture_album = dict_item
                        dict_video_album = {}
                        list_dict_video_album = q_video_album_collected.list_dict_video_album
                        if list_dict_video_album is not None and len(list_dict_video_album) > 0:
                            for dict_item in list_dict_video_album:
                                if dict_item['active'] == 'true' and dict_item['discard'] == 'false':
                                    dict_video_album = dict_item
                        list_serialized_data_video_album_collected.append(
                            {
                                'id': q_video_album_collected.id,
                                'title': q_video_album_collected.title,
                                'dict_picture_album': dict_picture_album,
                                'dict_video_album': dict_video_album,
                            }
                        )
            if len(list_collected_music_album_id) > 0:
                qs_music_album_collected = Picture_Album.objects.filter(id__in=list_collected_music_album_id)
                print('qs_music_album_collected length', len(qs_music_album_collected))
                if qs_music_album_collected is not None and len(qs_music_album_collected) > 0:
                    for q_music_album_collected in qs_music_album_collected:
                        dict_picture_album = {}
                        list_dict_picture_album = q_music_album_collected.list_dict_picture_album
                        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                            for dict_item in list_dict_picture_album:
                                if dict_item['active'] == 'true' and dict_item['discard'] == 'false':
                                    dict_picture_album = dict_item
                        dict_music_album = {}
                        list_dict_music_album = q_music_album_collected.list_dict_music_album
                        if list_dict_music_album is not None and len(list_dict_music_album) > 0:
                            for dict_item in list_dict_music_album:
                                if dict_item['active'] == 'true' and dict_item['discard'] == 'false':
                                    dict_music_album = dict_item
                        list_serialized_data_music_album_collected.append(
                            {
                                'id': q_music_album_collected.id,
                                'title': q_music_album_collected.title,
                                'dict_picture_album': dict_picture_album,
                                'dict_music_album': dict_music_album,
                            }
                        )

        # Actor Age update 하기
        if q_actor is not None:
            date_birth = q_actor.date_birth
            if date_birth is not None:
                age = calculate_age(date_birth)
                data = {
                    'age': age,
                }
                Actor.objects.filter(id=q_actor.id).update(**data)
                q_actor.refresh_from_db()
        

    
        # Actor를 연결된 Album에 등록하기
        if q_actor is not None:
            print('# Actor를 연결된 Album에 등록하기')
            print('main_actor', q_actor)
            hashcode = q_actor.hashcode
            list_dict_profile_album = q_actor.list_dict_profile_album
            num_item = len(list_dict_profile_album)
            if list_selected_picture_album_for_actor_create is not None and len(list_selected_picture_album_for_actor_create) > 0:
                print('list_selected_picture_album_for_actor_create', list_selected_picture_album_for_actor_create)
                qs_picture_album_actor = Picture_Album.objects.filter(id__in=list_selected_picture_album_for_actor_create) 
                if qs_picture_album_actor is not None and len(qs_picture_album_actor) > 0:
                    for q_picture_album_actor in qs_picture_album_actor:
                        data = {
                            'main_actor': q_actor,
                        }
                        Picture_Album.objects.filter(id=q_picture_album_actor.id).update(**data)
            if list_selected_video_album_for_actor_create is not None and len(list_selected_video_album_for_actor_create) > 0:
                print('video album')
                qs_video_album_actor = Video_Album.objects.filter(id__in=list_selected_video_album_for_actor_create) 
                if qs_video_album_actor is not None and len(qs_video_album_actor) > 0:
                    for q_video_album_actor in qs_video_album_actor:
                        print(q_video_album_actor.id)
                        data = {
                            'main_actor': q_actor,
                        }
                        Video_Album.objects.filter(id=q_video_album_actor.id).update(**data)
                        # video album 커버 이미지를 Actor의 profile 이미지 리스트에 하나씩 등록(Actor 커버이미지 선택시 활용 위해)
                        list_dict_picture_album = q_video_album_actor.list_dict_picture_album
                        
                        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                            for dict_picture_album in list_dict_picture_album:
                                if dict_picture_album['active'] == 'true':
                                    video_cover_image_name_original = dict_picture_album['original']
                                    video_cover_image_name_cover = dict_picture_album['cover']
                                    video_cover_image_thumbnail = dict_picture_album['thumbnail']
                                    input_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_cover_image_name_original)
                                    input_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_cover_image_name_cover)
                                    input_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_cover_image_thumbnail)
                                    
                                    file_extension = video_cover_image_name_original.split('.')[-1]
                                    # print('file_extension', file_extension)
                                    new_image_name_original = f'{hashcode}-o-{num_item}.{file_extension}'
                                    new_image_name_cover = f'{hashcode}-c-{num_item}.{file_extension}'
                                    new_image_name_thumbnail = f'{hashcode}-t-{num_item}.{file_extension}'
                                    output_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, new_image_name_original)
                                    output_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, new_image_name_cover)
                                    output_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, new_image_name_thumbnail)
                                    # print('output_path_original', output_path_original)
                                    # print('output_path_cover', output_path_cover)
                                    # print('output_path_thumbnail', output_path_thumbnail)

                                    # Actor폴더에 이동저장하기
                                    try:
                                        with Image.open(input_path_original) as img:
                                            img.save(output_path_original)
                                    except:
                                        pass
                                    try:
                                        with Image.open(input_path_cover) as img:
                                            img.save(output_path_cover)
                                    except:
                                        pass
                                    try:
                                        with Image.open(input_path_thumbnail) as img:
                                            img.save(output_path_thumbnail)
                                    except:
                                        pass
                                    # 저장한 이미지 path Actor에 등록하기
                                    list_dict_profile_album.append({'id': num_item, 'original': new_image_name_original, 'cover': new_image_name_cover, 'thumbnail': new_image_name_thumbnail, 'active': 'false', 'discard': 'false'})
                                    num_item = num_item + 1

                            data = {
                                'list_dict_profile_album': list_dict_profile_album,
                            }
                            Actor.objects.filter(id=q_actor.id).update(**data)
                            q_actor.refresh_from_db()
                                    
            if list_selected_music_album_for_actor_create is not None and len(list_selected_music_album_for_actor_create) > 0:
                qs_music_album_actor = Music_Album.objects.filter(id__in=list_selected_music_album_for_actor_create) 
                if qs_music_album_actor is not None and len(qs_music_album_actor) > 0:
                    for q_music_album_actor in qs_music_album_actor:
                        data = {
                            'main_actor': q_actor,
                        }
                        Music_Album.objects.filter(id=q_music_album_actor.id).update(**data)
            
           
           
        # 파일 업로드 했으면 저장하기
        if request.FILES:
            print(f'****************************************** 0')
            print('q_actor 0', q_actor)
            print('# 파일 업로드 했으면 저장하기')
            files = request.FILES.getlist('files')
            paths = request.POST.getlist('paths')

            folder_name_str = request.POST.get('folder_name')
            file_upload_option_str = request.POST.get('file_upload_option')
            folder_name_str = None if folder_name_str in LIST_STR_NONE_SERIES else folder_name_str
            file_upload_option_str = None if file_upload_option_str in LIST_STR_NONE_SERIES else file_upload_option_str

            print('folder_name_str', folder_name_str)

            if folder_name_str is not None:
                print(f'****************************************** 1')
                print('q_actor 1', q_actor)
                tree = {}

                for file_obj, relative_path in zip(files, paths):
                    parts = relative_path.strip('/').split('/')
                    current_level = tree

                    for idx, part in enumerate(parts):
                        if idx == len(parts) - 1:
                            # 마지막은 파일
                            current_level.setdefault('files', []).append(part)
                        else:
                            # 폴더
                            current_level = current_level.setdefault('folders', {}).setdefault(part, {})
                print(f'tree: {tree}' )

                if files is not None and len(files) > 0:
                    # save_actor_profile_images(q_actor, images)
                    save_folder_in_list_dict_xxx_album(q_actor, files, tree, folder_name_str, file_upload_option_str)
                
            else:
                print(f'****************************************** 2')
                type_album = 'actor'
                if files is not None and len(files) > 0:
                    print('q_actor 2', q_actor)
                    save_files_in_list_dict_xxx_album(q_actor, files, type_album)

            # Actor Profile용 이미지 수집하기
            collect_images_from_registered_all_album_for_actor_profile_cover_image(q_actor)

        # Data Serialize 하기
        if q_actor is not None:
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'LIST_DICT_SITE_ACTOR_INFO': LIST_DICT_SITE_ACTOR_INFO,
            'LIST_ACTOR_CATEGORY': LIST_ACTOR_CATEGORY,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'list_serialized_data_picture_album_collected': list_serialized_data_picture_album_collected,
            'list_serialized_data_manga_album_collected': list_serialized_data_manga_album_collected,
            'list_serialized_data_video_album_collected': list_serialized_data_video_album_collected,
            'list_serialized_data_music_album_collected': list_serialized_data_music_album_collected,
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)






















#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
# Picture Album  
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################



#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_picture_album_list(request):
    import datetime
    ls_today = datetime.date.today()
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()

    album_type = 'picture'
    if request.method == 'GET':
        if q_systemsettings_hansent is not None:
            parsing_picture_start_page_reverse_count = q_systemsettings_hansent.parsing_picture_start_page_reverse_count
        else:
            parsing_picture_start_page_reverse_count = None
        total_num_registered_item = Picture_Album.objects.count()
        # Searching 결과값 찾기
        list_searched_xxx_id = q_mysettings_hansent.list_searched_picture_album_id
        if list_searched_xxx_id is not None:
            total_num_searched_item = len(list_searched_xxx_id)
        else:
            total_num_searched_item = 0
        # Sorting Submenu 조건
        selected_field_sorting_str = q_mysettings_hansent.selected_field_picture
        selected_category_picture_str = q_mysettings_hansent.selected_category_picture
        # Acending or Decending?
        field_ascending_str = q_mysettings_hansent.check_field_ascending_picture
        if field_ascending_str == False:
            if selected_field_sorting_str == 'score':
                selected_field_sorting = selected_field_sorting_str
            else:
                selected_field_sorting = f'-{selected_field_sorting_str}'
        else:
            if selected_field_sorting_str == 'score':
                selected_field_sorting = f'-{selected_field_sorting_str}'
            else:
                selected_field_sorting = selected_field_sorting_str
        # 화면에 표시할 아이템 개수 지정
        count_page_number = q_mysettings_hansent.count_page_number_picture
        count_page_number_min = (count_page_number - 1) * LIST_NUM_DISPLAY_IN_PAGE
        count_page_number_max = count_page_number * LIST_NUM_DISPLAY_IN_PAGE
        # 쿼리 필터링
        if list_searched_xxx_id is not None and len(list_searched_xxx_id) > 0:
            if selected_category_picture_str == '00':
                print('1')
                qs_xxx = Picture_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
            else:
                print('2')
                qs_xxx = Picture_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id) & Q(category=selected_category_picture_str)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        else:
            if selected_category_picture_str == '00':
                print('3')
                qs_xxx = Picture_Album.objects.filter(Q(check_discard=False)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
            else:
                print('4')
                qs_xxx = Picture_Album.objects.filter(Q(check_discard=False) & Q(category=selected_category_picture_str)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        # print('qs_xxx', len(qs_xxx))

        # Score 계산
        for q_xxx in qs_xxx:
            dict_score_history = q_xxx.dict_score_history
            score = get_score_album(album_type, dict_score_history)
            data = {
                'score': score,
            }
            Picture_Album.objects.filter(id=q_xxx.id).update(**data)

        # Data Serialization            
        list_serialized_data_picture_album = Picture_Album_Serializer(qs_xxx, many=True).data
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_PICTURE': BASE_DIR_PICTURE,
            'BASE_DIR_MANGA': BASE_DIR_MANGA,
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'BASE_DIR_MUSIC': BASE_DIR_MUSIC,
            'LIST_PICTURE_CATEGORY': LIST_PICTURE_CATEGORY,
            'LIST_PICTURE_SORTING_FIELD': LIST_PICTURE_SORTING_FIELD,
            'list_serialized_data_picture_album': list_serialized_data_picture_album,
            'total_num_registered_item': total_num_registered_item,
            'total_num_searched_item': total_num_searched_item,
            'list_count_page_number': [count_page_number_min, count_page_number_max, count_page_number],
            'parsing_picture_start_page_reverse_count': parsing_picture_start_page_reverse_count,
        }
        return JsonResponse(jsondata, safe=False)
   
    if request.method == 'POST':
        print('#################################################', request.POST)

        selected_picture_album_id_str = str(request.POST.get('selected_picture_album_id'))
        selected_picture_album_id_str = None if selected_picture_album_id_str in LIST_STR_NONE_SERIES else selected_picture_album_id_str
        
        # 선택된 앨범 정보 획득
        if selected_picture_album_id_str is not None and selected_picture_album_id_str != '' :
            selected_picture_album_id = int(selected_picture_album_id_str)
            q_picture_album_selected = Picture_Album.objects.get(id=selected_picture_album_id)
        else:
            q_picture_album_selected = None 

        if request.POST.get('button') == 'sorting_items':
            selected_sorting_field_str = request.POST.get('sort_by')
            selected_field_picture = q_mysettings_hansent.selected_field_picture
            check_field_ascending_picture = q_mysettings_hansent.check_field_ascending_picture
            if selected_sorting_field_str == selected_field_picture:
                if check_field_ascending_picture == True:
                    check_field_ascending_picture = False
                else:
                    check_field_ascending_picture = True
            data = {
                'selected_field_picture':selected_sorting_field_str,
                'check_field_ascending_picture': check_field_ascending_picture,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            print('Sorting 조건 확정 및 저장')
            return redirect('hans-ent-picture-album-list')
        
        if request.POST.get('button') == 'category_filtering':
            selected_category_str = request.POST.get('selected_category')
            print('selected_category_str', selected_category_str)
            data = {
                'selected_category_picture': selected_category_str,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            return redirect('hans-ent-picture-album-list')
       
        if request.POST.get('button') == 'page_number_min':
            hans_ent_count_page_number_down(request, q_mysettings_hansent)
            return redirect('hans-ent-picture-album-list')
        
        if request.POST.get('button') == 'page_number_max':
            total_num_registered_item = Picture_Album.objects.count()
            hans_ent_count_page_number_up(request, q_mysettings_hansent, total_num_registered_item)
            return redirect('hans-ent-picture-album-list')

        if request.POST.get('button') == 'get_image_urls_from_given_gallery_url':
            if q_picture_album_selected is not None:
                dict_gallery_info = q_picture_album_selected.dict_gallery_info
                if dict_gallery_info is not None and len(dict_gallery_info) > 0:
                    print(f'# 선택한 앨범의 Gallery URL 정보를 시스템 세팅 DB에 저장하기: {dict_gallery_info}')
                    data = {
                        'dict_gallery_info_for_crawling_image_url': {'id': q_picture_album_selected.id, 'dict_gallery_info': dict_gallery_info}
                    }
                    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                    q_systemsettings_hansent.refresh_from_db()
                    print('백그라운드에서 선택한 앨범의 이미지 URL 수집을 실행합니다.')
                    get_image_url_from_gallery_info_from_views.delay()
                else:
                    print('앨범에 Gallery URL 정보가 없습니다. !!.')
                    pass
            else:
                print('선택된 앨범이 없습니다. !!.')
                pass

        if request.POST.get('button') == 'download_image_from_given_image_url':
            if q_picture_album_selected is not None:
                dict_gallery_info = q_picture_album_selected.dict_gallery_info
                if dict_gallery_info is not None and len(dict_gallery_info) > 0:
                    print(f'# 선택한 앨범의 Gallery URL 정보를 시스템 세팅 DB에 저장하기: {dict_gallery_info}')
                    data = {
                        'dict_gallery_info_for_crawling_image_url': {'id': q_picture_album_selected.id, 'dict_gallery_info': dict_gallery_info}
                    }
                    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                    q_systemsettings_hansent.refresh_from_db()
                    print('백그라운드에서 선택한 앨범의 이미지 URL 수집을 실행합니다.')
                    download_image_from_image_url_info_from_views.delay()
                else:
                    print('앨범에 Gallery URL 정보가 없습니다. !!.')
                    pass
            else:
                print('선택된 앨범이 없습니다. !!.')
                pass
        




        # Delete Duplicated Albums (중복 앨범 모두 삭제하기)
        if request.POST.get('button') == 'delete_duplicated_picture_album':
            # 1. 중복된 title 찾기
            duplicates = (
                Picture_Album.objects.values('title').annotate(title_count=Count('id')).filter(Q(title_count__gt=1) & Q(check_discard=False))
            )
            
            # 2. 중복 title 리스트
            duplicate_titles = [item['title'] for item in duplicates]
                        
            # 3. 각 중복 title에 대해 하나만 남기고 나머지 삭제
            for title in duplicate_titles:
                items = Picture_Album.objects.filter(title=title).order_by('id')
                # 첫 번째 것만 남기고 나머지 삭제
                if len(items) > 1:
                    print(f'length of items, {len(items)}')
                    i = 0
                    for item in items:
                        print(f'item id: {item.id}')
                        if i == 0:
                            pass 
                        else:
                            print(item.id)
                            type_album = 'picture'
                            type_list = 'all'
                            id_delete = 'all'
                            delete_files_in_list_dict_xxx_album(item, type_album, type_list, id_delete)
                        i = i + 1
                # items.exclude(id=items.first().id).delete()
            pass
            
        # Delete Selected Albums (선택 앨범 모두 삭제하기)
        if request.POST.get('button') == 'delete_selected_picture_album':
            print('# Selected Album Delete (선택 앨범 모두 삭제하기)')
            list_picture_album_id_for_checkbox_selection_str = request.POST.getlist('list_picture_album_id_for_checkbox_selection[]')
            list_picture_album_id_for_checkbox_selection = list(map(int, list_picture_album_id_for_checkbox_selection_str))
            qs_picture_album = Picture_Album.objects.filter(id__in=list_picture_album_id_for_checkbox_selection)
            if qs_picture_album is not None and len(qs_picture_album) > 0:
                for q_picture_album_selected in qs_picture_album:
                    delete_files_in_list_dict_xxx_album(q_picture_album_selected, 'picture', 'all', 'all')  ## album 종류(actor, picture, video, music 중 택 1), 싱글 쿼리, 삭제종류('all' or int(id)) 
               

        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_picture_album_list_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
    if request.method == 'GET':
        print('##############################################################', request.GET,)
        keyword_str = request.GET.get('keyword')
        qs_xxx = Picture_Album.objects.filter(Q(check_discard=False) & (Q(title__icontains=keyword_str) | Q(main_actor__name__icontains=keyword_str) | Q(main_actor__synonyms__icontains=keyword_str)))
        list_searched_picture_album_id = []
        if qs_xxx is not None and len(qs_xxx) > 0:
            for q_xxx in qs_xxx:
                list_searched_picture_album_id.append(q_xxx.id)
        data = {
            'list_searched_picture_album_id': list_searched_picture_album_id,
        }
        MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
        return redirect('hans-ent-picture-album-list')
   
    if request.method == 'POST':
        keyword_str = request.POST.get('button')
        if keyword_str == 'reset':
            reset_hans_ent_picture_album_list(q_mysettings_hansent)
        return redirect('hans-ent-picture-album-list')
   



#--------------------------------------------------------------------------------------------------------------------------------------
# @login_required
class hans_ent_picture_album_profile_modal(APIView):
    def get(self, request, format=None):
        jsondata = {'test': 'hello this is actor profile modal'}
        return Response(jsondata)

    def post(self, request, format=None):
        # q_user = request.user
        # q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
        jsondata = {'test': 'hello this is actor profile modal'}
        return Response(jsondata)
    



#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_picture_album_gallery_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == 'GET':
        print('streaming_picture_album_gallery_modal_view GET ======================================================= 1')
        print(request.GET,)
        print('======================================================================================================= 2')
        q_picture_album_selected = q_mysettings_hansent.picture_album_selected
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_picture_album_gallery_modal_view POST ======================================================= 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        selected_serialized_data_actor = {}
        selected_serialized_data_picture_album = {}
        list_serialized_data_picture_album_collected = []
        check_selected_picture_album_favorite = False
        list_picture_album_image_id_for_checkbox_selection_new = []
        check_checkbox_selected = False

        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_picture_album_id_str = request.POST.get('selected_picture_album_id')
        # selected_picture_album_picture_id_str = str(request.POST.get('selected_picture_album_picture_id'))
        dict_picture_album_id_str = request.POST.get('dict_picture_album_id')
        list_picture_album_image_id_for_checkbox_selection_str = request.POST.getlist('list_picture_album_image_id_for_checkbox_selection[]')
        
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        selected_picture_album_id_str = None if selected_picture_album_id_str in LIST_STR_NONE_SERIES else selected_picture_album_id_str
        # selected_picture_album_picture_id_str = None if selected_picture_album_picture_id_str in LIST_STR_NONE_SERIES else selected_picture_album_picture_id_str
        dict_picture_album_id_str = None if dict_picture_album_id_str in LIST_STR_NONE_SERIES else dict_picture_album_id_str
        list_picture_album_image_id_for_checkbox_selection_str = None if list_picture_album_image_id_for_checkbox_selection_str in LIST_STR_NONE_SERIES else list_picture_album_image_id_for_checkbox_selection_str
        

        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        try:
            print(f'selected actor id:  {q_actor.id}, name: {q_actor.name}')
        except:
            pass
            print(f'q_actor, {q_actor}')


        if selected_picture_album_id_str is not None and selected_picture_album_id_str != '':
            selected_picture_album_id = int(selected_picture_album_id_str)
            q_picture_album = Picture_Album.objects.get(id=selected_picture_album_id)
        else:
            q_picture_album = None
        try:
            print(f'q_picture_album id:  {q_picture_album.id}, title: {q_picture_album.title}')
        except:
            pass
            print(f'q_picture_album, {q_picture_album}')
        

        # 커버이미지 등록하기
        if request.POST.get('button') == 'select_image_as_profile_cover':
            print('# 커버이미지 등록하기')
            if dict_picture_album_id_str is not None and q_picture_album is not None:
                dict_picture_album_id = int(dict_picture_album_id_str)
                # print('dict_picture_album_id', dict_picture_album_id)
                list_dict_picture_album = q_picture_album.list_dict_picture_album
                if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                    for dict_picture_album in list_dict_picture_album:
                        if dict_picture_album['id'] == dict_picture_album_id:
                            image_name_original = dict_picture_album['original']
                            # print('image_name_original', image_name_original)
                            save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
                            path_file_name = os.path.join(save_dir, image_name_original)
                            file_extension = path_file_name.split('.')[-1]
                            # print('path_file_name', path_file_name)

                            # get new save image name and path
                            if q_actor is not None:
                                hashcode = q_actor.hashcode
                                list_dict_profile_album = q_actor.list_dict_profile_album
                                # print('list_dict_profile_album', list_dict_profile_album)
                                if list_dict_profile_album is not None and len(list_dict_profile_album) > 0:
                                    num_profile_image = len(list_dict_profile_album)
                                    new_image_name_original = f'{hashcode}-o-{num_profile_image}.{file_extension}'
                                    new_image_name_cover = f'{hashcode}-c-{num_profile_image}.{file_extension}'
                                    new_image_name_thumbnail = f'{hashcode}-t-{num_profile_image}.{file_extension}'

                                    # # Original은 비율맞추기 위해 Padding 추가
                                    # file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, new_image_name_original)
                                    # image_pil = Image.open(file_path_original)
                                    # original_pil = resize_with_padding(image_pil, 260*5, 320*5)
                                    # original_pil.save(file_path_original)

                                    # Cover, Thumbnail은 Crop 후 Resize
                                    file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, new_image_name_original)
                                    file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, new_image_name_cover)
                                    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, new_image_name_thumbnail)
                                    # print('file_path_original', file_path_original)
                                    # print('file_path_cover', file_path_cover)
                                    # print('file_path_thumbnail', file_path_thumbnail)

                                    resize_and_crop(path_file_name, file_path_original, target_size=(1040, 1280))
                                    resize_and_crop(path_file_name, file_path_cover, target_size=(520, 640))
                                    resize_and_crop(path_file_name, file_path_thumbnail, target_size=(260, 320))
                                    
                                    list_dict_profile_album.append({"id": num_profile_image, "original":new_image_name_original, "cover":new_image_name_cover, "thumbnail":new_image_name_thumbnail, "active":"false", "discard":"false"})
                                    
                                    data = {
                                        'list_dict_profile_album': list_dict_profile_album,
                                    }
                                    Actor.objects.filter(id=q_actor.id).update(**data)
                                    q_actor.refresh_from_db()

        # Favorite 상태 변경하기
        if request.POST.get('button') == 'status_favorite_change':
            print('status_favorite_change')
            if q_picture_album is not None:
                dict_score_history = q_picture_album.dict_score_history
                if dict_score_history is None:
                    dict_score_history = DEFAULT_DICT_SCORE_HISTORY_PICTURE
                    check_selected_picture_album_favorite = True
                else:
                    if 'favorite' in dict_score_history:
                        if dict_score_history['favorite'] == 'true':
                            dict_score_history['favorite'] = 'false'
                            check_selected_picture_album_favorite = False
                        else:
                            dict_score_history['favorite'] = 'true'
                            check_selected_picture_album_favorite = True
                    else:
                        dict_score_history['favorite'] = 'true'
                        check_selected_picture_album_favorite = True
                data = {
                    'dict_score_history': dict_score_history,
                }
                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                q_picture_album.refresh_from_db()
        
        # Rating 점수 상향
        if request.POST.get('button') == 'add_rating_score':
            if q_picture_album is not None:
                dict_score_history = q_picture_album.dict_score_history
                if dict_score_history is None:
                    dict_score_history = DEFAULT_DICT_SCORE_HISTORY_PICTURE
                else:
                    if 'rating' in dict_score_history:
                        rating = dict_score_history['rating']
                        rating = rating + 1
                        dict_score_history['rating'] = rating
                    else:
                        dict_score_history['rating'] = 1
                dict_score_history['favorite'] = 'true'
                check_selected_picture_album_favorite = True
                data = {
                    'dict_score_history': dict_score_history,
                }
                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                q_picture_album.refresh_from_db()

        # Gallery images sort_by_CLIP
        if request.POST.get('button') == 'sort_by_CLIP':
            if q_picture_album is not None:
                print('# Gallery images sort_by_CLIP', q_picture_album.id)


        # 선택한 Favorite 상태 확인하기 및 스코어링
        if q_picture_album is not None:
            dict_score_history = q_picture_album.dict_score_history
            if dict_score_history is None:
                dict_score_history = DEFAULT_DICT_SCORE_HISTORY_PICTURE
                check_selected_picture_album_favorite = False
            else:
                if 'rating' not in dict_score_history:
                    dict_score_history['rating'] = 0
                if dict_score_history['favorite'] == 'true':
                    if dict_score_history['rating'] == 0:
                        dict_score_history['rating'] = 1
                    check_selected_picture_album_favorite = True
                else:
                    check_selected_picture_album_favorite = False
            # 방문 점수 카운트
            total_visit_album = dict_score_history['total_visit_album']
            total_visit_album = total_visit_album + 1
            dict_score_history['total_visit_album'] = total_visit_album
            # Score 업데이트             
            album_type='picture'
            score = get_score_album(album_type, dict_score_history)
            print('score', score)
            data = {
                'score': score,
                'dict_score_history': dict_score_history,
            }
            Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
            q_picture_album.refresh_from_db()
        
        # Picture Order 리셋
        if request.POST.get('button') == 'select_picture_album_order_reset':
            print('# Picture Order 리셋')
            if q_picture_album is not None:
                list_dict_picture_album = q_picture_album.list_dict_picture_album
                if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                    list_dict_picture_album = sorted(list_dict_picture_album, key=lambda x: x['id'])
                    i = 1
                    for dict_picture_album in list_dict_picture_album:
                        if 'default' in dict_picture_album['original']:
                            dict_picture_album['id'] = 0
                        else:
                            dict_picture_album['id'] = i
                            i = i + 1
                data = {
                    'list_dict_picture_album': list_dict_picture_album,
                }
                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                q_picture_album.refresh_from_db()

        # Picture Order 변경 - 위로
        if request.POST.get('button') == 'select_image_order_top':
            print('select_image_order_top')
            list_picture_album_image_id_for_checkbox_selection = []
            if q_picture_album is not None:
                if list_picture_album_image_id_for_checkbox_selection_str is not None and len(list_picture_album_image_id_for_checkbox_selection_str) > 0:
                    check_checkbox_selected = True
                    list_picture_album_image_id_for_checkbox_selection = list(map(int, list_picture_album_image_id_for_checkbox_selection_str))
                else:
                    check_checkbox_selected = False
                    if dict_picture_album_id_str is not None and dict_picture_album_id_str != '':
                        dict_picture_album_id = int(dict_picture_album_id_str)
                        list_picture_album_image_id_for_checkbox_selection.append(dict_picture_album_id)
                    else:
                        list_picture_album_image_id_for_checkbox_selection = None
                print('list_picture_album_image_id_for_checkbox_selection', list_picture_album_image_id_for_checkbox_selection)
                if list_picture_album_image_id_for_checkbox_selection is not None and len(list_picture_album_image_id_for_checkbox_selection) > 0:
                    list_picture_album_image_id_for_checkbox_selection.sort(reverse=False)
                    for dict_picture_album_id in list_picture_album_image_id_for_checkbox_selection:
                        if dict_picture_album_id > 1:
                            list_dict_picture_album = q_picture_album.list_dict_picture_album
                            if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                                # print(f'파일 위치 스위칭을 위한 이름 변경 절차 시작, dict_picture_album_id: {dict_picture_album_id}, len(dict_picture_album_id): {len(list_dict_picture_album)}')
                                # 1. selected image -> 임시ID(99999)로 변경
                                # 2. next image -> selected image ID로 변경
                                # 3. 임시 ID -> next image로 ID 변경
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # Step 1: 선택한 이미지의 path 및 이동할 위치의 Temp 폴더 path 찾기기
                                for dict_picture_album in list_dict_picture_album:
                                    if dict_picture_album['id'] == dict_picture_album_id:
                                        # print(f'# Step 1: selected image -> 임시ID(99999)로 변경')
                                        dict_picture_album['id'] = 99999
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # Step 2 : 앞쪽 3개 이미지들 모두 뒤로 한 칸씩 보내야 함.
                                for dict_picture_album in list_dict_picture_album:
                                    if dict_picture_album_id == 2:
                                        if dict_picture_album['id'] == dict_picture_album_id - 1:
                                            print(f'# 앞에 1개 이미지만 있는 경우, 그 이미지를 찾아서 ID + 1 한다. 찾은 이미지: {dict_picture_album_id - 1}')
                                            dict_picture_album['id'] = dict_picture_album_id
                                            print('변경한 id 1', dict_picture_album['id'])
                                    elif dict_picture_album_id == 3:
                                        if dict_picture_album['id'] == dict_picture_album_id - 1:
                                            print(f'# 앞에 2개 이미지만 있는 경우, 바로앞 이미지를 찾아서 ID + 1 한다. 찾은 이미지: {dict_picture_album_id - 1}')
                                            dict_picture_album['id'] = dict_picture_album_id
                                            print('변경한 id 2', dict_picture_album['id'])
                                        if dict_picture_album['id'] == dict_picture_album_id - 2:
                                            print(f'# 앞에 2개 이미지만 있는 경우, 두번째 이미지를 찾아서 ID + 1 한다. 찾은 이미지: {dict_picture_album_id - 2}')
                                            dict_picture_album['id'] = dict_picture_album_id - 1
                                            print('변경한 id 3', dict_picture_album['id'])
                                    elif dict_picture_album_id > 3:
                                        if dict_picture_album['id'] == dict_picture_album_id - 1:
                                            print(f'# 앞에 3개 이미지만 있는 경우, 바로앞 이미지를 찾아서 ID + 1 한다. 찾은 이미지: {dict_picture_album_id - 1}')
                                            dict_picture_album['id'] = dict_picture_album_id
                                            print('변경한 id 4', dict_picture_album['id'])
                                        if dict_picture_album['id'] == dict_picture_album_id - 2:
                                            print(f'# 앞에 3개 이미지만 있는 경우, 두번째 이미지를 찾아서 ID + 1 한다. 찾은 이미지: {dict_picture_album_id - 2}')
                                            dict_picture_album['id'] = dict_picture_album_id - 1
                                            print('변경한 id 5', dict_picture_album['id'])
                                        if dict_picture_album['id'] == dict_picture_album_id - 3:
                                            print(f'# 앞에 3개 이미지만 있는 경우, 세세번째 이미지를 찾아서 ID + 1 한다. 찾은 이미지: {dict_picture_album_id - 3}')
                                            dict_picture_album['id'] = dict_picture_album_id - 2
                                            print('변경한 id 6', dict_picture_album['id'])
                                    else:
                                        print('기타')
                                        pass
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # print('# Step 3 : 임시 ID -> 3칸 앞으로 보냄: 기존 ID - 3 으로 변경')
                                # 임시저장 파일을 Top 위치로 ID 변경
                                for dict_picture_album in list_dict_picture_album:
                                    if dict_picture_album['id'] == 99999 :
                                        if dict_picture_album_id == 2:
                                            print(f'# 앞에 1개 이미지만 있는 경우, 1칸 앞으로: {dict_picture_album_id - 1}')
                                            dict_picture_album['id'] = dict_picture_album_id - 1
                                            list_picture_album_image_id_for_checkbox_selection_new.append(dict_picture_album_id - 1)
                                        elif dict_picture_album_id == 3:
                                            print(f'# 앞에 2개 이미지가 있는 경우, 2칸 앞으로: {dict_picture_album_id - 2}')
                                            dict_picture_album['id'] = dict_picture_album_id - 2
                                            list_picture_album_image_id_for_checkbox_selection_new.append(dict_picture_album_id - 2)
                                        elif dict_picture_album_id > 3:
                                            print(f'# 앞에 3개 이상의 이미지가 있는 경우, 3칸 앞으로: {dict_picture_album_id - 3}')
                                            dict_picture_album['id'] = dict_picture_album_id - 3
                                            list_picture_album_image_id_for_checkbox_selection_new.append(dict_picture_album_id - 3)
                                        else:
                                            pass
                                # 수정내용용 업데이트
                                data = {
                                    'list_dict_picture_album': list_dict_picture_album
                                }
                                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                                q_picture_album.refresh_from_db()
        # Picture Order 변경
        if request.POST.get('button') == 'select_image_order_prev':
            print('select_image_order_prev')
            list_picture_album_image_id_for_checkbox_selection = []
            if q_picture_album is not None:
                if list_picture_album_image_id_for_checkbox_selection_str is not None and len(list_picture_album_image_id_for_checkbox_selection_str) > 0:
                    check_checkbox_selected = True
                    list_picture_album_image_id_for_checkbox_selection = list(map(int, list_picture_album_image_id_for_checkbox_selection_str))
                else:
                    check_checkbox_selected = False
                    if dict_picture_album_id_str is not None and dict_picture_album_id_str != '':
                        dict_picture_album_id = int(dict_picture_album_id_str)
                        list_picture_album_image_id_for_checkbox_selection.append(dict_picture_album_id)
                    else:
                        list_picture_album_image_id_for_checkbox_selection = None
                print('list_picture_album_image_id_for_checkbox_selection', list_picture_album_image_id_for_checkbox_selection)
                if list_picture_album_image_id_for_checkbox_selection is not None and len(list_picture_album_image_id_for_checkbox_selection) > 0:
                    list_picture_album_image_id_for_checkbox_selection.sort(reverse=False)
                    for dict_picture_album_id in list_picture_album_image_id_for_checkbox_selection:
                        if dict_picture_album_id > 1:
                            list_dict_picture_album = q_picture_album.list_dict_picture_album
                            if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                                # print(f'파일 위치 스위칭을 위한 이름 변경 절차 시작, dict_picture_album_id: {dict_picture_album_id}, len(dict_picture_album_id): {len(list_dict_picture_album)}')
                                # 1. selected image -> 임시ID(99999)로 변경
                                # 2. Prev image -> selected image ID로 변경
                                # 3. 임시 ID -> Prev image로 ID 변경
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # Step 1: 선택한 이미지의 path 및 이동할 위치의 Temp 폴더 path 찾기기
                                for dict_picture_album in list_dict_picture_album:
                                    if dict_picture_album['id'] == dict_picture_album_id:
                                        # print(f'# Step 1: selected image -> 임시ID(99999)로 변경')
                                        dict_picture_album['id'] = 99999
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # Step 2 : 바로앞앞 이미지를 선택한 이미지 위치로 변경하기(이름바꾸기를 통해해)
                                for dict_picture_album in list_dict_picture_album:
                                    if dict_picture_album['id'] == dict_picture_album_id - 1:
                                        # print(f'# Step 2 : prev image -> selected image ID로 변경')
                                        dict_picture_album['id'] = dict_picture_album_id
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # print('# Step 3 : 임시 ID -> prev image로 ID 변경')
                                # 임시저장 파일을 앞쪽으로 ID 변경
                                for dict_picture_album in list_dict_picture_album:
                                    if dict_picture_album['id'] == 99999 :
                                        dict_picture_album['id'] = dict_picture_album_id - 1
                                        list_picture_album_image_id_for_checkbox_selection_new.append(dict_picture_album_id - 1)
                                # 수정내용용 업데이트
                                data = {
                                    'list_dict_picture_album': list_dict_picture_album
                                }
                                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                                q_picture_album.refresh_from_db()
                
        # Picture Order 변경
        if request.POST.get('button') == 'select_image_order_next':
            print('select_image_order_next')
            list_picture_album_image_id_for_checkbox_selection = []
            if q_picture_album is not None:
                if list_picture_album_image_id_for_checkbox_selection_str is not None and len(list_picture_album_image_id_for_checkbox_selection_str) > 0:
                    check_checkbox_selected = True
                    list_picture_album_image_id_for_checkbox_selection = list(map(int, list_picture_album_image_id_for_checkbox_selection_str))
                else:
                    check_checkbox_selected = False
                    if dict_picture_album_id_str is not None and dict_picture_album_id_str != '':
                        dict_picture_album_id = int(dict_picture_album_id_str)
                        list_picture_album_image_id_for_checkbox_selection.append(dict_picture_album_id)
                    else:
                        list_picture_album_image_id_for_checkbox_selection = None
                print('list_picture_album_image_id_for_checkbox_selection', list_picture_album_image_id_for_checkbox_selection)
                
                if list_picture_album_image_id_for_checkbox_selection is not None and len(list_picture_album_image_id_for_checkbox_selection) > 0:
                    list_picture_album_image_id_for_checkbox_selection.sort(reverse=True)
                    print('list_picture_album_image_id_for_checkbox_selection', list_picture_album_image_id_for_checkbox_selection)
                    for dict_picture_album_id in list_picture_album_image_id_for_checkbox_selection:
                        list_dict_picture_album = q_picture_album.list_dict_picture_album
                        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                            if dict_picture_album_id < len(list_dict_picture_album):
                                # print(f'파일 위치 스위칭을 위한 이름 변경 절차 시작, dict_picture_album_id: {dict_picture_album_id}, len(dict_picture_album_id): {len(list_dict_picture_album)}')
                                # 1. selected image -> 임시ID(99999)로 변경
                                # 2. next image -> selected image ID로 변경
                                # 3. 임시 ID -> next image로 ID 변경
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # Step 1: 선택한 이미지의 path 및 이동할 위치의 Temp 폴더 path 찾기기
                                for dict_picture_album in list_dict_picture_album:
                                    if dict_picture_album['id'] == dict_picture_album_id:
                                        # print(f'# Step 1: selected image -> 임시ID(99999)로 변경')
                                        dict_picture_album['id'] = 99999
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # Step 2 : Next 이미지를 선택한 이미지 위치로 변경하기(이름바꾸기를 통해해)
                                for dict_picture_album in list_dict_picture_album:
                                    if dict_picture_album['id'] == dict_picture_album_id + 1:
                                        # print(f'# Step 2 : next image -> selected image ID로 변경')
                                        dict_picture_album['id'] = dict_picture_album_id
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # print('# Step 3 : 임시 ID -> next image로 ID 변경')
                                # 임시저장 파일을 Next 이름으로 변경(input, output)
                                for dict_picture_album in list_dict_picture_album:
                                    if dict_picture_album['id'] == 99999 :
                                        dict_picture_album['id'] = dict_picture_album_id + 1
                                        list_picture_album_image_id_for_checkbox_selection_new.append(dict_picture_album_id + 1)
                                # 수정내용용 업데이트
                                data = {
                                    'list_dict_picture_album': list_dict_picture_album
                                }
                                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                                q_picture_album.refresh_from_db()
        
        # Picture Order 변경 - 위로로
        if request.POST.get('button') == 'select_image_order_bottom':
            print('select_image_order_bottom')
            list_picture_album_image_id_for_checkbox_selection = []
            if q_picture_album is not None:
                if list_picture_album_image_id_for_checkbox_selection_str is not None and len(list_picture_album_image_id_for_checkbox_selection_str) > 0:
                    check_checkbox_selected = True
                    list_picture_album_image_id_for_checkbox_selection = list(map(int, list_picture_album_image_id_for_checkbox_selection_str))
                else:
                    check_checkbox_selected = False
                    if dict_picture_album_id_str is not None and dict_picture_album_id_str != '':
                        dict_picture_album_id = int(dict_picture_album_id_str)
                        list_picture_album_image_id_for_checkbox_selection.append(dict_picture_album_id)
                    else:
                        list_picture_album_image_id_for_checkbox_selection = None
                print('list_picture_album_image_id_for_checkbox_selection', list_picture_album_image_id_for_checkbox_selection)
                
                if list_picture_album_image_id_for_checkbox_selection is not None and len(list_picture_album_image_id_for_checkbox_selection) > 0:
                    list_picture_album_image_id_for_checkbox_selection.sort(reverse=True)
                    print('list_picture_album_image_id_for_checkbox_selection', list_picture_album_image_id_for_checkbox_selection)
                    for dict_picture_album_id in list_picture_album_image_id_for_checkbox_selection:
                        print('dict_picture_album_id', dict_picture_album_id)
                        list_dict_picture_album = q_picture_album.list_dict_picture_album
                        list_dict_picture_album_filtered = []
                        list_dict_picture_album_filtered_out = []
                        for dict_picture_album in list_dict_picture_album:
                            if dict_picture_album['discard'] == 'false':
                                list_dict_picture_album_filtered.append(dict_picture_album)
                            else:
                                list_dict_picture_album_filtered_out.append(dict_picture_album)
                        print('list_dict_picture_album_filtered length', len(list_dict_picture_album_filtered))
                        if list_dict_picture_album_filtered is not None and len(list_dict_picture_album_filtered) > 0:
                            if dict_picture_album_id < len(list_dict_picture_album_filtered) + 1:
                                print(f'파일 위치 스위칭을 위한 이름 변경 절차 시작, dict_picture_album_id: {dict_picture_album_id}, len(dict_picture_album_id): {len(list_dict_picture_album)}')
                                # 1. selected image -> 임시ID(99999)로 변경
                                # 2. next image -> selected image ID로 변경
                                # 3. 임시 ID -> next image로 ID 변경
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # Step 1: 선택한 이미지의 path 및 이동할 위치의 Temp 폴더 path 찾기기
                                # if dict_picture_album_id != len(list_dict_picture_album_filtered):
                                for dict_picture_album in list_dict_picture_album_filtered:
                                    if dict_picture_album['id'] == dict_picture_album_id:
                                        print(f'# Step 1: selected image -> 임시ID(99999)로 변경')
                                        dict_picture_album['id'] = 99999
                                # --------------------------------------------------------------------------------------------------------------------------------
                                 # Step 2 : 뒤쪽 3개 이미지들 모두 앞앞로 한 칸씩 보내야 함.
                                for dict_picture_album in list_dict_picture_album_filtered:
                                    if dict_picture_album_id == len(list_dict_picture_album_filtered) - 1:
                                        if dict_picture_album['id'] == dict_picture_album_id + 1:
                                            print(f'# 뒤에 1개 이미지만 있는 경우, 그 이미지를 찾아서 ID - 1 한다. 찾은 이미지: {dict_picture_album_id + 1}')
                                            dict_picture_album['id'] = dict_picture_album_id
                                            print('변경한 id 1', dict_picture_album['id'])
                                    elif dict_picture_album_id == len(list_dict_picture_album_filtered) -2:
                                        if dict_picture_album['id'] == dict_picture_album_id + 1:
                                            print(f'# 뒤에 2개 이미지만 있는 경우, 바로 뒤 이미지를 찾아서 ID - 1 한다. 찾은 이미지: {dict_picture_album_id + 1}')
                                            dict_picture_album['id'] = dict_picture_album_id
                                            print('변경한 id 2', dict_picture_album['id'])
                                        if dict_picture_album['id'] == dict_picture_album_id + 2:
                                            print(f'# 뒤에 2개 이미지만 있는 경우, 두번째 이미지를 찾아서 ID - 1 한다. 찾은 이미지: {dict_picture_album_id + 2}')
                                            dict_picture_album['id'] = dict_picture_album_id + 1
                                            print('변경한 id 3', dict_picture_album['id'])
                                    elif dict_picture_album_id < len(list_dict_picture_album_filtered) - 2:
                                        if dict_picture_album['id'] == dict_picture_album_id + 1:
                                            print(f'# 뒤에 3개 이미지만 있는 경우, 바로 뒤 이미지를 찾아서 ID + 1 한다. 찾은 이미지: {dict_picture_album_id + 1}')
                                            dict_picture_album['id'] = dict_picture_album_id
                                            print('변경한 id 4', dict_picture_album['id'])
                                        if dict_picture_album['id'] == dict_picture_album_id + 2:
                                            print(f'# 뒤에 3개 이미지만 있는 경우, 두번째 이미지를 찾아서 ID + 1 한다. 찾은 이미지: {dict_picture_album_id + 2}')
                                            dict_picture_album['id'] = dict_picture_album_id + 1
                                            print('변경한 id 5', dict_picture_album['id'])
                                        if dict_picture_album['id'] == dict_picture_album_id + 3:
                                            print(f'# 뒤에 3개 이미지만 있는 경우, 세번째 이미지를 찾아서 ID + 1 한다. 찾은 이미지: {dict_picture_album_id + 3}')
                                            dict_picture_album['id'] = dict_picture_album_id + 2
                                            print('변경한 id 6', dict_picture_album['id'])
                                    else:
                                        # print('기타')
                                        pass
                                # --------------------------------------------------------------------------------------------------------------------------------
                                # print('# Step 3 : 임시 ID -> 3칸 앞으로 보냄: 기존 ID - 3 으로 변경')
                                # 임시저장 파일을 Top 위치로 ID 변경
                                for dict_picture_album in list_dict_picture_album_filtered:
                                    if dict_picture_album['id'] == 99999 :
                                        if dict_picture_album_id == len(list_dict_picture_album_filtered):
                                            dict_picture_album['id'] = dict_picture_album_id
                                            list_picture_album_image_id_for_checkbox_selection_new.append(dict_picture_album_id)
                                        elif dict_picture_album_id == len(list_dict_picture_album_filtered) - 1:
                                            print(f'# 뒤에 1개 이미지만 있는 경우, 1칸 앞으로: {dict_picture_album_id + 1}')
                                            dict_picture_album['id'] = dict_picture_album_id + 1
                                            list_picture_album_image_id_for_checkbox_selection_new.append(dict_picture_album_id + 1)
                                        elif dict_picture_album_id == len(list_dict_picture_album_filtered) -2:
                                            print(f'# 뒤에 2개 이미지가 있는 경우, 2칸 앞으로: {dict_picture_album_id + 2}')
                                            dict_picture_album['id'] = dict_picture_album_id + 2
                                            list_picture_album_image_id_for_checkbox_selection_new.append(dict_picture_album_id + 2)
                                        elif dict_picture_album_id < len(list_dict_picture_album_filtered) - 2:
                                            print(f'# 뒤에 3개 이상의 이미지가 있는 경우, 3칸 앞으로: {dict_picture_album_id + 3}')
                                            dict_picture_album['id'] = dict_picture_album_id + 3
                                            list_picture_album_image_id_for_checkbox_selection_new.append(dict_picture_album_id + 3)
                                        else:
                                            # print('기타2')
                                            pass
                                # 수정내용용 업데이트
                                if list_dict_picture_album_filtered_out is not None and len(list_dict_picture_album_filtered_out) > 0:
                                    j = 1
                                    for dict_picture_album_filtered_out in list_dict_picture_album_filtered_out:
                                        if dict_picture_album_filtered_out['id'] != 0:
                                            dict_picture_album_filtered_out['id'] = len(list_dict_picture_album_filtered) + j
                                            j = j + 1
                                list_dict_picture_album_filtered = list_dict_picture_album_filtered + list_dict_picture_album_filtered_out
                                data = {
                                    'list_dict_picture_album': list_dict_picture_album_filtered,
                                }
                                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                                q_picture_album.refresh_from_db()
                                

        # Data Serialization
        if q_picture_album is not None: 
            if q_actor is None:
                q_actor = q_picture_album.main_actor
            selected_serialized_data_picture_album = Picture_Album_Serializer(q_picture_album, many=False).data
        if q_actor is not None:
            print('q_actor', q_actor)
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data
        if check_checkbox_selected == False:
            list_picture_album_image_id_for_checkbox_selection_new = []
        
        
        jsondata = {
            'check_selected_picture_album_favorite': check_selected_picture_album_favorite,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_picture_album': selected_serialized_data_picture_album,
            'list_serialized_data_picture_album_collected': list_serialized_data_picture_album_collected,
            'list_picture_album_image_id_for_checkbox_selection': list_picture_album_image_id_for_checkbox_selection_new,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)




#--------------------------------------------------------------------------------------------------------------------------------------
# @login_required
class hans_ent_picture_album_gallery_fullscreen_modal(APIView):
    def get(self, request, format=None):
        jsondata = {'test': 'hello this is picture profile modal'}
        return Response(jsondata)
    def post(self, request, format=None):
        jsondata = {'test': 'hello this is picture profile modal'}
        return Response(jsondata)
    


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_picture_album_update_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    
    if request.method == "GET":
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'GET':
        selected_serialized_data_actor = {}
        selected_serialized_data_picture_album = {}
        q_picture_album_selected = q_mysettings_hansent.picture_album_selected
        # Get selected_serialized_data
        if q_picture_album_selected is not None:
            selected_serialized_data_picture_album = Picture_Album_Serializer(q_picture_album_selected, many=False).data
            if q_picture_album_selected.main_actor:
                selected_serialized_data_actor = Actor_Serializer(q_picture_album_selected.main_actor, many=False).data
            else:
                q_actor = q_mysettings_hansent.actor_selected
                if q_actor is not None:
                    selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data
        # Jsondata
        jsondata = {
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_picture_album': selected_serialized_data_picture_album,
        }
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_picture_album_update_modal_view POST ========================================================== 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        
        selected_serialized_data_picture_album = {}
        selected_serialized_data_actor = {}
                
        selected_picture_album_id_str = str(request.POST.get('selected_picture_album_id'))
        selected_picture_album_picture_id_str = str(request.POST.get('selected_picture_album_picture_id'))
        selected_actor_id_str = request.POST.get('selected_actor_id')
        input_text_title_str = request.POST.get('input_text_title')
        input_text_name_str = request.POST.get('input_text_name')
        input_text_studio_str = request.POST.get('input_text_studio')
        input_date_released_str = request.POST.get('input_date_released')
        input_text_tag_str = request.POST.get('input_text_tag')
        selected_picture_sub_type_str = request.POST.get('selected_picture_sub_type')
        selected_filtering_category_id_str = request.POST.get('selected_filtering_category_id')
        
        selected_picture_album_id_str = None if selected_picture_album_id_str in LIST_STR_NONE_SERIES else selected_picture_album_id_str
        selected_picture_album_picture_id_str = None if selected_picture_album_picture_id_str in LIST_STR_NONE_SERIES else selected_picture_album_picture_id_str
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        input_text_title_str = None if input_text_title_str in LIST_STR_NONE_SERIES else input_text_title_str
        input_text_name_str = None if input_text_name_str in LIST_STR_NONE_SERIES else input_text_name_str
        input_text_studio_str = None if input_text_studio_str in LIST_STR_NONE_SERIES else input_text_studio_str
        input_date_released_str = None if input_date_released_str in LIST_STR_NONE_SERIES else input_date_released_str
        selected_picture_sub_type_str = None if selected_picture_sub_type_str in LIST_STR_NONE_SERIES else selected_picture_sub_type_str
        selected_filtering_category_id_str = None if selected_filtering_category_id_str in LIST_STR_NONE_SERIES else selected_filtering_category_id_str
        
        folder_name_str = request.POST.get('folder_name')
        folder_name_str = None if folder_name_str in LIST_STR_NONE_SERIES else folder_name_str
        file_upload_option_str = request.POST.get('file_upload_option')
        file_upload_option_str = None if file_upload_option_str in LIST_STR_NONE_SERIES else file_upload_option_str
        input_info_site_name_str = request.POST.get('input_info_site_name')
        input_info_site_url_str = request.POST.get('input_info_site_url')
        input_info_site_name_str = None if input_info_site_name_str in LIST_STR_NONE_SERIES else input_info_site_name_str
        input_info_site_url_str = None if input_info_site_url_str in LIST_STR_NONE_SERIES else input_info_site_url_str

        print('************* selected_actor_id_str', selected_actor_id_str)
        print('selected_picture_album_id_str', selected_picture_album_id_str)

        # 선택된 모델 정보 획득
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        print('************************** q_actor', q_actor)
        
        
        # 선택된 앨범 정보 획득
        if selected_picture_album_id_str is not None and selected_picture_album_id_str != '' :
            selected_picture_album_id = int(selected_picture_album_id_str)
            q_picture_album_selected = Picture_Album.objects.get(id=selected_picture_album_id)
        else:
            q_picture_album_selected = None 
       
        # Pictuer Album 쿼리 생성하기
        if request.POST.get('button') == 'create_or_update':
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
                if q_actor is not None:
                    if q_picture_album_selected.main_actor is None:
                        data = {'main_actor':q_actor}
                        Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                        q_picture_album_selected.refresh_from_db()
                
        # Pictuer Album Refresh 하기
        if request.POST.get('button') == 'refresh_selected_album':
            if q_picture_album_selected is not None:
                print('# Pictuer Album Refresh 하기')
                selected_vault = q_picture_album_selected.selected_vault
                dict_picture_album_cover = q_picture_album_selected.dict_picture_album_cover
                list_dict_picture_album = q_picture_album_selected.list_dict_picture_album
                list_picture_url_album = q_picture_album_selected.list_picture_url_album
                dict_gallery_info = q_picture_album_selected.dict_gallery_info
                RELATIVE_PATH_PICTURE = f'{selected_vault}/picture'

                list_count_original_exist = []
                if len(list_dict_picture_album) > 1:
                    for dict_picture_album in list_dict_picture_album:
                        image_name_original = dict_picture_album['original']
                        image_name_cover = dict_picture_album['cover']
                        image_name_thumbnail = dict_picture_album['thumbnail']

                        image_original_file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_original)
                        image_cover_file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
                        image_thumbnail_file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)
                        # print(f'image_original_file_path: {image_original_file_path}')

                        if os.path.exists(image_original_file_path):
                            list_count_original_exist.append(True)
                            # print('1')
                            if not os.path.exists(image_cover_file_path):
                                # print('2')
                                image_pil = Image.open(image_original_file_path)
                                cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
                                cover_pil.save(image_cover_file_path)
                            if not os.path.exists(image_thumbnail_file_path):
                                # print('3')
                                image_pil = Image.open(image_original_file_path)
                                thumbnail_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
                                thumbnail_pil.save(image_thumbnail_file_path)
                        else:
                            list_count_original_exist.append(False)
                    
                    if list_count_original_exist.count(True)/len(list_count_original_exist) < 0.5:
                        # original이 저장된 확률이 50% 미만이면 다시 다운받는다.
                        if list_picture_url_album is not None and len(list_picture_url_album) > list_count_original_exist.count(True):
                            print(f'# Background로 URL 이미지 다운로드 수행: {q_picture_album_selected.id}')
                            data = {
                                'selected_picture_album_id': q_picture_album_selected.id
                            }
                            SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                            download_image_using_url_w_multiprocessing_for_selected_album_only.delay()
                            
                            # dict_gallery_info = dict_gallery_info
                            # gallery_url = dict_gallery_info['url']
                            # gallery_title = dict_gallery_info['title']


        # 앨범 선택 이미지 삭제하기
        if request.POST.get('button') == 'remove_picture_album_picture':
            print('# 앨범 이미지 삭제하기')
            if selected_picture_album_picture_id_str is not None and selected_picture_album_picture_id_str != '':
                selected_picture_album_picture_id = int(selected_picture_album_picture_id_str)
                if q_picture_album_selected is not None:
                    delete_files_in_list_dict_xxx_album(q_picture_album_selected, 'picture', 'image', selected_picture_album_picture_id)

        # 앨범 통으로 삭제하기
        if request.POST.get('button') == 'remove_picture_album':
            print('# 앨범 통으로 삭제하기', q_picture_album_selected)
            if q_picture_album_selected is not None:
                delete_files_in_list_dict_xxx_album(q_picture_album_selected, 'picture', 'all', 'all')  ## album 종류(actor, picture, video, music 중 택 1), 싱글 쿼리, 삭제종류('all' or int(id)) 
            return redirect('hans-ent-picture-album-list')

        # 앨범 커버 이미지 변경하기
        if request.POST.get('button') == 'change_picture_album_cover_image':
            if selected_picture_album_picture_id_str is not None and selected_picture_album_picture_id_str != '':
                selected_picture_album_picture_id = int(selected_picture_album_picture_id_str)
                print(f'selected_picture_album_picture_id: {selected_picture_album_picture_id}')
                if q_picture_album_selected is not None:
                    list_dict_picture_album = q_picture_album_selected.list_dict_picture_album
                    # acitve 모두 false 변경
                    for dict_picture_album in list_dict_picture_album:
                        dict_picture_album['active'] = 'false'
                        if dict_picture_album['id'] == selected_picture_album_picture_id:
                            dict_picture_album['active'] = 'true'
                    data = {'list_dict_picture_album': list_dict_picture_album}
                    print(f'list_dict_picture_album: {list_dict_picture_album}')
                    Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                    q_picture_album_selected.refresh_from_db()
        
        # 업로드 타이틀 정보 저장하기
        if input_text_title_str is not None and input_text_title_str != '':
            print('# 업로드 타이틀 정보 저장하기')
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
            data = {
                'title': input_text_title_str,
            }
            Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
            q_picture_album_selected.refresh_from_db()
            
        # 업로드 모델이름 저장하기
        if input_text_name_str is not None and input_text_name_str != '':
            print('# 업로드 모델이름 저장하기')
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
            data = {
                'name': input_text_name_str,
            }
            Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
            q_picture_album_selected.refresh_from_db()
        
        # 업로드 스튜디오 정보 저장하기
        if input_text_studio_str is not None and input_text_studio_str != '':
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
            data = {
                'studio': input_text_studio_str,
            }
            Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
            q_picture_album_selected.refresh_from_db()

        # 사진 앨범 타입 선택하기
        if selected_picture_sub_type_str is not None and selected_picture_sub_type_str != '':
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
            data = {
                'types': selected_picture_sub_type_str,
            }
            Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
            q_picture_album_selected.refresh_from_db()

        # 업로드 출시일 정보 저장하기
        if input_date_released_str is not None and input_date_released_str != '':
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
            date_string = str(input_date_released_str)
            date_format = '%Y-%m-%d'
            # date_released = datetime.strftime(input_date_released_str, date_format).date()
            import datetime
            date_object = datetime.datetime.strptime(date_string, date_format).date()
            data = {
                'date_released': date_object,
            }
            Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
            q_picture_album_selected.refresh_from_db()
        
        # 카테고리 저장하기
        if selected_filtering_category_id_str is not None and selected_filtering_category_id_str != '':
            print('# 카테고리 저장하기')
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
            data = {
                'category': selected_filtering_category_id_str,
            }
            Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
            q_picture_album_selected.refresh_from_db()

        # Website 등록
        print('input_info_site_url_str', input_info_site_url_str)
        if input_info_site_name_str is not None and input_info_site_name_str != '':
            print('# Website 등록')
            if input_info_site_url_str is not None and input_info_site_url_str != '':
                if q_picture_album_selected is None:
                    q_picture_album_selected = create_picture_album()
                list_dict_info_url = q_picture_album_selected.list_dict_info_url
                if list_dict_info_url is None:
                    list_dict_info_url = []
                if input_info_site_name_str not in list_dict_info_url:
                    list_dict_info_url.append({"name":input_info_site_name_str, "url":input_info_site_url_str})
                    data = {
                        'list_dict_info_url': list_dict_info_url,
                    }
                    Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                    q_picture_album_selected.refresh_from_db()

        # Tag 저장하기
        if input_text_tag_str is not None and input_text_tag_str != '':
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
            tags = q_picture_album_selected.tags
            if tags is None:
                tags = []
            if input_text_tag_str not in tags:
                print('tag save', input_text_tag_str)
                tags.append(input_text_tag_str)
            data = {
                'tags': tags,
            }
            Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
            q_picture_album_selected.refresh_from_db()


        # 모델 선택하기
        if request.POST.get('button') == 'actor_select':
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
            if q_picture_album_selected is not None and q_actor is not None:
                print('선택된 모델', q_actor)
                data = {
                    'main_actor': q_actor,
                }
                Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                q_picture_album_selected.refresh_from_db()

        # 모델 선택해제하기
        if request.POST.get('button') == 'actor_select_reset':
            print('# 모델 선택해제하기')
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
            if q_picture_album_selected is not None:
                data = {
                    'main_actor': None,
                }
                Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                q_picture_album_selected.refresh_from_db() 

        # 이미지 업로드 했으면 저장하기
        if request.FILES:
            print('request.FILES', request.FILES)
            if q_picture_album_selected is not None:
                print('# 앨범 갤러이 이미지 저장하기')
                files = request.FILES.getlist('files')
                if files is not None and len(files) > 0:
                    # save_picture_album_images(q_picture_album_selected, files)
                    save_files_in_list_dict_xxx_album(q_picture_album_selected, files, type_album='picture')
                    data = {
                        'check_4k_uploaded': True,
                    }
                    Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                    q_picture_album_selected.refresh_from_db()

        # 신규 Picture Album 생성
        if request.POST.get('button') == 'create_picture_album':
            q_actor = None 
            q_picture_album_selected = None
            print('good luck~!')
            pass

        # 파일만 업로드 했으면 폴더명으로 추가정보 기입하기
        """
        File Upload Options:
            folder_name_for_nothing
            folder_name_as_album_title
            folder_name_as_actor_name
            folder_name_as_album_title_and_actor_name
        """
        if folder_name_str is not None:
            print('# 파일만 업로드 했으면 폴더명으로 추가정보 기입하기 : ', file_upload_option_str)
            if q_picture_album_selected is not None:
                if file_upload_option_str == 'folder_name_for_nothing':
                    pass
                elif file_upload_option_str == 'folder_name_as_album_title':
                    data = {
                        'title': folder_name_str,
                    }
                    Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                    q_picture_album_selected.refresh_from_db() 
                elif file_upload_option_str == 'folder_name_as_actor_name':
                    q_actor = Actor.objects.filter(Q(check_discard=False) & Q(name=folder_name_str)).last()
                    if q_actor is None:
                        q_actor = create_actor()
                        data = {
                            'name':folder_name_str,
                        }
                        Actor.objects.filter(id=q_actor.id).update(**data)
                        q_actor.refresh_from_db()
                    data = {
                        'main_actor': q_actor,
                    }
                    Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                    q_picture_album_selected.refresh_from_db() 
                elif file_upload_option_str == 'folder_name_as_album_title_and_actor_name':
                    q_actor = Actor.objects.filter(Q(check_discard=False) & Q(name=folder_name_str)).last()
                    if q_actor is None:
                        q_actor = create_actor()
                        data = {
                            'name':folder_name_str,
                        }
                        Actor.objects.filter(id=q_actor.id).update(**data)
                        q_actor.refresh_from_db()
                    data = {
                        'title': folder_name_str,
                        'main_actor': q_actor,
                    }
                    Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                    q_picture_album_selected.refresh_from_db() 

        # Data Serialization
        if q_picture_album_selected is not None:
            print(f'# 앨범이 등록되어 있다면: {q_picture_album_selected}')
            print('q_actor', q_actor)
            if q_actor is None:
                q_actor = q_picture_album_selected.main_actor
               
            # Settings에 선택된 Album 쿼리 등록
            print('세팅에 현재 앨범 등록하기', q_mysettings_hansent)
            data = {
                'picture_album_selected': q_picture_album_selected
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            q_mysettings_hansent.refresh_from_db()

            # main actor 등록
            if q_picture_album_selected.main_actor is None:
                data = {"main_actor": q_actor}
                Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                q_picture_album_selected.refresh_from_db()

            # Data Serialize
            selected_serialized_data_picture_album = Picture_Album_Serializer(q_picture_album_selected, many=False).data
        
        if q_actor is not None:
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'LIST_PICTURE_CATEGORY': LIST_PICTURE_CATEGORY,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_picture_album': selected_serialized_data_picture_album,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)  




#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_picture_album_update_modal_actor_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == "GET":
        print('*********************************************************************** get: ', request)
        keyword_str = request.GET.get('keyword')
        print('keyword_str', keyword_str)
        qs_xxx = Actor.objects.filter(Q(check_discard=False) & (Q(name__icontains=keyword_str) | Q(synonyms__icontains=keyword_str)))
        list_serialized_data_actor = []
        if qs_xxx is not None and len(qs_xxx) > 0:
            list_serialized_data_actor = Actor_Serializer(qs_xxx, many=True).data
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'list_serialized_data_actor': list_serialized_data_actor, 
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)

    if request.method == 'POST':
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)













#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
# Manga Album  
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################



#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_manga_album_list(request):
    import datetime
    ls_today = datetime.date.today()
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    album_type = 'manga'
    if request.method == 'GET':
        total_num_registered_item = Manga_Album.objects.count()
        # Searching 결과값 찾기
        list_searched_xxx_id = q_mysettings_hansent.list_searched_manga_album_id
        if list_searched_xxx_id is not None:
            total_num_searched_item = len(list_searched_xxx_id)
        else:
            total_num_searched_item = 0
        # Sorting Submenu 조건
        selected_field_sorting_str = q_mysettings_hansent.selected_field_manga
        selected_category_manga_str = q_mysettings_hansent.selected_category_manga
        # Acending or Decending?
        field_ascending_str = q_mysettings_hansent.check_field_ascending_manga

        print("selected_field_sorting_str", selected_field_sorting_str)
        print('field_ascending_str', field_ascending_str)

        if field_ascending_str == False:
            print('field ascending FALSE')
            if selected_field_sorting_str == 'score':
                print('score')
                selected_field_sorting = f'-{selected_field_sorting_str}'
            else:
                print('NO score')
                selected_field_sorting = f'-{selected_field_sorting_str}'
        else:
            print('field ascending TRUE')
            if selected_field_sorting_str == 'score':
                print('score')
                selected_field_sorting = selected_field_sorting_str
            else:
                print('NO score')
                selected_field_sorting = selected_field_sorting_str

        # 화면에 표시할 아이템 개수 지정
        count_page_number = q_mysettings_hansent.count_page_number_manga
        count_page_number_min = (count_page_number - 1) * LIST_NUM_DISPLAY_IN_PAGE
        count_page_number_max = count_page_number * LIST_NUM_DISPLAY_IN_PAGE
        # print('count_page_number_min', count_page_number_min)
        # print('count_page_number_max', count_page_number_max)

        check_switch_manga_complete_hide = q_mysettings_hansent.check_switch_manga_complete_hide
        check_switch_manga_new_volume_update_only = q_mysettings_hansent.check_switch_manga_new_volume_update_only

        
        # 쿼리 필터링
        if list_searched_xxx_id is not None and len(list_searched_xxx_id) > 0:
            if selected_category_manga_str == '00':
                print('1')
                qs_xxx = Manga_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
            else:
                print('2')
                qs_xxx = Manga_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id) & Q(category=selected_category_manga_str)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        else:
            if selected_category_manga_str == '00':
                print('3')
                if selected_field_sorting_str == 'title':
                    print('title')
                    qs_xxx = Manga_Album.objects.filter(Q(check_discard=False))[count_page_number_min:count_page_number_max]
                    qs_xxx = sort_queryset_by_korean_title(qs_xxx, field_ascending_str)
                else:
                    print('No title')
                    qs_xxx = Manga_Album.objects.filter(Q(check_discard=False)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
            else:
                print('4')
                qs_xxx = Manga_Album.objects.filter(Q(check_discard=False) & Q(category=selected_category_manga_str)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        print('qs_xxx', len(qs_xxx))

        # Score 계산
        for q_xxx in qs_xxx:
            dict_score_history = q_xxx.dict_score_history
            score = get_score_album(album_type, dict_score_history)
            data = {
                'score': score,
            }
            Manga_Album.objects.filter(id=q_xxx.id).update(**data)

        # Data Serialization            
        # list_serialized_data_manga_album = Manga_Album_Serializer(qs_xxx, many=True).data
        list_serialized_data_manga_album = Manga_Album_list_Serializer(qs_xxx, many=True).data
        
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_PICTURE': BASE_DIR_PICTURE,
            'BASE_DIR_MANGA': BASE_DIR_MANGA,
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'BASE_DIR_MUSIC': BASE_DIR_MUSIC,
            'LIST_MANGA_CATEGORY': LIST_MANGA_CATEGORY,
            'LIST_MANGA_SORTING_FIELD': LIST_MANGA_SORTING_FIELD,
            'list_serialized_data_manga_album': list_serialized_data_manga_album,
            'total_num_registered_item': total_num_registered_item,
            'total_num_searched_item': total_num_searched_item,
            'list_count_page_number': [count_page_number_min, count_page_number_max, count_page_number],
            'check_switch_manga_complete_hide': check_switch_manga_complete_hide,
            'check_switch_manga_new_volume_update_only': check_switch_manga_new_volume_update_only,
        }
        return JsonResponse(jsondata, safe=False)
   
    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('button') == 'sorting_items':
            selected_sorting_field_str = request.POST.get('sort_by')
            selected_field_manga = q_mysettings_hansent.selected_field_manga
            check_field_ascending_manga = q_mysettings_hansent.check_field_ascending_manga
            if selected_sorting_field_str == selected_field_manga:
                if check_field_ascending_manga == True:
                    check_field_ascending_manga = False
                else:
                    check_field_ascending_manga = True
            data = {
                'selected_field_manga':selected_sorting_field_str,
                'check_field_ascending_manga': check_field_ascending_manga,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            print('Sorting 조건 확정 및 저장')
            return redirect('hans-ent-manga-album-list')
        
        if request.POST.get('button') == 'category_filtering':
            selected_category_str = request.POST.get('selected_category')
            data = {
                'selected_category_manga': selected_category_str,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            return redirect('hans-ent-manga-album-list')
       
        if request.POST.get('button') == 'page_number_min':
            hans_ent_count_page_number_down(request, q_mysettings_hansent)
            return redirect('hans-ent-manga-album-list')
        
        if request.POST.get('button') == 'page_number_max':
            total_num_registered_item = Manga_Album.objects.count()
            hans_ent_count_page_number_up(request, q_mysettings_hansent, total_num_registered_item)
            return redirect('hans-ent-manga-album-list')
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_manga_album_list_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
    if request.method == 'GET':
        print('##############################################################', request.GET,)
        keyword_str = request.GET.get('keyword')
        qs_xxx = Manga_Album.objects.filter(Q(check_discard=False) & (Q(title__icontains=keyword_str) | Q(main_actor__name__icontains=keyword_str) | Q(main_actor__synonyms__icontains=keyword_str)))
        list_searched_manga_album_id = []
        if qs_xxx is not None and len(qs_xxx) > 0:
            for q_xxx in qs_xxx:
                list_searched_manga_album_id.append(q_xxx.id)
        data = {
            'list_searched_manga_album_id': list_searched_manga_album_id,
        }
        MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
        return redirect('hans-ent-manga-album-list')
   
    if request.method == 'POST':
        print('##############################################################', request.POST,)
        keyword_str = request.POST.get('button')
        if keyword_str == 'reset':
            reset_hans_ent_manga_album_list(q_mysettings_hansent)

        if keyword_str == 'complete_hide_and_update_only':
            status_complete_hide_str = request.POST.get('status_complete_hide')
            status_update_only_str = request.POST.get('status_update_only')
            print('status_complete_hide_str', status_complete_hide_str)
            print('status_update_only_str', status_update_only_str)
            if status_complete_hide_str == 'true' :
                if status_update_only_str == 'true':
                    print('1')
                    check_switch_manga_complete_hide = True
                    check_switch_manga_new_volume_update_only = True
                    qs_xxx = Manga_Album.objects.filter(Q(check_discard=False) & Q(check_completed=False) & Q(check_new_volume=True))
                else:
                    print('2')
                    check_switch_manga_complete_hide = True
                    check_switch_manga_new_volume_update_only = False
                    qs_xxx = Manga_Album.objects.filter(Q(check_discard=False) & Q(check_completed=False))
            else:
                if status_update_only_str == 'true':
                    print('3')
                    check_switch_manga_complete_hide = False
                    check_switch_manga_new_volume_update_only = True
                    qs_xxx = Manga_Album.objects.filter(Q(check_discard=False) & Q(check_new_volume=True))
                else:
                    print('4')
                    check_switch_manga_complete_hide = False
                    check_switch_manga_new_volume_update_only = False
                    qs_xxx = Manga_Album.objects.filter(Q(check_discard=False))
            list_searched_manga_album_id = []
            if qs_xxx is not None and len(qs_xxx) > 0:
                for q_xxx in qs_xxx:
                    list_searched_manga_album_id.append(q_xxx.id)
            data = {
                'list_searched_manga_album_id': list_searched_manga_album_id,
                'check_switch_manga_complete_hide': check_switch_manga_complete_hide,
                'check_switch_manga_new_volume_update_only': check_switch_manga_new_volume_update_only,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)

            

        return redirect('hans-ent-manga-album-list')
   



# #--------------------------------------------------------------------------------------------------------------------------------------
# # @login_required
# class hans_ent_manga_album_profile_modal(APIView):
#     def get(self, request, format=None):
#         jsondata = {'test': 'hello this is actor profile modal'}
#         return Response(jsondata)

#     def post(self, request, format=None):
#         # q_user = request.user
#         # q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
#         jsondata = {'test': 'hello this is actor profile modal'}
#         return Response(jsondata)
    



#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_manga_album_profile_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == 'GET':
        print('streaming_manga_album_gallery_modal_view GET ======================================================= 1')
        print(request.GET,)
        print('======================================================================================================= 2')
        q_manga_album_selected = q_mysettings_hansent.manga_album_selected
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_manga_album_gallery_modal_view POST ======================================================= 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        selected_serialized_data_actor = {}
        selected_serialized_data_manga_album = {}
        dict_album_key_fullsize_value_thumbnail_image_path = {}
        list_album_thumbnail_url = []

        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_manga_album_id_str = request.POST.get('selected_manga_album_id')

        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        selected_manga_album_id_str = None if selected_manga_album_id_str in LIST_STR_NONE_SERIES else selected_manga_album_id_str
        
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        print('selected actor ', q_actor)

        if selected_manga_album_id_str is not None and selected_manga_album_id_str != '':
            selected_manga_album_id = int(selected_manga_album_id_str)
            q_manga_album = Manga_Album.objects.get(id=selected_manga_album_id)
        else:
            q_manga_album = None
        print('q_manga_album: ', q_manga_album)
        
        # Data Serialization
        if q_manga_album is not None: 
            if q_actor is None:
                q_actor = q_manga_album.main_actor
            selected_serialized_data_manga_album = Manga_Album_Serializer(q_manga_album, many=False).data
        if q_actor is not None:
            print('q_actor', q_actor)
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_manga_album': selected_serialized_data_manga_album,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)





#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_manga_album_gallery_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.last()


    if request.method == 'GET':
        print('streaming_manga_album_gallery_modal_view GET ======================================================= 1')
        print(request.GET,)
        print('======================================================================================================= 2')
        q_manga_album_selected = q_mysettings_hansent.manga_album_selected
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_manga_album_gallery_modal_view POST ======================================================= 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        selected_serialized_data_actor = {}
        selected_serialized_data_manga_album = {}
        list_dict_manga_album_in_this_volume = []
        selected_manga_album_volume_id = 0
        check_selected_manga_album_volume_favorite = False

        
        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_manga_album_id_str = request.POST.get('selected_manga_album_id')
        selected_manga_album_volume_id_str = request.POST.get('selected_manga_album_volume_id')
        

        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        selected_manga_album_id_str = None if selected_manga_album_id_str in LIST_STR_NONE_SERIES else selected_manga_album_id_str
        selected_manga_album_volume_id_str = None if selected_manga_album_volume_id_str in LIST_STR_NONE_SERIES else selected_manga_album_volume_id_str
        
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        print('selected actor ', q_actor)

        # 선택한 Manga 앨범 정보 확인 / 업데이트
        if selected_manga_album_id_str is not None and selected_manga_album_id_str != '':
            selected_manga_album_id = int(selected_manga_album_id_str)
            q_manga_album = Manga_Album.objects.get(id=selected_manga_album_id)
            list_dict_volume_manga = q_manga_album.list_dict_volume_manga
            if list_dict_volume_manga is not None:
                last_volume = len(list_dict_volume_manga)
                data = {'last_volume': last_volume}
                Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
                q_manga_album.refresh_from_db()
        else:
            q_manga_album = None
        
        
        # 선택한 Volume에 포함되는 Image 리스트 확보하기
        if selected_manga_album_volume_id_str is not None and selected_manga_album_volume_id_str != '':
            selected_manga_album_volume_id = int(selected_manga_album_volume_id_str)
            print("volume", selected_manga_album_volume_id)
            if q_manga_album is not None:
                list_dict_manga_album = q_manga_album.list_dict_manga_album
                list_dict_volume_manga = q_manga_album.list_dict_volume_manga
                for dict_volume_manga in list_dict_volume_manga:
                    if dict_volume_manga['volume'] == selected_manga_album_volume_id:
                        list_id = dict_volume_manga['list_id']
                        # print('list_id', list_id)
                        if 'favorite' in dict_volume_manga:
                            check_selected_manga_album_volume_favorite = dict_volume_manga['favorite']
                            if dict_volume_manga['favorite'] == 'true':
                                check_selected_manga_album_volume_favorite = True
                            else:
                                check_selected_manga_album_volume_favorite = False
                        else:
                            dict_volume_manga['favorite'] = 'false'
                            check_selected_manga_album_volume_favorite = False
                            data = {
                                'list_dict_volume_manga': list_dict_volume_manga,
                            }
                            Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
                            q_manga_album.refresh_from_db()

                if list_id is not None and len(list_id) > 0:
                    for dict_manga_album in list_dict_manga_album:
                        if dict_manga_album['id'] in list_id:
                            # print("dict_manga_album['id']", dict_manga_album['id'])
                            list_dict_manga_album_in_this_volume.append(dict_manga_album)
        

        # 사용자 선택한 Manga 및 Volume 정보 저장하기
        if q_manga_album is not None:
            print('# 사용자 선택한 Manga 및 Volume 정보 저장하기')
            list_manga_album_my_bookmark = q_mysettings_hansent.list_manga_album_my_bookmark
            if list_manga_album_my_bookmark is None:
                list_manga_album_my_bookmark = [] 
            title = q_manga_album.title 
            q_manga_album_id = q_manga_album.id 
            id_manga = q_manga_album.id_manga 
            volume = selected_manga_album_volume_id
            if len(list_manga_album_my_bookmark) > 0:
                check_new = True
                for item in list_manga_album_my_bookmark:
                    if item['id'] == q_manga_album_id:
                        if volume > item['volume']:
                            item['volume'] = volume
                        # item['id_manga'] = id_manga
                        # item['title'] = title
                        check_new = False
                if check_new == True:
                    list_manga_album_my_bookmark.append(
                        {
                            'id': q_manga_album_id,
                            'id_manga': id_manga, 
                            'title': title, 
                            'volume': volume,
                        }
                    )    
            else:
                list_manga_album_my_bookmark.append(
                    {
                        'id': q_manga_album_id,
                        'id_manga': id_manga, 
                        'title': title, 
                        'volume': volume,
                    }
                )
            print('list_manga_album_my_bookmark', list_manga_album_my_bookmark)
            data = {
                'list_manga_album_my_bookmark': list_manga_album_my_bookmark,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            q_mysettings_hansent.refresh_from_db()

        # Favorite 상태 변경하기
        if request.POST.get('button') == 'status_favorite_change':
            print('status_favorite_change')
            if selected_manga_album_volume_id_str is not None and selected_manga_album_volume_id_str != '':
                selected_manga_album_volume_id = int(selected_manga_album_volume_id_str)
                print("volume", selected_manga_album_volume_id)
                if q_manga_album is not None:
                    list_dict_volume_manga = q_manga_album.list_dict_volume_manga
                    for dict_volume_manga in list_dict_volume_manga:
                        if dict_volume_manga['volume'] == selected_manga_album_volume_id:
                            if 'favorite' in dict_volume_manga:
                                if dict_volume_manga['favorite'] == 'true':
                                    dict_volume_manga['favorite'] = 'false'
                                    check_selected_manga_album_volume_favorite = False
                                else:
                                    dict_volume_manga['favorite'] = 'true'
                                    check_selected_manga_album_volume_favorite = True
                            else:
                                dict_volume_manga['favorite'] = 'true'
                                check_selected_manga_album_volume_favorite = True
                                
                    data = {
                        'list_dict_volume_manga': list_dict_volume_manga,
                    }
                    Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
                    q_manga_album.refresh_from_db()

        # Rating 점수 상향
        if request.POST.get('button') == 'add_rating_score':
            if q_manga_album is not None:
                dict_score_history = q_manga_album.dict_score_history
                if dict_score_history is None:
                    dict_score_history = DEFAULT_DICT_SCORE_HISTORY_MANGA
                else:
                    if 'rating' in dict_score_history:
                        rating = dict_score_history['rating']
                        rating = rating + 1
                        dict_score_history['rating'] = rating
                    else:
                        dict_score_history['rating'] = 1
                dict_score_history['favorite'] = 'true'
                check_selected_manga_album_favorite = True
                data = {
                    'dict_score_history': dict_score_history,
                }
                Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
                q_manga_album.refresh_from_db()

        # 선택한 Volume Favorite 상태 확인하기 및 스코어링
        if selected_manga_album_volume_id_str is not None and selected_manga_album_volume_id_str != '':
            selected_manga_album_volume_id = int(selected_manga_album_volume_id_str)
            # print("volume", selected_manga_album_volume_id)
            if q_manga_album is not None:
                dict_score_history = q_manga_album.dict_score_history
                if dict_score_history is None:
                    dict_score_history = DEFAULT_DICT_SCORE_HISTORY_MANGA
                else:
                    if 'rating' not in dict_score_history:
                        dict_score_history['rating'] = 0
                    if dict_score_history['favorite_sum'] > 0:
                        if dict_score_history['rating'] == 0:
                            dict_score_history['rating'] = 1
                    else:
                        check_selected_manga_album_volume_favorite = False
                list_count_favorite = []
                list_dict_volume_manga = q_manga_album.list_dict_volume_manga
                for dict_volume_manga in list_dict_volume_manga:
                    if 'favorite' in dict_volume_manga:
                        if dict_volume_manga['favorite'] == 'true':
                            list_count_favorite.append(True)
                        if dict_volume_manga['volume'] == selected_manga_album_volume_id:
                            check_selected_manga_album_volume_favorite = dict_volume_manga['favorite']
                            if dict_volume_manga['favorite'] == 'true':
                                check_selected_manga_album_volume_favorite = True
                            else:
                                check_selected_manga_album_volume_favorite = False
                    else:
                        dict_volume_manga['favorite'] = 'false'
                        check_selected_manga_album_volume_favorite = False
                favorite_sum = list_count_favorite.count(True)
                dict_score_history['favorite_sum'] = favorite_sum
                # 방문 점수 카운트
                total_visit_album = dict_score_history['total_visit_album']
                total_visit_album = total_visit_album + 1
                dict_score_history['total_visit_album'] = total_visit_album
                # Score 업데이트 
                album_type='manga'
                score = get_score_album(album_type, dict_score_history)
                print('score', score)
                data = {
                    'score': score,
                    'dict_score_history': dict_score_history,
                    'list_dict_volume_manga': list_dict_volume_manga,
                }
                Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
                q_manga_album.refresh_from_db()
        
        if request.POST.get('button') == 'select_last_volume':
            if q_manga_album is not None:
                list_manga_album_my_bookmark = q_mysettings_hansent.list_manga_album_my_bookmark
                for item in list_manga_album_my_bookmark:
                    if item['id'] == q_manga_album.id:
                        selected_manga_album_volume_id = item['volume']
                list_dict_manga_album = q_manga_album.list_dict_manga_album
                # # 마지막 볼륨 id 찾기기
                # volume = 0
                # if q_manga_album.check_completed == False:
                #     for dict_manga_album in list_dict_manga_album:
                #         volume_new = dict_manga_album['volume']
                #         if volume_new > volume:
                #             volume = volume_new
                # selected_manga_album_volume_id = volume
                print('selected_manga_album_volume_id', selected_manga_album_volume_id)

                list_dict_volume_manga = q_manga_album.list_dict_volume_manga
                for dict_volume_manga in list_dict_volume_manga:
                    if dict_volume_manga['volume'] == selected_manga_album_volume_id:
                        list_id = dict_volume_manga['list_id']
                        # print('list_id', list_id)
                        if 'favorite' in dict_volume_manga:
                            check_selected_manga_album_volume_favorite = dict_volume_manga['favorite']
                            if dict_volume_manga['favorite'] == 'true':
                                check_selected_manga_album_volume_favorite = True
                            else:
                                check_selected_manga_album_volume_favorite = False
                        else:
                            dict_volume_manga['favorite'] = 'false'
                            check_selected_manga_album_volume_favorite = False
                            data = {
                                'list_dict_volume_manga': list_dict_volume_manga,
                            }
                            Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
                            q_manga_album.refresh_from_db()

                if list_id is not None and len(list_id) > 0:
                    for dict_manga_album in list_dict_manga_album:
                        if dict_manga_album['id'] in list_id:
                            # print("dict_manga_album['id']", dict_manga_album['id'])
                            list_dict_manga_album_in_this_volume.append(dict_manga_album)
        

        # Data Serialization
        if q_manga_album is not None: 
            if q_actor is None:
                q_actor = q_manga_album.main_actor
            data = {
                'check_new_volume': False,
            }
            Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
            q_manga_album.refresh_from_db()
            selected_serialized_data_manga_album = Manga_Album_Serializer(q_manga_album, many=False).data
        if q_actor is not None:
            print('q_actor', q_actor)
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        print('selected_manga_album_volume_id *************************', selected_manga_album_volume_id)
        jsondata = {
            'check_selected_manga_album_volume_favorite': check_selected_manga_album_volume_favorite,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_manga_album': selected_serialized_data_manga_album,
            'list_dict_manga_album_in_this_volume': list_dict_manga_album_in_this_volume,
            'selected_manga_album_volume_id': selected_manga_album_volume_id,
        }
        # print('jsondata', list_dict_manga_album_in_this_volume)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)




#--------------------------------------------------------------------------------------------------------------------------------------
# @login_required
class hans_ent_manga_album_gallery_fullscreen_modal(APIView):
    def get(self, request, format=None):
        jsondata = {'test': 'hello this is manga profile modal'}
        return Response(jsondata)
    def post(self, request, format=None):
        jsondata = {'test': 'hello this is manga profile modal'}
        return Response(jsondata)
    


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_manga_album_update_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    
    if request.method == "GET":
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'GET':
        selected_serialized_data_actor = {}
        selected_serialized_data_manga_album = {}
        q_manga_album_selected = q_mysettings_hansent.manga_album_selected
        # Get selected_serialized_data
        if q_manga_album_selected is not None:
            selected_serialized_data_manga_album = Manga_Album_Serializer(q_manga_album_selected, many=False).data
            if q_manga_album_selected.main_actor:
                selected_serialized_data_actor = Actor_Serializer(q_manga_album_selected.main_actor, many=False).data
            else:
                q_actor = q_mysettings_hansent.actor_selected
                if q_actor is not None:
                    selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data
        # Jsondata
        jsondata = {
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_manga_album': selected_serialized_data_manga_album,
        }
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_manga_album_update_modal_view POST ========================================================== 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        
        selected_serialized_data_manga_album = {}
        selected_serialized_data_actor = {}
                
        selected_manga_album_id_str = str(request.POST.get('selected_manga_album_id'))
        selected_manga_album_manga_id_str = str(request.POST.get('selected_manga_album_manga_id'))
        selected_actor_id_str = request.POST.get('selected_actor_id')
        input_text_title_str = request.POST.get('input_text_title')
        input_text_name_str = request.POST.get('input_text_name')
        input_text_studio_str = request.POST.get('input_text_studio')
        input_date_released_str = request.POST.get('input_date_released')
        input_text_tag_str = request.POST.get('input_text_tag')
        selected_manga_sub_type_str = request.POST.get('selected_manga_sub_type')
        input_number_volume_str = request.POST.get('input_number_volume')
        status_manga_update_checkbox_covoer_image_update_str = request.POST.get('status_manga_update_checkbox_covoer_image_update')
        selected_filtering_category_id_str = request.POST.get('selected_filtering_category_id')
        
        selected_manga_album_id_str = None if selected_manga_album_id_str in LIST_STR_NONE_SERIES else selected_manga_album_id_str
        selected_manga_album_manga_id_str = None if selected_manga_album_manga_id_str in LIST_STR_NONE_SERIES else selected_manga_album_manga_id_str
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        input_text_title_str = None if input_text_title_str in LIST_STR_NONE_SERIES else input_text_title_str
        input_text_name_str = None if input_text_name_str in LIST_STR_NONE_SERIES else input_text_name_str
        input_text_studio_str = None if input_text_studio_str in LIST_STR_NONE_SERIES else input_text_studio_str
        input_date_released_str = None if input_date_released_str in LIST_STR_NONE_SERIES else input_date_released_str
        selected_manga_sub_type_str = None if selected_manga_sub_type_str in LIST_STR_NONE_SERIES else selected_manga_sub_type_str
        input_number_volume_str = None if input_number_volume_str in LIST_STR_NONE_SERIES else input_number_volume_str
        status_manga_update_checkbox_covoer_image_update_str = None if status_manga_update_checkbox_covoer_image_update_str in LIST_STR_NONE_SERIES else status_manga_update_checkbox_covoer_image_update_str
        selected_filtering_category_id_str = None if selected_filtering_category_id_str in LIST_STR_NONE_SERIES else selected_filtering_category_id_str

        folder_name_str = request.POST.get('folder_name')
        folder_name_str = None if folder_name_str in LIST_STR_NONE_SERIES else folder_name_str
        input_info_site_name_str = request.POST.get('input_info_site_name')
        input_info_site_url_str = request.POST.get('input_info_site_url')
        input_info_site_name_str = None if input_info_site_name_str in LIST_STR_NONE_SERIES else input_info_site_name_str
        input_info_site_url_str = None if input_info_site_url_str in LIST_STR_NONE_SERIES else input_info_site_url_str

        print('selected_actor_id_str', selected_actor_id_str)
        print('selected_manga_album_id_str', selected_manga_album_id_str)

        # 선택된 모델 정보 획득
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        

        # 선택된 앨범 정보 획득
        if selected_manga_album_id_str is not None and selected_manga_album_id_str != '' :
            selected_manga_album_id = int(selected_manga_album_id_str)
            q_manga_album_selected = Manga_Album.objects.get(id=selected_manga_album_id)
        else:
            q_manga_album_selected = None 
        print('q_manga_album_selected', q_manga_album_selected)

        # Manga Album 쿼리 생성하기
        if request.POST.get('button') == 'create_or_update':
            if q_manga_album_selected is None:
                q_manga_album_selected = create_manga_album()
                if q_actor is not None:
                    if q_manga_album_selected.main_actor is None:
                        data = {'main_actor':q_actor}
                        Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
                        q_manga_album_selected.refresh_from_db()

        # 앨범 선택 이미지 삭제하기
        if request.POST.get('button') == 'remove_manga_album_manga':
            print('# 앨범 이미지 삭제하기')
            if selected_manga_album_manga_id_str is not None and selected_manga_album_manga_id_str != '':
                selected_manga_album_manga_id = int(selected_manga_album_manga_id_str)
                if q_manga_album_selected is not None:
                    delete_files_in_list_dict_xxx_album(q_manga_album_selected, 'manga', 'image', selected_manga_album_manga_id)

        # 앨범 통으로 삭제하기
        if request.POST.get('button') == 'remove_manga_album':
            print('# 앨범 통으로 삭제하기', q_manga_album_selected)
            if q_manga_album_selected is not None:
                delete_files_in_list_dict_xxx_album(q_manga_album_selected, 'manga', 'all', 'all')  ## album 종류(actor, manga, video, music 중 택 1), 싱글 쿼리, 삭제종류('all' or int(id)) 
            return redirect('hans-ent-manga-album-list')

        # 앨범 커버 이미지 변경하기
        if request.POST.get('button') == 'change_manga_album_cover_image':
            if selected_manga_album_manga_id_str is not None and selected_manga_album_manga_id_str != '':
                selected_manga_album_manga_id = int(selected_manga_album_manga_id_str)
                if q_manga_album_selected is not None:
                    list_dict_manga_album = q_manga_album_selected.list_dict_manga_album
                    # acitve 모두 false 변경
                    for dict_manga_album in list_dict_manga_album:
                        dict_manga_album['active'] = 'false'
                        if dict_manga_album['id'] == selected_manga_album_manga_id:
                            dict_manga_album['active'] = 'true'
                    data = {'list_dict_manga_album': list_dict_manga_album}
                    Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
                    q_manga_album_selected.refresh_from_db()

        # 앨범 커버 이미지 삭제하기
        if request.POST.get('button') == 'remove_cover_image':
            print('# 앨범 커버 이미지 삭제하기')
            if q_manga_album_selected is not None:
                list_dict_manga_album = q_manga_album_selected.list_dict_manga_album
                # acitve 모두 false 변경
                for dict_manga_album in list_dict_manga_album:
                    if dict_manga_album['id'] == 0:
                        RELATIVE_PATH_XXX = RELATIVE_PATH_MANGA
                        delete_manga_item(dict_manga_album, RELATIVE_PATH_XXX)
                        # Default image로 업데이트
                        dict_manga_album['original'] = 'default-o.png'
                        dict_manga_album['cover'] = 'default-c.png'
                        dict_manga_album['thumbnail'] = 'default-t.png'
                        dict_manga_album['active'] = 'true'
                data = {'list_dict_manga_album': list_dict_manga_album}
                Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
                q_manga_album_selected.refresh_from_db()

        
        # 업로드 타이틀 정보 저장하기
        if input_text_title_str is not None and input_text_title_str != '':
            print('# 업로드 타이틀 정보 저장하기')
            if q_manga_album_selected is None:
                q_manga_album_selected = create_manga_album()
            data = {
                'title': input_text_title_str,
            }
            Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
            q_manga_album_selected.refresh_from_db()
            
        # 업로드 모델이름 저장하기
        if input_text_name_str is not None and input_text_name_str != '':
            print('# 업로드 모델이름 저장하기')
            if q_manga_album_selected is None:
                q_manga_album_selected = create_manga_album()
            data = {
                'name': input_text_name_str,
            }
            Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
            q_manga_album_selected.refresh_from_db()
        
        # 업로드 스튜디오 정보 저장하기
        if input_text_studio_str is not None and input_text_studio_str != '':
            if q_manga_album_selected is None:
                q_manga_album_selected = create_manga_album()
            data = {
                'studio': input_text_studio_str,
            }
            Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
            q_manga_album_selected.refresh_from_db()

        # 사진 앨범 타입 선택하기
        if selected_manga_sub_type_str is not None and selected_manga_sub_type_str != '':
            if q_manga_album_selected is None:
                q_manga_album_selected = create_manga_album()
            data = {
                'types': selected_manga_sub_type_str,
            }
            Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
            q_manga_album_selected.refresh_from_db()

        # 업로드 출시일 정보 저장하기
        if input_date_released_str is not None and input_date_released_str != '':
            if q_manga_album_selected is None:
                q_manga_album_selected = create_manga_album()
            date_string = str(input_date_released_str)
            date_format = '%Y-%m-%d'
            # date_released = datetime.strftime(input_date_released_str, date_format).date()
            import datetime
            date_object = datetime.datetime.strptime(date_string, date_format).date()
            data = {
                'date_released': date_object,
            }
            Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
            q_manga_album_selected.refresh_from_db()
        
        # 카테고리 저장하기
        if selected_filtering_category_id_str is not None and selected_filtering_category_id_str != '':
            print('# 카테고리 저장하기')
            if q_manga_album_selected is None:
                q_manga_album_selected = create_manga_album()
            data = {
                'category': selected_filtering_category_id_str,
            }
            Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
            q_manga_album_selected.refresh_from_db()
        
        # Website 등록
        if input_info_site_name_str is not None and input_info_site_name_str != '':
            print('# Website 등록')
            if input_info_site_url_str is not None and input_info_site_url_str != '':
                if q_manga_album_selected is None:
                    q_manga_album_selected = create_manga_album()
                list_dict_info_url = q_manga_album_selected.list_dict_info_url
                if list_dict_info_url is None:
                    list_dict_info_url = []
                if input_info_site_name_str not in list_dict_info_url:
                    list_dict_info_url.append({"name":input_info_site_name_str, "url":input_info_site_url_str})
                    data = {
                        'list_dict_info_url': list_dict_info_url,
                    }
                    Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
                    q_manga_album_selected.refresh_from_db()

        # Tag 저장하기
        if input_text_tag_str is not None and input_text_tag_str != '':
            if q_manga_album_selected is None:
                q_manga_album_selected = create_manga_album()
            tags = q_manga_album_selected.tags
            if tags is None:
                tags = []
            if input_text_tag_str not in tags:
                print('tag save', input_text_tag_str)
                tags.append(input_text_tag_str)
            data = {
                'tags': tags,
            }
            Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
            q_manga_album_selected.refresh_from_db()

        # 업로드 Volume 정보 저장하기
        if input_number_volume_str is not None and input_number_volume_str != '':
            print('# 업로드 Volume 정보 저장하기')
            if q_manga_album_selected is not None:
                input_number_volume = int(input_number_volume_str)
                list_dict_manga_album = q_manga_album_selected.list_dict_manga_album
                list_dict_volume_manga = q_manga_album_selected.list_dict_volume_manga
                list_collect_volume_id = []
                for dict_volume_manga in list_dict_volume_manga:
                    list_collect_volume_id.append(dict_volume_manga['volume'])
                if input_number_volume not in list_collect_volume_id:
                    # 직전 volume item 업데이트
                    list_dict_volume_manga[-1]['last'] = 'false'
                    # 신규 volume item 생성
                    default_dict_volume_manga = DEFAULT_LIST_DICT_VOLUME_MANGA_INFO[0]
                    default_dict_volume_manga['volume'] = input_number_volume
                    default_dict_volume_manga['list_id'] = []
                    list_dict_volume_manga.append(default_dict_volume_manga)
                    last_volume = len(list_dict_volume_manga) - 1
                data = {
                    'last_volume': last_volume,
                    'list_dict_volume_manga': list_dict_volume_manga,
                }
                Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
                q_manga_album_selected.refresh_from_db()
            else:
                message = '먼저 Manga 앨범을 생성하세요.'

        # 모델 선택하기
        if request.POST.get('button') == 'actor_select':
            if q_manga_album_selected is None:
                q_manga_album_selected = create_manga_album()
            if q_manga_album_selected is not None and q_actor is not None:
                print('선택된 모델', q_actor)
                data = {
                    'main_actor': q_actor,
                }
                Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
                q_manga_album_selected.refresh_from_db()

        # 모델 선택해제하기
        if request.POST.get('button') == 'actor_select_reset':
            print('# 모델 선택해제하기')
            if q_manga_album_selected is None:
                q_manga_album_selected = create_manga_album()
            if q_manga_album_selected is not None:
                data = {
                    'main_actor': None,
                }
                Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
                q_manga_album_selected.refresh_from_db() 

        # 이미지 업로드 했으면 저장하기
        if request.FILES:
            if q_manga_album_selected is not None:
                # 앨범 갤러이 이미지 저장하기
                files = request.FILES.getlist('files')
                if files is not None and len(files) > 0:
                    if status_manga_update_checkbox_covoer_image_update_str == 'true':
                        save_file_to_replace_default_image(q_manga_album_selected, files, type_album='manga')
                    else:
                        # save_manga_album_images(q_manga_album_selected, files)
                        save_files_in_list_dict_xxx_album(q_manga_album_selected, files, type_album='manga')

        # 신규 Manga Album 생성
        if request.POST.get('button') == 'create_manga_album':
            q_actor = None 
            q_manga_album_selected = None
            print('good luck~!')
            pass

        # Data Serialization
        if q_manga_album_selected is not None:
            print('# 앨범이 등록되어 있다면', q_manga_album_selected)
            print('q_actor', q_actor)
            if q_actor is None:
                q_actor = q_manga_album_selected.main_actor
               
            # Settings에 선택된 Album 쿼리 등록
            print('세팅에 현재 앨범 등록하기', q_mysettings_hansent)
            data = {
                'manga_album_selected': q_manga_album_selected
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            q_mysettings_hansent.refresh_from_db()

            # main actor 등록
            if q_manga_album_selected.main_actor is None:
                data = {"main_actor": q_actor}
                Manga_Album.objects.filter(id=q_manga_album_selected.id).update(**data)
                q_manga_album_selected.refresh_from_db()

            # Data Serialize
            selected_serialized_data_manga_album = Manga_Album_Serializer(q_manga_album_selected, many=False).data
        
        if q_actor is not None:
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'LIST_MANGA_CATEGORY': LIST_MANGA_CATEGORY,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_manga_album': selected_serialized_data_manga_album,
        }
        # print('======================================================================================================= 3')
        # print('jsondata selected_serialized_data_manga_album ', jsondata['selected_serialized_data_manga_album'])
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)  




#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_manga_album_scraping_modal(request):
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.last()
    print('q_systemsettings_hansent', q_systemsettings_hansent)
   
    if request.method == 'GET':
        print('##############################################################', request.GET,)
        return True
   
    if request.method == 'POST':
        print('##############################################################', request.POST,)
        selected_serialized_data_systemsettings_hansent = {}
        messages = None
        
        input_text_title_str = request.POST.get('input_text_title')
        input_number_parsing_id_str = request.POST.get('input_number_parsing_id')
        input_text_url_str = request.POST.get('input_text_url')
        input_text_img_url_str = request.POST.get('input_text_img_url')
        selected_manga_id_str = request.POST.get('selected_manga_id')

        input_text_title_str = None if input_text_title_str in LIST_STR_NONE_SERIES else input_text_title_str
        input_number_parsing_id_str = None if input_number_parsing_id_str in LIST_STR_NONE_SERIES else input_number_parsing_id_str
        input_text_url_str = None if input_text_url_str in LIST_STR_NONE_SERIES else input_text_url_str
        input_text_img_url_str = None if input_text_img_url_str in LIST_STR_NONE_SERIES else input_text_img_url_str
        selected_manga_id_str = None if selected_manga_id_str in LIST_STR_NONE_SERIES else selected_manga_id_str
        print('input_text_title_str', input_text_title_str)
        print('input_number_parsing_id_str', input_number_parsing_id_str)

        list_dict_manga_info_for_parsing = q_systemsettings_hansent.list_dict_manga_info_for_parsing
        if list_dict_manga_info_for_parsing is None:
            # list_dict_manga_info_for_parsing = [{'title': '', 'id': 0, 'completed':'false'}]
            list_dict_manga_info_for_parsing = []
        

        if request.POST.get('button') == 'base_url_move':
            direction_str = request.POST.get('direction')
            print('direction_str', direction_str)

            parsing_base_url_manga = q_systemsettings_hansent.parsing_base_url_manga
            parsing_base_url_manga = parsing_base_url_manga.replace('https://wfwf', '')
            parsing_base_url_manga = parsing_base_url_manga.replace('.com/', '')
            print('parsing_base_url_manga', parsing_base_url_manga)

            try:
                parsing_base_url_manga_int = int(parsing_base_url_manga)
            except:
                parsing_base_url_manga_int = None 
            print('parsing_base_url_manga_int', parsing_base_url_manga_int)
            if parsing_base_url_manga_int is not None:
                if direction_str == 'down':
                    parsing_base_url_manga_int = parsing_base_url_manga_int - 1
                if direction_str == 'up':
                    parsing_base_url_manga_int = parsing_base_url_manga_int + 1
                
                parsing_base_url_manga = f'https://wfwf{parsing_base_url_manga_int}.com/'
                parsing_cover_img_url_manga = f'https://wfwf{parsing_base_url_manga_int}.com/assets/img/m_menu01.png?v=4'
                data = {
                    'parsing_base_url_manga': parsing_base_url_manga,
                    'parsing_cover_img_url_manga': parsing_cover_img_url_manga,
                }
                SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                q_systemsettings_hansent.refresh_from_db()

        if request.POST.get('button') == 'refresh':
            # manga album update
            for dict_manga_info_for_parsing in list_dict_manga_info_for_parsing:
                title = dict_manga_info_for_parsing['title']
                check_completed_str = dict_manga_info_for_parsing['completed'] 
                id_manga = dict_manga_info_for_parsing['id'] 

                if check_completed_str == 'true':
                    check_completed = True 
                else:
                    check_completed = False
                if title is not None:
                    q_manga_selected = Manga_Album.objects.filter(Q(check_discard=False) & Q(title=title)).last()
                if q_manga_selected is not None:
                    data = {
                        'id_manga': id_manga,
                        'check_completed': check_completed,
                    }
                    Manga_Album.objects.filter(id=q_manga_selected.id).update(**data)
                    q_manga_selected.refresh_from_db() 


            # 리스트 최신으로 업데이트
            for dict_manga_info_for_parsing in list_dict_manga_info_for_parsing:
                if dict_manga_info_for_parsing['completed'] == 'false':
                    title = dict_manga_info_for_parsing['title']
                    q_manga_for_update = Manga_Album.objects.filter(Q(check_discard=False) & Q(title=title)).last()
                    if q_manga_for_update is not None:
                        check_new_volume = q_manga_for_update.check_new_volume
                        if check_new_volume == True:
                            check_new_volume_str = 'true'
                        else:
                            check_new_volume_str = 'false'
                        # if check_new_volume == True:
                        print('check_new_volume', q_manga_for_update.title,  check_new_volume)
                        last_volume = q_manga_for_update.last_volume
                        list_dict_volume_manga = q_manga_for_update.list_dict_volume_manga
                        if list_dict_volume_manga is not None and len(list_dict_volume_manga) > 0:
                            last_volume = len(list_dict_volume_manga)
                            data = {'last_volume': last_volume}
                            Manga_Album.objects.filter(id=q_manga_for_update.id).update(**data) 
                            q_manga_for_update.refresh_from_db()
                        else:
                            last_volume = 0
                        dict_manga_info_for_parsing['last_volume'] = last_volume
                        dict_manga_info_for_parsing['check_new_volume'] = check_new_volume_str
            data = {'list_dict_manga_info_for_parsing': list_dict_manga_info_for_parsing}
            SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
            q_systemsettings_hansent.refresh_from_db()
            messages = '리스트를 최신 정보로 갱신하였습니다.'  

        if request.POST.get('button') == 'update_website':

            if input_text_url_str is not None:
                data = {
                    'parsing_base_url_manga': input_text_url_str,
                }
                SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                q_systemsettings_hansent.refresh_from_db() 
            
            if input_text_img_url_str is not None:
                data = {
                    'parsing_cover_img_url_manga': input_text_img_url_str,
                }
                SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                q_systemsettings_hansent.refresh_from_db() 

        if request.POST.get('button') == 'update_title':
            if input_text_title_str is not None and input_number_parsing_id_str is not None:
                check_title_duplicated = False
                for dict_manga_info_for_parsing in list_dict_manga_info_for_parsing:
                    if dict_manga_info_for_parsing['title'] == input_text_title_str:
                        check_title_duplicated = True
                if check_title_duplicated == False:
                    input_number_parsing_id = int(input_number_parsing_id_str)
                    list_collect_id_parsed = []
                    for dict_manga_info_for_parsing in list_dict_manga_info_for_parsing:
                        list_collect_id_parsed.append(dict_manga_info_for_parsing['id'])
                    if input_number_parsing_id not in list_collect_id_parsed:
                        #신규등록
                        list_dict_manga_info_for_parsing.append({'title': input_text_title_str, 'id': input_number_parsing_id, 'completed': 'false'})
                        data = {
                            'list_dict_manga_info_for_parsing': list_dict_manga_info_for_parsing,
                        }
                        SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                        q_systemsettings_hansent.refresh_from_db() 
                else:
                    messages = 'Title이 중복입니다. 다른 이름을 기입하세요.'    
            else:
                messages = 'Title 및 ID 모두 기입해야 합니다.'
        
        # Change Status Manga Completion
        if request.POST.get('button') == 'status_completion_change':
            print('# Change Status Manga Completion')
            if selected_manga_id_str is not None:
                selected_manga_id = int(selected_manga_id_str)
                title = None
                for dict_manga_info_for_parsing in list_dict_manga_info_for_parsing:
                    if dict_manga_info_for_parsing['id'] == selected_manga_id:
                        status_completion = str(dict_manga_info_for_parsing['completed'])
                        print('status_completion', status_completion)
                        title = dict_manga_info_for_parsing['title']

                        if status_completion == 'true':
                            print('??true')
                            dict_manga_info_for_parsing['completed'] = 'false'
                            check_completed = False
                        else:
                            print('??false')
                            dict_manga_info_for_parsing['completed'] = 'true'
                            check_completed = True
                        print(dict_manga_info_for_parsing['completed'])
                
                data = {
                    'list_dict_manga_info_for_parsing': list_dict_manga_info_for_parsing,
                }
                SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                q_systemsettings_hansent.refresh_from_db() 

                if title is not None:
                    q_manga_selected = Manga_Album.objects.filter(Q(check_discard=False) & Q(title=title)).last()
                if q_manga_selected is not None:
                    data = {
                        'check_completed': check_completed,
                    }
                    Manga_Album.objects.filter(id=q_manga_selected.id).update(**data)
                    q_manga_selected.refresh_from_db() 


        if request.POST.get('button') == 'scraping_start':
            # Celery Worker 사용 Background 수행
            update_latest_manga_data_to_db.delay()


        list_dict_manga_info_for_parsing = q_systemsettings_hansent.list_dict_manga_info_for_parsing
        if list_dict_manga_info_for_parsing is not None:
            print('list_dict_manga_info_for_parsing Before: ', list_dict_manga_info_for_parsing)
            list_dict_manga_info_for_parsing = sort_list_dict_by_chosung(list_dict_manga_info_for_parsing)
            print('list_dict_manga_info_for_parsing After: ', list_dict_manga_info_for_parsing)
            data = {
                'list_dict_manga_info_for_parsing': list_dict_manga_info_for_parsing,
            }
            SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
            q_systemsettings_hansent.refresh_from_db() 


        selected_serialized_data_systemsettings_hansent = SystemSettings_HansEnt_Serializer(q_systemsettings_hansent, many=False).data

        jsondata = {
            'messages': messages,
            'LIST_MANGA_CATEGORY': LIST_MANGA_CATEGORY,
            'selected_serialized_data_systemsettings_hansent': selected_serialized_data_systemsettings_hansent,
        }
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)










#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#
# Video Album  
#
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################


    
#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_video_album_list(request):
    import datetime
    ls_today = datetime.date.today()
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
    if request.method == 'GET':
        print('######################### hans_ent_video_album_list ', request.GET)
        total_num_registered_item = Video_Album.objects.count()
        # Searching 결과값 찾기
        list_searched_xxx_id = q_mysettings_hansent.list_searched_video_album_id
        if list_searched_xxx_id is not None:
            total_num_searched_item = len(list_searched_xxx_id)
        else:
            total_num_searched_item = 0
        # Sorting Submenu 조건
        selected_field_sorting_str = q_mysettings_hansent.selected_field_video
        selected_category_video_str = q_mysettings_hansent.selected_category_video
        # Acending or Decending?
        field_ascending_str = q_mysettings_hansent.check_field_ascending_video
        if field_ascending_str == False:
            selected_field_sorting = f'-{selected_field_sorting_str}'
        else:
            selected_field_sorting = selected_field_sorting_str
        # 화면에 표시할 아이템 개수 지정
        count_page_number = q_mysettings_hansent.count_page_number_video
        count_page_number_min = (count_page_number - 1) * LIST_NUM_DISPLAY_IN_PAGE
        count_page_number_max = count_page_number * LIST_NUM_DISPLAY_IN_PAGE
        # 쿼리 필터링
        if list_searched_xxx_id is not None and len(list_searched_xxx_id) > 0:
            if selected_category_video_str == '00':
                print('1')
                qs_xxx = Video_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
            else:
                print('2')
                qs_xxx = Video_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id) & Q(category=selected_category_video_str)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        else:
            if selected_category_video_str == '00':
                print('3')
                qs_xxx = Video_Album.objects.filter(Q(check_discard=False)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
            else:
                print('4')
                qs_xxx = Video_Album.objects.filter(Q(check_discard=False) & Q(category=selected_category_video_str)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        print('qs_xxx', len(qs_xxx))
        # Data Serialization            
        list_serialized_data_video_album = Video_Album_Serializer(qs_xxx, many=True).data
        
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_PICTURE': BASE_DIR_PICTURE,
            'BASE_DIR_MANGA': BASE_DIR_MANGA,
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'BASE_DIR_MUSIC': BASE_DIR_MUSIC,
            'LIST_VIDEO_CATEGORY': LIST_VIDEO_CATEGORY,
            'LIST_VIDEO_SORTING_FIELD': LIST_VIDEO_SORTING_FIELD,
            'LIST_DICT_SITE_VIDEO_INFO': LIST_DICT_SITE_VIDEO_INFO,
            'list_serialized_data_video_album': list_serialized_data_video_album,
            'total_num_registered_item': total_num_registered_item,
            'total_num_searched_item': total_num_searched_item,
            'list_count_page_number': [count_page_number_min, count_page_number_max, count_page_number],
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)
   
    if request.method == 'POST':
        print('hans_ent_video_album_list POST ======================================================================== 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        

        if request.POST.get('button') == 'sorting_items':
            selected_sorting_field_str = request.POST.get('sort_by')
            selected_field_video = q_mysettings_hansent.selected_field_video
            check_field_ascending_video = q_mysettings_hansent.check_field_ascending_video
            if selected_sorting_field_str == selected_field_video:
                if check_field_ascending_video == True:
                    check_field_ascending_video = False
                else:
                    check_field_ascending_video = True
            data = {
                'selected_field_video':selected_sorting_field_str,
                'check_field_ascending_video': check_field_ascending_video,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            print('Sorting 조건 확정 및 저장')
            return redirect('hans-ent-video-album-list')
        
        if request.POST.get('button') == 'category_filtering':
            selected_category_str = request.POST.get('selected_category')
            data = {
                'selected_category_video': selected_category_str,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            return redirect('hans-ent-video-album-list')
       
        if request.POST.get('button') == 'page_number_min':
            hans_ent_count_page_number_down(request, q_mysettings_hansent)
            return redirect('hans-ent-video-album-list')
        
        if request.POST.get('button') == 'page_number_max':
            total_num_registered_item = Video_Album.objects.count()
            hans_ent_count_page_number_up(request, q_mysettings_hansent, total_num_registered_item)
            return redirect('hans-ent-video-album-list')

        # Selected Album Merge (선택 앨범 합치기기)
        if request.POST.get('button') == 'merge_selected_video_album':
            list_video_album_id_for_checkbox_selection_str = request.POST.getlist('list_video_album_id_for_checkbox_selection[]')
            list_video_album_id_for_checkbox_selection = list(map(int, list_video_album_id_for_checkbox_selection_str))
            qs_video_album = Video_Album.objects.filter(id__in=list_video_album_id_for_checkbox_selection)
            if qs_video_album is not None and len(qs_video_album) > 0:
                
                list_dict_picture_album = []
                list_dict_video_album = []
                list_dict_picture_album_f = []
                list_dict_video_album_f = []

                q_video_album_f_id = None
                main_actor = None
                title = None
                score = 0
                rating = 0
                tags =[]

                i = 0
                for q_video_album in qs_video_album:
                    # 최초 1개만 남기고 나머지 쿼리 삭제(discard=True)
                    if i == 0:
                        # 남기는 앨범범
                        q_video_album_f_id = q_video_album.id
                        main_actor_f = q_video_album.main_actor
                        title_f = q_video_album.title
                        hashcode_f = q_video_album.hashcode
                        score_f = q_video_album.score
                        rating_f = q_video_album.rating
                        tags_f = q_video_album.tags
                        if tags_f is None:
                            tags_f = [] 
                        list_dict_picture_album_f = q_video_album.list_dict_picture_album
                        list_dict_video_album_f = q_video_album.list_dict_video_album
                        list_dict_picture_album_f[-1]["active"] = 'false'
                        list_dict_picture_album_f[-1]["discard"] = 'false'
                        if list_dict_picture_album_f is not None and len(list_dict_picture_album_f) > 0:
                            for item in list_dict_picture_album_f:
                                item["active"] = "false"
                        if list_dict_video_album_f is not None and len(list_dict_video_album_f) > 0:
                            for item in list_dict_video_album_f:
                                item["active"] = "false"
                        
                        # data = {'list_dict_picture_album': list_dict_picture_album_f,}
                        # Video_Album.objects.filter(id=q_video_album.id).update(**data)
                        # q_video_album.refresh_from_db()
                        
                        num_item_f_for_pic = len(list_dict_picture_album_f)
                        num_item_f_for_vid = len(list_dict_video_album_f)
                        print('num_item_f_for_pic', num_item_f_for_pic)
                        print('list_dict_picture_album_f', list_dict_picture_album_f)
                    else:
                        # 삭제하는 앨범
                        main_actor = q_video_album.main_actor
                        title = q_video_album.title
                        hashcode = q_video_album.hashcode
                        score = q_video_album.score
                        rating = q_video_album.rating
                        tags = q_video_album.tags
                        if tags is None:
                            tags = [] 
                        list_dict_picture_album = q_video_album.list_dict_picture_album
                        list_dict_video_album = q_video_album.list_dict_video_album

                        data = {
                            'check_discard': True,
                        }
                        Video_Album.objects.filter(id=q_video_album.id).update(**data)
                        q_video_album.refresh_from_db()
                    
                    if main_actor_f is None:
                        if main_actor is not None:
                            main_actor_f = main_actor 
                    if title_f is None:
                        if title is not None:
                            title_f = title 
                    if score != 0:
                        score_f = score_f + score 
                    if rating != 0:
                        rating_f = rating_f + rating 
                    if len(tags) > 0:
                        for item in tags:
                            if item not in tags_f:
                                tags_f.append(item)
                    
                    # 합치기 앨범의 list_dict_picture_album 합치기
                    if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                        j = 0
                        for dict_picture_album in list_dict_picture_album:
                            if dict_picture_album['id'] == 0:
                                pass 
                            elif dict_picture_album['original'] == "default-o.png" or dict_picture_album['cover'] == "default-c.png" or dict_picture_album['thumbnail'] == "default-t.png":
                                pass
                            else:
                                dict_picture_album_f = {}
                                # 변경 전 Picture 정보 확인
                                video_picture_image_name_original = dict_picture_album['original']
                                video_picture_image_name_cover = dict_picture_album['cover']
                                video_picture_image_thumbnail = dict_picture_album['thumbnail']
                                input_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_picture_image_name_original)
                                input_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_picture_image_name_cover)
                                input_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_picture_image_thumbnail)
                                # 변경 후 Picture 정보 지정
                                file_extension = video_picture_image_name_original.split('.')[-1]
                                new_image_name_original = f'{hashcode_f}-o-{num_item_f_for_pic}.{file_extension}'
                                new_image_name_cover = f'{hashcode_f}-c-{num_item_f_for_pic}.{file_extension}'
                                new_image_name_thumbnail = f'{hashcode_f}-t-{num_item_f_for_pic}.{file_extension}'
                                output_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, new_image_name_original)
                                output_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, new_image_name_cover)
                                output_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, new_image_name_thumbnail)
                                # 파일 이름 변경
                                try:
                                    os.rename(input_path_original, output_path_original)
                                except:
                                    print(f'failed rename {input_path_original}')
                                try:
                                    os.rename(input_path_cover, output_path_cover)
                                except:
                                    print(f'failed rename {input_path_cover}')
                                try:
                                    os.rename(input_path_thumbnail, output_path_thumbnail)
                                except:
                                    print(f'failed rename {input_path_thumbnail}')
                                # Picture 경로(이름) 합병되는 Hashcode로 업데이트
                                dict_picture_album_f['id'] = num_item_f_for_pic
                                dict_picture_album_f['active'] = 'false'
                                dict_picture_album_f['discard'] = 'false'
                                dict_picture_album_f['original'] = new_image_name_original
                                dict_picture_album_f['cover'] = new_image_name_cover 
                                dict_picture_album_f['thumbnail'] = new_image_name_thumbnail 
                                # List에 Item 추가
                                list_dict_picture_album_f.append(dict_picture_album_f)
                                print('list_dict_picture_album_f', list_dict_picture_album_f)
                                print('num_item_f_for_pic', num_item_f_for_pic)
                                num_item_f_for_pic = num_item_f_for_pic + 1
                            j = j + 1
                    
                    # 합치기 앨범의 list_dict_video_album 합치기    
                    if list_dict_video_album is not None and len(list_dict_video_album) > 0:
                        for dict_video_album in list_dict_video_album:
                            if dict_video_album['id'] == 0:
                                pass 
                            elif dict_video_album['video'] == 'default.mp4':
                                pass 
                            else:
                                dict_video_album_f = {}

                                try:
                                    title = dict_video_album['title'] 
                                except:
                                    title = None 
                                try:
                                    filename = dict_video_album['filename'] 
                                except:
                                    filename = None
                                try:
                                    file_size = dict_video_album['file_size'] 
                                except:
                                    file_size = None
                                # thumbnail = dict_video_album['thumbnail'] 
                                try:
                                    duration_str = dict_video_album['duration_str'] 
                                except:
                                    duration_str = None 
                                try:
                                    duration_second = dict_video_album['duration_second'] 
                                except:
                                    duration_second = None
                                try:
                                    video_name = dict_video_album['video']
                                except:
                                    video_name = None
                                if video_name is not None:
                                    video_file_path_old = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_name)
                                    file_extension = video_name.split('.')[-1]
                                    video_name_new = f'{hashcode_f}-v-{num_item_f_for_vid}.{file_extension}'
                                    video_file_path_new = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_name_new)
                                    
                                    # 비디오 파일 이름 변경
                                    try:
                                        os.rename(video_file_path_old, video_file_path_new)
                                    except:
                                        print(f'failed rename {video_file_path_old}')
                                    # 변경 전 Picture 정보 확인
                                    # list_collected_video_still_image_name = []
                                    list_video_still_image_f = []
                                    list_video_still_image = dict_video_album['still']
                                    if list_video_still_image is not None and len(list_video_still_image) > 0:
                                        j = 1
                                        for video_still_image in list_video_still_image:
                                            video_still_image_path = video_still_image['path']
                                            file_extension = video_still_image_path.split('.')[-1]
                                            # list_collected_video_still_image_name.append(video_still_image_path)
                                            input_still_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_still_image_path)
                                            video_still_image_name_new = f'{hashcode_f}-s-{num_item_f_for_vid}-{j}.{file_extension}'
                                            if j == 1:
                                                # 첫 번째 스틸 이미지를 앨범 썸네일 이미지로 등록록
                                                video_thumbnail_image_name_new = video_still_image_name_new
                                            new_input_still_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_still_image_name_new)
                                            # 스틸 이미지 파일 이름 변경
                                            try:
                                                os.rename(input_still_path, new_input_still_path)
                                            except:
                                                print(f'failed rename {input_still_path}')
                                            video_still_image['path'] = video_still_image_name_new
                                            list_video_still_image_f.append(video_still_image)
                                            j = j + 1 
                                    # Video 경로(이름) 합병되는 Hashcode로 업데이트     
                                    dict_video_album_f['id'] = num_item_f_for_vid
                                    dict_video_album_f['active'] = 'true'
                                    dict_video_album_f['discard'] = 'false'
                                    dict_video_album_f['title'] = title
                                    dict_video_album_f['filename'] = filename
                                    dict_video_album_f['file_size'] = file_size
                                    dict_video_album_f['duration_str'] = duration_str
                                    dict_video_album_f['duration_second'] = duration_second
                                    dict_video_album_f['video'] = video_name_new
                                    dict_video_album_f['thumbnail'] = video_thumbnail_image_name_new
                                    dict_video_album_f['still'] = list_video_still_image_f
                                    list_dict_video_album_f.append(dict_video_album_f)
                                    print('list_dict_video_album_f', list_dict_video_album_f)
                                    print('num_item_f_for_vid', num_item_f_for_vid)                     
                                    num_item_f_for_vid = num_item_f_for_vid + 1
                    i = i + 1

                list_dict_picture_album_f[-1]["active"] = 'true'
                list_dict_picture_album_f[-1]["discard"] = 'false'
                list_dict_video_album_f[-1]["active"] = 'true'
                list_dict_video_album_f[-1]["discard"] = 'false'
                if q_video_album_f_id is not None:
                    data = {
                        'main_actor': main_actor_f,
                        'title': title_f,
                        'score': score_f,
                        'rating': rating_f,
                        'tags': tags_f,
                        'list_dict_picture_album': list_dict_picture_album_f,
                        'list_dict_video_album': list_dict_video_album_f,
                    }
                    Video_Album.objects.filter(id=q_video_album_f_id).update(**data)
                    q_video_album.refresh_from_db()
                    
        # Selected Album Delete (선택 앨범 모두 삭제하기)
        if request.POST.get('button') == 'delete_selected_video_album':
            print('# Selected Album Delete (선택 앨범 모두 삭제하기)')
            list_video_album_id_for_checkbox_selection_str = request.POST.getlist('list_video_album_id_for_checkbox_selection[]')
            list_video_album_id_for_checkbox_selection = list(map(int, list_video_album_id_for_checkbox_selection_str))
            qs_video_album = Video_Album.objects.filter(id__in=list_video_album_id_for_checkbox_selection)
            if qs_video_album is not None and len(qs_video_album) > 0:
                for q_video_album_selected in qs_video_album:
                    delete_files_in_list_dict_xxx_album(q_video_album_selected, 'video', 'all', 'all')  ## album 종류(actor, picture, video, music 중 택 1), 싱글 쿼리, 삭제종류('all' or int(id)) 
               
        # Data Serialization
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    


    

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_video_album_list_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
    if request.method == 'GET':
        print(request.GET,)
        keyword_str = request.GET.get('keyword')
        qs_xxx = Video_Album.objects.filter(Q(check_discard=False) & (Q(title__icontains=keyword_str) | Q(main_actor__name__icontains=keyword_str) | Q(main_actor__synonyms__icontains=keyword_str)))
        list_searched_video_album_id = []
        if qs_xxx is not None and len(qs_xxx) > 0:
            for q_xxx in qs_xxx:
                list_searched_video_album_id.append(q_xxx.id)
        data = {
            'list_searched_video_album_id': list_searched_video_album_id,
        }
        MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
        return redirect('hans-ent-actor-list')
   
    if request.method == 'POST':
        keyword_str = request.POST.get('button')
        if keyword_str == 'reset':
            reset_hans_ent_video_album_list(q_mysettings_hansent)
        return redirect('hans-ent-video-album-list')
   


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_video_album_profile_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == 'GET':
        q_video_album_selected = q_mysettings_hansent.video_album_selected
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_video_album_profile_modal_view POST ======================================================= 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        selected_serialized_data_actor = {}
        selected_serialized_data_video_album = {}
        
        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_video_album_id_str = request.POST.get('selected_video_album_id')
        selected_video_album_video_id_str = request.POST.get('selected_video_album_video_id')

        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        selected_video_album_id_str = None if selected_video_album_id_str in LIST_STR_NONE_SERIES else selected_video_album_id_str
        selected_video_album_video_id_str = None if selected_video_album_video_id_str in LIST_STR_NONE_SERIES else selected_video_album_video_id_str
        
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        print('selected actor ', q_actor)

        if selected_video_album_id_str is not None and selected_video_album_id_str != '':
            selected_video_album_id = int(selected_video_album_id_str)
            q_video_album = Video_Album.objects.get(id=selected_video_album_id)
        else:
            q_video_album = None
        print('q_video_album: ', q_video_album)
        
        # Data Serialization
        if q_video_album is not None: 
            if q_actor is None:
                q_actor = q_video_album.main_actor
            selected_serialized_data_video_album = Video_Album_Serializer(q_video_album, many=False).data
        if q_actor is not None:
            print('q_actor', q_actor)
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        if selected_video_album_video_id_str is not None:
            selected_video_album_video_id = int(selected_video_album_video_id_str)
        else:
            selected_video_album_video_id = 0
        
        print('selected_video_album_video_id', selected_video_album_video_id)
        jsondata = {
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_video_album': selected_serialized_data_video_album,
            'selected_video_album_video_id': selected_video_album_video_id,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)





#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_video_album_gallery_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == 'GET':
        q_video_album_selected = q_mysettings_hansent.video_album_selected
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_video_album_gallery_modal_view POST ======================================================= 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        selected_serialized_data_actor = {}
        selected_serialized_data_video_album = {}
        
        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_video_album_id_str = request.POST.get('selected_video_album_id')
        selected_video_album_video_id_str = request.POST.get('selected_video_album_video_id')

        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        selected_video_album_id_str = None if selected_video_album_id_str in LIST_STR_NONE_SERIES else selected_video_album_id_str
        selected_video_album_video_id_str = None if selected_video_album_video_id_str in LIST_STR_NONE_SERIES else selected_video_album_video_id_str
        
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        print('selected actor ', q_actor)

        if selected_video_album_id_str is not None and selected_video_album_id_str != '':
            selected_video_album_id = int(selected_video_album_id_str)
            q_video_album = Video_Album.objects.get(id=selected_video_album_id)
        else:
            q_video_album = None
        print('q_video_album: ', q_video_album)
        
        # Data Serialization
        if q_video_album is not None: 
            if q_actor is None:
                q_actor = q_video_album.main_actor
            selected_serialized_data_video_album = Video_Album_Serializer(q_video_album, many=False).data
        if q_actor is not None:
            print('q_actor', q_actor)
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        if selected_video_album_video_id_str is not None:
            selected_video_album_video_id = int(selected_video_album_video_id_str)
        else:
            selected_video_album_video_id = 0
        
        print('selected_video_album_video_id', selected_video_album_video_id)
        jsondata = {
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_video_album': selected_serialized_data_video_album,
            'selected_video_album_video_id': selected_video_album_video_id,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)






#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_video_album_update_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    
    if request.method == "GET":
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'GET':
        selected_serialized_data_actor = {}
        selected_serialized_data_video_album = {}
        q_video_album_selected = q_mysettings_hansent.video_album_selected
        # Get selected_serialized_data
        if q_video_album_selected is not None:
            selected_serialized_data_video_album = Video_Album_Serializer(q_video_album_selected, many=False).data
            if q_video_album_selected.main_actor:
                selected_serialized_data_actor = Actor_Serializer(q_video_album_selected.main_actor, many=False).data
            else:
                q_actor = q_mysettings_hansent.actor_selected
                if q_actor is not None:
                    selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data
        # Jsondata
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'LIST_VIDEO_CATEGORY': LIST_VIDEO_CATEGORY,
            'LIST_DICT_SITE_VIDEO_INFO': LIST_DICT_SITE_VIDEO_INFO,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_video_album': selected_serialized_data_video_album,
        }
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_video_album_update_modal_view POST ========================================================== 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        
        selected_serialized_data_video_album = {}
        selected_serialized_data_actor = {}
                
        selected_video_album_id_str = str(request.POST.get('selected_video_album_id'))
        selected_video_album_picture_id_str = str(request.POST.get('selected_video_album_picture_id'))
        selected_video_album_video_id_str = str(request.POST.get('selected_video_album_video_id'))
        selected_actor_id_str = request.POST.get('selected_actor_id')
        input_text_title_str = request.POST.get('input_text_title')
        input_text_name_str = request.POST.get('input_text_name')
        input_text_studio_str = request.POST.get('input_text_studio')
        input_date_released_str = request.POST.get('input_date_released')
        input_text_tag_str = request.POST.get('input_text_tag')

        selected_site_name_video_info_str = request.POST.get('selected_site_name_video_info')
        selected_video_sub_type_str = request.POST.get('selected_video_sub_type')
        selected_filtering_category_id_str = request.POST.get('selected_filtering_category_id')
        input_streaming_video_url_str = request.POST.get('input_streaming_video_url')
        input_info_site_name_str = request.POST.get('input_info_site_name')
        input_info_site_url_str = request.POST.get('input_info_site_url')
        folder_name_str = request.POST.get('folder_name')
        file_upload_option_str = request.POST.get('file_upload_option')
        folder_upload_option_str = request.POST.get('folder_upload_option')
                
        selected_video_album_id_str = None if selected_video_album_id_str in LIST_STR_NONE_SERIES else selected_video_album_id_str
        selected_video_album_picture_id_str = None if selected_video_album_picture_id_str in LIST_STR_NONE_SERIES else selected_video_album_picture_id_str
        selected_video_album_video_id_str = None if selected_video_album_video_id_str in LIST_STR_NONE_SERIES else selected_video_album_video_id_str
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        input_text_title_str = None if input_text_title_str in LIST_STR_NONE_SERIES else input_text_title_str
        input_text_name_str = None if input_text_name_str in LIST_STR_NONE_SERIES else input_text_name_str
        input_text_studio_str = None if input_text_studio_str in LIST_STR_NONE_SERIES else input_text_studio_str
        input_date_released_str = None if input_date_released_str in LIST_STR_NONE_SERIES else input_date_released_str
        input_text_tag_str = None if input_text_tag_str in LIST_STR_NONE_SERIES else input_text_tag_str

        selected_site_name_video_info_str = None if selected_site_name_video_info_str in LIST_STR_NONE_SERIES else selected_site_name_video_info_str
        selected_video_sub_type_str = None if selected_video_sub_type_str in LIST_STR_NONE_SERIES else selected_video_sub_type_str
        selected_filtering_category_id_str = None if selected_filtering_category_id_str in LIST_STR_NONE_SERIES else selected_filtering_category_id_str
        input_streaming_video_url_str = None if input_streaming_video_url_str in LIST_STR_NONE_SERIES else input_streaming_video_url_str
        input_info_site_name_str = None if input_info_site_name_str in LIST_STR_NONE_SERIES else input_info_site_name_str
        input_info_site_url_str = None if input_info_site_url_str in LIST_STR_NONE_SERIES else input_info_site_url_str
        folder_name_str = None if folder_name_str in LIST_STR_NONE_SERIES else folder_name_str
        file_upload_option_str = None if file_upload_option_str in LIST_STR_NONE_SERIES else file_upload_option_str
        folder_upload_option_str = None if folder_upload_option_str in LIST_STR_NONE_SERIES else folder_upload_option_str
        
        print('selected_actor_id_str', selected_actor_id_str)
        print('selected_video_album_id_str', selected_video_album_id_str)
        print('folder_name_str', folder_name_str)
        print('file_upload_option_str', file_upload_option_str)
        print('folder_upload_option_str', folder_upload_option_str)

        # 선택된 모델 정보 획득
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        
        # 선택된 앨범 정보 획득
        if selected_video_album_id_str is not None and selected_video_album_id_str != '' :
            selected_video_album_id = int(selected_video_album_id_str)
            q_video_album_selected = Video_Album.objects.get(id=selected_video_album_id)
            if q_video_album_selected is not None:
                if q_actor is None:
                    q_actor = q_video_album_selected.main_actor
        else:
            q_video_album_selected = None 


        # Video Album Reload
        if request.POST.get('button') == 'refresh_selected_album':
            # print('Video Album Reload 개시!!!!!!!!!!!!! 2')
            if q_video_album_selected is not None:
                selected_vault = q_video_album_selected.selected_vault
                # print('Video Album Reload 개시!!!!!!!!!!!!! 3')
                hashcode = q_video_album_selected.hashcode
                                
                # 검색할 디렉토리와 문자열
                RELATIVE_PATH_VIDEO = f'{selected_vault}/video'
                root_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
                # root_dir = f"/django-project/site/public/media/{selected_vault}/video/"
                                
                # Collect all file names
                file_names = []
                for root, dirs, files in os.walk(root_dir):
                    for file in files:
                        file_names.append(os.path.join(root, file))
                # print(f'len(file_names): {len(file_names)}')

                list_matched_file_names = []
                # Print all file paths
                if len(file_names) > 0:
                    for name in file_names:
                        try:
                            name_str = str(name)
                        except:
                            name_str = None 
                        if name_str is not None and hashcode in name_str:
                            list_matched_file_names.append(name_str)
                # print(f'len(list_matched_file_names): {len(list_matched_file_names)}')

                list_dict_picture_album = q_video_album_selected.list_dict_picture_album
                if list_dict_picture_album is None:
                    list_dict_picture_album = DEFAULT_LIST_DICT_PICTURE_ALBUM
                list_dict_video_album = q_video_album_selected.list_dict_video_album
                if list_dict_video_album is None:
                    list_dict_video_album = DEFAULT_LIST_DICT_VIDEO_ALBUM

                # print(f'len(list_dict_picture_album) 1: {len(list_dict_picture_album)}')   
                # print(f'len(list_dict_video_album) 1: {len(list_dict_video_album)}')   

                if len(list_matched_file_names) > 0:
                    # 저장된 파일명과 같은 파일명이 Album에 있는지 없는지 체크, 없으면 Album에 등록해준다.
                    i = 0
                    v = 0
                    p = 0
                    for file_path in list_matched_file_names:
                        file_name = file_path.split('/')[-1]
                        file_extension = file_name.split('.')[-1]
                        find_id = file_name.split('.')[0]
                        try:
                            if '-v-' in find_id:
                                file_type = 'video'
                                find_id = find_id.split('-v-')[-1]
                                find_id = int(find_id)
                            else:
                                file_type = None
                                find_id = None
                        except:
                            file_type = None
                            find_id = None
                        # print(f'file_name: {file_name}')
                        # print(f'find_id: {find_id}')
                        # print(f'file_type: {file_type}')
                        
                        if find_id is not None:
                            dict_video_album_new = {"id":0, "video":"default.mp4", "original":"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "still":[{"time":1, "path":"default-s.png"}], "active":"false", "discard":"false", "streaming":"false"}
                            dict_video_album_new['id'] = find_id
                            dict_video_album_new['discard'] = 'true'

                            check_file_video_registered = False
                            if file_extension in LIST_VIDEO_EXTENSION:
                                v = v + 1
                                # print('# 비디오 파일이면면')
                                # 파일이 등록되었는지 확인
                                for dict_video_album in list_dict_video_album:
                                    if dict_video_album:
                                        # print('dict_video_album', dict_video_album)
                                        if dict_video_album['video'] == file_name:
                                            # print('파일이 등록되었음!! Skip한다.')
                                            check_file_video_registered = True
                                            break 
                                    else:
                                        # 빈 Dictionary 인 경우
                                        list_dict_video_album.remove(dict_video_album)
                                # print(f'check_file_video_registered: {check_file_video_registered}')

                                # 파일은 존재하나 등록안된 비디오 정보를 등록하기
                                if find_id is not None:
                                    if check_file_video_registered == False:
                                        # print('# Video 파일은 있으나 Album에 등록안된 경우!!, 등록해준다.')
                                        if file_type == 'video':
                                            dict_video_album_new['video'] = file_name
                                            dict_video_album_new['discard'] = 'false'
                                            # print(f'dict_video_album_new {dict_video_album_new}')
                                            list_dict_video_album.append(dict_video_album_new)
                        
                        # print(f'list_dict_video_album {list_dict_video_album}')
                        # print(f'비디오 등록 마침, len(list_dict_video_album)  : {len(list_dict_video_album)}')

                    for file_path in list_matched_file_names:
                        file_name = file_path.split('/')[-1]
                        file_extension = file_name.split('.')[-1]
                        find_id = file_name.split('.')[0]

                        try:
                            if '-v-' in find_id:
                                file_type = 'video'
                                find_id = find_id.split('-v-')[-1]
                                find_id = int(find_id)
                                find_id = None
                            elif '-o-' in find_id:
                                file_type = 'original'
                                find_id = find_id.split('-o-')[-1]
                                find_id = int(find_id)
                            elif '-c-' in find_id:
                                file_type = 'cover'
                                find_id = find_id.split('-c-')[-1]
                                find_id = int(find_id)
                            elif '-t-' in find_id:
                                file_type = 'thumbnail'
                                find_id = find_id.split('-t-')[-1]
                                find_id = int(find_id)
                            elif '-s-' in find_id:
                                file_type = 'still'
                                find_id = find_id.split('-s-')[-1]
                                find_id = int(find_id)
                                find_id = None
                            else:
                                file_type = None
                                find_id = None
                        except:
                            file_type = None
                            find_id = None
                        
                        if file_extension in LIST_PICTURE_EXTENSION and find_id is not None:
                            # print('# 사진 파일이면면')
                            p = p + 1
                            # Video 앨범에 등록하기기
                            check_file_picture_original_registered = False
                            check_file_picture_cover_registered = False
                            check_file_picture_thumbnail_registered = False
                            for dict_video_album in list_dict_video_album:
                                # print('dict_video_album', dict_video_album)
                                if dict_video_album:
                                    if dict_video_album['original'] == file_name:
                                        check_file_picture_original_registered = True
                                    if dict_video_album['cover'] == file_name:
                                        check_file_picture_cover_registered = True
                                    if dict_video_album['thumbnail'] == file_name:
                                        check_file_picture_thumbnail_registered = True
                                else:
                                    # 빈 Dictionary 인 경우
                                    list_dict_video_album.remove(dict_video_album)
                                # 존재여부 상태체크 결과
                            
                            # Video 파일에서, 기 등록된 ID가 있는지 체크. 있으면 기존 Item에 정보를 업데이트
                            # print(f'len(list_dict_video_album) : {len(list_dict_video_album)}')
                            for dict_video_album in list_dict_video_album:
                                if dict_video_album['id'] == find_id:
                                    
                                    check_id_not_found = True
                                    for dict_picture_album in list_dict_picture_album:
                                        if dict_picture_album['id'] == find_id:
                                            dict_picture_album_new = dict_picture_album
                                            check_id_not_found = False
                                            break
                                    if check_id_not_found == True:
                                        dict_picture_album_new = {'id':0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "file_size":"unknown", "image_size":[],"active":"false", "discard":"false", "streaming":"false"}
                                        dict_picture_album_new['id'] = find_id
                                        dict_picture_album_new['discard'] = 'false'
                                   
                                    if check_file_picture_original_registered == False:
                                        # print('# Original 파일은 있으나 Album에 등록안된 경우, 등록해준다.')
                                        if file_type == 'original':
                                            dict_video_album['original']=file_name
                                            dict_picture_album_new['original']=file_name
                                    if check_file_picture_cover_registered == False:
                                        # print('# Cover 파일은 있으나 Album에 등록안된 경우, 등록해준다.')
                                        if file_type == 'cover':
                                            dict_video_album['cover']=file_name
                                            dict_picture_album_new['cover']=file_name
                                    if check_file_picture_thumbnail_registered == False:
                                        # print('# Thumbnail 파일은 있으나 Album에 등록안된 경우, 등록해준다.')
                                        if file_type == 'thumbnail':
                                            dict_video_album['thumbnail']=file_name
                                            dict_picture_album_new['thumbnail']=file_name
                                    # print(f'dict_video_album 2: {dict_video_album}')
                                    if check_id_not_found == True:
                                        list_dict_picture_album.append(dict_picture_album_new)
                                    break
                        i = i + 1

                    # print(f'i : {i}')
                    # print(f'v : {v}')
                    # print(f'p : {p}')

                    if len(list_dict_picture_album) > 1:
                        list_dict_picture_album[0]['activate'] = 'false'
                        list_dict_picture_album[0]['discard'] = 'true'
                        list_dict_picture_album[-1]['activate'] = 'true'
                    if len(list_dict_video_album) > 1:
                        list_dict_video_album[0]['activate'] = 'false'
                        list_dict_video_album[0]['discard'] = 'true'
                        list_dict_video_album[-1]['activate'] = 'true'

                    if len(list_dict_picture_album) == 1:
                        list_dict_picture_album[0]['activate'] = 'true'
                        list_dict_picture_album[0]['discard'] = 'false'
                    if len(list_dict_video_album) == 1:
                        list_dict_video_album[0]['activate'] = 'true'
                        list_dict_video_album[0]['discard'] = 'false'

                    # print(f'len(list_dict_picture_album) 2: {len(list_dict_picture_album)}')   
                    # print(f'len(list_dict_video_album) 2: {len(list_dict_video_album)}')   

                    # print('# --------------------------------------------------------------------------------------------------------------------')
                    # print('# --------------------------------------------------------------------------------------------------------------------')
                    # print(f'list_dict_picture_album 2: {list_dict_picture_album}')   
                    # print('# --------------------------------------------------------------------------------------------------------------------')
                    # print('# --------------------------------------------------------------------------------------------------------------------')

                    # print('# --------------------------------------------------------------------------------------------------------------------')
                    # print('# --------------------------------------------------------------------------------------------------------------------')
                    # print(f'list_dict_video_album 2: {list_dict_video_album}')   
                    # print('# --------------------------------------------------------------------------------------------------------------------')
                    # print('# --------------------------------------------------------------------------------------------------------------------')

                    data = {
                        'list_dict_picture_album': list_dict_picture_album,
                        'list_dict_video_album': list_dict_video_album,
                    }
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)

                # Still 이미지 생성
                save_video_album_video_still_images_in_task([q_video_album_selected.id])




        # Video Album 쿼리 생성하기
        if request.POST.get('button') == 'create_or_update':
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
                print(f'비디오 앨범 생성!!!!!!!!!!!  ID : {q_video_album_selected.id}, length: {len(q_video_album_selected.list_dict_video_album)}')

                if q_actor is not None:
                    if q_video_album_selected.main_actor is None:
                        data = {'main_actor':q_actor}
                        Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                        q_video_album_selected.refresh_from_db()

        # 앨범 비디오 Still 이미지 생성하기
        if request.POST.get('button') == 'generate_video_still_image_all':
            print('# 앨범 비디오 Still 이미지 생성하기 시작 Ver.2 All')
            if q_video_album_selected is not None:
                print('q_video_album_selected', q_video_album_selected)
                save_video_album_video_still_images_in_task([q_video_album_selected.id])
                q_video_album_selected.refresh_from_db()
                

        # 앨범 커버 이미지 변경하기
        if request.POST.get('button') == 'change_video_album_cover_image':
            print('# 앨범 커버 이미지 변경하기')
            if selected_video_album_picture_id_str is not None and selected_video_album_picture_id_str != '':
                selected_video_album_picture_id = int(selected_video_album_picture_id_str)
                if q_video_album_selected is not None:
                    list_dict_picture_album = q_video_album_selected.list_dict_picture_album
                    # acitve 모두 false 변경 및 선택된 이미지만 Active true로 변경
                    for dict_picture_album in list_dict_picture_album:
                        dict_picture_album['active'] = 'false'
                        if dict_picture_album['id'] == selected_video_album_picture_id:
                            dict_picture_album['active'] = 'true'
                    data = {'list_dict_picture_album': list_dict_picture_album}
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                    q_video_album_selected.refresh_from_db()
        
        # 비디오 앨범 커버 이미지 삭제하기(선택한 이미지만)
        if request.POST.get('button') == 'remove_video_album_cover_image':
            print('# 비디오 앨범 이미지 삭제하기')
            if selected_video_album_picture_id_str is not None and selected_video_album_picture_id_str != '':
                selected_video_album_picture_id = int(selected_video_album_picture_id_str)
                if q_video_album_selected is not None:
                    delete_files_in_list_dict_xxx_album(q_video_album_selected, 'video', 'image', selected_video_album_picture_id)  ## album 종류(actor, picture, video, music 중 택 1), 싱글 쿼리, 삭제종류('all' or int(id)) 
                    
        # 비디오 앨범 비디오 삭제하기(선택한 비디오만)
        if request.POST.get('button') == 'remove_video_album_video':
            print('# 비디오 앨범 비디오 삭제하기')
            if selected_video_album_video_id_str is not None and selected_video_album_video_id_str != '':
                selected_video_album_video_id = int(selected_video_album_video_id_str)
                if q_video_album_selected is not None:
                    delete_files_in_list_dict_xxx_album(q_video_album_selected, 'video','video', selected_video_album_video_id)  ## album 종류(actor, picture, video, music 중 택 1), 싱글 쿼리, 삭제종류('all' or int(id)) 

        # 비디오 앨범 통으로 삭제하기
        if request.POST.get('button') == 'remove_video_album':
            print('# 비디오 앨범 통으로 삭제하기', q_video_album_selected)
            if q_video_album_selected is not None:
                delete_files_in_list_dict_xxx_album(q_video_album_selected, 'video', 'all', 'all')  ## album 종류(actor, picture, video, music 중 택 1), 싱글 쿼리, 삭제종류('all' or int(id)) 
            return redirect('hans-ent-video-album-list')

        # 업로드 타이틀 정보 저장하기
        if input_text_title_str is not None and input_text_title_str != '':
            print('# 업로드 타이틀 정보 저장하기')
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            data = {
                'title': input_text_title_str,
            }
            Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
            q_video_album_selected.refresh_from_db()
            
        # 업로드 모델이름 저장하기
        if input_text_name_str is not None and input_text_name_str != '':
            print('# 업로드 모델이름 저장하기')
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            data = {
                'name': input_text_name_str,
            }
            Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
            q_video_album_selected.refresh_from_db()
        
        # 업로드 스튜디오 정보 저장하기
        if input_text_studio_str is not None and input_text_studio_str != '':
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            data = {
                'studio': input_text_studio_str,
            }
            Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
            q_video_album_selected.refresh_from_db()

        # 사진 앨범 타입 선택하기
        if selected_video_sub_type_str is not None and selected_video_sub_type_str != '':
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            data = {
                'types': selected_video_sub_type_str,
            }
            Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
            q_video_album_selected.refresh_from_db()

        # 업로드 출시일 정보 저장하기
        if input_date_released_str is not None and input_date_released_str != '':
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            date_string = str(input_date_released_str)
            date_format = '%Y-%m-%d'
            import datetime
            date_object = datetime.datetime.strptime(date_string, date_format).date()
            data = {
                'date_released': date_object,
            }
            Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
            q_video_album_selected.refresh_from_db()
        
        # 카테고리 저장하기
        if selected_filtering_category_id_str is not None and selected_filtering_category_id_str != '':
            print('# 카테고리 저장하기')
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            data = {
                'category': selected_filtering_category_id_str,
            }
            Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
            q_video_album_selected.refresh_from_db()

        # Website 등록
        if input_info_site_url_str is not None:
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            list_dict_info_url = q_video_album_selected.list_dict_info_url
            if list_dict_info_url is None:
                list_dict_info_url = []
                
            if selected_site_name_video_info_str is not None and selected_site_name_video_info_str != 'blank':
                # preset에서 선택한 경우
                for DICT_SITE_VIDEO_INFO in LIST_DICT_SITE_VIDEO_INFO:
                    if DICT_SITE_VIDEO_INFO['key'] == selected_site_name_video_info_str:
                        site_name = DICT_SITE_VIDEO_INFO['name']
                list_dict_info_url.append({"key":input_info_site_name_str, 'name': site_name, "url":input_info_site_url_str})
                data = {
                    'list_dict_info_url': list_dict_info_url,
                }
                Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                q_video_album_selected.refresh_from_db()
            
            elif input_info_site_name_str is not None:
                # site 이름 직접 입력한 경우
                site_key = None
                for DICT_SITE_VIDEO_INFO in LIST_DICT_SITE_VIDEO_INFO:
                    if DICT_SITE_VIDEO_INFO['name'] == input_info_site_name_str:
                        site_key = DICT_SITE_VIDEO_INFO['key']
                        break 
                if site_key is None:
                    # 이름으로 key 생성
                    site_key = input_info_site_name_str.strip()
                    site_key = site_key.replace(' ', '')
                    site_key = site_key.lower() 
                list_dict_info_url.append({"key":site_key, 'name': input_info_site_name_str, "url":input_info_site_url_str})
                data = {
                    'list_dict_info_url': list_dict_info_url,
                }
                Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                q_video_album_selected.refresh_from_db()
            else:
                pass 

        # video album video order 변경하기 (ID 감소)
        if request.POST.get('button') == 'video_album_video_order_decrease':
            print('# video album video order 변경하기 (ID 감소) q_video_album_selected', q_video_album_selected)
            if q_video_album_selected is not None:
                list_dict_video_album = q_video_album_selected.list_dict_video_album
                if list_dict_video_album is not None and len(list_dict_video_album) > 0:
                    if selected_video_album_video_id_str is not None:
                        try:
                            selected_video_album_video_id = int(selected_video_album_video_id_str)
                        except:
                            selected_video_album_video_id = None
                        print('selected_video_album_video_id', selected_video_album_video_id)
                        if selected_video_album_video_id is not None:
                            if selected_video_album_video_id > 1:
                                # 선택한 video id 덮어쓰여지기 방지를 위해 99999 로 변경
                                for item in list_dict_video_album:
                                    if item['id'] == selected_video_album_video_id:
                                        item['id'] = 99999
                                # default 및 99999 제외, 선택 item과 위치 교환할 item은 선택 item id 부여여
                                for item in list_dict_video_album:
                                    if item['id'] != 0 and item['id'] != 99999 and item['id'] == selected_video_album_video_id - 1:
                                        item['id'] = selected_video_album_video_id
                                # 따로 빼둔 선택된 video id를 id - 1 하기
                                for item in list_dict_video_album:
                                    if item['id'] == 99999:
                                        item['id'] = selected_video_album_video_id - 1
                                data = {
                                    'list_dict_video_album': list_dict_video_album,
                                }
                                Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                                q_video_album_selected.refresh_from_db()
                                print(f'ID 감소 완료')
                                jsondata = {
                                    'list_dict_video_album': list_dict_video_album,
                                    'selected_video_album_video_id': selected_video_album_video_id - 1,
                                }
                                return JsonResponse(jsondata, safe=False)  
                            else:
                                print('젤 아래로 배치(마지막)')
                                # 선택한 video id 덮어쓰여지기 방지를 위해 99999 로 변경
                                for item in list_dict_video_album:
                                    if item['id'] == selected_video_album_video_id:
                                        item['id'] = 99999
                                # default 및 99999 제외, 선택 item과 위치 교환할 item은 선택 item id 부여여
                                for item in list_dict_video_album:
                                    if item['id'] != 0 and item['id'] != 99999 and item['id'] == len(list_dict_video_album) - 1:
                                        item['id'] = selected_video_album_video_id
                                # 따로 빼둔 선택된 video id를 id - 1 하기
                                for item in list_dict_video_album:
                                    if item['id'] == 99999:
                                        item['id'] = len(list_dict_video_album) - 1
                                data = {
                                    'list_dict_video_album': list_dict_video_album,
                                }
                                Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                                q_video_album_selected.refresh_from_db()
                                print(f'ID 감소 완료')
                                jsondata = {
                                    'list_dict_video_album': list_dict_video_album,
                                    'selected_video_album_video_id': len(list_dict_video_album) - 1,
                                }
                                return JsonResponse(jsondata, safe=False)  
                        else:
                            print('selected_video_album_video_id 이 없습니다.')
                            pass
                    else:
                        print('selected_video_album_video_id_str 이 없습니다.')
                        pass
                else:
                    print('list_dict_video_album 이 None 입니다. (저장된 video가 없습니다.).')
                    pass
            else:
                print('q_video_album_selected 이 없습니다.')
                pass

        # video album video order 변경하기 (ID 증가)
        if request.POST.get('button') == 'video_album_video_order_increase':
            print('# video album video order 변경하기 (ID 증가)  q_video_album_selected', q_video_album_selected)
            if q_video_album_selected is not None:
                list_dict_video_album = q_video_album_selected.list_dict_video_album
                if list_dict_video_album is not None and len(list_dict_video_album) > 0:
                    if selected_video_album_video_id_str is not None:
                        try:
                            selected_video_album_video_id = int(selected_video_album_video_id_str)
                        except:
                            selected_video_album_video_id = None
                        print('selected_video_album_video_id', selected_video_album_video_id)
                        if selected_video_album_video_id is not None:
                            if selected_video_album_video_id < len(list_dict_video_album) - 1:
                                # 선택한 video id 덮어쓰여지기 방지를 위해 99999 로 변경
                                for item in list_dict_video_album:
                                    if item['id'] == selected_video_album_video_id:
                                        item['id'] = 99999
                                # default 및 99999 제외, 선택 item과 위치 교환할 item은 선택 item id 부여여
                                for item in list_dict_video_album:
                                    if item['id'] != 0 and item['id'] != 99999 and item['id'] == selected_video_album_video_id + 1:
                                        item['id'] = selected_video_album_video_id
                                # 따로 빼둔 선택된 video id를 id + 1 하기
                                for item in list_dict_video_album:
                                    if item['id'] == 99999:
                                        item['id'] = selected_video_album_video_id + 1
                                data = {
                                    'list_dict_video_album': list_dict_video_album
                                }
                                Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                                q_video_album_selected.refresh_from_db()
                                print(f'ID 증가 완료 {selected_video_album_video_id + 1}')
                                jsondata = {
                                    'list_dict_video_album': list_dict_video_album,
                                    'selected_video_album_video_id': selected_video_album_video_id + 1,
                                }
                                return JsonResponse(jsondata, safe=False)  
                            else:
                                print('젤 위로 배치(처음)')
                                # 선택한 video id 덮어쓰여지기 방지를 위해 99999 로 변경
                                # id값이 큰 아이템이 앞에 오도록
                                list_dict_video_album_sorted = sorted(list_dict_video_album, key=lambda x: x['id'], reverse=True)
                                for item in list_dict_video_album_sorted:
                                    if item['id'] == selected_video_album_video_id:
                                        item['id'] = 99999
                                # default 및 99999 제외, 선택 item과 위치 교환할 item은 선택 item id 부여여
                                for item in list_dict_video_album_sorted:
                                    if item['id'] != 0 and item['id'] != 99999 :
                                        old_id = item['id'] 
                                        new_id = old_id + 1
                                        item['id'] = new_id
                                # 따로 빼둔 선택된 video id를 id - 1 하기
                                for item in list_dict_video_album_sorted:
                                    if item['id'] == 99999:
                                        item['id'] = 1
                                list_dict_video_album = sorted(list_dict_video_album_sorted, key=lambda x: x['id'], reverse=False)
                                data = {
                                    'list_dict_video_album': list_dict_video_album
                                }
                                Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                                q_video_album_selected.refresh_from_db()
                                print(f'ID 증가 완료 {selected_video_album_video_id + 1}')
                                jsondata = {
                                    'list_dict_video_album': list_dict_video_album,
                                    'selected_video_album_video_id': 1,
                                }
                                return JsonResponse(jsondata, safe=False)  
                        else:
                            print('selected_video_album_video_id 이 없습니다.')
                            pass
                    else:
                        print('selected_video_album_video_id_str 이 없습니다.')
                        pass
                else:
                    print('list_dict_video_album 이 None 입니다. (저장된 video가 없습니다.).')
                    pass
            else:
                print('q_video_album_selected 이 없습니다.')
                pass

        # video album video order 리셋하기
        if request.POST.get('button') == 'video_album_video_order_reset':
            print('# video album video order 변경하기 (ID 증가)  q_video_album_selected', q_video_album_selected)
            if q_video_album_selected is not None:
                list_dict_video_album = q_video_album_selected.list_dict_video_album
                if list_dict_video_album is not None and len(list_dict_video_album) > 0:
                    i = 1
                    for item in list_dict_video_album:
                        if item['id'] != 0:
                            item['id'] = i
                            i = i + 1
                    data = {
                        'list_dict_video_album': list_dict_video_album
                    }
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                    q_video_album_selected.refresh_from_db()
                    print(f'ID 리셋 완료 ')
                    jsondata = {
                        'list_dict_video_album': list_dict_video_album,
                        'selected_video_album_video_id': 0,
                    }
                    return JsonResponse(jsondata, safe=False)  

        # Tag 저장하기
        if input_text_tag_str is not None and input_text_tag_str != '':
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            tags = q_video_album_selected.tags
            if tags is None:
                tags = []
            if input_text_tag_str not in tags:
                print('tag save', input_text_tag_str)
                tags.append(input_text_tag_str)
            data = {
                'tags': tags,
            }
            Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
            q_video_album_selected.refresh_from_db()

        # Actor 선택하기
        if request.POST.get('button') == 'actor_select':
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            if q_video_album_selected is not None and q_actor is not None:
                print('선택된 모델', q_actor)
                data = {
                    'main_actor': q_actor,
                }
                Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                q_video_album_selected.refresh_from_db()

        # Actor 선택해제하기
        if request.POST.get('button') == 'actor_select_reset':
            print('# 모델 선택해제하기')
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            if q_video_album_selected is not None:
                data = {
                    'main_actor': None,
                }
                Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                q_video_album_selected.refresh_from_db() 
        
        # 스트리밍 Video URL 등록하기
        if input_streaming_video_url_str is not None:
            print('***************************** input_streaming_video_url_str', input_streaming_video_url_str)
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            if q_video_album_selected is not None:
                list_dict_video_album = q_video_album_selected.list_dict_video_album
                list_dict_picture_album = q_video_album_selected.list_dict_picture_album

                # 디폴트 Disable
                for item in list_dict_video_album:
                    item['active'] = 'false'
                    if item['id'] == 0:
                        item['discard'] = 'true'
                for item in list_dict_picture_album:
                    item['active'] = 'false'
                    if item['id'] == 0:
                        item['discard'] = 'true'

                list_dict_info_url = q_video_album_selected.list_dict_info_url
                if list_dict_info_url is None:
                    list_dict_info_url = []
                if 'youtube' in input_streaming_video_url_str:
                    print('# parsing youtube data')
                    return_value = get_youtube_video_info(input_streaming_video_url_str)
                    for k, v in return_value.items():
                        print(f'{k}: {v}')
                    title = return_value['title']
                    thumbnail = return_value['thumbnail']
                    
                    list_dict_info_url.append(return_value)
                    list_dict_video_album.append({
                        "id": len(list_dict_video_album), 
                        "video": "none", 
                        'video_url': input_streaming_video_url_str,
                        "original":"default-o.png", 
                        "cover": thumbnail, 
                        "thumbnail":thumbnail, 
                        "still":[{"time":1, "path":"default-s.png"}], 
                        "active":"true", 
                        "discard":"false",
                        "streaming":"true",
                    })
                    
                    list_dict_picture_album.append({
                        "id": len(list_dict_picture_album), 
                        "original": thumbnail, 
                        "cover": thumbnail, 
                        "thumbnail": thumbnail,
                        "active": "true", 
                        "discard": "false", 
                        "streaming":"true",
                    })
                    data = {
                        'title': title,
                        'list_dict_info_url': list_dict_info_url,
                        'list_dict_picture_album': list_dict_picture_album,
                        'list_dict_video_album': list_dict_video_album,
                    }
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                    q_video_album_selected.refresh_from_db() 
                else:
                    list_dict_video_album.append(
                        {
                            "id": len(list_dict_video_album), 
                            "video": "none", 
                            'video_url': input_streaming_video_url_str,
                            "original":"default-o.png", 
                            "cover":"default-c.png", 
                            "thumbnail":"default-t.png", 
                            "still":[{"time":1, "path":"default-s.png"}], 
                            "active":"true", 
                            "discard":"false",
                            "streaming":"true",
                        }
                    )
                    data = {
                        'list_dict_video_album': list_dict_video_album,
                    }
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                    q_video_album_selected.refresh_from_db() 
            pass

        # 파일 업로드 했으면 저장하기
        if request.FILES:
            print('# 파일 업로드 했으면 저장하기')
            files = request.FILES.getlist('files')

            if len(files) > 1:
                print('############################################## 파일 두 개 이상')
                if file_upload_option_str == 'folder_each_file_single_album' or  file_upload_option_str == 'files_individual_album':
                    print('############################################## 파일들을 각각의 앨범으로')
                    i = 0
                    for file in files:
                        print('i', i)
                        new_files = []
                        new_files.append(file)
                        if i != 0:
                            q_video_album_selected_new = create_video_album()
                            list_dict_video_album= q_video_album_selected_new.list_dict_video_album
                            print(f'list_dict_video_album: {list_dict_video_album}')
                            save_files_in_list_dict_xxx_album(q_video_album_selected_new, new_files, type_album='video')
                        else:
                            save_files_in_list_dict_xxx_album(q_video_album_selected, new_files, type_album='video')
                            if q_video_album_selected.main_actor is not None:
                                try:
                                    collect_images_from_registered_video_album_for_actor_profile_cover_image(q_video_album_selected.main_actor)
                                except:
                                    pass
                        i = i + 1
                    pass 
                else:
                    if q_video_album_selected is not None:
                        print(f'q_video_album_selected id: {q_video_album_selected.id}')
                        files = None if files in LIST_STR_NONE_SERIES else files
                        if files is not None and len(files) > 0:
                            save_files_in_list_dict_xxx_album(q_video_album_selected, files, type_album='video')
                            if q_video_album_selected.main_actor is not None:
                                try:
                                    collect_images_from_registered_video_album_for_actor_profile_cover_image(q_video_album_selected.main_actor)
                                except:
                                    pass
                    else:
                        print(f'q_video_album_selected 가 없습니다.1')
            else:
                print('############################################## 파일 하나')
                print('############################################## 업로드드 파일(들)을 하나의 앨범에 포함')
                if q_video_album_selected is not None:
                    print(f'q_video_album_selected list_dict_video_album length: {len(q_video_album_selected.list_dict_video_album)}')
                    print(f'q_video_album_selected id: {q_video_album_selected.id}')
                    files = None if files in LIST_STR_NONE_SERIES else files
                    if files is not None and len(files) > 0:
                        save_files_in_list_dict_xxx_album(q_video_album_selected, files, type_album='video')
                        if q_video_album_selected.main_actor is not None:
                            try:
                                collect_images_from_registered_video_album_for_actor_profile_cover_image(q_video_album_selected.main_actor)
                            except:
                                pass
                else:
                    print(f'q_video_album_selected 가 없습니다.2')


                

        # 파일만 업로드 했으면 폴더명으로 추가정보 기입하기
        """
        File Upload Options:
            folder_name_for_nothing
            folder_name_as_album_title
            folder_name_as_actor_name
            folder_name_as_album_title_and_actor_name
        """
        if folder_name_str is not None:
            print('# 파일만 업로드 했으면 폴더명으로 추가정보 기입하기 : ', file_upload_option_str)
            if q_video_album_selected is not None:
                if file_upload_option_str == 'folder_name_for_nothing':
                    pass
                elif file_upload_option_str == 'folder_name_as_album_title':
                    data = {
                        'title': folder_name_str,
                    }
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                    q_video_album_selected.refresh_from_db() 
                elif file_upload_option_str == 'folder_name_as_actor_name':
                    q_actor = Actor.objects.filter(Q(check_discard=False) & Q(name=folder_name_str)).last()
                    if q_actor is None:
                        q_actor = create_actor()
                        data = {
                            'name':folder_name_str,
                        }
                        Actor.objects.filter(id=q_actor.id).update(**data)
                        q_actor.refresh_from_db()
                    data = {
                        'main_actor': q_actor,
                    }
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                    q_video_album_selected.refresh_from_db() 
                elif file_upload_option_str == 'folder_name_as_album_title_and_actor_name':
                    q_actor = Actor.objects.filter(Q(check_discard=False) & Q(name=folder_name_str)).last()
                    if q_actor is None:
                        q_actor = create_actor()
                        data = {
                            'name':folder_name_str,
                        }
                        Actor.objects.filter(id=q_actor.id).update(**data)
                        q_actor.refresh_from_db()
                    data = {
                        'title': folder_name_str,
                        'main_actor': q_actor,
                    }
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                    q_video_album_selected.refresh_from_db() 
                elif file_upload_option_str == 'folder_each_file_single_album':
                    pass

        # Data Serialization
        if q_video_album_selected is not None:
            print('# 앨범이 등록되어 있다면', q_video_album_selected)
            print('q_actor', q_actor)
            if q_actor is None:
                if q_video_album_selected.main_actor is not None:
                    q_actor = q_video_album_selected.main_actor
               
            # Settings에 선택된 Album 쿼리 등록
            print('세팅에 현재 앨범 등록하기', q_mysettings_hansent)
            data = {
                'video_album_selected': q_video_album_selected
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            q_mysettings_hansent.refresh_from_db()

            # main actor 등록
            if q_video_album_selected.main_actor is None:
                if q_actor is not None:
                    data = {"main_actor": q_actor}
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                    q_video_album_selected.refresh_from_db()
            
            # Data Serialize
            selected_serialized_data_video_album = Video_Album_Serializer(q_video_album_selected, many=False).data
        
        if q_actor is not None:
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        # print('selected_serialized_data_video_album', selected_serialized_data_video_album)
        jsondata = {
            'LIST_VIDEO_CATEGORY': LIST_VIDEO_CATEGORY,
            'LIST_DICT_SITE_VIDEO_INFO': LIST_DICT_SITE_VIDEO_INFO,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_video_album': selected_serialized_data_video_album,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)  





#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_video_album_update_modal_actor_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == "GET":
        print('*********************************************************************** get: ', request)
        keyword_str = request.GET.get('keyword')
        print('keyword_str', keyword_str)
        qs_xxx = Actor.objects.filter(Q(check_discard=False) & (Q(name__icontains=keyword_str) | Q(synonyms__icontains=keyword_str)))
        list_serialized_data_actor = []
        if qs_xxx is not None and len(qs_xxx) > 0:
            list_serialized_data_actor = Actor_Serializer(qs_xxx, many=True).data
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'list_serialized_data_actor': list_serialized_data_actor, 
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)

    if request.method == 'POST':
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)












#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
# Music Album  
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################




# ----------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_music_album_list(request):
    import datetime
    ls_today = datetime.date.today()
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
    if request.method == 'GET':
        total_num_registered_item = Music_Album.objects.count()
        # Searching 결과값 찾기
        list_searched_xxx_id = q_mysettings_hansent.list_searched_music_album_id
        if list_searched_xxx_id is not None:
            total_num_searched_item = len(list_searched_xxx_id)
        else:
            total_num_searched_item = 0
        # Sorting Submenu 조건
        selected_field_sorting_str = q_mysettings_hansent.selected_field_music
        selected_category_music_str = q_mysettings_hansent.selected_category_music
        # Acending or Decending?
        field_ascending_str = q_mysettings_hansent.check_field_ascending_music
        if field_ascending_str == False:
            selected_field_sorting = f'-{selected_field_sorting_str}'
        else:
            selected_field_sorting = selected_field_sorting_str
        # 화면에 표시할 아이템 개수 지정
        count_page_number = q_mysettings_hansent.count_page_number_music
        count_page_number_min = (count_page_number - 1) * LIST_NUM_DISPLAY_IN_PAGE
        count_page_number_max = count_page_number * LIST_NUM_DISPLAY_IN_PAGE
        # 쿼리 필터링
        # if list_searched_xxx_id is not None and len(list_searched_xxx_id) > 0:
        #     qs_xxx = Music_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        # else:
        #     qs_xxx = Music_Album.objects.filter(Q(check_discard=False)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        # print('qs_xxx', qs_xxx)
        if list_searched_xxx_id is not None and len(list_searched_xxx_id) > 0:
            if selected_category_music_str == '00':
                print('1')
                qs_xxx = Music_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
            else:
                print('2')
                qs_xxx = Music_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id) & Q(category=selected_category_music_str)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        else:
            if selected_category_music_str == '00':
                print('3')
                qs_xxx = Music_Album.objects.filter(Q(check_discard=False)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
            else:
                print('4')
                qs_xxx = Music_Album.objects.filter(Q(check_discard=False) & Q(category=selected_category_music_str)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        print('qs_xxx', len(qs_xxx))

        # Data Serialization            
        list_serialized_data_music_album = Music_Album_Serializer(qs_xxx, many=True).data
        
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_PICTURE': BASE_DIR_PICTURE,
            'BASE_DIR_MANGA': BASE_DIR_MANGA,
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'BASE_DIR_MUSIC': BASE_DIR_MUSIC,
            'LIST_MUSIC_CATEGORY': LIST_MUSIC_CATEGORY,
            'LIST_MUSIC_SORTING_FIELD': LIST_MUSIC_SORTING_FIELD,
            'list_serialized_data_music_album': list_serialized_data_music_album,
            'total_num_registered_item': total_num_registered_item,
            'total_num_searched_item': total_num_searched_item,
            'list_count_page_number': [count_page_number_min, count_page_number_max, count_page_number],
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)
   
    if request.method == 'POST':
        # print(request.POST)
        if request.POST.get('button') == 'sorting_items':
            selected_sorting_field_str = request.POST.get('sort_by')
            selected_field_music = q_mysettings_hansent.selected_field_music
            check_field_ascending_music = q_mysettings_hansent.check_field_ascending_music
            if selected_sorting_field_str == selected_field_music:
                if check_field_ascending_music == True:
                    check_field_ascending_music = False
                else:
                    check_field_ascending_music = True
            data = {
                'selected_field_music':selected_sorting_field_str,
                'check_field_ascending_music': check_field_ascending_music,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            print('Sorting 조건 확정 및 저장')
            return redirect('hans-ent-music-album-list')
        
        if request.POST.get('button') == 'category_filtering':
            selected_category_str = request.POST.get('selected_category')
            data = {
                'selected_category_music': selected_category_str,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            return redirect('hans-ent-music-album-list')
       
        if request.POST.get('button') == 'page_number_min':
            hans_ent_count_page_number_down(request, q_mysettings_hansent)
            return redirect('hans-ent-music-album-list')
        
        if request.POST.get('button') == 'page_number_max':
            total_num_registered_item = Music_Album.objects.count()
            hans_ent_count_page_number_up(request, q_mysettings_hansent, total_num_registered_item)
            return redirect('hans-ent-music-album-list')
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_music_album_list_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
    if request.method == 'GET':
        print(request.GET,)
        keyword_str = request.GET.get('keyword')
        qs_xxx = Music_Album.objects.filter(Q(check_discard=False) & (Q(title__icontains=keyword_str) | Q(main_actor__name__icontains=keyword_str) | Q(main_actor__synonyms__icontains=keyword_str)))
        list_searched_music_album_id = []
        if qs_xxx is not None and len(qs_xxx) > 0:
            for q_xxx in qs_xxx:
                list_searched_music_album_id.append(q_xxx.id)
        data = {
            'list_searched_music_album_id': list_searched_music_album_id,
        }
        MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
        return redirect('hans-ent-music-album-list')
   
    if request.method == 'POST':
        keyword_str = request.POST.get('button')
        if keyword_str == 'reset':
            reset_hans_ent_music_album_list(q_mysettings_hansent)
        return redirect('hans-ent-music-album-list')
   

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_music_album_gallery_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == 'GET':
        q_music_album_selected = q_mysettings_hansent.music_album_selected
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_music_album_gallery_modal_view POST ======================================================= 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        selected_serialized_data_mysettings = {}
        selected_serialized_data_actor = {}
        selected_serialized_data_music_album = {}
        
        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_music_album_id_str = request.POST.get('selected_music_album_id')
        selected_music_album_music_id_str = request.POST.get('selected_music_album_music_id')

        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        selected_music_album_id_str = None if selected_music_album_id_str in LIST_STR_NONE_SERIES else selected_music_album_id_str
        selected_music_album_music_id_str = None if selected_music_album_music_id_str in LIST_STR_NONE_SERIES else selected_music_album_music_id_str
        
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        print('selected actor ', q_actor)

        if selected_music_album_id_str is not None and selected_music_album_id_str != '':
            selected_music_album_id = int(selected_music_album_id_str)
            q_music_album = Music_Album.objects.get(id=selected_music_album_id)
        else:
            q_music_album = None
        print('q_music_album: ', q_music_album)

        # 이전 엘범 선택하기
        if request.POST.get('button') == 'select_previous_album':
            print('# 이전 엘범 선택하기')
            if q_music_album is not None:
                q_music_album_first = Music_Album.objects.filter(check_discard=False).first()
                current_album_id = q_music_album.id
                i = 1
                while current_album_id - i > q_music_album_first.id - 1:
                    subtracted_album_id = current_album_id - i
                    q_music_album_selected = Music_Album.objects.filter(Q(id=subtracted_album_id) & Q(check_discard=False)).last()
                    if q_music_album_selected is not None:
                        q_music_album = q_music_album_selected
                        break
        
        # 다음 엘범 선택하기
        if request.POST.get('button') == 'select_next_album':
            print('# 다음 엘범 선택하기')
            if q_music_album is not None:
                q_music_album_last = Music_Album.objects.filter(check_discard=False).last()
                current_album_id = q_music_album.id
                i = 1
                while current_album_id + i < q_music_album_last.id + 1:
                    added_album_id = current_album_id + i
                    q_music_album_selected = Music_Album.objects.filter(Q(id=added_album_id) & Q(check_discard=False)).last()
                    if q_music_album_selected is not None:
                        q_music_album = q_music_album_selected
                        break
        
        # 즐겨찾기 등록/해제
        if request.POST.get('button') == 'add_or_remove_favorite_song':
            print('# 즐겨찾기 등록/해제')
            if selected_music_album_music_id_str is not None and selected_music_album_music_id_str != '':
                selected_music_album_music_id = int(selected_music_album_music_id_str)
                if q_music_album_selected is not None:
                    list_dict_music_album = q_music_album_selected.list_dict_music_album
                    if len(list_dict_music_album) > 1:
                        for dict_music_album in list_dict_music_album:
                            if dict_music_album['id'] == selected_music_album_music_id and dict_music_album["id"] != 0:
                                if dict_music_album['favorite'] == 'false':
                                    dict_music_album['favorite'] = 'true'
                                else:
                                    dict_music_album['favorite'] = 'false'
                            data = {'list_dict_music_album': list_dict_music_album}
                            Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)

        # Audio Player 세팅 저장하기
        if request.POST.get('button') == 'save_audioplayer_settings':
            print('# Audio Player 세팅 저장하기')
            check_music_player_expand_str = request.POST.get('check_music_player_expand')
            check_audio_is_playing_now_str = request.POST.get('check_audio_is_playing_now')
            check_shuffle_play_activated_str = request.POST.get('check_shuffle_play_activated')
            check_loop_play_activated_str = request.POST.get('check_loop_play_activated')
            check_repeat_play_activated_str = request.POST.get('check_repeat_play_activated')
            check_favorite_play_activated_str = request.POST.get('check_favorite_play_activated')
            check_background_play_activated_str = request.POST.get('check_background_play_activated')

            check_music_player_expand = check_music_player_expand_str.lower() != 'false'
            check_audio_is_playing_now = check_audio_is_playing_now_str.lower() != 'false'
            check_shuffle_play_activated = check_shuffle_play_activated_str.lower() != 'false'
            check_loop_play_activated = check_loop_play_activated_str.lower() != 'false'
            check_repeat_play_activated = check_repeat_play_activated_str.lower() != 'false'
            check_favorite_play_activated = check_favorite_play_activated_str.lower() != 'false'
            check_background_play_activated = check_background_play_activated_str.lower() != 'false'
            
            # if check_music_player_expand_str == 'false':
            #     check_music_player_expand = False 
            # else:
            #     check_music_player_expand_str = True
        
            if q_mysettings_hansent is not None:
                data = {
                    'check_music_player_expand': check_music_player_expand,
                    'check_audio_is_playing_now': check_audio_is_playing_now,
                    'check_shuffle_play_activated': check_shuffle_play_activated,
                    'check_loop_play_activated': check_loop_play_activated,
                    'check_repeat_play_activated': check_repeat_play_activated,
                    'check_favorite_play_activated': check_favorite_play_activated,
                    'check_background_play_activated': check_background_play_activated,
                }
                MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
                q_mysettings_hansent.refresh_from_db()
        
        # Data Serialization
        if q_music_album is not None: 
            if q_actor is None:
                q_actor = q_music_album.main_actor
            selected_serialized_data_music_album = Music_Album_Serializer(q_music_album, many=False).data
        if q_actor is not None:
            print('q_actor', q_actor)
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data
        if q_mysettings_hansent is not None:
            selected_serialized_data_mysettings = Mysettings_Hans_Ent_Serializer(q_mysettings_hansent, many=False).data
        jsondata = {
            'selected_serialized_data_mysettings': selected_serialized_data_mysettings,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_music_album': selected_serialized_data_music_album,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_music_album_update_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    
    if request.method == "GET":
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'GET':
        selected_serialized_data_actor = {}
        selected_serialized_data_music_album = {}
        q_music_album_selected = q_mysettings_hansent.music_album_selected
        # Get selected_serialized_data
        if q_music_album_selected is not None:
            selected_serialized_data_music_album = Music_Album_Serializer(q_music_album_selected, many=False).data
            if q_music_album_selected.main_actor:
                selected_serialized_data_actor = Actor_Serializer(q_music_album_selected.main_actor, many=False).data
            else:
                q_actor = q_mysettings_hansent.actor_selected
                if q_actor is not None:
                    selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data
        # Jsondata
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_MUSIC': BASE_DIR_MUSIC,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_music_album': selected_serialized_data_music_album,
        }
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_music_album_update_modal_view POST ========================================================== 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        
        selected_serialized_data_music_album = {}
        selected_serialized_data_actor = {}
        
        selected_music_album_id_str = str(request.POST.get('selected_music_album_id'))
        selected_music_album_picture_id_str = str(request.POST.get('selected_music_album_picture_id'))
        selected_music_album_music_id_str = str(request.POST.get('selected_music_album_music_id'))
        selected_actor_id_str = request.POST.get('selected_actor_id')
        input_text_title_str = request.POST.get('input_text_title')
        input_text_name_str = request.POST.get('input_text_name')
        input_text_studio_str = request.POST.get('input_text_studio')
        input_date_released_str = request.POST.get('input_date_released')
        input_text_tag_str = request.POST.get('input_text_tag')
        selected_music_sub_type_str = request.POST.get('selected_music_sub_type')
        selected_filtering_category_id_str = request.POST.get('selected_filtering_category_id')

        selected_music_album_id_str = None if selected_music_album_id_str in LIST_STR_NONE_SERIES else selected_music_album_id_str
        selected_music_album_picture_id_str = None if selected_music_album_picture_id_str in LIST_STR_NONE_SERIES else selected_music_album_picture_id_str
        selected_music_album_music_id_str = None if selected_music_album_music_id_str in LIST_STR_NONE_SERIES else selected_music_album_music_id_str
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        input_text_title_str = None if input_text_title_str in LIST_STR_NONE_SERIES else input_text_title_str
        input_text_name_str = None if input_text_name_str in LIST_STR_NONE_SERIES else input_text_name_str
        input_text_studio_str = None if input_text_studio_str in LIST_STR_NONE_SERIES else input_text_studio_str
        input_date_released_str = None if input_date_released_str in LIST_STR_NONE_SERIES else input_date_released_str
        selected_music_sub_type_str = None if selected_music_sub_type_str in LIST_STR_NONE_SERIES else selected_music_sub_type_str
        selected_filtering_category_id_str = None if selected_filtering_category_id_str in LIST_STR_NONE_SERIES else selected_filtering_category_id_str

        folder_name_str = request.POST.get('folder_name')
        folder_name_str = None if folder_name_str in LIST_STR_NONE_SERIES else folder_name_str
        input_info_site_name_str = request.POST.get('input_info_site_name')
        input_info_site_url_str = request.POST.get('input_info_site_url')
        input_info_site_name_str = None if input_info_site_name_str in LIST_STR_NONE_SERIES else input_info_site_name_str
        input_info_site_url_str = None if input_info_site_url_str in LIST_STR_NONE_SERIES else input_info_site_url_str

        print('selected_actor_id_str', selected_actor_id_str)
        print('selected_music_album_id_str', selected_music_album_id_str)

        # 선택된 모델 정보 획득
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        
        # 선택된 앨범 정보 획득
        if selected_music_album_id_str is not None and selected_music_album_id_str != '' :
            selected_music_album_id = int(selected_music_album_id_str)
            q_music_album_selected = Music_Album.objects.get(id=selected_music_album_id)
            if q_music_album_selected is not None:
                if q_actor is None:
                    q_actor = q_music_album_selected.main_actor
        else:
            q_music_album_selected = None 
        
        # 뮤직 Album 쿼리 생성하기
        if request.POST.get('button') == 'create_or_update':
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
                if q_actor is not None:
                    if q_music_album_selected.main_actor is None:
                        data = {'main_actor':q_actor}
                        Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
                        q_music_album_selected.refresh_from_db()
        
        # 앨범 커버 이미지 변경하기
        if request.POST.get('button') == 'change_music_album_cover_image':
            print('# 앨범 커버 이미지 변경하기')
            if selected_music_album_picture_id_str is not None and selected_music_album_picture_id_str != '':
                selected_music_album_picture_id = int(selected_music_album_picture_id_str)
                if q_music_album_selected is not None:
                    list_dict_picture_album = q_music_album_selected.list_dict_picture_album
                    # acitve 모두 false 변경 및 선택된 이미지만 Active true로 변경
                    for dict_picture_album in list_dict_picture_album:
                        dict_picture_album['active'] = 'false'
                        if dict_picture_album['id'] == selected_music_album_picture_id:
                            dict_picture_album['active'] = 'true'
                    data = {'list_dict_picture_album': list_dict_picture_album}
                    Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
                    q_music_album_selected.refresh_from_db()
                    

        # 뮤직 앨범 커버 이미지 삭제하기(선택한 이미지만)
        if request.POST.get('button') == 'remove_music_album_cover_image':
            print('# 앨범 커버 이미지 삭제하기')
            if selected_music_album_picture_id_str is not None and selected_music_album_picture_id_str != '':
                selected_music_album_picture_id = int(selected_music_album_picture_id_str)
                if q_music_album_selected is not None:
                    delete_files_in_list_dict_xxx_album(q_music_album_selected, 'music', 'image', selected_music_album_picture_id)

        # 뮤직 앨범 오디오 삭제하기(선택한 오디오만)
        if request.POST.get('button') == 'remove_music_album_music':
            print('# 앨범 오디오 삭제하기')
            if selected_music_album_music_id_str is not None and selected_music_album_music_id_str != '':
                selected_music_album_music_id = int(selected_music_album_music_id_str)
                if q_music_album_selected is not None:
                    delete_files_in_list_dict_xxx_album(q_music_album_selected, 'music', 'audio', selected_music_album_music_id)

        # 뮤직 앨범 통으로 삭제하기
        if request.POST.get('button') == 'remove_music_album':
            print('# 앨범 통으로 삭제하기', q_music_album_selected)
            if q_music_album_selected is not None:
                delete_files_in_list_dict_xxx_album(q_music_album_selected, 'music', 'all', 'all')  ## album 종류(actor, picture, video, music 중 택 1), 싱글 쿼리, 삭제종류('all' or int(id)) 
            return redirect('hans-ent-music-album-list')

        
        # 업로드 타이틀 정보 저장하기
        if input_text_title_str is not None and input_text_title_str != '':
            print('# 업로드 타이틀 정보 저장하기')
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            data = {
                'title': input_text_title_str,
            }
            Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
            q_music_album_selected.refresh_from_db()
            
        # 업로드 모델이름 저장하기
        if input_text_name_str is not None and input_text_name_str != '':
            print('# 업로드 모델이름 저장하기')
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            data = {
                'name': input_text_name_str,
            }
            Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
            q_music_album_selected.refresh_from_db()
        
        # 업로드 스튜디오 정보 저장하기
        if input_text_studio_str is not None and input_text_studio_str != '':
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            data = {
                'studio': input_text_studio_str,
            }
            Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
            q_music_album_selected.refresh_from_db()

        # 사진 앨범 타입 선택하기
        if selected_music_sub_type_str is not None and selected_music_sub_type_str != '':
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            data = {
                'types': selected_music_sub_type_str,
            }
            Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
            q_music_album_selected.refresh_from_db()
       
        # 업로드 출시일 정보 저장하기
        if input_date_released_str is not None and input_date_released_str != '':
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            date_string = str(input_date_released_str)
            date_format = '%Y-%m-%d'
            import datetime
            date_object = datetime.datetime.strptime(date_string, date_format).date()
            data = {
                'date_released': date_object,
            }
            Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
            q_music_album_selected.refresh_from_db()
        
        # 카테고리 저장하기
        if selected_filtering_category_id_str is not None and selected_filtering_category_id_str != '':
            print('# 카테고리 저장하기')
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            data = {
                'category': selected_filtering_category_id_str,
            }
            Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
            q_music_album_selected.refresh_from_db()

        # Website 등록
        if input_info_site_name_str is not None and input_info_site_name_str != '':
            print('# Website 등록')
            if input_info_site_url_str is not None and input_info_site_url_str != '':
                if q_music_album_selected is None:
                    q_music_album_selected = create_music_album()
                list_dict_info_url = q_music_album_selected.list_dict_info_url
                if list_dict_info_url is None:
                    list_dict_info_url = []
                if input_info_site_name_str not in list_dict_info_url:
                    list_dict_info_url.append({"name":input_info_site_name_str, "url":input_info_site_url_str})
                    data = {
                        'list_dict_info_url': list_dict_info_url,
                    }
                    Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
                    q_music_album_selected.refresh_from_db()

        # Tag 저장하기
        if input_text_tag_str is not None and input_text_tag_str != '':
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            tags = q_music_album_selected.tags
            if tags is None:
                tags = []
            if input_text_tag_str not in tags:
                print('tag save', input_text_tag_str)
                tags.append(input_text_tag_str)
            data = {
                'tags': tags,
            }
            Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
            q_music_album_selected.refresh_from_db()

        # Actor 선택하기
        if request.POST.get('button') == 'actor_select':
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            if q_music_album_selected is not None and q_actor is not None:
                print('선택된 Actor', q_actor)
                data = {
                    'main_actor': q_actor,
                }
                Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
                q_music_album_selected.refresh_from_db()

        # Actor 선택해제하기
        if request.POST.get('button') == 'actor_select_reset':
            print('# Actor 선택해제하기')
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            if q_music_album_selected is not None:
                data = {
                    'main_actor': None,
                }
                Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
                q_music_album_selected.refresh_from_db() 

        # 이미지 업로드 했으면 저장하기
        if request.FILES:
            if q_music_album_selected is not None:
                # 앨범 갤러이 이미지 저장하기
                files = request.FILES.getlist('files')
                files = None if files in LIST_STR_NONE_SERIES else files
                if files is not None and len(files) > 0:
                    # save_music_album_images(q_music_album_selected, files)
                    save_files_in_list_dict_xxx_album(q_music_album_selected, files, type_album='music')

        # Data Serialization
        if q_music_album_selected is not None:
            print('# 앨범이 등록되어 있다면', q_music_album_selected)
            print('q_actor', q_actor)
            if q_actor is None:
                q_actor = q_music_album_selected.main_actor
               
            # Settings에 선택된 Album 쿼리 등록
            print('세팅에 현재 앨범 등록하기', q_mysettings_hansent)
            data = {
                'music_album_selected': q_music_album_selected
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            q_mysettings_hansent.refresh_from_db()
            
            # main actor 등록
            if q_music_album_selected.main_actor is None:
                data = {"main_actor": q_actor}
                Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
                q_music_album_selected.refresh_from_db()

            # Data Serialize
            selected_serialized_data_music_album = Music_Album_Serializer(q_music_album_selected, many=False).data
            # dict_album_key_fullsize_value_thumbnail_image_path = get_dict_album_key_fullsize_value_thumbnail_image_path(q_music_album_selected)  # 앨범에 등록된 이미지 표시정보(Path) 획득하기
        
        if q_actor is not None:
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'LIST_MUSIC_CATEGORY': LIST_MUSIC_CATEGORY,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_music_album': selected_serialized_data_music_album,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)  



#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_music_album_update_modal_actor_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == "GET":
        print('*********************************************************************** get: ', request)
        keyword_str = request.GET.get('keyword')
        print('keyword_str', keyword_str)
        qs_xxx = Actor.objects.filter(Q(check_discard=False) & (Q(name__icontains=keyword_str) | Q(synonyms__icontains=keyword_str)))
        list_serialized_data_actor = []
        if qs_xxx is not None and len(qs_xxx) > 0:
            list_serialized_data_actor = Actor_Serializer(qs_xxx, many=True).data
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'list_serialized_data_actor': list_serialized_data_actor, 
        }
        # print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)

    if request.method == 'POST':
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)








#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Secret
#
#############################################################################################################################################
#############################################################################################################################################

@login_required
def secret(request):
    page_category = 'secret'
    check_authority = f_check_authority(request, page_category)
    if check_authority:
        template = 'secret.html'
    else:
        template = 'users/unauthorized.html'
    context={'key1': 'Good!'}
    return render(request, template, context)



#############################################################################################################################################
#############################################################################################################################################
#
#                                                       User
#
#############################################################################################################################################
#############################################################################################################################################



def register_user(request):
    if request.method == 'POST':
        form = user_register_form(request.POST)    
        if form.is_valid():
            form.save()
            q_user = User.objects.last() 
            data = {'user': q_user}
            Profile_User.objects.create(**data)
            Authorization.objects.create(**data)

            messages.success(request, f'Your account has been created! You are now able to log in!')
            return redirect('login')
    else:
        form = user_register_form()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_user(request):
    selected_user = request.user
    print(selected_user.profile_user.image.url)
    if request.method == 'POST':
        u_form = user_update_form(request.POST, instance=request.user)
        p_form = profile_update_form(request.POST, request.FILES, instance=request.user.profile_user)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
        return redirect('profile-user')
    else:
        u_form = user_update_form(instance=request.user)
        p_form = profile_update_form(instance=request.user.profile_user)
        context = {
            'u_form': u_form,
            'p_form': p_form
        }
    return render(request, 'users/profile.html', context)


@login_required
def logout_user(request):
    template = 'users/logout.html'
    context={'key1': 'Good!'}
    return render(request, template, context)



#############################################################################################################################################






























































































            # # -----------------------------------------------------------------------------------
            # # 파일 이름 변경을 통한 이미지 위치 변경
            # # -----------------------------------------------------------------------------------
            # print('select_image_order_next')
            # if dict_picture_album_id_str is not None and dict_picture_album_id_str != '':
            #     dict_picture_album_id = int(dict_picture_album_id_str)
            #     print('dict_picture_album_id', dict_picture_album_id)
            # else:
            #     dict_picture_album_id = None
            # if q_picture_album is not None and dict_picture_album_id is not None:
            #     list_dict_picture_album = q_picture_album.list_dict_picture_album
            #     if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
            #         if dict_picture_album_id < len(list_dict_picture_album):
            #             print(f'파일 위치 스위칭을 위한 이름 변경 절차 시작, dict_picture_album_id: {dict_picture_album_id}, len(dict_picture_album_id): {len(list_dict_picture_album)}')
            #             # 1. selected image -> temp 폴더로 파일 path 변경
            #             # 2. next image -> selected image로 파일 name 변경
            #             # 3. temp image -> next image로 파일 path, name 변경
            #             image_selected_original = None
            #             image_selected_cover = None
            #             image_selected_thumbnail = None
            #             image_next_original = None
            #             image_next_cover = None
            #             image_next_thumbnail = None

            #             path_selected_original = None
            #             path_selected_cover = None
            #             path_selected_thumbnail = None
            #             path_temp_original = None
            #             path_temp_cover = None
            #             path_temp_thumbnail = None
            #             path_next_original = None
            #             path_next_cover = None
            #             path_next_thumbnail = None
            #             TEMP_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE_TEMP)
            #             if not os.path.exists(TEMP_DIR):
            #                 print(f'no directory exist, create directory {TEMP_DIR}')
            #                 try:
            #                     os.makedirs(TEMP_DIR)
            #                 except:
            #                     print('failed making dir')
            #             # --------------------------------------------------------------------------------------------------------------------------------
            #             # Step 1: 선택한 이미지의 path 및 이동할 위치의 Temp 폴더 path 찾기기
            #             for dict_picture_album in list_dict_picture_album:
            #                 if dict_picture_album['id'] == dict_picture_album_id:
            #                     print(f'# Step 1: 선택한 이미지의 path 및 이동할 위치의 Temp 폴더 path 찾기기, 선택된 dict_picture_album_id: {dict_picture_album_id}')
            #                     image_selected_original = dict_picture_album['original']
            #                     image_selected_cover = dict_picture_album['cover']
            #                     image_selected_thumbnail = dict_picture_album['thumbnail']
            #                     if image_selected_original is not None:
            #                         path_selected_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_selected_original)
            #                         path_temp_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE_TEMP, image_selected_original)
            #                     else:
            #                         path_selected_original = None
            #                         path_temp_original = None
            #                     if image_selected_cover is not None:
            #                         path_selected_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_selected_cover)
            #                         path_temp_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE_TEMP, image_selected_cover)
            #                     else:
            #                         path_selected_cover = None
            #                         path_temp_cover = None
            #                     if image_selected_thumbnail is not None:
            #                         path_selected_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_selected_thumbnail)
            #                         path_temp_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE_TEMP, image_selected_thumbnail)
            #                     else:
            #                         path_selected_thumbnail = None
            #                         path_temp_thumbnail = None
            #             # 선택한 파일 이름을 임시저장 이름으로 변경(input, output)
            #             try:
            #                 if os.path.exists(path_selected_original):
            #                     os.rename(path_selected_original, path_temp_original)
            #                     os.remove(path_selected_original)
            #                     print(f'rename {path_selected_original} to {path_temp_original}')
            #                 else:
            #                     print('no original file on path exist')
            #             except:
            #                 pass
            #                 print(f'failed rename {path_selected_original}')
            #             try:
            #                 if os.path.exists(path_selected_cover):
            #                     os.rename(path_selected_cover, path_temp_cover)
            #                     os.remove(path_selected_cover)
            #                     print(f'rename {path_selected_cover} to {path_temp_cover}')
            #                 else:
            #                     print('no cover file on path exist')
            #             except:
            #                 pass
            #                 print(f'failed rename {path_selected_cover}')
            #             try:
            #                 if os.path.exists(path_selected_thumbnail):
            #                     os.rename(path_selected_thumbnail, path_temp_thumbnail)
            #                     os.remove(path_selected_thumbnail)
            #                     print(f'rename {path_selected_thumbnail} to {path_temp_thumbnail}')
            #                 else:
            #                     print('no thumbnail file on path exist')
            #             except:
            #                 pass
            #                 print(f'failed rename {path_selected_thumbnail}')
            #             # --------------------------------------------------------------------------------------------------------------------------------
            #             # Step 2 : Next 이미지를 선택한 이미지 위치로 변경하기(이름바꾸기를 통해해)
            #             for dict_picture_album in list_dict_picture_album:
            #                 if dict_picture_album['id'] == dict_picture_album_id + 1:
            #                     print(f'# Step 2 : Next 이미지를 선택한 이미지 위치로 변경하기(이름바꾸기를 통해해), 선택된 Next 이미지 ID: {dict_picture_album_id + 1}')
            #                     image_next_original = dict_picture_album['original']
            #                     image_next_cover = dict_picture_album['cover']
            #                     image_next_thumbnail = dict_picture_album['thumbnail']
            #                     print('image_selected_original', image_selected_original)
            #                     print('image_selected_cover', image_selected_cover)
            #                     print('image_selected_thumbnail', image_selected_thumbnail)
            #                     print('image_next_original', image_next_original)
            #                     print('image_next_cover', image_next_cover)
            #                     print('image_next_thumbnail', image_next_thumbnail)
            #                     if image_next_original is not None and image_selected_original is not None:
            #                         path_next_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_next_original)
            #                         path_selected_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_selected_original)
            #                     else:
            #                         path_next_original = None
            #                         path_selected_original = None
            #                     if image_next_cover is not None and image_selected_cover is not None:
            #                         path_next_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_next_cover)
            #                         path_selected_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_selected_cover)
            #                     else:
            #                         path_next_cover = None
            #                         path_selected_cover = None
            #                     if image_next_thumbnail is not None and image_selected_thumbnail is not None:
            #                         path_next_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_next_thumbnail)
            #                         path_selected_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_selected_thumbnail)
            #                     else:
            #                         path_next_thumbnail = None
            #                         path_selected_thumbnail = None
            #             # Next를 선택한 이미지 위치 이름으로 변경해서 위치이동시킴킴(input, output)
            #             try:
            #                 if os.path.exists(path_next_original):
            #                     os.rename(path_next_original, path_selected_original)
            #                     os.remove(path_next_original)
            #                     print(f'rename {path_next_original} to {path_selected_original}')
            #                 else:
            #                     print('no original file on path exist')
            #             except:
            #                 pass
            #                 print(f'failed rename {path_next_original}')
            #             try:
            #                 if os.path.exists(path_next_cover):
            #                     os.rename(path_next_cover, path_selected_cover)
            #                     os.remove(path_next_cover)
            #                     print(f'rename {path_next_cover} to {path_selected_cover}')
            #                 else:
            #                     print('no cover file on path exist')
            #             except:
            #                 pass
            #                 print(f'failed rename {path_next_cover}')
            #             try:
            #                 if os.path.exists(path_next_thumbnail):
            #                     os.rename(path_next_thumbnail, path_selected_thumbnail)
            #                     os.remove(path_next_thumbnail)
            #                     print(f'rename {path_next_thumbnail} to {path_selected_thumbnail}')
            #                 else:
            #                     print('no thumbnail file on path exist')
            #             except:
            #                 pass
            #                 print(f'failed rename {path_next_thumbnail}')
            #             # --------------------------------------------------------------------------------------------------------------------------------
            #             print('# Step 3 : Temp로 옮긴 선택 이미지를 Next 위치로 이름 변경시켜 위치 맞바꾸기 마무리')
            #             # 임시저장 파일을 Next 이름으로 변경(input, output)
            #             if path_temp_original is not None and path_next_original is not None:
            #                 try:
            #                     if os.path.exists(path_temp_original):
            #                         os.rename(path_temp_original, path_next_original)
            #                         os.remove(path_temp_original)
            #                         print(f'rename {path_temp_original} to {path_next_original}')
            #                 except:
            #                     pass
            #                     # print(f'failed rename {path_temp_original}')
            #             if path_temp_cover is not None and path_next_cover is not None:
            #                 try:
            #                     if os.path.exists(path_temp_cover):
            #                         os.rename(path_temp_cover, path_next_cover)
            #                         os.remove(path_temp_cover)
            #                         print(f'rename {path_temp_cover} to {path_next_cover}')
            #                 except:
            #                     pass
            #                     # print(f'failed rename {path_temp_cover}')
            #             if path_temp_thumbnail is not None and path_next_thumbnail is not None:
            #                 try:
            #                     if os.path.exists(path_temp_thumbnail):
            #                         os.rename(path_temp_thumbnail, path_next_thumbnail)
            #                         os.remove(path_temp_thumbnail)
            #                         print(f'rename {path_temp_thumbnail} to {path_next_thumbnail}')
            #                 except:
            #                     pass
            #                     # print(f'failed rename {path_temp_thumbnail}')
                            
            #             print('----------------------------------------------------------------')
            #             print('path_selected_original', path_selected_original)
            #             print('path_selected_cover', path_selected_cover)
            #             print('path_selected_thumbnail', path_selected_thumbnail)
            #             print('path_temp_original', path_temp_original)
            #             print('path_temp_cover', path_temp_cover)
            #             print('path_temp_thumbnail', path_temp_thumbnail)
            #             print('path_next_original', path_next_original)
            #             print('path_next_cover', path_next_cover)
            #             print('path_next_thumbnail', path_next_thumbnail)

                            
                            
                
        