
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
            'date_birth',
            'locations',
            'evaluation',
            'list_dict_info_url',
            'list_actor_picture_id',
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