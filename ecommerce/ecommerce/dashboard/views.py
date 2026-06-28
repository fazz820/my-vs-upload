from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from ecommerce.orders.models import Order, OrderItem
from ecommerce.products.models import Product, Category
from django.contrib.auth import get_user_model
from ecommerce.dashboard.forms import ProductForm, CategoryForm

User = get_user_model()


@staff_member_required
def dashboard_view(request):
    now = timezone.now()
    current_year = now.year

    total_products = Product.objects.count()
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    revenue = OrderItem.objects.filter(
        order__status__in=['delivered', 'shipped']
    ).aggregate(total=Sum('price'))['total'] or 0

    orders_by_month = (
        Order.objects
        .filter(created_at__year=current_year)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    revenue_by_month = (
        OrderItem.objects
        .filter(order__created_at__year=current_year, order__status__in=['delivered', 'shipped'])
        .annotate(month=TruncMonth('order__created_at'))
        .values('month')
        .annotate(total=Sum('price'))
        .order_by('month')
    )

    status_counts = (
        Order.objects
        .values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )

    status_labels = dict(Order.STATUS_CHOICES)
    recent_orders = Order.objects.select_related('user').prefetch_related('items__product')[:5]

    months = []
    orders_data = []
    for entry in orders_by_month:
        months.append(entry['month'].strftime('%b %Y') if entry['month'] else '')
        orders_data.append(entry['count'])

    rev_months = []
    rev_data = []
    for entry in revenue_by_month:
        rev_months.append(entry['month'].strftime('%b %Y') if entry['month'] else '')
        rev_data.append(float(entry['total']))

    status_labels_list = []
    status_data = []
    status_colors = {
        'pending': '#ffc107',
        'processing': '#0dcaf0',
        'shipped': '#0d6efd',
        'delivered': '#198754',
        'cancelled': '#dc3545',
    }
    for entry in status_counts:
        status_labels_list.append(status_labels.get(entry['status'], entry['status']))
        status_data.append(entry['count'])

    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_orders': total_orders,
        'revenue': revenue,
        'months': months,
        'orders_data': orders_data,
        'rev_months': rev_months,
        'rev_data': rev_data,
        'status_labels': status_labels_list,
        'status_data': status_data,
        'status_colors': status_colors,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/index.html', context)


@staff_member_required
def product_list_view(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.select_related('category').all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    total = products.count()
    context = {
        'products': products,
        'query': query,
        'total': total,
    }
    return render(request, 'dashboard/product_list.html', context)


@staff_member_required
def product_create_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {
        'form': form,
        'title': 'Create Product',
        'submit_text': 'Create Product',
    })


@staff_member_required
def product_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {
        'form': form,
        'title': 'Edit Product',
        'submit_text': 'Update Product',
        'product': product,
    })


@staff_member_required
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/product_confirm_delete.html', {
        'product': product,
    })


@staff_member_required
def order_list_view(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    orders = Order.objects.select_related('user').prefetch_related('items').all()

    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(shipping_address__icontains=query)
        )

    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)

    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'dashboard/order_list.html', context)


@staff_member_required
def order_detail_view(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'),
        pk=pk,
    )
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'dashboard/order_detail.html', context)


@staff_member_required
def order_status_update_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status', '').strip()
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.get_status_display()
            order.status = new_status
            order.save(update_fields=['status'])
            messages.success(
                request,
                f'Order {order.order_number} status changed from "{old_status}" to "{order.get_status_display()}".',
            )
        else:
            messages.error(request, 'Invalid status selected.')
    return redirect('dashboard:order_detail', pk=order.pk)


@staff_member_required
def category_list_view(request):
    categories = Category.objects.annotate(product_count=Count('products')).all()
    return render(request, 'dashboard/category_list.html', {'categories': categories})


@staff_member_required
def category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/category_form.html', {
        'form': form,
        'title': 'Create Category',
        'submit_text': 'Create Category',
    })


@staff_member_required
def category_edit_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/category_form.html', {
        'form': form,
        'title': 'Edit Category',
        'submit_text': 'Update Category',
        'category': category,
    })


@staff_member_required
def category_delete_view(request, pk):
    category = get_object_or_404(Category.objects.annotate(product_count=Count('products')), pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully.')
        return redirect('dashboard:category_list')
    return render(request, 'dashboard/category_confirm_delete.html', {
        'category': category,
    })
