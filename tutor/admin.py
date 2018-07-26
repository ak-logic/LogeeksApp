from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User
from tutor.models import Tutor
from image_cropping import ImageCroppingMixin


class TutorAdmin(ImageCroppingMixin, admin.ModelAdmin):
    pass

admin.site.register(Tutor, TutorAdmin)


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton


# class TutorInline(admin.StackedInline):
#     model = Tutor
#     can_delete = False
#     verbose_name_plural = 'tutors'
# # Define a new User admin
#
#
# class UserAdmin(BaseUserAdmin):
#     inlines = (TutorInline, )
# # Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
# admin.site.register(Tutor)
# admin.site.register(User)