# Generated by Django 5.1 on 2024-08-13 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hans_ent', '0013_alter_actor_list_dict_info_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='height',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
