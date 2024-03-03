from django.db import models
from uuid import uuid4


class Payment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # https://docs.djangoproject.com/en/5.0/ref/models/fields/#uuidfield
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    def __str__(self):
        return f"Payment[id={self.id}]"
