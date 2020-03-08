from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profiles'
    fk_name = 'user'
    pass

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_image', 'get_sms', 'get_phone', 'get_address')
    list_select_related = ('userprofile', )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

    def get_image(self, instance):
        return instance.userprofile.image

    def get_sms(self, instance):
        return instance.userprofile.sms

    def get_phone(self, instance):
        return instance.userprofile.phone

    def get_address(self, instance):
        return instance.userprofile.address
    pass

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
