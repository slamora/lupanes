# python manage.py shell <<'PY'
import csv
from lupanes.models import Product

output_path = "/tmp/products-export.csv"

with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "id",
        "name",
        "description",
        "producer_id",
        "producer__name",
        "unit",
        "is_active",
    ])

    for product in Product.objects.select_related("producer").order_by("id"):
        writer.writerow([
            product.id,
            product.name,
            product.description,
            product.producer_id,
            product.producer.name,
            product.unit,
            "sí" if product.is_active else "no",
        ])

print(f"CSV written to {output_path}")
# PY
