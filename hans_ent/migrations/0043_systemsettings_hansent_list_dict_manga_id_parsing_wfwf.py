# Generated by Django 5.1 on 2024-09-30 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hans_ent', '0042_video_album_check_uploaded'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemsettings_hansent',
            name='list_dict_manga_id_parsing_wfwf',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
