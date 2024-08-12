from django.shortcuts import render, redirect, reverse 
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User 

from webui.forms import user_register_form, user_update_form, profile_update_form
from webui.models import Profile_User, Authorization
from hans_ent.models import *



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