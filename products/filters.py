# products/filters.py
from django.db.models import Q, Func
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.contrib.postgres.lookups import Unaccent
import django_filters
from .models import Product

from django.db.models import Func, F
from django.db.models.functions import Lower

class Unaccent(Func):
    function = 'unaccent'
    template = "%(function)s(%(expressions)s)"


class ProductFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method='custom_search')
    category = django_filters.CharFilter(field_name='category__slug')
    brand = django_filters.CharFilter(field_name='brand__slug')
    min_calories = django_filters.NumberFilter(field_name='calories', lookup_expr='gte')
    max_calories = django_filters.NumberFilter(field_name='calories', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['query', 'category', 'brand', 'min_calories', 'max_calories']

    def custom_search(self, queryset, name, value):
        if not value:
            return queryset

        normalized_query = value.lower()
        terms = normalized_query.split()

        search_query_en = SearchQuery(normalized_query, config='english')
        search_query_ar = SearchQuery(normalized_query, config='arabic')

        # Annotate unaccented and lowercased fields
        queryset = queryset.annotate(
            name_en_unaccented=Lower(Unaccent(F('name_en'))),
            name_ar_unaccented=Lower(Unaccent(F('name_ar'))),
            rank_en=SearchRank(F('search_vector_en'), search_query_en),
            rank_ar=SearchRank(F('search_vector_ar'), search_query_ar),
        )

        conditions = Q()
        for term in terms:
            term = term.lower()
            conditions |= Q(name_en__icontains=term)
            conditions |= Q(name_ar__icontains=term)
            conditions |= Q(name_en_unaccented__icontains=term)
            conditions |= Q(name_ar_unaccented__icontains=term)

        return queryset.filter(
            Q(search_vector_en=search_query_en) |
            Q(search_vector_ar=search_query_ar) |
            conditions
        ).order_by('-rank_en', '-rank_ar').distinct()
