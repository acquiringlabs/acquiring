# Generated by Django 5.0.2 on 2024-03-15 11:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('started', 'Started'), ('failed', 'Failed'), ('completed', 'Completed'), ('requires_action', 'Requires Action'), ('pending', 'Pending')], max_length=15)),
                ('block_name', models.CharField(max_length=20)),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.paymentmethod')),
            ],
        ),
    ]
