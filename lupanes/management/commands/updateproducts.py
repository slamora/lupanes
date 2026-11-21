import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from lupanes.models import Producer, Product


class Command(BaseCommand):
    help = "Update existing products from an exported products CSV file."

    required_columns = {
        "id",
        "name",
        "description",
        "producer_id",
        "producer__name",
        "unit",
        "is_active",
    }

    def add_arguments(self, parser):
        parser.add_argument("input_file", help="Path to the exported products CSV file.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the changes without updating products.",
        )

    def handle(self, *args, **options):
        try:
            with open(options["input_file"], encoding="utf-8-sig", newline="") as input_file:
                csv_reader = csv.DictReader(input_file)
                self.validate_columns(csv_reader.fieldnames)
                updated_count, error_count = self.process_rows(csv_reader, options["dry_run"])
        except OSError as error:
            raise CommandError(f"Could not read CSV file {options['input_file']!r}: {error}") from error

        if options["dry_run"]:
            self.stdout.write("Dry run: no changes made.")
        else:
            noun = "product" if updated_count == 1 else "products"
            self.stdout.write(f"Updated {updated_count} {noun}.")
        if error_count:
            noun = "row" if error_count == 1 else "rows"
            self.stderr.write(f"Skipped {error_count} {noun} due to errors.")

    def validate_columns(self, fieldnames):
        missing_columns = self.required_columns - set(fieldnames or [])
        if missing_columns:
            columns = ", ".join(sorted(missing_columns))
            raise CommandError(f"CSV is missing required columns: {columns}")

    def process_rows(self, csv_reader, dry_run):
        updated_count = 0
        error_count = 0
        seen_product_ids = set()
        for row_number, row in enumerate(csv_reader, start=2):
            try:
                missing_values = [column for column in self.required_columns if row.get(column) is None]
                if missing_values:
                    columns = ", ".join(sorted(missing_values))
                    raise CommandError(f"Row {row_number}: missing values for columns: {columns}")

                product = self.get_product(row, row_number)
                if product.pk in seen_product_ids:
                    raise CommandError(f"Row {row_number}: duplicate product id {product.pk}.")
                seen_product_ids.add(product.pk)
                changes = self.get_changes(product, row, row_number)
            except CommandError as error:
                self.stderr.write(str(error))
                error_count += 1
                continue

            if not changes:
                self.print_changes(product, changes)
                continue

            self.print_changes(product, changes)
            try:
                with transaction.atomic():
                    for field, value in changes.items():
                        setattr(product, field, value)
                    product.save(update_fields=list(changes))
                    if dry_run:
                        transaction.set_rollback(True)
            except IntegrityError as error:
                self.stderr.write(f"Row {row_number}: could not update product {product.pk}: {error}")
                error_count += 1
                continue

            if not dry_run:
                updated_count += 1

        return updated_count, error_count

    def get_product(self, row, row_number):
        try:
            product_id = int(row["id"])
        except (TypeError, ValueError):
            raise CommandError(f"Row {row_number}: invalid product id {row.get('id')!r}.")

        try:
            return Product.objects.select_related("producer").get(pk=product_id)
        except Product.DoesNotExist:
            raise CommandError(f"Row {row_number}: product id {product_id} does not exist.")

    def get_changes(self, product, row, row_number):
        producer_id = self.parse_integer(row, "producer_id", row_number)
        try:
            producer = Producer.objects.get(pk=producer_id)
        except Producer.DoesNotExist:
            raise CommandError(f"Row {row_number}: producer id {producer_id} does not exist.")

        producer_name = (row.get("producer__name") or "").strip()
        if producer.name != producer_name:
            raise CommandError(
                f"Row {row_number}: producer id {producer_id} is {producer.name!r}, "
                f"not {producer_name!r}."
            )

        name = (row.get("name") or "").strip()
        if not name:
            raise CommandError(f"Row {row_number}: product name cannot be empty.")

        unit_value = (row.get("unit") or "").strip()
        try:
            unit = Product.Unit(unit_value)
        except ValueError:
            valid_units = ", ".join(Product.Unit.values)
            raise CommandError(f"Row {row_number}: invalid unit {unit_value!r}; expected one of {valid_units}.")

        active_value = (row.get("is_active") or "").strip().lower()
        if active_value in {"sí", "si"}:
            is_active = True
        elif active_value == "no":
            is_active = False
        else:
            raise CommandError(f"Row {row_number}: invalid is_active value {active_value!r}; expected 'sí' or 'no'.")

        proposed_values = {
            "name": name,
            "description": row.get("description") or "",
            "producer": producer,
            "unit": unit,
            "is_active": is_active,
        }
        return {
            field: value
            for field, value in proposed_values.items()
            if getattr(product, field) != value
        }

    @staticmethod
    def parse_integer(row, field, row_number):
        try:
            return int(row[field])
        except (TypeError, ValueError):
            raise CommandError(f"Row {row_number}: invalid {field} value {row.get(field)!r}.")

    def print_changes(self, product, changes):
        self.stdout.write(f"Product {product.pk} ({product.name}):")
        if not changes:
            self.stdout.write("  no changes.")
            return

        for field, new_value in changes.items():
            old_value = getattr(product, field)
            if field == "producer":
                old_value = old_value.name
                new_value = new_value.name
            elif field == "is_active":
                old_value = "sí" if old_value else "no"
                new_value = "sí" if new_value else "no"
            elif field == "unit":
                old_value = str(old_value)
                new_value = str(new_value)
            self.stdout.write(f"  {field}: {old_value!r} -> {new_value!r}")
