from django.contrib import admin

from .models import User, DonneurProfile, HopitalProfile

admin.site.register(User)
admin.site.register(DonneurProfile)
admin.site.register(HopitalProfile)