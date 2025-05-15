
from rest_framework import serializers
from hans_ent.models import *
from study.models import *


class Paper_Search_Google_and_PubMed_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Paper_Search_Google_and_PubMed
        fields = [
            'id',
            'keyword',
            'list_dict_paper_info_from_pubmed',
            'list_dict_paper_info_from_google',
            'list_dict_paper_info_from_voronoi_db', 
            'list_dict_paper_info_from_my_favorite', 
            'list_dict_paper_info_from_etc',
            'list_paper_id_from_pubmed',
            'list_paper_id_from_google',
            'list_paper_id_from_etc',
            'list_paper_id_from_voronoi_db',
            'list_paper_id_from_my_favorite',
            'list_selected_search_options',
        ]


class Paper_Search_Google_and_PubMed_Mine_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Paper_Search_Google_and_PubMed
        fields = [
            'id',
            'keyword',
            'list_selected_search_options',
        ]


class Paper_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = [
            'id',
            'title',
            'doi',
            'doi_url',
            'pmcid',
            'first_author_name', 
            'first_author_url',
            'file_path_xml', 
            'file_path_pdf', 
            'dict_paper_info', 
            'publication_year',
            'list_dict_reference_paper',
            'list_dict_reference_paper',
            'list_dict_relevant_paper',
            'list_reference_paper_id',
            'list_author_paper_id',
            'list_relevant_paper_id',
            'list_dict_paper_hierachy',
            'list_bookmarked_user_id',
            'list_dict_paper_image',
        ]


class List_Paper_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = [
            'id',
            'title',
            'doi',
            'pmcid',
            'first_author_name', 
            'first_author_url',
            'file_path_xml', 
            'file_path_pdf', 
            'dict_paper_info', 
            'publication_year', 
            'doi_url',
            'article_url',
            'pdf_url',
            
            # 'list_dict_reference_paper',
            # 'list_dict_reference_paper',
            # 'list_dict_relevant_paper',
            # 'list_reference_paper_id',
            # 'list_author_paper_id',
            # 'list_relevant_paper_id',
            # 'list_dict_paper_hierachy',
        ]

class MySettings_Study_Serializer(serializers.ModelSerializer):
    class Meta:
        model = MySettings_Study
        fields = [
            'menu_selected',
            'list_history_search_paper',
            'list_bookmarked_paper_id',
            'active_tab_searched_paper',
            'list_selected_options_paper_search',
            'active_tab_collected_paper',
        ]









class Actor_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = [
            'id',
            'name',
            'synonyms',
            'age',
            'height',
            'date_birth',
            'locations',
            'tags',
            'score',
            'rating',
            'list_dict_info_url',
            'list_dict_profile_album',
            'category',
        ]


class Picture_Album_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Picture_Album
        fields = [
            'id',
            # 'main_actor__id',
            'title',
            'list_dict_picture_album',
            'list_picture_url_album', 
            'list_dict_info_url',
            'code',
            'studio',
            'score',
            'rating',
            'tags',
            'date_released',
            'category',
            'check_url_downloaded',
            'check_4k_uploaded',
        ]

class Picture_Album_Basic_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Picture_Album
        fields = [
            'id',
            'title',
            'list_dict_picture_album',
        ]



class Manga_Album_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Manga_Album
        fields = [
            'id',
            'id_manga',
            'title',
            'dict_manga_album_cover',
            'list_dict_manga_album',
            'list_dict_volume_manga',
            'list_dict_info_url',
            'last_volume',
            'studio',
            'score',
            'rating',
            'tags',
            'date_released',
            'category',
            'check_new_volume',
            'check_completed',
        ]

class Manga_Album_list_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Manga_Album
        fields = [
            'id',
            'id_manga',
            'title',
            'dict_manga_album_cover',
            'list_dict_info_url',
            'last_volume',
            'studio',
            'score',
            'rating',
            'tags',
            'date_released',
            'category',
            'check_new_volume',
            'check_completed',
        ]
    




class Video_Album_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Video_Album
        fields = [
            'id',
            # 'main_actor__id',
            'title',
            'list_dict_picture_album',
            'list_dict_video_album',
            'list_dict_info_url',
            'code',
            'studio',
            'score',
            'rating',
            'tags',
            'date_released',
            'category',
        ]


class Music_Album_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Music_Album
        fields = [
            'id',
            # 'main_actor__id',
            'title',
            'list_dict_picture_album',
            'list_dict_music_album',
            'list_dict_info_url',
            'code',
            'studio',
            'score',
            'rating',
            'tags',
            'date_released',
            'category',
        ]


class Mysettings_Hans_Ent_Serializer(serializers.ModelSerializer):
    class Meta:
        model = MySettings_HansEnt
        fields = [
            # 'menu_selected',
            # 'actor_selected',
            # 'selected_field_actor',
            # 'check_field_ascending_actor',
            # 'count_page_number_actor',
            # 'list_searched_actor_id',
            # # 'picture_album_selected',
            # 'selected_field_picture',
            # 'check_field_ascending_picture',
            # 'count_page_number_picture',
            # 'list_searched_picture_album_id',
            # # 'video_album_selected',
            # 'selected_field_video',
            # 'check_field_ascending_video',
            # 'count_page_number_video',
            # 'list_searched_video_album_id',
            # # 'music_album_selected',
            # 'selected_field_music',
            # 'check_field_ascending_music',
            # 'count_page_number_music',
            # 'list_searched_music_album_id',

            'check_music_player_expand',
            'check_audio_is_playing_now',
            'check_shuffle_play_activated',
            'check_loop_play_activated',
            'check_repeat_play_activated',
            'check_favorite_play_activated',
            'check_background_play_activated',
        ]



class SystemSettings_HansEnt_Serializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings_HansEnt
        fields = [
            'list_dict_nationality',
            'parsing_base_url_manga',
            'parsing_cover_img_url_manga',
            'list_dict_manga_info_for_parsing',
        ]