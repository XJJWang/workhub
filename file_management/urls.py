from django.urls import path
from . import views

app_name = 'file_management'

urlpatterns = [
    path('', views.file_list, name='file_list'),
]