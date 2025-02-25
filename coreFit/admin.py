from django.contrib import admin
from .models import CustomUser
from django.contrib.admin import AdminSite
from .forms import CustomAdminAuthenticationForm
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token


class CustomAdminSite(AdminSite):
    login_form = CustomAdminAuthenticationForm

admin_site = CustomAdminSite()
admin_site.register(Group)
admin_site.register(Token)

admin_site.register(CustomUser)

# Register your models here.
