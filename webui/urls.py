from django.urls import path
from webui.views import *
from django.contrib.auth import views as auth_views




urlpatterns = [
    path("", index, name="home"),
    path("family/", family, name="family"),
    path("study/", study, name="study"),
    path("entertainment/", entertainment, name="entertainment"),
    path("hans_ent/", hans_ent, name="hans-ent"),
    path("secret/", secret, name="secret"),

    path('register/', register_user, name="register-user"),
    path('profile/', profile_user, name="profile-user"),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout-user/', logout_user, name='logout-user'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name="logout"),
]