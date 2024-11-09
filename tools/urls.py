from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('bill-ocr/', views.bill_ocr, name='bill_ocr'),
]