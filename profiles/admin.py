from django.contrib import admin
from .models.users import CustomUser

admin.site.register(CustomUser)
