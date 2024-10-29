from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, UserProfileForm

User = get_user_model()


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"您已成功登录为 {username}。")
                return redirect('home')  # 假设您有一个名为 'home' 的URL
            else:
                messages.error(request, "用户名或密码无效。")
        else:
            messages.error(request, "用户名或密码无效。")
    form = AuthenticationForm()
    return render(request=request, template_name="users/login.html", context={"login_form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "您已成功退出登录。")
    return redirect('home')  # 假设您有一个名为 'home' 的URL


@csrf_protect
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'账号已创建，{username}！您现在可以登录了。')
            return redirect('users:login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'register_form': form})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料已更新成功！')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})
