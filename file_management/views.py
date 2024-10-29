from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import UploadedFile

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def file_list(request):
    search_query = request.GET.get('search', '')
    file_type = request.GET.get('file_type', '')
    
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    
    if search_query:
        files = files.filter(file__icontains=search_query)
    
    if file_type:
        files = files.filter(file__endswith=file_type)
    
    context = {
        'files': files,
        'search_query': search_query,
        'file_type': file_type,
    }
    return render(request, 'file_management/file_list.html', context)

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
                file_name=uploaded_file.name,
                description=description,
                uploaded_by=request.user
            )
            file_instance.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
                
            messages.success(request, '文件上传成功！')
            return redirect('file_management:file_list')
            
        except Exception as e:
            messages.error(request, f'上传失败：{str(e)}')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            return render(request, 'file_management/upload_file.html')
            
    return render(request, 'file_management/upload_file.html')

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    
    if request.user == file.uploaded_by or request.user.is_staff:
        file_name = file.file.name
        file.file.delete()  # 删除实际文件
        file.delete()       # 删除数据库记录
        messages.success(request, f'文件 "{file_name}" 已成功删除。')
    else:
        messages.error(request, '您没有权限删除此文件。')
    
    return redirect('file_management:file_list')
