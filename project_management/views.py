from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Project
from .forms import ProjectForm

@login_required
def project_list(request):
    """项目列表视图"""
    projects = Project.objects.all().order_by('-year', 'name')
    return render(request, 'project_management/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    """创建项目视图"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, '项目创建成功！')
            return redirect('project_management:project_list')
    else:
        form = ProjectForm()
    return render(request, 'project_management/project_form.html', {
        'form': form,
        'title': '创建项目'
    })

@login_required
def project_detail(request, project_id):
    """项目详情视图"""
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'project_management/project_detail.html', {'project': project})

@login_required
def project_edit(request, project_id):
    """编辑项目视图"""
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, '项目更新成功！')
            return redirect('project_management:project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project_management/project_form.html', {
        'form': form,
        'title': '编辑项目'
    })

@login_required
@require_POST
def project_delete(request, project_id):
    """删除项目视图"""
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    return JsonResponse({'status': 'success'})
