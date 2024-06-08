from django.contrib import admin

from acquiring.storage.django.models import PaymentAttempt

from .models import Customer, Item, Order, Product, Variant

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Item)
admin.site.register(PaymentAttempt)
admin.site.register(Variant)
