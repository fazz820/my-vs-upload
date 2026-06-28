from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add_view, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove_view, name='cart_remove'),
    path('update/<int:product_id>/', views.cart_update_view, name='cart_update'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_history_view, name='order_history'),
    path('orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('orders/<str:order_number>/invoice/', views.order_invoice_view, name='order_invoice'),
    path('order/<str:order_number>/', views.order_success_view, name='order_success'),
]
