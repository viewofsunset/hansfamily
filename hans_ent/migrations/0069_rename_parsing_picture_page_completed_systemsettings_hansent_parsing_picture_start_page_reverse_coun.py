# Generated by Django 5.1 on 2024-10-20 05:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hans_ent', '0068_rename_list_dict_gallery_info_picture_album_dict_gallery_info'),
    ]

    operations = [
        migrations.RenameField(
            model_name='systemsettings_hansent',
            old_name='parsing_picture_page_completed',
            new_name='parsing_picture_start_page_reverse_count',
        ),
    ]
