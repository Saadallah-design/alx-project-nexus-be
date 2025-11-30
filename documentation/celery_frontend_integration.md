# Celery Integration - Frontend Documentation

## Overview
Our backend uses **Celery** with **Redis** for asynchronous task processing. This means certain operations happen in the background without blocking API responses, providing a better user experience.

---

## 📋 Current Celery Tasks

### 1. **Order Confirmation Emails** 
- **Task Name**: `send_order_confirmation_email`
- **Type**: Fire-and-forget (no progress tracking needed)
- **When Triggered**: Automatically after successful checkout
- **Processing Time**: ~0.03 seconds (very fast)

**What happens:**
1. User completes checkout
2. API responds immediately with order details
3. Email is sent in the background (user doesn't wait)

---

## 🔌 API Endpoints Using Celery

### 1. **Authenticated User Checkout**
```http
POST /api/orders/checkout/
```

**Headers:**
```json
{
  "Authorization": "Bearer <access_token>",
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "shipping_address": "123 Main Street",
  "shipping_address_line_2": "Apt 4B",
  "shipping_city": "New York",
  "shipping_state": "NY",
  "shipping_postal_code": "10001",
  "shipping_country": "USA"
}
```

**Response (200 OK):**
```json
{
  "message": "Order placed. Proceed to payment.",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "total": 299.99
}
```

**What happens behind the scenes:**
- Order status changed from `CART` → `PENDING`
- Email task queued (if email provided)
- Response returned immediately
- Email sent asynchronously

---

### 2. **Guest Checkout**
```http
POST /api/orders/guest-checkout/
```

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone_number": "+1234567890",
  "shipping_address": "456 Oak Avenue",
  "shipping_city": "Los Angeles",
  "shipping_state": "CA",
  "shipping_postal_code": "90001",
  "shipping_country": "USA"
}
```

**Response (200 OK):**
```json
{
  "message": "Order placed successfully.",
  "order_id": "660e8400-e29b-41d4-a716-446655440001",
  "total": 149.99,
  "email": "jane@example.com"
}
```

**What happens behind the scenes:**
- Order status changed from `CART` → `PENDING`
- Email task queued (if email provided)
- Response returned immediately
- Email sent asynchronously

---

## 🎯 Implementation Type: **Fire-and-Forget**

**What this means for frontend:**
- ✅ **No progress tracking needed** - emails send instantly (~30ms)
- ✅ **No polling required** - email happens automatically
- ✅ **No additional API calls** - one-time checkout is enough
- ✅ **User gets instant response** - no waiting for email to send

**User Experience Flow:**
```
1. User clicks "Place Order" button
2. Frontend calls checkout API
3. API responds in ~100-200ms (fast!)
4. Frontend shows success message: "Order placed! Check your email for confirmation."
5. Email arrives in user's inbox within seconds (background)
```

---

## 💡 Frontend Implementation Guide

### React Example (Checkout Flow)

```typescript
// CheckoutPage.tsx

const handleCheckout = async (formData: CheckoutFormData) => {
  try {
    setLoading(true);
    
    const response = await fetch('/api/orders/guest-checkout/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });
    
    if (!response.ok) {
      throw new Error('Checkout failed');
    }
    
    const data = await response.json();
    
    // ✅ Show success message immediately
    toast.success(
      `Order placed successfully! 
       Order ID: ${data.order_id}
       Confirmation email sent to ${data.email || formData.email}`
    );
    
    // Navigate to order confirmation page
    navigate(`/order-confirmation/${data.order_id}`, {
      state: { orderData: data }
    });
    
  } catch (error) {
    toast.error('Failed to place order. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

### Success Message Examples

**Option 1: Simple**
```
✅ Order placed successfully!
Check your email for confirmation.
```

**Option 2: Detailed**
```
✅ Order #12345 confirmed!
Total: $299.99
📧 Confirmation email sent to john@example.com
```

**Option 3: With Next Steps (Recommended)**
```
✅ Thank you for your order!

Order ID: 550e8400-e29b-41d4-a716-446655440000
Total: $299.99

📧 We've sent a confirmation email to john@example.com
💡 Tip: Check your spam/promotions folder if you don't see it within a few minutes.
Next: Proceed to payment
```

**Option 4: With Email Delivery Guidance**
```
✅ Order confirmed!

📧 Confirmation email sent to john@example.com

Haven't received it?
• Check your spam or promotions folder
• Email may take 1-2 minutes to arrive
• Contact support if needed
```

---

## ⚠️ Important Notes for Frontend

### 1. **Email Delivery is Asynchronous**
- Don't show "Sending email..." loading state
- Don't wait for email confirmation
- Just show order success message

### 2. **Email Field is Optional for Authenticated Users**
- If user is logged in, their account email is used
- Guest checkout requires email field
- Backend handles email selection automatically

### 3. **Error Handling**
```typescript
// Email sending errors are handled silently by backend
// Frontend doesn't need to worry about email failures
// User still gets order confirmation on screen

if (response.ok) {
  // Order was placed successfully
  // Email is being sent (or already sent)
  showSuccessMessage();
}
```

### 4. **No Task IDs Returned**
```json
// Response does NOT include task_id
// This is intentional - frontend doesn't need it
{
  "message": "Order placed successfully.",
  "order_id": "660e8400-e29b-41d4-a716-446655440001",
  "total": 149.99
  // ❌ No task_id - you don't need to track email status
}
```

---

## 🔮 Future Celery Tasks (Planned)

### 2. **Product Image Processing** (Not yet implemented)
- Resize product images
- Generate thumbnails
- Optimize for web

### 3. **Inventory Cleanup** (Not yet implemented)
- Clean up expired carts
- Archive old orders
- Send low stock alerts

### 4. **Order Status Notifications** (Not yet implemented)
- Send shipping updates
- Delivery confirmations
- Order status changes

---

## 🐛 Debugging for Frontend Developers

### Common Questions

**Q: How do I know if the email was sent?**
- A: If checkout succeeds (200 OK), email is queued. User will receive it within seconds to a few minutes.

**Q: What if email fails to send?**
- A: Backend logs the error. User still has order confirmation. Support team can resend manually.

**Q: Should I show "Email sent successfully"?**
- A: No. Show "Order placed successfully! Check your email." Email happens automatically.

**Q: Can I get email status?**
- A: Not currently implemented. Email is fire-and-forget (instant delivery).

**Q: What about email for authenticated users?**
- A: Backend uses their account email automatically if `email` field is empty in checkout.

**Q: User says they didn't receive the email. What should I tell them?**
- A: Suggest checking:
  1. **Spam/Junk folder** - Most common reason
  2. **Promotions tab** (Gmail) - Automated emails often go here
  3. **All Mail folder** - Email might be filtered
  4. **Wait 1-2 minutes** - Delivery can be delayed
  5. **Verify email address** - Typos happen
  6. Contact support if still missing after 5 minutes

---

## 📊 Response Time Comparison

### Before Celery (Blocking):
```
User clicks checkout
  ↓
Backend processes order (50ms)
  ↓
Backend sends email (2000ms) ⏱️ SLOW
  ↓
Response returned (2050ms total)
```

### After Celery (Async):
```
User clicks checkout
  ↓
Backend processes order (50ms)
  ↓
Email task queued (1ms)
  ↓
Response returned (51ms total) ⚡ FAST
  ↓
Email sent in background (30ms)
```

**Result:** ~40x faster response time! 🚀

---

## 🎨 UI/UX Recommendations

### Loading States
```typescript
// ✅ Good: Show generic loading
<Button loading={isCheckingOut}>
  Place Order
</Button>

// ❌ Bad: Don't show email-specific loading
<Button loading={isCheckingOut}>
  Placing order and sending email...
</Button>
```

### Success Messages
```typescript
// ✅ Good: Mention email will be sent
"Order confirmed! Check your email for details."

// ❌ Bad: Don't wait for email
"Order confirmed! Email sent successfully!"
// (You don't know if it's sent yet - it's async!)
```

### Order Confirmation Page
```tsx
// ✅ Show this immediately after checkout
<OrderConfirmation>
  <h1>Order Confirmed! 🎉</h1>
  <p>Order ID: {orderId}</p>
  <p>Total: ${total}</p>
  <p>📧 A confirmation email has been sent to {email}</p>
  <Button>Continue Shopping</Button>
</OrderConfirmation>
```

---

## 🛠️ Development & Testing

### Local Testing
1. Backend runs on `http://localhost:8000`
2. Celery worker must be running (handled by backend team)
3. Emails print to backend console in development
4. Production uses real SMTP (configured by backend)

### Testing Checkout Flow
```bash
# Test authenticated checkout
curl -X POST http://localhost:8000/api/orders/checkout/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "shipping_address": "123 Test St",
    "shipping_city": "Test City",
    "shipping_state": "TS",
    "shipping_postal_code": "12345",
    "shipping_country": "USA"
  }'

# Test guest checkout
curl -X POST http://localhost:8000/api/orders/guest-checkout/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "guest@example.com",
    "first_name": "Guest",
    "last_name": "User",
    "shipping_address": "456 Guest Ave",
    "shipping_city": "Guest City",
    "shipping_state": "GS",
    "shipping_postal_code": "54321",
    "shipping_country": "USA"
  }'
```

---

## 📞 Need Help?

Contact backend team if:
- Email functionality not working
- Need additional Celery tasks implemented
- Want progress tracking for long-running tasks
- Need real-time task status updates

---

## Summary for Frontend Team

✅ **What you need to know:**
1. Checkout APIs return immediately (fast!)
2. Emails are sent automatically in background
3. No progress tracking needed
4. No additional API calls required
5. Just show success message and assume email will arrive

✅ **What you DON'T need to worry about:**
1. Email delivery status
2. Task IDs or polling
3. Retry logic
4. Email failures (backend handles it)

✅ **Implementation is simple:**
```typescript
// That's it! Just call the API and show success
const response = await checkout(formData);
if (response.ok) {
  showSuccess("Order placed! Check your email.");
}
```

**Keep it simple. Celery makes things faster, not more complex!** 🚀
