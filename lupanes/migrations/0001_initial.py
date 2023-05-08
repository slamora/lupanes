# Generated by Django 4.2.1 on 2023-05-08 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Producer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "producer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="lupanes.producer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductPrice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.DecimalField(decimal_places=2, max_digits=5)),
                ("start_date", models.DateField()),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="lupanes.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DeliveryNote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateTimeField(auto_now_add=True)),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=3, max_digits=6, verbose_name="Cantidad"
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="lupanes.customer",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="lupanes.product",
                    ),
                ),
            ],
        ),
    ]
