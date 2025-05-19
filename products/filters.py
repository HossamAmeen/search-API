from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.db.models import F, Q
from django_filters import rest_framework as filters

from .models import Product


class ProductSearchFilter(filters.FilterSet):
    search = filters.CharFilter(method="universal_search", label="Search")

    class Meta:
        model = Product
        fields = ["search"]

    def universal_search(self, queryset, name, value):
        if not value or len(value) < 2:
            return queryset.none()

        # Create search vectors using only existing fields
        vector_en = SearchVector("name_en", weight="A") + SearchVector(
            "description_en", weight="B"
        )
        vector_ar = SearchVector("name_ar", weight="A") + SearchVector(
            "description_ar", weight="B"
        )

        search_query = SearchQuery(value, config="simple")

        queryset = queryset.annotate(
            ft_rank_en=SearchRank(vector_en, search_query),
            ft_rank_ar=SearchRank(vector_ar, search_query),
            fuzzy_name_en=TrigramSimilarity("name_en", value),
            fuzzy_name_ar=TrigramSimilarity("name_ar", value),
            fuzzy_desc_en=TrigramSimilarity("description_en", value),
            fuzzy_desc_ar=TrigramSimilarity("description_ar", value),
            relevance=(
                (F("ft_rank_en") + F("ft_rank_ar")) * 0.7
                + (F("fuzzy_name_en") + F("fuzzy_name_ar")) * 0.3
                + (F("fuzzy_desc_en") + F("fuzzy_desc_ar")) * 0.2
            ),
        )

        return queryset.filter(
            Q(ft_rank_en__gt=0.1)
            | Q(ft_rank_ar__gt=0.1)
            | Q(fuzzy_name_en__gt=0.2)
            | Q(fuzzy_name_ar__gt=0.2)
            | Q(name_en__icontains=value)  # Fallback partial match
            | Q(name_ar__icontains=value)  # Fallback partial match
        ).order_by("-relevance")
