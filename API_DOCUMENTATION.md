# API Documentation - Oraagh Premium Woolen Products

This document provides comprehensive API documentation for the Oraagh premium woolen products e-commerce platform.

## 🔗 Base URL
```
Development: http://127.0.0.1:8000
Production: https://oraagh.com
```

## 🔐 Authentication

### Session Authentication
The platform uses Django's built-in session authentication. Users must be logged in to access protected endpoints.

### CSRF Protection
All POST, PUT, DELETE requests require CSRF token in headers:
```javascript
headers: {
    'X-CSRFToken': getCookie('csrftoken')
}
```

## 📦 Products API

### List Products
```http
GET /products/
```

**Parameters:**
- `category` (optional): Filter by category ID
- `search` (optional): Search in product name/description
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `sort` (optional): Sort by `name`, `price`, `created_at`
- `page` (optional): Page number for pagination

**Response:**
```json
{
    "count": 25,
    "next": "/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Antique Mining Lamp",
            "slug": "antique-mining-lamp",
            "price": "150.00",
            "tax_percentage": "10.00",
            "price_with_tax": "165.00",
            "stock_quantity": 5,
            "category": {
                "id": 1,
                "name": "Scarves & Wraps"
            },
            "brand": "Oraagh Collection",
            "condition": "excellent",
            "is_featured": true,
            "main_image": "/media/products/lamp_main.jpg",
            "created_at": "2025-08-31T10:30:00Z"
        }
    ]
}
```

### Get Product Details
```http
GET /products/{slug}/
```

**Response:**
```json
{
    "id": 1,
    "name": "Antique Mining Lamp",
    "slug": "antique-mining-lamp",
    "description": "Authentic 1920s mining lamp...",
    "price": "150.00",
    "tax_percentage": "10.00",
    "price_with_tax": "165.00",
    "stock_quantity": 5,
    "weight": "2.50",
    "origin": "Colorado, USA",
    "condition": "excellent",
    "product_type": "antique",
    "category": {
        "id": 1,
        "name": "Lighting Equipment",
        "slug": "lighting-equipment"
    },
    "media": [
        {
            "id": 1,
            "image": "/media/products/lamp_main.jpg",
            "alt_text": "Main view of antique mining lamp",
            "is_main": true
        }
    ],
    "reviews": [
        {
            "id": 1,
            "user": "john_doe",
            "rating": 5,
            "comment": "Excellent condition and fast shipping!",
            "status": "approved",
            "created_at": "2025-08-30T14:20:00Z"
        }
    ],
    "average_rating": 4.8,
    "review_count": 12
}
```

### Submit Product Review
```http
POST /products/{slug}/review/
```

**Request Body:**
```json
{
    "rating": 5,
    "comment": "Great product, exactly as described!"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Review submitted successfully. It will be visible after admin approval.",
    "review_id": 15
}
```

### Submit Deal Request
```http
POST /products/{slug}/deal-request/
```

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "message": "Interested in bulk purchase of 10 units. Can you provide a discount?",
    "quantity": 10
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Deal request submitted successfully. We'll contact you within 24 hours.",
    "request_id": 8
}
```

## 🛒 Cart & Orders API

### Get Cart
```http
GET /orders/cart/
```

**Response:**
```json
{
    "id": 1,
    "items": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "name": "Antique Mining Lamp",
                "price": "150.00",
                "main_image": "/media/products/lamp_main.jpg"
            },
            "quantity": 2,
            "unit_price": "150.00",
            "total_price": "300.00"
        }
    ],
    "subtotal": "300.00",
    "tax_amount": "30.00",
    "total": "330.00",
    "item_count": 2
}
```

### Add to Cart
```http
POST /orders/add-to-cart/
```

**Request Body:**
```json
{
    "product_id": 1,
    "quantity": 2
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Product added to cart",
    "cart_item_count": 3,
    "cart_total": "495.00"
}
```

### Update Cart Item
```http
POST /orders/update-cart-item/
```

**Request Body:**
```json
{
    "item_id": 1,
    "quantity": 3
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Cart updated",
    "item_total": "450.00",
    "cart_total": "495.00"
}
```

### Remove from Cart
```http
POST /orders/remove-from-cart/
```

**Request Body:**
```json
{
    "item_id": 1
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Item removed from cart",
    "cart_total": "165.00"
}
```

### Checkout
```http
POST /orders/checkout/
```

**Request Body:**
```json
{
    "shipping_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main St",
        "city": "Denver",
        "state": "CO",
        "postal_code": "80202",
        "country": "USA"
    },
    "billing_address": {
        "same_as_shipping": true
    },
    "delivery_option": "standard",
    "payment_method": "card",
    "notes": "Please handle with care"
}
```

**Response:**
```json
{
    "status": "success",
    "order_id": "ORD-2025-001234",
    "total": "330.00",
    "message": "Order placed successfully",
    "redirect_url": "/orders/confirmation/ORD-2025-001234/"
}
```

## 👤 User Account API

### User Registration
```http
POST /accounts/signup/
```

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password1": "SecurePassword123!",
    "password2": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Account created successfully. Please check your email for verification code.",
    "user_id": 15
}
```

### Email Verification
```http
POST /accounts/verify-email/
```

**Request Body:**
```json
{
    "verification_code": "123456"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Email verified successfully. You can now log in."
}
```

### User Login
```http
POST /accounts/login/
```

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "SecurePassword123!",
    "remember_me": true
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Login successful",
    "redirect_url": "/",
    "user": {
        "id": 15,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

### Password Reset Request
```http
POST /accounts/password-reset/
```

**Request Body:**
```json
{
    "email": "john@example.com"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Password reset code sent to your email."
}
```

### Password Reset Confirm
```http
POST /accounts/password-reset-confirm/
```

**Request Body:**
```json
{
    "email": "john@example.com",
    "reset_code": "123456",
    "new_password": "NewSecurePassword123!"
}
```

## 📧 Newsletter API

### Subscribe to Newsletter
```http
POST /newsletter/subscribe/
```

**Request Body:**
```json
{
    "email": "john@example.com"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Successfully subscribed to newsletter!"
}
```

### Unsubscribe from Newsletter
```http
POST /newsletter/unsubscribe/
```

**Request Body:**
```json
{
    "email": "john@example.com"
}
```

## 📝 Contact API

### Submit Contact Form
```http
POST /contact/
```

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Product Inquiry",
    "message": "I'm interested in your antique mining equipment collection..."
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Thank you for your message. We'll get back to you within 24 hours."
}
```

## 📰 Blog API

### List Blog Posts
```http
GET /blog/
```

**Parameters:**
- `category` (optional): Filter by category slug
- `tag` (optional): Filter by tag slug
- `page` (optional): Page number

**Response:**
```json
{
    "count": 15,
    "next": "/blog/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "The History of Mining Equipment",
            "slug": "history-of-mining-equipment",
            "excerpt": "Explore the evolution of mining tools...",
            "featured_image": "/media/blog/mining_history.jpg",
            "author": "Admin",
            "published_at": "2025-08-30T10:00:00Z",
            "view_count": 245,
            "categories": ["History", "Equipment"],
            "tags": ["mining", "antiques", "history"]
        }
    ]
}
```

### Get Blog Post
```http
GET /blog/{slug}/
```

**Response:**
```json
{
    "id": 1,
    "title": "The History of Mining Equipment",
    "slug": "history-of-mining-equipment",
    "content": "Full blog post content...",
    "excerpt": "Explore the evolution of mining tools...",
    "featured_image": "/media/blog/mining_history.jpg",
    "author": "Admin",
    "published_at": "2025-08-30T10:00:00Z",
    "view_count": 246,
    "categories": [
        {
            "id": 1,
            "name": "History",
            "slug": "history"
        }
    ],
    "tags": [
        {
            "id": 1,
            "name": "mining",
            "slug": "mining"
        }
    ],
    "related_posts": [
        {
            "id": 2,
            "title": "Collecting Antique Tools",
            "slug": "collecting-antique-tools"
        }
    ]
}
```


## 🛡️ Admin Dashboard API

### Dashboard Statistics
```http
GET /admin-dashboard/api/stats/
```

**Authentication Required:** Admin user

**Response:**
```json
{
    "total_products": 150,
    "total_orders": 89,
    "new_deals": 12,
    "total_customers": 245,
    "total_blog_posts": 25,
    "monthly_revenue": "15420.50",
    "pending_reviews": 8,
    "low_stock_products": 5
}
```

### Recent Orders
```http
GET /admin-dashboard/api/recent-orders/
```

**Parameters:**
- `limit` (optional): Number of orders to return (default: 10)

**Response:**
```json
{
    "orders": [
        {
            "id": "ORD-2025-001234",
            "customer": "John Doe",
            "total": "330.00",
            "status": "processing",
            "created_at": "2025-08-31T15:30:00Z",
            "item_count": 2
        }
    ]
}
```

### Update Order Status
```http
POST /admin-dashboard/orders/{order_id}/update-status/
```

**Request Body:**
```json
{
    "status": "shipped",
    "tracking_number": "1Z999AA1234567890",
    "notes": "Shipped via UPS"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Order status updated successfully",
    "order": {
        "id": "ORD-2025-001234",
        "status": "shipped",
        "tracking_number": "1Z999AA1234567890"
    }
}
```

## 📊 Analytics API

### Product Analytics
```http
GET /admin-dashboard/api/product-analytics/
```

**Parameters:**
- `period` (optional): `week`, `month`, `year` (default: month)

**Response:**
```json
{
    "top_products": [
        {
            "product_id": 1,
            "name": "Cashmere Wool Scarf",
            "views": 1250,
            "orders": 45,
            "revenue": "6750.00"
        }
    ],
    "category_performance": [
        {
            "category": "Scarves & Wraps",
            "product_count": 25,
            "total_revenue": "12500.00"
        }
    ]
}
```

### Order Analytics
```http
GET /admin-dashboard/api/order-analytics/
```

**Response:**
```json
{
    "total_orders": 89,
    "total_revenue": "15420.50",
    "average_order_value": "173.26",
    "orders_by_status": {
        "pending": 5,
        "processing": 12,
        "shipped": 65,
        "delivered": 7
    },
    "monthly_trend": [
        {
            "month": "2025-08",
            "orders": 25,
            "revenue": "4320.50"
        }
    ]
}
```

## 🔔 Notification API

### Get User Notifications
```http
GET /accounts/notifications/
```

**Response:**
```json
{
    "notifications": [
        {
            "id": 1,
            "type": "order_update",
            "title": "Order Shipped",
            "message": "Your order ORD-2025-001234 has been shipped",
            "read": false,
            "created_at": "2025-08-31T16:00:00Z"
        }
    ],
    "unread_count": 3
}
```

### Mark Notification as Read
```http
POST /accounts/notifications/{notification_id}/mark-read/
```

**Response:**
```json
{
    "status": "success",
    "message": "Notification marked as read"
}
```

## 🔍 Search API

### Global Search
```http
GET /search/
```

**Parameters:**
- `q`: Search query
- `type` (optional): `products`, `blog`, `all` (default: all)

**Response:**
```json
{
    "query": "mining lamp",
    "results": {
        "products": [
            {
                "id": 1,
                "name": "Antique Mining Lamp",
                "price": "150.00",
                "main_image": "/media/products/lamp_main.jpg",
                "relevance_score": 0.95
            }
        ],
        "blog_posts": [
            {
                "id": 1,
                "title": "The History of Mining Equipment",
                "excerpt": "Explore the evolution...",
                "relevance_score": 0.78
            }
        ]
    },
    "total_results": 8
}
```

## ⚠️ Error Responses

### Standard Error Format
```json
{
    "status": "error",
    "message": "Detailed error message",
    "code": "ERROR_CODE",
    "details": {
        "field_name": ["Field-specific error message"]
    }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Form validation failed
- `AUTHENTICATION_REQUIRED`: User not authenticated
- `PERMISSION_DENIED`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMITED`: Too many requests
- `SERVER_ERROR`: Internal server error

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

## 📈 Rate Limiting

### Default Limits
- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour
- **Admin users**: 5000 requests/hour

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1693497600
```

## 🔧 Development Tools

### API Testing with cURL

#### Get Products
```bash
curl -X GET "http://127.0.0.1:8000/products/" \
     -H "Accept: application/json"
```

#### Add to Cart
```bash
curl -X POST "http://127.0.0.1:8000/orders/add-to-cart/" \
     -H "Content-Type: application/json" \
     -H "X-CSRFToken: your-csrf-token" \
     -d '{"product_id": 1, "quantity": 2}'
```

### API Testing with Python
```python
import requests

# Get products
response = requests.get('http://127.0.0.1:8000/products/')
products = response.json()

# Login and get session
session = requests.Session()
login_data = {
    'username': 'testuser',
    'password': 'testpass'
}
session.post('http://127.0.0.1:8000/accounts/login/', data=login_data)

# Add to cart with session
cart_data = {'product_id': 1, 'quantity': 2}
response = session.post('http://127.0.0.1:8000/orders/add-to-cart/', json=cart_data)
```

## 📱 Mobile API Considerations

### Mobile-Specific Endpoints
- Optimized payload sizes
- Compressed image responses
- Reduced data transfer
- Offline capability support

### Response Optimization
```json
{
    "products": [
        {
            "id": 1,
            "name": "Antique Mining Lamp",
            "price": "150.00",
            "thumbnail": "/media/products/thumbs/lamp_thumb.jpg",
            "stock_status": "in_stock"
        }
    ]
}
```

## 🔒 Security Considerations

### API Security Best Practices
- Always validate input data
- Use HTTPS in production
- Implement rate limiting
- Log API access and errors
- Validate file uploads
- Sanitize user input
- Use parameterized queries

### Authentication Flow
1. User submits credentials
2. Server validates credentials
3. Session created and stored
4. CSRF token generated
5. Subsequent requests include session + CSRF

---

**For additional API support, contact the development team or refer to the Django admin interface for testing endpoints.**
