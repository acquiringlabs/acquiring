from django.contrib import admin

from .models import Customer, Item, Order, Product, Variant

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Item)
admin.site.register(Variant)
