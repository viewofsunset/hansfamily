import os
from celery import Celery
from celery.schedules import schedule
from celery.schedules import crontab

from datetime import timedelta
from django.conf import settings
from django.db.utils import OperationalError
import datetime
import pytz
nowfun = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
print('nowfun', nowfun)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hansfamily.settings')

app = Celery('hansfamily')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    task_time_limit=60*60*24*7,  # Time limit for tasks (one week)
    broker_url='redis://localhost:6379/0',  # Update with your broker settings
    result_backend='redis://localhost:6379/0',  # Update with your backend settings
    beat_scheduler='django_celery_beat.schedulers.DatabaseScheduler',  # Only if using django-celery-beat
    broker_connection_retry_on_startup = True # Retain the behavior to retry broker connections on startup
)

# # Set the timezone to Asia/Seoul
# app.conf.timezone = 'Asia/Seoul'
# app.conf.enable_utc = False  # Disable UTC, use local time (Asia/Seoul)


# Optional: Set a global timezone (can be UTC or any timezone)
app.conf.timezone = 'Asia/Seoul'  # This can be left as UTC or set to a default timezone
# app.conf.enable_utc = True  # Enable UTC by default
app.conf.enable_utc = False  # Enable UTC by default


app.conf.beat_schedule = {
    'task-every-day-at-130am': {
        'task': 'hans_ent.tasks.update_latest_manga_data_to_db',
        'schedule': crontab(hour=1, minute=30, nowfun='Asia/Seoul'),  # Set timezone here
        'args': [],
    },
    'task-every-day-at-200am': {
        'task': 'hans_ent.tasks.update_latest_4khd_data_to_db',
        'schedule': crontab(hour=2, minute=0, nowfun=nowfun),  # Set timezone here
        'args': [],
    },
    'task-every-day-at-230am': {
        'task': 'hans_ent.tasks.download_image_using_url_w_multiprocessing1',
        'schedule': crontab(hour=2, minute=30, nowfun='Asia/Seoul'),  # Set timezone here
        'args': [],
    },
}

# app.conf.beat_schedule = {
#     'task-every-day-at-130am': {
#         'task': 'hans_ent.tasks.update_latest_manga_data_to_db', 
#         'schedule': crontab(hour=1, minute=30), 
#     },
#     'task-every-day-at-200am': {
#         'task': 'hans_ent.tasks.update_latest_4khd_data_to_db',  # Replace with your task name
#         'schedule': crontab(hour=2, minute=0,),  # Schedule it to run daily at 02:00 AM
#     },
#     'task-every-day-at-230am': {
#         'task': 'hans_ent.tasks.download_image_using_url_w_multiprocessing1',  # Replace with your task name
#         'schedule': crontab(hour=2, minute=30),  # Schedule it to run daily at 02:00 AM
#     },
# }


# Automatically discover tasks from all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)



# @app.task(bind=True, ignore_result=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')







    # 'task-every-30-seconds': {
    #     'task': 'study.tasks.your_task0',  # Use the dotted path to your task
    #     # 'schedule': schedule(30.0),  # Run every 10 seconds
    #     'schedule': timedelta(seconds=10),
    #     # 'schedule': timedelta(minutes=2),  # Run every 2 minutes
    # },
    # 'task-every-day-at-2am': {
    #     'task': 'study.tasks.your_task1',  # Replace with your task name
    #     'schedule': crontab(hour=20, minute=22),  # Schedule it to run daily at 02:00 AM
    # },
    # 'task-every-1-minutes': {
    #     'task': 'study.tasks.your_task2',  # Replace with your task's path
    #     'schedule': crontab(minute='*/1'),  # This runs the task every 10 minutes
    # },
    # 'task-every-two-minutes': {
    #     'task': 'study.tasks.your_task3',  # Replace with your task's path
    #     'schedule': crontab(minute='*/2'),  # This runs the task every 2 minutes
    # },
    # 'task-every-10-minutes': {
    #     'task': 'study.tasks.your_task4',  # Replace with your task's path
    #     'schedule': crontab(minute='*/10'),  # This runs the task every 10 minutes
    # },
