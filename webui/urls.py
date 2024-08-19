from django.urls import path
from webui.views import *
from django.contrib.auth import views as auth_views




urlpatterns = [
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Home
    #--------------------------------------------------------------------------------------------------------------------------------------
    path("", index, name="home"),
    path("family/", family, name="family"),
    path("study/", study, name="study"),
    path("entertainment/", entertainment, name="entertainment"),
    

    #--------------------------------------------------------------------------------------------------------------------------------------
    # hans_ent
    #--------------------------------------------------------------------------------------------------------------------------------------
    # actor
    path("hans_ent/", hans_ent, name="hans-ent"),
    path("hans_ent_actor_list", hans_ent_actor_list, name="hans-ent-actor-list"),
    path("hans_ent_actor_list_search/", hans_ent_actor_list_search, name="hans-ent-actor-list-search"),
    path("hans_ent_actor_profile_modal/", hans_ent_actor_profile_modal, name="hans-ent-actor-profile-modal"),
    path("hans_ent_actor_upload_modal/", hans_ent_actor_upload_modal, name="hans-ent-actor-upload-modal"),
    
    # picture album
    path("hans_ent_picture_album_list/", hans_ent_picture_album_list, name="hans-ent-picture-album-list"),
    path("hans_ent_picture_album_list_search/", hans_ent_picture_album_list_search, name="hans-ent-picture-album-list-search"),
    path("hans_ent_picture_album_gallery_modal/", hans_ent_picture_album_gallery_modal, name="hans-ent-picture-album-gallery-modal"),
    path("hans_ent_picture_album_upload_modal/", hans_ent_picture_album_upload_modal, name="hans-ent-picture-album-upload-modal"),
    path("hans_ent_picture_album_upload_modal_actor_search/", hans_ent_picture_album_upload_modal_actor_search, name="hans-ent-picture-album-upload-modal-actor-search"),
    
    # video album
    path("hans_ent_video_album_list/", hans_ent_video_album_list, name="hans-ent-video-album-list"),
    path("hans_ent_video_album_list_search/", hans_ent_video_album_list_search, name="hans-ent-video-album-list-search"),
    path("hans_ent_video_album_gallery_modal/", hans_ent_video_album_gallery_modal, name="hans-ent-video-album-gallery-modal"),
    path("hans_ent_video_album_upload_modal/", hans_ent_video_album_upload_modal, name="hans-ent-video-album-upload-modal"),
    path("hans_ent_video_album_upload_modal_actor_search/", hans_ent_video_album_upload_modal_actor_search, name="hans-ent-video-album-upload-modal-actor-search"),
    
    # music album
    path("hans_ent_music_album_list/", hans_ent_music_album_list, name="hans-ent-music-album-list"),
    path("hans_ent_music_album_list_search/", hans_ent_music_album_list_search, name="hans-ent-music-album-list-search"),
    path("hans_ent_music_album_gallery_modal/", hans_ent_music_album_gallery_modal, name="hans-ent-music-album-gallery-modal"),
    path("hans_ent_music_album_upload_modal/", hans_ent_music_album_upload_modal, name="hans-ent-music-album-upload-modal"),
    path("hans_ent_music_album_upload_modal_actor_search/", hans_ent_music_album_upload_modal_actor_search, name="hans-ent-music-album-upload-modal-actor-search"),
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # secret
    #--------------------------------------------------------------------------------------------------------------------------------------
    path("secret/", secret, name="secret"),

    #--------------------------------------------------------------------------------------------------------------------------------------
    # User
    #--------------------------------------------------------------------------------------------------------------------------------------
    path('register/', register_user, name="register-user"),
    path('profile/', profile_user, name="profile-user"),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout-user/', logout_user, name='logout-user'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name="logout"),
]