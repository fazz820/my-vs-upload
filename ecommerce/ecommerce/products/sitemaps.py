from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from ecommerce.products.models import Product, Category


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'product_list']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('product_list_by_category', args=[obj.slug])


class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True).select_related('category')

    def location(self, obj):
        return reverse('product_detail', args=[obj.category.slug, obj.slug])

    def lastmod(self, obj):
        return obj.updated_at
