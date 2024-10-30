from django.db import models
from django.conf import settings  # 导入settings
from django.contrib.auth import get_user_model  # 导入get_user_model
from mptt.models import MPTTModel

class FileCategory(MPTTModel):
    name = models.CharField(max_length=100, verbose_name='分类名称')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='父分类')
    project = models.ForeignKey('project_management.Project', on_delete=models.CASCADE, verbose_name='所属项目')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = '文件分类'
        verbose_name_plural = '文件分类'

    def __str__(self):
        return self.name

    # 添加获取关联文件的方法
    def get_files(self):
        return UploadedFile.objects.filter(category=self)

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name='文件')
    file_name = models.CharField(max_length=255, verbose_name='文件名')
    description = models.TextField(null=True, blank=True, verbose_name='描述')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='上传者')
    project = models.ForeignKey('project_management.Project', on_delete=models.SET_NULL, 
                              null=True, blank=True, verbose_name='所属项目')
    category = models.ForeignKey(FileCategory, on_delete=models.SET_NULL, 
                               null=True, blank=True, verbose_name='文件分类')

    def save(self, *args, **kwargs):
        if not self.file_name and self.file:
            self.file_name = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name or self.file.name
