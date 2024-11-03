from datetime import datetime, date
from lunar_python import Lunar, Solar
import calendar

def calculate_solar_birthday(birth_date):
    """计算下一个阳历生日"""
    if not birth_date:
        return None
        
    today = date.today()
    this_year_birthday = date(today.year, birth_date.month, birth_date.day)
    
    # 如果今年的生日已经过了，计算明年的生日
    if this_year_birthday < today:
        next_birthday = date(today.year + 1, birth_date.month, birth_date.day)
    else:
        next_birthday = this_year_birthday
        
    return next_birthday

def calculate_lunar_birthday(birth_date):
    """计算下一个农历生日对应的阳历日期"""
    if not birth_date:
        return None
        
    # 将 date 转换为 datetime
    birth_datetime = datetime.combine(birth_date, datetime.min.time())
    
    # 将生日转换为农历日期
    solar = Solar.fromDate(birth_datetime)
    lunar = Lunar.fromSolar(solar)
    lunar_month = lunar.getMonth()
    lunar_day = lunar.getDay()
    
    # 获取当前日期
    today = date.today()
    
    # 计算今年的农历生日对应的阳历日期
    this_year_lunar = Lunar(today.year, lunar_month, lunar_day, 0, 0, 0)
    this_year_solar = this_year_lunar.getSolar()
    this_year_birthday = date(this_year_solar.getYear(), 
                            this_year_solar.getMonth(), 
                            this_year_solar.getDay())
    
    # 如果今年的生日已过，计算明年的农历生日
    if this_year_birthday < today:
        next_year_lunar = Lunar(today.year + 1, lunar_month, lunar_day, 0, 0, 0)
        next_year_solar = next_year_lunar.getSolar()
        next_birthday = date(next_year_solar.getYear(),
                           next_year_solar.getMonth(),
                           next_year_solar.getDay())
    else:
        next_birthday = this_year_birthday
        
    return next_birthday

def get_next_birthday(user):
    """获取用户的下一个生日日期"""
    if not user.birth_date:
        return None
        
    if user.calendar_type == 'solar':
        return calculate_solar_birthday(user.birth_date)
    else:
        return calculate_lunar_birthday(user.birth_date)

def get_days_until_birthday(user):
    """计算距离下一个生日还有多少天"""
    next_birthday = get_next_birthday(user)
    if not next_birthday:
        return None
        
    today = date.today()
    delta = next_birthday - today
    return delta.days

def get_nearest_birthday_user():
    """获取最近要过生日的用户"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # 获取所有设置了生日的用户
    users = User.objects.exclude(birth_date__isnull=True)
    
    # 如果没有用户设置生日，返回 None
    if not users.exists():
        return None
    
    # 计算每个用户的下一个生日，并找出最近的
    nearest_user = None
    min_days = float('inf')
    
    for user in users:
        next_birthday = get_next_birthday(user)
        if next_birthday:
            days = (next_birthday - date.today()).days
            if days < min_days:
                min_days = days
                nearest_user = user
    
    return nearest_user