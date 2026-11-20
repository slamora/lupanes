from typing import Any, Dict

from django.db.models.functions import Lower
from django.db.models.query import QuerySet

from lupanes.models import Producer, Product


class ProductFilter:
    """Encapsulates validation, filtering, sorting, and UI metadata for Products."""

    DEFAULT_SORT = "name"
    TIE_BREAKERS = ("producer__name", Lower("name"), "pk")

    def __init__(self, query_params: Dict[str, Any], user: Any):
        self.params = query_params
        self.user = user
        self.can_filter_status: bool = getattr(user, "is_manager", False)

        # Cleaned / validated filter parameters
        self.search_query: str = self.params.get("q", "").strip()
        self.selected_producer: str = ""
        self.selected_unit: str = ""
        self.selected_active: str = ""
        self.selected_sort: str = self.DEFAULT_SORT
        self.visible_producer_ids: QuerySet = Producer.objects.none()

        self._init_sort_fields()

    def _init_sort_fields(self) -> None:
        self.sort_fields = {
            "name": Lower("name"),
            "producer": "producer__name",
            "unit": "unit",
        }
        if self.can_filter_status:
            self.sort_fields["is_active"] = "is_active"

    def filter_queryset(self, base_queryset: QuerySet[Product]) -> QuerySet[Product]:
        qs = base_queryset.select_related("producer")

        if not self.can_filter_status:
            qs = qs.filter(is_active=True)

        # Producers available in the filtered scope (before producer-specific filter)
        self.visible_producer_ids = (
            qs.order_by().values_list("producer_id", flat=True).distinct()
        )

        if self.search_query:
            qs = qs.filter(name__icontains=self.search_query)

        producer_id = self.params.get("producer", "")
        if producer_id.isdigit():
            self.selected_producer = producer_id
            qs = qs.filter(producer_id=producer_id)

        unit = self.params.get("unit", "")
        if unit in Product.Unit.values:
            self.selected_unit = unit
            qs = qs.filter(unit=unit)

        if self.can_filter_status:
            active = self.params.get("is_active", "")
            if active in {"0", "1"}:
                self.selected_active = active
                qs = qs.filter(is_active=(active == "1"))

        return qs.order_by(self._resolve_ordering(), *self.TIE_BREAKERS)

    def _resolve_ordering(self) -> Any:
        sort_raw = self.params.get("sort", self.DEFAULT_SORT)
        descending = sort_raw.startswith("-")
        field_name = sort_raw.removeprefix("-")

        if field_name not in self.sort_fields or sort_raw.count("-") > 1:
            self.selected_sort = self.DEFAULT_SORT
            descending = False
            field_name = self.DEFAULT_SORT
        else:
            self.selected_sort = sort_raw

        ordering = self.sort_fields[field_name]
        if isinstance(ordering, str):
            return f"-{ordering}" if descending else ordering
        return ordering.desc() if descending else ordering

    def get_sort_urls(self) -> Dict[str, str]:
        sort_urls = {}
        for field in self.sort_fields:
            for sort_value, url_key in ((field, field), (f"-{field}", f"{field}_desc")):
                query_copy = self.params.copy()
                query_copy["sort"] = sort_value
                sort_urls[url_key] = f"?{query_copy.urlencode()}"
        return sort_urls
