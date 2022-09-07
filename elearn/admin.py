from django.contrib import admin
from embed_video.admin import AdminVideoMixin

from .models import *


class tutorialAdmin(AdminVideoMixin, admin.ModelAdmin):
    pass


# Register your models here.
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Tutorial)
admin.site.register(User)
admin.site.register(Module)
admin.site.register(Profile)
admin.site.register(Quiz)
admin.site.register(Question)

