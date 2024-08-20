import uuid
import os
import io
import cv2

from pathlib import Path
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from hans_ent.models import *



#############################################################################################################################################
#############################################################################################################################################
#
#                                                       공통
#
#############################################################################################################################################
#############################################################################################################################################


def count_page_number_down(request, q_mysettings_hansent):
    print('min')
    menu_selected = q_mysettings_hansent.menu_selected
    count_page_number_str = request.POST.get('count_page_number')
    count_page_number = int(count_page_number_str)
    if count_page_number is not None and count_page_number > 1:
        count_page_number = int(count_page_number)
        if menu_selected == LIST_MENU_HANS_ENT[0][0]:
            data = {'count_page_number_actor': count_page_number - 1}
        elif menu_selected == LIST_MENU_HANS_ENT[1][0]:
            data = {'count_page_number_picture': count_page_number - 1}
        elif menu_selected == LIST_MENU_HANS_ENT[2][0]:
            data = {'count_page_number_video': count_page_number - 1}
        MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
        q_mysettings_hansent.refresh_from_db()
    return True



def count_page_number_up(request, q_mysettings_hansent, total_num_registered_item):
    menu_selected = q_mysettings_hansent.menu_selected
    count_page_number_str = request.POST.get('count_page_number')
    count_page_number = int(count_page_number_str)
    count_page_number_max = total_num_registered_item // LIST_NUM_DISPLAY_IN_PAGE
    count_page_number_max = count_page_number_max + 1
    if count_page_number is not None and count_page_number < count_page_number_max:
        count_page_number = int(count_page_number)
        if menu_selected == LIST_MENU_HANS_ENT[0][0]:
            data = {'count_page_number_actor': count_page_number + 1}
        elif menu_selected == LIST_MENU_HANS_ENT[1][0]:
            data = {'count_page_number_picture': count_page_number + 1}
        elif menu_selected == LIST_MENU_HANS_ENT[2][0]:
            data = {'count_page_number_video': count_page_number + 1}
        MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
        q_mysettings_hansent.refresh_from_db()
    return True



def hashcode_generator():
    # Generate a random UUID
    random_uuid = uuid.uuid4()
    # Convert it to a string (this will give you a 32-character hexadecimal string)
    hash_code = str(random_uuid)
    print("UUID4 Hash:", hash_code)
    return hash_code

#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Hans Ent
#
#############################################################################################################################################
#############################################################################################################################################

# Mysettings Reset하기
def reset_hans_ent_actor_list(q_mysettings_hansent):
    data = {
        'actor_selected': None,
        # 'actor_pic_selected': None,
        'selected_field_actor': LIST_ACTOR_FIELD[0],
        'check_field_ascending_actor': True,
        'count_page_number_actor': 1,
        'list_searched_actor_id': None,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    return True

def reset_hans_ent_picture_album_list(q_mysettings_hansent):
    data = {
        'picture_album_selected': None,
        'selected_field_picture': LIST_PICTURE_FIELD[0],
        'check_field_ascending_picture': True,
        'count_page_number_picture': 1,
        'list_searched_picture_album_id': None,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    return True

def reset_hans_ent_video_album_list(q_mysettings_hansent):
    data = {
        'video_album_selected': None,
        'selected_field_video': LIST_VIDEO_FIELD[0],
        'check_field_ascending_video': True,
        'count_page_number_video': 1,
        'list_searched_video_album_id': None,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    return True

def reset_hans_ent_music_album_list(q_mysettings_hansent):
    data = {
        'music_album_selected': None,
        'selected_field_music': LIST_MUSIC_FIELD[0],
        'check_field_ascending_music': True,
        'count_page_number_music': 1,
        'list_searched_music_album_id': None,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    return True




# Default 배우 쿼리 생성
def create_actor():
    hashcode = hashcode_generator()
    data = {
        'hashcode': hashcode,
        'list_dict_profile_album':DEFAULT_LIST_DICT_PROFILE_ALBUM,
    }
    q_actor = Actor.objects.create(**data)
    print('Actor 신규 생성!', q_actor)
    return q_actor

# Default Picture Album 쿼리 생성
def create_picture_album():
    hashcode = hashcode_generator()
    data = {
        'hashcode': hashcode,
        'list_dict_picture_album':DEFAULT_LIST_DICT_PICTURE_ALBUM,
    }
    q_picture_album = Picture_Album.objects.create(**data)
    print('Picture Album 신규 생성!', q_picture_album)
    return q_picture_album

# Default Video Album 쿼리 생성
def create_video_album():
    hashcode = hashcode_generator()
    data = {
        'hashcode': hashcode,
        'list_dict_picture_album':DEFAULT_LIST_DICT_PICTURE_ALBUM,
        'list_dict_video_album': DEFAULT_LIST_DICT_VIDEO_ALBUM,
    }
    q_video_album = Video_Album.objects.create(**data)
    print('Video Album 신규 생성!', q_video_album)
    return q_video_album

# Default Music Album 쿼리 생성
def create_music_album():
    hashcode = hashcode_generator()
    data = {
        'hashcode': hashcode,
        'list_dict_picture_album':DEFAULT_LIST_DICT_PICTURE_ALBUM,
        'list_dict_video_album': DEFAULT_LIST_DICT_VIDEO_ALBUM,
    }
    q_music_album = Music_Album.objects.create(**data)
    print('Music Album 신규 생성!', q_music_album)
    return q_music_album





# 두 배우 합치기
def merge_two_actor_into_one(q_actor, q_actor_s):
    hashcode = q_actor.hashcode
    hashcode_s = q_actor_s.hashcode
    synonyms = q_actor.synonyms
    date_birth = q_actor.date_birth 
    list_dict_info_url = q_actor.list_dict_info_url
    height = q_actor.height
    list_dict_profile_album = q_actor.list_dict_profile_album

    if synonyms is None:
        synonyms = []
    if list_dict_info_url is None:
        list_dict_info_url = []
    if list_dict_profile_album is None:
        list_dict_profile_album = []

    # 배우이름 합치기
    name_s = q_actor_s.name
    if name_s is not None:
        if name_s not in synonyms:
            synonyms.append(name_s)
    # 다른이름 합치기
    synonyms_s = q_actor_s.synonyms
    if synonyms_s is not None:
        for item in synonyms_s:
            if item not in synonyms:
                synonyms.append(item)
    # 생일 합치기
    if date_birth is None:
        date_birth_s = q_actor_s.date_birth
        if date_birth_s is not None:
            data_birth = date_birth_s
    # 배우정보사이트리스트 합치기
    list_dict_info_url_s = q_actor_s.list_dict_info_url
    if list_dict_info_url_s is not None:
        for item in list_dict_info_url_s:
            if item not in list_dict_info_url:
                list_dict_info_url.append(item)
    # 키 정보 합치기
    if height is None:
        height_s = q_actor_s.height
        if height_s is not None:
            height = height_s
    # 이미지 합치기 
    if list_dict_profile_album is not None:
        list_dict_profile_album_s = q_actor_s.list_dict_profile_album
        if list_dict_profile_album_s is not None:
            # 합쳐서 사라지는 쪽의 image hashcode를 남는쪽의 hashcode로 파일이름까지 변경해야 함.
            for dict_profile_album_s in list_dict_profile_album_s:
                # Find Path
                thumbnail_name_s = dict_profile_album_s["thumbnail"]
                thumbnail_name = thumbnail_name_s.replace(hashcode_s, hashcode)
                cover_name_s = dict_profile_album_s["cover"]
                cover_name = cover_name_s.replace(hashcode_s, hashcode)
                original_name_s = dict_profile_album_s["original"]
                original_name = original_name_s.replace(hashcode_s, hashcode)
                # Change File Path Name
                thumbnail_old_file = Path(f'{BASE_DIR_ACTOR}/{thumbnail_name_s}')
                thumbnail_new_file = Path(f'{BASE_DIR_ACTOR}/{thumbnail_name}')
                try:
                    os.rename(thumbnail_old_file, thumbnail_new_file)
                except FileNotFoundError:
                    print(f"Error: {thumbnail_old_file} not found.")
                cover_old_file = Path(f'{BASE_DIR_ACTOR}/{cover_name_s}')
                cover_new_file = Path(f'{BASE_DIR_ACTOR}/{cover_name}')
                try:
                    os.rename(cover_old_file, cover_new_file)
                except FileNotFoundError:
                    print(f"Error: {cover_old_file} not found.")
                original_old_file = Path(f'{BASE_DIR_ACTOR}/{original_name_s}')
                original_new_file = Path(f'{BASE_DIR_ACTOR}/{original_name}')
                try:
                    os.rename(original_old_file, original_new_file)
                except FileNotFoundError:
                    print(f"Error: {original_old_file} not found.")
                # List 업데이트
                list_dict_profile_album.appned({"thumbnail":thumbnail_name, "cover":cover_name, "original":original_name})
    # List turn None if no item in it.
    if len(synonyms) == 0:
        synonyms = None
    if len(list_dict_info_url) == 0:
        list_dict_info_url = None
    if len(list_dict_profile_album) == 0:
        list_dict_profile_album = None
    # Update Data
    data = {
        'synonyms': synonyms,
        'date_birth': date_birth,
        'height': height,
        'list_dict_info_url': list_dict_info_url,
        'list_dict_profile_album': list_dict_profile_album,
    }
    Actor.objects.filter(id=q_actor.id).update(**data)
    q_actor.refresh_from_db()
    return q_actor
    



# 이미지 저장하기
""" 
입력값은 PIL object. 그러면 알아서 커버이미지, 썸네일이미지 두가지 모두 출력
    PIL image, 
    커버이미지 == Landscape 비율
    썸네일이미지 == Portrait 비율
            
    Width	Height	Name
    640	    360	    nHD
    854	    480	    FWVGA
    960	    540	    qHD
    1024	576	    WSVGA
    1280	720	    HD
    1366	768	    FWXGA
    1600	900	    HD+
    1920	1080	Full HD
    2560	1440	QHD
    3200	1800	QHD+
    3840	2160	4K UHD
    5120	2880	5K
    7680	4320	8K UHD
"""

"""
    image naming $ size rules
    thumbnail image: hashcode-t.xxx  // size: 260px by 320px
    cover image: hashcode-c.xxx  // size: 520px by 640px
    original image: hashcode-o.xxx  // size: 그대로
    still image: hashcode-s-<order number>.xxx  // size: 65px by 80px
"""    

def resize_with_padding(image, target_width, target_height):
    # Resize the image while maintaining aspect ratio
    color=(255, 255, 255)
    image.thumbnail((target_width, target_height))
    # Calculate padding
    width, height = image.size
    pad_width = (target_width - width) // 2
    pad_height = (target_height - height) // 2

    # Create a new image with the target size and specified background color
    new_image = Image.new("RGB", (target_width, target_height), color)

    # Paste the resized image onto the new image, centered
    new_image.paste(image, (pad_width, pad_height))
    return new_image

def resize_pil_image_for_cover_and_thumbnail_pil(img):
    
    resized_image_c = resize_with_padding(img, 520, 640)  # Target size: 300x300 with white background
    resized_image_t = resize_with_padding(img, 260, 320)  # Target size: 300x300 with white background

    # Get the original dimensions
    # original_width, original_height = img.size
    # original_max_size = max(original_width, original_height)
    # cover_output_image_size = (520, 640)
    # cover_max_size = 640
    # thumbnail_output_image_size = (260, 320)
    # thumbnail_max_size = 320
   


    # cover_img = img.resize((cover_new_width, cover_new_height), Image.Resampling.LANCZOS)
    # thumbnail_img = img.resize((thumbnail_new_width, thumbnail_new_height), Image.Resampling.LANCZOS)

    # # Calculate the scaling factor for width and height
    # cover_width_scale = cover_max_size / original_width
    # cover_height_scale = cover_max_size / original_height
    # thumbnail_width_scale = thumbnail_max_size / original_width
    # thumbnail_height_scale = thumbnail_max_size / original_height
    # # Choose the smaller of the two scales to maintain aspect ratio
    # cover_scale = min(cover_width_scale, cover_height_scale)
    # thumbnail_scale = min(thumbnail_width_scale, thumbnail_height_scale)
    # # Calculate the new dimensions
    # cover_new_width = int(original_width * cover_scale)
    # cover_new_height = int(original_height * cover_scale)
    # thumbnail_new_width = int(original_width * thumbnail_scale)
    # thumbnail_new_height = int(original_height * thumbnail_scale)
    # # Resize the image
    # cover_img = img.resize((cover_new_width, cover_new_height), Image.Resampling.LANCZOS)
    # thumbnail_img = img.resize((thumbnail_new_width, thumbnail_new_height), Image.Resampling.LANCZOS)

    # thumbnail_img_width, thumbnail_img_heigh = thumbnail_img.size
    # thumb_center_x = thumbnail_img_width / 2
    # thumb_center_y = thumbnail_img_heigh / 2
    # center_x = cover_output_image_size[0] / 2
    # center_y = cover_output_image_size[1] / 2
    # # Calculate cropping box coordinates for cover image
    # left = center_x - cover_output_image_size[0] / 2
    # top = center_y - cover_output_image_size[1] / 2
    # right = center_x + cover_output_image_size[0] / 2
    # bottom = center_y + cover_output_image_size[1] / 2
    # # Crop the image
    # cover_img = cover_img.crop((left, top, right, bottom))
    # # Calculate cropping box coordinates for thumbnail
    # left = thumb_center_x - thumbnail_output_image_size[0] / 2
    # top = thumb_center_y - thumbnail_output_image_size[1] / 2
    # right = thumb_center_x + thumbnail_output_image_size[0] / 2
    # bottom = thumb_center_y + thumbnail_output_image_size[1] / 2
    # # Crop the image
    # thumbnail_img = thumbnail_img.crop((left, top, right, bottom))
    return resized_image_c, resized_image_t

    
# 배우 갤러리 이미지/썸네일 저장하기
def save_actor_profile_images(q_actor, images):
    """
        이미지를 PIL 객체로 변환한 뒤
        편집을 수행
        원본사이즈 이미지 저장 
        사이즈 조정
        썸네일 저장
    """
    # reset active to false
    list_dict_profile_album = q_actor.list_dict_profile_album
    if list_dict_profile_album is not None and len(list_dict_profile_album) > 0:
        for dict_profile_album in list_dict_profile_album:
            dict_profile_album["active"] = "false"
        data = {
                'list_dict_profile_album': list_dict_profile_album,
        }
        Actor.objects.filter(id=q_actor.id).update(**data)
        q_actor.refresh_from_db()
    else:
        list_dict_profile_album = []
    num_profile_image = len(list_dict_profile_album)
    # get base info
    hashcode = q_actor.hashcode
    total_image_number = len(images)
    i = 0
    for image_file in images:   
        image_file_name = image_file.name
        file_extension = image_file_name.split('.')[-1]
        print('file_extension', file_extension)
        # convert file to PIL object
        image_pil = Image.open(image_file)
        # Remove Alpah channel befor saving
        image_pil = image_pil.convert('RGB')
        # 원본 이미지 저장
        image_name_original = f'{hashcode}-o-{num_profile_image}.{file_extension}'
        file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_original)
        image_pil.save(file_path)
        
        # Get Thumbnail, Cover size PIL objects
        cover_pil, thumbnail_pil = resize_pil_image_for_cover_and_thumbnail_pil(image_pil)
        # 커버이미지 저장
        image_name_cover = f'{hashcode}-c-{num_profile_image}.{file_extension}'
        file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_cover)
        cover_pil.save(file_path)
        # 썸네일 이미지 저장
        image_name_thumbnail = f'{hashcode}-t-{num_profile_image}.{file_extension}'
        file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_thumbnail)
        thumbnail_pil.save(file_path)
        # List 업데이트
        if total_image_number == i + 1:
            list_dict_profile_album.append({"id": num_profile_image, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"true", "discard":"false"})
        else:
            list_dict_profile_album.append({"id": num_profile_image, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false"})
        i = i + 1
        num_profile_image = num_profile_image + 1
    # default 이미지 discard 하기
    for dict_profile_album in list_dict_profile_album:
        if dict_profile_album["id"] == 0:
            dict_profile_album["active"] = 'false'
            dict_profile_album["discard"] = 'true'
    # db save and refresh  
    data = {
        'list_dict_profile_album': list_dict_profile_album,
    }
    Actor.objects.filter(id=q_actor.id).update(**data)
    q_actor.refresh_from_db()
    return list_dict_profile_album
    

# Picture Album 이미지/썸네일 저장하기
def save_picture_album_images(q_picture_album_selected, images):
    """
        Picture Album은
        active: true 이면 대문(커버) 이미지로 할당한다는 의미
        discard: true 이면 삭제한다는 의미
        id == number of items로 표시, 
        item 삭제시 파일은 삭제하고 리스트에서는 discard=true만 설정하고 item을 삭제하지는 않는다. ID 변경되지 않게 하려고
    """
    print('num of images', len(images))
    # reset active to false
    list_dict_picture_album = q_picture_album_selected.list_dict_picture_album
    if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
        for dict_picture_album in list_dict_picture_album:
            dict_picture_album["active"] = "false"
        data = {'list_dict_picture_album': list_dict_picture_album,}
        Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
        q_picture_album_selected.refresh_from_db()
    else:
        list_dict_picture_album = []
    num_picture_album_image = len(list_dict_picture_album)
    # get base info
    hashcode = q_picture_album_selected.hashcode
    if hashcode is None:
        hashcode = hashcode_generator()
        data = {'hashcode': hashcode}
        Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
        q_picture_album_selected.refresh_from_db()
    total_image_number = len(images)
    i = 0
    for image_file in images:   
        image_file_name = image_file.name
        file_extension = image_file_name.split('.')[-1]
        print('file_extension', file_extension)
        # convert file to PIL object
        image_pil = Image.open(image_file)
        # Remove Alpah channel befor saving
        image_pil = image_pil.convert('RGB')
        # 원본 이미지 저장
        image_name_original = f'{hashcode}-o-{num_picture_album_image}.{file_extension}'
        file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_original)
        image_pil.save(file_path)
        
        # Get Thumbnail, Cover size PIL objects
        cover_pil, thumbnail_pil = resize_pil_image_for_cover_and_thumbnail_pil(image_pil)
        # 커버이미지 저장
        image_name_cover = f'{hashcode}-c-{num_picture_album_image}.{file_extension}'
        file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
        cover_pil.save(file_path)
        # 썸네일 이미지 저장
        image_name_thumbnail = f'{hashcode}-t-{num_picture_album_image}.{file_extension}'
        file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)
        thumbnail_pil.save(file_path)
        # List 업데이트
        if total_image_number == i + 1:
            list_dict_picture_album.append({"id": num_picture_album_image, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"true", "discard":"false"})
        else:
            list_dict_picture_album.append({"id": num_picture_album_image, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false"})
        i = i + 1
        num_picture_album_image = num_picture_album_image + 1
    # default 이미지 discard 하기
    for dict_picture_album in list_dict_picture_album:
        if dict_picture_album["id"] == 0:
            dict_picture_album["active"] = 'false'
            dict_picture_album["discard"] = 'true'
    # db save and refresh  
    data = {
        'list_dict_picture_album': list_dict_picture_album,
    }
    Picture_Album.objects.filter(id=q_picture_album_selected.id).update(**data)
    q_picture_album_selected.refresh_from_db()
    return list_dict_picture_album
    




# Video Album 이미지/썸네일 저장하기
def save_video_album_images(q_video_album_selected, images):
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
        
        active: true 이면 대문(커버) 이미지로 할당한다는 의미
        discard: true 이면 삭제한다는 의미
        id == number of items로 표시, 
        item 삭제시 파일은 삭제하고 리스트에서는 discard=true만 설정하고 item을 삭제하지는 않는다. ID 변경되지 않게 하려고
    """
    print('num of images', len(images))
    # get base info
    hashcode = q_video_album_selected.hashcode
    if hashcode is None:
        hashcode = hashcode_generator()
        data = {'hashcode': hashcode}
        Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
        q_video_album_selected.refresh_from_db()
    # reset active to false
    list_dict_picture_album = q_video_album_selected.list_dict_picture_album
    if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
        for dict_picture_album in list_dict_picture_album:
            dict_picture_album["active"] = "false"
        data = {'list_dict_picture_album': list_dict_picture_album,}
        Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
        q_video_album_selected.refresh_from_db()
    else:
        list_dict_picture_album = []
    num_picture_album_image = len(list_dict_picture_album)
    total_image_number = len(images)
    i = 0
    for image_file in images:   
        image_file_name = image_file.name
        file_extension = image_file_name.split('.')[-1]
        print('file_extension', file_extension)
        # convert file to PIL object
        image_pil = Image.open(image_file)
        # Remove Alpah channel befor saving
        image_pil = image_pil.convert('RGB')
        # 원본 이미지 저장
        image_name_original = f'{hashcode}-o-{num_picture_album_image}.{file_extension}'
        file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_original)
        image_pil.save(file_path)
        
        # Get Thumbnail, Cover size PIL objects
        cover_pil, thumbnail_pil = resize_pil_image_for_cover_and_thumbnail_pil(image_pil)
        # 커버이미지 저장
        image_name_cover = f'{hashcode}-c-{num_picture_album_image}.{file_extension}'
        file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_cover)
        cover_pil.save(file_path)
        # 썸네일 이미지 저장
        image_name_thumbnail = f'{hashcode}-t-{num_picture_album_image}.{file_extension}'
        file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_thumbnail)
        thumbnail_pil.save(file_path)
        # List 업데이트
        if total_image_number == i + 1:
            list_dict_picture_album.append({"id": num_picture_album_image, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"true", "discard":"false"})
        else:
            list_dict_picture_album.append({"id": num_picture_album_image, "original":image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "active":"false", "discard":"false"})
        i = i + 1
        num_picture_album_image = num_picture_album_image + 1
    # default 이미지 discard 하기
    for dict_picture_album in list_dict_picture_album:
        if dict_picture_album["id"] == 0:
            dict_picture_album["active"] = 'false'
            dict_picture_album["discard"] = 'true'
    # db save and refresh  
    data = {
        'list_dict_picture_album': list_dict_picture_album,
    }
    Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
    q_video_album_selected.refresh_from_db()
    return True





# Video Album Video / Still image 저장하기
def save_video_album_videos(q_video_album_selected, videos):
    """
     Video Album은
        1개의 list_dict_picture_album과 1개의 list_dict_video_album 이 있음
        list_dict_video_album은 video들을 담당

        [
        {"id":"0", "video":"default.mp4", "thumbnail":"default-t.png", "still":[{"time":1, "path":"default-s.png"}], "active":"true", "discard":"false"},
        {"id":"1", "video":"abcd-v-1.mp4", "thumbnail":"abcd-v-t-1.png", "still":[{"time":10, "path":"abcd-s-1-1.png", "20":"abcd-s-1-2.png"}], "active":"false", "discard":"false"},
        {"id":"2", "video":"abcd-v-2.mp4", "thumbnail":"abcd-v-t-2.png", "still":[{"time":10, "path":"abcd-s-2-1.png", "20":"abcd-s-2-2.png"}], "active":"false", "discard":"false"},
        ]
        abcd == hashcode

        스틸이미지는 dictionary 형태로 시간값을 키값으로, 이미지패쓰를 밸류값으로 가진다.
    """
    # get base info
    hashcode = q_video_album_selected.hashcode
    if hashcode is None:
        hashcode = hashcode_generator()
        data = {'hashcode': hashcode}
        Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
        q_video_album_selected.refresh_from_db()
    # reset active to false
    list_dict_video_album = q_video_album_selected.list_dict_video_album
    if list_dict_video_album is not None and len(list_dict_video_album) > 0:
        for dict_video_album in list_dict_video_album:
            dict_video_album["active"] = "false"
        data = {'list_dict_video_album': list_dict_video_album,}
        Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
        q_video_album_selected.refresh_from_db()
    else:
        list_dict_video_album = []
    num_video_album_video = len(list_dict_video_album)
    total_video_number = len(videos)
    i = 0
    for video_file in videos:   
        video_file_name = video_file.name
        file_extension = video_file_name.split('.')[-1]
        print('file_extension', file_extension)

        # 원본 비디오 저장
        video_name_original = f'{hashcode}-v-{num_video_album_video}.{file_extension}'
        file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_name_original)
        with open(file_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        def still_image_save(j, unit_frame, hashcode, num_video_album_video):
            cap.set(cv2.CAP_PROP_POS_FRAMES, unit_frame*j)
            ret, frame = cap.read()
            if ret:
                # Save the frame as an image file
                video_still_path = f'{hashcode}-s-{num_video_album_video}-{j}.jpg'
                file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_still_path)
                cv2.imwrite(file_path, frame)
                return {"time":j, "path":video_still_path}
            else:
                return None
            
        # Still 이미지 확보
        list_still = []
        cap = cv2.VideoCapture(file_path)
        if cap.isOpened():
            list_frame_cut_still = []
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration_seconds = total_frames / fps

            if duration_seconds < 600: # 10 min under == 5 cut
                unit_frame = total_frames // 5
                j = 1
                while j < 6:
                    return_value = still_image_save(j, unit_frame, hashcode, num_video_album_video)
                    if return_value is not None:
                        list_still.append(return_value)
                    j = j + 1
            elif duration_seconds >= 600 and duration_seconds < 3000: # 10 ~ 30 min  == 10 cut
                unit_frame = total_frames // 10
                j = 1
                while j < 11:
                    return_value = still_image_save(j, unit_frame, hashcode, num_video_album_video)
                    if return_value is not None:
                        list_still.append(return_value)
                    j = j + 1
            elif duration_seconds >= 3000 and duration_seconds < 9000: # 30 ~ 90 min  == 15 cut
                unit_frame = total_frames // 15
                j = 1
                while j < 16:
                    return_value = still_image_save(j, unit_frame, hashcode, num_video_album_video)
                    if return_value is not None:
                        list_still.append(return_value)
                    j = j + 1
            else: # 90 min ~ Over == 20 cut
                unit_frame = total_frames // 20
                j = 1
                while j < 21:
                    return_value = still_image_save(j, unit_frame, hashcode, num_video_album_video)
                    if return_value is not None:
                        list_still.append(return_value)
                    j = j + 1
                
        # List 업데이트
        if total_video_number == i + 1:
            list_dict_video_album.append({"id": num_video_album_video, "video": video_name_original, "thumbnail":list_still[0]["path"], "still":list_still, "active":"true", "discard":"false"})
        else:
            list_dict_video_album.append({"id": num_video_album_video, "video": video_name_original, "thumbnail":list_still[0]["path"], "still":list_still, "active":"false", "discard":"false"})
        i = i + 1
        num_video_album_video = num_video_album_video + 1

    return True






# 스틸 이미지 사이즈 조절
def resize_still_image_file(img):
    output_image_size = (300, 200)
    max_size = 300
    # Get the original dimensions
    original_width, original_height = img.size
    # Calculate the scaling factor for width and height
    width_scale = max_size / original_width
    height_scale = max_size / original_height
    # Choose the smaller of the two scales to maintain aspect ratio
    scale = min(width_scale, height_scale)
    # Calculate the new dimensions
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    # Resize the image
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    bulky_resized_width, bulky_resized_height = img.size
    # Calculate the center coordinates
    center_x = bulky_resized_width / 2
    center_y = bulky_resized_height / 2
    # Calculate cropping box coordinates
    left = center_x - output_image_size[0] / 2
    top = center_y - output_image_size[1] / 2
    right = center_x + output_image_size[0] / 2
    bottom = center_y + output_image_size[1] / 2
    # Crop the image
    img = img.crop((left, top, right, bottom))
    print(img.size)
    return img


# 비디오 파일로부터 썸네일, 스틸 이미지 생성하기
def get_thumbnail_and_stillimages(q_vid, file_name):
    
    
    video_file_name = str(q_vid.video_file)
    video_file_name = video_file_name.split('/')[-1]
    video_file_path = os.path.join(VIDEO_FILE_DIR, video_file_name) 
    print('video_file_path', video_file_path)
    dict_still_image_path_interval = {}
    try:
        clips = VideoFileClip(video_file_path)
        print('clips', clips)
        
        frames = clips.reader.fps #frame per second
        duration = clips.duration # seconds
        print('duration', duration)
        max_duration = int(duration)+1
        if duration < 600:
            # < 10 min
            division = 5  
        else:
            if duration < 3600:
                # < 60 min
                division = 10
            else:
                if duration < 7200:
                    # < 120 min
                    division = 15
                else:  
                    # > 120 min
                    division = 20
        interval = max_duration // division
        i = 1
        while i < division + 1:
            print('i', i)
            interval_x = interval * i  
            print('interval_x', interval_x)
            frame = clips.get_frame(interval_x)

            # Still 이미지 저장하기(장고DB Filefield 저장하지 않고 모두 모아서 JsonField에 저장한다.)
            still_img_file_path = os.path.join(STILL_IMAGE_DIR, f"{q_vid.id}-still-{file_name}-{i}.jpg")
            new_still_pil  = Image.fromarray(frame) # Get still image from specific video frame
            # Remove Alpah channel befor saving
            new_still_pil = new_still_pil.convert('RGB')
            resized_still_pil = resize_still_image_file(new_still_pil)
            resized_still_pil.save(still_img_file_path)
            new_still_img_file_path = still_img_file_path.split('media/')[-1]
            dict_still_image_path_interval[i] = [new_still_img_file_path, interval_x]
            # print('dict_still_image_path', dict_still_image_path)

            # 비디오 중간지점에서 썸네일 하나 생성하기
            if (division + 1)//2 == i:
                print('# 비디오 중간지점에서 썸네일 하나 생성하기 시작')
                cover_img_file_path = os.path.join(COVER_IMAGE_DIR, f"{q_vid.id}-cover-{file_name}-{i}.jpg")
                thumbnail_img_file_path = os.path.join(THUMBNAIL_IMAGE_DIR, f"{q_vid.id}-thumbnail-{file_name}-{i}.jpg")
                
                new_frame_image = Image.fromarray(frame)
                new_frame_image = new_frame_image.convert('RGB')
                cover_pil, thumbnail_pil  = resize_pil_image_for_cover_and_thumbnail_pil(new_frame_image)

                # 커버이미지 및 썸네일 이미지 저장
                print('# 커버이미지 및 썸네일 이미지 저장', q_vid.image_cover, q_vid.image_thumbnail )
                image_cover_path = str(q_vid.image_cover)
                image_thumbnail_path = str(q_vid.image_thumbnail)
                if image_cover_path is None or image_cover_path == '':
                    print('# 커버이미지 저장')
                    cover_pil.save(cover_img_file_path)
                    new_cover_img_file_path = cover_img_file_path.split('media/')[-1]
                    data = {
                        'image_cover': new_cover_img_file_path,
                    }
                    Video_Album_Vid.objects.filter(id=q_vid.id).update(**data)
                    q_vid.refresh_from_db()

                if image_thumbnail_path is None or image_thumbnail_path == '':
                    print('# 썸네일 이미지 저장')
                    thumbnail_pil.save(thumbnail_img_file_path)
                    new_thumbnail_img_file_path = thumbnail_img_file_path.split('media/')[-1]
                    data = {
                        'image_thumbnail': new_thumbnail_img_file_path,
                    }
                    Video_Album_Vid.objects.filter(id=q_vid.id).update(**data)
                    q_vid.refresh_from_db()
            i = i + 1
    except:
        data = {
            'image_cover': NO_IMAGE_PATH,
            'image_thumbnail': NO_IMAGE_PATH,
        }
        Video_Album_Vid.objects.filter(id=q_vid.id).update(**data)
        q_vid.refresh_from_db()
        dict_still_image_path_interval = None

    data = {
        'list_still_image': dict_still_image_path_interval
    }
    print('list_still_image', dict_still_image_path_interval)
    Video_Album_Vid.objects.filter(id=q_vid.id).update(**data)
    return True

    
# Video Album Vidoe File 저장하기
def save_video_album_files_to_db(q_selected_video_album, videos):
    # BASE_DIR = settings.MEDIA_ROOT
    # BASE_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads") 
    # VIDEO_ALBUM_DIR = os.path.join(BASE_UPLOAD_DIR, "video_album") 
    # VIDEO_FILE_DIR = os.path.join(VIDEO_ALBUM_DIR, "video_files") 
    # SUBTITLE_FILE_DIR = os.path.join(VIDEO_ALBUM_DIR, "subtitle_files") 
    # COVER_IMAGE_DIR = os.path.join(VIDEO_ALBUM_DIR, "cover_images") 
    # THUMBNAIL_IMAGE_DIR = os.path.join(VIDEO_ALBUM_DIR, "thumbnail_images") 
    # STILL_IMAGE_DIR = os.path.join(VIDEO_ALBUM_DIR, "still_images") 

    # # 폴더 내 파일 이름 리스트화 및 동일파일이름 체크
    # list_album_file_name = []
    # file_names = os.listdir(VIDEO_FILE_DIR)
    # for file_name in file_names:
    #     list_album_file_name.append(file_name)

    title = q_selected_video_album.title
    actor_name = q_selected_video_album.actor_name

    list_dict_video_album = q_selected_video_album.list_dict_video_album
    if list_dict_video_album is not None and len(list_dict_video_album) > 0:
        for dict_video_album in list_dict_video_album:
            dict_video_album["active"] = "false"
        data = {'list_dict_video_album': list_dict_video_album,}
        Video_Album.objects.filter(id=q_selected_video_album.id).update(**data)
        q_selected_video_album.refresh_from_db()
    else:
        list_dict_video_album = []
    num_video_album_video = len(list_dict_video_album)
    # get base info
    # hashcode = q_selected_video_album.hashcode
    # if hashcode is None:
    #     hashcode = hashcode_generator()
    #     data = {'hashcode': hashcode}
    #     Video_Album.objects.filter(id=q_selected_video_album.id).update(**data)
    #     q_selected_video_album.refresh_from_db()
    
    total_video_number = len(videos)
    i = 0
    for file in videos:    
        if image_cover_path is None or image_cover_path == '':
            print('앨범에 커버 없음, 영상프레임에서 뽑아써야함')
            vid_image_cover = None
        else:
            print('앨범에 커버 있음, Vid에 재활용')
            vid_image_cover = q_selected_album.image_cover
            
        if image_thumbnail_path is None or image_thumbnail_path == '':
            print('앨범에 썸네일 없음, 영상프레임에서 뽑아써야함')
            vid_image_thumbnail = None
        else:
            print('앨범에 썸네일 있음, Vid에 재활용')
            vid_image_thumbnail = q_selected_album.image_thumbnail
            
        
    if image_cover_path is None or image_cover_path == '':
        print('앨범에 커버 없음, 영상프레임에서 뽑아써 저장하기')
        album_image_cover = q_vid.image_cover
    else:
        album_image_cover= q_selected_album.image_cover
    if image_thumbnail_path is None or image_thumbnail_path == '':
        print('앨범에 썸네일 없음, 영상프레임에서 뽑아써 저장하기')
        album_image_thumbnail = q_vid.image_thumbnail
    else:
        album_image_thumbnail= q_selected_album.image_thumbnail
    data = {
        'list_album_video_id': list_album_video_id,
        
    }
    Video_Album.objects.filter(id=q_selected_album.id).update(**data)
    q_selected_album.refresh_from_db()
    return q_selected_album
    
