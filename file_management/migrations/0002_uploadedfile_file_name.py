# Generated by Django 5.1.2 on 2024-10-29 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedfile',
            name='file_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]