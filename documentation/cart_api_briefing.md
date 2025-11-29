# 🛒 Cart & Orders API Briefing

This document details the newly implemented Shopping Cart API.

## 📍 Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| **GET** | `/api/cart/` | View current user's active cart | ✅ Yes |
| **GET** | `/api/cart/items/` | List items in the cart | ✅ Yes |
| **POST** | `/api/cart/items/` | Add item to cart | ✅ Yes |

---

## 🚀 How to Use

### **1. View Your Cart**
**Endpoint:** `GET /api/cart/`
**Headers:** `Authorization: Bearer <your_token>`

**Response:**
```json
{
    "id": "a1b2c3d4-...",
    "status": "CART",
    "items": [
        {
            "id": 1,
            "product_name": "Smartphone X",
            "quantity": 2,
            "price": "999.00",
            "extended_price": "1998.00"
        }
    ],
    "total_price": 1998.00,
    "created_at": "2023-11-28T12:00:00Z"
}
```

---

### **2. Add Item to Cart**
**Endpoint:** `POST /api/cart/items/`
**Headers:** `Authorization: Bearer <your_token>`

**Body (JSON):**
```json
{
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "quantity": 1
}
```

**Response:**
```json
{
    "id": 1,
    "product_id": "550e8400-...",
    "product_name": "Smartphone X",
    "quantity": 1,
    "price": "999.00",
    "extended_price": "999.00"
}
```

---

### **3. Update Item Quantity**
*Currently, you can add the same product again to increase quantity.*
*To implement specific update/delete logic (e.g., remove item), we can add `RetrieveUpdateDestroyAPIView` for `OrderItem` later.*

---

## 🧪 Testing with Postman

1.  **Login** to get your JWT token.
2.  **Get a Product ID** from `/api/catalog/products/`.
3.  **POST** to `/api/cart/items/` with the `product_id`.
4.  **GET** `/api/cart/` to see your updated cart and total price.

## 🔒 Security Features
*   **User Isolation:** Users can only access their own cart.
*   **Price Locking:** The price is saved when the item is added. Future product price changes won't affect existing cart items.
*   **Availability Check:** You cannot add unavailable products to the cart.
