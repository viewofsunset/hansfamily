# Generated by Django 5.1 on 2024-08-24 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hans_ent', '0025_music_album_list_dict_picture_album_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysettings_hansent',
            name='list_dict_history_actor_select',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
