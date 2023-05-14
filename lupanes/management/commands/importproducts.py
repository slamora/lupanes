import argparse
import csv
from decimal import Decimal

from django.core.management.base import BaseCommand

from lupanes.models import Producer, Product, ProductPrice


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('r'))

    def handle(self, *args, **options):

        csv_reader = csv.DictReader(options["input_file"])
        for row in csv_reader:
            item = Row(row)

            producer, _ = Producer.objects.get_or_create(name=item.producer)
            # TODO(@slamora) handle units
            product = Product.objects.create(name=item.product, unit=Product.Unit.UNIDAD, producer=producer)
            ProductPrice.objects.create(value=item.price, start_date="2010-01-01", product=product)


class Row:
    def __init__(self, data):
        self.data = data
        self.product = self.clean_product()
        self.price = self.clean_price()
        self.producer = self.clean_producer()

    def clean_product(self):
        value = self.data['producto'].strip()
        # TODO(@slamora: extract start_date to create ProductPrice
        return value

    def clean_price(self):
        value = self.data['precio'].replace(',', '.')
        return Decimal(value)

    def clean_producer(self):
        value = self.data['productor']
        return value
