# Image Handling Guide for E-Commerce Backend

This guide covers complete image management for your Django e-commerce project, from development to production deployment.

---

## 📋 Table of Contents
1. [Current Setup](#current-setup)
2. [Development Environment](#development-environment)
3. [Image Upload & Management](#image-upload--management)
4. [API Endpoints for Images](#api-endpoints-for-images)
5. [Frontend Integration](#frontend-integration)
6. [Production Setup Options](#production-setup-options)
7. [Image Optimization](#image-optimization)
8. [Security Best Practices](#security-best-practices)

---

## 🔧 Current Setup

### Models Structure

You have two image storage mechanisms:

#### 1. **Product Model** (Legacy/Fallback)
```python
class Product(models.Model):
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
```
- Single image per product
- Kept for backward compatibility
- Can be used as fallback if ProductImage is empty

#### 2. **ProductImage Model** (Recommended)
```python
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
```
- Multiple images per product
- Image gallery support
- SEO-friendly alt text
- Explicit ordering control

### Current Settings

```python
# ecommerce_backend/settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## 💻 Development Environment

### 1. Install Pillow (Image Processing Library)

```bash
# Activate virtual environment
source venv/bin/activate

# Install Pillow
pip install Pillow

# Update requirements
pip freeze > requirements.txt
```

### 2. Verify Settings Configuration

Your `settings.py` should have:

```python
# Media Files Configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # Already configured ✅

# For local development
if DEBUG:
    import os
    os.makedirs(MEDIA_ROOT, exist_ok=True)
```

### 3. Configure URLs for Serving Media in Development

Update `ecommerce_backend/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/catalog/', include('catalog.urls')),
    path('api/orders/', include('orders.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**⚠️ Important**: This only works in development. Production requires different setup (see below).

### 4. Create Media Directory Structure

```bash
# From project root
mkdir -p ecommerce_backend/media/product_images

# Verify structure
tree ecommerce_backend/media/
# ecommerce_backend/media/
# └── product_images/
```

### 5. Add to .gitignore

```bash
# Add to .gitignore (don't commit uploaded images)
echo "ecommerce_backend/media/" >> .gitignore
echo "!ecommerce_backend/media/.gitkeep" >> .gitignore

# Keep directory structure in git
touch ecommerce_backend/media/.gitkeep
touch ecommerce_backend/media/product_images/.gitkeep
```

---

## 📤 Image Upload & Management

### Option 1: Django Admin Interface

#### Configure Admin

Update `catalog/admin.py`:

```python
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage, Category


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images"""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'order', 'is_primary', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'sale_price', 'stock_quantity', 
                    'is_available', 'primary_image_preview')
    list_filter = ('category', 'is_available', 'is_featured', 'is_new')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'sale_price')
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('base_price', 'discount_percentage', 'sale_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'is_available')
        }),
        ('Marketing', {
            'fields': ('is_featured', 'is_new', 'is_top_rated', 'is_best_seller')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def primary_image_preview(self, obj):
        """Show primary image in list view"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                primary_image.image.url
            )
        elif obj.image:  # Fallback to legacy image
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    primary_image_preview.short_description = 'Image'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'order', 'is_primary', 'image_preview', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    list_editable = ('order', 'is_primary')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'
```

**Usage:**
1. Go to `http://localhost:8000/admin/`
2. Navigate to Products
3. Create/Edit product
4. Add images in the "Product Images" inline section
5. Set one image as primary

---

### Option 2: API Endpoints for Image Upload

#### Create Serializer

Update `catalog/serializers.py`:

```python
from rest_framework import serializers
from .models import Product, ProductImage, Category


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'order', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        """Return full URL for image"""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer with image support"""
    images = ProductImageSerializer(many=True, read_only=True)
    sale_price = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'base_price', 'discount_percentage', 'sale_price',
            'stock_quantity', 'is_available',
            'is_featured', 'is_new', 'is_top_rated', 'is_best_seller',
            'image',  # Legacy fallback
            'images',  # New image gallery
            'primary_image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sale_price', 'created_at', 'updated_at']
    
    def get_primary_image(self, obj):
        """Get primary image or first image or fallback to legacy"""
        request = self.context.get('request')
        
        # Try primary image from ProductImage model
        primary = obj.images.filter(is_primary=True).first()
        if primary and request:
            return {
                'id': primary.id,
                'url': request.build_absolute_uri(primary.image.url),
                'alt_text': primary.alt_text
            }
        
        # Try first image
        first_image = obj.images.first()
        if first_image and request:
            return {
                'id': first_image.id,
                'url': request.build_absolute_uri(first_image.image.url),
                'alt_text': first_image.alt_text
            }
        
        # Fallback to legacy image field
        if obj.image and request:
            return {
                'id': None,
                'url': request.build_absolute_uri(obj.image.url),
                'alt_text': obj.name
            }
        
        return None


class ProductImageUploadSerializer(serializers.Serializer):
    """Serializer for uploading product images"""
    product_id = serializers.UUIDField()
    image = serializers.ImageField()
    alt_text = serializers.CharField(max_length=255, required=False, allow_blank=True)
    order = serializers.IntegerField(default=0, required=False)
    is_primary = serializers.BooleanField(default=False, required=False)
    
    def validate_product_id(self, value):
        """Ensure product exists"""
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product not found")
        return value
    
    def create(self, validated_data):
        """Create product image"""
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)
        
        return ProductImage.objects.create(
            product=product,
            **validated_data
        )
```

#### Create Views

Update `catalog/views.py`:

```python
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Product, ProductImage, Category
from .serializers import (
    ProductSerializer, 
    ProductImageSerializer,
    ProductImageUploadSerializer,
    CategorySerializer
)


class ProductImageUploadView(generics.CreateAPIView):
    """
    Upload a new image for a product.
    
    Admin only endpoint.
    """
    serializer_class = ProductImageUploadSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # Return created image details
        image_serializer = ProductImageSerializer(instance, context={'request': request})
        return Response(image_serializer.data, status=status.HTTP_201_CREATED)


class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a product image.
    
    Admin only endpoint.
    """
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    def delete(self, request, *args, **kwargs):
        """Delete product image"""
        instance = self.get_object()
        
        # If deleting primary image, set another as primary
        if instance.is_primary:
            next_image = instance.product.images.exclude(id=instance.id).first()
            if next_image:
                next_image.is_primary = True
                next_image.save()
        
        return super().delete(request, *args, **kwargs)


class ProductImageListView(generics.ListAPIView):
    """
    List all images for a specific product.
    
    Public endpoint.
    """
    serializer_class = ProductImageSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductImage.objects.filter(product_id=product_id).order_by('order', 'created_at')


class ProductListView(generics.ListAPIView):
    """List all products with images"""
    queryset = Product.objects.filter(is_available=True).select_related('category').prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class ProductDetailView(generics.RetrieveAPIView):
    """Get product details with all images"""
    queryset = Product.objects.filter(is_available=True).select_related('category').prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
```

#### Update URLs

Update `catalog/urls.py`:

```python
from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductImageUploadView,
    ProductImageDetailView,
    ProductImageListView,
    CategoryListView,
    CategoryDetailView,
)

urlpatterns = [
    # Products
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='product-detail'),
    
    # Product Images
    path('products/<uuid:product_id>/images/', ProductImageListView.as_view(), name='product-images'),
    path('images/upload/', ProductImageUploadView.as_view(), name='image-upload'),
    path('images/<uuid:pk>/', ProductImageDetailView.as_view(), name='image-detail'),
    
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]
```

---

## 🌐 API Endpoints for Images

### 1. **Upload Image**

```http
POST /api/catalog/images/upload/
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

Body (form-data):
- product_id: <uuid>
- image: <file>
- alt_text: "Product front view" (optional)
- order: 1 (optional)
- is_primary: true (optional)
```

**Response:**
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "image": "/media/product_images/jellaba_abc123.jpg",
    "image_url": "http://localhost:8000/media/product_images/jellaba_abc123.jpg",
    "alt_text": "Product front view",
    "order": 1,
    "is_primary": true,
    "created_at": "2025-11-30T10:00:00Z"
}
```

### 2. **List Product Images**

```http
GET /api/catalog/products/<product_id>/images/
```

**Response:**
```json
[
    {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "image": "/media/product_images/jellaba_front.jpg",
        "image_url": "http://localhost:8000/media/product_images/jellaba_front.jpg",
        "alt_text": "Front view",
        "order": 0,
        "is_primary": true,
        "created_at": "2025-11-30T10:00:00Z"
    },
    {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "image": "/media/product_images/jellaba_back.jpg",
        "image_url": "http://localhost:8000/media/product_images/jellaba_back.jpg",
        "alt_text": "Back view",
        "order": 1,
        "is_primary": false,
        "created_at": "2025-11-30T10:01:00Z"
    }
]
```

### 3. **Get Product with Images**

```http
GET /api/catalog/products/<product_id>/
```

**Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Traditional Jellaba",
    "description": "Authentic Moroccan jellaba",
    "category": "123e4567-e89b-12d3-a456-426614174002",
    "category_name": "Traditional Wear",
    "base_price": "299.99",
    "discount_percentage": "10.00",
    "sale_price": "269.99",
    "stock_quantity": 15,
    "is_available": true,
    "image": null,
    "images": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "image": "/media/product_images/jellaba_front.jpg",
            "image_url": "http://localhost:8000/media/product_images/jellaba_front.jpg",
            "alt_text": "Front view",
            "order": 0,
            "is_primary": true
        }
    ],
    "primary_image": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "url": "http://localhost:8000/media/product_images/jellaba_front.jpg",
        "alt_text": "Front view"
    }
}
```

### 4. **Update Image**

```http
PATCH /api/catalog/images/<image_id>/
Authorization: Bearer <admin_token>

Body:
{
    "alt_text": "Updated description",
    "order": 2,
    "is_primary": true
}
```

### 5. **Delete Image**

```http
DELETE /api/catalog/images/<image_id>/
Authorization: Bearer <admin_token>
```

---

## 💡 Frontend Integration

### React Example

```typescript
// Upload image
const uploadProductImage = async (productId: string, file: File) => {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('image', file);
    formData.append('alt_text', 'Product image');
    formData.append('is_primary', 'true');

    const response = await fetch('/api/catalog/images/upload/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
        body: formData,
    });

    return response.json();
};

// Display product with images
const ProductDetail = ({ product }) => {
    const [selectedImage, setSelectedImage] = useState(product.primary_image?.url);

    return (
        <div>
            {/* Main image */}
            <img 
                src={selectedImage || '/placeholder.jpg'} 
                alt={product.name}
                className="w-full h-96 object-cover"
            />

            {/* Image gallery */}
            <div className="flex gap-2 mt-4">
                {product.images.map((img) => (
                    <img
                        key={img.id}
                        src={img.image_url}
                        alt={img.alt_text}
                        className="w-20 h-20 object-cover cursor-pointer"
                        onClick={() => setSelectedImage(img.image_url)}
                    />
                ))}
            </div>

            <h1>{product.name}</h1>
            <p>${product.sale_price}</p>
        </div>
    );
};
```

---

## 🚀 Production Setup Options

### Option 1: AWS S3 (Recommended for Scale)

#### 1. Install django-storages

```bash
pip install django-storages boto3
pip freeze > requirements.txt
```

#### 2. Configure S3 in settings.py

```python
# settings.py
import environ

env = environ.Env()

# AWS Configuration
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# S3 Settings
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # 1 day cache
}
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False

# Use S3 for media files in production
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

#### 3. Environment Variables (.env)

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

#### 4. Create S3 Bucket

1. Go to AWS S3 Console
2. Create bucket with public read access
3. Configure CORS:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD", "PUT", "POST"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag"]
    }
]
```

---

### Option 2: Cloudinary (Easy Setup)

#### 1. Install cloudinary

```bash
pip install django-cloudinary-storage
pip freeze > requirements.txt
```

#### 2. Configure in settings.py

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'cloudinary_storage',
    'cloudinary',
    # ...
]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET')
}

# Use Cloudinary in production
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

#### 3. Environment Variables

```bash
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

---

### Option 3: DigitalOcean Spaces

Similar to S3 but with simpler pricing:

```python
# settings.py
AWS_ACCESS_KEY_ID = env('SPACES_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = env('SPACES_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = env('SPACES_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = f'https://{env("SPACES_REGION")}.digitaloceanspaces.com'
AWS_S3_REGION_NAME = env('SPACES_REGION', default='nyc3')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com'

if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

---

## 🎨 Image Optimization

### 1. Install Pillow for Processing

```bash
pip install Pillow
```

### 2. Create Image Utilities

Create `catalog/utils.py`:

```python
from PIL import Image
from io import BytesIO
from django.core.files import File


def compress_image(image_file, quality=85):
    """
    Compress image to reduce file size
    
    Args:
        image_file: Django UploadedFile
        quality: JPEG quality (1-100)
    
    Returns:
        Compressed File object
    """
    img = Image.open(image_file)
    
    # Convert RGBA to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Resize if too large (max 1920x1920)
    max_size = (1920, 1920)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Compress
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    return File(output, name=image_file.name)


def create_thumbnail(image_file, size=(300, 300)):
    """
    Create thumbnail version of image
    
    Args:
        image_file: Django UploadedFile
        size: Tuple of (width, height)
    
    Returns:
        Thumbnail File object
    """
    img = Image.open(image_file)
    img.thumbnail(size, Image.Resampling.LANCZOS)
    
    output = BytesIO()
    img.save(output, format='JPEG', quality=90)
    output.seek(0)
    
    return File(output, name=f'thumb_{image_file.name}')
```

### 3. Apply in Model Save Method

```python
# catalog/models.py
from .utils import compress_image

class ProductImage(models.Model):
    # ... fields
    
    def save(self, *args, **kwargs):
        # Compress image before saving
        if self.image and not self.pk:  # Only on first save
            self.image = compress_image(self.image, quality=85)
        
        # Ensure only one primary image
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, 
                is_primary=True
            ).update(is_primary=False)
        
        super().save(*args, **kwargs)
```

---

## 🔒 Security Best Practices

### 1. File Type Validation

```python
# catalog/serializers.py
from django.core.exceptions import ValidationError

def validate_image_file(file):
    """Validate uploaded image file"""
    # Check file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError("Image file too large ( > 5MB )")
    
    # Check file extension
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file extension. Use: {', '.join(valid_extensions)}")
    
    # Verify it's actually an image
    try:
        img = Image.open(file)
        img.verify()
    except Exception:
        raise ValidationError("Invalid image file")
    
    return file


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_image_file])
    # ... rest of fields
```

### 2. Sanitize Filenames

```python
import os
import uuid
from django.utils.text import slugify


def upload_to_product_images(instance, filename):
    """Generate unique filename for uploaded images"""
    # Get file extension
    ext = os.path.splitext(filename)[1].lower()
    
    # Create unique filename
    unique_id = str(uuid.uuid4())[:8]
    product_slug = slugify(instance.product.name)
    new_filename = f"{product_slug}_{unique_id}{ext}"
    
    return f'product_images/{new_filename}'


class ProductImage(models.Model):
    image = models.ImageField(upload_to=upload_to_product_images)
    # ... rest of model
```

### 3. Rate Limiting

```python
# Install django-ratelimit
pip install django-ratelimit

# catalog/views.py
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


@method_decorator(ratelimit(key='user', rate='10/h', method='POST'), name='dispatch')
class ProductImageUploadView(generics.CreateAPIView):
    """Rate limit: 10 uploads per hour per user"""
    # ... view code
```

---

## 📊 Testing Image Uploads

### Using cURL

```bash
# Upload image
curl -X POST http://localhost:8000/api/catalog/images/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "product_id=550e8400-e29b-12d3-a456-446655440000" \
  -F "image=@/path/to/image.jpg" \
  -F "alt_text=Product view" \
  -F "is_primary=true"

# Get product images
curl http://localhost:8000/api/catalog/products/550e8400-e29b-12d3-a456-446655440000/images/
```

### Using Python Requests

```python
import requests

# Upload
url = 'http://localhost:8000/api/catalog/images/upload/'
headers = {'Authorization': f'Bearer {access_token}'}
files = {'image': open('product.jpg', 'rb')}
data = {
    'product_id': '550e8400-e29b-41d4-a716-446655440000',
    'alt_text': 'Product image',
    'is_primary': True
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

---

## 📋 Checklist

### Development Setup
- [ ] Install Pillow
- [ ] Configure MEDIA_URL and MEDIA_ROOT
- [ ] Add media URL pattern to urls.py
- [ ] Create media directory structure
- [ ] Add media/ to .gitignore
- [ ] Configure admin for image management

### Production Setup
- [ ] Choose storage backend (S3/Cloudinary/Spaces)
- [ ] Install required packages (django-storages, boto3)
- [ ] Configure environment variables
- [ ] Create bucket/space with public read access
- [ ] Configure CORS for your frontend domain
- [ ] Test image upload in production
- [ ] Set up CDN (CloudFront/Cloudflare) for faster delivery

### Optimization
- [ ] Implement image compression
- [ ] Add file size validation
- [ ] Add file type validation
- [ ] Sanitize filenames
- [ ] Create thumbnails for listings
- [ ] Add rate limiting

### Security
- [ ] Validate file types
- [ ] Limit file sizes
- [ ] Sanitize filenames
- [ ] Use admin-only upload endpoints
- [ ] Configure proper CORS
- [ ] Use HTTPS in production

---

## 🎯 Summary

**Development:**
- Use local filesystem with Django's static file serving
- Upload via Django admin or API endpoints

**Production:**
- Use AWS S3, Cloudinary, or DigitalOcean Spaces
- Configure CDN for fast global delivery
- Implement image optimization and compression

**Best Practices:**
- Multiple images per product via ProductImage model
- Automatic compression on upload
- Secure file validation
- Admin-only upload permissions
- CDN for performance

Your current setup supports both approaches - you have the models ready, just need to choose your production storage! 🚀
