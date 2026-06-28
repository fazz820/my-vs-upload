from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('products/', views.product_list_view, name='product_list'),
    path('products/create/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit_view, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/<int:pk>/', views.order_detail_view, name='order_detail'),
    path('orders/<int:pk>/status/', views.order_status_update_view, name='order_status_update'),
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit_view, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
]
