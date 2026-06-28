from datetime import datetime
from ecommerce.products.models import Category
from ecommerce.orders.cart import CartManager


def categories(request):
    return {'categories': Category.objects.all()}


def cart(request):
    cart_manager = CartManager(request)
    return {'cart_count': len(cart_manager)}


def wishlist(request):
    if request.user.is_authenticated:
        ids = list(request.user.wishlist.values_list('product_id', flat=True))
        return {'wishlist_ids': ids, 'wishlist_count': len(ids)}
    return {'wishlist_ids': [], 'wishlist_count': 0}


def site_meta(request):
    return {
        'site_name': 'ShopMart',
        'site_description': 'Your premium e-commerce destination for quality products at unbeatable prices. Fast shipping, easy returns, and exceptional customer service.',
        'current_year': datetime.now().year,
    }
