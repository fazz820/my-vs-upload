from decimal import Decimal
from django.conf import settings
from ecommerce.products.models import Product


CART_SESSION_KEY = 'cart'


class CartManager:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not cart:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def save(self):
        self.session.modified = True

    def add(self, product_id, quantity=1):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {'quantity': quantity}
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                del self.cart[product_id]
            self.save()

    def clear(self):
        self.cart = {}
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        product_map = {str(p.id): p for p in products}
        for prod_id, item in self.cart.items():
            product = product_map.get(prod_id)
            if product:
                item['product'] = product
                item['product_id'] = int(prod_id)
                item['price'] = product.get_discounted_price()
                item['total'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal(self):
        return sum(
            Decimal(item['total'])
            for item in self
        )

    def get_items(self):
        return list(self)
