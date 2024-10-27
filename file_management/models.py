from django.db import models
from django.conf import settings  # 导入settings
from django.contrib.auth import get_user_model  # 导入get_user_model

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')  # 文件字段
    description = models.CharField(max_length=255)  # 描述字段
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 更新为使用settings.AUTH_USER_MODEL
    uploaded_at = models.DateTimeField(auto_now_add=True)  # 上传时间

    def __str__(self):
        return self.file.name
