from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .forms import ProductForm
from .models import Product

def input_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'products/input.html', {'form': ProductForm(), 'success': True})
    else:
        form = ProductForm()
    return render(request, 'products/input.html', {'form': form})

def autocomplete_barcode(request):
    query = request.GET.get('term', '')
    products = Product.objects.filter(barcode__startswith=query)[:10]
    results = [{'id': product.id, 'label': product.barcode, 'value': product.barcode} for product in products]
    return JsonResponse(results, safe=False)
