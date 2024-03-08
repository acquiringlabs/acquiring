import factory


class PaymentAttemptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "payments.PaymentAttempt"


class PaymentMethodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "payments.PaymentMethod"


class StageEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "payments.StageEvent"
