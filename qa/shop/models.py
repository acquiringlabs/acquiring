"""
Structure of the models is taken from Pizza Place Payments

See https://news.alvaroduran.com/p/pizza-place-payments
"""

import decimal

import django
import simple_history

import acquiring.storage


class Customer(django.db.models.Model):
    """User places Orders in the system on behalf of the Customer"""

    name = django.db.models.CharField(max_length=100)
    phone_number = django.db.models.CharField(max_length=15)
    email = django.db.models.CharField(max_length=30)

    def __str__(self) -> str:
        return f"Customer {self.name}"


class Product(django.db.models.Model):
    """
    Products end up being associated with Orders as denormalized copies called Items.
    History of Products is preserved.
    """

    name = django.db.models.CharField(max_length=100)
    history = simple_history.models.HistoricalRecords()
    available = django.db.models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Product: {self.name}"


class Variant(django.db.models.Model):
    """A Product can have multiple Variants (size, gluten-free, extra cheese)"""

    product = django.db.models.ForeignKey(Product, on_delete=django.db.models.PROTECT)
    name = django.db.models.CharField(max_length=100)
    price = django.db.models.DecimalField(decimal_places=2, max_digits=9)
    currency = django.db.models.CharField(max_length=3)
    history = simple_history.models.HistoricalRecords()
    available = django.db.models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.product}, Variant: {self.name} | {self.currency}{self.price}"


class Order(django.db.models.Model):
    """An Order is associated with multiple Items and a PaymentAttempt"""

    customers = django.db.models.ManyToManyField(Customer)
    payment_attempt = django.db.models.OneToOneField(
        acquiring.storage.django.models.PaymentAttempt,
        on_delete=django.db.models.PROTECT,
        null=True,
        blank=True,
    )
    currency = django.db.models.CharField(max_length=3)

    def __str__(self) -> str:
        return f"Order id={self.id} | {self.currency}{self.total}"

    @property
    def total(self) -> decimal.Decimal:
        return sum([item.total for item in self.items])

    @property
    def invoice(self) -> dict:
        """
        Invoice data is a mutable copy of all information related to an order.
        It may be used later to generate the data on the Receipt.
        """
        return {}


class Item(django.db.models.Model):
    """
    An Order consists of multiple Items, which are *denormalized* copies of Product
    and can be checked against Product and Variant history.
    """

    variant = django.db.models.ForeignKey(Variant, on_delete=django.db.models.PROTECT)
    order = django.db.models.ForeignKey(Order, on_delete=django.db.models.PROTECT, related_name="items")
    quantity = django.db.models.IntegerField()
    note = django.db.models.TextField()
    price = django.db.models.DecimalField(decimal_places=2, max_digits=9)
    currency = django.db.models.CharField(max_length=3)

    @property
    def total(self) -> decimal.Decimal:
        return self.quantity * self.price


class Receipt(django.db.models.Model):
    """An immutable copy of the Order, its contents and how it got paid."""

    identifier = django.db.models.TextField(unique=True)
    order = django.db.models.OneToOneField(Order, on_delete=django.db.models.PROTECT)
    data = django.db.models.JSONField()
