# Generated by Django 5.1 on 2024-08-13 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hans_ent', '0005_mysettings_hansent_check_discard'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysettings_hansent',
            name='check_field_ascending_actor',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='mysettings_hansent',
            name='selected_field_actor',
            field=models.CharField(blank=True, default='id', max_length=50),
        ),
    ]
