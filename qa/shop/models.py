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
    """
    A Product can have multiple Variants (size, gluten-free, extra cheese)

    There must be at least one Variant so that a Product gets associated with an Item (and therefore an Order)
    """

    product = django.db.models.ForeignKey(Product, on_delete=django.db.models.PROTECT)
    name = django.db.models.CharField(max_length=100)
    price = django.db.models.DecimalField(decimal_places=2, max_digits=9)
    currency = django.db.models.CharField(max_length=3)
    history = simple_history.models.HistoricalRecords()
    available = django.db.models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.product}, Variant: {self.name} | {self.currency}{self.price}"


class Order(django.db.models.Model):
    """
    An Order is associated with multiple Items and a PaymentAttempt

    It gets created empty, associated to a Customer.
    Then, Items get added to it.
    """

    customers = django.db.models.ManyToManyField(Customer)
    payment_attempt = django.db.models.OneToOneField(
        acquiring.storage.models.PaymentAttempt,
        on_delete=django.db.models.PROTECT,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"Order id={self.id} | Total price {self.currency}{self.total} {'| Payment: ' + str(self.payment_attempt) if self.payment_attempt else ''}"

    @property
    def total(self) -> decimal.Decimal:
        return sum([item.total for item in self.items.all()])

    @property
    def currency(self) -> str:
        return self.items.first().currency if self.items.exists() else ""

    @property
    def invoice(self) -> dict:
        """
        Invoice data is a mutable copy of all information related to an order.
        It may be used later to generate the data on the Receipt.
        """
        return {
            "items": [item.as_dict for item in self.items.all()],
            "total": self.total,
            "currency": self.currency,
        }


class Item(django.db.models.Model):
    """
    An Order consists of multiple Items, which are *denormalized* copies of Product
    and can be checked against Product and Variant history.

    An Item can only be created by associating it with an existing Variant.
    """

    variant = django.db.models.ForeignKey(Variant, on_delete=django.db.models.PROTECT)
    order = django.db.models.ForeignKey(Order, on_delete=django.db.models.PROTECT, related_name="items")
    quantity = django.db.models.IntegerField()
    note = django.db.models.TextField(null=True, blank=True)
    price = django.db.models.DecimalField(decimal_places=2, max_digits=9)
    currency = django.db.models.CharField(max_length=3)

    def __str__(self) -> str:
        return f"Item in Order[{self.order_id}]: {self.variant} | Quantity {self.quantity}, Total price {self.total}"

    @property
    def total(self) -> decimal.Decimal:
        return self.quantity * self.price

    @property
    def as_dict(self) -> dict:
        return {
            "product": str(self.variant),
            "quantity": self.quantity,
            "note": self.note,
            "price": self.price,
            "currency": self.currency,
        }


class Receipt(django.db.models.Model):
    """An immutable copy of the Order, its contents and how it got paid."""

    identifier = django.db.models.TextField(unique=True)
    order = django.db.models.OneToOneField(Order, on_delete=django.db.models.PROTECT)
    data = django.db.models.JSONField()
