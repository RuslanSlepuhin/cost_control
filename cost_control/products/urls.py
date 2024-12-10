from django.urls import path
from . import views

urlpatterns = [
    path('input/', views.input_product, name='input_product'),
    path('autocomplete/barcode/', views.autocomplete_barcode, name='autocomplete_barcode'),
    path('autocomplete/name/', views.autocomplete_name, name='autocomplete_name'),
    path('report/', views.report, name='report'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_subcategory/', views.add_subcategory, name='add_subcategory'),
]
