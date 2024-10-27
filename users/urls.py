from django.urls import path
from . import views

app_name = 'users'  # 添加这行来设置命名空间

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    # 其他 URL 模式...
]