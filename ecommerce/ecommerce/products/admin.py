from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['slug', 'created_at']
    list_filter = ['created_at']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    list_editable = ['stock', 'is_featured', 'is_active', 'discount_price']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['slug', 'created_at', 'updated_at', 'image_preview']
    list_select_related = ['category']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'image', 'image_preview'),
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price'),
        }),
        ('Inventory', {
            'fields': ('stock',),
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="max-height: 100px;">', obj.image.url)
        return ''
    image_preview.short_description = 'Image Preview'
