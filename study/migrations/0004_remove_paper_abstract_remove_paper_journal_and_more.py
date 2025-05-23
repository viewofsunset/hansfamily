# Generated by Django 5.1 on 2024-10-16 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0003_rename_list_dict_paper_info_paper_search_google_list_dict_paper_info_from_google'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paper',
            name='abstract',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='journal',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='list_authors',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='list_references',
        ),
        migrations.AddField(
            model_name='paper',
            name='dict_pdf_info_from_journal',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='paper_search_google',
            name='list_dup_remove_dict_pdf_info_from_journal',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='paper_search_google',
            name='list_related_paper_id',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
