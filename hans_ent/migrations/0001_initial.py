# Generated by Django 5.1 on 2024-08-12 07:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('synonyms', models.JSONField(blank=True, null=True)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('date_birth', models.DateField(blank=True, null=True)),
                ('locations', models.CharField(blank=True, choices=[('01', 'KOREA'), ('02', 'JAPAN'), ('03', 'CHINA'), ('04', 'MIDDLE_EAST'), ('05', 'EUROP'), ('06', 'NORTH_AMERICA'), ('07', 'SOUTH_AMERICA'), ('08', 'AFRICA'), ('09', 'ETC')], default='01', max_length=50)),
                ('evaluation', models.FloatField(default=0)),
                ('list_dict_info_url', models.TextField(blank=True, null=True)),
                ('list_actor_picture_id', models.JSONField(blank=True, null=True)),
                ('date_created', models.DateField(auto_now_add=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True, null=True)),
                ('check_discard', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Actor_Pic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=250, null=True)),
                ('image_thumbnail', models.ImageField(blank=True, null=True, upload_to='')),
                ('image_original', models.ImageField(blank=True, null=True, upload_to='')),
                ('check_discard', models.BooleanField(default=False)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hans_ent.actor')),
            ],
        ),
    ]
