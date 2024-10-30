from django.urls import path
from . import views

app_name = 'file_management'

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('upload/', views.upload_file, name='upload_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('create-category/', views.create_category, name='create_category'),
    path('get-project-categories/', views.get_project_categories, name='get_project_categories'),
]
