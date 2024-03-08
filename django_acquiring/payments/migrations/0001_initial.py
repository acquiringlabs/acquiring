# Generated by Django 5.0.2 on 2024-03-08 22:04

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentAttempt',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('payment_attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.paymentattempt')),
            ],
        ),
        migrations.CreateModel(
            name='StageEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(choices=[('authenticate', 'Authenticate'), ('authorize', 'Authorize'), ('charge', 'Charge'), ('void', 'Void'), ('refund', 'Refund'), ('synchronize', 'Synchronize'), ('mark_as_canceled', 'Mark As Canceled')], max_length=16)),
                ('status', models.CharField(choices=[('started', 'Started'), ('failed', 'Failed'), ('completed', 'Completed'), ('requires_action', 'Requires Action')], max_length=15)),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.paymentmethod')),
            ],
        ),
    ]
