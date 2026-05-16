from django.contrib import admin
from django.utils.formats import date_format

from lupanes.models import DeliveryNote, Producer, Product, ProductPrice


@admin.register(DeliveryNote)
class DeliveryNoteAdmin(admin.ModelAdmin):
    list_display = ["date_short", "customer", "product", "quantity"]
    list_filter = ["date__year"]
    search_fields = ["customer__username", "product__name"]
    ordering = ["date"]

    def date_short(self, obj):
        return date_format(obj.date, format='SHORT_DATE_FORMAT', use_l10n=True)
    date_short.admin_order_field = "date"
    date_short.short_description = "Date"


class ProductPriceInline(admin.TabularInline):
    model = ProductPrice


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "producer", "unit", "is_active"]
    list_filter = ["producer", "is_active"]
    search_fields = ["name", "producer__name"]
    inlines = [ProductPriceInline]
    ordering = ["name"]


admin.site.register(Producer)
