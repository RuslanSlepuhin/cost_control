from django.shortcuts import render, redirect
from .forms import ProductForm, CategoryForm, SubcategoryForm
from .models import Product, Category, Subcategory
from django.db.models import Sum, Count
from django.utils import timezone
from django.http import JsonResponse

def input_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'products/input.html', {'form': ProductForm(), 'success': True})
    else:
        form = ProductForm()
    return render(request, 'products/input.html', {'form': form})

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('input_product')
    else:
        form = CategoryForm()
    return render(request, 'products/add_category.html', {'form': form})

def add_subcategory(request):
    if request.method == 'POST':
        form = SubcategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('input_product')
    else:
        form = SubcategoryForm()
    return render(request, 'products/add_subcategory.html', {'form': form})

def autocomplete_barcode(request):
    query = request.GET.get('term', '')
    products = Product.objects.filter(barcode__startswith=query).values('barcode').annotate(count=Count('barcode')).order_by('-count')[:10]
    results = []
    for product in products:
        latest_product = Product.objects.filter(barcode=product['barcode']).order_by('-created_at').first()
        if latest_product:
            results.append({
                'id': latest_product.id,
                'label': f"{latest_product.barcode} - {latest_product.name}",
                'value': latest_product.barcode,
                'category_id': latest_product.category.id,  # Добавляем ID категории
                'subcategory_id': latest_product.subcategory.id,  # Добавляем ID подкатегории
                'name': latest_product.name,
                'price_per_unit': str(latest_product.price_per_unit),
                'quantity_kg': str(latest_product.quantity_kg),
                'quantity_pcs': str(latest_product.quantity_pcs),
            })
    return JsonResponse(results, safe=False)

def autocomplete_name(request):
    query = request.GET.get('term', '')
    products = Product.objects.filter(name__icontains=query).values('name').annotate(count=Count('name')).order_by('-count')[:10]
    results = []
    for product in products:
        latest_product = Product.objects.filter(name=product['name']).order_by('-created_at').first()
        if latest_product:
            results.append({
                'id': latest_product.id,
                'label': latest_product.name,
                'value': latest_product.name,
                'category_id': latest_product.category.id,  # Добавляем ID категории
                'subcategory_id': latest_product.subcategory.id,  # Добавляем ID подкатегории
                'barcode': latest_product.barcode,
                'price_per_unit': str(latest_product.price_per_unit),
                'quantity_kg': str(latest_product.quantity_kg),
                'quantity_pcs': str(latest_product.quantity_pcs),
            })
    return JsonResponse(results, safe=False)

def report(request):
    current_month = timezone.now().month
    current_year = timezone.now().year
    start_date = timezone.make_aware(timezone.datetime(current_year, current_month, 1))
    end_date = timezone.make_aware(timezone.datetime(current_year, current_month + 1, 1)) if current_month != 12 else timezone.make_aware(timezone.datetime(current_year + 1, 1, 1))

    food_report = Product.objects.filter(
        category__name='Food',
        created_at__gte=start_date,
        created_at__lt=end_date
    ).values('subcategory__name').annotate(total_price_sum=Sum('total_price')).order_by('subcategory__name')

    return render(request, 'products/report.html', {'food_report': food_report})

