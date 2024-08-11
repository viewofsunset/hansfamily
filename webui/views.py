from django.shortcuts import render, redirect, reverse 
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User 

from webui.forms import user_register_form, user_update_form, profile_update_form
from webui.models import Profile_User


def index(request):
    # return HttpResponse("Hello world. this is hans family root page")
    # PreprocessingSettings.objects.all().delete()
    # MySettings.objects.all().delete()
    # print('deleted!!!')

    template = 'home.html'
    context={'key1': 'Good!'}
    # create_user_settings(request)
    # create_default_settings(request)
    return render(request, template, context)




def register_user(request):
    if request.method == 'POST':
        form = user_register_form(request.POST)    
        if form.is_valid():
            form.save()
            q_user = User.objects.last() 
            data = {'user': q_user}
            Profile_User.objects.create(**data)

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