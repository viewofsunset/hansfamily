# Generated by Django 5.1 on 2024-12-28 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hans_ent', '0071_systemsettings_hansent_parsing_picture_end_page_4khd'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemsettings_hansent',
            name='list_picture_id_parsing_error',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
