from django.db import models
from django.contrib.auth.models import AbstractUser

import random
import string
# Create your models here.


class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ]
    
    real_name = models.CharField(max_length=50, blank=True, verbose_name='真实姓名')
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES, 
        blank=True, 
        null=True,
        verbose_name='性别'
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


def generate_invitation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class InvitationCode(models.Model):
    code = models.CharField(max_length=8, unique=True, default=generate_invitation_code)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.code
