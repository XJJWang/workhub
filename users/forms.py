from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import InvitationCode


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    invitation_code = forms.CharField(
        max_length=20, required=True, help_text='请输入邀请码')

    class Meta:
        model = User
        fields = ("username", "email", "password1",
                  "password2", "invitation_code")

    def clean_invitation_code(self):
        code = self.cleaned_data.get('invitation_code')
        # 这里需要添加验证邀请码的逻辑
        # 例如：检查数据库中是否存在该邀请码，以及是否已被使用
        if not self.is_valid_invitation_code(code):
            raise forms.ValidationError("无效的邀请码")
        return code

    def is_valid_invitation_code(self, code):
        # 这里实现邀请码验证逻辑
        # 例如：检查数据库中是否存在该邀请码，以及是否已被使用
        # 返回 True 如果邀请码有效，否则返回 False
        pass


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    invitation_code = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "invitation_code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置中文标签
        self.fields['username'].label = '用户名'
        self.fields['email'].label = '电子邮箱'
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '确认密码'
        self.fields['invitation_code'].label = '邀请码'
        
        # 添加 Bootstrap 类和占位符文本
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入用户名'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入邮箱'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请再次输入密码'
        })
        self.fields['invitation_code'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入邀请码'
        })

    def clean_invitation_code(self):
        code = self.cleaned_data.get('invitation_code')
        try:
            invitation = InvitationCode.objects.get(code=code, is_used=False)
        except InvitationCode.DoesNotExist:
            raise forms.ValidationError("无效的邀请码")
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # 标记邀请码为已使用
            invitation = InvitationCode.objects.get(code=self.cleaned_data['invitation_code'])
            invitation.is_used = True
            invitation.used_at = timezone.now()
            invitation.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['real_name', 'email', 'phone_number', 'birth_date', 'bio']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'real_name': '真实姓名',
            'email': '电子邮箱',
            'phone_number': '手机号码',
            'birth_date': '出生日期',
            'bio': '个人简介',
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['real_name', 'gender', 'email', 'phone_number', 
                 'birth_date', 'calendar_type', 'bio']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'calendar_type': forms.Select(attrs={'class': 'form-control'}),
            'real_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'real_name': '真实姓名',
            'gender': '性别',
            'email': '电子邮箱',
            'phone_number': '手机号码',
            'birth_date': '出生日期',
            'calendar_type': '生日历法',
            'bio': '个人简介',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].required = False
        self.fields['gender'].choices = [('', '请选择')] + list(User.GENDER_CHOICES)
        self.fields['calendar_type'].required = False
        self.fields['calendar_type'].choices = [('', '请选择')] + list(User.CALENDAR_CHOICES)
