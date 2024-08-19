import uuid
import os
import io
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
        'list_searched_picture_id': None,
    }
    MySettings_HansEnt.objects.filter(id=q_mysettings_hansent.id).update(**data)
    return True


def reset_hans_ent_video_album_list(q_mysettings_hansent):
    data = {
        'video_album_selected': None,
        'selected_field_video': LIST_VIDEO_FIELD[0],
        'check_field_ascending_video': True,
        'count_page_number_video': 1,
        'list_searched_video_id': None,
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
    # return True