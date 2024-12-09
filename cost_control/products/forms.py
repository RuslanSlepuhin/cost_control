from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'subcategory', 'barcode', 'name', 'quantity_kg', 'quantity_pcs', 'price_per_unit', 'total_price']
