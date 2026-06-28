from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ecommerce.products.models import Product
from .models import Order, OrderItem
from .cart import CartManager
from .forms import CheckoutForm


def cart_detail_view(request):
    cart = CartManager(request)
    return render(request, 'orders/cart.html', {
        'cart_items': cart.get_items(),
        'subtotal': cart.get_subtotal(),
    })


@require_POST
def cart_add_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = CartManager(request)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > product.stock:
        return JsonResponse({'error': 'Not enough stock'}, status=400)

    cart.add(product_id, quantity)
    return JsonResponse({'cart_count': len(cart), 'message': f'{product.name} added to cart'})


@require_POST
def cart_remove_view(request, product_id):
    cart = CartManager(request)
    cart.remove(product_id)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': len(cart), 'subtotal': str(cart.get_subtotal())})
    messages.success(request, 'Item removed from cart.')
    return redirect('cart_detail')


@require_POST
def cart_update_view(request, product_id):
    cart = CartManager(request)
    quantity = int(request.POST.get('quantity', 0))
    cart.update(product_id, quantity)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': len(cart), 'subtotal': str(cart.get_subtotal())})
    messages.success(request, 'Cart updated.')
    return redirect('cart_detail')


@login_required
def checkout_view(request):
    cart = CartManager(request)
    cart_items = cart.get_items()

    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                shipping_address=form.cleaned_data['shipping_address'],
                phone=form.cleaned_data['phone'],
                total_amount=cart.get_subtotal(),
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price'],
                )
                product = item['product']
                if product.stock >= item['quantity']:
                    product.stock -= item['quantity']
                    product.save()

            cart.clear()
            messages.success(request, 'Order placed successfully!')
            return redirect('order_success', order_number=order.order_number)
    else:
        form = CheckoutForm()

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': cart.get_subtotal(),
    })


@login_required
def order_history_view(request):
    orders_list = Order.objects.filter(user=request.user).prefetch_related('items__product')
    paginator = Paginator(orders_list, 10)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        order_number=order_number,
        user=request.user,
    )
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_invoice_view(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        order_number=order_number,
        user=request.user,
    )
    return render(request, 'orders/invoice.html', {'order': order})


@login_required
def order_success_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})
