# Product Search API with Hybrid Search

A high-performance Django REST Framework API featuring hybrid search (full-text + fuzzy) with Redis caching, supporting English and Arabic product fields.

## Features

- 🔍 **Hybrid Search** combining:
  - Full-text search (PostgreSQL `SearchVector`)
  - Fuzzy matching (Trigram similarity)
- 🌍 **Multi-language support** (English & Arabic)
- 🎯 **Relevance-ranked results**
- ✨ **Typo tolerance** ("melk" → "milk")
- ⚡ **Redis caching** for blazing-fast repeated queries
- 📊 **Test-ready** with fake data generator

## Setup Instructions

### 1. Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Redis 7.2+
- Django 5.2+

### 2. Installation
```bash
# Clone and setup
git clone https://github.com/HossamAmeen/search-API.git
cd search-API

# Environment setup
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configuration
cp .env_example .env
# Edit .env with your credentials

# PostgreSQL extensions
psql -U youruser -d yourdb -c "CREATE EXTENSION pg_trgm; CREATE EXTENSION fuzzystrmatch;"

# Run migrations
python manage.py migrate

# Start Redis (requires Redis server installed)
redis-server &

# Generate fake products
python manage.py generate_fake_products --count 10000 --batch 1000

# Run the server
python manage.py runserver
```

### 3. API Usage

```bash
# Search products
GET /products/?search=milk
```

### 4. API Endpoints

```bash
GET /products/ - List all products
GET /products/?search={query} - Search products
```

### 5. Pagination

```bash
GET /products/?page=1 - Page number
GET /products/?page_size=10 - Number of items per page
```

