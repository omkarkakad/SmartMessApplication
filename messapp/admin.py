from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import OrderModel, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'get_phone_number', 'is_staff')

    def get_phone_number(self, obj):
        return obj.profile.phone_number
    get_phone_number.short_description = 'Phone Number'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class OrderModelAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user', 'name', 'surname', 'order_place', 'is_paid', 'order_time')

admin.site.register(OrderModel, OrderModelAdmin)
