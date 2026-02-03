#!/usr/bin/env python
"""
Seed script to populate the Lupanes database with fake data for debugging.

This script creates:
- User groups (customers and managers)
- Multiple users (customers and managers)
- Producers
- Products with different units
- Product prices (current and historical)
- Delivery notes spanning several months

Usage:
    python seed_fake_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
from random import choice, randint, uniform, sample
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from lupanes.models import Producer, Product, ProductPrice, DeliveryNote

User = get_user_model()


# Fake data definitions
SPANISH_FIRST_NAMES = [
    "María", "Carmen", "Ana", "Isabel", "Dolores", "Pilar", "Teresa", "Rosa",
    "Antonio", "José", "Manuel", "Francisco", "Juan", "David", "Javier", "Daniel",
    "Laura", "Marta", "Paula", "Cristina", "Sara", "Lucía", "Elena", "Beatriz",
    "Carlos", "Miguel", "Pedro", "Ángel", "Luis", "Sergio", "Jorge", "Alberto"
]

SPANISH_LAST_NAMES = [
    "García", "Rodríguez", "González", "Fernández", "López", "Martínez", "Sánchez",
    "Pérez", "Martín", "Gómez", "Ruiz", "Hernández", "Jiménez", "Díaz", "Moreno",
    "Álvarez", "Muñoz", "Romero", "Alonso", "Gutiérrez", "Navarro", "Torres",
    "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez", "Serrano", "Blanco", "Molina"
]

PRODUCERS = [
    "Aceites del Sur",
    "Conservas Artesanas",
    "Huerta Orgánica",
    "Granja La Esperanza",
    "Bodega Los Viñedos",
    "Lácteos Naturales",
    "Pan de Pueblo",
    "Miel de las Sierras",
    "Frutas del Campo",
    "Verduras Frescas S.L.",
]

PRODUCTS = [
    # (name, producer_name, unit, base_price)
    ("Aceite de Oliva Virgen Extra", "Aceites del Sur", "LITRO", "8.50"),
    ("Aceite de Girasol", "Aceites del Sur", "LITRO", "3.20"),
    ("Tomate Frito Casero", "Conservas Artesanas", "BOTE", "2.80"),
    ("Mermelada de Fresa", "Conservas Artesanas", "BOTE", "3.50"),
    ("Lechugas", "Huerta Orgánica", "UNIDAD", "1.20"),
    ("Tomates", "Huerta Orgánica", "KG", "2.50"),
    ("Patatas", "Huerta Orgánica", "KG", "1.80"),
    ("Zanahorias", "Verduras Frescas S.L.", "KG", "1.50"),
    ("Huevos Camperos", "Granja La Esperanza", "DOCENA", "4.20"),
    ("Pollo Ecológico", "Granja La Esperanza", "KG", "8.90"),
    ("Vino Tinto Crianza", "Bodega Los Viñedos", "BOTELLA", "6.50"),
    ("Vino Blanco", "Bodega Los Viñedos", "BOTELLA", "5.20"),
    ("Leche Entera", "Lácteos Naturales", "LITRO", "1.10"),
    ("Yogur Natural", "Lácteos Naturales", "PAQUETE", "2.80"),
    ("Queso Curado", "Lácteos Naturales", "KG", "12.50"),
    ("Pan de Pueblo", "Pan de Pueblo", "UNIDAD", "1.80"),
    ("Barra Integral", "Pan de Pueblo", "UNIDAD", "2.00"),
    ("Miel de Romero", "Miel de las Sierras", "BOTE", "7.50"),
    ("Miel de Azahar", "Miel de las Sierras", "BOTE", "8.20"),
    ("Naranjas", "Frutas del Campo", "KG", "1.90"),
    ("Manzanas", "Frutas del Campo", "KG", "2.20"),
    ("Pimientos", "Verduras Frescas S.L.", "KG", "3.10"),
    ("Calabacines", "Verduras Frescas S.L.", "KG", "2.40"),
    ("Aceitunas Aliñadas", "Conservas Artesanas", "GARRAFA", "15.50"),
]


def create_groups():
    """Create user groups."""
    print("Creating user groups...")
    customers_group, created = Group.objects.get_or_create(name="neveras")
    if created:
        print(f"  ✓ Created group: neveras (customers)")
    else:
        print(f"  - Group 'neveras' already exists")

    managers_group, created = Group.objects.get_or_create(name="tienda")
    if created:
        print(f"  ✓ Created group: tienda (managers)")
    else:
        print(f"  - Group 'tienda' already exists")

    return customers_group, managers_group


def create_users(customers_group, managers_group, num_customers=15, num_managers=3):
    """Create customer and manager users."""
    print(f"\nCreating users ({num_customers} customers, {num_managers} managers)...")

    customers = []
    managers = []
    used_usernames = set(User.objects.values_list('username', flat=True))

    # Create customers
    for i in range(num_customers):
        first_name = choice(SPANISH_FIRST_NAMES)
        last_name = choice(SPANISH_LAST_NAMES)

        # Generate unique username
        base_username = f"{first_name.lower()}.{last_name.lower()}"
        username = base_username
        counter = 1
        while username in used_usernames:
            username = f"{base_username}{counter}"
            counter += 1
        used_usernames.add(username)

        email = f"{username}@example.com"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'is_active': True,
                'is_staff': False,
            }
        )

        if created:
            user.set_password('password123')  # Default password for debugging
            user.save()
            user.groups.add(customers_group)
            customers.append(user)
            print(f"  ✓ Created customer: {username}")
        else:
            if customers_group not in user.groups.all():
                user.groups.add(customers_group)
            customers.append(user)
            print(f"  - Customer '{username}' already exists")

    # Create managers
    for i in range(num_managers):
        first_name = choice(SPANISH_FIRST_NAMES)
        last_name = choice(SPANISH_LAST_NAMES)

        base_username = f"manager.{first_name.lower()}.{last_name.lower()}"
        username = base_username
        counter = 1
        while username in used_usernames:
            username = f"{base_username}{counter}"
            counter += 1
        used_usernames.add(username)

        email = f"{username}@lupierra.com"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'is_active': True,
                'is_staff': True,
            }
        )

        if created:
            user.set_password('manager123')  # Default password for debugging
            user.save()
            user.groups.add(managers_group)
            managers.append(user)
            print(f"  ✓ Created manager: {username}")
        else:
            if managers_group not in user.groups.all():
                user.groups.add(managers_group)
            managers.append(user)
            print(f"  - Manager '{username}' already exists")

    return customers, managers


def create_producers():
    """Create producers."""
    print("\nCreating producers...")
    producers = []

    for producer_name in PRODUCERS:
        producer, created = Producer.objects.get_or_create(name=producer_name)
        producers.append(producer)
        if created:
            print(f"  ✓ Created producer: {producer_name}")
        else:
            print(f"  - Producer '{producer_name}' already exists")

    return producers


def create_products():
    """Create products with their producers."""
    print("\nCreating products...")
    products = []

    for product_name, producer_name, unit, base_price in PRODUCTS:
        producer = Producer.objects.get(name=producer_name)

        product, created = Product.objects.get_or_create(
            name=product_name,
            defaults={
                'producer': producer,
                'unit': unit,
                'is_active': True,
                'description': f"{product_name} producido por {producer_name}"
            }
        )
        products.append((product, Decimal(base_price)))

        if created:
            print(f"  ✓ Created product: {product_name} ({unit})")
        else:
            print(f"  - Product '{product_name}' already exists")

    return products


def create_product_prices(products):
    """Create current and historical prices for products."""
    print("\nCreating product prices...")

    today = timezone.now().date()

    for product, base_price in products:
        # Create historical prices (going back 6 months with price variations)
        for months_ago in [6, 4, 2]:
            historical_date = today - timedelta(days=months_ago * 30)
            # Historical prices are slightly lower/higher
            price_variation = uniform(0.85, 0.95)
            historical_price = (base_price * Decimal(str(price_variation))).quantize(Decimal('0.01'))

            ProductPrice.objects.get_or_create(
                product=product,
                start_date=historical_date,
                defaults={'value': historical_price}
            )

        # Create current price
        price, created = ProductPrice.objects.get_or_create(
            product=product,
            start_date=today,
            defaults={'value': base_price}
        )

        if created:
            print(f"  ✓ Created price for {product.name}: €{base_price}")
        else:
            print(f"  - Price for '{product.name}' already exists")


def create_delivery_notes(customers, managers, products, num_notes=100):
    """Create delivery notes spanning the last 3 months."""
    print(f"\nCreating {num_notes} delivery notes...")

    today = timezone.now()
    three_months_ago = today - timedelta(days=90)

    for i in range(num_notes):
        # Random date in the last 3 months
        days_ago = randint(0, 90)
        note_date = today - timedelta(days=days_ago)

        customer = choice(customers)
        created_by = choice(managers)
        product, _ = choice(products)

        # Generate quantity based on unit type
        if product.unit_accept_decimals():  # KG
            quantity = Decimal(str(round(uniform(0.5, 5.0), 3)))
        elif product.unit in ['DOCENA', 'PAQUETE']:
            quantity = Decimal(str(randint(1, 5)))
        else:  # Other units
            quantity = Decimal(str(randint(1, 10)))

        # Sheet number (some have it, some don't)
        sheet_number = str(randint(1000, 9999)) if randint(0, 1) else ''

        note, created = DeliveryNote.objects.get_or_create(
            customer=customer,
            created_by=created_by,
            date=note_date,
            product=product,
            quantity=quantity,
            defaults={'sheet_number': sheet_number}
        )

        if created and (i + 1) % 10 == 0:
            print(f"  ✓ Created {i + 1}/{num_notes} delivery notes...")

    print(f"  ✓ Completed creating {num_notes} delivery notes")


def print_summary():
    """Print database summary."""
    print("\n" + "="*60)
    print("DATABASE SUMMARY")
    print("="*60)

    total_users = User.objects.count()
    customers = User.objects.filter(groups__name="neveras").count()
    managers = User.objects.filter(groups__name="tienda").count()

    print(f"Users: {total_users} total")
    print(f"  - Customers (neveras): {customers}")
    print(f"  - Managers (tienda): {managers}")
    print(f"Producers: {Producer.objects.count()}")
    print(f"Products: {Product.objects.count()}")
    print(f"Product Prices: {ProductPrice.objects.count()}")
    print(f"Delivery Notes: {DeliveryNote.objects.count()}")

    print("\n" + "="*60)
    print("SAMPLE LOGIN CREDENTIALS")
    print("="*60)

    sample_customer = User.objects.filter(groups__name="neveras").first()
    sample_manager = User.objects.filter(groups__name="tienda").first()

    if sample_customer:
        print(f"Sample Customer:")
        print(f"  Username: {sample_customer.username}")
        print(f"  Password: password123")

    if sample_manager:
        print(f"\nSample Manager:")
        print(f"  Username: {sample_manager.username}")
        print(f"  Password: manager123")

    print("\n" + "="*60)


def main():
    """Main execution function."""
    print("="*60)
    print("LUPANES - Fake Data Seeding Script")
    print("="*60)

    try:
        # Create groups
        customers_group, managers_group = create_groups()

        # Create users
        customers, managers = create_users(customers_group, managers_group)

        # Create producers
        producers = create_producers()

        # Create products
        products = create_products()

        # Create product prices
        create_product_prices(products)

        # Create delivery notes
        create_delivery_notes(customers, managers, products, num_notes=100)

        # Print summary
        print_summary()

        print("\n✓ Fake data seeding completed successfully!")

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
