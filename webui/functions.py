import uuid
import os
from pathlib import Path

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


# Default 배우 쿼리 생성
def create_actor():
    data = {}
    q_actor = Actor.objects.create(**data)
    print('Actor 신규 생성!', q_actor)
    return q_actor


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
    



    
# Album Image file => Original / Cover / Thumbnail 저장하기
def save_image_file_to_original_cover_and_thumbnail_images(q_xxx, image_file):
    """
    이미지를 PIL 객체로 변환한 뒤
    편집을 수행
    원본사이즈 이미지 저장 
    사이즈 조정
    썸네일 저장
    """
    print('# Album Image file => Original / Cover / Thumbnail 저장하기')
    print('q_xxx', q_xxx, type(q_xxx))
    print('image_file', image_file, type(image_file))
        
    if image_file is not None:
        image_file_name = image_file.name
        image_file_name_cleaned = file_name_cleaner(image_file_name)
        image_file.name = image_file_name_cleaned

        q_xxx_id_str = str(q_xxx.id)

        # PIL 객체 변환 및 편집
        image_pil = Image.open(image_file)
        # Remove Alpah channel befor saving
        image_pil = image_pil.convert('RGB')

        # PIL 객체로부터 Thumbnail, Cover 사이즈 PIL 객체 확보
        cover_pil, thumbnail_pil = resize_pil_image_for_cover_and_thumbnail_pil(image_pil)

        # 원본 이미지 저장
        image_io = io.BytesIO()
        image_pil.save(image_io, format='JPEG')
        image_name_original = f'{q_xxx_id_str}-original-{image_file_name_cleaned}'
        q_xxx.image_original.save(image_name_original, ContentFile(image_io.getvalue()), save=True)

        # 커버이미지 저장
        image_io = io.BytesIO()
        cover_pil.save(image_io, format='JPEG')
        image_name_cover = f'{q_xxx_id_str}-cover-{image_file_name_cleaned}'
        q_xxx.image_cover.save(image_name_cover, ContentFile(image_io.getvalue()), save=True)
        
        # 썸네일 이미지 저장
        image_io = io.BytesIO()
        thumbnail_pil.save(image_io, format='JPEG')
        image_name_thumbnail = f'{q_xxx_id_str}-thumbnail-{image_file_name_cleaned}'
        q_xxx.image_thumbnail.save(image_name_thumbnail, ContentFile(image_io.getvalue()), save=True)

        q_xxx.refresh_from_db()
    return q_xxx



# 배우 갤러리 이미지/썸네일 저장하기
def save_actor_gallery_images_and_thumbnail_to_db(q_actor, images):
    print('gallery image 저장하기')
    BASE_DIR = settings.MEDIA_ROOT
    BASE_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads") 
    DESTINATION_DIR = os.path.join(BASE_UPLOAD_DIR, "actor_images") 
    # 폴더 내 파일 이름 리스트화 및 동일파일이름 체크
    list_album_file_name = []
    file_names = os.listdir(DESTINATION_DIR)
    for file_name in file_names:
        list_album_file_name.append(file_name)
    
    list_actor_picture_id = q_actor.list_actor_picture_id
    if list_actor_picture_id is None:
        list_actor_picture_id = []
    name = q_actor.name
    i = len(list_actor_picture_id) + 1
    for image_file in images:    
        image_file_name = image_file.name
        image_file_name_cleaned = file_name_cleaner(image_file_name)
        actor_id_str = str(q_actor.id)
        image_file.name = f'{actor_id_str}-{image_file_name_cleaned}'
        title = f'model_album_{name}-({i})'
        if image_file_name_cleaned not in list_album_file_name:
            q_pic = Picture_Actor_Pic.objects.create(
                actor=q_actor,
                # image=image,
                title=title,
                name=name
            )
            print('q_pic', q_pic)
            list_actor_picture_id.append(q_pic.id)
            save_image_file_to_original_cover_and_thumbnail_images(q_pic, image_file)
        i = i + 1
    return list_actor_picture_id