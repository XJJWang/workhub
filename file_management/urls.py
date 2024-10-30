from django.urls import path
from . import views

app_name = 'file_management'

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('upload/', views.upload_file, name='upload_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('create-category/', views.create_category, name='create_category'),
    path('get-project-categories/', views.get_project_categories, name='get_project_categories'),
    path('categories/manage/', views.manage_categories, name='manage_categories'),
    path('categories/delete/', views.delete_category, name='delete_category'),
    path('categories/update-order/', views.update_category_order, name='update_category_order'),
    path('categories/update/', views.update_category, name='update_category'),
]
