import factory


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "django_acquiring.Order"


class PaymentAttemptFactory(factory.django.DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)

    class Meta:
        model = "django_acquiring.PaymentAttempt"


class PaymentMethodFactory(factory.django.DjangoModelFactory):

    confirmable = False

    class Meta:
        model = "django_acquiring.PaymentMethod"


class PaymentOperationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "django_acquiring.PaymentOperation"
