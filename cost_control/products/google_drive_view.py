import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
import gspread
from django.http import JsonResponse
from oauth2client.service_account import ServiceAccountCredentials
from .models import Category, Subcategory, Product

# Установите путь к вашему файлу учетных данных
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'goofle-drive-test-381714-1b93f2e6b85e.json')


def import_data_from_google_sheets(request):
    if not os.path.exists(CREDENTIALS_FILE):
        return JsonResponse({'error': 'Credentials file not found'}, status=500)

    data = read_google_file()
    return save_data(data)


def read_google_file():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)
    client = gspread.authorize(credentials)

    spreadsheet = client.open('Expenses')
    sheet = spreadsheet.worksheet('Expenses')

    expected_headers = [
        'Category', 'Subcategory', 'Дата', 'Штрихкод', 'Название',
        'Кг в 1 шт', 'Кол-во', 'Цена', 'Сумма'
    ]

    # data = sheet.get_all_records(head=2, expected_headers=expected_headers)
    all_data = sheet.get_all_values()
    data = all_data[2:]

    return data


def save_data(data):
    saved, not_saved = 0, 0
    for row in data:
        if isinstance(row, dict):
            category_name, subcategory_name, barcode, name, quantity_kg_str, quantity_pcs_str, price_per_unit_str, total_price_str, purchase_date_str = compose_data_from_dict(row)
        else:
            category_name, subcategory_name, barcode, name, quantity_kg_str, quantity_pcs_str, price_per_unit_str, total_price_str, purchase_date_str = compose_data_from_list(row)

        if not name:
            break
        # Создаем или находим категорию
        category, _ = Category.objects.get_or_create(name=category_name)

        # Проверяем существование подкатегории с учетом категории
        subcategory = Subcategory.objects.filter(name=subcategory_name).first()
        if subcategory:
            # Обновляем категорию подкатегории, если она отличается
            if subcategory.category != category:
                subcategory.category = category
                subcategory.save()
        else:
            # Создаем новую подкатегорию, если её нет
            try:
                subcategory = Subcategory.objects.create(name=subcategory_name, category=category)
            except Exception as ex:
                print(f'CREATE SUBCATEGORY: '
                      f'category {category}; '
                      f'subcategory {subcategory}; '
                      f'subcategory_name {subcategory_name}; '
                      f'product {name}')
                return JsonResponse({'error': f'Create subcategory error: {ex}, '
                                              f'category {category}, '
                                              f'subcategory {subcategory}, '
                                              f'subcategory_name {subcategory_name}, '
                                              f'product {name}, '
                                              f'quantity_kg {quantity_kg_str}, '
                                              f'quantity_pcs {quantity_pcs_str}, '
                                              f'price_per_unit {price_per_unit_str}, '
                                              f'total_price {total_price_str}'},
                                    status=400)

        # Преобразование строки даты в объект datetime.date
        try:
            purchase_date = datetime.strptime(purchase_date_str, '%d.%m.%y').date()
        except ValueError:
            return JsonResponse({'error': f'Invalid date format: {purchase_date_str}'}, status=400)

        # Преобразование строк в десятичные числа
        try:
            quantity_kg = get_decimal_value(quantity_kg_str) if quantity_kg_str else None
            quantity_pcs = get_decimal_value(quantity_pcs_str)
            price_per_unit = get_decimal_value(price_per_unit_str)
            total_price = get_decimal_value(total_price_str)
        except InvalidOperation as e:
            return JsonResponse({'error': f'Invalid decimal value: {e}, '
                                          f'category {category}, '
                                          f'subcategory {subcategory}, '
                                          f'product {name}, '
                                          f'quantity_kg {quantity_kg_str}, '
                                          f'quantity_pcs {quantity_pcs_str}, '
                                          f'price_per_unit {price_per_unit_str}, '
                                          f'total_price {total_price_str}'},
                                status=400)

        # Сохраняем данные в базу как новую запись
        try:
            Product.objects.create(
                barcode=barcode,
                category=category,
                subcategory=subcategory,
                name=name,
                quantity_kg=quantity_kg,
                quantity_pcs=quantity_pcs,
                price_per_unit=price_per_unit,
                total_price=total_price,
                purchase_date=purchase_date
            )
            saved += 1
        except Exception as ex:
            not_saved += 1
            print(f"Error saving product: {ex}")

    print(f"Saved: {saved}, Not Saved: {not_saved}")
    return JsonResponse({'message': 'Done', 'saved': saved, 'not_saved': not_saved}, status=200)


def get_decimal_value(number):
    if isinstance(number, str):
        number = number.replace(',', '.')
        number = number.replace(' ', '')
        number = number.replace('\u00A0', '')
    if not number:
        number = 0
    return Decimal(number)

def compose_data_from_dict(row):
    category_name = row['Category']
    subcategory_name = row['Subcategory']
    barcode = row['Штрихкод']
    name = row['Название']
    quantity_kg_str = row['Кг в 1 шт']
    quantity_pcs_str = row['Кол-во']
    price_per_unit_str = row['Цена']
    total_price_str = row['Сумма']
    purchase_date_str = row['Дата']

    print(category_name, subcategory_name, name, purchase_date_str, price_per_unit_str)
    return category_name, subcategory_name, barcode, name, quantity_kg_str, quantity_pcs_str, price_per_unit_str, total_price_str, purchase_date_str

def compose_data_from_list(row):
    category_name = row[0]
    subcategory_name = row[1]
    barcode = row[3]
    name = row[4]
    quantity_kg_str = row[5]
    quantity_pcs_str = row[6]
    price_per_unit_str = row[7]
    total_price_str = row[8]
    purchase_date_str = row[2]

    print(category_name, subcategory_name, name, purchase_date_str, price_per_unit_str)
    return category_name, subcategory_name, barcode, name, quantity_kg_str, quantity_pcs_str, price_per_unit_str, total_price_str, purchase_date_str

def append_to_google_sheet(product):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)
    client = gspread.authorize(credentials)

    spreadsheet = client.open('Expenses')
    sheet = spreadsheet.worksheet('Expenses')

    # Подготовка данных для записи в Google Таблицу
    data = [
        product.category.name,
        product.subcategory.name,
        product.purchase_date.strftime('%d.%m.%y'),
        product.barcode,
        product.name,
        str(product.quantity_kg).replace('.', ',') if product.quantity_kg is not None else '',
        str(product.quantity_pcs).replace('.', ',') if product.quantity_pcs is not None else '',
        str(product.price_per_unit).replace('.', ',') if product.price_per_unit is not None else '',
        # str(product.total_price) if product.total_price is not None else ''
    ]

    # Получаем все значения из столбца "Название" (предполагается, что это 5-й столбец)
    name_column_values = sheet.col_values(5)

    # Подсчитываем количество непустых строк в столбце "Название"
    next_row = len([value for value in name_column_values if value]) + 1

    # Вставляем данные в соответствующие ячейки
    try:
        # for i, value in enumerate(data, start=1):
        #     sheet.update_cell(next_row, i, value)
        sheet.append_row(data)
        return True
    except Exception as e:
        print(f"Error appending to Google Sheet: {e}")
        return False
