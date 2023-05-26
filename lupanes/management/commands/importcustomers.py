import argparse
import csv

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from lupanes.users.mixins import CUSTOMERS_GROUP

User = get_user_model()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('input_file', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        customers = []
        csv_reader = csv.DictReader(options["input_file"])
        for row in csv_reader:
            username = row['Nombre nevera'].strip()
            user = User.objects.create(username=username)
            customers.append(user)

        customers_group, _ = Group.objects.get_or_create(name=CUSTOMERS_GROUP)
        qs_current_users = list(customers_group.user_set.all())
        customers_group.user_set.set(qs_current_users + customers)

        self.stdout.write(f"Imported {len(customers)} customers.")
