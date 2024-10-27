from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # 将主页面设置为网站根路径
    path('users/', include('users.urls')),
    path('files/', include('file_management.urls')),
]