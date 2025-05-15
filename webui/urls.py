from django.urls import path, include
from webui.views import *
from django.contrib.auth import views as auth_views




urlpatterns = [

    #--------------------------------------------------------------------------------------------------------------------------------------
    # Home
    #--------------------------------------------------------------------------------------------------------------------------------------
    path("", index, name="home"),
    path("family/", family, name="family"),
    
    #--------------------------------------------------------------------------------------------------------------------------------------
    # Study
    #--------------------------------------------------------------------------------------------------------------------------------------
    path("study/", study, name="study"),
    path('study_refresh_router/', study_refresh_router, name="study-refresh-router"),

    # My Study
    path("study_mystudy/", study_mystudy, name="study-mystudy"),
    
    # Conference
    path("study_conference/", study_conference, name="study-conference"),

    # Paper
    path("study_paper/", study_paper, name="study-paper"),
    path("study_paper_search_form/", study_paper_search_form, name="study-paper-search-form"),
    path("study_paper_selected_paper_data_collection/", study_paper_selected_paper_data_collection, name="study-paper-selected-paper-data-collection"),
    path("study_paper_selected_paper_modal_action/", study_paper_selected_paper_modal_action, name="study-paper-selected-paper-modal-action"),
    
    # Patent
    path("study_patent/", study_patent, name="study-patent"),

    # Protocol
    path("study_protocol/", study_protocol, name="study-protocol"),

    # FDA
    path("study_fda/", study_fda, name="study-fda"),

    # Lecture
    path("study_lecture/", study_lecture, name="study-lecture"),


    #--------------------------------------------------------------------------------------------------------------------------------------
    # hans_ent
    #--------------------------------------------------------------------------------------------------------------------------------------
    path("hans_ent/", hans_ent, name="hans-ent"),
    path('hans_ent_refresh_router/', hans_ent_refresh_router, name="hans-ent-refresh-router"),
    
    path('hans_ent_test_function/', hans_ent_test_function, name="hans_ent_test_function"),
    # actor
    path("hans_ent_actor_list/", hans_ent_actor_list, name="hans-ent-actor-list"),
    path("hans_ent_actor_list_search/", hans_ent_actor_list_search, name="hans-ent-actor-list-search"),
    path("hans_ent_actor_profile_modal/", hans_ent_actor_profile_modal, name="hans-ent-actor-profile-modal"),
    path("hans_ent_actor_update_modal/", hans_ent_actor_update_modal, name="hans-ent-actor-upload-modal"),

    # picture album
    path("hans_ent_picture_album_list/", hans_ent_picture_album_list, name="hans-ent-picture-album-list"),
    path("hans_ent_picture_album_list_search/", hans_ent_picture_album_list_search, name="hans-ent-picture-album-list-search"),
    path("hans_ent_picture_album_gallery_modal/", hans_ent_picture_album_gallery_modal, name="hans-ent-picture-album-gallery-modal"),
    path("hans_ent_picture_album_update_modal/", hans_ent_picture_album_update_modal, name="hans-ent-picture-album-upload-modal"),
    path("hans_ent_picture_album_update_modal_actor_search/", hans_ent_picture_album_update_modal_actor_search, name="hans-ent-picture-album-upload-modal-actor-search"),

    # manga album
    path("hans_ent_manga_album_list/", hans_ent_manga_album_list, name="hans-ent-manga-album-list"),
    path("hans_ent_manga_album_list_search/", hans_ent_manga_album_list_search, name="hans-ent-manga-album-list-search"),
    path("hans_ent_manga_album_profile_modal/", hans_ent_manga_album_profile_modal, name="hans-ent-manga-album-profile-modal"),
    path("hans_ent_manga_album_gallery_modal/", hans_ent_manga_album_gallery_modal, name="hans-ent-manga-album-gallery-modal"),
    path("hans_ent_manga_album_update_modal/", hans_ent_manga_album_update_modal, name="hans-ent-manga-album-upload-modal"),
    path("hans_ent_manga_album_scraping_modal/", hans_ent_manga_album_scraping_modal, name="hans-ent-manga-album-scraping-modal"), 

    # video album
    path("hans_ent_video_album_list/", hans_ent_video_album_list, name="hans-ent-video-album-list"),
    path("hans_ent_video_album_list_search/", hans_ent_video_album_list_search, name="hans-ent-video-album-list-search"),
    path("hans_ent_video_album_profile_modal/", hans_ent_video_album_profile_modal, name="hans-ent-video-album-profile-modal"),
    path("hans_ent_video_album_gallery_modal/", hans_ent_video_album_gallery_modal, name="hans-ent-video-album-gallery-modal"),
    path("hans_ent_video_album_update_modal/", hans_ent_video_album_update_modal, name="hans-ent-video-album-upload-modal"),
    path("hans_ent_video_album_update_modal_actor_search/", hans_ent_video_album_update_modal_actor_search, name="hans-ent-video-album-upload-modal-actor-search"),
    
    # music album
    path("hans_ent_music_album_list/", hans_ent_music_album_list, name="hans-ent-music-album-list"),
    path("hans_ent_music_album_list_search/", hans_ent_music_album_list_search, name="hans-ent-music-album-list-search"),
    path("hans_ent_music_album_gallery_modal/", hans_ent_music_album_gallery_modal, name="hans-ent-music-album-gallery-modal"),
    path("hans_ent_music_album_update_modal/", hans_ent_music_album_update_modal, name="hans-ent-music-album-upload-modal"),
    path("hans_ent_music_album_update_modal_actor_search/", hans_ent_music_album_update_modal_actor_search, name="hans-ent-music-album-upload-modal-actor-search"),
    
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