from django.db import models
from django.contrib.auth.models import User 
from django.core.validators import FileExtensionValidator 





# LIST_MENU_VIDEO_TYPES = (
#     ('01', 'YOUTUBE_STUDY'),
#     ('02', 'YOUTUBE_ENT'),
#     ('03', 'MOVIE'),
#     ('04', 'DRAMA'),
#     ('05', 'KMODEL'),
#     ('06', 'KBJ'),
#     ('07', 'KAMA'),
#     ('08', 'JPN'),
#     ('09', 'CHN'),
#     ('10', 'WEST'),
#     ('11', 'VR'),
#     ('12', 'ETC'),
# )
# LIST_MENU_PICTURE_TYPES = (
#     ('01', '4KUP'),
#     ('02', 'ENT'),
#     ('03', 'AMA'),
#     ('04', 'ETC'),
# )
# LIST_MENU_MUSIC_TYPES = (
#     ('01', 'KPOP'),
#     ('02', 'POP'),
#     ('03', 'CLASSIC'),
#     ('04', 'JAZZ'),
#     ('05', 'ETC'),
# )
# LIST_SUB_MENU_VIDEO_TYPES = (
#     ('01', 'ALBUM'),
#     ('02', 'ACTOR'),
#     ('03', 'FAVORITE'),
#     ('04', 'ETC'),
# )
# LIST_SUB_MENU_PICTURE_TYPES = (
#     ('01', 'ALBUM'),
#     ('02', 'ACTOR'),
#     ('03', 'FAVORITE'),
#     ('04', 'ETC'),
# )
# LIST_SUB_MENU_MUSIC_TYPES = (
#     ('01', 'ALBUM'),
#     ('02', 'ACTOR'),
#     ('03', 'FAVORITE'),
#     ('04', 'ETC'),
# )
# LIST_RATING_SCORES = (
#     ('01', 'A'),
#     ('02', 'AA'),
#     ('03', 'AAA'),
#     ('04', 'AAAA'),
#     ('05', 'AAAAA'),
# )


BASE_DIR_ACTOR = '/media/vault1/actor/'
BASE_DIR_PICTURE = '/media/vault1/picture/'
BASE_DIR_VIDEO = '/media/vault1/video/'

LIST_MENU_HANS_ENT = (
    ('01', 'ACTOR'),
    ('02', 'PICTURE'),
    ('03', 'VIDEO'),
)
LIST_ACTOR_TAGS = ["JAV", "BJ", "Model", "Actress","Idol", "Amature", "Gravure", "Onlyfans", "Tweeter", "Instagram", "Porn_Actor", "Youtuber"]
LIST_LOCATIONS = (
    ('01', 'KOREA'),
    ('02', 'JAPAN'),
    ('03', 'CHINA'),
    ('04', 'MIDDLE_EAST'),
    ('05', 'EUROP'),
    ('06', 'NORTH_AMERICA'),
    ('07', 'SOUTH_AMERICA'),
    ('08', 'AFRICA'),
    ('09', 'ETC'),
)

"""
image naming $ size rules
thumbnail image: hashcode-t.xxx  // size: 260px by 320px
cover image: hashcode-c.xxx  // size: 520px by 640px
original image: hashcode-o.xxx  // size: 그대로
still image: hashcode-s-<order number>.xxx  // size: 65px by 80px
"""    

"""
list_dict_profile_album rule:
[
{"id":"0", "thumbnail":"default_actor-t.png", "cover":"default_actor-c.png", "original":"default_actor-o.png", "active":"true"},
{"id":"1", "thumbnail":"abcd-t-1.png", "cover":"abcd-c-1.png", "original":"abcd-o-1.png", "active":"false"},
{"id":"2", "thumbnail":"abcd-t-2.png", "cover":"abcd-c-2.png", "original":"abcd-o-2.png", "active":"false"},
]
abcd == hashcode
"""
class Actor(models.Model):
    # classification
    # types = models.CharField(max_length=50, choices=LIST_MENU_STREAMING, default=LIST_MENU_STREAMING[0][0], blank=True) # Submenu Switching
    # sub_types_video = models.CharField(max_length=50, choices=LIST_MENU_VIDEO_TYPES, default=LIST_MENU_VIDEO_TYPES[0][0], blank=True) # Submenu Switching
    # sub_types_picture = models.CharField(max_length=50, choices=LIST_MENU_PICTURE_TYPES, default=LIST_MENU_PICTURE_TYPES[0][0], blank=True) # Submenu Switching
    # sub_types_music = models.CharField(max_length=50, choices=LIST_MENU_MUSIC_TYPES, default=LIST_MENU_MUSIC_TYPES[0][0], blank=True) # Submenu Switching
    
    # properties
    name = models.CharField(max_length=200, null=True, blank=True)
    synonyms = models.JSONField(null=True, blank=True)
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    image_cover = models.ImageField(null=True, blank=True)  # 400px by 500px, 
    age = models.IntegerField(null=True, blank=True)
    date_birth = models.DateField(null=True, blank=True)
    locations = models.CharField(max_length=50, choices=LIST_LOCATIONS, default=LIST_LOCATIONS[0][0], blank=True) # Submenu Switching
    height = models.IntegerField(null=True, blank=True)
    tags = models.JSONField(null=True, blank=True) # Collect tags from LIST_ACTOR_TAGS
    evaluation = models.FloatField(default=0)
    # URL info
    list_dict_info_url =  models.JSONField(null=True, blank=True) # [{"name":'imdb', "site":'https://www.imbd.com/xxx'}, {}]
    list_actor_picture_id = models.JSONField(null=True, blank=True)
    list_dict_profile_album = models.JSONField(null=True, blank=True) # list_dict_profile_album rule 참고

    # system
    date_created = models.DateField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)
    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} Actor'
    


# # class Picture_Actor_Pic(models.Model):
# class Actor_Pic(models.Model):
#     actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
#     title = models.CharField(max_length=250, null=True, blank=True)
#     # name = models.CharField(max_length=250, null=True, blank=True)
#     hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
#     image_thumbnail = models.ImageField(null=True, blank=True) # 260px by 320px
#     image_cover = models.ImageField(null=True, blank=True)  # 520px by 640px
#     image_original = models.ImageField(null=True, blank=True) # original 그대로
#     check_discard = models.BooleanField(default=False)
    
#     def __str__(self):
#         return f'{self.actor.name}-{self.id} Actor_Pic'


"""
list_dict_picture_album rule:
[
{"id":"0", "thumbnail":"default_picture_album-t.png", "cover":"default_picture_album-c.png", "original":"default_picture_album-o.png", "active":"true"},
{"id":"1", "thumbnail":"abcd-1-t.png", "cover":"abcd-1-c.png", "original":"abcd-1-o.png", "active":"false"},
{"id":"2", "thumbnail":"abcd-2-t.png", "cover":"abcd-2-c.png", "original":"abcd-2-o.png", "active":"false"},
]
abcd == hashcode
"""
class Picture_Album(models.Model):
    main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    list_dict_picture_album = models.JSONField(null=True, blank=True)
    check_discard = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.title} Picture_Album'


"""
list_dict_video_album rule:
[
{"id":"0", "video":"abcd-1-v.mp4", "thumbnail":"default_video_album-t.png", "cover":"default_video_album-c.png", "original":"default_video_album-o.png", "still":"default_video_album-s.png" "active":"true"},
{"id":"1", "video":"abcd-1-v.mp4", "thumbnail":"abcd-1-t.png", "cover":"abcd-1-c.png", "original":"abcd-1-o.png", "still":["abcd-1-s-1.png", "abcd-1-s-2.png"], "active":"false"},
{"id":"2", "video":"abcd-2-v.mp4", "thumbnail":"abcd-2-t.png", "cover":"abcd-2-c.png", "original":"abcd-2-o.png", "still":["abcd-2-s-1.png", "abcd-2-s-2.png"], "active":"false"},
]
abcd == hashcode
"""
class Video_Album(models.Model):
    main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    list_dict_video_album = models.JSONField(null=True, blank=True)
    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} Video_Album'



LIST_NUM_DISPLAY_IN_PAGE = 100
LIST_ACTOR_FIELD = ["id", "name", "age", "locations", "evaluation", "date_updated"]
LIST_PICTURE_FIELD = ["id", "name", "age", "locations", "evaluation", "date_updated"]
LIST_VIDEO_FIELD = ["id", "name", "age", "locations", "evaluation", "date_updated"]

class MySettings_HansEnt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) 
    menu_selected = models.CharField(choices=LIST_MENU_HANS_ENT, default=LIST_MENU_HANS_ENT[0][0], blank=True)
    # actor
    actor_selected = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    # actor_pic_selected = models.ForeignKey(Actor_Pic, on_delete=models.SET_NULL, null=True, blank=True)
    selected_field_actor = models.CharField(max_length=50, default=LIST_ACTOR_FIELD[0], blank=True)
    check_field_ascending_actor = models.BooleanField(default=True)
    count_page_number_actor = models.IntegerField(default=1)
    list_searched_actor_id = models.JSONField(null=True, blank=True)

    # picture
    selected_field_picture = models.CharField(max_length=50, default=LIST_PICTURE_FIELD[0], blank=True)
    check_field_ascending_picture = models.BooleanField(default=True)
    count_page_number_picture = models.IntegerField(default=1)
    list_searched_picture_id = models.JSONField(null=True, blank=True)

    # video
    selected_field_video = models.CharField(max_length=50, default=LIST_VIDEO_FIELD[0], blank=True)
    check_field_ascending_video = models.BooleanField(default=True)
    count_page_number_video = models.IntegerField(default=1)
    list_searched_video_id = models.JSONField(null=True, blank=True)

    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} MySettings_HansEnt'



# class Picture_Album(models.Model):
#     main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)

#     title = models.CharField(max_length=200, null=True, blank=True)
#     name = models.CharField(max_length=200, null=True, blank=True)
#     types = models.CharField(max_length=50, choices=LIST_MENU_PICTURE_TYPES, default=LIST_MENU_PICTURE_TYPES[0][0], blank=True) # Submenu Switching
#     location = models.CharField(max_length=50, choices=LIST_LOCATIONS, default=LIST_LOCATIONS[0][0], blank=True) # Submenu Switching
#     score = models.CharField(max_length=50, choices=LIST_RATING_SCORES, default=LIST_RATING_SCORES[0][0], blank=True) # Submenu Switching
#     # properties
#     studio = models.CharField(max_length=200, null=True, blank=True)
#     date_released = models.DateField(null=True, blank=True)
#     list_tag = models.JSONField(null=True, blank=True) 
#     code = models.CharField(max_length=50, null=True, blank=True)

#     # URLs
#     detail_info_url =  models.TextField(null=True, blank=True)  # 앨범 정보 및 섬네일 있는 페이지
#     list_album_thumbnail_url = models.JSONField(null=True, blank=True) # Web에 있는 Thumbnail URL
#     album_download_url = models.TextField(null=True, blank=True) # Web에 모델 출현 엘범 갤러리 URL
#     list_album_picture_url = models.JSONField(null=True, blank=True) # Web에 있는 이미지 URL
#     model_gallery_url = models.TextField(null=True, blank=True) # Web에 모델 출현 엘범 갤러리 URL
#     cover_image_url =  models.TextField(null=True, blank=True)
#     # DB images
#     image_cover = models.ImageField(null=True, blank=True)  # uploads/picture_album/cover_images/{{ q_pic_album.id }}/{{ file_name }}
#     list_album_picture_id = models.JSONField(null=True, blank=True) # DB에 저장된 Picture_Album_Pic ID
    
#     # check_systems
#     # check_profile_album = models.BooleanField(default=False)
#     check_under_uploading = models.BooleanField(default=False)
#     date_created = models.DateField(auto_now_add=True, null=True)
#     date_updated = models.DateTimeField(auto_now=True, null=True)
#     check_discard = models.BooleanField(default=False)
    



# class Picture_Album_Pic(models.Model):
#     album = models.ForeignKey(Picture_Album, on_delete=models.SET_NULL, null=True, blank=True)
#     title = models.CharField(max_length=250, null=True, blank=True)
#     image_thumbnail = models.ImageField(null=True, blank=True) # uploads/picture_album/thumbnail_images/{{ q_pic.id }}/{{ file_name }}
#     image_original = models.ImageField(null=True, blank=True) # uploads/picture_album/original_images /{{ q_pic_album.id }}/{{ file_name }}
#     check_discard = models.BooleanField(default=False)





# class Video_Album(models.Model):
#     main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)

#     title = models.CharField(max_length=200, null=True, blank=True)
#     file_name = models.CharField(max_length=200, null=True, blank=True)
#     types = models.CharField(max_length=50, choices=LIST_MENU_VIDEO_TYPES, default=LIST_MENU_VIDEO_TYPES[0][0], blank=True) # Submenu Switching
#     locations = models.CharField(max_length=50, choices=LIST_LOCATIONS, default=LIST_LOCATIONS[0][0], blank=True) # Submenu Switching
#     score = models.CharField(max_length=50, choices=LIST_RATING_SCORES, default=LIST_RATING_SCORES[0][0], blank=True) # Submenu Switching
#     # properties
#     studio = models.CharField(max_length=100, null=True, blank=True)
#     actor_name = models.CharField(max_length=200, null=True, blank=True)
#     list_actors = models.JSONField(null=True, blank=True)
#     director = models.CharField(max_length=100, null=True, blank=True)
#     description = models.TextField(null=True, blank=True)
#     date_released = models.DateField(null=True, blank=True)
#     code = models.CharField(max_length=50, null=True, blank=True)
#     # URLs
#     detail_info_url = models.TextField(null=True, blank=True)
#     cover_image_url = models.TextField(null=True, blank=True)
#     # DB images
#     image_original = models.ImageField(null=True, blank=True) # uploads/video_album/original_images /{{ q_vid.id }}/{{ file_name }}
#     image_cover = models.ImageField(null=True, blank=True)  # uploads/video_album/cover_images/{{ q_vid.id }}/{{ file_name }}
#     list_album_video_id = models.JSONField(null=True, blank=True) # DB에 저장된 Video_Album_Vid ID
#     # check systems
#     date_created = models.DateField(auto_now_add=True, null=True)
#     date_updated = models.DateTimeField(auto_now=True, null=True)
#     check_discard = models.BooleanField(default=False)

#     # check_under_uploading = models.BooleanField(default=False)


# class Video_Album_Vid(models.Model):
#     album = models.ForeignKey(Video_Album, on_delete=models.SET_NULL, null=True, blank=True)
#     title = models.CharField(max_length=250, null=True, blank=True)
#     youtube_address_key = models.CharField(max_length=100, null=True, blank=True)
#     video_file = models.FileField(null=True, blank=True)  # uploads/video_album/video_files/{{ q_vid.id }}/{{ file_name }}
#     subtitle_file = models.FileField(null=True, blank=True)  # uploads/video_album/subtitle_files/{{ q_vid.id }}/{{ file_name }}
#     image_thumbnail = models.ImageField(null=True, blank=True) # uploads/video_album/thumbnail_images/{{ q_vid.id }}/{{ file_name }}
#     list_still_image = models.JSONField(null=True, blank=True)  # list [path_still_images]
#     check_discard = models.BooleanField(default=False)
    





# class Music_Album(models.Model):
#     main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)

#     title = models.CharField(max_length=200, null=True, blank=True)
#     types = models.CharField(max_length=50, choices=LIST_MENU_MUSIC_TYPES, default=LIST_MENU_MUSIC_TYPES[0][0], blank=True) # Submenu Switching
#     location = models.CharField(max_length=50, choices=LIST_LOCATIONS, default=LIST_LOCATIONS[0][0], blank=True) # Submenu Switching
#     score = models.CharField(max_length=50, choices=LIST_RATING_SCORES, default=LIST_RATING_SCORES[0][0], blank=True) # Submenu Switching
#     # properties
#     date_released = models.DateField(null=True, blank=True)
#     # URLs
#     detail_info_url =  models.TextField(null=True, blank=True)
#     cover_image_url =  models.TextField(null=True, blank=True)
#     # DB images
#     image_original = models.ImageField(null=True, blank=True) # uploads/music_album/original_images /{{ q_music_album.id }}/{{ file_name }}
#     image_cover = models.ImageField(null=True, blank=True)  # uploads/music_album/cover_images/{{ q_music_album.id }}/{{ file_name }}
#     list_album_music_id = models.JSONField(null=True, blank=True) # DB에 저장된 Picture_Album_Pic ID
#     # systems
#     date_created = models.DateField(auto_now_add=True, null=True)
#     date_updated = models.DateTimeField(auto_now=True, null=True)
#     check_discard = models.BooleanField(default=False)

#     # check_under_uploading = models.BooleanField(default=False)


# class Music_Album_Mus(models.Model):
#     album = models.ForeignKey(Music_Album, on_delete=models.SET_NULL, null=True, blank=True)
#     title = models.CharField(max_length=250, null=True, blank=True)
#     video_file = models.FileField(null=True, blank=True)  # uploads/music_album/video_files/{{ q_mus.id }}/{{ file_name }}
#     audio_file = models.FileField(null=True, blank=True)  # uploads/music_album/audio_files/{{ q_mus.id }}/{{ file_name }}
#     youtube_address_key = models.CharField(max_length=200, null=True, blank=True)
#     image_thumbnail = models.ImageField(null=True, blank=True) # uploads/music_album/thumbnail_images/{{ q_pic.id }}/{{ file_name }}
#     check_discard = models.BooleanField(default=False)


