from django.shortcuts import render, redirect, reverse 
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User 

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