from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import UploadedFile

def file_list(request):
    files = UploadedFile.objects.all()  # 获取所有已上传的文件
    return render(request, 'file_management/file_list.html', {'files': files})

def upload_file(request):
    if request.method == 'POST':
        try:
            if 'file' not in request.FILES:
                messages.error(request, '请选择要上传的文件')
                return render(request, 'file_management/upload_file.html')
                
            uploaded_file = request.FILES['file']
            description = request.POST.get('description', '')
            
            file_instance = UploadedFile(
                file=uploaded_file,
                description=description,
                uploaded_by=request.user
            )
            file_instance.save()
            
            messages.success(request, '文件上传成功！')
            return redirect('file_management:file_list')
            
        except Exception as e:
            messages.error(request, f'上传失败：{str(e)}')
            return render(request, 'file_management/upload_file.html')
            
    return render(request, 'file_management/upload_file.html')
