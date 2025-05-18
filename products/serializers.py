# products/serializers.py
from rest_framework import serializers
from .models import Product, Category, Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name_en', 'name_ar', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name_en', 'name_ar', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    category = CategorySerializer()
    rank_en = serializers.FloatField()
    rank_ar = serializers.FloatField()
    
    
    class Meta:
        model = Product
        fields = '__all__'
