from django.shortcuts import render
from .utils import get_nearest_birthday_user, get_next_birthday, get_days_until_birthday
from datetime import date

def home(request):
    nearest_user = get_nearest_birthday_user()
    context = {
        'nearest_user': nearest_user,
    }
    
    if nearest_user:
        next_birthday = get_next_birthday(nearest_user)
        days_until = get_days_until_birthday(nearest_user)
        
        context.update({
            'next_birthday': next_birthday,
            'days_until_birthday': days_until,
            'calendar_type': nearest_user.get_calendar_type_display(),
            'is_birthday': days_until == 0  # 判断是否是生日当天
        })
    
    return render(request, 'home.html', context)