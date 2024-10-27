from django.contrib import admin
from .models import InvitationCode, User
import random
import string


@admin.register(InvitationCode)
class InvitationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'is_used', 'created_at', 'used_at')
    actions = ['generate_invitation_codes']

    def generate_invitation_codes(self, request, queryset):
        num_codes = 1  # 每次生成的邀请码数量，可以根据需求调整
        for _ in range(num_codes):
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=8))
            InvitationCode.objects.create(code=code)
        self.message_user(request, f"成功生成 {num_codes} 个新的邀请码。")
    generate_invitation_codes.short_description = "生成新的邀请码"

    def save_model(self, request, obj, form, change):
        if not obj.code:
            obj.code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=8))
        super().save_model(request, obj, form, change)


admin.site.register(User)
