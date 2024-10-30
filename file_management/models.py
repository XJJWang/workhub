from django.db import models
from django.conf import settings  # 导入settings
from django.contrib.auth import get_user_model  # 导入get_user_model

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')  # 文件字段
    file_name = models.CharField(max_length=255, blank=True)  # 添加文件名字段
    description = models.CharField(max_length=255, blank=True, null=True)  # 修改这里，允许为空
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 更新为使用settings.AUTH_USER_MODEL
    uploaded_at = models.DateTimeField(auto_now_add=True)  # 上传时间
    project = models.ForeignKey('project_management.Project', on_delete=models.SET_NULL, null=True, verbose_name='所属项目')  # 添加这行

    def save(self, *args, **kwargs):
        if not self.file_name and self.file:
            self.file_name = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name or self.file.name
