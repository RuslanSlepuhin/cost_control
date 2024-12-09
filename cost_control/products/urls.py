from django.urls import path
from . import views

urlpatterns = [
    path('input/', views.input_product, name='input_product'),
    path('autocomplete/', views.autocomplete_barcode, name='autocomplete_barcode'),
]
