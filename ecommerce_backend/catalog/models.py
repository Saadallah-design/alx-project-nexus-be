from django.db import models
from uuid import uuid4
from decimal import Decimal
# uuid is a module that provides a way to generate unique identifiers
# it is useful for creating unique primary keys for database records


# First model: Category

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    # the id is used here for security reasons
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]
        # unique_together = [["slug", "parent"]] This line here is if I intend to use nested categories like shoes/boots
        # indexes = [models.Index(fields=["slug"])]: This line here is if I want to create an index on the slug field
        # the indexes are used to speed up the search process
    
    def __str__(self):
        return self.name
        

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    # for now I will keep this as fallback but I will create a seperate ProductImage model
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    # for the discount percentage i will add a property to handle it: best practices
    stock_quantity = models.IntegerField(default=0)
    # for the stock quantity, I better add validation to make sure it is not negative
    # I can do it by adding a custom validator
    # validators=[MinValueValidator(0)]

    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # later if I wanted to add discount_percentage or other fields.

    
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)

    # Marketing fields: currently these are somehow static. meaning that the admin will have to set them manually.
    #  in order to make it data driven
    is_top_rated = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]
        
    def __str__(self):
        return self.name

    # Model Property: Calculate sale price dynamically (Best Practice)
    @property
    def sale_price(self):
        if self.discount_percentage > 0:
            discount_amount = self.base_price * (self.discount_percentage / 100)
            return self.base_price - discount_amount
        return self.base_price


class ProductImage(models.Model):
    """Multiple images for a product"""
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images'  # Allows: product.images.all()
    )
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, help_text="SEO alt text")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_primary = models.BooleanField(default=False, help_text="Main product image")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']  
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
    
    def __str__(self):
        return f"Image for {self.product.name} (Order: {self.order})"
    
    def save(self, *args, **kwargs):
        # Auto-set as primary if it's the first image
        if self.is_primary:
            # Ensure only one primary image per product
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)