import logging
import argparse
import csv
from decimal import Decimal

from django.core.management.base import BaseCommand

from lupanes.models import DeliveryNote, Producer, Product, ProductPrice

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        debug = False   # TODO(@slamora): add_argument
        drop = True | False   # TODO(@slamora): add_argument

        csv_reader = csv.DictReader(options["input_file"])

        if debug:
            with open("/tmp/outfile.csv", mode="w") as outfile:
                csv_writer = csv.DictWriter(outfile, fieldnames=csv_reader.fieldnames)
                csv_writer.writeheader()
                for row in csv_reader:
                    item = Row(row)
                    value = {
                        "producto": item.product,
                        "fecha": item.date,
                        "precio": item.price,
                        "productor": item.producer,
                    }
                    csv_writer.writerow(value)

        if drop:
            DeliveryNote.objects.all().delete()
            Product.objects.all().delete()
            Producer.objects.all().delete()

        products = {}
        for row in csv_reader:
            item = Row(row)
            if item.product in products:
                product = products[item.product]
            else:
                producer, _ = Producer.objects.get_or_create(name=item.producer)
                product = Product.objects.create(name=item.product, unit=item.unit, producer=producer)
                products[item.product] = product

            ProductPrice.objects.create(value=item.price, start_date=item.date, product=product)


class Row:
    # some date before Lupierra era
    DEFAULT_DATE = "2000-01-01"

    def __init__(self, data):
        self.data = data
        self.product = self.clean_product()
        self.price = self.clean_price()
        self.producer = self.clean_producer()
        self.unit = self.clean_unit()

    def clean_product(self):
        value = self.data['producto'].strip()

        # extract start_date to create ProductPrice
        date_beg = value.rfind("(")

        if date_beg == -1:
            self.date = Row.DEFAULT_DATE
            return value

        date_end = value.rfind(")")
        date_raw = value[date_beg + 1:date_end]

        # discard noisy data
        date_raw = date_raw.replace("desde el ", "")
        date_raw = date_raw.replace("desde ", "")

        from datetime import datetime
        try:
            date_parsed = datetime.strptime(date_raw, "%d/%m/%Y")
        except ValueError as e:
            logger.debug(e)
            try:
                date_parsed = datetime.strptime(date_raw, "%d/%m/%y")
            except ValueError as e:
                # seems that there is no date
                logger.debug(e)
                self.date = Row.DEFAULT_DATE
                return value

        self.date = date_parsed.strftime("%Y-%m-%d")

        product_name = value[0:date_beg].strip()
        return product_name

    def clean_price(self):
        value = self.data['precio'].replace(',', '.')
        try:
            return Decimal(value)
        except Exception as e:
            print(e)
            print(value)

    def clean_producer(self):
        value = self.data['productor']
        return value

    def clean_unit(self):
        value = self.data['unidad']
        return Product.Unit(value.strip())
