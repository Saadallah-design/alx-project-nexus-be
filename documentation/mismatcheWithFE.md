API Integration Analysis & Mismatches
🔍 Summary
Analysis of the frontend implementation against the backend API documentation to identify mismatches and required changes.

⚠️ Critical Issues
1. API Base URL Mismatch
Current: .env file has VITE_API_URL="http://localhost:8000/api/catalog"
Expected: Should be http://localhost:8000/api

Problem: The base URL includes /catalog which will cause incorrect endpoint construction.

Fix Required:

# .env
VITE_API_URL="http://localhost:8000/api"
Impact:

Products API calls are currently going to /api/catalog/products/ (correct)
But if we add cart/auth endpoints, they would incorrectly go to /api/catalog/cart/ instead of /api/cart/
2. Products API Endpoint
Current: 
productsApi.ts
 uses /products/
Expected: /catalog/products/

Current Code:

fetchAll: () => apiClient.get<Product[]>('/products/'),
Should Be:

fetchAll: () => apiClient.get<Product[]>('/catalog/products/'),
Fix: Update 
src/api/productsApi.ts
 line 7

3. Product ID Type Mismatch
Current: 
fetchById
 uses id: number
Expected: id: string (UUIDs)

Current Code:

fetchById: (id: number) => apiClient.get<Product>(`/products/${id}/`),
Should Be:

fetchById: (id: string) => apiClient.get<Product>(`/catalog/products/${id}/`),
Fix: Update 
src/api/productsApi.ts
 line 21

4. Missing Cart API
Status: ❌ Not Implemented

Required Endpoints:

// src/api/cartApi.ts (needs to be created)
export const cartApi = {
  // GET /api/cart/
  getCart: () => apiClient.get('/cart/'),
  
  // POST /api/cart/items/
  addItem: (product_id: string, quantity: number) => 
    apiClient.post('/cart/items/', { product_id, quantity }),
  
  // PATCH /api/cart/items/<item-id>/
  updateItem: (itemId: number, quantity: number) => 
    apiClient.patch(`/cart/items/${itemId}/`, { quantity }),
  
  // DELETE /api/cart/items/<item-id>/
  removeItem: (itemId: number) => 
    apiClient.delete(`/cart/items/${itemId}/`),
};
5. Missing Authentication API
Status: ❌ Not Implemented

Required Endpoints:

// src/api/authApi.ts (needs to be created)
export const authApi = {
  // POST /api/auth/register/
  register: (data: RegisterData) => 
    apiClient.post('/auth/register/', data),
  
  // POST /api/auth/token/
  login: (email: string, password: string) => 
    apiClient.post('/auth/token/', { email, password }),
  
  // POST /api/auth/token/refresh/
  refreshToken: (refresh: string) => 
    apiClient.post('/auth/token/refresh/', { refresh }),
  
  // POST /api/auth/token/blacklist/
  logout: (refresh: string) => 
    apiClient.post('/auth/token/blacklist/', { refresh }),
  
  // GET /api/auth/me/
  getProfile: () => apiClient.get('/auth/me/'),
  
  // PATCH /api/auth/me/
  updateProfile: (data: Partial<UserProfile>) => 
    apiClient.patch('/auth/me/', data),
};
6. Missing Orders/Checkout API
Status: ❌ Not Implemented

Required Endpoints:

// src/api/ordersApi.ts (needs to be created or updated)
export const ordersApi = {
  // POST /api/cart/checkout/
  checkout: (data: CheckoutData) => 
    apiClient.post('/cart/checkout/', data),
  
  // POST /api/cart/orders/<order-id>/pay/
  processPayment: (orderId: string) => 
    apiClient.post(`/cart/orders/${orderId}/pay/`, {}),
};
Checkout Data Structure (from API docs):

interface CheckoutData {
  shipping_address: string;
  shipping_city: string;
  shipping_postal_code: string;
  shipping_country: string;
}
🔄 Type Mismatches
1. Checkout Address Structure
Current Frontend (
src/types/checkout.ts
):

export interface Address {
  first_name: string;
  last_name: string;
  phone_number: string;
  email: string;
  address_line_1: string;
  address_line_2: string | null;
  city: string;
  state_province: string;
  postal_code: string;
  country: string;
}
Backend API Expects (from docs):

{
  "shipping_address": "123 Rue Mohammed V",
  "shipping_city": "Casablanca",
  "shipping_postal_code": "20000",
  "shipping_country": "Morocco"
}
Issue: The frontend has a complex Address object, but the backend expects flat fields.

Recommendation: Either:

Update backend to accept nested address object, OR
Transform frontend Address to backend format before submission
2. Order Creation Payload
Current Frontend (
src/types/order.ts
):

export interface OrderCreationPayload {
  order_items: OrderItemPayload[];
  shipping_address: Address;
  shipping_rate_id: string;
  payment_method: 'COD' | 'Card';
  user_id?: string;
}
Backend API (from docs):

{
  "shipping_address": "string",
  "shipping_city": "string",
  "shipping_postal_code": "string",
  "shipping_country": "string"
}
Issue: Frontend expects to send order_items, shipping_rate_id, and payment_method, but backend docs don't show these fields.

Action Required: Verify actual backend implementation or update types to match.

✅ Correct Implementations
1. Product Type ✓
The 
Product
 interface matches the API response perfectly:

UUID 
id
 field
Nested category object
images array with 
ProductImage
 objects
Decimal prices as strings
All fields match API documentation
2. API Client Structure ✓
The apiClient in 
client.ts
 has correct structure for GET/POST operations.

Needs Addition:

PATCH method
DELETE method
PUT method (if needed)
🛠️ Required Fixes
Priority 1: Critical (Breaks Current Functionality)
Fix .env file:

VITE_API_URL="http://localhost:8000/api"
Fix productsApi.ts:

fetchAll: () => apiClient.get<Product[]>('/catalog/products/'),
fetchById: (id: string) => apiClient.get<Product>(`/catalog/products/${id}/`),
Priority 2: High (Needed for Checkout)
Add missing HTTP methods to apiClient:

patch: async <T>(endpoint: string, data: unknown): Promise<T> => { ... },
delete: async <T>(endpoint: string): Promise<T> => { ... },
Create cartApi.ts with all cart endpoints

Create authApi.ts with all auth endpoints

Update ordersApi.ts to match backend checkout endpoint

Priority 3: Medium (Type Safety)
Align checkout types with actual backend API

Add proper error handling for 401, 404, 500 responses

Implement token refresh logic (access token expires in 5 minutes)

📋 Implementation Checklist
 Update .env to use correct base URL
 Fix 
productsApi.ts
 endpoints
 Add PATCH/DELETE methods to apiClient
 Create cartApi.ts
 Create authApi.ts
 Update 
ordersApi.ts
 for checkout
 Verify checkout types match backend
 Add authentication interceptor
 Implement token refresh
 Add error handling for all API responses
 Test all endpoints with actual backend
🔗 Next Steps
Immediate: Fix the .env and 
productsApi.ts
 to ensure products load correctly
Short-term: Implement cart and auth APIs for full functionality
Long-term: Add comprehensive error handling and token management