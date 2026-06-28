from django.db.models import Q, Min, Max, Count
from django.views.generic import ListView, DetailView, TemplateView
from .models import Product, Category


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

        min_price = self.request.GET.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self.request.GET.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset.select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.kwargs.get('category_slug', '')

        price_range = Product.objects.filter(is_active=True).aggregate(
            min_price=Min('price'), max_price=Max('price')
        )
        context['min_price_limit'] = price_range['min_price'] or 0
        context['max_price_limit'] = price_range['max_price'] or 0
        context['current_min_price'] = self.request.GET.get('min_price', '')
        context['current_max_price'] = self.request.GET.get('max_price', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            is_active=True, is_featured=True
        ).select_related('category')[:8]
        context['categories'] = Category.objects.annotate(
            product_count=Count('products')
        ).order_by('-created_at')[:6]
        context['new_arrivals'] = Product.objects.filter(
            is_active=True
        ).select_related('category').order_by('-created_at')[:8]
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        return Product.objects.filter(
            slug=self.kwargs['slug'],
            category__slug=self.kwargs['category_slug'],
        ).select_related('category').first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        if product:
            context['related_products'] = Product.objects.filter(
                category=product.category,
                is_active=True,
            ).exclude(id=product.id)[:4]
        return context
