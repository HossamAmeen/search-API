# products/management/commands/generate_fake_products.py
import random

from bidi.algorithm import get_display
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from faker import Faker
from unidecode import unidecode

from products.models import Brand, Category, Product


class Command(BaseCommand):
    help = "Generates fake product data with guaranteed unique barcodes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10000,
            help="Number of products to generate (default: 10000)",
        )
        parser.add_argument(
            "--batch",
            type=int,
            default=1000,
            help="Batch size for bulk creation (default: 1000)",
        )

    def handle(self, *args, **options):
        num_products = options["count"]
        batch_size = options["batch"]

        fake = Faker()
        Faker.seed(42)  # For reproducible results

        # Arabic Faker
        fake_ar = Faker("ar_AA")

        # Create or get categories
        category_data = [
            {"en": "Dairy", "ar": "ألبان"},
            {"en": "Beverages", "ar": "مشروبات"},
            {"en": "Snacks", "ar": "وجبات خفيفة"},
            {"en": "Bakery", "ar": "مخبوزات"},
            {"en": "Canned Goods", "ar": "سلع معلبة"},
            {"en": "Frozen Foods", "ar": "أطعمة مجمدة"},
            {"en": "Meat", "ar": "لحوم"},
            {"en": "Produce", "ar": "منتجات"},
            {"en": "Cleaning", "ar": "تنظيف"},
            {"en": "Personal Care", "ar": "العناية الشخصية"},
        ]

        self.stdout.write("Creating categories...")
        categories = []
        for data in category_data:
            cat, created = Category.objects.get_or_create(
                slug=slugify(unidecode(data["en"])),
                defaults={"name_en": data["en"], "name_ar": data["ar"]},
            )
            categories.append(cat)
            if created:
                self.stdout.write(f"Created category: {data['en']}")

        # Create or get brands
        brand_data = [
            {"en": "Nestle", "ar": "نستله"},
            {"en": "Pepsi", "ar": "بيبسي"},
            {"en": "Coca-Cola", "ar": "كوكا كولا"},
            {"en": "Kelloggs", "ar": "كيلوغز"},
            {"en": "Unilever", "ar": "يونيليفر"},
            {"en": "P&G", "ar": "بي آند جي"},
            {"en": "Danone", "ar": "دانون"},
            {"en": "Mars", "ar": "مارس"},
            {"en": "Cadbury", "ar": "كادبوري"},
            {"en": "Heinz", "ar": "هاينز"},
        ]

        self.stdout.write("Creating brands...")
        brands = []
        for data in brand_data:
            brand, created = Brand.objects.get_or_create(
                slug=slugify(unidecode(data["en"]).replace("&", "and")),
                defaults={"name_en": data["en"], "name_ar": data["ar"]},
            )
            brands.append(brand)
            if created:
                self.stdout.write(f"Created brand: {data['en']}")

        # Arabic food names with English translations
        arabic_foods = [
            ("حليب", "Milk"),
            ("خبز", "Bread"),
            ("جبن", "Cheese"),
            ("زبادي", "Yogurt"),
            ("عسل", "Honey"),
            ("زيتون", "Olives"),
            ("تمر", "Dates"),
            ("فول", "Fava Beans"),
            ("حمص", "Chickpeas"),
            ("طحينة", "Tahini"),
            ("رز", "Rice"),
            ("عدس", "Lentils"),
            ("سمك", "Fish"),
            ("لحم", "Meat"),
            ("دجاج", "Chicken"),
            ("بيض", "Eggs"),
            ("فواكه", "Fruits"),
            ("خضار", "Vegetables"),
            ("عصير", "Juice"),
            ("ماء", "Water"),
        ]

        # Generate products in a transaction
        with transaction.atomic():
            self.stdout.write("Checking existing barcodes...")
            used_barcodes = set(Product.objects.values_list(
                "barcode", flat=True))

            created_count = 0

            self.stdout.write(
                f"Generating {num_products} products in batches of "
                f"{batch_size}..."
            )

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

                    products_batch.append(
                        Product(
                            name_en=en_name,
                            name_ar=ar_name,
                            description_en=fake.paragraph(),
                            description_ar=get_display(fake_ar.paragraph()),
                            brand=random.choice(brands),
                            category=random.choice(categories),
                            barcode=barcode,
                            calories=random.randint(0, 500),
                            protein=round(random.uniform(0, 30), 1)
                        )
                    )

                Product.objects.bulk_create(products_batch)
                created_count += current_batch
                self.stdout.write(f"Created {created_count}/{num_products} products...")

        # Update search vectors
        self.stdout.write("Updating search vectors...")
        from django.contrib.postgres.search import SearchVector

        Product.objects.update(
            search_vector_en=SearchVector("name_en", "description_en"),
            search_vector_ar=SearchVector("name_ar", "description_ar"),
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {num_products} products with unique barcodes and updated search vectors"
            )
        )
