from django.db import models
from django.contrib.auth.models import User 
from django.core.validators import FileExtensionValidator 



LIST_VAULT = ['vault1', 'vault2', 'vault3', 'vault4', 'vault5', 'vault6']
    
# LIST_VAULT = (
#     ('01', 'vault1'),
#     ('02', 'vault2'),
#     ('03', 'vault3'),
#     ('04', 'vault4'),
#     ('05', 'vault5'),
#     ('06', 'vault6'),
# )

LIST_ACTOR_CATEGORY = (
    ('00', 'ALL'),
    ('01', 'ENTERTAINER'),
    ('02', 'SINGER'),
    ('04', 'ACTOR'),
    ('05', 'ACTOR_ADULT'),
    ('06', 'AMATUER'),
    ('07', 'AMATUER_ADULT'),
    ('08', 'MODEL'),
    ('09', 'MODEL_ADULT'), # 화보 모델, 맥심 모델
    ('10', 'SNS'),  # 관종
    ('11', 'BJ'), 
    ('12', 'PRIVITE'), # 개인소장 
    ('13', 'AI'), # 개인소장 

    ('15', 'DIRECTOR'),
    ('16', 'WRITER'),
    ('17', 'LECTURER'),
    ('19', 'ETC'),
)
LIST_PICTURE_CATEGORY = (
    ('00', 'ALL'),
    ('01', '일상사진'),
    ('02', '일반화보'),
    ('03', '성인화보'),
    ('04', '일반기타'),
    ('05', '성인기타'),
)
LIST_MANGA_CATEGORY = (
    ('00', 'ALL'),
    ('01', '국내성인'),
    ('02', '국내일반'),
    ('03', '해외성인'),
    ('04', '해외일반'),
    ('05', 'ETC'),
)
LIST_VIDEO_CATEGORY = (
    ('00', 'ALL'),
    ('01', 'ENTERTAINMENT'),
    ('02', 'STUDY'),
    ('03', 'MOVIE'),
    ('04', 'DRAMA'),
    ('04', 'MUSIC'),
    ('05', 'DOCUMENTARY'),
    ('06', 'ADULT'),
    ('07', 'VR'),
    ('08', 'ETC'),
)
LIST_MUSIC_CATEGORY = (
    ('00', 'ALL'),
    ('01', 'KPOP'),
    ('02', 'POP'),
    ('03', 'CLASSIC'),
    ('04', 'JAZZ'),
    ('05', 'ETC'),
)


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


LIST_MENU_HANS_ENT = (
    ('01', 'ACTOR'),
    ('02', 'PICTURE'),
    ('03', 'MANGA'),
    ('04', 'VIDEO'),
    ('05', 'MUSIC'),
)

BASE_DIR_ACTOR = '/media/vault1/actor/'
BASE_DIR_PICTURE = '/media/vault1/picture/'
BASE_DIR_MANGA = '/media/vault1/manga/'
BASE_DIR_VIDEO = '/media/vault1/video/'
BASE_DIR_MUSIC = '/media/vault1/music/'

RELATIVE_PATH_ACTOR = 'vault1/actor/'
RELATIVE_PATH_PICTURE = 'vault1/picture/'
RELATIVE_PATH_PICTURE_TEMP = 'vault1/picture/temp/'
RELATIVE_PATH_MANGA = 'vault1/manga/'
RELATIVE_PATH_VIDEO = 'vault1/video/'
RELATIVE_PATH_MUSIC = 'vault1/music/'


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

LIST_DEFAULT_IMAGES = ['default-c.png', 'default-o.png', 'default-s.png', 'default-t.png']

LIST_NUM_DISPLAY_IN_PAGE = 100
LIST_ACTOR_SORTING_FIELD = ["id", "name", "age", "locations", "score", "date_updated"]
LIST_PICTURE_SORTING_FIELD = ["id", "title", "code", "studio", "score", "date_released"]
LIST_MANGA_SORTING_FIELD = ["id", "title", "score", "date_released"]
LIST_VIDEO_SORTING_FIELD = ["id", "title", "code", "studio", "score", "date_released"]
LIST_MUSIC_SORTING_FIELD = ["id", "title", "code", "studio", "score", "date_released"]


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
{"id":"0", "thumbnail":"default_actor-t.png", "cover":"default_actor-c.png", "original":"default_actor-o.png", "active":"false", "discard":"true},
{"id":"1", "thumbnail":"abcd-t-1.png", "cover":"abcd-c-1.png", "original":"abcd-o-1.png", "active":"false", "discard":"false"},
{"id":"2", "thumbnail":"abcd-t-2.png", "cover":"abcd-c-2.png", "original":"abcd-o-2.png", "active":"true", "discard":"false"},
]
abcd == hashcode
"""
DEFAULT_DICT_ACTOR_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
DEFAULT_LIST_DICT_PROFILE_ALBUM = [{'id':0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "active":"true", "discard":"false", "source": "none"}]  # Source는 이미지 Original 파일을 사용
DEFAULT_DICT_SCORE_HISTORY_ACTOR = {"favorite": "false", "rating": 0, "favorite_sum": 0, "total_visit_album": 0, "user_multiple": 1 }

LIST_DICT_SITE_ACTOR_INFO = [
    {'id': 0, 'key': 'blank', 'name': '선택안함', 'url': 'null'},
    {'id': 1, 'key': 'namuwiki', 'name': '나무위키', 'url': 'https://namu.wiki/'}, 
    {'id': 2, 'key': 'wikipedia','name': '위키백과', 'url': 'https://ko.wikipedia.org/'}, 
    {'id': 3, 'key': 'javdatabase','name': 'JAV Database', 'url': 'https://www.javdatabase.com/'},
    {'id': 4, 'key': 'iafd','name': 'Int Adult Film DB', 'url': 'https://www.iafd.com/'},
    {'id': 5, 'key': 'instagram', 'name': '인스타그램', 'url': 'https://www.instagram.com/'},
    {'id': 6, 'key': 'fantrie', 'name': '팬트리', 'url': 'https://fantrie.com/'},
    {'id': 7, 'key': 'onlyfans', 'name': '온리팬스', 'url': 'https://www.onlyfans.com/'},
]

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
    category = models.CharField(max_length=50, choices=LIST_ACTOR_CATEGORY, default=LIST_ACTOR_CATEGORY[0][0], null=True, blank=True) 
    age = models.IntegerField(null=True, blank=True)
    date_birth = models.DateField(null=True, blank=True)
    locations = models.CharField(max_length=50, choices=LIST_LOCATIONS, default=LIST_LOCATIONS[0][0], blank=True) # Submenu Switching
    height = models.IntegerField(null=True, blank=True)
    dict_score_history = models.JSONField(null=True, blank=True)
    score = models.FloatField(default=0)
    rating = models.IntegerField(default=0)
    tags = models.JSONField(null=True, blank=True) # Collect tags from LIST_ACTOR_TAGS
    # 
    dict_actor_album_cover = models.JSONField(null=True, blank=True)
    list_dict_info_url =  models.JSONField(null=True, blank=True) # [{"name":'imdb', "site":'https://www.imbd.com/xxx'}, {}]
    list_dict_profile_album = models.JSONField(null=True, blank=True) # list_dict_profile_album rule 참고

    # system
    date_created = models.DateField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)
    selected_vault = models.CharField(max_length=50, default=LIST_VAULT[0], blank=True)
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
DEFAULT_DICT_PICTURE_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
DEFAULT_LIST_DICT_PICTURE_ALBUM = [{'id':0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "file_size":"unknown", "image_size":[],"active":"true", "discard":"false"}]
DEFAULT_DICT_SCORE_HISTORY_PICTURE = {"favorite": "false", "rating": 0, "total_visit_album": 0, "user_multiple": 1 }
LIST_PICTURE_EXTENSION = ['jpg', 'jpeg', 'png', 'webp', 'gif']

class Picture_Album(models.Model):
    main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    category = models.CharField(max_length=50, choices=LIST_PICTURE_CATEGORY, default=LIST_PICTURE_CATEGORY[0][0], null=True, blank=True) 
    code = models.CharField(max_length=250, null=True, blank=True)
    studio = models.CharField(max_length=250, null=True, blank=True)
    tags = models.JSONField(null=True, blank=True) # Collect tags from LIST_ACTOR_TAGS

    dict_picture_album_cover = models.JSONField(null=True, blank=True)              # 앨범 커버 이미지 주소 저장 (사용안함. 나중에 삭제)
    list_dict_picture_album = models.JSONField(null=True, blank=True)               # 다운받은 이미지 Hashcode 기반 이미지 주소 리스트 (active == True이면 대문에 사용)
    dict_gallery_info = models.JSONField(null=True, blank=True)                     # 웹 갤러리 title 및 갤러리 url 저장 {'title': 'title_xxx', 'url':'gallery_url'}
    list_picture_url_album = models.JSONField(null=True, blank=True)                # 웹 갤러리에서 추출한 각 이미지 주소 리스트 저장
    
    picture_download_url = models.CharField(max_length=250, null=True, blank=True)  # TeraBox 등의 고해상도 이미지 다운받는 사이트 url 
    list_dict_info_url =  models.JSONField(null=True, blank=True)                   # 앨범 관련 정보 URL [{"name":'imdb', "site":'https://www.imbd.com/xxx'}, {}]
    
    check_url_downloaded = models.BooleanField(default=False)                       # 갤러리 이미지 주소(4KHD)를 다운받았는지 체크
    check_4k_downloaded = models.BooleanField(default=False)                        # 갤러리 이미지(4KHD)를 다운받았는지 체크
    check_4k_uploaded = models.BooleanField(default=False)                          # 고해상도 이미지(Terabox)를 업로드 했는지 체크

    list_dict_related_album = models.JSONField(null=True, blank=True)
    list_dict_related_actor = models.JSONField(null=True, blank=True)
    
    dict_score_history = models.JSONField(null=True, blank=True)
    score = models.FloatField(default=0)
    rating = models.IntegerField(default=0) # Star 개수, 1 ~ 5 까지 Favorite 점수 줄 수 있음.
    
    date_released = models.DateField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True, null=True)
    selected_vault = models.CharField(max_length=50, default=LIST_VAULT[0], blank=True)
    check_discard = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.title} Picture_Album'

DEFAULT_DICT_MANGA_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
DEFAULT_LIST_DICT_MANGA_ALBUM = [{'id':0, 'volume': 0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "active":"true", "discard":"false"}]
DEFAULT_LIST_DICT_VOLUME_MANGA_INFO = [{"volume": 0, "title": "None", "date_released": "unknown", "list_id": [], "last": "true", "favorite":"false", "discard": "false"}]
DEFAULT_DICT_SCORE_HISTORY_MANGA = {"favorite_sum": 0, "total_visit_album": 0, "user_multiple": 1 }

class Manga_Album(models.Model):
    main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    id_manga = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    category = models.CharField(max_length=50, choices=LIST_MANGA_CATEGORY, default=LIST_MANGA_CATEGORY[0][0], null=True, blank=True) 
    dict_manga_album_cover = models.JSONField(null=True, blank=True)
    list_dict_manga_album = models.JSONField(null=True, blank=True)
    list_dict_volume_manga = models.JSONField(null=True, blank=True)
    list_dict_info_url =  models.JSONField(null=True, blank=True) # [{"name":'imdb', "site":'https://www.imbd.com/xxx'}, {}]
    list_dict_related_album = models.JSONField(null=True, blank=True)
    list_dict_related_actor = models.JSONField(null=True, blank=True)
    last_volume = models.IntegerField(default=0)  # 최근호 볼륨 정보 기입
    studio = models.CharField(max_length=250, null=True, blank=True)
    dict_score_history = models.JSONField(null=True, blank=True)
    score = models.FloatField(default=0)
    rating = models.IntegerField(default=0)
    check_new_volume = models.BooleanField(default=False)
    check_completed = models.BooleanField(default=False)
    tags = models.JSONField(null=True, blank=True) # Collect tags from LIST_ACTOR_TAGS
    date_released = models.DateField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True, null=True)
    selected_vault = models.CharField(max_length=50, default=LIST_VAULT[0], blank=True)
    check_discard = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.title} Manga_Album'


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
# DEFAULT_DICT_VIDEO_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
# DEFAULT_LIST_DICT_VIDEO_ALBUM = [{"id":0, "video":"default.mp4", "original":"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "still":[{"time":1, "path":"default-s.png"}], "active":"true", "discard":"false"}]
# DEFAULT_DICT_SCORE_HISTORY_VIDEO = {"favorite_sum": 0, "total_visit_album": 0, "user_multiple": 1 }

DEFAULT_DICT_VIDEO_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
DEFAULT_LIST_DICT_PICTURE_ALBUM = [{'id':0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "file_size":"unknown", "image_size":[],"active":"true", "discard":"false", "streaming":"false"}]
DEFAULT_LIST_DICT_VIDEO_ALBUM = [{"id":0, "video":"default.mp4", "original":"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "still":[{"time":1, "path":"default-s.png"}], "active":"true", "discard":"false", "streaming":"false"}]
DEFAULT_DICT_SCORE_HISTORY_VIDEO = {"favorite_sum": 0, "total_visit_album": 0, "user_multiple": 1 }

LIST_DICT_SITE_VIDEO_INFO = [
    {'id': 0, 'key': 'blank', 'name': '선택안함', 'url': 'null'},
    {'id': 1, 'key': 'namuwiki', 'name': '나무위키', 'url': 'https://namu.wiki/'}, 
    {'id': 2, 'key': 'wikipedia','name': '위키백과', 'url': 'https://ko.wikipedia.org/'}, 
    {'id': 3, 'key': 'imbd','name': 'IMBD', 'url': 'https://www.imdb.com/'},
    {'id': 4, 'key': 'iafd','name': 'Int Adult Film DB', 'url': 'https://www.iafd.com/'},
    {'id': 5, 'key': 'navertv', 'name': '네이버 TV', 'url': 'https://tv.naver.com/'},
]
LIST_VIDEO_EXTENSION = ['mp4', 'avi', 'wmv', 'kmv', 'mpg', 'mpeg', 'ts']

class Video_Album(models.Model):
    main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    category = models.CharField(max_length=50, choices=LIST_VIDEO_CATEGORY, default=LIST_VIDEO_CATEGORY[0][0], null=True, blank=True) 
    dict_video_album_cover = models.JSONField(null=True, blank=True) # 커버사진 정보만
    list_dict_picture_album = models.JSONField(null=True, blank=True)
    list_dict_video_album = models.JSONField(null=True, blank=True)
    list_dict_info_url =  models.JSONField(null=True, blank=True) # 스크래핑으로 긁어모은 정보들
    list_dict_related_album = models.JSONField(null=True, blank=True)
    list_dict_related_actor = models.JSONField(null=True, blank=True)
    code = models.CharField(max_length=250, null=True, blank=True)
    studio = models.CharField(max_length=250, null=True, blank=True)
    dict_score_history = models.JSONField(null=True, blank=True)
    score = models.FloatField(default=0)
    rating = models.IntegerField(default=0)
    tags = models.JSONField(null=True, blank=True) # Collect tags from LIST_ACTOR_TAGS
    check_uploaded = models.BooleanField(default=False)   # Video 파일이 DB에 업로드 되었는가? 아니면 스크래핑된 정보만 들어있는가?
    date_released = models.DateField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True, null=True)
    selected_vault = models.CharField(max_length=50, default=LIST_VAULT[0], blank=True)
    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} Video_Album'


"""
list_dict_video_album rule:
[
{"id":"0", "audio":"abcd-1-m.mp3", "thumbnail":"default-t.png", "cover":"default-c.png", "original":"default-o.png", "lyrics":"default-l.txt" "active":"false", "discard":"false"},
{"id":"1", "audio":"abcd-m-1.mp3", "thumbnail":"abcd-t-1.png", "cover":"abcd-c-1.png", "original":"abcd-o-1.png", "lyrics":"abcd-l-1.txt", "active":"true", "discard":"false"},
{"id":"2", "audio":"abcd-m-2.mp3", "thumbnail":"abcd-t-2.png", "cover":"abcd-c-2.png", "original":"abcd-o-2.png", "lyrics":"abcd-l-2.txt", "active":"false", "discard":"false"},
]
abcd == hashcode
"""
DEFAULT_DICT_MUSIC_ALBUM_COVER = {'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png"}
DEFAULT_LIST_DICT_MUSIC_ALBUM = [{'id':0, "source":"default.mp3", "original":"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "active":"true", "discard":"false", "discard":"false"}]
LIST_AUDIO_FILE_EXTENSIONS = ['mp3', 'mpeg', 'opus', 'ogg', 'oga', 'wav', 'aac', 'caf', 'm4a', 'mp4', 'weba', 'webm', 'dolby', 'flac']
DEFAULT_DICT_SCORE_HISTORY_MUSIC = {"favorite_sum": 0, "total_visit_album": 0, "user_multiple": 1 }

class Music_Album(models.Model):
    main_actor = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    hashcode = models.CharField(max_length=250, null=True, blank=True)  # hash code = str(random_uuid), random_uuid = uuid.uuid4()
    category = models.CharField(max_length=50, choices=LIST_MUSIC_CATEGORY, default=LIST_MUSIC_CATEGORY[0][0], null=True, blank=True) 
    list_dict_picture_album = models.JSONField(null=True, blank=True)
    # list_dict_video_album = models.JSONField(null=True, blank=True)
    dict_music_album_cover = models.JSONField(null=True, blank=True)
    list_dict_music_album = models.JSONField(null=True, blank=True)
    list_dict_info_url =  models.JSONField(null=True, blank=True) # [{"name":'imdb', "site":'https://www.imbd.com/xxx'}, {}]
    list_dict_related_album = models.JSONField(null=True, blank=True)
    list_dict_related_actor = models.JSONField(null=True, blank=True)
    code = models.CharField(max_length=250, null=True, blank=True)
    studio = models.CharField(max_length=250, null=True, blank=True)
    dict_score_history = models.JSONField(null=True, blank=True)
    score = models.FloatField(default=0)
    rating = models.IntegerField(default=0)
    tags = models.JSONField(null=True, blank=True) # Collect tags from LIST_ACTOR_TAGS
    date_released = models.DateField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True, null=True)
    selected_vault = models.CharField(max_length=50, default=LIST_VAULT[0], blank=True)
    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} Music_Album'




class MySettings_HansEnt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    menu_selected = models.CharField(choices=LIST_MENU_HANS_ENT, default=LIST_MENU_HANS_ENT[0][0], blank=True)
    # actor
    actor_selected = models.ForeignKey(Actor, on_delete=models.SET_NULL, null=True, blank=True)
    selected_category_actor = models.CharField(max_length=50, choices=LIST_ACTOR_CATEGORY, default=LIST_ACTOR_CATEGORY[0][0], blank=True)
    selected_field_actor = models.CharField(max_length=50, default=LIST_ACTOR_SORTING_FIELD[0], blank=True)
    check_field_ascending_actor = models.BooleanField(default=True)
    count_page_number_actor = models.IntegerField(default=1)
    list_searched_actor_id = models.JSONField(null=True, blank=True)
    # picture
    picture_album_selected = models.ForeignKey(Picture_Album, on_delete=models.SET_NULL, null=True, blank=True)
    selected_category_picture = models.CharField(max_length=50, choices=LIST_PICTURE_CATEGORY, default=LIST_PICTURE_CATEGORY[0][0], blank=True)
    selected_field_picture = models.CharField(max_length=50, default=LIST_PICTURE_SORTING_FIELD[0], blank=True)
    check_field_ascending_picture = models.BooleanField(default=True)
    count_page_number_picture = models.IntegerField(default=1)
    list_searched_picture_album_id = models.JSONField(null=True, blank=True)
    # manga
    manga_album_selected = models.ForeignKey(Manga_Album, on_delete=models.SET_NULL, null=True, blank=True)
    selected_category_manga = models.CharField(max_length=50, choices=LIST_MANGA_CATEGORY, default=LIST_MANGA_CATEGORY[0][0], blank=True)
    selected_field_manga = models.CharField(max_length=50, default=LIST_MANGA_SORTING_FIELD[0], blank=True)
    check_field_ascending_manga = models.BooleanField(default=True)
    count_page_number_manga = models.IntegerField(default=1)
    list_searched_manga_album_id = models.JSONField(null=True, blank=True)
    list_manga_album_my_bookmark = models.JSONField(null=True, blank=True)  # [{'id': 123, 'id_manga': '4223', 'title': 'S수업', 'volume': 32}]
    check_switch_manga_complete_hide = models.BooleanField(default=False)
    check_switch_manga_new_volume_update_only = models.BooleanField(default=False)

    # video
    video_album_selected = models.ForeignKey(Video_Album, on_delete=models.SET_NULL, null=True, blank=True)
    selected_category_video = models.CharField(max_length=50, choices=LIST_VIDEO_CATEGORY, default=LIST_VIDEO_CATEGORY[0][0], blank=True)
    selected_field_video = models.CharField(max_length=50, default=LIST_VIDEO_SORTING_FIELD[0], blank=True)
    check_field_ascending_video = models.BooleanField(default=True)
    count_page_number_video = models.IntegerField(default=1)
    list_searched_video_album_id = models.JSONField(null=True, blank=True)
    # music
    music_album_selected = models.ForeignKey(Music_Album, on_delete=models.SET_NULL, null=True, blank=True)
    selected_category_music = models.CharField(max_length=50, choices=LIST_MUSIC_CATEGORY, default=LIST_MUSIC_CATEGORY[0][0], blank=True)
    selected_field_music = models.CharField(max_length=50, default=LIST_MUSIC_SORTING_FIELD[0], blank=True)
    check_field_ascending_music = models.BooleanField(default=True)
    count_page_number_music = models.IntegerField(default=1)
    list_searched_music_album_id = models.JSONField(null=True, blank=True)
    
    check_music_player_expand = models.BooleanField(default=False)
    check_audio_is_playing_now = models.BooleanField(default=False)
    check_shuffle_play_activated = models.BooleanField(default=False)
    check_loop_play_activated = models.BooleanField(default=False)
    check_repeat_play_activated = models.BooleanField(default=False)
    check_favorite_play_activated = models.BooleanField(default=False)
    check_background_play_activated = models.BooleanField(default=False)

    # system
    check_discard = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} MySettings_HansEnt'


class SystemSettings_HansEnt(models.Model):
    list_dict_nationality = models.JSONField(null=True, blank=True)  # [{'name': 'korea', 'path': 'xxx.jpg':}]

    # Scraping Picture
    selected_picture_album_id = models.IntegerField(null=True, blank=True)
    list_dict_report_error_picture = models.JSONField(null=True, blank=True)
    parsing_picture_start_page_reverse_count = models.IntegerField(default=1)
    list_done_cover_resize_id = models.JSONField(null=True, blank=True)
    parsing_picture_end_page_4khd = models.IntegerField(default=713)
    list_picture_id_parsing_error = models.JSONField(null=True, blank=True)  # parsing 갤러리 url 주소는 있는데 갤러리 주소로부터 image url 파싱 실패한 경우.
    dict_gallery_info_for_crawling_image_url = models.JSONField(null=True, blank=True)
    
    # scraping Manga
    parsing_base_url_manga = models.CharField(max_length=250, null=True, blank=True)
    parsing_cover_img_url_manga = models.CharField(max_length=250, null=True, blank=True)
    
    # {"id": 71558, "title": "S수업", "completed": "true", "last_volume": 32, "check_new_volume": false},
    list_dict_manga_info_for_parsing = models.JSONField(null=True, blank=True)  
    list_dict_report_error_manga = models.JSONField(null=True, blank=True)

    # scraping Javdatabase
    parsing_movie_page_completed = models.IntegerField(default=1)

    # Storage Check
    list_dict_stoage_status = models.JSONField(null=True, blank=True)
    selected_vault = models.CharField(max_length=50, default=LIST_VAULT[0], blank=True)

    check_discard = models.BooleanField(default=False)


