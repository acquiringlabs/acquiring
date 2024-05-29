# Generated by Django 4.2 on 2024-05-29 17:32

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


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
                ('amount', models.BigIntegerField(help_text='Amount intended to be collected. A positive integer representing how much to charge in the currency unit (e.g., 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency).')),
                ('currency', models.CharField(max_length=3, validators=[django.core.validators.MinLengthValidator(3)])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('confirmable', models.BooleanField(editable=False, help_text='Whether this PaymentMethod can at some point run inside PaymentFlow.confirm')),
                ('payment_attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to='acquiring.paymentattempt')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.TextField()),
                ('timestamp', models.DateTimeField()),
                ('raw_data', models.JSONField()),
                ('provider_name', models.TextField()),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='acquiring.paymentmethod')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('token', models.TextField()),
                ('fingerprint', models.TextField(blank=True, help_text='Fingerprinting provides a way to correlate multiple tokens together that contain the same data without needing access to the underlying data.', null=True)),
                ('metadata', models.JSONField(blank=True, help_text='tag your tokens with custom key-value attributes (i.e., to reference a record in your own database, tag records that fall into certain compliance requirements like GDPR, etc)', null=True)),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='acquiring.paymentmethod')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentOperation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('initialize', 'Initialize'), ('process_action', 'Process Action'), ('pay', 'Pay'), ('confirm', 'Confirm'), ('void', 'Void'), ('refund', 'Refund'), ('after_pay', 'After Pay'), ('after_confirm', 'After Confirm'), ('after_void', 'After Void'), ('after_refund', 'After Refund')], max_length=16)),
                ('status', models.CharField(choices=[('started', 'Started'), ('failed', 'Failed'), ('completed', 'Completed'), ('requires_action', 'Requires Action'), ('pending', 'Pending'), ('not_performed', 'Not Performed')], db_index=True, max_length=15)),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_operations', to='acquiring.paymentmethod')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('quantity', models.PositiveSmallIntegerField(help_text='Quantity of the order line item. Must be a non-negative number.')),
                ('quantity_unit', models.TextField(blank=True, help_text='Unit used to describe the quantity, e.g. kg, pcs, etc.', null=True)),
                ('reference', models.TextField(help_text="Used for storing merchant's internal reference number")),
                ('unit_price', models.BigIntegerField(help_text='Price for a single unit of the order line. A positive integer representing how much to charge in the currency unit (e.g., 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency). Currency is assumed to be the one provided in PaymentAttempt.')),
                ('payment_attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='acquiring.paymentattempt')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BlockEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('started', 'Started'), ('failed', 'Failed'), ('completed', 'Completed'), ('requires_action', 'Requires Action'), ('pending', 'Pending'), ('not_performed', 'Not Performed')], max_length=15)),
                ('block_name', models.CharField(max_length=20)),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acquiring.paymentmethod')),
            ],
            options={
                'unique_together': {('status', 'payment_method', 'block_name')},
            },
        ),
    ]
