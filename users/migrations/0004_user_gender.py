# Generated by Django 5.1.2 on 2024-10-30 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_real_name_alter_invitationcode_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', '男'), ('F', '女'), ('O', '其他')], max_length=1, null=True, verbose_name='性别'),
        ),
    ]
