# 🚀 E-Commerce API Documentation

**Base URL:** `http://localhost:8000`  
**Version:** 1.0  
**Authentication:** JWT (JSON Web Tokens)

---

## 📑 Table of Contents

1. [Authentication](#authentication)
2. [Products](#products)
3. [Categories](#categories)
4. [Shopping Cart](#shopping-cart)
5. [Orders](#orders)
6. [User Profile](#user-profile)
7. [Error Handling](#error-handling)

---

## 🔐 Authentication

### Register New User
```http
POST /api/auth/register/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

---

### Login (Get Tokens)
```http
POST /api/auth/token/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Token Lifetimes:**
- Access Token: 5 minutes
- Refresh Token: 1 day

---

### Refresh Access Token
```http
POST /api/auth/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "your-refresh-token"
}
```

**Response (200 OK):**
```json
{
  "access": "new-access-token",
  "refresh": "new-refresh-token"
}
```

---

### Logout (Blacklist Token)
```http
POST /api/auth/token/blacklist/
```

**Headers:**
```
Authorization: Bearer <access-token>
```

**Request Body:**
```json
{
  "refresh": "your-refresh-token"
}
```

---

## 🛍️ Products

### List All Products
```http
GET /api/catalog/products/
```

**Response (200 OK):**
```json
[
  {
    "id": "be6d475c-0bb9-4a5b-a1d8-eceb5e15ecf3",
    "category": {
      "id": "uuid",
      "name": "Jellaba",
      "slug": "jellaba"
    },
    "name": "Veste en Brochet avec Sfifa Merema",
    "description": "Beautiful traditional vest",
    "base_price": "350.00",
    "sale_price": "350.00",
    "discount_percentage": "0.00",
    "images": [
      {
        "id": 1,
        "image": "/media/product_images/veste_front.jpg",
        "image_url": "http://localhost:8000/media/product_images/veste_front.jpg",
        "alt_text": "Front view",
        "order": 0,
        "is_primary": true
      },
      {
        "id": 2,
        "image": "/media/product_images/veste_back.jpg",
        "image_url": "http://localhost:8000/media/product_images/veste_back.jpg",
        "alt_text": "Back view",
        "order": 1,
        "is_primary": false
      }
    ],
    "stock_quantity": 10,
    "is_available": true,
    "is_featured": false,
    "created_at": "2025-11-29T12:00:00Z",
    "updated_at": "2025-11-29T12:00:00Z"
  }
]
```

---

### Get Single Product
```http
GET /api/catalog/products/<product-id>/
```

**Example:**
```http
GET /api/catalog/products/be6d475c-0bb9-4a5b-a1d8-eceb5e15ecf3/
```

**Response:** Same structure as list item above.

---

### Filter Products by Category
```http
GET /api/catalog/categories/<category-slug>/products/
```

**Example:**
```http
GET /api/catalog/categories/jellaba/products/
```

---

## 📂 Categories

### List All Categories
```http
GET /api/catalog/categories/
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "name": "Jellaba",
    "slug": "jellaba"
  },
  {
    "id": "uuid",
    "name": "Caftan",
    "slug": "caftan"
  }
]
```

---

### Get Single Category
```http
GET /api/catalog/categories/<slug>/
```

**Example:**
```http
GET /api/catalog/categories/jellaba/
```

---

## 🛒 Shopping Cart

### View Cart
```http
GET /api/cart/
```

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "id": "cart-uuid",
  "status": "CART",
  "items": [
    {
      "id": 1,
      "product_name": "Veste en Brochet",
      "quantity": 2,
      "price": "350.00",
      "extended_price": 700.0
    }
  ],
  "total_price": 700.0,
  "created_at": "2025-11-29T12:00:00Z"
}
```

---

### Add Item to Cart
```http
POST /api/cart/items/
```

**Headers:**
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "product_id": "be6d475c-0bb9-4a5b-a1d8-eceb5e15ecf3",
  "quantity": 2
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "product_name": "Veste en Brochet",
  "quantity": 2,
  "price": "350.00",
  "extended_price": 700.0
}
```

**Note:** If product already exists in cart, quantity will be added to existing quantity.

---

### Update Cart Item Quantity
```http
PATCH /api/cart/items/<item-id>/
```

**Headers:**
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "quantity": 5
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "product_name": "Veste en Brochet",
  "quantity": 5,
  "price": "350.00",
  "extended_price": 1750.0
}
```

---

### Remove Item from Cart
```http
DELETE /api/cart/items/<item-id>/
```

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (204 No Content)**

---

## 📦 Orders

### Checkout (Create Order)
```http
POST /api/cart/checkout/
```

**Headers:**
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

**Request Body (Minimal - Backward Compatible):**
```json
{
  "shipping_address": "123 Rue Mohammed V",
  "shipping_city": "Casablanca",
  "shipping_postal_code": "20000"
}
```

**Request Body (Full - Recommended):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+212612345678",
  "email": "john.doe@example.com",
  "shipping_address": "123 Rue Mohammed V",
  "shipping_address_line_2": "Apt 4B",
  "shipping_city": "Casablanca",
  "shipping_state": "Grand Casablanca",
  "shipping_postal_code": "20000",
  "shipping_country": "Morocco"
}
```

**Field Requirements:**
| Field | Required | Description |
|-------|----------|-------------|
| `first_name` | Optional | Customer first name |
| `last_name` | Optional | Customer last name |
| `phone_number` | Optional | Contact phone for delivery |
| `email` | Optional | Contact email |
| `shipping_address` | **Required** | Street address |
| `shipping_address_line_2` | Optional | Apartment, suite, etc. |
| `shipping_city` | **Required** | City name |
| `shipping_state` | Optional | State/province |
| `shipping_postal_code` | **Required** | Postal/ZIP code |
| `shipping_country` | Optional | Defaults to "Morocco" |

**Response (200 OK):**
```json
{
  "message": "Order placed. Proceed to payment.",
  "order_id": "order-uuid",
  "total": 700.0
}
```

**Status Change:** Cart status changes from `CART` → `PENDING`

---

### List Order History
```http
GET /api/cart/orders/
```

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
[
  {
    "id": "84d14525-5def-4935-9e2c-07eafc9980cc",
    "status": "PENDING",
    "items": [
      {
        "id": 5,
        "product_name": "Veste en Brochet avec Sfifa Merema",
        "quantity": 1,
        "price": "350.00",
        "extended_price": 350.0
      }
    ],
    "total_price": 350.0,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+212612345678",
    "email": "john.doe@example.com",
    "shipping_address": "123 Rue Mohammed V",
    "shipping_address_line_2": "Apt 4B",
    "shipping_city": "Casablanca",
    "shipping_state": "Grand Casablanca",
    "shipping_postal_code": "20000",
    "shipping_country": "Morocco",
    "payment_method": "",
    "paid_at": null,
    "created_at": "2025-11-29T06:09:14.646596Z",
    "updated_at": "2025-11-29T18:59:19.299600Z"
  }
]
```

**Notes:**
- Returns orders in reverse chronological order (newest first)
- Excludes active cart (status='CART')
- Only returns authenticated user's orders

---

### Get Order Details
```http
GET /api/cart/orders/<order-id>/
```

**Headers:**
```
Authorization: Bearer <access-token>
```

**Example:**
```http
GET /api/cart/orders/84d14525-5def-4935-9e2c-07eafc9980cc/
```

**Response (200 OK):**
Same structure as order list item above.

**Notes:**
- User can only view their own orders
- Returns 404 if order doesn't exist or belongs to another user

---

### Process Payment (Mock)
```http
POST /api/cart/orders/<order-id>/pay/
```

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "message": "Payment successful",
  "order_id": "order-uuid",
  "status": "PAID",
  "paid_at": "2025-11-29T13:00:00Z"
}
```

**Status Change:** Order status changes from `PENDING` → `PAID`

**Status Change:** Order status changes from `PENDING` → `PAID`

---

### Guest Checkout (New)
```http
POST /api/cart/guest/checkout/
```

**Headers:**
```
Content-Type: application/json
```
*(No Authorization header required)*

**Request Body:**
```json
{
  "email": "guest@example.com",
  "first_name": "Guest",
  "last_name": "User",
  "shipping_address": "123 Guest St",
  "shipping_city": "Casablanca",
  "shipping_postal_code": "20000"
}
```

**Requirements:**
- `email` is **REQUIRED** for guest checkout
- Other fields follow same rules as regular checkout

**Response (200 OK):**
```json
{
  "message": "Order placed. Check your email for confirmation.",
  "order_id": "order-uuid",
  "total": 700.0,
  "email": "guest@example.com"
}
```

---

### Guest Order Lookup
```http
POST /api/cart/guest/orders/lookup/
```

**Request Body:**
```json
{
  "email": "guest@example.com",
  "order_id": "order-uuid"
}
```

**Response (200 OK):**
Returns full order details (same as Get Order Details).

---

### Link Guest Orders
```http
POST /api/cart/link-guest-orders/
```

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "message": "Linked 2 previous orders to your account",
  "orders_linked": 2
}
```

---

## 👤 User Profile

### Get Profile
```http
GET /api/auth/me/
```

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

---

### Update Profile
```http
PATCH /api/auth/me/
```

**Headers:**
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response (200 OK):**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

---

## ⚠️ Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "field_name": ["Error message here"]
}
```

**Example:**
```json
{
  "email": ["This field is required."],
  "password": ["This password is too common."]
}
```

---

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

or

```json
{
  "detail": "Given token not valid for any token type"
}
```

---

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 🔧 Frontend Integration Examples

### JavaScript/Fetch

```javascript
// Login
async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/auth/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  return data;
}

// Get Products
async function getProducts() {
  const response = await fetch('http://localhost:8000/api/catalog/products/');
  return await response.json();
}

// Add to Cart (Works for both Guest & Auth)
async function addToCart(productId, quantity) {
  const token = localStorage.getItem('access_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  
  // Note: For guests, browser automatically handles cookies
  const response = await fetch('http://localhost:8000/api/cart/items/', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({ product_id: productId, quantity })
  });
  return await response.json();
}

// Guest Checkout
async function guestCheckout(email, addressData) {
  const response = await fetch('http://localhost:8000/api/cart/guest/checkout/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, ...addressData })
  });
  return await response.json();
}

// Link Guest Orders (Call after registration)
async function linkGuestOrders() {
  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/api/cart/link-guest-orders/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}
```

---

### Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login
export const login = (email, password) => 
  api.post('/auth/token/', { email, password });

// Get Products
export const getProducts = () => 
  api.get('/catalog/products/');

// Add to Cart
export const addToCart = (product_id, quantity) => 
  api.post('/cart/items/', { product_id, quantity });

// Guest Checkout
export const guestCheckout = (email, addressData) =>
  api.post('/cart/guest/checkout/', { email, ...addressData });

// Link Guest Orders
export const linkGuestOrders = () =>
  api.post('/cart/link-guest-orders/');
```

---

## 📝 Notes

1. **CORS:** The backend is configured to accept requests from:
   - `http://localhost:3000`
   - `http://localhost:5173`
   - `http://localhost:5174`

2. **Media Files:** Product images are served from `/media/` directory

3. **Token Refresh:** Implement automatic token refresh when access token expires (5 min)

4. **Price Locking:** Cart item prices are locked at time of addition and won't change even if product price updates

5. **UUIDs:** All IDs are UUIDs, not integers

---

## 🔗 Quick Links

- **Admin Panel:** http://localhost:8000/admin/
- **API Root:** http://localhost:8000/api/
- **Media Files:** http://localhost:8000/media/

---

## 📋 Changelog

### Version 1.2 (November 30, 2025)
**Guest Checkout (Hybrid)**
- ✅ Added guest checkout endpoint (`POST /api/cart/guest/checkout/`)
- ✅ Added guest order lookup (`POST /api/cart/guest/orders/lookup/`)
- ✅ Added account linking (`POST /api/cart/link-guest-orders/`)
- ✅ Updated cart endpoints to support session-based guest carts

### Version 1.1 (November 30, 2025)
**Enhanced Checkout & Order History**
- ✅ Added 6 optional fields to checkout (first_name, last_name, phone_number, email, shipping_address_line_2, shipping_state)
- ✅ Added order history endpoints (`GET /api/cart/orders/` and `GET /api/cart/orders/<id>/`)
- ✅ Backward compatible - old checkout format still works
- ✅ OrderDetailSerializer returns complete order information

### Version 1.0 (November 29, 2025)
**Initial Release**
- Authentication (JWT)
- Product catalog with images
- Shopping cart
- Basic checkout
- Mock payment

---

**Last Updated:** November 30, 2025 - Version 1.2
