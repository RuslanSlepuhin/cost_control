from datetime import datetime

from .google_drive_view import append_to_google_sheet
from .models import Product, Category, Subcategory
from django.db.models import Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm, CategoryForm, SubcategoryForm
from django.utils import timezone
from django.http import JsonResponse
from .models import Subcategory

def input_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            print("saved!!!!!!!!!!!!!!!!!", product)
            append = append_to_google_sheet(product)
            if append:
                return render(request, 'products/input.html', {'form': ProductForm(initial={'purchase_date': timezone.now().date()}), 'success': True})
            else:
                return JsonResponse({"error": "Have not been saved to google sheet"})
    else:
        form = ProductForm(initial={'purchase_date': timezone.now().date()})
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
    print('query', query)
    products = Product.objects.filter(name__icontains=query).values('name').annotate(count=Count('name')).order_by('-count')[:10]
    print(products)
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
    categories = Category.objects.all()
    selected_category = request.GET.get('category', '')
    if selected_category == '':
        selected_category = None

    # Обработка дат
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str and end_date_str:
        start_date = timezone.make_aware(timezone.datetime.strptime(start_date_str, '%Y-%m-%d'))
        end_date = timezone.make_aware(timezone.datetime.strptime(end_date_str, '%Y-%m-%d') + timezone.timedelta(days=1))
    else:
        # Если даты не переданы, используем текущий месяц по умолчанию
        current_month = timezone.now().month
        current_year = timezone.now().year
        start_date = timezone.make_aware(timezone.datetime(current_year, current_month, 1))
        end_date = timezone.make_aware(timezone.datetime(current_year, current_month + 1, 1)) if current_month != 12 else timezone.make_aware(timezone.datetime(current_year + 1, 1, 1))

    if selected_category is None:
        report_data = Product.objects.filter(
            purchase_date__gte=start_date,
            purchase_date__lt=end_date
        ).values('subcategory__name').annotate(total_price_sum=Sum('total_price')).order_by('-total_price_sum', 'subcategory__name')

        total_sum = Product.objects.filter(
            purchase_date__gte=start_date,
            purchase_date__lt=end_date
        ).aggregate(total_price_sum=Sum('total_price'))['total_price_sum'] or 0
    else:
        report_data = Product.objects.filter(
            category__name=selected_category,
            purchase_date__gte=start_date,
            purchase_date__lt=end_date
        ).values('subcategory__name').annotate(total_price_sum=Sum('total_price')).order_by('-total_price_sum', 'subcategory__name')
        total_sum = Product.objects.filter(
            category__name=selected_category,
            purchase_date__gte=start_date,
            purchase_date__lt=end_date
        ).aggregate(total_price_sum=Sum('total_price'))['total_price_sum'] or 0

    return render(request, 'products/report.html', {
        'food_report': report_data,
        'categories': categories,
        'selected_category': selected_category if selected_category else "All Categories",
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': (end_date - timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
        'total_sum': total_sum
    })

def load_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category_id=category_id).all()
    return JsonResponse(list(subcategories.values('id', 'name')), safe=False)

def product_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    products = Product.objects.all()

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        products = products.filter(purchase_date__gte=start_date)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        products = products.filter(purchase_date__lte=end_date)

    return render(request, 'products/product_list.html', {'products': products})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'products/delete_product.html', {'product': product})

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)


