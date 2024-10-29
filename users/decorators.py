from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def custom_login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    自定义登录要求装饰器，在重定向到登录页面前添加提示消息
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            messages.warning(request, '请先登录后再访问该页面。')
            return redirect(login_url or 'users:login')
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator