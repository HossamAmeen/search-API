# products/views.py
from django.core.cache import cache
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from .filters import ProductSearchFilter
from .models import Product
from .serializers import ProductSerializer


class ProductAPIView(ListAPIView):
    queryset = Product.objects.select_related("brand", "category").all()
    serializer_class = ProductSerializer
    filterset_class = ProductSearchFilter

    def list(self, request, *args, **kwargs):
        cache_key = f"product_search_{request.GET.urlencode()}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            cache.set(cache_key, response.data, timeout=60*15)
            return response

        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60*15)
        return Response(serializer.data)
