from django.shortcuts import render

def file_list(request):
    # 这里暂时返回一个简单的响应
    return render(request, 'file_management/file_list.html')