
from rest_framework import serializers
from hans_ent.models import *



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
            'evaluation',
            'list_dict_info_url',
            'list_dict_profile_album',
        ]


class Picture_Album_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Picture_Album
        fields = [
            'id',
            # 'main_actor__id',
            'title',
            'list_dict_picture_album',
            'code',
            'studio',
            'score',
            'tags',
            'date_released',
        ]



class Video_Album_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Video_Album
        fields = [
            'id',
            # 'main_actor__id',
            'title',
            'list_dict_video_album',
            'code',
            'studio',
            'score',
            'tags',
            'date_released',
        ]


class Music_Album_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Music_Album
        fields = [
            'id',
            # 'main_actor__id',
            'title',
            'list_dict_music_album',
            'code',
            'studio',
            'score',
            'tags',
            'date_released',
        ]