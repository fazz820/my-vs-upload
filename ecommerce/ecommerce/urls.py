from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from ecommerce.products.views import HomeView
from ecommerce.products.sitemaps import StaticViewSitemap, CategorySitemap, ProductSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'products': ProductSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('ecommerce.dashboard.urls')),
    path('accounts/', include('ecommerce.accounts.urls')),
    path('cart/', include('ecommerce.orders.urls')),
    path('products/', include('ecommerce.products.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('', HomeView.as_view(), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'ecommerce.views.page_not_found'
handler500 = 'ecommerce.views.server_error'
