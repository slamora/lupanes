import argparse
import csv

from django.core.management.base import BaseCommand  # , CommandError

from lupanes.models import Customer


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        customers = []
        csv_reader = csv.DictReader(options["input_file"])
        for row in csv_reader:
            name = row['Nombre nevera'].strip()
            customers.append(Customer(name=name))

        Customer.objects.bulk_create(customers, batch_size=200)

        self.stdout.write(f"Imported {len(customers)} customers.")
