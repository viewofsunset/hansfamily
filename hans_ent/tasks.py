

import multiprocessing
import time
import os 
import cv2
import signal
import uuid
from celery import Celery
from celery import shared_task
from celery.schedules import crontab
app = Celery()
from billiard import Pool as b_Pool


from pathlib import Path
from PIL import Image, ImageFile, ImageSequence
ImageFile.LOAD_TRUNCATED_IMAGES = True

from pygifmaker.pygifmaker import GifMaker
import io
from django.conf import settings
from hans_ent.models import *

from mutagen import File as mutagen_file
from tinytag import TinyTag
import datetime
import platform

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd

import pickle
import random
import time
import pathlib
import requests
from django.db.models import Q, F, Func
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from hans_ent.models import *
# from webui.functions import create_manga_album




# @app.task()
# def task_send_email():
#     subject = "message"
#     to = ["viewofsunset@naver.com"]
#     from_email = "viewofsunset@naver.com"
#     message = "메세지 테스트"
#     EmailMessage(subject=subject, body=message, to=to, from_email=from_email).send()
    


def get_cpu_count():
    cpu_count = os.cpu_count()
    if cpu_count is None:
        print("Unable to determine CPU count")
        cpu_count = 1  # Default to 1 if count cannot be determined
    print(f"Number of CPUs: {cpu_count}")
    return cpu_count

def is_prime(n):
    """Check if a number is prime."""
    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


@shared_task
def find_primes(numbers):
    print('start find_primes task!!')
    """Find all prime numbers in a list."""
    primes = []
    for number in numbers:
        if is_prime(number):
            primes.append(number)
    return primes


# @app.task() 
@shared_task
def task_prime(numbers):
    import multiprocessing
    import time
    import os 

    print('start celery task!!')
    """pools make working with multiprocessing easier"""
    # Define the list of numbers to find primes in
    
    # the number of processes to use
    processes = 10

    # Divide the list of numbers into chunks for each process
    chunk_size = len(numbers) // processes
    chunks = [numbers[i : i + chunk_size] for i in range(0, len(numbers), chunk_size)]

    pool = multiprocessing.Pool(processes=processes)
    start_time = time.monotonic()

    results = pool.map(find_primes, chunks)

    primes = []
    for result in results:
        primes += result

    pool.close()
    pool.join()

    end_time = time.monotonic()

    print(
        f"Found {len(primes):_} prime numbers "
        f"between {numbers[0]:_} and {numbers[-1]:_} "
        f"in {(end_time - start_time):.2f} seconds."
    )
    return len(primes)


# @app.task()
@shared_task
def task_add(x, y):
    print('task_add x, y', x, y)
    return x + y


# @app.task() 
@shared_task
def task_exponent(x, y):
    print('task_exponent x, y', x, y)
    return x + y


@shared_task
def send_email(email):
    print(f'A sample message is sent to {email}')










#############################################################################################################################################
#############################################################################################################################################
#
#                                                      Album Save Utilities
#
#############################################################################################################################################
#############################################################################################################################################



def resize_with_padding(image, target_width, target_height):
    # Resize the image while maintaining aspect ratio
    color=(255, 255, 255)
    try:
        image.thumbnail((target_width, target_height))
        # Calculate padding
        width, height = image.size
        pad_width = (target_width - width) // 2
        pad_height = (target_height - height) // 2
        # Create a new image with the target size and specified background color
        new_image = Image.new("RGB", (target_width, target_height), color)
        # Paste the resized image onto the new image, centered
        new_image.paste(image, (pad_width, pad_height))
    except:
        new_image = image
        print('이미지 크기 변경 실패')
    return new_image



# Function to resize and pad the frame
def resize_and_pad(frame, target_width, target_height, pad_color):
    # Get the original dimensions
    original_height, original_width = frame.shape[:2]
    # Compute the scaling factor and new dimensions
    scale_width = target_width / original_width
    scale_height = target_height / original_height
    scale = min(scale_width, scale_height)
    # Compute the new width and height to maintain aspect ratio
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    # Resize the frame
    resized_frame = cv2.resize(frame, (new_width, new_height))
    # Compute the padding for top/bottom and left/right
    pad_left = (target_width - new_width) // 2
    pad_right = target_width - new_width - pad_left
    pad_top = (target_height - new_height) // 2
    pad_bottom = target_height - new_height - pad_top
    # Add padding
    padded_frame = cv2.copyMakeBorder(
        resized_frame,
        pad_top,
        pad_bottom,
        pad_left,
        pad_right,
        cv2.BORDER_CONSTANT,
        value=pad_color
    )
    return padded_frame




def title_string_convert_to_title_elements_in_task(title):
    list_title_element_remove_check = ['', ' ', 'and']
    list_title_element_contain_check = ['mb', 'photo', 'photos']
    title = title.lower()
    title = title.replace('[', ' ')
    title = title.replace(']', ' ')
    title = title.replace('(', ' ')
    title = title.replace(')', ' ')
    title = title.replace('+', ' ')
    title = title.replace('-', ' ')
    title = title.replace('_', ' ')
    title = title.replace('「', ' ')
    title = title.replace('」', ' ')
    title = title.replace('【', ' ')
    title = title.replace('】', ' ')
    title = title.replace('photos', ' ')
    list_title_element = title.split(' ')
    list_title_element_new = []
    for item in list_title_element:
        check_good = True
        item = item.strip()
        if len(item) <= 1:
            check_good = False
        if item.isdigit():
            check_good = False
        for check_item in list_title_element_remove_check:
            if item == check_item:
                check_good = False
        for check_item in list_title_element_contain_check:
            if check_item in item:
                check_good = False
        if check_good == True:
            list_title_element_new.append(item)
    return list_title_element_new



#############################################################################################################################################
#############################################################################################################################################
#
#                                                Save Video Still Image 
#
#############################################################################################################################################
#############################################################################################################################################



# Multiprocessing으로 Video Album Still image 저장하기
@shared_task
def parallel_save_video_album_video_still_images_in_task(q_video_album_selected_id, list_dict_video_album):
    max_processor = 50
    timeout_sec = 200
    list_job = []
    
    # 실제 사용할 프로세서 개수 정하기
    req_processor = len(list_dict_video_album)
    print(req_processor)
    if max_processor > req_processor:
        final_processor = req_processor
    else:
        final_processor = max_processor
    print(final_processor)

    n = 1
    for dict_video_album in list_dict_video_album:
        if dict_video_album['discard'] == 'false':
            list_job.append((q_video_album_selected_id, dict_video_album))
        n = n + 1 
    
    print('list_job', len(list_job))
    # Set the timeout handler for the SIGALRM signal
    signal.signal(signal.SIGALRM, timeout_handler_hans_ent)
    list_result = []
    try:
        signal.alarm(timeout_sec)
        print('# 1. 멀티프로세싱 활용 이미지 저장 With WITH 함수, 빠름(2배정도). (중간에 뻗음?)')
        with b_Pool(processes=final_processor) as pool:
            list_result = pool.starmap(save_video_album_video_still_images_for_parallel, list_job)
        signal.alarm(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        list_result = []
    
    # list_dict_video_album 업데이트
    data = {
        "list_dict_video_album": list_result,
    }
    Video_Album.objects.filter(id=q_video_album_selected_id).update(**data)
    return True




# Multiprocessing으로 Video Album Still image 저장하기
def save_video_album_video_still_images_for_parallel(q_video_album_selected_id, dict_video_album):
    q_video_album_selected = Video_Album.objects.get(id=q_video_album_selected_id)
    # get base info
    hashcode = q_video_album_selected.hashcode
    video_id = dict_video_album['id']
    list_still_original = dict_video_album["still"]
    file_video_name = dict_video_album["video"]
    
    DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    file_video_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, file_video_name)
    if file_video_path:
        try:
            file_size = os.path.getsize(file_video_path)
            # Define size units and thresholds
            if file_size < 1024:  # Less than 1 KB
                file_size_b = file_size  # Byte
                file_size_b = f"{file_size_b:.2f} Byte"
                dict_video_album["file_size"] = file_size_b
            elif file_size < 1024 ** 2:  # Less than 1 MB
                file_size_kb = file_size / 1024  # KB
                file_size_kb = f"{file_size_kb:.2f} KB"
                dict_video_album["file_size"] = file_size_kb
            elif file_size < 1024 ** 3:  # Less than 1 GB
                file_size_mb = file_size / (1024 ** 2)  # MB
                file_size_mb = f"{file_size_mb:.2f} MB"
                dict_video_album["file_size"] = file_size_mb
            else:
                file_size_gb = file_size / (1024 ** 3)  # GB
                file_size_gb = f"{file_size_gb:.2f} GB"
                dict_video_album["file_size"] = file_size_gb
        except:
            pass

    # default still 이미지가 들어있는 모든 아이템은(리스트 길이가 1인) still 이미지 생성
    if len(list_still_original) == 1:
        # Still 이미지 확보
        list_still = []
        cap = cv2.VideoCapture(file_video_path)
        if cap.isOpened():
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            try:
                duration_seconds = total_frames / fps
                duration_seconds = round(duration_seconds, 2)
            except:
                duration_seconds = 0 

            if duration_seconds > 0:
                duration_str = str(datetime.timedelta(seconds=int(duration_seconds)))
            else:
                duration_str = 'None'

            # SAVE duration_second 
            if "duration_second" in dict_video_album:
                dict_video_album["duration_second"] = duration_seconds
            else:
                dict_video_album.update({'duration_second':duration_seconds})
            
            # SAVE duration_str 
            if "duration_str" in dict_video_album:
                dict_video_album["duration_str"] = duration_str
            else:
                dict_video_album.update({'duration_str':duration_str})
            
            # Get Still images and Time
            if duration_seconds < 600: # 10 min under == 10 cut
                unit_frame = total_frames // 10
                # print('5 unit_frame ', unit_frame)
                i = 1
                while i < 11:
                    print(i)
                    try:
                        return_value = still_image_save(i, cap, unit_frame, hashcode, video_id, fps)
                    except:
                        return_value = None
                        pass
                    if return_value is not None:
                        list_still.append(return_value)
                    i = i + 1
            elif duration_seconds >= 600 and duration_seconds < 3000: # 10 ~ 30 min  == 15 cut
                unit_frame = total_frames // 15
                # print('10 unit_frame ', unit_frame)
                i = 1
                while i < 16:
                    print(i)
                    try:
                        return_value = still_image_save(i, cap, unit_frame, hashcode, video_id, fps)
                    except:
                        return_value = None
                        pass
                    if return_value is not None:
                        list_still.append(return_value)
                    i = i + 1
            elif duration_seconds >= 3000 and duration_seconds < 9000: # 30 ~ 90 min  == 15 cut
                unit_frame = total_frames // 20
                # print('15 unit_frame ', unit_frame)
                i = 1
                while i < 21:
                    print(i)
                    try:
                        return_value = still_image_save(i, cap, unit_frame, hashcode, video_id, fps)
                    except:
                        return_value = None
                        pass
                    if return_value is not None:
                        list_still.append(return_value)
                    i = i + 1
            else: # 90 min ~ Over == 20 cut
                unit_frame = total_frames // 25
                # print('20 unit_frame ', unit_frame)
                i = 1
                while i < 26:
                    print(i)
                    try:
                        return_value = still_image_save(i, cap, unit_frame, hashcode, video_id, fps)
                    except:
                        return_value = None
                        pass
                    if return_value is not None:
                        list_still.append(return_value)
                    i = i + 1
            # Save Still
            dict_video_album["still"] = list_still
            # Save Thumbnail
            if len(list_still) > 0:
                dict_video_album["thumbnail"] = list_still[0]["path"]
    return dict_video_album





# 스틸 이미지 Resize and Crop 하고 저장하기
def resize_and_crop_in_task(input_path, output_path, target_size):
    """
    Resizes and crops an image to the target size without padding.
    target_size for cover =(520, 640)
    target_size for thumbnail = (260, 320)

    :input_path: Path to the original image.
    :output_path: Path where the resized and cropped image will be saved.
    :target_size: Desired size as a tuple (width, height).
    """
    # print(f'input_path: {input_path}')
    # print(f'output_path: {output_path}')
    # print(f'target_size: {target_size}')
    
    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        resample_filter = Image.ANTIALIAS

    try:
        with Image.open(input_path) as img:
            original_width, original_height = img.size
            target_width, target_height = target_size

            # print(f"Original image size: {original_width}x{original_height}px")
            # print(f"Target image size: {target_width}x{target_height}px")

            # Calculate aspect ratios
            original_ratio = original_width / original_height
            target_ratio = target_width / target_height

            # Determine scaling factor and size to resize
            if original_ratio > target_ratio:
                # Image is wider than target aspect ratio
                new_height = target_height
                new_width = int(new_height * original_ratio)
            else:
                # Image is taller than target aspect ratio
                new_width = target_width
                new_height = int(new_width / original_ratio)

            # print(f"Resizing image to: {new_width}x{new_height}px")

            # Resize the image while maintaining aspect ratio
            img_resized = img.resize((new_width, new_height), resample_filter)

            # Calculate coordinates to crop the image to the target size
            left = (new_width - target_width) / 2
            top = (new_height - target_height) / 2
            right = left + target_width
            bottom = top + target_height

            # print(f"Cropping image: left={left}, top={top}, right={right}, bottom={bottom}")

            # Crop the center of the image
            img_cropped = img_resized.crop((left, top, right, bottom))

            # Save the final image
            img_cropped.save(output_path)
            # print(f"Resized and cropped image saved as: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        pass



# 스틸 이미지 저장하기
def still_image_save(i, cap, unit_frame, hashcode, video_id, fps):
    cap.set(cv2.CAP_PROP_POS_FRAMES, unit_frame*i)
    ret, frame = cap.read()
    # Padding color (black in this case)
    pad_color = (255, 255, 255)  # (B, G, R)
    target_width = 640
    target_height = 360
    # Resize and pad the frame
    frame = resize_and_pad(frame, target_width, target_height, pad_color)
    # Save
    if ret:
        # Save the frame as an image file
        try:
            DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
            if not os.path.exists(DOWNLOAD_DIR):
                os.makedirs(DOWNLOAD_DIR)
            video_still_path = f'{hashcode}-s-{video_id}-{i}.jpg'
            file_still_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, video_still_path)
            # save Frame
            cv2.imwrite(file_still_path, frame)
            timestamp = (i*unit_frame) // fps
            return {"time":timestamp, "path":video_still_path}
        except:
            print('still 이미지 저장 실패')
            return None
    else:
        print('ret is None')
        return None



@shared_task
def saved_image_postprocessing_in_background(file_format, type_album, temp_file_path, image_name_cover, image_name_thumbnail):

    is_image = True
    is_video = False 
    is_audio = False
    if type_album == 'actor':
        pass
    elif type_album == 'picture':
        pass 
    elif type_album == 'manga':
        pass 
    elif type_album == 'video':
        if file_format == 'video':
            is_image = False
            is_video = True
    elif type_album == 'music':
        if file_format == 'audio':
            is_image = False
            is_audio = True
    # print("is_image is_video is_audio", is_image, is_video, is_audio)
    if is_image:
        # get Original image file
        image_pil = Image.open(temp_file_path)
        # File Path
        if type_album == 'actor':
            DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR)
            if not os.path.exists(DOWNLOAD_DIR):
                os.makedirs(DOWNLOAD_DIR)
            file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_cover)
            file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_thumbnail)
        elif type_album == 'picture':
            DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
            if not os.path.exists(DOWNLOAD_DIR):
                os.makedirs(DOWNLOAD_DIR)
            file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
            file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)
        elif type_album == 'manga':
            DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA)
            if not os.path.exists(DOWNLOAD_DIR):
                os.makedirs(DOWNLOAD_DIR)
            file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA, image_name_cover)
            file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA, image_name_thumbnail)
        elif type_album == 'video':
            DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
            if not os.path.exists(DOWNLOAD_DIR):
                os.makedirs(DOWNLOAD_DIR)
            file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_cover)
            file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_thumbnail)
        elif type_album == 'music':
            DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC)
            if not os.path.exists(DOWNLOAD_DIR):
                os.makedirs(DOWNLOAD_DIR)
            file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_cover)
            file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_thumbnail)
        
        # Resize Original Image for Thumbnail, Cover
        cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
        thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
        
        # 커버이미지 저장
        cover_pil.save(file_path_cover)
        
        # 썸네일 이미지 저장
        thumbnail_pil.save(file_path_thumbnail)
    return True


@shared_task
def saved_image_postprocessing_in_background_v2(list_dict_file_info_for_post_processing_in_parallel):
    """
    list_dict_file_info_for_post_processing_in_parallel = [
        {
            'id': q,
            'q_xxx_album_id': q_xxx_album.id,
            'file_name': file_name,
            'title_item': title_item, 
            'type_album': type_album,
            'file_extension': file_extension,
            'file_format': file_format,
            'default_storage_path': default_storage_path,
            'image_name_original': image_name_original,
            'image_name_cover': image_name_cover,
            'image_name_thumbnail': image_name_thumbnail,
            'video_name_original': video_name_original,
            'music_name_original': music_name_original,
            'original_image_file_path': original_image_file_path,
        }
    ]
    """
    for dict_file_info_for_post_processing_in_parallel in list_dict_file_info_for_post_processing_in_parallel:
        q_xxx_album_id = dict_file_info_for_post_processing_in_parallel['q_xxx_album_id']
        file_name = dict_file_info_for_post_processing_in_parallel['file_name']
        title_item = dict_file_info_for_post_processing_in_parallel['title_item']
        type_album = dict_file_info_for_post_processing_in_parallel['type_album']
        file_extension = dict_file_info_for_post_processing_in_parallel['file_extension']
        file_format = dict_file_info_for_post_processing_in_parallel['file_format']
        default_storage_path = dict_file_info_for_post_processing_in_parallel['default_storage_path']
        image_name_original = dict_file_info_for_post_processing_in_parallel['image_name_original']
        image_name_cover = dict_file_info_for_post_processing_in_parallel['image_name_cover']
        image_name_thumbnail = dict_file_info_for_post_processing_in_parallel['image_name_thumbnail']
        video_name_original = dict_file_info_for_post_processing_in_parallel['video_name_original']
        music_name_original = dict_file_info_for_post_processing_in_parallel['music_name_original']
        original_image_file_path = dict_file_info_for_post_processing_in_parallel['original_image_file_path']
            
        is_image = True
        is_video = False 
        is_audio = False
        if type_album == 'actor':
            pass
        elif type_album == 'picture':
            pass 
        elif type_album == 'manga':
            pass 
        elif type_album == 'video':
            if file_format == 'video':
                is_image = False
                is_video = True
        elif type_album == 'music':
            if file_format == 'audio':
                is_image = False
                is_audio = True
        # print("is_image is_video is_audio", is_image, is_video, is_audio)
        if is_image:
            # get Original image file
            image_pil = Image.open(default_storage_path)
            # File Path
            if type_album == 'actor':
                DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR)
                if not os.path.exists(DOWNLOAD_DIR):
                    os.makedirs(DOWNLOAD_DIR)
                file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_cover)
                file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_ACTOR, image_name_thumbnail)
            elif type_album == 'picture':
                DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
                if not os.path.exists(DOWNLOAD_DIR):
                    os.makedirs(DOWNLOAD_DIR)
                file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
                file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)
            elif type_album == 'manga':
                DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA)
                if not os.path.exists(DOWNLOAD_DIR):
                    os.makedirs(DOWNLOAD_DIR)
                file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA, image_name_cover)
                file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA, image_name_thumbnail)
            elif type_album == 'video':
                DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
                if not os.path.exists(DOWNLOAD_DIR):
                    os.makedirs(DOWNLOAD_DIR)
                file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_cover)
                file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, image_name_thumbnail)
            elif type_album == 'music':
                DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC)
                if not os.path.exists(DOWNLOAD_DIR):
                    os.makedirs(DOWNLOAD_DIR)
                file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_cover)
                file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MUSIC, image_name_thumbnail)
            
            # Resize Original Image for Thumbnail, Cover
            cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
            thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
            
            # 커버이미지 저장
            cover_pil.save(file_path_cover)
            
            # 썸네일 이미지 저장
            thumbnail_pil.save(file_path_thumbnail)
    return True



# Video Album Still image 저장하기
@shared_task
def save_video_album_video_still_images_in_task(list_collected_video_album_id_for_still_image_post_processing):
    # print(f'length of list_collected_video_album_id_for_still_image_post_processing, {len(list_collected_video_album_id_for_still_image_post_processing)} ')
    # print(f'list_collected_video_album_id_for_still_image_post_processing, {list_collected_video_album_id_for_still_image_post_processing} ')
    for q_video_album_selected_id in list_collected_video_album_id_for_still_image_post_processing:
        print(f'# Video Album Still image 저장하기 q_video_album_selected_id: {q_video_album_selected_id}')
        q_video_album_selected = Video_Album.objects.get(id=q_video_album_selected_id)
        list_dict_picture_album = q_video_album_selected.list_dict_picture_album
        list_dict_video_album = q_video_album_selected.list_dict_video_album
        # print(f'list_dict_picture_album, {list_dict_picture_album} ')
        print(f'list_dict_video_album, {list_dict_video_album} ')
        hashcode = q_video_album_selected.hashcode
        
        if list_dict_video_album is not None and len(list_dict_video_album) > 0:
            for dict_video_album in list_dict_video_album:
                if dict_video_album['id'] > 0:
                    list_still_original = dict_video_album["still"]
                    print(f'len of list_still_original: {len(list_still_original)}')
                    video_id = dict_video_album["id"]
                    file_video_name = dict_video_album["video"]
                    DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
                    if not os.path.exists(DOWNLOAD_DIR):
                        os.makedirs(DOWNLOAD_DIR)
                    file_video_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, file_video_name)
                    if file_video_path:
                        # file size 저장하기
                        print(f'file_video_path: {file_video_path}')
                        try:
                            file_size = os.path.getsize(file_video_path)
                            # Define size units and thresholds
                            if file_size < 1024:  # Less than 1 KB
                                file_size_b = file_size  # Byte
                                file_size_b = f"{file_size_b:.2f} Byte"
                                dict_video_album["file_size"] = file_size_b
                            elif file_size < 1024 ** 2:  # Less than 1 MB
                                file_size_kb = file_size / 1024  # KB
                                file_size_kb = f"{file_size_kb:.2f} KB"
                                dict_video_album["file_size"] = file_size_kb
                            elif file_size < 1024 ** 3:  # Less than 1 GB
                                file_size_mb = file_size / (1024 ** 2)  # MB
                                file_size_mb = f"{file_size_mb:.2f} MB"
                                dict_video_album["file_size"] = file_size_mb
                            else:
                                file_size_gb = file_size / (1024 ** 3)  # GB
                                file_size_gb = f"{file_size_gb:.2f} GB"
                                dict_video_album["file_size"] = file_size_gb
                        except:
                            pass
                    
                        # default still 이미지가 들어있는 모든 아이템은(리스트 길이가 1인) still 이미지 생성
                        if len(list_still_original) == 1:  # default 값만 있는 경우, Still 이미지 생성하기 시작
                            print(f'# default still 이미지가 들어있는 모든 아이템은(리스트 길이가 1인) still 이미지 생성')
                            list_still = []
                            cap = cv2.VideoCapture(file_video_path)
                            if cap.isOpened():
                                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                                fps = cap.get(cv2.CAP_PROP_FPS)
                                try:
                                    duration_seconds = total_frames / fps
                                    duration_seconds = round(duration_seconds, 2)
                                except:
                                    duration_seconds = 0 

                                if duration_seconds > 0:
                                    duration_str = str(datetime.timedelta(seconds=int(duration_seconds)))
                                else:
                                    duration_str = 'None'

                                # SAVE duration_second 
                                if "duration_second" in dict_video_album:
                                    dict_video_album["duration_second"] = duration_seconds
                                else:
                                    dict_video_album.update({'duration_second':duration_seconds})
                                
                                # SAVE duration_str 
                                if "duration_str" in dict_video_album:
                                    dict_video_album["duration_str"] = duration_str
                                else:
                                    dict_video_album.update({'duration_str':duration_str})
                                
                                print(f'duration_seconds: {duration_seconds}')
                                # Get Still images and Time
                                if duration_seconds < 600: # 10 min under == 10 cut
                                    unit_frame = total_frames // 10
                                    print('5 unit_frame ', unit_frame)
                                    i = 1
                                    while i < 11:
                                        # print('i', i)
                                        try:
                                            return_value = still_image_save(i, cap, unit_frame, hashcode, video_id, fps)
                                        except:
                                            return_value = None
                                            pass
                                        if return_value is not None:
                                            list_still.append(return_value)
                                        i = i + 1
                                elif duration_seconds >= 600 and duration_seconds < 3000: # 10 ~ 30 min  == 15 cut
                                    unit_frame = total_frames // 15
                                    print('10 unit_frame ', unit_frame)
                                    i = 1
                                    while i < 16:
                                        # print('i', i)
                                        try:
                                            return_value = still_image_save(i, cap, unit_frame, hashcode, video_id, fps)
                                        except:
                                            return_value = None
                                            pass
                                        if return_value is not None:
                                            list_still.append(return_value)
                                        i = i + 1
                                elif duration_seconds >= 3000 and duration_seconds < 9000: # 30 ~ 90 min  == 15 cut
                                    unit_frame = total_frames // 20
                                    print('15 unit_frame ', unit_frame)
                                    i = 1
                                    while i < 21:
                                        # print('i', i)
                                        try:
                                            return_value = still_image_save(i, cap, unit_frame, hashcode, video_id, fps)
                                        except:
                                            return_value = None
                                            pass
                                        if return_value is not None:
                                            list_still.append(return_value)
                                        i = i + 1
                                else: # 90 min ~ Over == 20 cut
                                    unit_frame = total_frames // 25
                                    print('20 unit_frame ', unit_frame)
                                    i = 1
                                    while i < 26:
                                        # print('i', i)
                                        try:
                                            return_value = still_image_save(i, cap, unit_frame, hashcode, video_id, fps)
                                        except:
                                            return_value = None
                                            pass
                                        if return_value is not None:
                                            list_still.append(return_value)
                                        i = i + 1
                                
                                # Save Still
                                print(f'Still 이미지 생성 후 list_still: {list_still}')
                                dict_video_album["still"] = list_still
                                
                                
                                # Save Thumbnail (최초 Still 이미지를 프로필 사진으로 등록)
                                if len(list_still) > 0:
                                    print('# video 스틸 이미지를 이용하여 video album 커버 이미지로 등록')
                                    dict_video_album["thumbnail"] = list_still[0]["path"]
                                    dict_video_album_id = dict_video_album['id'] + 1  # 앨범 스틸 이미지 커버이미지로 등록용 ID
                                    thumbnail = dict_video_album['thumbnail']
                                    save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO)
                                    path_file_name = os.path.join(save_dir, thumbnail)
                                    
                                    new_image_name_original = f'{hashcode}-o-{dict_video_album_id}.jpg'
                                    new_image_name_cover = f'{hashcode}-c-{dict_video_album_id}.jpg'
                                    new_image_name_thumbnail = f'{hashcode}-t-{dict_video_album_id}.jpg'
                                    file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, new_image_name_original)
                                    file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, new_image_name_cover)
                                    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_VIDEO, new_image_name_thumbnail)
                                    resize_and_crop_in_task(path_file_name, file_path_original, target_size=(260*4, 320*4))
                                    resize_and_crop_in_task(path_file_name, file_path_cover, target_size=(260*2, 320*2))
                                    resize_and_crop_in_task(path_file_name, file_path_thumbnail, target_size=(260, 320))

                                    # 비디오 커버 이미지 저장.
                                    list_dict_picture_album = q_video_album_selected.list_dict_picture_album
                                    print(f'list_dict_picture_album, {list_dict_picture_album} - 11')
                                    if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                                        # 초기조건 변경경
                                        for dict_picture_album in list_dict_picture_album:
                                            dict_picture_album['active'] = "false"  # 대문에서 내리기
                                            if dict_picture_album['id'] == 0:
                                                dict_picture_album['discard'] = "true" # 안보이게 하기
                                        list_dict_picture_album.append(
                                            {
                                                "id": len(list_dict_picture_album), 
                                                "cover": new_image_name_cover, 
                                                "original": new_image_name_original,
                                                "thumbnail": new_image_name_thumbnail,
                                                "active": "true", "discard": "false"}
                                        )
                                        # print(f'list_dict_picture_album, {list_dict_picture_album} - 12')
                                        data = {
                                            'list_dict_picture_album': list_dict_picture_album,
                                        }
                                        Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
                                else:
                                    dict_video_album["still"] = [{"time":1, "path":"default-s.png"}]
                                    print(f'video 스틸 이미지가 생성되지 않았습니다.')

                        else:
                            print(f'length of list_still_original is not 1 == 이미 still 이미지를 생성했으니 Skip 한다는 의미')
                            pass
            # list_dict_video_album 업데이트
            data = {
                "list_dict_video_album": list_dict_video_album,
            }
            Video_Album.objects.filter(id=q_video_album_selected.id).update(**data)
            q_video_album_selected.refresh_from_db()
    return True






#############################################################################################################################################
#############################################################################################################################################
#
#                                                      Scraping Default
#
#############################################################################################################################################
#############################################################################################################################################


"""
    DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER)

    file_extension = 'pdf'
    pdf_name = f'paper-{hashcode}.{file_extension}'
    file_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_STUDY_PAPER, pdf_name)
    check_download_pdf = False

    # PDF Download using request
    if pdf_url is not None and file_path is not None:
        # 디렉토리가 없으면 생성한다.
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        # 파일이 이미 저장되어 있으면 저장하지 않고 건너뛴다.
        if os.path.exists(file_path):
            print(f'동일한 파일이 존재합니다.')
            check_download_pdf = True
        else:
            print(f'동일한 파일이 없습니다. PDF 다운로드합니다.')
            headers = get_random_header()
            session = requests.Session()
            response = session.get(pdf_url, headers=headers)
"""


# Chrome Driver 띄우기
def boot_google_chrome_driver_in_hans_ent_task():
    print('# 외부사이트 Update용 # Chrome Driver 띄우기')
    os_name = platform.system()
        
    # Check if the OS is Linux or Windows
    if os_name == 'Linux':
        print("The operating system is Linux.")
        CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
        service = Service(executable_path=CHROME_DRIVER_PATH)
        chrome_options = Options()
        chrome_options.add_argument("--window-size=6000,6000")
        chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        prefs = {
            # "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,  # Disable the "Save As" dialog
            "download.directory_upgrade": True,          # Ensure the directory exists
            "safebrowsing.enabled": True,                # Enable safe browsing
            # "profile.default_content_settings.popups": 0,
            # "profile.default_content_setting_values.automatic_downloads": 1,
            # "profile.managed_default_content_settings.images": 1  # Allow image downloads
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
    elif os_name == 'Windows':
        print("The operating system is Windows.")
        driver = webdriver.Chrome()
    return driver 


# Chrome Driver 띄우기
def boot_google_chrome_driver_for_parsing_info():
    CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
    service = Service(executable_path=CHROME_DRIVER_PATH)
    chrome_options = Options()
    # chrome_options.add_argument("--window-size=6000,6000")
    chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
    chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
    chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver 


#############################################################################################################################################
#############################################################################################################################################
#
#                                                      Picture Crawling
#
#############################################################################################################################################
#############################################################################################################################################



# Default Picture Album 쿼리 생성
def create_picture_album_in_hans_ent_task():
    random_uuid = uuid.uuid4()
    hashcode = str(random_uuid)
    data = {
        'hashcode': hashcode,
        'dict_picture_album_cover':DEFAULT_DICT_PICTURE_ALBUM_COVER,
        'list_dict_picture_album':DEFAULT_LIST_DICT_PICTURE_ALBUM,
        'dict_score_history': DEFAULT_DICT_SCORE_HISTORY_PICTURE, 
    }
    q_picture_album = Picture_Album.objects.create(**data)
    print('Picture Album 신규 생성!', q_picture_album)
    return q_picture_album


# Error 리포트 생성
def f_report_error_picture_4k_in_task(title, num_image, image_url, q_picture_album_id, contents):
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    list_dict_report_error_picture = q_systemsettings_hansent.list_dict_report_error_picture
    if list_dict_report_error_picture is None:
        list_dict_report_error_picture = []
    list_dict_report_error_picture.append({'title':title, 'num_img':num_image, 'image_url':image_url, 'picture_album_id': q_picture_album_id, 'contents': contents})
    data = {
        'list_dict_report_error_picture': list_dict_report_error_picture,
    }
    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
    q_systemsettings_hansent.refresh_from_db()


# Error 리포트 생성
def f_report_error_picture_4k(title, num_image, image_url, q_picture_album_id, contents):
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    list_dict_report_error_picture = q_systemsettings_hansent.list_dict_report_error_picture
    if list_dict_report_error_picture is None:
        list_dict_report_error_picture = []
    list_dict_report_error_picture.append({'title':title, 'num_img':num_image, 'image_url':image_url, 'picture_album_id': q_picture_album_id, 'contents': contents})
    data = {
        'list_dict_report_error_picture': list_dict_report_error_picture,
    }
    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
    q_systemsettings_hansent.refresh_from_db()


# Define timeout exception
class TimeoutException_hans_ent(Exception):
    pass

# Define the timeout handler
def timeout_handler_hans_ent(signum, frame):
    raise TimeoutException_hans_ent("Timeout: f_a exceeded the time limit.")







#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#
#                                                    4KHD Gallery URL 및 Image URL 획득하기
#
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################




# ---------------------------------------------------------------------------------------------------------------------------------------------
# A-1-2. 4KHD Gallery URL 정보를 이용하여 Image URL 정보 획득하기
# ---------------------------------------------------------------------------------------------------------------------------------------------
# Image URL 정보 획득 함수
def get_image_url_from_gallery_info(gallery_title, gallery_url):
    print(f'이미지 url 정보를 다운받습니다. gallery_title: {gallery_title}, gallery_url: {gallery_url}')
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    selected_vault = q_systemsettings_hansent.selected_vault
    list_collect_gallery_image_url_all_page_no_dup = []
    q_picture_album_id = None
    check_collect = False

    random_sec = random.uniform(2, 4)
    time.sleep(random_sec)
    driver = boot_google_chrome_driver_in_hans_ent_task()
    
    try:
        driver.get(gallery_url)
        source2 = driver.page_source
        soup2 = BeautifulSoup(source2, 'html.parser')
        elements2 = soup2.find_all(class_="is-layout-flow wp-block-group is-style-default")
    except:
        driver.quit()
        elements2 = None
        print(f'선택한 Gallery URL로 사이트 정보 크롤링 실패.')
        pass
    
    if elements2 is not None:
        # 중복확인
        q_picture_album = Picture_Album.objects.filter(Q(check_discard=False) & Q(title=gallery_title)).last()
        print(f'q_picture_album id : {q_picture_album.id}')

        if q_picture_album is not None:
            print(f'1-1 : {q_picture_album.id}')
            q_picture_album_id = q_picture_album.id
            list_dict_picture_album = q_picture_album.list_dict_picture_album    # 다운받은 이미지 Hashcode 기반 이미지 주소 리스트
            list_picture_url_album = q_picture_album.list_picture_url_album      # 웹 갤러리에서 추출한 각 이미지 주소 리스트 저장
            print('1-1-1')
            if list_dict_picture_album is None:
                print('1-1-2')
                list_dict_picture_album = [{'id':0, 'original':"default-o.png", "cover":"default-c.png", "thumbnail":"default-t.png", "file_size":"unknown", "image_size":[],"active":"true", "discard":"false"}]
                num_list_dict_picture_album = 1
            else:
                print('1-1-3')
                num_list_dict_picture_album = len(list_dict_picture_album)

            if list_picture_url_album is None:
                print('1-1-4')
                list_picture_url_album = [] 
                num_list_picture_url_album = 0
            else:
                print('1-1-5')
                num_list_picture_url_album = len(list_picture_url_album)
        else:
            print('1-2')
            q_picture_album_id = None


        if q_picture_album is None:
            check_collect = True
            print(f'등록된 앨범이 없습니다. 앨범을 생성하고 이미지 URL을 다운받습니다.0.')
        else:
            if num_list_picture_url_album > 0 :
                if num_list_dict_picture_album != num_list_picture_url_album + 1:
                    print(f'수집한 Gallery URL 정보가 있습니다. 이미지 URL을 다운받습니다.1.')
                    check_collect = True
                else:
                    print(f'수집한 Image URL 개수와 다운받은 Image 개수가 동일합니다. 다운받을 이미지 URL이 없습니다.')
                    check_collect = False
            else:
                print(f'수집한 Gallery URL 정보가가 없습니다. Image URL을 다운받습니다.2.')
                check_collect = True
                pass
        
        print(f'check_collect: {check_collect}')

        if check_collect == True:
            print('2-1 이미지 URL 크롤링 시작')
            list_list_collect_gallery_image_url = []
            list_dict_picture_album = []
            list_page_num = []
            # list_job = []
            # list_result = []

            start_time = time.time()  # Record the start time
            print('1')
            # #################################################################################################
            # # 앨범 생성하기
            # #################################################################################################
            if q_picture_album is None:
                print('# Picture Album 생성하기')
                q_picture_album = create_picture_album_in_hans_ent_task()
                q_picture_album_id = q_picture_album.id
                list_picture_url_album = q_picture_album.list_picture_url_album
                try:
                    num_list_picture_url_album = len(list_picture_url_album)
                except:
                    list_picture_url_album = []
                    num_list_picture_url_album = 0

            print('2')
            try:
                hashcode = q_picture_album.hashcode
            except:
                hashcode = None
            print(f'hashcode: {hashcode}')
            
            try:
                list_dict_picture_album = q_picture_album.list_dict_picture_album
                if list_dict_picture_album is None:
                    list_dict_picture_album = DEFAULT_LIST_DICT_PICTURE_ALBUM
            except:
                list_dict_picture_album = DEFAULT_LIST_DICT_PICTURE_ALBUM
            print(f'list_dict_picture_album: {list_dict_picture_album}')

            if len(list_dict_picture_album) > 0: # 디폴트 disable 시킴킴
                print('3')
                try:
                    list_dict_picture_album[0]['active'] = 'false'
                    list_dict_picture_album[0]['discard'] = 'true'
                except:
                    print('디폴트 disable 실패')
                    pass
            else:
                print('디폴트 없음')
                pass

            # max_processor = 100
            # timeout_sec = 200
            
            print(f'list_dict_picture_album 길이 1: {len(list_dict_picture_album)}')  # 1 이면 디폴트 값만 들어있는 경우

            # #################################################################################################
            # # 이미지주소 다운받기
            # #################################################################################################
            # Gallery First Page Image URL Parsing
            print('# 이미지주소 다운받기 시작')
            k = 1
            for element2 in elements2:
                print(f'element2: {element2}')
                list_collect_gallery_image_url = []
                tags = element2.find_all('a')
                m = 0
                for tag in tags:
                    href = tag.get('href')
                    # 해당 Gallery 다음 페이지들 주소 수집
                    if '.webp' not in href and href.split('html')[-1] != '' and 'https://m.4khd.com' not in href:
                        page_num_str = href.split('html/')[-1]
                        try:
                            page_num = int(page_num_str)
                            if page_num not in list_page_num:
                                list_page_num.append(page_num)
                        except:
                            pass
                    # gallery image url 수집
                    if '.webp' in href:
                        list_collect_gallery_image_url.append(href)
                    else:
                        # print(href)
                        pass
                    m = m + 1
                list_list_collect_gallery_image_url.append(list_collect_gallery_image_url)
                k = k + 1
            if len(list_list_collect_gallery_image_url) > 0:
                list_collect_gallery_image_url_all_page = list_list_collect_gallery_image_url[0]
            else:
                list_collect_gallery_image_url_all_page = []
            list_collect_gallery_image_url_all_page_no_dup = list_collect_gallery_image_url_all_page_no_dup + list_collect_gallery_image_url_all_page
            print(f'list_collect_gallery_image_url_all_page: {len(list_collect_gallery_image_url_all_page)}')

            # 2 page 이상 있으면 추가 이미지 주소 획득
            print(f'갤러리 페이지 개수 : {list_page_num}')
            if 2 in list_page_num:
                for page_num in list_page_num:
                    # print('page_num', page_num)
                    time.sleep(random_sec)

                    list_list_collect_gallery_image_url = []
                    gallery_url_page = f'{gallery_url}/{page_num}'
                    try:
                        driver.get(gallery_url_page)
                        source_page = driver.page_source
                        soup_page = BeautifulSoup(source_page, 'html.parser')
                        elements_page = soup_page.find_all(class_="is-layout-flow wp-block-group is-style-default")

                        q = 0
                        for element_page in elements_page:
                            list_collect_gallery_image_url = []
                            tags = element_page.find_all('a')
                            r = 0
                            for tag in tags:
                                href = tag.get('href')
                                # 해당 Gallery 다음 페이지들 주소 수집
                                if '.webp' not in href and href.split('html')[-1] != '':
                                    page_num_str = href.split('html/')[-1]
                                    try:
                                        page_num = int(page_num_str)
                                        if page_num not in list_page_num:
                                            list_page_num.append(page_num)
                                    except:
                                        pass
                                # gallery image url 수집
                                if '.webp' in href:
                                    list_collect_gallery_image_url.append(href)
                                else:
                                    # print(href)
                                    pass
                                r = r + 1
                            list_list_collect_gallery_image_url.append(list_collect_gallery_image_url)
                            q = q + 1
                        if len(list_list_collect_gallery_image_url) > 0:
                            list_collect_gallery_image_url_all_page = list_list_collect_gallery_image_url[0]
                        else:
                            list_collect_gallery_image_url_all_page = []
                        list_collect_gallery_image_url_all_page_no_dup = list_collect_gallery_image_url_all_page_no_dup + list_collect_gallery_image_url_all_page
                    except:
                        pass
            print(f'##### 획득한 이미지 주소 개수 : {len(list_collect_gallery_image_url_all_page_no_dup)}')

            # 획득한 다운받을 이미지 주소 리스트 저장하기
            if len(list_collect_gallery_image_url_all_page_no_dup) > 0:
                try:
                    tags = title_string_convert_to_title_elements_in_task(gallery_title)
                    data = {
                        'title': gallery_title,   
                        'tags': tags,
                        'list_picture_url_album': list_collect_gallery_image_url_all_page_no_dup,     
                        # 'dict_gallery_info': dict_gallery_info,                    
                    }
                except:
                    data = {
                        'title': gallery_title,   
                        'list_picture_url_album': list_collect_gallery_image_url_all_page_no_dup,     
                        # 'dict_gallery_info': dict_gallery_info,                    
                    }
                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                q_picture_album.refresh_from_db()
            else:
                print(f'gallery_url는 있지만 획득한 다운받을 이미지 주소 파싱 0개. 에러등록')
                q_systemsettings_hansent.refresh_from_db()
                list_picture_id_parsing_error = q_systemsettings_hansent.list_picture_id_parsing_error
                if list_picture_id_parsing_error is None:
                    list_picture_id_parsing_error = []
                if q_picture_album.id not in list_picture_id_parsing_error:
                    list_picture_id_parsing_error.append(q_picture_album.id)
                data = {
                    'list_picture_id_parsing_error': list_picture_id_parsing_error,
                }
                SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                q_picture_album.refresh_from_db()

            # #################################################################################################
            # 추가정보 업데이트
            end_time = time.time()  # Record the end time
            processing_time = end_time - start_time  # Calculate the time difference
            print(f"Task processed in {processing_time:.4f} seconds") 
        else:
            print(f'선택한 앨범 정보가 없습니다.')
            pass
        driver.quit()
        
    return q_picture_album_id, list_collect_gallery_image_url_all_page_no_dup




# ---------------------------------------------------------------------------------------------------------------------------------------------
# A-1-3 4KHD Gallery URL 정보를 이용하여 Image URL 정보 획득하기 by 사용자 선택한 특정 사진 앨범에서
# ---------------------------------------------------------------------------------------------------------------------------------------------
# 사용자 선택한 Gallery URL을 이용하여 Image URL 정보 획득하기
@shared_task
def get_image_url_from_gallery_info_from_views():
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    dict_gallery_info_for_crawling_image_url = q_systemsettings_hansent.dict_gallery_info_for_crawling_image_url
    # print(f'dict_gallery_info_for_crawling_image_url: {dict_gallery_info_for_crawling_image_url}')
    try:
        q_picture_album_id = dict_gallery_info_for_crawling_image_url['id']
        dict_gallery_info = dict_gallery_info_for_crawling_image_url['dict_gallery_info']
        gallery_url = dict_gallery_info['url']
        gallery_title = dict_gallery_info['title']

        # print(f'gallery_url: {gallery_url}, gallery_title: {gallery_title}')

        q_picture_album_id, list_collect_gallery_image_url_all_page_no_dup = get_image_url_from_gallery_info(gallery_title, gallery_url)
               
        print('success 크롤링 이미지 URL')
    except:
        print('failed 크롤링 이미지 URL')
        pass
    
    try:
        download_image_using_image_url(q_picture_album_id)
        print('success 다운로드 이미지')
    except:
        print('failed 다운로드 이미지')
        pass

    # 해당 필드 리셋하기
    data = {
        'dict_gallery_info_for_crawling_image_url': None,
    }
    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
    q_systemsettings_hansent.refresh_from_db()
    print('Gallery URL을 이용하여 Image URL 정보 획득하기 종료')



# ---------------------------------------------------------------------------------------------------------------------------------------------
# A-1-4 4KHD Image URL 정보를 이용하여 Image Download하기 by 사용자 선택한 특정 사진 앨범에서
# ---------------------------------------------------------------------------------------------------------------------------------------------
# 사용자 선택한 Gallery Image URL을 이용하여 Image Download 하기
@shared_task
def download_image_from_image_url_info_from_views():
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    dict_gallery_info_for_crawling_image_url = q_systemsettings_hansent.dict_gallery_info_for_crawling_image_url
    # print(f'dict_gallery_info_for_crawling_image_url: {dict_gallery_info_for_crawling_image_url}')
    try:
        q_picture_album_id = dict_gallery_info_for_crawling_image_url['id']
        dict_gallery_info = dict_gallery_info_for_crawling_image_url['dict_gallery_info']
        print('success 정보 획득')
    except:
        print('failed 정보 획득')
        pass
    
    try:
        download_image_using_image_url(q_picture_album_id)
        print('success 다운로드 이미지')
    except:
        print('failed 다운로드 이미지')
        pass

    # 해당 필드 리셋하기
    data = {
        'dict_gallery_info_for_crawling_image_url': None,
    }
    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
    q_systemsettings_hansent.refresh_from_db()
    print('Gallery URL을 이용하여 Image URL 정보 획득하기 종료')


# ---------------------------------------------------------------------------------------------------------------------------------------------
# A-1. 4KHD Gallery URL 정보 획득하기 (선택한 페이지 범위에서)
# ---------------------------------------------------------------------------------------------------------------------------------------------
# 자동으로 4KHD 접속하여 여러 페이지의 Gallery URL 획득하기
@shared_task
def update_latest_4khd_data_to_db():
    random_sec = random.uniform(2, 4)
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.last()
    p_last = q_systemsettings_hansent.parsing_picture_start_page_reverse_count
    p_first = 0.5

    while p_last > p_first:
        # while p > p_first:
        print(f'4KHD 웹사이트 페이지 :  {p_last}')
        driver = boot_google_chrome_driver_in_hans_ent_task()
        
        DESTINATION_URL = f'https://www.4khd.com/?query-3-page={p_last}'
        # DESTINATION_URL = f'https://www.4khd.com/pages/album?query-3-page={p}'
        time.sleep(random_sec)
        driver.get(DESTINATION_URL)
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')
        elements = soup.find_all(class_='is-nowrap')
        # elements = soup.find_all(class_="is-layout-flow wp-block-group is-style-no-margin")

        # print('Gallery URL 획득하기')
        list_dict_gallery_info = []
        list_title_dup_check = []
        download_url = None
        i = 0
        for element in elements:
            tags = element.find_all('a')
            for tag in tags:
                dict_gallery_info = {}
                title = tag.text
                href = tag.get('href')
                if href is not None and tag.text.lower() == 'terabox':
                    download_url = href
                if title not in list_title_dup_check and title != '' and 'https://' in href:
                    dict_gallery_info['title'] = title
                    dict_gallery_info['url'] = href
                    list_dict_gallery_info.append(dict_gallery_info)
                
                list_title_dup_check.append(title) # 중복등록 방지용
            i = i + 1
        # 역순으로 만들기
        list_dict_gallery_info.reverse()
        print(f'페이지 내 획득한 갤러리 주소 정보 개수 : {len(list_dict_gallery_info)}')
        
        # print(f'페이지 내 획득한 갤러리 주소 정보 개수 : {list_dict_gallery_info}')
        
        # print('# 획득한 URL로 이미지 정보 획득하기')
        list_picture_album_id_to_download = []
        if list_dict_gallery_info is not None and len(list_dict_gallery_info) > 0:
            j = 0
            for dict_gallery_info in list_dict_gallery_info:
                print(f'이미지 Scraping 시작')
                start_time = time.time()  # Record the start time
                check_proceed_collecting_gallery_image_urls = False
                list_collect_gallery_image_url_all_page_no_dup = []
                list_list_collect_gallery_image_url = []
                list_page_num = []
                gallery_url = dict_gallery_info['url']
                gallery_title = dict_gallery_info['title']
                print(f'title : {gallery_title}')
                q_picture_album = Picture_Album.objects.filter(Q(check_discard=False) & Q(title=gallery_title)).last()
                if q_picture_album is None:
                    check_proceed_collecting_gallery_image_urls = True
                    print('# Picture Album 생성하기')
                    q_picture_album = create_picture_album_in_hans_ent_task()
                else:
                    list_picture_url_album = q_picture_album.list_picture_url_album
                    if list_picture_url_album is None or len(list_picture_url_album) == 0 :
                        check_proceed_collecting_gallery_image_urls = True

                if check_proceed_collecting_gallery_image_urls == True:
                    try:
                        driver.get(gallery_url)
                        source2 = driver.page_source
                        soup2 = BeautifulSoup(source2, 'html.parser')
                        elements2 = soup2.find_all(class_="is-layout-flow wp-block-group is-style-default")
                        
                        k = 1
                        for element2 in elements2:
                            # print('k', k)
                            list_collect_gallery_image_url = []
                            tags = element2.find_all('a')
                            m = 0
                            for tag in tags:
                                href = tag.get('href')
                                # 해당 Gallery 다음 페이지들 주소 수집
                                if '.webp' not in href and href.split('html')[-1] != '' and 'https://m.4khd.com' not in href:
                                    page_num_str = href.split('html/')[-1]
                                    try:
                                        page_num = int(page_num_str)
                                        if page_num not in list_page_num:
                                            list_page_num.append(page_num)
                                    except:
                                        pass
                                # gallery image url 수집
                                if '.webp' in href:
                                    list_collect_gallery_image_url.append(href)
                                else:
                                    # print(href)
                                    pass
                                m = m + 1
                            list_list_collect_gallery_image_url.append(list_collect_gallery_image_url)
                            k = k + 1
                        if len(list_list_collect_gallery_image_url) > 0:
                            list_collect_gallery_image_url_all_page = list_list_collect_gallery_image_url[0]
                        else:
                            list_collect_gallery_image_url_all_page = []
                        list_collect_gallery_image_url_all_page_no_dup = list_collect_gallery_image_url_all_page_no_dup + list_collect_gallery_image_url_all_page
                        
                        # 2 page 이상 있으면 추가 이미지 주소 획득
                        print(f'갤러리 페이지 개수 : {list_page_num}')
                        if 2 in list_page_num:
                            for page_num in list_page_num:
                                # print('page_num', page_num)
                                time.sleep(random_sec)

                                list_list_collect_gallery_image_url = []
                                gallery_url_page = f'{gallery_url}/{page_num}'
                                try:
                                    driver.get(gallery_url_page)
                                    source_page = driver.page_source
                                    soup_page = BeautifulSoup(source_page, 'html.parser')
                                    elements_page = soup_page.find_all(class_="is-layout-flow wp-block-group is-style-default")

                                    q = 0
                                    for element_page in elements_page:
                                        list_collect_gallery_image_url = []
                                        tags = element_page.find_all('a')
                                        r = 0
                                        for tag in tags:
                                            href = tag.get('href')
                                            # 해당 Gallery 다음 페이지들 주소 수집
                                            if '.webp' not in href and href.split('html')[-1] != '':
                                                page_num_str = href.split('html/')[-1]
                                                try:
                                                    page_num = int(page_num_str)
                                                    if page_num not in list_page_num:
                                                        list_page_num.append(page_num)
                                                except:
                                                    pass
                                            # gallery image url 수집
                                            if '.webp' in href:
                                                list_collect_gallery_image_url.append(href)
                                            else:
                                                # print(href)
                                                pass
                                            r = r + 1
                                        list_list_collect_gallery_image_url.append(list_collect_gallery_image_url)
                                        q = q + 1
                                    
                                    # print('list_list_collect_gallery_image_url', list_list_collect_gallery_image_url)
                                    if len(list_list_collect_gallery_image_url) > 0:
                                        list_collect_gallery_image_url_all_page = list_list_collect_gallery_image_url[0]
                                    else:
                                        list_collect_gallery_image_url_all_page = []
                                    list_collect_gallery_image_url_all_page_no_dup = list_collect_gallery_image_url_all_page_no_dup + list_collect_gallery_image_url_all_page
                                except:
                                    pass
                    except:
                        pass

                if check_proceed_collecting_gallery_image_urls == True:
                    list_picture_album_id_to_download.append(q_picture_album.id)
                    print('q_picture_album 업데이트 수행')  
                    print(f'collected image url number: {len(list_collect_gallery_image_url_all_page_no_dup)}')
                    data = {
                        'title': gallery_title,   
                        'list_picture_url_album': list_collect_gallery_image_url_all_page_no_dup,     
                        'dict_gallery_info': dict_gallery_info,                    
                    }
                    Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                else:
                    print('q_picture_album 업데이트 건너뛰기')
                    pass
                # 추가정보 업데이트
                end_time = time.time()  # Record the end time
                processing_time = end_time - start_time  # Calculate the time difference
                print(f"Task processed in {processing_time:.4f} seconds") 

        p_last = p_last - 1
        driver.quit()
    
    # 이미지 저장하기
    # print('# image donwload using image url')
    # if len(list_picture_album_id_to_download) > 0:
    #     qs_picture_album_to_download = Picture_Album.objects.filter(id__in=list_picture_album_id_to_download)
    #     if qs_picture_album_to_download is not None and len(qs_picture_album_to_download) > 0:
    #         for q_picture_album_to_download in qs_picture_album_to_download:
    #             pass
                

    print('# 빼먹은 쿼리 찾아서 돌리기')
    # qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False) & Q(Func(F('list_dict_picture_album'), function='jsonb_array_length') <= 1) & Q(Func(F('list_picture_url_album'), function='jsonb_array_length') == 0) & Q(Func(F('dict_gallery_info'), function='jsonb_array_length') == 1))
    qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False))
    print(len(qs_picture_album))
    list_collected_dict_gallery_url = []
    if qs_picture_album is not None and len(qs_picture_album) > 0:
        for q_picture_album in qs_picture_album:
            list_dict_picture_album = q_picture_album.list_dict_picture_album
            list_picture_url_album = q_picture_album.list_picture_url_album
            dict_gallery_info = q_picture_album.dict_gallery_info
            if list_dict_picture_album is None:
                list_dict_picture_album = []
            if list_picture_url_album is None:
                list_picture_url_album = []
            if dict_gallery_info is None:
                dict_gallery_info = {}
            if len(list_dict_picture_album) <= 1 and len(list_picture_url_album) == 0 and len(dict_gallery_info) == 1:
                list_collected_dict_gallery_url.append(q_picture_album.dict_gallery_info)
    print(f'수행할 앨범 개수: {len(list_collected_dict_gallery_url)}')

    print('# 획득한 URL로 이미지 정보 획득하기')
    if list_collected_dict_gallery_url is not None and len(list_collected_dict_gallery_url) > 0:
        j = 0
        for dict_gallery_info in list_collected_dict_gallery_url:
            gallery_url = dict_gallery_info['url']
            gallery_title = dict_gallery_info['title']

            q_picture_album_id, list_collect_gallery_image_url_all_page_no_dup = get_image_url_from_gallery_info(gallery_title, gallery_url)
            
            data = {
                'title': gallery_title,   
                'list_picture_url_album': list_collect_gallery_image_url_all_page_no_dup,     
                'picture_download_url': download_url,   # tera
                'dict_gallery_info': dict_gallery_info,                    
            }
            Picture_Album.objects.filter(id=q_picture_album_id).update(**data)
            driver.quit()
            j = j + 1
    # 추가정보 업데이트
    print('Image URL 업데이트 종료')
    return True






#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#
#                                             Image URL 이용하여 스크린샷으로 이미지 저장하기
#
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################




# A-3-1. 4KHD Image 다운로드 (이미지 저장하기 함수(Screenshot으로))
def f_save_images_from_url_in_task(image_url, hashcode, n):
    # print('image_url, hashcode, n', image_url, hashcode, n)
    random_sec = random.uniform(2, 4)
    time.sleep(random_sec)
    
    file_extension = 'jpg'

    image_name_original = f'{hashcode}-o-{n}.{file_extension}'
    image_name_cover = f'{hashcode}-c-{n}.{file_extension}'
    image_name_thumbnail = f'{hashcode}-t-{n}.{file_extension}'

    file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_original)
    file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)

    if os.path.exists(file_path_original):
        # 파일이 이미 저장되어 있으면 건너뛴다.
        return None
    else:
        DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)

        CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
        service = Service(executable_path=CHROME_DRIVER_PATH)
        chrome_options = Options()
        chrome_options.add_argument("--window-size=6000,6000")
        chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-extensions')  # Disable extensions to save memory
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
                
        # Configure Chrome's download directory and behavior
        prefs = {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,  # Disable the "Save As" dialog
            "download.directory_upgrade": True,          # Ensure the directory exists
            "safebrowsing.enabled": True,                # Enable safe browsing
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        time.sleep(random_sec)
        try:
            time.sleep(random_sec)
            driver.get(image_url)
            time.sleep(random_sec)
            # Get the image content as binary data
            image_data = driver.find_element(By.TAG_NAME, "img").screenshot_as_png
        except:
            image_data = None
        
        if image_data is not None:
            # Check if the file exists
            try:
                # Original Image JPG 변환 및 저장
                image = Image.open(io.BytesIO(image_data))
                rgb_image = image.convert('RGB')  # Convert the image to RGB mode
                # Save the image as a JPG in binary mode
                with open(file_path_original, "wb") as f:
                    rgb_image.save(f, "JPEG")
            except:
                print('rgb_image is None!, !!! check media folder ownership. hans should have ownership instead of root !!!')
                rgb_image = None
                pass 
            
            if rgb_image is not None:
                try:
                    image_pil = Image.open(file_path_original)
                    img_width, img_height = image_pil.size
                except:
                    print('Save Error !!!!  q_pictuer_album_id : ', hashcode)
                    image_pil = None
                    img_width = 0
                    img_height = 0

                try:
                    file_size = os.path.getsize(file_path_original)
                except:
                    print('file_size is None!')
                    file_size = 'unknown'

                # Check if the file exists
                if image_pil is not None:
                    if os.path.exists(file_path_cover):
                        pass
                    else:
                        # 커버 이미지 저장
                        cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
                        try:
                            cover_pil.save(file_path_cover)
                        except:
                            print('cover_pil is None!')
                            pass
                    if os.path.exists(file_path_thumbnail):
                        pass
                    else:
                        # 썸네일 이미지 저장
                        thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
                        try:
                            thumbnail_pil.save(file_path_thumbnail) 
                        except:
                            print('thumbnail_pil is None!')
                            pass
            
                driver.quit()
                return {'id':n, 'original':image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "file_size":file_size, "image_size":[img_width, img_height],"active":"false", "discard":"false"}
            else:
                driver.quit()
                return None
        else:
            driver.quit()
            return None



# A-3-2. 4KHD Image 다운로드 - PROXY 이용 (이미지 저장하기 함수(Screenshot으로))
def f_save_images_from_url_in_task_w_proxy(image_url, hashcode, n):
    # print('image_url, hashcode, n', image_url, hashcode, n)
    from study.models import SMARTPROXY_USER_NAME, SMARTPROXY_USER_PASSWORD
    proxy_port = random.randint(10001, 11000)
    proxy = f"http://{SMARTPROXY_USER_NAME}:{SMARTPROXY_USER_PASSWORD}@us.smartproxy.com:{proxy_port}"
    
    random_sec = random.uniform(2, 4)
    time.sleep(random_sec)
    
    file_extension = 'jpg'

    image_name_original = f'{hashcode}-o-{n}.{file_extension}'
    image_name_cover = f'{hashcode}-c-{n}.{file_extension}'
    image_name_thumbnail = f'{hashcode}-t-{n}.{file_extension}'

    file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_original)
    file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)

    if os.path.exists(file_path_original):
        # 파일이 이미 저장되어 있으면 건너뛴다.
        return None
    else:
        DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)

        CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
        service = Service(executable_path=CHROME_DRIVER_PATH)
        chrome_options = Options()
        chrome_options.add_argument("--window-size=6000,6000")
        chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-extensions')  # Disable extensions to save memory
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        chrome_options.add_argument(f"--proxy-server={proxy}")

        
        # Configure Chrome's download directory and behavior
        prefs = {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,  # Disable the "Save As" dialog
            "download.directory_upgrade": True,          # Ensure the directory exists
            "safebrowsing.enabled": True,                # Enable safe browsing
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        time.sleep(random_sec)
        try:
            time.sleep(random_sec)
            driver.get(image_url)
            time.sleep(random_sec)
            # Get the image content as binary data
            image_data = driver.find_element(By.TAG_NAME, "img").screenshot_as_png
        except:
            image_data = None
        
        if image_data is not None:
            # Check if the file exists
            try:
                # Original Image JPG 변환 및 저장
                image = Image.open(io.BytesIO(image_data))
                rgb_image = image.convert('RGB')  # Convert the image to RGB mode
                # Save the image as a JPG in binary mode
                with open(file_path_original, "wb") as f:
                    rgb_image.save(f, "JPEG")
            except:
                print('rgb_image is None!')
                rgb_image = None
                pass 
            
            if rgb_image is not None:
                try:
                    image_pil = Image.open(file_path_original)
                    img_width, img_height = image_pil.size
                except:
                    print('Save Error !!!!  q_pictuer_album_id : ', hashcode)
                    image_pil = None
                    img_width = 0
                    img_height = 0

                try:
                    file_size = os.path.getsize(file_path_original)
                except:
                    print('file_size is None!')
                    file_size = 'unknown'

                # Check if the file exists
                if image_pil is not None:
                    if os.path.exists(file_path_cover):
                        pass
                    else:
                        # 커버 이미지 저장
                        cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
                        try:
                            cover_pil.save(file_path_cover)
                        except:
                            print('cover_pil is None!')
                            pass
                    if os.path.exists(file_path_thumbnail):
                        pass
                    else:
                        # 썸네일 이미지 저장
                        thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
                        try:
                            thumbnail_pil.save(file_path_thumbnail) 
                        except:
                            print('thumbnail_pil is None!')
                            pass
            
                driver.quit()
                return {'id':n, 'original':image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "file_size":file_size, "image_size":[img_width, img_height],"active":"false", "discard":"false"}
            else:
                driver.quit()
                return None
        else:
            driver.quit()
            return None



# 선택된 앨범의 이미지를 4KHD에서 다운받기
def download_image_using_image_url(q_picture_album_id):
    print('# 다운받아야 하는 이미지 ULR 정보가 있는 경우')
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    list_picture_id_parsing_error = q_systemsettings_hansent.list_picture_id_parsing_error

    max_processor = 100
    timeout_sec = 200
    random_sec = random.uniform(2, 4)
    time.sleep(random_sec)
    
    list_job=[]
    start_time = time.time()  # Record the start time
    
    q_picture_album = Picture_Album.objects.get(id=q_picture_album_id)
    q_picture_album.refresh_from_db()
    hashcode = q_picture_album.hashcode
    list_picture_url_album = q_picture_album.list_picture_url_album
    
    
    print(f'q_picture_album_id: {q_picture_album_id}, hashcode: {hashcode}, len(list_picture_url_album): {len(list_picture_url_album)}')
    
    # 이미지 다운로드
    def download_image_using_image_url_inside_function(q_picture_album_id):
        q_picture_album = Picture_Album.objects.get(id=q_picture_album_id)
        list_dict_picture_album = q_picture_album.list_dict_picture_album
        list_picture_url_album = q_picture_album.list_picture_url_album

        print(f'download_image_using_image_url_inside_function 함수 시작')
        time.sleep(random_sec)
        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
            try:
                list_dict_picture_album[0]['active'] = 'false'
                list_dict_picture_album[0]['discard'] = 'true'
            except:
                pass
        else:
            list_dict_picture_album = DEFAULT_LIST_DICT_PICTURE_ALBUM
            list_dict_picture_album[0]['active'] = 'false'
            list_dict_picture_album[0]['discard'] = 'true'
        
        if len(list_picture_url_album) > 0:
            n = 1
            for image_url in list_picture_url_album:
                list_job.append((image_url, hashcode, n))
                n = n + 1 
        
            # 실제 사용할 프로세서 개수 정하기
            req_processor = len(list_job)
            if max_processor > req_processor:
                final_processor = req_processor
            else:
                final_processor = max_processor
            print(f'final_processor: {final_processor}')

            # Set the timeout handler for the SIGALRM signal
            signal.signal(signal.SIGALRM, timeout_handler_hans_ent)
            list_result = []
            try:
                signal.alarm(timeout_sec)
                print('# 1-1. 멀티프로세싱 활용 이미지 저장 w/o Proxy')
                with b_Pool(processes=final_processor) as pool:
                    list_result = pool.starmap(f_save_images_from_url_in_task, list_job)
                signal.alarm(0)
            except Exception as e:
                print(f"An error occurred 1: {e}")
                try:
                    print('# 1-2. 멀티프로세싱 활용 이미지 저장 w/ Proxy')
                    with b_Pool(processes=final_processor) as pool:
                        list_result = pool.starmap(f_save_images_from_url_in_task_w_proxy, list_job)
                except Exception as e:
                    print('# 1-3. 멀티프로세싱 활용 이미지 저장 실패')
                    print(f"An error occurred 2: {e}")
                    
            if list_result is not None and len(list_result) > 0:
                dict_picture_album_0 = list_dict_picture_album[0]
                list_dict_picture_album = []
                list_dict_picture_album.append(dict_picture_album_0)
                for result in list_result:
                    if result is not None:
                        list_dict_picture_album.append(result)

                if len(list_dict_picture_album) > 1:
                    list_dict_picture_album[-1]['active'] = 'true'
                data = {
                    'list_dict_picture_album': list_dict_picture_album,
                    'check_url_downloaded': True,
                }
                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                q_picture_album.refresh_from_db()
                print(f'{q_picture_album.id} 업데이트 완료.')
            else:
                print(f'{q_picture_album.id} list_result 결과값이 없습니다.')
                list_picture_id_parsing_error.append(q_picture_album.id)
        else:
            print(f'수집한 image url이 없습니다.')
            pass


    if list_picture_url_album is not None and len(list_picture_url_album) > 0:
        print(f'다운받을 이미지 주소 정보가 있습니다. 다운로드를 시작합니다.')
        download_image_using_image_url_inside_function(q_picture_album_id)
    else:
        dict_gallery_info = q_picture_album.dict_gallery_info
        try:
            gallery_url = dict_gallery_info['url']
            gallery_title = dict_gallery_info['title']
        except:
            gallery_url = None
            gallery_title = None
        if gallery_title is not None and gallery_url is not None:   
            print(f'다운받을 이미지 주소 정보가 없습니다.갤러리 주소를 이용하여 이미지 주소를 먼저 크롤링 합니다.')
            get_image_url_from_gallery_info(gallery_title, gallery_url)
            q_picture_album.refresh_from_db()
            list_picture_url_album = q_picture_album.list_picture_url_album
            if list_picture_url_album is not None and len(list_picture_url_album) > 0:
                print(f'다운받을 이미지 주소 정보를 크롤링 하였습니다. 다운로드를 시작합니다.')
                download_image_using_image_url_inside_function(q_picture_album_id)
            else:
                print(f'다운받을 이미지 주소 정보를 크롤링 실패하였습니다.')
                list_picture_id_parsing_error.append(q_picture_album.id)
        else:
            print(f'다운받을 갤러리 주소 정보가 없습니다.')
            list_picture_id_parsing_error.append(q_picture_album.id)
    data = {
        'list_picture_id_parsing_error': list_picture_id_parsing_error
    }
    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
    


# ---------------------------------------------------------------------------------------------------------------------------------------------
# 모든 다운가능한 상태의 앨범 image url로부터 이미지 스크린샷으로 다운받기
## A-2. 4KHD Image 다운로드 (Multiprocessing using single Celery Worker)
# ---------------------------------------------------------------------------------------------------------------------------------------------
@shared_task
def download_image_using_url_w_multiprocessing1():
    
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    list_picture_id_parsing_error = q_systemsettings_hansent.list_picture_id_parsing_error
    if list_picture_id_parsing_error is None: 
        list_picture_id_parsing_error = []

    qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False) & Q(check_url_downloaded=False) & Q(check_4k_uploaded=False) & ~Q(id__in=list_picture_id_parsing_error)).order_by('-id')
    tot_num_mission = len(qs_picture_album)
    print(f'total album : {tot_num_mission}')
    print(f'qs_picture_album last id : {qs_picture_album.first().id}')

    for q_picture_album in qs_picture_album:
        download_image_using_image_url(q_picture_album.id)
        tot_num_mission = tot_num_mission - 1
        print(f'remained mission: {tot_num_mission}')
    
    return True 


# ---------------------------------------------------------------------------------------------------------------------------------------------
# 지정한 앨범만 image url로부터 이미지 스크린샷으로 다운받기
## 4KHD Image 다운로드 (Multiprocessing using single Celery Worker)
# ---------------------------------------------------------------------------------------------------------------------------------------------
@shared_task
def download_image_using_url_w_multiprocessing_for_selected_album_only():
    print(f'지정한 앨범만 image url로부터 이미지 스크린샷으로 다운받기')
    random_sec = random.uniform(2, 4)
    import time
    max_processor = 100
    timeout_sec = 200
    
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    selected_vault = q_systemsettings_hansent.selected_vault
    selected_picture_album_id = q_systemsettings_hansent.selected_picture_album_id

    if selected_picture_album_id is not None:
        q_picture_album = Picture_Album.objects.get(id=selected_picture_album_id)
        print(f'********************* q_picture_album_id: {q_picture_album.id}')
        # 다운받은 이미지 파일이 존재하는지 체크
        hashcode = q_picture_album.hashcode
        RELATIVE_PATH_PICTURE = f'{selected_vault}/picture'
        DOWNLOAD_PICTURE_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
        
        random_sec = random.uniform(2, 4)
        list_job=[]
        start_time = time.time()  # Record the start time
        hashcode = q_picture_album.hashcode
        list_dict_picture_album = q_picture_album.list_dict_picture_album
        list_picture_url_album = q_picture_album.list_picture_url_album

        try:
            dict_gallery_info = q_picture_album.dict_gallery_info
        except:
            dict_gallery_info = None
        if dict_gallery_info is not None:
            try:
                gallery_url = dict_gallery_info['url']
            except:
                gallery_url = None 
            try:
                gallery_title = dict_gallery_info['title']
            except:
                gallery_title = None
        else:
            gallery_url = None
            gallery_title = None

        
        # 다운받아야 하는 이미지 ULR 정보가 없는 경우, list_picture_url_album 정보 획득하기
        if list_picture_url_album is None or len(list_picture_url_album) == 0:
            print('1')
            q_picture_album_id, list_collect_gallery_image_url_all_page_no_dup = get_image_url_from_gallery_info(gallery_title, gallery_url)

        q_picture_album.refresh_from_db()
        list_picture_url_album = q_picture_album.list_picture_url_album

        # 다운받아야 하는 이미지 ULR 정보가 있는 경우
        if list_picture_url_album is not None and len(list_picture_url_album) > 0:
            print('2')
            download_image_using_image_url(q_picture_album.id)
        
        end_time = time.time()  # Record the end time
        processing_time = end_time - start_time  # Calculate the time difference
        print(f"Task processed in {processing_time:.4f} seconds") 
        
        # Get current local date & time
        now = datetime.datetime.now()
        print(f"Completed time: {now}")

        q_picture_album.refresh_from_db()
        list_dict_picture_album= q_picture_album.list_dict_picture_album
        list_dict_picture_album[-1]['active'] = 'true'
        data = {
            'list_dict_picture_album': list_dict_picture_album,
        }
        Picture_Album.objects.filter(id=selected_picture_album_id).update(**data)
    else:
        pass 
    

    
    data = {
        'selected_picture_album_id': None
    }
    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
    return True


#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################
#
#                                             Picture Album 유지보수
#
#############################################################################################################################################
#############################################################################################################################################
#############################################################################################################################################




# 파일은 저장했는데 list_dict_picture_album에 미등록된 경우 등록하기
@shared_task
def update_missing_files_in_list_dict_picture_album():
    qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False) & Q(check_4k_uploaded=False))
    # Specify the folder path
    folder_path = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
    # folder_path = '/django-project/site/public/media/vault1/picture/'
    # print('folder_path', folder_path)

    # Get the list of all files and directories in the specified folder
    file_list = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    print('len(file_list)', len(file_list))

    p = 1
    for q_picture_album in qs_picture_album:
        title = q_picture_album.title
        
        hashcode = q_picture_album.hashcode
        list_picture_url_album = q_picture_album.list_picture_url_album
        if list_picture_url_album is None or len(list_picture_url_album) == 0:
            num_list_picture_url_album = 0
        else:    
            num_list_picture_url_album = len(list_picture_url_album)

        list_dict_picture_album = q_picture_album.list_dict_picture_album
        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
            num_list_dict_picture_album = len(list_dict_picture_album)
        else:
            num_list_dict_picture_album = 0 

        list_file_name_matched_hashcode = []
        if num_list_picture_url_album > 0 and num_list_dict_picture_album < 2:
            for file_name in file_list:
                if hashcode in file_name:
                    list_file_name_matched_hashcode.append(file_name)
        
        if len(list_file_name_matched_hashcode) > 0:
            print('len(list_file_name_matched_hashcode)', len(list_file_name_matched_hashcode))
            print(f'page {p}, {title}, id: {q_picture_album.id}')
            list_dict_picture_album[0]['active'] = 'false'
            list_dict_picture_album[0]['discard'] = 'true'
            check_o_exist = False 
            check_c_exist = False 
            check_t_exist = False 

            for file_name_matched_hashcode in list_file_name_matched_hashcode:
                file_name_type = file_name_matched_hashcode.split(f'{hashcode}-')[-1]
                if 'o' in file_name_type:
                    check_o_exist = True
                if 'c' in file_name_type:
                    check_c_exist = True
                if 't' in file_name_type:
                    check_t_exist = True
                if check_o_exist == True and check_c_exist == True and check_t_exist == True:
                    break 
            if check_o_exist == True and check_c_exist == True and check_t_exist == True:
                num_matched_file = len(list_file_name_matched_hashcode) 
                each_num_matched_file = num_matched_file/3
                i = 1
                while i < each_num_matched_file + 1:
                    file_extension = 'jpg'
                    image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                    image_name_cover = f'{hashcode}-c-{i}.{file_extension}'
                    image_name_thumbnail = f'{hashcode}-t-{i}.{file_extension}'
                    file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_original)
                    try:
                        image_pil = Image.open(file_path_original)
                        img_width, img_height = image_pil.size
                    except:
                        print('Save Error !!!!  q_pictuer_album_id : ', hashcode)
                        img_width = 0
                        img_height = 0
                    try:
                        file_size = os.path.getsize(file_path_original)
                    except:
                        print('file_size is None!')
                        file_size = 'unknown'
                    list_dict_picture_album.append({'id':i, 'original':image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "file_size":file_size, "image_size":[img_width, img_height],"active":"false", "discard":"false"}) 
                    i = i + 1
            else:
                if check_o_exist == True and check_c_exist == False and check_t_exist == False:
                    each_num_matched_file = num_matched_file
                    i = 1
                    while i < each_num_matched_file + 1:
                        file_extension = 'jpg'
                        image_name_original = f'{hashcode}-o-{i}.{file_extension}'
                        image_name_cover = f'{hashcode}-c-{i}.{file_extension}'
                        image_name_thumbnail = f'{hashcode}-t-{i}.{file_extension}'
                        file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_original)
                        try:
                            image_pil = Image.open(file_path_original)
                            img_width, img_height = image_pil.size
                        except:
                            print('Save Error !!!!  q_pictuer_album_id : ', hashcode)
                            image_pil = None
                            img_width = 0
                            img_height = 0
                        try:
                            file_size = os.path.getsize(file_path_original)
                        except:
                            print('file_size is None!')
                            file_size = 'unknown'
                        # Check if the file exists
                        if image_pil is not None:
                            # 커버 이미지 저장
                            file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
                            cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
                            try:
                                cover_pil.save(file_path_cover)
                            except:
                                print('cover_pil is None!')
                                pass
                        
                            # 썸네일 이미지 저장
                            file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)
                            thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
                            try:
                                thumbnail_pil.save(file_path_thumbnail) 
                            except:
                                print('thumbnail_pil is None!')
                                pass
                        list_dict_picture_album.append({'id':i, 'original':image_name_original, "cover":image_name_cover, "thumbnail":image_name_thumbnail, "file_size":file_size, "image_size":[img_width, img_height],"active":"false", "discard":"false"}) 
                        i = i + 1

            list_dict_picture_album[-1]['active'] = 'true'
            list_dict_picture_album[-1]['discard'] = 'false'
            data = {
                'list_dict_picture_album': list_dict_picture_album,
                'check_url_downloaded': True,
            }
            Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
        p = p + 1



# Picture Album 오류 수정하기
@shared_task
def check_picture_album_defect_and_correct_by_album(q_picture_album_id):
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    list_done_cover_resize_id = q_systemsettings_hansent.list_done_cover_resize_id
    if list_done_cover_resize_id is None:
        list_done_cover_resize_id = []

    q_picture_album = Picture_Album.objects.get(id=q_picture_album_id)
    selected_vault = q_picture_album.selected_vault

    # print('# # 다운받은 이미지 정보와 실제 다운받은 파일이 있는지 체크')
    # folder_path = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture')
    list_dict_picture_album = q_picture_album.list_dict_picture_album
    list_check_file_original = []
    if list_dict_picture_album is not None and len(list_dict_picture_album) > 1:
        for dict_picture_album in list_dict_picture_album:
            image_name_original = dict_picture_album['original']
            file_path = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture', image_name_original)
            if not os.path.exists(file_path):
                list_dict_picture_album.remove(dict_picture_album)
                list_check_file_original.append(False)
            else:
                list_check_file_original.append(False)
        check_4k_downloaded = q_picture_album.check_4k_downloaded
        if list_check_file_original.count(True)/len(list_check_file_original) < 0.5:
            check_4k_downloaded = False
        data = {
            'list_dict_picture_album': list_dict_picture_album,
            'check_4k_downloaded': check_4k_downloaded
        }
        Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
        q_picture_album.refresh_from_db()

    # print('# # 이미지 다운받았으나 체크되지 않은 상태 변경하기')
    if q_picture_album.check_url_downloaded == False:
        check_url_downloaded = q_picture_album.check_url_downloaded
        list_picture_url_album = q_picture_album.list_picture_url_album
        if list_picture_url_album is None or len(list_picture_url_album) == 0:
            num_list_picture_url_album = 0
        else:    
            num_list_picture_url_album = len(list_picture_url_album)

        list_dict_picture_album = q_picture_album.list_dict_picture_album
        if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
            num_list_dict_picture_album = len(list_dict_picture_album)
        else:
            num_list_dict_picture_album = 0 
        if num_list_picture_url_album > 0 and num_list_dict_picture_album > 1 and check_url_downloaded == False:
            data = {
                'check_url_downloaded': True
            }
            Picture_Album.objects.filter(id=q_picture_album.id).update(**data)

    # print('# # 오리지널만 저장된 상태로 list dict 내용이 모두 들어간 경우. 커버, 썸네일 다시 저장하기 함수')
    if q_picture_album.id not in list_done_cover_resize_id:
        list_done_cover_resize_id.append(q_picture_album.id)
        hashcode = q_picture_album.hashcode
        file_extension = 'jpg'
        image_name_original_base = f'{hashcode}-o-'
        image_name_original_first = f'{hashcode}-o-{1}.{file_extension}'
        
        # 오리지널 첫 번째 이미지 저장됐나 확인
        file_path_original_first = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture', image_name_original_first)
        directory_picture_path_ = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture')
        if os.path.exists(file_path_original_first):
            check_original_downloaded = True
        else:
            check_original_downloaded = False

        list_check_image_file_downloaded = []
        num_tot_original_images = 0
        if check_original_downloaded == True:
            # DB에 저장된 오리지널 이미지 파악
            for filename in os.listdir(directory_picture_path_):
                if image_name_original_base in filename:
                    filename = filename.split('.')[0]
                    filename = filename.split('-o-')[-1]
                    try:
                        filename = int(filename)
                    except:
                        try:
                            filename = filename.spiit('_')[0]
                            filename = int(filename)
                        except:
                            filename = None
                    if filename is not None:
                        list_check_image_file_downloaded.append(filename)
            num_tot_original_images = len(list_check_image_file_downloaded)
        
        # 마지막 커버 / 썸네일 이미지 저장됐나 확인
        check_cover_downloaded = False
        check_thumbnail_downloaded = False
        if num_tot_original_images > 0:
            image_name_cover_last = f'{hashcode}-c-{num_tot_original_images}.{file_extension}'
            image_name_thumbnail_last = f'{hashcode}-t-{num_tot_original_images}.{file_extension}'
            file_path_cover_last = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture', image_name_cover_last)
            file_path_thumbnail_last = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture', image_name_thumbnail_last)
            if os.path.exists(file_path_cover_last):
                check_cover_downloaded = True
            if os.path.exists(file_path_thumbnail_last):
                check_thumbnail_downloaded = True
            
        if check_original_downloaded == True:
            if check_cover_downloaded != True or check_thumbnail_downloaded != True:
                if len(list_check_image_file_downloaded) > 0:
                    print("커버/썸네일 저장중 ")
                    for image_number in list_check_image_file_downloaded:
                        image_name_original = f'{hashcode}-o-{image_number}.{file_extension}'
                        image_name_cover = f'{hashcode}-c-{image_number}.{file_extension}'
                        image_name_thumbnail = f'{hashcode}-t-{image_number}.{file_extension}'
                        file_path_original = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture', image_name_original)
                        try:
                            image_pil = Image.open(file_path_original)
                            img_width, img_height = image_pil.size

                            if check_cover_downloaded == False:
                                if os.path.exists(image_name_cover):
                                    pass 
                                else:
                                    # 오리지널 이미지로부터 커버 이미지 변환 시작
                                    cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
                                    file_path_cover = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture', image_name_cover)
                                    try:
                                        cover_pil.save(file_path_cover)
                                    except:
                                        print('cover_pil is None!')
                                        pass

                            if check_thumbnail_downloaded == False:
                                if os.path.exists(file_path_thumbnail_last):
                                    pass 
                                else:
                                    # 오리지널 이미지로부터 썸네일 이미지 변환 시작
                                    thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
                                    file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture', image_name_thumbnail)
                                    try:
                                        thumbnail_pil.save(file_path_thumbnail) 
                                    except:
                                        print('thumbnail_pil is None!')
                                        pass
                        except:
                            print('Save Error !!!!  q_pictuer_album_id : ', hashcode)
        
                    data = {
                        'list_done_cover_resize_id': list_done_cover_resize_id,
                    }
                    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                    q_systemsettings_hansent.refresh_from_db()
    
    print(f'끝난 작업 앨범 ID: {q_picture_album_id}')
    return True

# Picture Album 오류 수정하기 멀티로
@shared_task
def check_picture_album_defect_and_correct_by_multiprocessing():

    max_processor = 100
    timeout_sec = 200
    random_sec = random.uniform(2, 4)
    time.sleep(random_sec)
    list_job=[]
    list_result = []
    start_time = time.time()  # Record the start time

    qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False))
    total_num_tasks = len(qs_picture_album)
    print(f'total_num_tasks: {total_num_tasks}')

    if qs_picture_album is not None and len(qs_picture_album) > 0:
        for q_picture_album in qs_picture_album:
            list_job.append((q_picture_album.id))
    
    if len(list_job) > 0:
        # 실제 사용할 프로세서 개수 정하기
        req_processor = len(list_job)
        if max_processor > req_processor:
            final_processor = req_processor
        else:
            final_processor = max_processor
        print(f'final_processor: {final_processor}')
        
        try:
            signal.alarm(timeout_sec)
            print('# 1-1. Picture Album 오류 수정하기 멀티로')
            with b_Pool(processes=final_processor) as pool:
                list_result = pool.starmap(check_picture_album_defect_and_correct_by_album, list_job)
            signal.alarm(0)
        except Exception as e:
            print(f"An error occurred 1: {e}")

    print(list_result.count)


# Picture Album 오류 수정하기
@shared_task
def check_picture_album_defect_and_correct():
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    list_done_cover_resize_id = q_systemsettings_hansent.list_done_cover_resize_id
    if list_done_cover_resize_id is None:
        list_done_cover_resize_id = []

    qs_picture_album = Picture_Album.objects.filter(Q(check_discard=False))
    total_num_tasks = len(qs_picture_album)
    print(f'total_num_tasks: {total_num_tasks}')
    
    if qs_picture_album is not None and len(qs_picture_album) > 0:
        start_time = time.time()  # Record the start time
        p = 1    
        for q_picture_album in qs_picture_album:

            # print('# # 다운받은 이미지 정보와 실제 다운받은 파일이 있는지 체크')
            selected_vault = q_picture_album.selected_vault
            # folder_path = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture')
            list_dict_picture_album = q_picture_album.list_dict_picture_album
            list_check_file_original = []
            if list_dict_picture_album is not None and len(list_dict_picture_album) > 1:
                for dict_picture_album in list_dict_picture_album:
                    image_name_original = dict_picture_album['original']
                    file_path = os.path.join(settings.MEDIA_ROOT, selected_vault, 'picture', image_name_original)
                    if not os.path.exists(file_path):
                        list_dict_picture_album.remove(dict_picture_album)
                        list_check_file_original.append(False)
                    else:
                        list_check_file_original.append(False)
                check_4k_downloaded = q_picture_album.check_4k_downloaded
                if list_check_file_original.count(True)/len(list_check_file_original) < 0.5:
                    check_4k_downloaded = False
                data = {
                    'list_dict_picture_album': list_dict_picture_album,
                    'check_4k_downloaded': check_4k_downloaded
                }
                Picture_Album.objects.filter(id=q_picture_album.id).update(**data)
                q_picture_album.refresh_from_db()
                    

            # print('# # 이미지 다운받았으나 체크되지 않은 상태 변경하기')
            if q_picture_album.check_url_downloaded == False:
                check_url_downloaded = q_picture_album.check_url_downloaded
                list_picture_url_album = q_picture_album.list_picture_url_album
                if list_picture_url_album is None or len(list_picture_url_album) == 0:
                    num_list_picture_url_album = 0
                else:    
                    num_list_picture_url_album = len(list_picture_url_album)

                list_dict_picture_album = q_picture_album.list_dict_picture_album
                if list_dict_picture_album is not None and len(list_dict_picture_album) > 0:
                    num_list_dict_picture_album = len(list_dict_picture_album)
                else:
                    num_list_dict_picture_album = 0 
                if num_list_picture_url_album > 0 and num_list_dict_picture_album > 1 and check_url_downloaded == False:
                    data = {
                        'check_url_downloaded': True
                    }
                    Picture_Album.objects.filter(id=q_picture_album.id).update(**data)

            # print('# # 오리지널만 저장된 상태로 list dict 내용이 모두 들어간 경우. 커버, 썸네일 다시 저장하기 함수')
            if q_picture_album.id not in list_done_cover_resize_id:
                list_done_cover_resize_id.append(q_picture_album.id)
                hashcode = q_picture_album.hashcode
                file_extension = 'jpg'
                image_name_original_base = f'{hashcode}-o-'
                image_name_original_first = f'{hashcode}-o-{1}.{file_extension}'
                
                # 오리지널 첫 번째 이미지 저장됐나 확인
                file_path_original_first = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_original_first)
                directory_picture_path_ = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE)
                if os.path.exists(file_path_original_first):
                    check_original_downloaded = True
                else:
                    check_original_downloaded = False

                list_check_image_file_downloaded = []
                num_tot_original_images = 0
                if check_original_downloaded == True:
                    # DB에 저장된 오리지널 이미지 파악
                    for filename in os.listdir(directory_picture_path_):
                        if image_name_original_base in filename:
                            filename = filename.split('.')[0]
                            filename = filename.split('-o-')[-1]
                            try:
                                filename = int(filename)
                            except:
                                try:
                                    filename = filename.spiit('_')[0]
                                    filename = int(filename)
                                except:
                                    filename = None
                            if filename is not None:
                                list_check_image_file_downloaded.append(filename)
                    num_tot_original_images = len(list_check_image_file_downloaded)
                
                # 마지막 커버 / 썸네일 이미지 저장됐나 확인
                check_cover_downloaded = False
                check_thumbnail_downloaded = False
                if num_tot_original_images > 0:
                    image_name_cover_last = f'{hashcode}-c-{num_tot_original_images}.{file_extension}'
                    image_name_thumbnail_last = f'{hashcode}-t-{num_tot_original_images}.{file_extension}'
                    file_path_cover_last = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover_last)
                    file_path_thumbnail_last = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail_last)
                    if os.path.exists(file_path_cover_last):
                        check_cover_downloaded = True
                    if os.path.exists(file_path_thumbnail_last):
                        check_thumbnail_downloaded = True
                    
                if check_original_downloaded == True:
                    if check_cover_downloaded != True or check_thumbnail_downloaded != True:
                        if len(list_check_image_file_downloaded) > 0:
                            print("커버/썸네일 저장중 ")
                            for image_number in list_check_image_file_downloaded:
                                image_name_original = f'{hashcode}-o-{image_number}.{file_extension}'
                                image_name_cover = f'{hashcode}-c-{image_number}.{file_extension}'
                                image_name_thumbnail = f'{hashcode}-t-{image_number}.{file_extension}'
                                file_path_original = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_original)
                                try:
                                    image_pil = Image.open(file_path_original)
                                    img_width, img_height = image_pil.size

                                    if check_cover_downloaded == False:
                                        if os.path.exists(image_name_cover):
                                            pass 
                                        else:
                                            # 오리지널 이미지로부터 커버 이미지 변환 시작
                                            cover_pil = resize_with_padding(image_pil, 520, 640)  # Target size: 300x300 with white background
                                            file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_cover)
                                            try:
                                                cover_pil.save(file_path_cover)
                                            except:
                                                print('cover_pil is None!')
                                                pass

                                    if check_thumbnail_downloaded == False:
                                        if os.path.exists(file_path_thumbnail_last):
                                            pass 
                                        else:
                                            # 오리지널 이미지로부터 썸네일 이미지 변환 시작
                                            thumbnail_pil = resize_with_padding(image_pil, 260, 320)  # Target size: 300x300 with white background
                                            file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_PICTURE, image_name_thumbnail)
                                            try:
                                                thumbnail_pil.save(file_path_thumbnail) 
                                            except:
                                                print('thumbnail_pil is None!')
                                                pass
                                except:
                                    print('Save Error !!!!  q_pictuer_album_id : ', hashcode)
                
                            data = {
                                'list_done_cover_resize_id': list_done_cover_resize_id,
                            }
                            SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
                            q_systemsettings_hansent.refresh_from_db()
            print(f'진행상황: {p}/{total_num_tasks}, progress: {round(p/total_num_tasks, 1)}) %')
            p = p + 1
        
        end_time = time.time()  # Record the end time
        processing_time = end_time - start_time  # Calculate the time difference
        print(f"Task processed in {processing_time:.4f} seconds") 
    else:
        print('모아놓은 image url이 없습니다.')
        pass





#############################################################################################################################################
#############################################################################################################################################
#
#                                                      Video Scraping
#
#############################################################################################################################################
#############################################################################################################################################


#############################################################################################################################################
#############################################################################################################################################
#
#                                                       Javdatabase.com
#
#############################################################################################################################################
#############################################################################################################################################



# Update Latest Javdatabase data
@shared_task
def update_latest_javdatabase_data_to_db():
    print('# Update Latest Javdatabase data')
    random_sec = random.uniform(2, 4)
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    parsing_movie_page_completed = q_systemsettings_hansent.parsing_movie_page_completed
    list_skip_subject = ['Sperm', 'Fun', 'Cosplay', 'School', 'Tifa', 'Facial' 'Cute', 'Sucking']
    driver = boot_google_chrome_driver_in_hans_ent_task()

    print('# update 정보 획득')
    # DESTINATION_URL = 'https://www.javdatabase.com/'
    p = parsing_movie_page_completed
    p_last = p + 500
    while p < p_last:
        print('page Parsing 하기 : ', p)
        DESTINATION_URL = f'https://www.javdatabase.com/movies/page/{p}/'
        time.sleep(1)
        driver.get(DESTINATION_URL)
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')
        
        print('# Actor Info 수집')
        elements = soup.find_all(class_="idol-thumb")
        list_list_collect_data_actor = []
        i = 0
        for element in elements:
            # print('i', i)
            list_collect_data = []
            try:
                tags = element.find_all('a')
                # print(tags)
                for tag in tags:
                    if 'javdatabase.com' in str(tag):
                        href = tag.get('href')
                        name = href.split('/')[-2]
                        name = name.replace('-', ' ')
                        # print('1', href)
                        if href not in list_collect_data:
                            list_collect_data.append(href)
                        if name not in list_collect_data:
                            list_collect_data.append(name)
            except:
                pass
            try:
                tags = element.find_all('img')
                for tag in tags:
                    if 'javdatabase.com' in str(tag):
                        src = tag.get('src')
                        if src not in list_collect_data:
                            list_collect_data.append(src)
            except:
                pass
            if len(list_collect_data) > 0:
                list_list_collect_data_actor.append(list_collect_data)
            i = i + 1

        print('# Video Info 수집')
        # elements = soup.find_all(class_="movie-cover-thumb")
        elements = soup.find_all(class_="col-md-3 col-lg-2 col-xxl-2 col-4")
        list_list_collect_data_movie = []
        j = 1
        for element in elements:
            list_collect_data = []
            try:
                XPATH_TARGET = f'//*[@id="main"]/div[4]/div[{j}]/div/div/div[2]/a'
                description = driver.find_element(By.XPATH, XPATH_TARGET)
                description_text = description.text
            except:
                description_text = None
            try:
                tags = element.find_all('a')
                for tag in tags:
                    href = tag.get('href')
                    if href not in list_collect_data:
                        list_collect_data.append(href)
            except:
                pass

            try:
                tags = element.find_all('img')
                for tag in tags:
                    src = tag.get('src')
                    alt = tag.get('alt')
                    alt = alt.split(' ')[0]
                    if src not in list_collect_data:
                        list_collect_data.append(src)
                    if alt not in list_collect_data:
                        list_collect_data.append(alt)
                list_collect_data.append(description_text)
            except:
                pass
            if len(list_collect_data) > 0:
                list_list_collect_data_movie.append(list_collect_data)
            j = j + 1


        # print('list_list_collect_data_actor', list_list_collect_data_actor)
        print('# DB에 수집한 Actor 데이터 저장하기')
        if len(list_list_collect_data_actor) > 0:
            k = 0
            for list_collect_data_actor in list_list_collect_data_actor:
                # print('k', k)
                list_dict_info_url = []
                name = list_collect_data_actor[1]
                list_dict_info_url.append({
                    'info_url':list_collect_data_actor[0],
                    'cover_image_url': list_collect_data_actor[2],
                    'name': name,
                    'source_url': 'https://www.javdatabase.com',
                })

                q_actor = Actor.objects.filter(Q(name=name) & Q(category='05')).last()
                if name not in list_skip_subject:
                    if q_actor is None:
                        random_uuid = uuid.uuid4()
                        hashcode = str(random_uuid)
                        data = {
                            'hashcode': hashcode,
                            'category': '05',
                            'name': name,
                            'list_dict_info_url': list_dict_info_url,
                        }
                        q_actor = Actor.objects.create(**data)
                k = k + 1

        print('# Video Detail Info 수집')
        if list_list_collect_data_movie is not None and len(list_list_collect_data_movie) > 0:
            list_collect_data_movie_error = []
            list_dict_video_detail_info = []

            m = 0
            for list_collect_data_movie in list_list_collect_data_movie:
                # print('m', m)
                if "https://" in list_collect_data_movie[2]:
                    time.sleep(random_sec)
                    dict_video_detail_info = {}

                    video_url = list_collect_data_movie[0]
                    studio_url = list_collect_data_movie[1]
                    try:
                        studio = studio_url.split('/studios/')[-1]
                        studio = studio.replace('/', '')
                    except:
                        studio = None
                    cover_img_url = list_collect_data_movie[2]
                    code = list_collect_data_movie[3]
                    
                    try:
                        driver.get(video_url)
                        source = driver.page_source
                        soup = BeautifulSoup(source, 'html.parser')
                        
                        elements = soup.find_all(class_="col-md-10 col-lg-10 col-xxl-10 col-8")
                        
                        # print('elements', elements)
                        element = elements[0]
                        tags = element.find_all('p')
                        
                        dict_video_detail_info['code'] = code
                        dict_video_detail_info['cover_image_url'] = cover_img_url
                        dict_video_detail_info['info_url'] = video_url
                        dict_video_detail_info['studio_url'] = studio_url
                        dict_video_detail_info['studio'] = studio
                        dict_video_detail_info['source_url'] = 'https://www.javdatabase.com'

                        for tag in tags:
                            # print('tag', tag)
                            # print('tag TEXT : ', tag.text)
                            tag_text = tag.text
                            tag_text_key_str = tag_text.split(':')[0]
                            tag_text_key_str = tag_text_key_str.lower()
                            tag_text_key_str = tag_text_key_str.replace(' ', '_')
                            tag_text_key_str = tag_text_key_str.replace('title', 'description')
                            tag_text_key_str = tag_text_key_str.replace('(s)', '')
                            tag_text_key_str = tag_text_key_str.replace('(es)', '')
                            tag_text_key_str = tag_text_key_str.replace('idol/actress', 'actress')
                            
                            tag_text_value_str = tag_text.split(':')[-1]
                            tag_text_value_str = tag_text_value_str.strip()
                            dict_video_detail_info[tag_text_key_str] = tag_text_value_str

                            try:
                                tag_a = tag.find_all('a')[0]
                                url = tag_a.get('href')
                            except:
                                url = None

                            if url is not None:
                                tag_text_key_url_str = f'{tag_text_key_str}_url'
                                dict_video_detail_info[tag_text_key_url_str]= url
                            # print('dict_video_detail_info', dict_video_detail_info)

                        list_dict_video_detail_info.append(dict_video_detail_info)
                    except:
                        list_collect_data_movie_error.append(video_url)
                    m = m + 1

        # print('list_list_collect_data_movie', list_list_collect_data_movie)
        print('# DB에 수집한 Video 데이터 저장하기')
        if len(list_dict_video_detail_info) > 0:
            n = 0
            for dict_video_detail_info in list_dict_video_detail_info:
                # print('n', n)
                code = dict_video_detail_info['code']
                list_dict_info_url = []
                
                q_video = Video_Album.objects.filter(code=code).last()
                if q_video is not None:
                    list_dict_info_url = q_video.list_dict_info_url
                    if list_dict_info_url is None:
                        list_dict_info_url = []
                
                if code not in list_skip_subject:
                    # print("code", code)
                    list_dict_info_url.append(dict_video_detail_info)
                    actor_name = dict_video_detail_info['actress']
                    q_actor = Actor.objects.filter(Q(check_discard=False) & Q(name=actor_name) & Q(category='05')).last()
                    # print('q_actor', q_actor)
                    date_released_str = dict_video_detail_info['release_date']
                    import datetime
                    try:
                        date_released = datetime.strftime(date_released_str, "%Y-%m-%d")
                    except:
                        date_released = None
                    if q_video is None:
                        random_uuid = uuid.uuid4()
                        hashcode = str(random_uuid)
                        data = {
                            'main_actor': q_actor,
                            'hashcode': hashcode,
                            'category': '06',  # ('06', 'ADULT'),
                            'code': code,
                            'list_dict_info_url': list_dict_info_url,
                            'date_released': date_released,
                        }
                        q_video = Video_Album.objects.create(**data)
                        print('q_video created!!', q_video)
                    else:
                        data = {
                            'main_actor': q_actor,
                            'category': '06',  # ('06', 'ADULT'),
                            'code': code,
                            'list_dict_info_url': list_dict_info_url,
                            'date_released': date_released,
                        }
                        Video_Album.objects.filter(id=q_video.id).update(**data)
                        print('q_video Updated!!', q_video)
                n = n + 1
        
        data = {
            'parsing_movie_page_completed': p
        }
        SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
        q_systemsettings_hansent.refresh_from_db()
        
        p = p + 1
    
    driver.quit()
    print('업데이트 종료')
    return True








#############################################################################################################################################
#############################################################################################################################################
#
#                                                      Manga Scraping
#
#############################################################################################################################################
#############################################################################################################################################


#############################################################################################################################################
#############################################################################################################################################
#
#                                                       wfwfxxx.com
#
#############################################################################################################################################
#############################################################################################################################################

# 에러 리포트트
def f_report_error_manga(title, num_episode, episode_url, q_manga_album_id, contents):
    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    list_dict_report_error_manga = q_systemsettings_hansent.list_dict_report_error_manga
    if list_dict_report_error_manga is None:
        list_dict_report_error_manga = []
    list_dict_report_error_manga.append({'title':title, 'volume':num_episode, 'info_url':episode_url, 'manga_album_id': q_manga_album_id, 'contents': contents})
    data = {
        'list_dict_report_error_manga': list_dict_report_error_manga,
    }
    SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
    q_systemsettings_hansent.refresh_from_db()


# Default Manga Album 쿼리 생성
def create_manga_album_in_task():
    random_uuid = uuid.uuid4()
    hashcode = str(random_uuid)
     
    data = {
        'hashcode': hashcode,
        'dict_manga_album_cover':DEFAULT_DICT_MANGA_ALBUM_COVER,
        'list_dict_manga_album':DEFAULT_LIST_DICT_MANGA_ALBUM,
        'list_dict_volume_manga': DEFAULT_LIST_DICT_VOLUME_MANGA_INFO,
    }
    q_manga_album = Manga_Album.objects.create(**data)
    print('Manga Album 신규 생성!', q_manga_album)
    return q_manga_album


# 페이지 최하단으로 내리기 함수
def page_scroll_down_to_bottom(driver):
    random_sec = random.uniform(2, 4)
    current_path = os.getcwd()
    prev_height = driver.execute_script('return document.body.scrollHeight')

    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(random_sec)
        current_height = driver.execute_script('return document.body.scrollHeight')
        if current_height == prev_height:
            # print('arrived bottom')
            break
        prev_height = current_height


# Title별 회차 리스트 확보
def get_list_episode_url(soup, base_url):
    list_soup = soup.find_all(class_="view_open")
    list_episode_url = []
    i = 0
    for x in list_soup:
        # print('===================================', x)
        try:
            # Extract the 'href' attribute
            if x:
                href_value = x.get('href')
                episode_url = base_url+href_value
                list_episode_url.append(episode_url)
        except:
            pass
        i = i + 1
    list_episode_url.reverse()
    # print(list_episode_url)
    return list_episode_url


# Episode 내 image 주소 긁어오기
def get_list_image_url_in_episode(soup):
    list_soup = soup.find_all('img', {'class': 'v-img lazyload'})
    list_image_url = []
    i = 0
    for x in list_soup:
        try:
            if x:
                href_value = x.get('data-original')
                episode_url = href_value
                list_image_url.append(episode_url)
        except:
            pass
        i = i + 1
    # list_image_url.reverse()
    return list_image_url


# Episode / Image 긁어오기 함수
def get_image_from_episode(driver, title, num_episode, episode_url, q_manga_album_id):
    print('# Episode Image 긁어오기 함수 실행')
    
    print(f'title: {title}, num_episode: {num_episode}, episode_url:  {episode_url}, q_manga_album_id: {q_manga_album_id}')

    q_manga_album = Manga_Album.objects.get(id=q_manga_album_id)
    hashcode = q_manga_album.hashcode
    date_released = datetime.date.today()
    if date_released is not None:
        try:
            date_released_str = str(date_released.strftime("%Y-%m-%d"))
        except:
            date_released_str = 'unknown'
    else:
        date_released_str = 'unknown'
    print(f'date_released_str: {date_released_str}')
    
    # list_dict_volume_manga = []
    # list_dict_volume_manga.append({"volume": num_episode, "title": title, "list_id":[], "discard": "false", "date_released": "unknown", "last": "false" })
    list_dict_volume_manga = q_manga_album.list_dict_volume_manga
    if list_dict_volume_manga is None:
        list_dict_volume_manga = []
    list_dict_manga_album = q_manga_album.list_dict_manga_album
    if list_dict_manga_album is None:
        list_dict_manga_album = []
    list_id_manga_in_volume = []

    driver.get(episode_url)
    page_scroll_down_to_bottom(driver)
    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')

    list_image_url = get_list_image_url_in_episode(soup)

    i = len(list_dict_manga_album)
    if list_image_url is not None and len(list_image_url) > 0:
        for img_url in list_image_url:
            # file_extension = img_url.split('.')[-1]
            file_extension = 'jpg'
            image_name_original = f'{hashcode}-o-{i}.{file_extension}'
            image_name_cover = f'{hashcode}-c-{i}.{file_extension}'
            image_name_thumbnail = f'{hashcode}-t-{i}.{file_extension}'

            list_dict_manga_album.append({"id": i, "volume":num_episode, "original": image_name_original, "cover": image_name_cover, "thumbnail": image_name_thumbnail, "active":"false", "discard":"false"})
            if len(list_dict_manga_album) > 1:
                list_dict_manga_album[-2]["active"] = "false"
                list_dict_manga_album[0]["discard"] = "true"
            list_dict_manga_album[-1]["active"] = "true"
            list_id_manga_in_volume.append(i)

            save_dir = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA)
            path_file_name = os.path.join(save_dir, image_name_original)

            # 수동 파일 저장 ------------------------------------------------------------------------------------------------------------------
            # data = requests.get(img_url).content
            # with open(path_file_name, "wb") as f:
            #     f.write(data)
            try:
                with requests.get(img_url, stream=True, timeout=10) as r:
                    r.raise_for_status() 
                    with open(path_file_name, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
            except requests.exceptions.RequestException as e:
                print(f"Download failed: {e}")

            # ---------------------------------------------------------------------------------------------------------------------------------

            original_file_path = os.path.join(save_dir, image_name_original)
            try:
                image_pil = Image.open(original_file_path)
            except:
                f_report_error_manga(title, num_episode, episode_url, q_manga_album_id, contents='Parsing한 Image URL에 original 이미지가 없어 파일 저장못함')
                image_pil = None
                list_dict_manga_album = [d for d in list_dict_manga_album if d['id'] != i]
                list_id_manga_in_volume.remove(i)

            if image_pil is not None:
                file_path_cover = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA, image_name_cover)
                file_path_thumbnail = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA, image_name_thumbnail)
                # Resize Original Image for Thumbnail, Cover
                cover_pil = resize_with_padding(image_pil.copy(), 520, 640)  # Target size: 300x300 with white background
                thumbnail_pil = resize_with_padding(image_pil.copy(), 260, 320)  # Target size: 300x300 with white background
                # 커버이미지 저장
                cover_pil.save(file_path_cover)
                # 썸네일 이미지 저장
                thumbnail_pil.save(file_path_thumbnail)
            i = i + 1
        print(f'{title}: Episode - {str(num_episode)} completed!!')
    else:
        print(f'{title}: Episode - {str(num_episode)} parsing failed')
    
    list_collect_exist_voume = []
    if list_dict_volume_manga is not None and len(list_dict_volume_manga) > 0:
        for dict_volume_manga in list_dict_volume_manga:
            selected_volume = dict_volume_manga['volume']
            print(f'selected_volume: {selected_volume}')
            list_collect_exist_voume.append(int(selected_volume))
    # print('list_collect_exist_voume', list_collect_exist_voume)
    
    if num_episode not in list_collect_exist_voume:
        list_dict_volume_manga.append({"volume": num_episode, "title": title, "list_id":[], "discard": "false", "date_released": "unknown", "last": "false" })

    list_dict_manga_album[-1]["active"] = 'true'
    for dict_volume_manga in  list_dict_volume_manga:
        if dict_volume_manga['volume'] == num_episode:
            list_id_manga_in_volume_old = dict_volume_manga['list_id']
            in_first = set(list_id_manga_in_volume_old)
            in_second = set(list_id_manga_in_volume)
            in_second_but_not_in_first  = in_second - in_first 
            list_id_manga_in_volume = list_id_manga_in_volume_old + list(in_second_but_not_in_first)
            dict_volume_manga['list_id'] = list_id_manga_in_volume
            dict_volume_manga['date_released'] = date_released_str
            dict_volume_manga['title'] = title
    data = {
        'list_dict_manga_album': list_dict_manga_album,
        'list_dict_volume_manga': list_dict_volume_manga,
        'date_released': date_released,
        'check_new_volume': True,
    }
    Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
    q_manga_album.refresh_from_db()
    print(f'# Episode Image 긁어오기 함수  title: {title}, num_episode: {num_episode} 종료')



# ---------------------------------------------------------------------------------------------------------------------------------------------
# Manga Parsing 
#
"""
    # dict_manga_scheduled_to_collect = {
    #     # '혼쭐고백': f"{base_url_front}8863{base_url_back}",
    #     # '넷이선못살아': f"{base_url_front}8864{base_url_back}",
    #     # '이시국에개인교습': f"{base_url_front}5157{base_url_back}",
    #     # '미필적꼴림': f"{base_url_front}8734{base_url_back}",
    #     # '악당영애길들이기': f"{base_url_front}13493{base_url_back}",
    #     # '마사지를너무잘함': f"{base_url_front}4427{base_url_back}",
    #     # '치트타자가다따먹음': f"{base_url_front}13586{base_url_back}",
    #     # '직장관리자권한': f"{base_url_front}5187{base_url_back}",
    #     'S수업': f"{base_url}{base_url_front}71558{base_url_back}",
    #     # '결정사후기푼다': f"{base_url_front}7995{base_url_back}",
    #     # '너말고내동생': f"{base_url_front}13619{base_url_back}",
    #     # '무인도모자생존기': f"{base_url_front}8246{base_url_back}",
    #     # '비밀수업': f"{base_url_front}5370{base_url_back}",
    #     # '오늘부터친구먹자': f"{base_url_front}5172{base_url_back}",
    #     # '여름안에서': f"{base_url_front}5156{base_url_back}",
    #     # '집주인딸내미': f"{base_url_front}4960{base_url_back}",
    #     # '인턴해녀': f"{base_url_front}4572{base_url_back}",
    #     # '이웃집동창': f"{base_url_front}8973{base_url_back}",
    #     # '동아리': f"{base_url_front}4419{base_url_back}",
    #     # '섹톱워치': f"{base_url_front}5171{base_url_back}",
    #     # '건물주누나': f"{base_url_front}5176{base_url_back}",
    #     # '공대엔여신이없다': f"{base_url_front}4789{base_url_back}",
    #     # '구멍가게구멍열었습니다': f"{base_url_front}4574{base_url_back}",
    #     # '주인공이빌런임': f"{base_url_front}5386{base_url_back}",
    #     # '정자페이로결재하세요': f"{base_url_front}5379{base_url_back}",
    #     # '대물제자': f"{base_url_front}4764{base_url_back}",
    #     # '내인생떡상': f"{base_url_front}8925{base_url_back}",

    #     # '얘랑했어': f"{base_url_front}5145{base_url_back}",
    #     # '여름방학': f"{base_url_front}4784{base_url_back}",
    #     # '대학여우': f"{base_url_front}5541{base_url_back}",
    #     # '비밀친구': f"{base_url_front}5103{base_url_back}",
    #     # '동네누나': f"{base_url_front}5507{base_url_back}",
    #     # '첩': f"{base_url_front}4760{base_url_back}",
    #     # '내맘대로이세계최면': f"{base_url_front}4765{base_url_back}",
    #     }
"""
# ---------------------------------------------------------------------------------------------------------------------------------------------
@shared_task
def update_latest_manga_data_to_db():
    print('########################### update_latest_manga_data_to_db 실행')
    random_sec = random.uniform(2, 4)
    current_path = os.getcwd()
    
    # 연재 중인 타이틀 딕셔너리
    # base_url_front = "https://newtoki.vip/webtoon/"
    # base_url_back = "?toon=%EC%84%B1%EC%9D%B8%EC%9B%B9%ED%88%B0"

    q_systemsettings_hansent = SystemSettings_HansEnt.objects.filter(check_discard=False).last()
    base_url = q_systemsettings_hansent.parsing_base_url_manga
    list_dict_manga_info_for_parsing = q_systemsettings_hansent.list_dict_manga_info_for_parsing
    
    # base_url = "https://wfwf350.com/"
    base_url_front = "list?toon="
    base_url_back = ""
    # [{'title':'S수업', 'id':71558, 'completed':'false'}]
    
    # 완료되지 않은 망가 타이틀 및 접속url 확보 [{'title':'title', 'url': 'url'}]
    dict_manga_scheduled_to_collect = {}
    for dict_manga_info_for_parsing in list_dict_manga_info_for_parsing:
        if dict_manga_info_for_parsing['completed'] == 'false':
            dict_manga_scheduled_to_collect[dict_manga_info_for_parsing['title']] = f"{base_url}{base_url_front}{dict_manga_info_for_parsing['id']}{base_url_back}"
    print(f'length of dict_manga_scheduled_to_collect: {len(dict_manga_scheduled_to_collect)}')
    
    # 타이틀별 에피소드별 이미지 획득 메인 함수
    driver = boot_google_chrome_driver_in_hans_ent_task()

    list_dict_title_volume_collected = []  #[{"title": "xxx", "list_volume":[0, 1, 2, 3]},  {"title": "yyy", "list_volume":[0, 1, 2]}]
    dict_title_volume_collected = {}  #[{"xxx": [0, 1, 2, 3], "yyy": [0, 1, 2], "xxx": 'completed']
    dict_title_volume_missing = {}

    list_manga_completed_manga_id = []
    qs_manga_album = Manga_Album.objects.filter(check_discard=False)
    if qs_manga_album is not None and len(qs_manga_album) > 0:
        for q_manga_album in qs_manga_album:
            hashcode = q_manga_album.hashcode
            title = q_manga_album.title
            check_completed = q_manga_album.check_completed
            if check_completed == True:
                # dict_title_volume_collected[title] = 'completed'
                pass
            else:
                list_dict_volume_manga = q_manga_album.list_dict_volume_manga
                if list_dict_volume_manga is not None and len(list_dict_volume_manga) > 0:
                    # print(f'망가 내 volume 개수: {len(list_dict_volume_manga)}')
                    for dict_volume_manga in list_dict_volume_manga:
                        title = dict_volume_manga['title']
                        volume = dict_volume_manga['volume']
                        # Volume별 파일 존재여부 확인
                        try:
                            list_id = dict_volume_manga['list_id']
                            volume_first_id = list_id[0]
                            DOWNLOAD_MANGA_DIR = os.path.join(settings.MEDIA_ROOT, RELATIVE_PATH_MANGA)
                            test_file_name = f'{hashcode}-o-{volume_first_id}.jpg'
                            test_file_path = os.path.join(DOWNLOAD_MANGA_DIR, test_file_name)
                            if os.path.exists(test_file_path):
                                # print(f'동일한 파일이 존재합니다.')
                                check_download_manga_volume = True
                            else:
                                # print(f'동일한 파일이 없습니다. 다운로드합니다.')
                                check_download_manga_volume = False
                        except:
                            check_download_manga_volume = False
                        
                        if check_download_manga_volume == True:
                            if title in dict_title_volume_collected: 
                                dict_title_volume_collected[title].append(volume)
                            else:
                                dict_title_volume_collected[title]=[volume]
                        else:
                            if title in dict_title_volume_missing: 
                                dict_title_volume_missing[title].append(volume)
                            else:
                                dict_title_volume_missing[title]=[volume]
                else:
                    # 모은 episode가 없습니다.
                    dict_title_volume_collected[title] = None

    # print(f'length of dict_title_volume_collected {len(dict_title_volume_collected)}')
    # print(f'length of dict_title_volume_missing {len(dict_title_volume_missing)}')

    # 수집해야 하는 망가 title별로 파싱                            
    for title, url in dict_manga_scheduled_to_collect.items():
        check_new_manga = False
        print(f'title: {title}, url: {url}')
        check_episode_collected_all = False
        list_missing_episode = []
        list_collected_episode = []
        
        # 해당 title 없으면 신규 쿼리 생성
        q_manga_album = Manga_Album.objects.filter(Q(check_discard=False) & Q(title=title)).last()
        if q_manga_album is None:
            q_manga_album = create_manga_album_in_task()
            data = {
                'title': title
            }
            Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
            q_manga_album.refresh_from_db()
            check_new_manga = True
        
        # 연재 중
        driver.get(url)
        time.sleep(random_sec)
        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')
        
        # 에피소드 URL 리스트 확보하기기
        list_episode_url = get_list_episode_url(soup, base_url)

        # 에피소드 URL을 활용하여 해당 에피소드 이미지 다운받기기
        if list_episode_url is not None and len(list_episode_url) > 0:
            # try:
            #     print(f'list_episode_url: {len(list_episode_url)}')
            #     i = 0
            #     while len(list_episode_url) == 0:
            #         print(f'check base url: try {i}')
            #         check_save_new_url = True
            #         base_url_num_str = base_url.split('wfwf')[-1]
            #         base_url_num_str = base_url_num_str.split('.com')[0]
            #         base_url_num = int(base_url_num_str)
            #         base_url_num_new = base_url_num + 1
            #         base_url_num_new_str = str(base_url_num_new)
            #         base_url_new = f'https://wfwf{base_url_num_new_str}.com'

            #         url_new = url_new.split(base_url)[-1]
            #         url_new = f'{base_url_new}{url_new}'

            #         print(f'base_url_new: {base_url_new}')
            #         print(f'url_new: {url_new}')
            #         driver.get(url_new)
            #         time.sleep(random_sec)
            #         source = driver.page_source
            #         soup = BeautifulSoup(source, 'html.parser')
            #         list_episode_url = get_list_episode_url(soup, base_url_new)
            #         print(f'list_episode_url: {list_episode_url}')
            #         i = i + 1
            #         if i == 20:
            #             check_save_new_url = False
            #             break
            #     if check_save_new_url == True:
            #         data = {
            #             'parsing_base_url_manga': base_url,
            #         }
            #         SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
            #         q_systemsettings_hansent.refresh_from_db()
            #         print(f'collected working url: {base_url}')
            # except:
            #     pass

            time.sleep(random_sec)

            if check_new_manga == False:
                # Title별 긁어모은 episode 확인, 중복으로 긁어오기 방지용
                print('# Title을 모으는 중이면')
                list_collected_episode = dict_title_volume_collected[title]
                if list_collected_episode is not None:
                    print(f'list_collected_episode 1 : {len(list_collected_episode)}')
                    if len(list_episode_url) == len(list_collected_episode):
                        # 웹페이지 리스트의 긁어모은 Episode 개수와 저장된 Episode 개수가 일치하면
                        check_episode_collected_all = True
                    else:
                        # 웹페이지 리스트의 긁어모은 Episode 개수와 저장된 Episode 개수가 불일치하면
                        # 빈 곳을 찾아서 긁어온다. 빈 곳(긁어오지 못한 Episode를 찾아라)
                        num_episode = len(list_collected_episode) + 1
                        print(f'num_episode, {num_episode}')
                        i = 0
                        while i < len(list_episode_url):
                            if i in list_collected_episode:
                                pass
                            else:
                                list_missing_episode.append(i)
                            i = i + 1
                else:
                    num_episode = 0
                    print(f'list_collected_episode 1 : None')
                print(f'list_missing_episode 1 : {len(list_missing_episode)}')
            else:
                num_episode = 0

            # 에피소드 이미지 긁어오기기
            if q_manga_album is not None:
                check_new_volume = q_manga_album.check_new_volume
                q_manga_album_id = q_manga_album.id
                try:
                    print(f'len(list_episode_url): {len(list_episode_url)}')
                except:
                    pass

                if check_episode_collected_all == False:
                    print('# Title별 episode 긁어오기 함수 실행')
                    if len(list_missing_episode) == 0:
                        print('# 모아놓은 Episode가 없으면')
                        if num_episode == 0:
                            print('# 신규 Title이면 처음부터 긁어모으기')
                            for episode_url in list_episode_url:
                                time.sleep(random_sec)
                                print(f'title : {title},  episode : {num_episode}')
                                get_image_from_episode(driver, title, num_episode, episode_url, q_manga_album_id)
                                num_episode = num_episode + 1
                        else:
                            print('Error!, 빼먹은 Episode가 없으면서 신규 Title인데 Episode 1이 없는 경우')
                            pass
                    else:
                        print('# 일부 Episode가 있으면')
                        for episode_num_missing in list_missing_episode:
                            episode_url = list_episode_url[episode_num_missing - 1]
                            time.sleep(random_sec)
                            print(f'title : {title},  episode : {episode_num_missing}')
                            get_image_from_episode(driver, title, episode_num_missing, episode_url, q_manga_album_id)
                    check_new_volume = True
                else:
                    print('모든 Episod 모은 상태임')
                    check_new_volume = False
                    pass

            print(f'{title} update completed')
            time.sleep(random_sec)

            # 업데이트된 현재 선택된 타이틀의 볼륨별 정보 리스트
            q_manga_album.refresh_from_db()
            list_dict_volume_manga = q_manga_album.list_dict_volume_manga
            if list_dict_volume_manga is not None and len(list_dict_volume_manga) > 0:
                last_volume = len(list_dict_volume_manga) - 1
            else:
                last_volume = 0

            # system settings 값 업데이트            
            for dict_manga_info_for_parsing in list_dict_manga_info_for_parsing:
                if dict_manga_info_for_parsing['title'] == title:
                    if list_dict_volume_manga is not None:
                        dict_manga_info_for_parsing['last_volume'] = last_volume
            data = {
                'list_dict_manga_info_for_parsing': list_dict_manga_info_for_parsing
                }
            SystemSettings_HansEnt.objects.filter(id=q_systemsettings_hansent.id).update(**data)
            q_systemsettings_hansent.refresh_from_db()
        
            # Manga Album Update
            data = {
                'last_volume': last_volume,
                'check_new_volume': check_new_volume
                }
            Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
            q_manga_album.refresh_from_db()

            if check_new_volume == True:
                date_released = datetime.date.today()
                data = {
                'date_released': date_released,
                }
            Manga_Album.objects.filter(id=q_manga_album.id).update(**data)
            q_manga_album.refresh_from_db()
        
        else:
            print('collected episode url is none')
            pass
    
    driver.quit()
    print('업데이트 종료')
    return True
    


































