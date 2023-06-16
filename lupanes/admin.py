from django.contrib import admin
from django.utils.formats import date_format

from lupanes.models import DeliveryNote, Producer, Product


@admin.register(DeliveryNote)
class DeliveryNoteAdmin(admin.ModelAdmin):
    list_display = ["date_short", "customer", "product", "quantity"]
    ordering = ["date"]

    def date_short(self, obj):
        return date_format(obj.date, format='SHORT_DATE_FORMAT', use_l10n=True)
    date_short.admin_order_field = "date"
    date_short.short_description = "Date"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "producer", "unit", "is_active"]
    ordering = ["name"]


admin.site.register(Producer)
