from django.urls import path
from . import views

urlpatterns = [
    path('input/', views.input_product, name='input_product'),
    path('autocomplete/barcode/', views.autocomplete_barcode, name='autocomplete_barcode'),
    path('autocomplete/name/', views.autocomplete_name, name='autocomplete_name'),
    path('report/', views.report, name='report'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_subcategory/', views.add_subcategory, name='add_subcategory'),
    path('ajax/load-subcategories/', views.load_subcategories, name='ajax_load_subcategories'),
    path('product_list/', views.product_list, name='product_list'),  # Новый URL-паттерн
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
]
