from django import forms


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(
        label='Shipping Address',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Street, City, State, Zip Code',
        }),
    )
    phone = forms.CharField(
        label='Phone Number',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567',
        }),
    )
