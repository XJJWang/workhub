from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .models import UploadedFile

def file_list(request):
    files = UploadedFile.objects.all()  # 获取所有已上传的文件
    return render(request, 'file_management/file_list.html', {'files': files})

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        description = request.POST.get('description')  # 获取描述
        fs = FileSystemStorage()
        file_instance = UploadedFile(file=uploaded_file, description=description, uploaded_by=request.user)  # 创建文件实例
        file_instance.save()  # 保存文件实例
        return redirect('file_management:file_list')  # 上传成功后重定向到文件列表
    return render(request, 'file_management/upload_file.html')
