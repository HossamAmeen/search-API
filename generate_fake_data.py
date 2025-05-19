# products/utils/generate_fake_data.py
import random
from faker import Faker
from bidi.algorithm import get_display
from unidecode import unidecode
from django.utils.text import slugify
from django.db import transaction
from products.models import Product, Category, Brand

def generate_fake_products(num_products=10000):
    """Generate fake product data with guaranteed unique barcodes"""
    fake = Faker()
    Faker.seed(42)  # For reproducible results
    
    # Arabic Faker
    fake_ar = Faker('ar_AA')
    
    # Create or get categories
    category_data = [
        {'en': 'Dairy', 'ar': 'ألبان'},
        # ... rest of category data ...
    ]
    
    categories = []
    for data in category_data:
        cat, created = Category.objects.get_or_create(
            slug=slugify(unidecode(data['en'])),
            defaults={
                'name_en': data['en'],
                'name_ar': data['ar']
            }
        )
        categories.append(cat)
    
    # Create or get brands
    brand_data = [
        {'en': 'Nestle', 'ar': 'نستله'},
        # ... rest of brand data ...
    ]
    
    brands = []
    for data in brand_data:
        brand, created = Brand.objects.get_or_create(
            slug=slugify(unidecode(data['en']).replace('&', 'and')),
            defaults={
                'name_en': data['en'],
                'name_ar': data['ar']
            }
        )
        brands.append(brand)
    
    # Arabic food names with English translations
    arabic_foods = [
        ('حليب', 'Milk'),
        # ... rest of food data ...
    ]
    
    # Generate products in a transaction
    with transaction.atomic():
        # Track used barcodes in memory
        used_barcodes = set(Product.objects.values_list('barcode', flat=True))
        
        batch_size = 1000
        created_count = 0
        
        while created_count < num_products:
            current_batch = min(batch_size, num_products - created_count)
            products_batch = []
            
            for _ in range(current_batch):
                # Generate unique barcode
                while True:
                    barcode = fake.ean13()
                    if barcode not in used_barcodes:
                        used_barcodes.add(barcode)
                        break
                
                # Choose a random Arabic food or generate a fake name
                if random.random() < 0.7:
                    ar_name, en_name = random.choice(arabic_foods)
                    if random.random() < 0.5:
                        ar_name = f"{random.choice(['جديد', 'طبيعي', 'عضوي', 'خاص'])} {ar_name}"
                        en_name = f"{random.choice(['New', 'Natural', 'Organic', 'Special'])} {en_name}"
                else:
                    en_name = fake.catch_phrase()
                    ar_name = get_display(fake_ar.text(max_nb_chars=20))
                
                products_batch.append(Product(
                    name_en=en_name,
                    name_ar=ar_name,
                    description_en=fake.paragraph(),
                    description_ar=get_display(fake_ar.paragraph()),
                    brand=random.choice(brands),
                    category=random.choice(categories),
                    barcode=barcode,
                    calories=random.randint(0, 500),
                    protein=round(random.uniform(0, 30), 1),
                    carbs=round(random.uniform(0, 100), 1),
                    fat=round(random.uniform(0, 50), 1)
                ))
            
            Product.objects.bulk_create(products_batch)
            created_count += current_batch
            print(f"Created {created_count}/{num_products} products...")
    
    # Update search vectors
    print("Updating search vectors...")
    from django.contrib.postgres.search import SearchVector
    Product.objects.update(
        search_vector_en=SearchVector('name_en', 'description_en'),
        search_vector_ar=SearchVector('name_ar', 'description_ar')
    )
    
    print(f"Successfully created {num_products} products with unique barcodes")