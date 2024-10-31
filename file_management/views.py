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
        return JsonResponse({'success': False, 'error': '未指定项目'}, status=400)
        
    try:
        categories = FileCategory.objects.filter(project_id=project_id)
        category_data = [
            {
                'id': category.id,
                'parent_id': category.parent_id,
                'name': category.name
            }
            for category in categories
        ]
        
        return JsonResponse({
            'success': True,
            'categories': category_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@custom_login_required
def create_category(request):
    """创建新分类"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '不支持的请求方法'}, status=400)
    
    try:
        # 打印接收到的数据，用于调试
        print("Received data:", request.body.decode('utf-8'))
        
        data = json.loads(request.body)
        name = data.get('name')
        project_id = data.get('project_id')
        parent_id = data.get('parent_id')
        
        # 验证必要参数
        if not name or not project_id:
            return JsonResponse({
                'success': False, 
                'error': f'缺少必要参数: name={name}, project_id={project_id}'
            }, status=400)
            
        # 创建分类
        category = FileCategory(
            name=name,
            project_id=project_id
        )
        
        if parent_id:
            try:
                parent = FileCategory.objects.get(id=parent_id)
                category.parent = parent
            except FileCategory.DoesNotExist:
                return JsonResponse({'success': False, 'error': '父分类不存在'}, status=400)
        
        category.save()
        
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'parent_id': category.parent_id
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        print("Error creating category:", str(e))  # 添加错误日志
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@custom_login_required
def manage_categories(request):
    """分类管理页面"""
    context = {
        'projects': Project.objects.all()  # 暂时显示所有项目
    }
    return render(request, 'file_management/manage_categories.html', context)

@custom_login_required
def delete_category(request):
    """删除分类"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '不支持的请求方法'}, status=400)
    
    try:
        data = json.loads(request.body)
        category_id = data.get('id')
        
        if not category_id:
            return JsonResponse({'success': False, 'error': '未指定分类ID'}, status=400)
            
        category = FileCategory.objects.get(id=category_id)
        
        # 检查是否有子分类
        if category.children.exists():
            return JsonResponse({
                'success': False, 
                'error': '该分类下还有子分类，请先删除子分类'
            }, status=400)
            
        # 检查是否有关联的文件
        if category.get_files().exists():
            return JsonResponse({
                'success': False, 
                'error': '该分类下还有文件，请先移除或删除相关文件'
            }, status=400)
            
        # 执行删除操作
        category.delete()
        return JsonResponse({'success': True})
        
    except FileCategory.DoesNotExist:
        return JsonResponse({'success': False, 'error': '分类不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def update_category_order(request):
    """更新分类顺序"""
    if request.method != 'POST':
        return JsonResponse({'error': '不支持的请求方法'}, status=400)
    
    try:
        data = json.loads(request.body)
        for item in data:
            category = FileCategory.objects.get(id=item['id'])
            category.parent_id = item.get('parent_id')
            category.order = item.get('order', 0)
            category.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@custom_login_required
def update_category(request):
    """更新分类名称"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '不支持的请求方法'}, status=400)
    
    try:
        data = json.loads(request.body)
        category_id = data.get('id')
        new_name = data.get('name')
        
        if not all([category_id, new_name]):
            return JsonResponse({'success': False, 'error': '参数不完整'}, status=400)
            
        category = FileCategory.objects.get(id=category_id)
        category.name = new_name
        category.save()
        
        return JsonResponse({'success': True})
    except FileCategory.DoesNotExist:
        return JsonResponse({'success': False, 'error': '分类不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)