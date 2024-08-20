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
BASE_DIR_MUSIC = '/media/vault1/music/'

RELATIVE_PATH_ACTOR = 'vault1/actor/'
RELATIVE_PATH_PICTURE = 'vault1/picture/'
RELATIVE_PATH_VIDEO = 'vault1/video/'
RELATIVE_PATH_MUSIC = 'vault1/music/'

LIST_MENU_HANS_ENT = (
    ('01', 'ACTOR'),
    ('02', 'PICTURE'),
    ('03', 'VIDEO'),
    ('04', 'MUSIC'),
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

LIST_NUM_DISPLAY_IN_PAGE = 100
LIST_ACTOR_FIELD = ["id", "name", "age", "locations", "evaluation", "date_updated"]
LIST_PICTURE_FIELD = ["id", "name", "age", "locations", "evaluation", "date_updated"]
LIST_VIDEO_FIELD = ["id", "name", "age", "locations", "evaluation", "date_updated"]
LIST_MUSIC_FIELD = ["id", "name", "age", "locations", "evaluation", "date_updated"]


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
DEFAULT_LIST_DICT_PROFILE_ALBUM = [{'id':0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "active":"true", "discard":"false"}]

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
    age = models.IntegerField(null=True, blank=True)
    date_birth = models.DateField(null=True, blank=True)
    locations = models.CharField(max_length=50, choices=LIST_LOCATIONS, default=LIST_LOCATIONS[0][0], blank=True) # Submenu Switching
    height = models.IntegerField(null=True, blank=True)
    tags = models.JSONField(null=True, blank=True) # Collect tags from LIST_ACTOR_TAGS
    evaluation = models.FloatField(default=0)
    # 
    list_dict_info_url =  models.JSONField(null=True, blank=True) # [{"name":'imdb', "site":'https://www.imbd.com/xxx'}, {}]
    list_dict_profile_album = models.JSONField(null=True, blank=True) # list_dict_profile_album rule 참고

    # system
    date_created = models.DateField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)
    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} Actor'
    


"""
Picture Album은
    1개의 list_dict_picture_album 을 가진다:
    [
    {"id":"0", "thumbnail":"default-t.png", "cover":"default-c.png", "original":"default-o.png", "active":"true", "discard":"false"},
    {"id":"1", "thumbnail":"abcd-t-1.png", "cover":"abcd-c-1.png", "original":"abcd-o-1.png", "active":"false", "discard":"false"},
    {"id":"2", "thumbnail":"abcd-t-2.png", "cover":"abcd-c-2.png", "original":"abcd-o-2.png", "active":"false", "discard":"false"},
    ]
    abcd == hashcode
"""
DEFAULT_LIST_DICT_PICTURE_ALBUM = [{'id':0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "active":"true", "discard":"false"}]

class Picture_Album(models.Model):
    main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    list_dict_picture_album = models.JSONField(null=True, blank=True)
    code = models.CharField(max_length=250, null=True, blank=True)
    studio = models.CharField(max_length=250, null=True, blank=True)
    score = models.FloatField(default=0)
    tags = models.JSONField(null=True, blank=True) # Collect tags from LIST_ACTOR_TAGS
    date_released = models.DateField(null=True, blank=True)
    check_discard = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.title} Picture_Album'


"""
Video Album은
        1개의 list_dict_picture_album과 1개의 list_dict_video_album 이 있음
        list_dict_picture_album은 커버이미지들을 담당. Picture_Album의 list_dict_picture_album과 기능적으로 같다.
        [
        {"id":"0", "thumbnail":"default-t.png", "cover":"default-c.png", "original":"default-o.png", "active":"true", "discard":"false"},
        {"id":"1", "thumbnail":"abcd-p-t-1.png", "cover":"abcd-p-c-1.png", "original":"abcd-p-o-1.png", "active":"false", "discard":"false"},
        {"id":"2", "thumbnail":"abcd-p-t-2.png", "cover":"abcd-p-c-2.png", "original":"abcd-p-o-2.png", "active":"false", "discard":"false"},
        ]
        abcd == hashcode
        list_dict_video_album은 video들을 담당
        [
        {"id":"0", "video":"default.mp4", "thumbnail":"default-t.png", "cover":"default-c.png", "original":"default-o.png", "still":{"0":"default-s.png"}, "active":"true", "discard":"false"},
        {"id":"1", "video":"abcd-v-1.mp4", "thumbnail":"abcd-v-t-1.png", "cover":"abcd-v-c-1.png", "original":"abcd-v-o-1.png", "still":{"10":"abcd-s-1-1.png", "20":"abcd-s-1-2.png"}, "active":"false", "discard":"false"},
        {"id":"2", "video":"abcd-v-2.mp4", "thumbnail":"abcd-v-t-2.png", "cover":"abcd-v-c-2.png", "original":"abcd-v-o-2.png", "still":{"10":"abcd-s-2-1.png", "20":"abcd-s-2-2.png"}, "active":"false", "discard":"false"},
        ]
        스틸이미지는 dictionary 형태로 시간값을 키값으로, 이미지패쓰를 밸류값으로 가진다.
        abcd == hashcode
"""
DEFAULT_LIST_DICT_VIDEO_ALBUM = [{"id":0, "video":"default.mp4", "original":"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "still":[{"time":1, "path":"default-s.png"}], "active":"true", "discard":"false"}]

class Video_Album(models.Model):
    main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    list_dict_picture_album = models.JSONField(null=True, blank=True)
    list_dict_video_album = models.JSONField(null=True, blank=True)
    code = models.CharField(max_length=250, null=True, blank=True)
    studio = models.CharField(max_length=250, null=True, blank=True)
    score = models.FloatField(default=0)
    tags = models.JSONField(null=True, blank=True) # Collect tags from LIST_ACTOR_TAGS
    date_released = models.DateField(null=True, blank=True)
    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} Video_Album'



"""
list_dict_video_album rule:
[
{"id":"0", "music":"abcd-1-m.mp3", "thumbnail":"default-t.png", "cover":"default-c.png", "original":"default-o.png", "lyrics":"default-l.txt" "active":"false", "discard":"false"},
{"id":"1", "music":"abcd-m-1.mp3", "thumbnail":"abcd-t-1.png", "cover":"abcd-c-1.png", "original":"abcd-o-1.png", "lyrics":"abcd-l-1.txt", "active":"true", "discard":"false"},
{"id":"2", "music":"abcd-m-2.mp3", "thumbnail":"abcd-t-2.png", "cover":"abcd-c-2.png", "original":"abcd-o-2.png", "lyrics":"abcd-l-2.txt", "active":"false", "discard":"false"},
]
abcd == hashcode
"""

DEFAULT_LIST_DICT_MUSIC_ALBUM = [{'id':0, "music":"default.mp3", "original":"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "active":"true", "discard":"false", "discard":"false"}]

class Music_Album(models.Model):
    main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    list_dict_picture_album = models.JSONField(null=True, blank=True)
    list_dict_video_album = models.JSONField(null=True, blank=True)
    list_dict_music_album = models.JSONField(null=True, blank=True)
    code = models.CharField(max_length=250, null=True, blank=True)
    studio = models.CharField(max_length=250, null=True, blank=True)
    score = models.FloatField(default=0)
    tags = models.JSONField(null=True, blank=True) # Collect tags from LIST_ACTOR_TAGS
    date_released = models.DateField(null=True, blank=True)
    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} Music_Album'




class MySettings_HansEnt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    menu_selected = models.CharField(choices=LIST_MENU_HANS_ENT, default=LIST_MENU_HANS_ENT[0][0], blank=True)
    # actor
    actor_selected = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    selected_field_actor = models.CharField(max_length=50, default=LIST_ACTOR_FIELD[0], blank=True)
    check_field_ascending_actor = models.BooleanField(default=True)
    count_page_number_actor = models.IntegerField(default=1)
    list_searched_actor_id = models.JSONField(null=True, blank=True)
    # picture
    picture_album_selected = models.ForeignKey(Picture_Album, on_delete=models.SET_NULL, null=True, blank=True)
    selected_field_picture = models.CharField(max_length=50, default=LIST_PICTURE_FIELD[0], blank=True)
    check_field_ascending_picture = models.BooleanField(default=True)
    count_page_number_picture = models.IntegerField(default=1)
    list_searched_picture_album_id = models.JSONField(null=True, blank=True)
    # video
    video_album_selected = models.ForeignKey(Video_Album, on_delete=models.SET_NULL, null=True, blank=True)
    selected_field_video = models.CharField(max_length=50, default=LIST_VIDEO_FIELD[0], blank=True)
    check_field_ascending_video = models.BooleanField(default=True)
    count_page_number_video = models.IntegerField(default=1)
    list_searched_video_album_id = models.JSONField(null=True, blank=True)
    # music
    music_album_selected = models.ForeignKey(Music_Album, on_delete=models.SET_NULL, null=True, blank=True)
    selected_field_music = models.CharField(max_length=50, default=LIST_MUSIC_FIELD[0], blank=True)
    check_field_ascending_music = models.BooleanField(default=True)
    count_page_number_music = models.IntegerField(default=1)
    list_searched_music_album_id = models.JSONField(null=True, blank=True)
    # system
    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} MySettings_HansEnt'


