from django import forms

from ecommerce.products.models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'slug', 'description', 'price',
            'discount_price', 'stock', 'image', 'is_featured', 'is_active',
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError('Price must be greater than zero.')
        return price

    def clean_stock(self):
        stock = self.cleaned_data['stock']
        if stock < 0:
            raise forms.ValidationError('Stock cannot be negative.')
        return stock

    def clean_discount_price(self):
        price = self.cleaned_data.get('price')
        discount_price = self.cleaned_data.get('discount_price')
        if discount_price and price and discount_price >= price:
            raise forms.ValidationError('Discount price must be less than the regular price.')
        return discount_price

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = 'Select a category'

        for field_name in ['discount_price', 'description', 'image']:
            self.fields[field_name].required = False


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Category description (optional)'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not name:
            raise forms.ValidationError('Category name is required.')
        instance = getattr(self, 'instance', None)
        qs = Category.objects.filter(name__iexact=name)
        if instance and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError('A category with this name already exists.')
        return name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['image'].required = False
