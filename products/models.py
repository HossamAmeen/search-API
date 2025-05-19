# products/models.py
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models


class Category(models.Model):
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name_en


class Brand(models.Model):
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name_en


class Product(models.Model):
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True,
                               null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True)

    # Search fields
    search_vector_en = SearchVectorField(null=True, blank=True)
    search_vector_ar = SearchVectorField(null=True, blank=True)

    # Nutrition facts (simplified)
    calories = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector_en"]),
            GinIndex(fields=["search_vector_ar"]),
            GinIndex(
                fields=["name_en"],
                name="name_en_trgm_idx",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["name_ar"],
                name="name_ar_trgm_idx",
                opclasses=["gin_trgm_ops"],
            ),
            models.Index(fields=["barcode"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.name_en
