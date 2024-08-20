from django.shortcuts import render, redirect, reverse 
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User 

from datetime import time, timedelta, datetime 

from webui.forms import user_register_form, user_update_form, profile_update_form
from webui.models import *
from webui.serializers import *
from webui.functions import *
from hans_ent.models import *



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
    data = {'user':q_user}
    q_mysettings_hansent = MySettings_HansEnt.objects.filter(Q(check_discard=False) & Q(user=q_user)).last()
    if q_mysettings_hansent is None:
        MySettings_HansEnt.objects.create(**data)
    q_authorization = Authorization.objects.filter(Q(check_discard=False) & Q(user=q_user)).last()
    if q_authorization is None:
        Authorization.objects.create(**data)

def f_check_authority(request, page_category):
    create_user_settings(request)
    q_user = request.user 
    list_allowed = q_user.authorization.list_allowed
    if page_category in list_allowed:
        
        # create_default_settings(request)
        return True 
    else:
        return False


@login_required
def index(request):
    page_category = 'home'
    template = 'home.html'
    context={'key1': 'Good!'}
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

@login_required
def study(request):
    page_category = 'study'
    check_authority = f_check_authority(request, page_category)
    if check_authority:
        template = 'study.html'
    else:
        template = 'users/unauthorized.html'
    context={'key1': 'Good!'}
    return render(request, template, context)


#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Entertainment
#
#############################################################################################################################################
#############################################################################################################################################

@login_required
def entertainment(request):
    page_category = 'entertainment'
    check_authority = f_check_authority(request, page_category)
    if check_authority:
        template = 'entertainment.html'
    else:
        template = 'users/unauthorized.html'
    context={'key1': 'Good!'}
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
    page_category = 'hans_ent'
    check_authority = f_check_authority(request, page_category)
    if check_authority:
        template = 'hans_ent.html'
        q_user = request.user
        q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    else:
        q_mysettings_hansent = None
        template = 'users/unauthorized.html'
    context={
        'key1': 'Good!',
        'LIST_MENU_HANS_ENT': LIST_MENU_HANS_ENT,
        'q_mysettings_hansent': q_mysettings_hansent,
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
        return redirect('hans-ent')


#############################################################################################################################################
# Actor
#############################################################################################################################################

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_actor_list(request):
    import datetime
    ls_today = datetime.date.today()
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
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
        # Acending or Decending? 
        field_ascending_str = q_mysettings_hansent.check_field_ascending_actor
        if field_ascending_str == False:
            selected_field_sorting = f'-{selected_field_sorting_str}'
        else:
            selected_field_sorting = selected_field_sorting_str
        # 화면에 표시할 아이템 개수 지정
        count_page_number = q_mysettings_hansent.count_page_number_actor 
        count_page_number_min = (count_page_number - 1) * LIST_NUM_DISPLAY_IN_PAGE 
        count_page_number_max = count_page_number * LIST_NUM_DISPLAY_IN_PAGE
        # 쿼리 필터링
        if list_searched_xxx_id is not None and len(list_searched_xxx_id) > 0:
            qs_xxx = Actor.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        else:
            qs_xxx = Actor.objects.filter(Q(check_discard=False)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        # Data Serialization            
        list_serialized_data_actor = Actor_Serializer(qs_xxx, many=True).data
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'list_field_sorting': LIST_ACTOR_FIELD,
            'list_serialized_data_actor': list_serialized_data_actor,
            'total_num_registered_item': total_num_registered_item, 
            'total_num_searched_item': total_num_searched_item,
            'list_count_page_number': [count_page_number_min, count_page_number_max, count_page_number],
        }
        print('jsondata', jsondata)
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
        
        if request.POST.get('button') == 'page_number_min':
            count_page_number_down(request, q_mysettings_hansent)
            return redirect('hans-ent-actor-list')
        if request.POST.get('button') == 'page_number_max':
            count_page_number_up(request, q_mysettings_hansent, total_num_registered_item)
            return redirect('hans-ent-actor-list')
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_actor_list_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == 'GET':
        print(request.GET,)
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

    if request.method == "GET":
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)
    if request.method == "POST":
        """
        Actor 관련 정보 + Actor가 참여한 모든 앨범(Picture, Video, Music, Anything) 정보를 표시
        """
        print(request.POST,)
        selected_serialized_data_actor = {}
        list_serialized_data_picture_album = []
        list_serialized_data_video_album = []
        list_serialized_data_music_album = []
        
        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        print('selected actor: ', q_actor)

        selected_picture_album_id_str = request.POST.get('selected_picture_album_id')
        selected_picture_album_id_str = None if selected_picture_album_id_str in LIST_STR_NONE_SERIES else selected_picture_album_id_str
        if selected_picture_album_id_str is not None and selected_picture_album_id_str != '':
            selected_picture_album_id = int(selected_picture_album_id_str)
            q_picture_album = Picture_Album.objects.get(id=selected_picture_album_id)
            if q_picture_album is not None:
                q_actor = q_picture_album.main_actor
        else:
            q_picture_album = None
        print('q_picture_album: ', q_picture_album)
        
        selected_video_album_id_str = request.POST.get('selected_video_album_id')
        selected_video_album_id_str = None if selected_video_album_id_str in LIST_STR_NONE_SERIES else selected_video_album_id_str
        if selected_video_album_id_str is not None and selected_video_album_id_str != '':
            selected_video_album_id = int(selected_video_album_id_str)
            q_video_album = Video_Album.objects.get(id=selected_video_album_id)
            if q_video_album is not None:
                q_actor = q_video_album.main_actor
        else:
            q_video_album = None
        print('q_video_album: ', q_video_album)

        # 보내야 하는 정보 수집하기 ###############################################################
        if q_actor is not None:
            print('보내는 Data 수집')
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data
            qs_video_album = Video_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_actor))
            qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False) & Q(main_actor=q_actor))
            if qs_picture_album is not None and len(qs_picture_album) > 0:
                list_serialized_data_picture_album = Picture_Album_Serializer(qs_picture_album, many=True).data
            # if qs_video_album is not None and len(qs_video_album) > 0:
            #     list_serialized_data_video_album = Video_Album_Detail_Serializer(qs_video_album, many=True).data
            
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_PICTURE': BASE_DIR_PICTURE,
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'BASE_DIR_MUSIC': BASE_DIR_MUSIC,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'list_serialized_data_picture_album': list_serialized_data_picture_album,
            'list_serialized_data_video_album': list_serialized_data_video_album,
            'list_serialized_data_music_album': list_serialized_data_music_album,
        }
        print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_actor_upload_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    
    if request.method == "GET":
        jsondata = {}   
        return JsonResponse(jsondata, safe=False)
    if request.method == "POST":
        print(request.POST,)
        selected_serialized_data_actor = {}
        # Request 정보 획득
        selected_actor_id_str = request.POST.get('selected_actor_id') # 기 선택되어 있는 배우, Merge시 사라지는 모델
        sacrificial_actor_id_str = request.POST.get('sacrificial_actor_id') # 새로 선택한 배우, Merge 하고 나서 살아남는 모델
        selected_profile_album_picture_id_str = request.POST.get('selected_profile_album_picture_id')
        input_text_name_str = request.POST.get('input_text_name')
        input_text_synonyms_str = request.POST.get('input_text_synonyms')
        input_date_birthday_str = request.POST.get('input_date_birthday')
        input_text_height_str = request.POST.get('input_text_height')
        input_info_site_name_str = request.POST.get('input_info_site_name')
        input_info_site_url_str = request.POST.get('input_info_site_url')
        input_text_tag_str = request.POST.get('input_text_tag')
        
        # Request 정보 필터링 String화
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        sacrificial_actor_id_str = None if sacrificial_actor_id_str in LIST_STR_NONE_SERIES else sacrificial_actor_id_str
        selected_profile_album_picture_id_str = None if selected_profile_album_picture_id_str in LIST_STR_NONE_SERIES else selected_profile_album_picture_id_str
        input_text_name_str = None if input_text_name_str in LIST_STR_NONE_SERIES else input_text_name_str
        input_text_synonyms_str = None if input_text_synonyms_str in LIST_STR_NONE_SERIES else input_text_synonyms_str
        input_date_birthday_str = None if input_date_birthday_str in LIST_STR_NONE_SERIES else input_date_birthday_str
        input_text_height_str = None if input_text_height_str in LIST_STR_NONE_SERIES else input_text_height_str
        input_info_site_name_str = None if input_info_site_name_str in LIST_STR_NONE_SERIES else input_info_site_name_str
        input_info_site_url_str = None if input_info_site_url_str in LIST_STR_NONE_SERIES else input_info_site_url_str
        input_text_tag_str = None if input_text_tag_str in LIST_STR_NONE_SERIES else input_text_tag_str
        
        # 선택된 배우 쿼리 찾기
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None 
        
        print('q_actor', q_actor)

        # 앨범 커버 이미지 변경하기
        if request.POST.get('button') == 'change_profile_album_cover_image':
            if selected_profile_album_picture_id_str is not None and selected_profile_album_picture_id_str != '':
                selected_profile_album_picture_id = int(selected_profile_album_picture_id_str)
                if q_actor is not None:
                    list_dict_profile_album = q_actor.list_dict_profile_album
                    # acitve 모두 false 변경
                    for dict_profile_album in list_dict_profile_album:
                        dict_profile_album['active'] = 'false'
                        if dict_profile_album['id'] == selected_profile_album_picture_id:
                            dict_profile_album['active'] = 'true'
                    data = {'list_dict_profile_album': list_dict_profile_album}
                    Actor.objects.filter(id=q_actor.id).update(**data)
                    q_actor.refresh_from_db()
        
        # 앨범 이미지 삭제하기
        if request.POST.get('button') == 'remove_profile_album_picture':
            print('# 앨범 이미지 삭제하기')
            if selected_profile_album_picture_id_str is not None and selected_profile_album_picture_id_str != '':
                selected_profile_album_picture_id = int(selected_profile_album_picture_id_str)
                if q_actor is not None:
                    list_dict_profile_album = q_actor.list_dict_profile_album
                    # 이미지 삭제 프로세스
                    check_discard_active_picture = False
                    for dict_profile_album in list_dict_profile_album:
                        if dict_profile_album["id"] == selected_profile_album_picture_id:
                            # 커버이미지를 삭제하는 경우이면 Default를 커버로 지정하기 위해 플래그 올린다.
                            if dict_profile_album["active"] == 'true':
                                check_discard_active_picture = True
                            # 서버어서 이미지 삭제하기
                            if dict_profile_album["id"] != 0:
                                # Default 이미지가 아닌 경우 삭제가능
                                image_name_original = dict_profile_album["original"]
                                image_name_cover = dict_profile_album["cover"]
                                image_name_thumbnail = dict_profile_album["thumbnail"]
                                file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_original)
                                file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_cover)
                                file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_thumbnail)
                                print('file_path_o', file_path_o)
                                if os.path.exists(file_path_o):
                                    try:
                                        os.remove(file_path_o)
                                    except:
                                        pass
                                if os.path.exists(file_path_c):
                                    try:
                                        os.remove(file_path_c)
                                    except:
                                        pass
                                if os.path.exists(file_path_t):
                                    try:
                                        os.remove(file_path_t)
                                    except:
                                        pass
                                # 리스트에서 discard 처리하기
                                dict_profile_album['active'] = 'false'
                                dict_profile_album['discard'] = 'true'
                    # Active true(커버이미지)를 삭제한 경우 Default이미지를 커버로 다시 등장시킨다.
                    if check_discard_active_picture == True:
                        for dict_profile_album in list_dict_profile_album:
                            if dict_profile_album["id"] == 0:
                                dict_profile_album["active"] = 'true'
                                dict_profile_album["discard"] = 'false'
                    # Query 저장 프로세스
                    data = {'list_dict_profile_album': list_dict_profile_album}
                    Actor.objects.filter(id=q_actor.id).update(**data)
                    q_actor.refresh_from_db() 

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
            if q_actor is None:
                q_actor = create_actor()
            data = {
                'name': input_text_name_str,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()

        # Actor 동의어 저장하기
        if input_text_synonyms_str is not None and input_text_synonyms_str != '':
            if q_actor is None:
                q_actor = create_actor()
            synonyms = q_actor.synonyms
            if synonyms is None:
                synonyms = []
            if input_text_synonyms_str not in synonyms:
                synonyms.append(input_text_synonyms_str)
            data = {
                'synonyms': synonyms,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()
        
        # 생일 정보 저장하기
        if input_date_birthday_str is not None and input_date_birthday_str != '':
            if q_actor is None:
                q_actor = create_actor()
            date_string = str(input_date_birthday_str)
            date_format = '%Y-%m-%d'
            date_object = datetime.strptime(date_string, date_format).date()
            data = {
                'date_birth': date_object,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()
        
        # 키 저장하기
        if input_text_height_str is not None and input_text_height_str != '':
            if q_actor is None:
                q_actor = create_actor()
            input_text_height_int = int(input_text_height_str)
            data = {
                'height': input_text_height_int,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()
        
        # Website 등록
        if input_info_site_name_str is not None and input_info_site_name_str != '':
            if input_info_site_url_str is not None and input_info_site_url_str != '':
                if q_actor is None:
                    q_actor = create_actor()
                list_dict_info_url = q_actor.list_dict_info_url
                if list_dict_info_url is None:
                    list_dict_info_url = []
                if input_info_site_name_str not in list_dict_info_url:
                    list_dict_info_url.append({"name":input_info_site_name_str, "url":input_info_site_url_str})
                    data = {
                        'list_dict_info_url': list_dict_info_url,
                    }
                    Actor.objects.filter(id=q_actor.id).update(**data)
                    q_actor.refresh_from_db()
        
        # Tag 저장하기
        if input_text_tag_str is not None and input_text_tag_str != '':
            if q_actor is None:
                q_actor = create_actor()
            tags = q_actor.tags
            if tags is None:
                tags = []
            if input_text_tag_str not in tags:
                print('tag save', input_text_tag_str)
                tags.append(input_text_tag_str)
            data = {
                'tags': tags,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()

        # Actor Profile 이미지 업로드 저장하기
        if request.FILES:
            if q_actor is None:
                q_actor = create_actor()
            # 앨범 갤러이 이미지 저장하기
            images = request.FILES.getlist('images')
            if images is not None and len(images) > 0:
                save_actor_profile_images(q_actor, images)

        # 선택 모델 삭제하기
        if request.POST.get('button') == 'actor_delete':
            if q_actor is None:
                q_actor = create_actor()
            data = {'check_discard':True}
            Actor.objects.filter(id=q_actor.id).update(**data)
            data = {
                'actor_selected': None,
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            q_mysettings_hansent.refresh_from_db() 
            q_actor = None
            return redirect('hans-ent-actor-list')

        # Data Serialize 하기
        if q_actor is not None:
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'selected_serialized_data_actor': selected_serialized_data_actor,
        }
        print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)


#############################################################################################################################################
# Picture Album  
#############################################################################################################################################

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_picture_album_list(request):
    import datetime
    ls_today = datetime.date.today()
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
    if request.method == 'GET':
        total_num_registered_item = Picture_Album.objects.count()
        # Searching 결과값 찾기
        list_searched_xxx_id = q_mysettings_hansent.list_searched_picture_album_id
        if list_searched_xxx_id is not None:
            total_num_searched_item = len(list_searched_xxx_id)
        else:
            total_num_searched_item = 0
        # Sorting Submenu 조건
        selected_field_sorting_str = q_mysettings_hansent.selected_field_picture
        # Acending or Decending?
        field_ascending_str = q_mysettings_hansent.check_field_ascending_picture
        if field_ascending_str == False:
            selected_field_sorting = f'-{selected_field_sorting_str}'
        else:
            selected_field_sorting = selected_field_sorting_str
        # 화면에 표시할 아이템 개수 지정
        count_page_number = q_mysettings_hansent.count_page_number_picture
        count_page_number_min = (count_page_number - 1) * LIST_NUM_DISPLAY_IN_PAGE
        count_page_number_max = count_page_number * LIST_NUM_DISPLAY_IN_PAGE
        # 쿼리 필터링
        if list_searched_xxx_id is not None and len(list_searched_xxx_id) > 0:
            qs_xxx = Picture_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        else:
            qs_xxx = Picture_Album.objects.filter(Q(check_discard=False)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        print('qs_xxx', qs_xxx)
        # Data Serialization            
        list_serialized_data_picture_album = Picture_Album_Serializer(qs_xxx, many=True).data
        
        jsondata = {
            'BASE_DIR_PICTURE': BASE_DIR_PICTURE,
            'list_field_sorting': LIST_PICTURE_FIELD,
            'list_serialized_data_picture_album': list_serialized_data_picture_album,
            'total_num_registered_item': total_num_registered_item,
            'total_num_searched_item': total_num_searched_item,
            'list_count_page_number': [count_page_number_min, count_page_number_max, count_page_number],
        }
        print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)
   
    if request.method == 'POST':
        # print(request.POST)
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
            return redirect('hans-ent-actor-list')
       
        if request.POST.get('button') == 'page_number_min':
            count_page_number_down(request, q_mysettings_hansent)
            return redirect('hans-ent-actor-list')
        if request.POST.get('button') == 'page_number_max':
            count_page_number_up(request, q_mysettings_hansent, total_num_registered_item)
            return redirect('hans-ent-actor-list')
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_picture_album_list_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
    if request.method == 'GET':
        print(request.GET,)
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
        return redirect('hans-ent-actor-list')
   
    if request.method == 'POST':
        keyword_str = request.POST.get('button')
        if keyword_str == 'reset':
            reset_hans_ent_picture_album_list(q_mysettings_hansent)
        return redirect('hans-ent-picture-album-list')
   

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_picture_album_gallery_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)

    if request.method == 'GET':
        q_picture_album_selected = q_mysettings_hansent.picture_album_selected
        jsondata = {}
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_picture_album_gallery_modal_view POST ======================================================= 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        selected_serialized_data_actor = {}
        selected_serialized_data_picture_album = {}
        dict_album_key_fullsize_value_thumbnail_image_path = {}
        list_album_thumbnail_url = []

        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_picture_album_id_str = request.POST.get('selected_picture_album_id')

        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        selected_picture_album_id_str = None if selected_picture_album_id_str in LIST_STR_NONE_SERIES else selected_picture_album_id_str
        
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        print('selected actor ', q_actor)

        if selected_picture_album_id_str is not None and selected_picture_album_id_str != '':
            selected_picture_album_id = int(selected_picture_album_id_str)
            q_picture_album = Picture_Album.objects.get(id=selected_picture_album_id)
        else:
            q_picture_album = None
        print('q_picture_album: ', q_picture_album)
        
        # Data Serialization
        if q_picture_album is not None: 
            if q_actor is None:
                q_actor = q_picture_album.main_actor
            selected_serialized_data_picture_album = Picture_Album_Serializer(q_picture_album, many=False).data
        if q_actor is not None:
            print('q_actor', q_actor)
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'BASE_DIR_PICTURE': BASE_DIR_PICTURE,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_picture_album': selected_serialized_data_picture_album,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_picture_album_upload_modal(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    
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
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_PICTURE': BASE_DIR_PICTURE,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_picture_album': selected_serialized_data_picture_album,
        }
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_picture_album_upload_modal_view POST ========================================================== 1')
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
        
        selected_picture_album_id_str = None if selected_picture_album_id_str in LIST_STR_NONE_SERIES else selected_picture_album_id_str
        selected_picture_album_picture_id_str = None if selected_picture_album_picture_id_str in LIST_STR_NONE_SERIES else selected_picture_album_picture_id_str
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        input_text_title_str = None if input_text_title_str in LIST_STR_NONE_SERIES else input_text_title_str
        input_text_name_str = None if input_text_name_str in LIST_STR_NONE_SERIES else input_text_name_str
        input_text_studio_str = None if input_text_studio_str in LIST_STR_NONE_SERIES else input_text_studio_str
        input_date_released_str = None if input_date_released_str in LIST_STR_NONE_SERIES else input_date_released_str
        selected_picture_sub_type_str = None if selected_picture_sub_type_str in LIST_STR_NONE_SERIES else selected_picture_sub_type_str
        
        print('selected_actor_id_str', selected_actor_id_str)
        print('selected_picture_album_id_str', selected_picture_album_id_str)

        # 선택된 모델 정보 획득
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None
        
        # 선택된 앨범 정보 획득
        if selected_picture_album_id_str is not None and selected_picture_album_id_str != '' :
            selected_picture_album_id = int(selected_picture_album_id_str)
            q_picture_album_selected = Picture_Album.objects.get(id=selected_picture_album_id)
            if q_picture_album_selected is not None:
                if q_actor is None:
                    q_actor = q_picture_album_selected.main_actor
        else:
            q_picture_album_selected = None 
        
        # 앨범 통으로 삭제하기
        if request.POST.get('button') == 'picture_album_delete':
            print('# 앨범 통으로 삭제하기', q_picture_album_selected)
            if q_picture_album_selected is not None:
                list_dict_picture_album = q_picture_album_selected.list_dict_picture_album
                if list_dict_picture_album is not None and len(list_dict_picture_album) > 1:
                    # 앨범에 등록된 Picture 삭제하기
                    for dict_picture_album in list_dict_picture_album:
                        # 서버어서 이미지 삭제하기
                        if dict_picture_album["id"] != 0:
                            # Default 이미지가 아닌 경우 삭제가능
                            image_name_original = dict_picture_album["original"]
                            image_name_cover = dict_picture_album["cover"]
                            image_name_thumbnail = dict_picture_album["thumbnail"]
                            file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_original)
                            file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
                            file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)
                            print('file_path_o', file_path_o)
                            if os.path.exists(file_path_o):
                                try:
                                    os.remove(file_path_o)
                                except:
                                    pass
                            if os.path.exists(file_path_c):
                                try:
                                    os.remove(file_path_c)
                                except:
                                    pass
                            if os.path.exists(file_path_t):
                                try:
                                    os.remove(file_path_t)
                                except:
                                    pass
                            # 리스트에서 discard 처리하기
                            dict_picture_album['active'] = 'false'
                            dict_picture_album['discard'] = 'true'
                # Query 저장 프로세스
                data = {
                    'list_dict_picture_album': list_dict_picture_album,
                    'check_discard': True,
                    }
                Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                q_picture_album_selected.refresh_from_db()
                    
            return redirect('hans-ent-picture-album-list')

        # 앨범 커버 이미지 변경하기
        if request.POST.get('button') == 'change_picture_album_cover_image':
            if selected_picture_album_picture_id_str is not None and selected_picture_album_picture_id_str != '':
                selected_picture_album_picture_id = int(selected_picture_album_picture_id_str)
                if q_picture_album_selected is not None:
                    list_dict_picture_album = q_picture_album_selected.list_dict_picture_album
                    # acitve 모두 false 변경
                    for dict_picture_album in list_dict_picture_album:
                        dict_picture_album['active'] = 'false'
                        if dict_picture_album['id'] == selected_picture_album_picture_id:
                            dict_picture_album['active'] = 'true'
                    data = {'list_dict_picture_album': list_dict_picture_album}
                    Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
                    q_picture_album_selected.refresh_from_db()
        
        # 앨범 이미지 삭제하기
        if request.POST.get('button') == 'remove_picture_album_picture':
            print('# 앨범 이미지 삭제하기')
            if selected_picture_album_picture_id_str is not None and selected_picture_album_picture_id_str != '':
                selected_picture_album_picture_id = int(selected_picture_album_picture_id_str)
                if q_picture_album_selected is not None:
                    list_dict_picture_album = q_picture_album_selected.list_dict_picture_album
                    # 이미지 삭제 프로세스
                    check_discard_active_picture = False
                    for dict_picture_album in list_dict_picture_album:
                        if dict_picture_album["id"] == selected_picture_album_picture_id:
                            # 커버이미지를 삭제하는 경우이면 Default를 커버로 지정하기 위해 플래그 올린다.
                            if dict_picture_album["active"] == 'true':
                                check_discard_active_picture = True
                            # 서버어서 이미지 삭제하기
                            if dict_picture_album["id"] != 0:
                                # Default 이미지가 아닌 경우 삭제가능
                                image_name_original = dict_picture_album["original"]
                                image_name_cover = dict_picture_album["cover"]
                                image_name_thumbnail = dict_picture_album["thumbnail"]
                                file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_original)
                                file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
                                file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)
                                print('file_path_o', file_path_o)
                                if os.path.exists(file_path_o):
                                    try:
                                        os.remove(file_path_o)
                                    except:
                                        pass
                                if os.path.exists(file_path_c):
                                    try:
                                        os.remove(file_path_c)
                                    except:
                                        pass
                                if os.path.exists(file_path_t):
                                    try:
                                        os.remove(file_path_t)
                                    except:
                                        pass
                                # 리스트에서 discard 처리하기
                                dict_picture_album['active'] = 'false'
                                dict_picture_album['discard'] = 'true'
                    # Active true(커버이미지)를 삭제한 경우 Default이미지를 커버로 다시 등장시킨다.
                    if check_discard_active_picture == True:
                        for dict_picture_album in list_dict_picture_album:
                            if dict_picture_album["id"] == 0:
                                dict_picture_album["active"] = 'true'
                                dict_picture_album["discard"] = 'false'
                    # Query 저장 프로세스
                    data = {'list_dict_picture_album': list_dict_picture_album}
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
            date_object = datetime.strptime(date_string, date_format).date()
            data = {
                'date_released': date_object,
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
            if q_picture_album_selected is None:
                q_picture_album_selected = create_picture_album()
            # 앨범 갤러이 이미지 저장하기
            images = request.FILES.getlist('images')
            if images is not None and len(images) > 0:
                save_picture_album_images(q_picture_album_selected, images)

        # 신규 Picture Album 생성
        if request.POST.get('button') == 'create_picture_album':
            q_actor = None 
            q_picture_album_selected = None
            print('good luck~!')
            pass

        # Data Serialization
        if q_picture_album_selected is not None:
            print('# 앨범이 등록되어 있다면', q_picture_album_selected)
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
        
            # Data Serialize
            selected_serialized_data_picture_album = Picture_Album_Serializer(q_picture_album_selected, many=False).data
            # dict_album_key_fullsize_value_thumbnail_image_path = get_dict_album_key_fullsize_value_thumbnail_image_path(q_picture_album_selected)  # 앨범에 등록된 이미지 표시정보(Path) 획득하기
        
        if q_actor is not None:
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_PICTURE': BASE_DIR_PICTURE,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_picture_album': selected_serialized_data_picture_album,
        }
        print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)  


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_picture_album_upload_modal_actor_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    
    if request.method == 'GET':
        print('get', request)
        keyword_str = request.GET.get('keyword')
        qs_xxx = Actor.objects.filter(Q(check_discard=False) & (Q(name__icontains=keyword_str) | Q(synonyms__icontains=keyword_str)))
        list_serialized_data_actor = None
        if qs_xxx is not None and len(qs_xxx) > 0:
            list_serialized_data_actor = Actor_Serializer(qs_xxx, many=True).data
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'list_serialized_data_actor': list_serialized_data_actor, 
        }
        return JsonResponse(jsondata, safe=False)

    if request.method == 'POST':
        print('********************', request.POST)
        jsondata = {}
        return JsonResponse(jsondata, safe=False)



#############################################################################################################################################
# Video Album  
#############################################################################################################################################

#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_video_album_list(request):
    import datetime
    ls_today = datetime.date.today()
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
   
    if request.method == 'GET':
        total_num_registered_item = Video_Album.objects.count()
        # Searching 결과값 찾기
        list_searched_xxx_id = q_mysettings_hansent.list_searched_video_album_id
        if list_searched_xxx_id is not None:
            total_num_searched_item = len(list_searched_xxx_id)
        else:
            total_num_searched_item = 0
        # Sorting Submenu 조건
        selected_field_sorting_str = q_mysettings_hansent.selected_field_video
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
            qs_xxx = Video_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        else:
            qs_xxx = Video_Album.objects.filter(Q(check_discard=False)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        print('qs_xxx', qs_xxx)
        # Data Serialization            
        list_serialized_data_video_album = Video_Album_Serializer(qs_xxx, many=True).data
        
        jsondata = {
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'list_field_sorting': LIST_VIDEO_FIELD,
            'list_serialized_data_video_album': list_serialized_data_video_album,
            'total_num_registered_item': total_num_registered_item,
            'total_num_searched_item': total_num_searched_item,
            'list_count_page_number': [count_page_number_min, count_page_number_max, count_page_number],
        }
        print('jsondata', jsondata)
        return JsonResponse(jsondata, safe=False)
   
    if request.method == 'POST':
        # print(request.POST)
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
            return redirect('hans-ent-actor-list')
       
        if request.POST.get('button') == 'page_number_min':
            count_page_number_down(request, q_mysettings_hansent)
            return redirect('hans-ent-actor-list')
        if request.POST.get('button') == 'page_number_max':
            count_page_number_up(request, q_mysettings_hansent, total_num_registered_item)
            return redirect('hans-ent-actor-list')
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
        dict_album_key_fullsize_value_thumbnail_image_path = {}
        list_album_thumbnail_url = []

        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_video_album_id_str = request.POST.get('selected_video_album_id')

        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        selected_video_album_id_str = None if selected_video_album_id_str in LIST_STR_NONE_SERIES else selected_video_album_id_str
        
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

        jsondata = {
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_video_album': selected_serialized_data_video_album,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_video_album_upload_modal(request):
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
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_video_album': selected_serialized_data_video_album,
        }
        return JsonResponse(jsondata, safe=False)
    
    if request.method == 'POST':
        print('streaming_video_album_upload_modal_view POST ========================================================== 1')
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
        selected_video_sub_type_str = request.POST.get('selected_video_sub_type')
        
        selected_video_album_id_str = None if selected_video_album_id_str in LIST_STR_NONE_SERIES else selected_video_album_id_str
        selected_video_album_picture_id_str = None if selected_video_album_picture_id_str in LIST_STR_NONE_SERIES else selected_video_album_picture_id_str
        selected_video_album_video_id_str = None if selected_video_album_video_id_str in LIST_STR_NONE_SERIES else selected_video_album_video_id_str
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        input_text_title_str = None if input_text_title_str in LIST_STR_NONE_SERIES else input_text_title_str
        input_text_name_str = None if input_text_name_str in LIST_STR_NONE_SERIES else input_text_name_str
        input_text_studio_str = None if input_text_studio_str in LIST_STR_NONE_SERIES else input_text_studio_str
        input_date_released_str = None if input_date_released_str in LIST_STR_NONE_SERIES else input_date_released_str
        selected_video_sub_type_str = None if selected_video_sub_type_str in LIST_STR_NONE_SERIES else selected_video_sub_type_str
        
        print('selected_actor_id_str', selected_actor_id_str)
        print('selected_video_album_id_str', selected_video_album_id_str)

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
        
        # 앨범 통으로 삭제하기
        if request.POST.get('button') == 'video_album_delete':
            print('# 앨범 통으로 삭제하기', q_video_album_selected)
            if q_video_album_selected is not None:
                list_dict_video_album = q_video_album_selected.list_dict_video_album
                if list_dict_video_album is not None and len(list_dict_video_album) > 1:
                    # 앨범에 등록된 Video 삭제하기
                    for dict_video_album in list_dict_video_album:
                        # 서버어서 이미지 삭제하기
                        if dict_video_album["id"] != 0:
                            # Default 이미지가 아닌 경우 삭제가능
                            image_name_original = dict_video_album["original"]
                            image_name_cover = dict_video_album["cover"]
                            image_name_thumbnail = dict_video_album["thumbnail"]
                            file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_original)
                            file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_cover)
                            file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_thumbnail)
                            print('file_path_o', file_path_o)
                            if os.path.exists(file_path_o):
                                try:
                                    os.remove(file_path_o)
                                except:
                                    pass
                            if os.path.exists(file_path_c):
                                try:
                                    os.remove(file_path_c)
                                except:
                                    pass
                            if os.path.exists(file_path_t):
                                try:
                                    os.remove(file_path_t)
                                except:
                                    pass
                            # 리스트에서 discard 처리하기
                            dict_video_album['active'] = 'false'
                            dict_video_album['discard'] = 'true'
                # Query 저장 프로세스
                data = {
                    'list_dict_video_album': list_dict_video_album,
                    'check_discard': True,
                    }
                Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                q_video_album_selected.refresh_from_db()
                    
            return redirect('hans-ent-video-album-list')

        # 앨범 커버 이미지 변경하기
        if request.POST.get('button') == 'change_video_album_cover_image':
            if selected_video_album_picture_id_str is not None and selected_video_album_picture_id_str != '':
                selected_video_album_picture_id = int(selected_video_album_picture_id_str)
                if q_video_album_selected is not None:
                    list_dict_picture_album = q_video_album_selected.list_dict_picture_album
                    # acitve 모두 false 변경
                    for dict_picture_album in list_dict_picture_album:
                        dict_picture_album['active'] = 'false'
                        if dict_picture_album['id'] == selected_video_album_picture_id:
                            dict_picture_album['active'] = 'true'
                    data = {'list_dict_picture_album': list_dict_picture_album}
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                    q_video_album_selected.refresh_from_db()
        
        # 앨범 이미지 삭제하기
        if request.POST.get('button') == 'remove_video_album_video':
            print('# 앨범 이미지 삭제하기')
            if selected_video_album_video_id_str is not None and selected_video_album_video_id_str != '':
                selected_video_album_video_id = int(selected_video_album_video_id_str)
                if q_video_album_selected is not None:
                    list_dict_video_album = q_video_album_selected.list_dict_video_album
                    # 이미지 삭제 프로세스
                    check_discard_active_video = False
                    for dict_video_album in list_dict_video_album:
                        if dict_video_album["id"] == selected_video_album_video_id:
                            # 커버이미지를 삭제하는 경우이면 Default를 커버로 지정하기 위해 플래그 올린다.
                            if dict_video_album["active"] == 'true':
                                check_discard_active_video = True
                            # 서버어서 이미지 삭제하기
                            if dict_video_album["id"] != 0:
                                # Default 이미지가 아닌 경우 삭제가능
                                image_name_original = dict_video_album["original"]
                                image_name_cover = dict_video_album["cover"]
                                image_name_thumbnail = dict_video_album["thumbnail"]
                                file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_original)
                                file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_cover)
                                file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_thumbnail)
                                print('file_path_o', file_path_o)
                                if os.path.exists(file_path_o):
                                    try:
                                        os.remove(file_path_o)
                                    except:
                                        pass
                                if os.path.exists(file_path_c):
                                    try:
                                        os.remove(file_path_c)
                                    except:
                                        pass
                                if os.path.exists(file_path_t):
                                    try:
                                        os.remove(file_path_t)
                                    except:
                                        pass
                                # 리스트에서 discard 처리하기
                                dict_video_album['active'] = 'false'
                                dict_video_album['discard'] = 'true'
                    # Active true(커버이미지)를 삭제한 경우 Default이미지를 커버로 다시 등장시킨다.
                    if check_discard_active_video == True:
                        for dict_video_album in list_dict_video_album:
                            if dict_video_album["id"] == 0:
                                dict_video_album["active"] = 'true'
                                dict_video_album["discard"] = 'false'
                    # Query 저장 프로세스
                    data = {'list_dict_video_album': list_dict_video_album}
                    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                    q_video_album_selected.refresh_from_db() 

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
            # date_released = datetime.strftime(input_date_released_str, date_format).date()
            date_object = datetime.strptime(date_string, date_format).date()
            data = {
                'date_released': date_object,
            }
            Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
            q_video_album_selected.refresh_from_db()
        
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


        # 모델 선택하기
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

        # 모델 선택해제하기
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

        # 이미지 업로드 했으면 저장하기
        if request.FILES:
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            # 앨범 갤러이 이미지 저장하기
            images = request.FILES.getlist('images')
            if images is not None and len(images) > 0:
                save_video_album_images(q_video_album_selected, images)

        # 비디오 업로드 했으면 저장하기
        if request.FILES:
            print('# 비디오 업로드 했으면 저장하기')
            if q_video_album_selected is None:
                q_video_album_selected = create_video_album()
            # 비디오 저장하기
            videos = request.FILES.getlist('videos')
            if videos is not None and len(videos) > 0:
                print('# 비디오 저장하기')
                save_video_album_videos(q_video_album_selected, videos)

        # 신규 Video Album 생성
        if request.POST.get('button') == 'create_video_album':
            q_actor = None 
            q_video_album_selected = None
            print('good luck~!')
            pass

        # Data Serialization
        if q_video_album_selected is not None:
            print('# 앨범이 등록되어 있다면', q_video_album_selected)
            print('q_actor', q_actor)
            if q_actor is None:
                q_actor = q_video_album_selected.main_actor
               
            # Settings에 선택된 Album 쿼리 등록
            print('세팅에 현재 앨범 등록하기', q_mysettings_hansent)
            data = {
                'video_album_selected': q_video_album_selected
            }
            MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
            q_mysettings_hansent.refresh_from_db()
        
            # Data Serialize
            selected_serialized_data_video_album = Video_Album_Serializer(q_video_album_selected, many=False).data
        
        if q_actor is not None:
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_VIDEO': BASE_DIR_VIDEO,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_video_album': selected_serialized_data_video_album,
        }
        print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)  


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_video_album_upload_modal_actor_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    
    if request.method == 'GET':
        print('get', request)
        keyword_str = request.GET.get('keyword')
        qs_xxx = Actor.objects.filter(Q(check_discard=False) & (Q(name__icontains=keyword_str) | Q(synonyms__icontains=keyword_str)))
        list_serialized_data_actor = None
        if qs_xxx is not None and len(qs_xxx) > 0:
            list_serialized_data_actor = Actor_Serializer(qs_xxx, many=True).data
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'list_serialized_data_actor': list_serialized_data_actor, 
        }
        return JsonResponse(jsondata, safe=False)

    if request.method == 'POST':
        print('********************', request.POST)
        jsondata = {}
        return JsonResponse(jsondata, safe=False)



#############################################################################################################################################
# Music Album  
#############################################################################################################################################

#--------------------------------------------------------------------------------------------------------------------------------------
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
        if list_searched_xxx_id is not None and len(list_searched_xxx_id) > 0:
            qs_xxx = Music_Album.objects.filter(Q(check_discard=False) & Q(id__in=list_searched_xxx_id)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        else:
            qs_xxx = Music_Album.objects.filter(Q(check_discard=False)).order_by(selected_field_sorting)[count_page_number_min:count_page_number_max]
        print('qs_xxx', qs_xxx)
        # Data Serialization            
        list_serialized_data_music_album = Music_Album_Serializer(qs_xxx, many=True).data
        
        jsondata = {
            'BASE_DIR_MUSIC': BASE_DIR_MUSIC,
            'list_field_sorting': LIST_MUSIC_FIELD,
            'list_serialized_data_music_album': list_serialized_data_music_album,
            'total_num_registered_item': total_num_registered_item,
            'total_num_searched_item': total_num_searched_item,
            'list_count_page_number': [count_page_number_min, count_page_number_max, count_page_number],
        }
        print('jsondata', jsondata)
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
            return redirect('hans-ent-actor-list')
       
        if request.POST.get('button') == 'page_number_min':
            count_page_number_down(request, q_mysettings_hansent)
            return redirect('hans-ent-actor-list')
        if request.POST.get('button') == 'page_number_max':
            count_page_number_up(request, q_mysettings_hansent, total_num_registered_item)
            return redirect('hans-ent-actor-list')
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
        return redirect('hans-ent-actor-list')
   
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
        selected_serialized_data_actor = {}
        selected_serialized_data_music_album = {}
        dict_album_key_fullsize_value_thumbnail_image_path = {}
        list_album_thumbnail_url = []

        # 받아야 하는 정보 수집하기 Actor or Album ##############################################
        selected_actor_id_str = request.POST.get('selected_actor_id')
        selected_music_album_id_str = request.POST.get('selected_music_album_id')

        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        selected_music_album_id_str = None if selected_music_album_id_str in LIST_STR_NONE_SERIES else selected_music_album_id_str
        
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
        
        # Data Serialization
        if q_music_album is not None: 
            if q_actor is None:
                q_actor = q_music_album.main_actor
            selected_serialized_data_music_album = Music_Album_Serializer(q_music_album, many=False).data
        if q_actor is not None:
            print('q_actor', q_actor)
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'BASE_DIR_MUSIC': BASE_DIR_MUSIC,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_music_album': selected_serialized_data_music_album,
        }
        # print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_music_album_upload_modal(request):
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
        print('streaming_music_album_upload_modal_view POST ========================================================== 1')
        print(request.POST,)
        print('======================================================================================================= 2')
        
        selected_serialized_data_music_album = {}
        selected_serialized_data_actor = {}
                
        selected_music_album_id_str = str(request.POST.get('selected_music_album_id'))
        selected_music_album_music_id_str = str(request.POST.get('selected_music_album_music_id'))
        selected_actor_id_str = request.POST.get('selected_actor_id')
        input_text_title_str = request.POST.get('input_text_title')
        input_text_name_str = request.POST.get('input_text_name')
        input_text_studio_str = request.POST.get('input_text_studio')
        input_date_released_str = request.POST.get('input_date_released')
        input_text_tag_str = request.POST.get('input_text_tag')
        selected_music_sub_type_str = request.POST.get('selected_music_sub_type')
        
        selected_music_album_id_str = None if selected_music_album_id_str in LIST_STR_NONE_SERIES else selected_music_album_id_str
        selected_music_album_music_id_str = None if selected_music_album_music_id_str in LIST_STR_NONE_SERIES else selected_music_album_music_id_str
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        input_text_title_str = None if input_text_title_str in LIST_STR_NONE_SERIES else input_text_title_str
        input_text_name_str = None if input_text_name_str in LIST_STR_NONE_SERIES else input_text_name_str
        input_text_studio_str = None if input_text_studio_str in LIST_STR_NONE_SERIES else input_text_studio_str
        input_date_released_str = None if input_date_released_str in LIST_STR_NONE_SERIES else input_date_released_str
        selected_music_sub_type_str = None if selected_music_sub_type_str in LIST_STR_NONE_SERIES else selected_music_sub_type_str
        
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
        
        # 앨범 통으로 삭제하기
        if request.POST.get('button') == 'music_album_delete':
            print('# 앨범 통으로 삭제하기', q_music_album_selected)
            if q_music_album_selected is not None:
                list_dict_music_album = q_music_album_selected.list_dict_music_album
                if list_dict_music_album is not None and len(list_dict_music_album) > 1:
                    # 앨범에 등록된 Music 삭제하기
                    for dict_music_album in list_dict_music_album:
                        # 서버어서 이미지 삭제하기
                        if dict_music_album["id"] != 0:
                            # Default 이미지가 아닌 경우 삭제가능
                            image_name_original = dict_music_album["original"]
                            image_name_cover = dict_music_album["cover"]
                            image_name_thumbnail = dict_music_album["thumbnail"]
                            file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_original)
                            file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_cover)
                            file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_thumbnail)
                            print('file_path_o', file_path_o)
                            if os.path.exists(file_path_o):
                                try:
                                    os.remove(file_path_o)
                                except:
                                    pass
                            if os.path.exists(file_path_c):
                                try:
                                    os.remove(file_path_c)
                                except:
                                    pass
                            if os.path.exists(file_path_t):
                                try:
                                    os.remove(file_path_t)
                                except:
                                    pass
                            # 리스트에서 discard 처리하기
                            dict_music_album['active'] = 'false'
                            dict_music_album['discard'] = 'true'
                # Query 저장 프로세스
                data = {
                    'list_dict_music_album': list_dict_music_album,
                    'check_discard': True,
                    }
                Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
                q_music_album_selected.refresh_from_db()
                    
            return redirect('hans-ent-music-album-list')

        # 앨범 커버 이미지 변경하기
        if request.POST.get('button') == 'change_music_album_cover_image':
            if selected_music_album_music_id_str is not None and selected_music_album_music_id_str != '':
                selected_music_album_music_id = int(selected_music_album_music_id_str)
                if q_music_album_selected is not None:
                    list_dict_music_album = q_music_album_selected.list_dict_music_album
                    # acitve 모두 false 변경
                    for dict_music_album in list_dict_music_album:
                        dict_music_album['active'] = 'false'
                        if dict_music_album['id'] == selected_music_album_music_id:
                            dict_music_album['active'] = 'true'
                    data = {'list_dict_music_album': list_dict_music_album}
                    Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
                    q_music_album_selected.refresh_from_db()
        
        # 앨범 이미지 삭제하기
        if request.POST.get('button') == 'remove_music_album_music':
            print('# 앨범 이미지 삭제하기')
            if selected_music_album_music_id_str is not None and selected_music_album_music_id_str != '':
                selected_music_album_music_id = int(selected_music_album_music_id_str)
                if q_music_album_selected is not None:
                    list_dict_music_album = q_music_album_selected.list_dict_music_album
                    # 이미지 삭제 프로세스
                    check_discard_active_music = False
                    for dict_music_album in list_dict_music_album:
                        if dict_music_album["id"] == selected_music_album_music_id:
                            # 커버이미지를 삭제하는 경우이면 Default를 커버로 지정하기 위해 플래그 올린다.
                            if dict_music_album["active"] == 'true':
                                check_discard_active_music = True
                            # 서버어서 이미지 삭제하기
                            if dict_music_album["id"] != 0:
                                # Default 이미지가 아닌 경우 삭제가능
                                image_name_original = dict_music_album["original"]
                                image_name_cover = dict_music_album["cover"]
                                image_name_thumbnail = dict_music_album["thumbnail"]
                                file_path_o = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_original)
                                file_path_c = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_cover)
                                file_path_t = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_thumbnail)
                                print('file_path_o', file_path_o)
                                if os.path.exists(file_path_o):
                                    try:
                                        os.remove(file_path_o)
                                    except:
                                        pass
                                if os.path.exists(file_path_c):
                                    try:
                                        os.remove(file_path_c)
                                    except:
                                        pass
                                if os.path.exists(file_path_t):
                                    try:
                                        os.remove(file_path_t)
                                    except:
                                        pass
                                # 리스트에서 discard 처리하기
                                dict_music_album['active'] = 'false'
                                dict_music_album['discard'] = 'true'
                    # Active true(커버이미지)를 삭제한 경우 Default이미지를 커버로 다시 등장시킨다.
                    if check_discard_active_music == True:
                        for dict_music_album in list_dict_music_album:
                            if dict_music_album["id"] == 0:
                                dict_music_album["active"] = 'true'
                                dict_music_album["discard"] = 'false'
                    # Query 저장 프로세스
                    data = {'list_dict_music_album': list_dict_music_album}
                    Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
                    q_music_album_selected.refresh_from_db() 

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
            # date_released = datetime.strftime(input_date_released_str, date_format).date()
            date_object = datetime.strptime(date_string, date_format).date()
            data = {
                'date_released': date_object,
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


        # 모델 선택하기
        if request.POST.get('button') == 'actor_select':
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            if q_music_album_selected is not None and q_actor is not None:
                print('선택된 모델', q_actor)
                data = {
                    'main_actor': q_actor,
                }
                Music_Album.objects.filter(id=q_music_album_selected.id).update(**data)
                q_music_album_selected.refresh_from_db()

        # 모델 선택해제하기
        if request.POST.get('button') == 'actor_select_reset':
            print('# 모델 선택해제하기')
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
            if q_music_album_selected is None:
                q_music_album_selected = create_music_album()
            # 앨범 갤러이 이미지 저장하기
            images = request.FILES.getlist('images')
            if images is not None and len(images) > 0:
                save_music_album_images(q_music_album_selected, images)

        # 신규 Music Album 생성
        if request.POST.get('button') == 'create_music_album':
            q_actor = None 
            q_music_album_selected = None
            print('good luck~!')
            pass

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
        
            # Data Serialize
            selected_serialized_data_music_album = Music_Album_Serializer(q_music_album_selected, many=False).data
            # dict_album_key_fullsize_value_thumbnail_image_path = get_dict_album_key_fullsize_value_thumbnail_image_path(q_music_album_selected)  # 앨범에 등록된 이미지 표시정보(Path) 획득하기
        
        if q_actor is not None:
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data

        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'BASE_DIR_MUSIC': BASE_DIR_MUSIC,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'selected_serialized_data_music_album': selected_serialized_data_music_album,
        }
        print('jsondata', jsondata)
        print('======================================================================================================= 3')
        return JsonResponse(jsondata, safe=False)  


#--------------------------------------------------------------------------------------------------------------------------------------
@login_required
def hans_ent_music_album_upload_modal_actor_search(request):
    q_user = request.user
    q_mysettings_hansent = MySettings_HansEnt.objects.get(user=q_user)
    
    if request.method == 'GET':
        print('get', request)
        keyword_str = request.GET.get('keyword')
        qs_xxx = Actor.objects.filter(Q(check_discard=False) & (Q(name__icontains=keyword_str) | Q(synonyms__icontains=keyword_str)))
        list_serialized_data_actor = None
        if qs_xxx is not None and len(qs_xxx) > 0:
            list_serialized_data_actor = Actor_Serializer(qs_xxx, many=True).data
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'list_serialized_data_actor': list_serialized_data_actor, 
        }
        return JsonResponse(jsondata, safe=False)

    if request.method == 'POST':
        print('********************', request.POST)
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