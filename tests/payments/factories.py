import factory


class PaymentAttemptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "payments.PaymentAttempt"
