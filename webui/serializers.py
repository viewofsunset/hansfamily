
from rest_framework import serializers
from hans_ent.models import *



class Actor_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = [
            'id',
            'name',
            'synonyms',
            'image_cover',
            'age',
            'height',
            'date_birth',
            'locations',
            'tags',
            'evaluation',
            'list_dict_info_url',
            'list_actor_picture_id',
            'list_dict_profile_album',
        ]


class Picture_Album_Detail_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Picture_Album
        fields = [
            'id',
            'title',
        ]



class Video_Album_Detail_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Video_Album
        fields = [
            'id',
            'title',
        ]