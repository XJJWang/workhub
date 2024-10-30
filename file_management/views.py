from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import UploadedFile, FileCategory
from project_management.models import Project
from users.decorators import custom_login_required
from django.core.serializers.json import DjangoJSONEncoder
import json

User = get_user_model()

@custom_login_required
def upload_file(request):
    if request.method == 'GET':
        projects = Project.objects.all().order_by('-year', 'name')
        categories = FileCategory.objects.all()
        
        # 准备分类数据
        category_data = [
            {
                'id': str(category.id),
                'parent': str(category.parent_id) if category.parent_id else '#',
                'text': category.name
            }
            for category in categories
        ]
        
        return render(request, 'file_management/upload_file.html', {
            'projects': projects,
            'categories': categories,
            'category_data_json': json.dumps(category_data, cls=DjangoJSONEncoder)
        })
    
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'error': '请选择要上传的文件'}, status=400)
        
        try:
            uploaded_file = request.FILES['file']
            description = request.POST.get('description', '')
            project_id = request.POST.get('project_id')
            category_id = request.POST.get('category_id')
            
            if not description:
                return JsonResponse({'error': '请填写文件描述'}, status=400)
            
            file_instance = UploadedFile(
                file=uploaded_file,
                file_name=uploaded_file.name,
                description=description,
                uploaded_by=request.user
            )
            
            if project_id:
                file_instance.project_id = project_id
                
            if category_id:
                file_instance.category_id = category_id
                
            file_instance.save()
            
            return JsonResponse({'message': '文件上传成功'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@custom_login_required
def file_list(request):
    search_query = request.GET.get('search', '')
    file_type = request.GET.get('file_type', '')
    project_id = request.GET.get('project', '')
    date_range = request.GET.get('date_range', '')
    uploader = request.GET.get('uploader', '')
    category_id = request.GET.get('category', '')
    
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    
    if search_query:
        files = files.filter(
            Q(file_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if file_type:
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
        if date_range == 'today':
            files = files.filter(uploaded_at__date=timezone.now().date())
        elif date_range == 'week':
            files = files.filter(uploaded_at__gte=timezone.now() - timedelta(days=7))
        elif date_range == 'month':
            files = files.filter(uploaded_at__gte=timezone.now() - timedelta(days=30))
            
    if category_id:
        category = get_object_or_404(FileCategory, id=category_id)
        descendant_categories = category.get_descendants(include_self=True)
        files = files.filter(category__in=descendant_categories)
    
    projects = Project.objects.all().order_by('-year', 'name')
    uploaders = User.objects.filter(uploadedfile__isnull=False).distinct()
    categories = FileCategory.objects.all()
    current_category = FileCategory.objects.get(id=category_id) if category_id else None
    
    context = {
        'files': files,
        'search_query': search_query,
        'file_type': file_type,
        'projects': projects,
        'selected_project': project_id,
        'date_range': date_range,
        'uploader': uploader,
        'uploaders': uploaders,
        'categories': categories,
        'current_category': current_category,
        'selected_category': category_id,
    }
    return render(request, 'file_management/file_list.html', context)

@custom_login_required
def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    
    # 检查权限：只有文件上传者或管理员可以删除文件
    if request.user != file.uploaded_by and not request.user.is_staff:
        messages.error(request, '您没有权限删除此文件')
        return redirect('file_management:file_list')
    
    try:
        file.file.delete()  # 删除物理文件
        file.delete()  # 删除数据库记录
        messages.success(request, '文件已成功删除')
    except Exception as e:
        messages.error(request, f'删除文件时出错：{str(e)}')
    
    return redirect('file_management:file_list')

@custom_login_required
def get_project_categories(request):
    """获取指定项目的分类树"""
    project_id = request.GET.get('project_id')
    if not project_id:
        return JsonResponse({'error': '未指定项目'}, status=400)
        
    categories = FileCategory.objects.filter(project_id=project_id)
    category_data = [
        {
            'id': str(category.id),
            'parent': str(category.parent_id) if category.parent_id else '#',
            'text': category.name
        }
        for category in categories
    ]
    
    return JsonResponse(category_data, safe=False)

@custom_login_required
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent_id')
        project_id = request.POST.get('project_id')  # 添加项目ID
        
        if not all([name, project_id]):
            return JsonResponse({'error': '缺少必要参数'}, status=400)
            
        try:
            category = FileCategory(
                name=name,
                project_id=project_id
            )
            if parent_id:
                category.parent_id = parent_id
            category.save()
            
            return JsonResponse({
                'id': category.id,
                'name': category.name,
                'parent_id': category.parent_id
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': '无效请求'}, status=400)