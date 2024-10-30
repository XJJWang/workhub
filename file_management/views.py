from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import UploadedFile
from users.decorators import custom_login_required  # 导入自定义装饰器
from django.db.models import Q

from django.http import JsonResponse

from project_management.models import Project
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
User = get_user_model()

@custom_login_required
def file_list(request):
    search_query = request.GET.get('search', '')
    file_type = request.GET.get('file_type', '')
    project_id = request.GET.get('project', '')  # 添加项目筛选
    date_range = request.GET.get('date_range', '')  # 添加日期范围筛选
    uploader = request.GET.get('uploader', '')  # 添加上传者筛选
    
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    
    if search_query:
        # 扩展搜索范围到文件名、描述
        files = files.filter(
            Q(file_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if file_type:
        # 处理多个文件类型的情况
        if ',' in file_type:
            file_types = file_type.split(',')
            file_query = Q()
            for ft in file_types:
                file_query |= Q(file__endswith=ft)
            files = files.filter(file_query)
        else:
            files = files.filter(file__endswith=file_type)
    
    if project_id:
        files = files.filter(project_id=project_id)
        
    if uploader:
        files = files.filter(uploaded_by__username__icontains=uploader)
        
    if date_range:
        # 处理日期范围筛选
        if date_range == 'today':
            files = files.filter(uploaded_at__date=timezone.now().date())
        elif date_range == 'week':
            files = files.filter(uploaded_at__gte=timezone.now() - timedelta(days=7))
        elif date_range == 'month':
            files = files.filter(uploaded_at__gte=timezone.now() - timedelta(days=30))
    
    # 获取所有项目和上传者，用于筛选选项
    projects = Project.objects.all().order_by('-year', 'name')
    uploaders = User.objects.filter(uploadedfile__isnull=False).distinct()
    
    context = {
        'files': files,
        'search_query': search_query,
        'file_type': file_type,
        'projects': projects,
        'selected_project': project_id,
        'date_range': date_range,
        'uploader': uploader,
        'uploaders': uploaders,
    }
    return render(request, 'file_management/file_list.html', context)
@custom_login_required
def upload_file(request):
    if request.method == 'GET':
        projects = Project.objects.all().order_by('-year', 'name')
        return render(request, 'file_management/upload_file.html', {'projects': projects})
    if request.method == 'POST':
        try:
            if 'file' not in request.FILES:
                messages.error(request, '请选择要上传的文件')
                return render(request, 'file_management/upload_file.html')
                
            uploaded_file = request.FILES['file']
            description = request.POST.get('description', '')
            project_id = request.POST.get('project_id')
            
            file_instance = UploadedFile(
                file=uploaded_file,
                file_name=uploaded_file.name,
                description=description,
                uploaded_by=request.user,
                project_id=project_id
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

@custom_login_required
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
