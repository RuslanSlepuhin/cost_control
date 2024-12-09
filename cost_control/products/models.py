from django.db import models

from django.db import models

class Product(models.Model):
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)
    barcode = models.CharField(max_length=13, unique=True)
    name = models.CharField(max_length=200)
    quantity_kg = models.FloatField()
    quantity_pcs = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

