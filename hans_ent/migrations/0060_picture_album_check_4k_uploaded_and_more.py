# Generated by Django 5.1 on 2024-10-10 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hans_ent', '0059_picture_album_picture_download_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='picture_album',
            name='check_4k_uploaded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='picture_album',
            name='check_url_downloaded',
            field=models.BooleanField(default=False),
        ),
    ]
