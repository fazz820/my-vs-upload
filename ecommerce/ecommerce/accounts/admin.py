from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Wishlist


class WishlistInline(admin.TabularInline):
    model = Wishlist
    extra = 0
    fields = ['product', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['product']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'product__name']
    autocomplete_fields = ['user', 'product']
    list_select_related = ['user', 'product']


admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'order_count', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login', 'order_count']
    inlines = [WishlistInline]

    fieldsets = (
        ('Login', {
            'fields': ('username', 'password'),
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Activity', {
            'fields': ('last_login', 'date_joined', 'order_count'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request)

    def order_count(self, obj):
        return obj.orders.count()
    order_count.short_description = 'Orders'
