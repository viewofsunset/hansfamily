from django.contrib import admin
from hans_ent.models import *




admin.site.register(Actor)
admin.site.register(Picture_Album)
admin.site.register(Manga_Album)
admin.site.register(Video_Album)
admin.site.register(Music_Album)

admin.site.register(MySettings_HansEnt)
admin.site.register(SystemSettings_HansEnt)
