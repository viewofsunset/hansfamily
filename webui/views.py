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
        qs_xxx = Actor.objects.filter(Q(check_discard=False)) & (Q(name__icontains=keyword_str))
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
        list_serialized_data_video_album = {}
        list_serialized_data_picture_album = {}
        
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
            print('qs_video_album', qs_video_album)
            print('qs_picture_album', qs_picture_album)
            # print('qs_music_album', qs_music_album)
            if qs_picture_album is not None and len(qs_picture_album) > 0:
                list_serialized_data_picture_album = Picture_Album_Detail_Serializer(qs_picture_album, many=True).data
            if qs_video_album is not None and len(qs_video_album) > 0:
                list_serialized_data_video_album = Video_Album_Detail_Serializer(qs_video_album, many=True).data
            
        jsondata = {
            'selected_serialized_data_actor': selected_serialized_data_actor,
            'list_serialized_data_picture_album': list_serialized_data_picture_album,
            'list_serialized_data_video_album': list_serialized_data_video_album,
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
        # Request 정보 획득
        selected_actor_id_str = request.POST.get('selected_actor_id') # 기 선택되어 있는 배우, Merge시 사라지는 모델
        sacrificial_actor_id_str = request.POST.get('sacrificial_actor_id') # 새로 선택한 배우, Merge 하고 나서 살아남는 모델
        input_model_name_str = request.POST.get('input_text_name')
        input_date_birthday_str = request.POST.get('input_date_birthday')
        selected_actor_type_str = request.POST.get('selected_actor_type')
        selected_actor_sub_type_str = request.POST.get('selected_actor_sub_type')
        
        # Request 정보 필터링 String화
        selected_actor_id_str = None if selected_actor_id_str in LIST_STR_NONE_SERIES else selected_actor_id_str
        sacrificial_actor_id_str = None if sacrificial_actor_id_str in LIST_STR_NONE_SERIES else sacrificial_actor_id_str
        input_model_name_str = None if input_model_name_str in LIST_STR_NONE_SERIES else input_model_name_str
        input_date_birthday_str = None if input_date_birthday_str in LIST_STR_NONE_SERIES else input_date_birthday_str
        selected_actor_type_str = None if selected_actor_type_str in LIST_STR_NONE_SERIES else selected_actor_type_str
        selected_actor_sub_type_str = None if selected_actor_sub_type_str in LIST_STR_NONE_SERIES else selected_actor_sub_type_str
        
        # 선택된 배우 쿼리 찾기
        if selected_actor_id_str is not None and selected_actor_id_str != '':
            selected_actor_id = int(selected_actor_id_str)
            q_actor = Actor.objects.get(id=selected_actor_id)
        else:
            q_actor = None 
        
        # Merge 위해 새로 선택한 모델 정보 획득
        if sacrificial_actor_id_str is not None and sacrificial_actor_id_str != '':
            if q_actor is None:
                q_actor = create_actor()
            sacrificial_actor_id = int(sacrificial_actor_id_str)
            q_actor_s = Actor.objects.get(id=sacrificial_actor_id)
        else:
            q_actor_s = None 
        
        # 업로드 모델이름 저장하기
        if input_model_name_str is not None and input_model_name_str != '':
            if q_actor is None:
                q_actor = create_actor()
            data = {
                'name': input_model_name_str,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()
        
        # 생일 정보 저장하기
        if input_date_birthday_str is not None and input_date_birthday_str != '':
            if q_actor is None:
                q_actor = create_actor()
            print('# 생일 정보 저장하기', input_date_birthday_str, type(input_date_birthday_str))
            date_string = str(input_date_birthday_str)
            date_format = '%Y-%m-%d'
            date_object = datetime.strptime(date_string, date_format).date()
            data = {
                'date_birth': date_object,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()
        
        # Website 등록
        if request.POST.get('button') == 'website_url':
            if q_actor is None:
                q_actor = create_actor()
            input_actor_info_site_name = request.POST.get('input_actor_info_site_name')
            input_actor_info_site_url = request.POST.get('input_actor_info_site_url')
            list_dict_info_url = q_actor.list_dict_info_url
            if list_dict_info_url is None:
                list_dict_info_url = []
            list_dict_info_url.append({"name":input_actor_info_site_name, "site":input_actor_info_site_url})
            data = {
                'list_dict_info_url': list_dict_info_url,
            }
            Actor.objects.filter(id=q_actor.id).update(**data)
            q_actor.refresh_from_db()
        
        # Merge 하기, 선택된 모델에 검색된 모델을 합치기(선택된 모델이 살아남는다.)
        if request.POST.get('button') == 'select_to_merge':
            print('# 기존등록모델 선택 q_actor', q_actor)
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
        
        # Actor 커버 이미지 삭제하기 == default를 active 시키고 나머지는 inactive 시키기
        if request.POST.get('button') == 'remove_cover_image':
            if q_actor is None:
                q_actor = create_actor()
            if q_actor is not None:
                list_dict_profile_album = q_actor.list_dict_profile_album
                for dict_profile_album in list_dict_profile_album:
                    if dict_profile_album["id"] == "0":
                        dict_profile_album["active"] = "true"
                    else:
                        dict_profile_album["active"] = "false"
                data = {
                    'list_dict_profile_album': list_dict_profile_album,
                }
                Actor.objects.filter(id=q_actor.id).update(**data)
                q_actor.refresh_from_db() 
            
        # Actor 커버 이미지 & 갤러리 이미지 업로드 저장하기
        if request.FILES:
            if q_actor is None:
                q_actor = create_actor()
            if request.POST.get('image_type') == 'image_cover':
                # 앨범 커버 이미지 저장하기
                print('cover image', q_actor)
                image_cover = request.FILES.get('image_cover')
                if image_cover is not None:
                    q_actor = save_image_file_to_original_cover_and_thumbnail_images(q_actor, image_cover)

            if request.POST.get('image_type') == 'gallery_image':
                # 앨범 갤러이 이미지 저장하기
                print('gallery image')
                images = request.FILES.getlist('images')
                list_actor_picture_id = q_actor.list_actor_picture_id
                if list_actor_picture_id is None:
                    list_actor_picture_id = []
                if images is not None and len(images) > 0:
                    list_actor_picture_id_new = save_actor_gallery_images_and_thumbnail_to_db(q_actor, images)
                    if len(list_actor_picture_id_new) > 0:
                        for actor_picture_id_new in list_actor_picture_id_new:
                            if actor_picture_id_new not in list_actor_picture_id:
                                list_actor_picture_id.append(actor_picture_id_new)
                data = {
                    'list_actor_picture_id': list_actor_picture_id,
                }
                Actor.objects.filter(id=q_actor.id).update(**data)
                q_actor.refresh_from_db()

        # 선택 모델 삭제하기
        if request.POST.get('modal') == 'actor_delete':
            if q_actor is not None:
                data = {'check_discard':True}
                Actor.objects.filter(id=q_actor.id).update(**data)
            data = {
                'actor_selected': None,
            }
            StreamingSettings.objects.filter(id=q_streamingsettings.id).update(**data)
            q_streamingsettings.refresh_from_db() 
            q_actor = None
            return redirect('streaming-adult-actor-upload-modal-view')

        # Data Serialize 하기
        if q_actor is not None:
            print('q_actor', q_actor)
            selected_serialized_data_actor = Actor_Serializer(q_actor, many=False).data
        jsondata = {
            'BASE_DIR_ACTOR': BASE_DIR_ACTOR,
            'selected_serialized_data_actor': selected_serialized_data_actor,
            
        }
        print('jsondata', jsondata)
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