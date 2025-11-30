# Database Optimization with Indexing - Complete Guide

## 📋 Table of Contents
1. [What is Database Indexing?](#what-is-database-indexing)
2. [When to Use Indexes](#when-to-use-indexes)
3. [Types of Indexes](#types-of-indexes)
4. [Implementing Indexes in Django](#implementing-indexes-in-django)
5. [Current Project Analysis](#current-project-analysis)
6. [Recommended Indexes for This Project](#recommended-indexes-for-this-project)
7. [Query Optimization Techniques](#query-optimization-techniques)
8. [Performance Monitoring](#performance-monitoring)
9. [Best Practices](#best-practices)
10. [Common Pitfalls](#common-pitfalls)

---

## What is Database Indexing?

### 🎯 Simple Analogy
Think of a database index like an **index in a book**:
- Without an index: You must read every page to find a topic (slow)
- With an index: You look up the page number and jump directly to it (fast)

### Technical Definition
A database index is a **data structure** (typically a B-Tree) that:
- Stores a sorted copy of selected columns
- Contains pointers to the actual table rows
- Dramatically speeds up `SELECT` queries with `WHERE`, `ORDER BY`, `JOIN` clauses
- Slightly slows down `INSERT`, `UPDATE`, `DELETE` operations

### Performance Impact Example
```sql
-- Without Index: Full table scan (slow)
-- Scans ALL 1,000,000 products
SELECT * FROM catalog_product WHERE category_id = 'abc-123';
-- Time: ~2000ms

-- With Index on category_id: Index scan (fast)
-- Only reads indexed rows
SELECT * FROM catalog_product WHERE category_id = 'abc-123';
-- Time: ~5ms
```

**400x faster!** 🚀

---

## When to Use Indexes

### ✅ Good Candidates for Indexing

1. **Foreign Key Columns** (Most Important)
   ```python
   category = models.ForeignKey(Category, on_delete=models.SET_NULL)
   # Always index: used in JOINs
   ```

2. **Columns in WHERE Clauses**
   ```python
   # Frequently filtered fields
   is_available = models.BooleanField()
   status = models.CharField()
   ```

3. **Columns in ORDER BY**
   ```python
   created_at = models.DateTimeField()
   # Used for: .order_by('-created_at')
   ```

4. **Unique Fields**
   ```python
   email = models.EmailField(unique=True)
   slug = models.SlugField(unique=True)
   # Django auto-indexes these
   ```

5. **Composite Queries**
   ```python
   # If you frequently query: status='CART' AND user_id=X
   # Create composite index on (user_id, status)
   ```

### ❌ Don't Index These

1. **Small Tables** (< 1000 rows)
   - Indexes add overhead
   - Full table scan is already fast

2. **Columns with Low Cardinality**
   ```python
   # Bad: Only 2 possible values
   is_featured = models.BooleanField()  # True or False
   
   # Exception: If combined with other filters
   # WHERE is_featured=True AND category_id='abc'
   # Then composite index is useful
   ```

3. **Rarely Queried Columns**
   ```python
   # Not used in filters/sorts
   description = models.TextField()  # Don't index
   ```

4. **Frequently Updated Columns**
   - Every UPDATE must update the index
   - Slows down write operations

---

## Types of Indexes

### 1. **Single-Column Index**
```python
class Product(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]
```
**Use Case:** `Product.objects.filter(name='Laptop')`

---

### 2. **Composite (Multi-Column) Index**
```python
class Order(models.Model):
    user = models.ForeignKey(User)
    status = models.CharField()
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),  # Order matters!
        ]
```

**Use Cases:**
```python
# ✅ Uses index (matches left-to-right)
Order.objects.filter(user=user, status='PENDING')
Order.objects.filter(user=user)  # Uses first part of index

# ❌ Does NOT use index (status is 2nd column)
Order.objects.filter(status='PENDING')
```

**Rule:** Index columns match queries **left-to-right**.

---

### 3. **Partial Index** (Django 3.2+)
Index only a subset of rows.

```python
class Product(models.Model):
    is_available = models.BooleanField()
    stock_quantity = models.IntegerField()
    
    class Meta:
        indexes = [
            # Only index available products
            models.Index(
                fields=['stock_quantity'],
                condition=models.Q(is_available=True),
                name='available_products_stock_idx'
            ),
        ]
```

**Benefit:** Smaller index, faster for common queries.

---

### 4. **Unique Index**
```python
class CustomUser(models.Model):
    email = models.EmailField(unique=True)  # Auto-creates unique index
```

Django automatically creates indexes for:
- Primary keys (`id`)
- `unique=True` fields
- Foreign keys

---

### 5. **Full-Text Index** (PostgreSQL)
For text search.

```python
from django.contrib.postgres.indexes import GinIndex

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        indexes = [
            GinIndex(fields=['name', 'description']),
        ]
```

**Use with:**
```python
from django.contrib.postgres.search import SearchVector

Product.objects.annotate(
    search=SearchVector('name', 'description')
).filter(search='laptop')
```

---

## Implementing Indexes in Django

### Method 1: Model Meta Class (Recommended)

```python
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            # Single-column indexes
            models.Index(fields=['is_available'], name='product_available_idx'),
            models.Index(fields=['-created_at'], name='product_created_idx'),  # Descending
            
            # Composite indexes
            models.Index(fields=['category', 'is_available'], name='product_cat_avail_idx'),
            models.Index(fields=['is_available', 'base_price'], name='product_avail_price_idx'),
            
            # Named for clarity
            models.Index(fields=['name'], name='product_name_search_idx'),
        ]
        
        # Additional optimizations
        ordering = ['-created_at']  # Default sort order
```

### Method 2: Direct Field Specification

```python
class Product(models.Model):
    # db_index=True creates single-column index
    slug = models.SlugField(unique=True, db_index=True)
    sku = models.CharField(max_length=50, db_index=True)
```

### Generating Migrations

```bash
# Create migration
python manage.py makemigrations

# Apply to database
python manage.py migrate

# Check SQL that will run (before migrating)
python manage.py sqlmigrate catalog 0004
```

---

## Current Project Analysis

### Existing Models Review

#### **1. CustomUser Model**
```python
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True)  # Auto-indexed
    email = models.EmailField(unique=True)   # Auto-indexed
```
✅ **No additional indexes needed** (already optimized)

---

#### **2. Category Model**
```python
class Category(models.Model):
    id = models.UUIDField(primary_key=True)  # Auto-indexed
    slug = models.SlugField(unique=True)     # Auto-indexed
```
✅ **No additional indexes needed**

---

#### **3. Product Model** ⚠️ Needs Optimization

**Current Issues:**
```python
class Product(models.Model):
    category = models.ForeignKey(Category)  # ✅ Auto-indexed
    is_available = models.BooleanField()    # ❌ NOT indexed
    created_at = models.DateTimeField()     # ❌ NOT indexed
    is_featured = models.BooleanField()     # ❌ NOT indexed
```

**Common Queries:**
```python
# Query 1: Filter by availability
Product.objects.filter(is_available=True)

# Query 2: Category + availability
Product.objects.filter(category=cat, is_available=True)

# Query 3: Sort by date
Product.objects.order_by('-created_at')

# Query 4: Featured products
Product.objects.filter(is_featured=True)
```

**Recommendation:** Add composite indexes.

---

#### **4. Order Model** ⚠️ Needs Optimization

```python
class Order(models.Model):
    user = models.ForeignKey(User)         # ✅ Auto-indexed
    status = models.CharField()            # ❌ NOT indexed
    is_guest = models.BooleanField()       # ❌ NOT indexed
    session_key = models.CharField()       # ❌ NOT indexed
    created_at = models.DateTimeField()    # ❌ NOT indexed
```

**Common Queries:**
```python
# Query 1: User's orders
Order.objects.filter(user=user).exclude(status='CART')

# Query 2: Guest cart
Order.objects.get(session_key=key, status='CART', is_guest=True)

# Query 3: Order history
Order.objects.filter(user=user).order_by('-created_at')
```

**Recommendation:** Add composite indexes for common query patterns.

---

#### **5. OrderItem Model**

```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order)     # ✅ Auto-indexed
    product = models.ForeignKey(Product) # ✅ Auto-indexed
```
✅ **Sufficient** (foreign keys are indexed)

---

## Recommended Indexes for This Project

### 🎯 Priority 1: Critical Performance Indexes

```python
# catalog/models.py

class Product(models.Model):
    # ... existing fields ...
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]
        
        indexes = [
            # Index 1: Category + Availability (most common query)
            models.Index(
                fields=['category', 'is_available'],
                name='product_cat_avail_idx'
            ),
            
            # Index 2: Availability + Date (filtering + sorting)
            models.Index(
                fields=['is_available', '-created_at'],
                name='product_avail_date_idx'
            ),
            
            # Index 3: Featured products filter
            models.Index(
                fields=['is_featured', 'is_available'],
                name='product_featured_idx'
            ),
            
            # Index 4: Best sellers + top rated
            models.Index(
                fields=['is_best_seller', 'is_available'],
                name='product_bestseller_idx'
            ),
            
            # Index 5: New products
            models.Index(
                fields=['is_new', '-created_at'],
                name='product_new_idx'
            ),
        ]
```

```python
# orders/models.py

class Order(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            # Index 1: User orders (excluding cart)
            models.Index(
                fields=['user', 'status', '-created_at'],
                name='order_user_status_idx'
            ),
            
            # Index 2: Guest cart lookup
            models.Index(
                fields=['session_key', 'status', 'is_guest'],
                name='order_guest_cart_idx'
            ),
            
            # Index 3: Guest orders by email
            models.Index(
                fields=['guest_email', 'is_guest'],
                name='order_guest_email_idx'
            ),
            
            # Index 4: Order status tracking
            models.Index(
                fields=['status', '-created_at'],
                name='order_status_date_idx'
            ),
            
            # Index 5: Paid orders
            models.Index(
                fields=['status', 'paid_at'],
                condition=models.Q(status='PAID'),
                name='order_paid_idx'
            ),
        ]
```

### 🎯 Priority 2: Search Optimization (PostgreSQL)

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField

class Product(models.Model):
    # ... existing fields ...
    
    # Add search vector field (optional but faster)
    search_vector = SearchVectorField(null=True, blank=True)
    
    class Meta:
        indexes = [
            # ... existing indexes ...
            
            # Full-text search index
            GinIndex(fields=['name', 'description'], name='product_search_idx'),
        ]
```

---

## Query Optimization Techniques

### 1. **select_related()** - Reduce JOINs

**Problem: N+1 Query Problem**
```python
# BAD: Generates 101 queries (1 + 100)
products = Product.objects.all()  # 1 query
for product in products:
    print(product.category.name)  # 100 queries (one per product)
```

**Solution:**
```python
# GOOD: Generates 1 query with JOIN
products = Product.objects.select_related('category').all()  # 1 query
for product in products:
    print(product.category.name)  # No extra queries
```

**Use for:** Foreign keys and One-to-One relationships.

---

### 2. **prefetch_related()** - Optimize Reverse Relationships

```python
# BAD: N+1 queries
orders = Order.objects.all()
for order in orders:
    for item in order.items.all():  # Query per order
        print(item.product.name)

# GOOD: 2 queries total
orders = Order.objects.prefetch_related('items__product').all()
for order in orders:
    for item in order.items.all():  # No extra queries
        print(item.product.name)
```

**Use for:** Many-to-Many and reverse Foreign Keys.

---

### 3. **only() / defer()** - Limit Fields

```python
# Fetch only needed fields
products = Product.objects.only('id', 'name', 'base_price')

# Exclude heavy fields
products = Product.objects.defer('description')  # Skip TextField
```

---

### 4. **Efficient Counting**

```python
# BAD: Loads all objects
count = len(Product.objects.filter(is_available=True))

# GOOD: COUNT query only
count = Product.objects.filter(is_available=True).count()
```

---

### 5. **Bulk Operations**

```python
# BAD: N queries
for product in products:
    product.stock_quantity -= 1
    product.save()

# GOOD: 1 query
Product.objects.filter(id__in=product_ids).update(
    stock_quantity=F('stock_quantity') - 1
)
```

---

### 6. **Optimized Views Example**

```python
# orders/views.py

class CartView(generics.RetrieveAPIView):
    def get_object(self):
        # Optimized query with joins
        cart = Order.objects.select_related(
            'user'
        ).prefetch_related(
            'items__product__category',
            'items__product__images'
        ).get(
            user=self.request.user,
            status='CART'
        )
        return cart

class OrderListView(generics.ListAPIView):
    def get_queryset(self):
        # Optimized with indexes and prefetch
        return Order.objects.filter(
            user=self.request.user
        ).exclude(
            status='CART'
        ).select_related(
            'user'
        ).prefetch_related(
            'items__product'
        ).order_by('-created_at')  # Uses index
```

---

## Performance Monitoring

### 1. **Django Debug Toolbar**

Install:
```bash
pip install django-debug-toolbar
```

Configure:
```python
# settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

**Shows:**
- Number of queries per page
- Slow queries
- Index usage

---

### 2. **Query Logging**

```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

See all SQL queries in console.

---

### 3. **PostgreSQL EXPLAIN**

```python
# Shell
python manage.py shell

# Analyze query
from django.db import connection
from catalog.models import Product

products = Product.objects.filter(is_available=True)
print(products.query)  # See SQL

# Check execution plan
with connection.cursor() as cursor:
    cursor.execute(f"EXPLAIN ANALYZE {products.query}")
    print(cursor.fetchall())
```

---

### 4. **pg_stat_statements** (PostgreSQL)

Enable in PostgreSQL:
```sql
-- Add to postgresql.conf
shared_preload_libraries = 'pg_stat_statements'

-- Create extension
CREATE EXTENSION pg_stat_statements;

-- View slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## Best Practices

### ✅ Do's

1. **Index Foreign Keys** (Django does this automatically)
2. **Use Composite Indexes** for common multi-column queries
3. **Index columns in WHERE and ORDER BY**
4. **Name your indexes** for clarity
5. **Monitor query performance** regularly
6. **Use select_related() and prefetch_related()**
7. **Test with production-scale data**

### ❌ Don'ts

1. **Don't over-index** - Each index slows writes
2. **Don't index everything** - Wastes space
3. **Don't index low-cardinality columns alone** (e.g., boolean)
4. **Don't forget to migrate** after adding indexes
5. **Don't assume indexes help** - Always measure

---

## Common Pitfalls

### Pitfall 1: Wrong Index Order

```python
# Query
Order.objects.filter(status='CART').filter(user=user)

# Wrong index (less efficient)
models.Index(fields=['status', 'user'])  # ❌

# Right index (more efficient)
models.Index(fields=['user', 'status'])  # ✅
```

**Why?** More selective column first (user) narrows results faster.

---

### Pitfall 2: Indexing Without Measurement

```python
# Don't blindly add indexes
class Product(models.Model):
    # This might not help!
    class Meta:
        indexes = [
            models.Index(fields=['description']),  # Rarely queried
        ]
```

**Always profile first!**

---

### Pitfall 3: Forgetting Index Maintenance

PostgreSQL indexes need periodic maintenance:
```sql
-- Rebuild indexes
REINDEX TABLE catalog_product;

-- Analyze statistics
ANALYZE catalog_product;
```

---

## Implementation Checklist

- [ ] Analyze current query patterns
- [ ] Add indexes to Product model
- [ ] Add indexes to Order model
- [ ] Create and run migrations
- [ ] Update views with select_related/prefetch_related
- [ ] Install Django Debug Toolbar
- [ ] Test query performance
- [ ] Monitor slow queries
- [ ] Document index decisions
- [ ] Set up periodic VACUUM/ANALYZE (PostgreSQL)

---

## Quick Reference

| Scenario | Index Type | Example |
|----------|-----------|---------|
| Foreign key lookups | Auto-indexed | `user=models.ForeignKey()` |
| Unique fields | Auto-indexed | `email=models.EmailField(unique=True)` |
| Frequent WHERE clause | Single-column | `Index(fields=['status'])` |
| Multi-column filters | Composite | `Index(fields=['user', 'status'])` |
| Sorting | Include in index | `Index(fields=['-created_at'])` |
| Partial data | Partial index | `Index(..., condition=Q(...))` |
| Text search | GinIndex | `GinIndex(fields=['name'])` |

---

## Summary

### Key Takeaways

1. **Indexes = Speed** - But use them wisely
2. **Foreign keys are auto-indexed** - Don't duplicate
3. **Composite indexes for common query patterns**
4. **Order matters** in composite indexes (left-to-right)
5. **Measure before and after** - Don't guess
6. **Use Django query optimization** - select_related, prefetch_related
7. **Monitor production** - Slow queries reveal missing indexes

### Expected Performance Gains

With proper indexing:
- **Product listing**: 50-100ms → 5-10ms (10x faster)
- **Cart retrieval**: 200ms → 20ms (10x faster)
- **Order history**: 500ms → 50ms (10x faster)

---

## Next Steps

1. Apply recommended indexes
2. Test with realistic data volume
3. Monitor query performance
4. Iterate and optimize

**Remember:** Premature optimization is the root of all evil. Profile first, optimize second! 🚀
