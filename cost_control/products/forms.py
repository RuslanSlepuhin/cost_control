from django import forms
from .models import Product, Category, Subcategory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['barcode', 'name', 'category', 'subcategory', 'quantity_kg', 'quantity_pcs', 'price_per_unit', 'total_price', 'purchase_date']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            # 'purchase_date': forms.DateInput(attrs={'type': 'date'}, format='%m/%d/%Y'),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['name', 'category']
