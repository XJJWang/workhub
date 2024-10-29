from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name='项目名称')
    short_name = models.CharField(max_length=50, verbose_name='项目简称')
    year = models.IntegerField(verbose_name='年份')

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'
        ordering = ['-year', 'name']  # 按年份降序，同年份按名称升序排列

    def __str__(self):
        return f"{self.year}-{self.short_name}"