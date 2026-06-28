from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['product', 'quantity', 'item_total']
    readonly_fields = ['item_total']
    autocomplete_fields = ['product']

    def item_total(self, obj):
        if obj.pk:
            return f'${obj.get_total():.2f}'
        return ''
    item_total.short_description = 'Total'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_count', 'cart_total', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    inlines = [CartItemInline]
    list_select_related = ['user']

    def item_count(self, obj):
        return obj.get_item_count()
    item_count.short_description = 'Items'

    def cart_total(self, obj):
        return f'${obj.get_total():.2f}'
    cart_total.short_description = 'Total'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price', 'item_total']
    readonly_fields = ['price', 'item_total']

    def item_total(self, obj):
        if obj.pk:
            return f'${obj.get_total():.2f}'
        return ''
    item_total.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'item_count', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'shipping_address']
    list_editable = ['status']
    readonly_fields = ['order_number', 'total_amount', 'created_at']
    inlines = [OrderItemInline]
    list_select_related = ['user']

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'total_amount', 'created_at'),
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'phone'),
        }),
    )

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'item_total']
    search_fields = ['order__order_number', 'product__name']
    list_select_related = ['order', 'product']

    def item_total(self, obj):
        return f'${obj.get_total():.2f}'
    item_total.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'item_total']
    search_fields = ['cart__user__username', 'product__name']
    list_select_related = ['cart__user', 'product']

    def item_total(self, obj):
        if obj.pk:
            return f'${obj.get_total():.2f}'
        return ''
    item_total.short_description = 'Total'
