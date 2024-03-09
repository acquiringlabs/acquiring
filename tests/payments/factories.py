import factory


class PaymentAttemptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "payments.PaymentAttempt"


class PaymentMethodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "payments.PaymentMethod"


class PaymentOperationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "payments.PaymentOperation"
