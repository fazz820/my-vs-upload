from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter
def currency(value):
    try:
        return f'${float(value):.2f}'
    except (ValueError, TypeError):
        return '$0.00'


@register.filter
def discount_percentage(price, discount_price):
    try:
        if discount_price and price and discount_price < price:
            return int((1 - float(discount_price) / float(price)) * 100)
        return 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.simple_tag
def product_image(product, size='sm'):
    if product and product.image:
        return product.image.url
    return 'https://via.placeholder.com/400x400?text=No+Image'


@register.filter
def stars(rating):
    try:
        rating = int(rating)
    except (ValueError, TypeError):
        rating = 0
    full = '<i class="bi bi-star-fill text-warning"></i>' * min(rating, 5)
    empty = '<i class="bi bi-star text-warning"></i>' * max(5 - rating, 0)
    return format_html(full + empty)


@register.filter
def in_stock(product):
    return product.stock > 0


@register.simple_tag
def active_if(request, url_name):
    if request.resolver_match and request.resolver_match.url_name == url_name:
        return 'active'
    return ''


@register.filter
def truncate_chars(value, max_length):
    if not value:
        return ''
    if len(value) <= max_length:
        return value
    return value[:max_length].rsplit(' ', 1)[0] + '...'
