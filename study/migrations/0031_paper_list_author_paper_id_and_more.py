# Generated by Django 5.1 on 2024-10-30 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0030_paper_first_author_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='list_author_paper_id',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='paper',
            name='list_dict_relevant_paper',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='paper',
            name='list_relevant_paper_id',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
