# Generated by Django 5.0.3 on 2024-03-29 03:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0007_alter_shipment_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='delivery_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='driver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tracker.driver'),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='order_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='shipment_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='total_cost',
            field=models.FloatField(default=0),
        ),
    ]
