from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ecommerce.products.models import Product
from .models import Wishlist
from .forms import (
    UserRegisterForm,
    UserProfileForm,
    UserPasswordChangeForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
)


def signup_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product__category')
    return render(request, 'accounts/wishlist.html', {'wishlist_items': items})


@login_required
@require_POST
def wishlist_add_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    _, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({
        'created': created,
        'wishlist_count': count,
        'message': f'{product.name} added to wishlist' if created else 'Already in wishlist',
    })


@login_required
@require_POST
def wishlist_remove_view(request, product_id):
    deleted, _ = Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({
        'removed': bool(deleted),
        'wishlist_count': count,
        'message': 'Removed from wishlist' if deleted else 'Not in wishlist',
    })
