from django.urls import path
from . import views

app_name = 'file_management'

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('upload/', views.upload_file, name='upload_file'),  # 添加上传文件的路径
]
