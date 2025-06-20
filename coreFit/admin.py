from django.contrib import admin
from .models import CustomUser, Payment, Membership,MembershipPlan, MembershipFeature
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

class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price', 'is_active', 'created_at', 'popular')
    filter_horizontal = ('features',)
    search_fields = ('name',)
    list_filter = ('is_active', 'duration')
    ordering = ('-created_at',)
admin_site.register(MembershipPlan, MembershipPlanAdmin)
admin_site.register(MembershipFeature)


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'plan', 'start_date', 'end_date', 'is_active')
    search_fields = ('user__full_name', 'plan__name')
    list_filter = ('is_active', 'plan')
    ordering = ('-start_date',)

    def get_full_name(self, obj):
        return obj.user.full_name or obj.user.username
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__full_name'

admin_site.register(Membership, MembershipAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership', 'amount', 'status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'transaction_id')
    list_filter = ('status', 'payment_method')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

admin_site.register(Payment, PaymentAdmin)

# Register your models here.
