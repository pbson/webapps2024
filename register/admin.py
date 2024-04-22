from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'currency', 'balance', 'is_staff',]
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('currency', 'balance',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('currency', 'balance',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
