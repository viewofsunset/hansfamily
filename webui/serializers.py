
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
            'date_birth',
            'locations',
            'evaluation',
            'list_dict_info_url',
            'list_actor_picture_id',
        ]

