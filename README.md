# PRICE_TRACKER
This is developed to get the prices of the various products across all the ecommerce websites .
# 🛒 E-Commerce Price Tracker API

A FastAPI-based e-commerce price tracking and product-data API that collects product information from **Amazon and Flipkart**, stores processed data in **Redis and PostgreSQL**, and exposes the data through authenticated REST APIs.

The project combines **web scraping, asynchronous APIs, Redis caching, JWT-based API keys, PostgreSQL, SQLAlchemy/SQLModel, and Redis Lua scripting** to create a backend system for e-commerce price tracking.

---

## 🚀 Features

* 🔐 User account creation
* 🔑 JWT-based API key generation
* 🛡️ API key authentication
* 🚦 Redis-based token bucket rate limiter
* ⚡ Redis caching for frequently requested data
* 🛍️ Amazon product scraping
* 🛒 Flipkart product scraping
* 📱 iPhone product tracking
* 📱 Samsung S-Series product tracking
* 💰 Product price extraction
* 🔄 Product + price dataset merging
* 📊 Amazon vs Flipkart price comparison
* 🔎 Dynamic product searching
* ❤️ Wishlist / cart functionality
* 🗄️ PostgreSQL database integration
* ⚡ Async database operations
* 🌐 Async HTTP client using HTTPX
* 📦 JSON-based intermediate data storage
* 📲 Telegram integration for product notifications
* 📖 Automatic FastAPI Swagger documentation

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │       Client         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │       REST API       │
                         └──────────┬───────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
        ┌──────────────┐     ┌──────────────┐    ┌───────────────┐
        │ PostgreSQL   │     │    Redis     │    │   Services    │
        │              │     │              │    │               │
        │ Users        │     │ Cache        │    │ Price Tracker │
        │ Wishlist     │     │ Rate Limit   │    │ Authentication│
        └──────────────┘     └──────┬───────┘    └───────┬───────┘
                                    │                     │
                                    └──────────┬──────────┘
                                               ▼
                                  ┌────────────────────────┐
                                  │   External Websites    │
                                  │                        │
                                  │ Amazon + Flipkart      │
                                  └────────────────────────┘
```

---

# 🧰 Tech Stack

| Technology           | Purpose                           |
| -------------------- | --------------------------------- |
| **Python**           | Core programming language         |
| **FastAPI**          | REST API framework                |
| **PostgreSQL**       | Persistent database               |
| **SQLAlchemy**       | Async database engine             |
| **SQLModel**         | Database models and queries       |
| **Redis**            | Caching and rate limiting         |
| **Lua**              | Atomic Redis rate limiter         |
| **JWT**              | API key generation and validation |
| **BeautifulSoup**    | HTML parsing                      |
| **Requests**         | Web scraping                      |
| **HTTPX**            | Async HTTP requests               |
| **Pandas**           | Data processing                   |
| **JSON**             | Intermediate data storage         |
| **Telegram Bot API** | Notifications                     |

---

# 📂 Project Structure

A recommended structure for the project is:

```text
ecommerce-price-tracker/
│
├── main.py
├── models.py
├── schemas.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── amazon/
│   └── flipkart/
│
├── services/
│   └── price_tracker.py
│
└── tests/
```

The current implementation primarily contains the application logic in the FastAPI application file, with database models and schemas separated into:

```text
models.py
schemas.py
```

---

# ⚙️ How the Application Works

The application follows this general flow:

```text
Application Startup
        │
        ▼
Initialize PostgreSQL
        │
        ▼
Initialize Redis
        │
        ▼
Load Redis Lua Rate Limiter
        │
        ▼
Initialize HTTPX
        │
        ▼
Create PRICE_TRACKER
        │
        ▼
Scrape Product Data
        │
        ├───────────────┐
        ▼               ▼
    Flipkart         Amazon
        │               │
        └───────┬───────┘
                ▼
        Extract Products
                │
                ▼
          Extract Prices
                │
                ▼
       Merge Product + Price
                │
                ▼
          Store in Redis
                │
                ▼
         Serve through API
```

---

# 🔐 Authentication

The API uses **JWT tokens as API keys**.

When a user creates an account, the application generates a signed JWT containing information about the user.

Example payload:

```json
{
    "user": {
        "email": "user@example.com",
        "age": 21,
        "name": "John"
    }
}
```

The token is signed using:

```text
HS256
```

The generated API key is stored with the user's account.

---

# 👤 User Registration

### Endpoint

```http
POST /new/user/signup/
```

The endpoint accepts user information and performs the following:

```text
Receive user information
        ↓
Check whether user already exists
        ↓
Create database record
        ↓
Generate JWT API key
        ↓
Store API key
        ↓
Return API key
```

Example response:

```json
{
    "message": "Account creation is succesfull",
    "API_KEY": "YOUR_GENERATED_API_KEY",
    "NAME": "John"
}
```

The API key can then be used to access protected endpoints.

---

# 🚦 Redis Rate Limiting

The project implements a **token bucket rate limiter using Redis and Lua**.

The limiter maintains:

```text
tokens
last_refill
```

for every API key.

Conceptually:

```text
                 Request
                    │
                    ▼
              Extract API Key
                    │
                    ▼
             Redis Token Bucket
                    │
          ┌─────────┴─────────┐
          │                   │
      Token available      No token
          │                   │
          ▼                   ▼
       Allow              Reject
          │                   │
          ▼                   ▼
    Consume token       HTTP 429
```

The current configuration uses:

```text
Capacity:     10 requests
Refill rate:  1 token/second
```

Therefore, the client can initially make up to 10 requests if the bucket is full, after which tokens are gradually regenerated.

The rate limiter is implemented using a Redis Lua script so the token calculation and update happen atomically inside Redis.

---

# ⚡ Why Redis?

Redis is used for two important purposes.

### 1. Product-data caching

Instead of scraping websites for every API request:

```text
Client
  ↓
FastAPI
  ↓
Redis
  ↓
Cached product data
```

This significantly reduces unnecessary external requests.

### 2. Rate limiting

Redis stores the token bucket associated with each API key:

```text
api_rate_limit:<API_KEY>
```

This allows the rate limiter to maintain request state across API calls.

---

# 🛍️ Product Data Pipeline

The application collects product information from Amazon and Flipkart.

For example:

```text
Flipkart HTML
      ↓
BeautifulSoup
      ↓
Product Names
      +
Product Prices
      ↓
Merge
      ↓
JSON
      ↓
Redis
      ↓
API
```

The same architecture is used for Amazon.

---

# 📱 iPhone Tracking

The project collects iPhone listings from both marketplaces.

### Flipkart

The scraper collects:

```text
Product Name
Price
```

The data is stored in Redis using keys such as:

```text
flipkart_iphone_product_listings
flipkart_iphone_price_listings
flipkart_iphone_merged_data
```

The merged structure looks conceptually like:

```json
[
    {
        "MODEL": "iPhone Model",
        "PRICE": "79999"
    }
]
```

---

# 📱 Samsung Tracking

The project also tracks Samsung S-Series products.

Data is collected from:

```text
Amazon
Flipkart
```

Redis stores the processed data using keys such as:

```text
flipkart_samsung_listings
flipkart_samsung_price_list
flipkart_merged_samsung_data

amazon_s_s_series_product_listings
amazon_samsung_s_series_price_listings
amazon_samsung_merged_data
```

---

# 🔄 Data Merging

The project combines product names and prices into a single dataset.

Conceptually:

```text
Products:

[
    "iPhone 15",
    "iPhone 16",
    "iPhone 16 Pro"
]

Prices:

[
    "69999",
    "79999",
    "109999"
]
```

becomes:

```json
[
    {
        "MODEL": "iPhone 15",
        "PRICE": "69999"
    },
    {
        "MODEL": "iPhone 16",
        "PRICE": "79999"
    },
    {
        "MODEL": "iPhone 16 Pro",
        "PRICE": "109999"
    }
]
```

The project currently uses Python's `zip()` to associate product names with prices.

---

# 📊 Price Comparison

The application can compare the processed Amazon and Flipkart datasets.

For example:

```json
[
    {
        "MODEL": "iPhone 16",
        "FLIPKART_PRICE": "79999",
        "AMAZON_PRICE": "80999"
    }
]
```

The comparison result is cached in Redis.

### iPhone comparison

```http
GET /compare/iphone/prices/
```

### Samsung comparison

```http
GET /compare/samsung/prices/
```

---

# 🌐 API Endpoints

## 👤 Account

### Create Account

```http
POST /new/user/signup/
```

Creates a new user and generates an API key.

---

# 🍎 Flipkart iPhone APIs

### Get iPhone Listings

```http
GET /get/flipkart/iphone/listings/
```

Returns the collected Flipkart iPhone product listings.

### Get iPhone Prices

```http
GET /iphone/prices/flipkart/
```

Returns Flipkart iPhone prices.

### Get Merged iPhone Data

```http
GET /iphone/merged/data
```

Returns product names together with their prices.

---

# 📱 Flipkart Samsung APIs

### Get Samsung Products

```http
GET /samsung/flipkart/products/
```

Returns Samsung products collected from Flipkart.

### Get Samsung Prices

```http
GET /flipkart/samsung/price/listings/
```

Returns Samsung prices from Flipkart.

### Get Merged Samsung Data

```http
GET /samsung/merged/detail
```

Returns merged Samsung product and price information.

---

# 🛒 Amazon iPhone APIs

### Get iPhone Listings

```http
GET /amazon/iphone/listings/
```

### Get iPhone Prices

```http
GET /amazon/iphone/price/listings/
```

### Get Merged iPhone Data

```http
GET /amazon/iphone/merged/
```

---

# 📱 Amazon Samsung APIs

### Get Samsung Products

```http
GET /amazon/samsung/product/listings/
```

### Get Samsung Prices

```http
GET /amazon/samsung/price/listings/
```

### Get Merged Samsung Data

```http
GET /amazon/samsung/merged/
```

---

# 📊 Price Comparison APIs

### Compare iPhone Prices

```http
GET /compare/iphone/prices/
```

### Compare Samsung Prices

```http
GET /compare/samsung/prices/
```

These endpoints return the comparison data stored in Redis.

---

# 🔎 Dynamic Product Search

The application also contains a dynamic product service.

The idea is:

```text
User Product Query
       ↓
Amazon Search
       ↓
HTML Response
       ↓
BeautifulSoup
       ↓
Extract Product Names
       +
Extract Prices
       ↓
Merge
       ↓
Return Data
```

The API endpoint is:

```http
GET /dynamic/products/
```

This allows the application to work with products beyond the predefined iPhone and Samsung datasets.

---

# ❤️ Wishlist / Cart System

The application also contains an `ADD_TO_CART` model and a corresponding API.

```http
POST /Add_to_cart/
```

The intended workflow is:

```text
User
 ↓
Verify Account
 ↓
Check Product
 ↓
Check Existing Wishlist Entry
 ↓
Add Product
 ↓
Store in PostgreSQL
```

The stored information includes fields such as:

```text
NAME
AGE
EMAIL_ID
TELEGRAM_ID
PRODUCT_NAME
```

This functionality forms the foundation for future price-monitoring and notification features.

---

# 📲 Telegram Notification System

The project contains a continuous-processing workflow intended to:

1. Read products saved by users.
2. Search for the requested product.
3. Retrieve current product information.
4. Merge product and price information.
5. Send the resulting data to the user's Telegram ID.

Conceptually:

```text
User Wishlist
      ↓
PostgreSQL
      ↓
Read Product
      ↓
Search Amazon
      ↓
Extract Current Price
      ↓
Generate Dataset
      ↓
Telegram Bot
      ↓
User
```

This can eventually be extended into a full **automated price-alert system**.

---

# 🧠 Service Architecture

The project separates application logic into two major classes.

## `PRICE_TRACKER`

Responsible mainly for:

```text
Web scraping
HTML parsing
Product extraction
Price extraction
Data merging
Price comparison
Dynamic product processing
```

Examples:

```python
getting_the_flipkart_iphone_metadata()
getting_the_flipkart_iphone_data_descriptions()
getting_the_flipkart_iphone_price_details()

getting_the_samsung_flipkart_data()
getting_the_samsung_price_list()

accessing_the_amazon_s_series_pr_descri()
getting_the_price_list_samsung()

compare_iphone_prices()
compare_samsung_prices()
```

---

## `PRICE_TRACKER_SERVICE`

Responsible mainly for application/business logic:

```text
User creation
User verification
API-key generation
API-key validation
Rate limiting
Dynamic product service
Wishlist management
```

This separation gives the project a service-oriented structure:

```text
API Routes
    ↓
PRICE_TRACKER_SERVICE
    ↓
PRICE_TRACKER
    ↓
Scraping / Redis / Database
```

---

# 🗄️ PostgreSQL Data

PostgreSQL is used for persistent information such as:

### Users

User information includes fields such as:

```text
NAME
AGE
EMAIL_ID
CONTACT_NO
API_KEY
```

### Wishlist / Cart

Product tracking information includes:

```text
NAME
AGE
EMAIL_ID
TELEGRAM_ID
PRODUCT_NAME
```

Unlike Redis, PostgreSQL provides persistent storage.

---

# 🔐 Request Authentication Flow

Protected endpoints follow this pattern:

```text
Client Request
      │
      ▼
Extract X-API-Key
      │
      ▼
Redis Rate Limiter
      │
      ├── Rejected → 429
      │
      ▼
Validate API Key
      │
      ├── Invalid → 401
      │
      ▼
Read Cached Data
      │
      ├── Missing → 203
      │
      ▼
Return Product Data
```

This means the API combines **authentication + rate limiting + caching** before returning data.

---

# 📦 Installation

## 1. Clone the repository

```bash
git clone https://github.com/your-username/ecommerce-price-tracker.git
```

```bash
cd ecommerce-price-tracker
```

---

## 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install fastapi uvicorn
pip install sqlalchemy sqlmodel asyncpg
pip install redis
pip install requests beautifulsoup4
pip install httpx
pip install pyjwt
pip install pandas
pip install fastapi-mail
pip install logzero
```

Or, if `requirements.txt` is available:

```bash
pip install -r requirements.txt
```

---

# 🐘 PostgreSQL Setup

Create a PostgreSQL database:

```text
ECOMMERCE
```

The application expects PostgreSQL to be available locally.

Default PostgreSQL port:

```text
5432
```

Make sure the PostgreSQL server is running before starting FastAPI.

---

# 🔴 Redis Setup

Redis must also be running locally.

Default configuration:

```text
Host: localhost
Port: 6379
```

You can verify Redis with:

```bash
redis-cli ping
```

Expected result:

```text
PONG
```

---

# ▶️ Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:ecommerce --reload
```

Replace `main` with the filename containing the `ecommerce` FastAPI object.

For example, if the file is:

```text
ecommerce.py
```

use:

```bash
uvicorn ecommerce:ecommerce --reload
```

---

# 📖 API Documentation

Once the server is running, FastAPI automatically provides Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Alternative ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

Swagger makes it possible to test the API directly from the browser.

---

# 🔑 Example API Request

A protected endpoint expects an API key.

Example:

```http
GET /get/flipkart/iphone/listings/
X-API-Key: YOUR_API_KEY
```

The server then:

```text
X-API-Key
     ↓
Redis Rate Limiter
     ↓
Database API-Key Verification
     ↓
Redis Product Cache
     ↓
JSON Response
```

---

# 📋 Example Response

A product-list endpoint can return data similar to:

```json
[
    "Apple iPhone 16",
    "Apple iPhone 16 Plus",
    "Apple iPhone 16 Pro",
    "Apple iPhone 16 Pro Max"
]
```

A merged endpoint can return:

```json
[
    {
        "MODEL": "Apple iPhone 16",
        "PRICE": "69999"
    },
    {
        "MODEL": "Apple iPhone 16 Pro",
        "PRICE": "109999"
    }
]
```

---

# ⏱️ Rate-Limit Response

When the Redis token bucket has no available tokens, the API returns:

```http
429 Too Many Requests
```

Example:

```json
{
    "detail": "API LIMIT EXCEEDED PLEASE TRY AFTER SOMETIME"
}
```

---

# 🔒 Security

The current project uses JWT-based API keys and Redis rate limiting.

For production deployment, the following should be moved out of source code:

```text
Database password
JWT secret
Telegram bot token
API credentials
Redis credentials
```

Recommended approach:

```text
Environment Variables
        ↓
Application
        ↓
Secrets
```

For example:

```env
DATABASE_URL=...
JWT_SECRET=...
REDIS_HOST=localhost
REDIS_PORT=6379
TELEGRAM_BOT_TOKEN=...
```

**Never commit real secrets to GitHub.**

If credentials have already been committed to a public repository, they should be rotated.

---

# ⚠️ Current Project Limitations

This project is currently a **development/beta implementation**.

The following areas should be improved before production deployment:

* Move secrets into environment variables.
* Add proper request/response schemas for all endpoints.
* Improve exception handling.
* Add structured logging.
* Add automated tests.
* Separate scraping logic into dedicated modules.
* Add database migrations using Alembic.
* Avoid performing large scraping operations directly during application startup.
* Add retry and timeout handling for external websites.
* Improve product-to-price matching instead of relying only on list ordering.
* Validate scraped HTML because marketplace HTML structures can change.
* Improve async/synchronous separation.
* Add authentication middleware/dependencies to reduce repeated endpoint code.
* Add pagination for large datasets.
* Add monitoring and health-check endpoints.
* Add Docker support for deployment.
* Add CI/CD testing.

---

# 🧪 Future Improvements

Possible future versions could include:

### Price Alerts

```text
User selects product
        ↓
User specifies target price
        ↓
Background worker checks price
        ↓
Price reaches target
        ↓
Telegram notification
```

### Historical Price Tracking

Instead of storing only the current price:

```text
Product
   ↓
Price history
   ↓
Database
   ↓
Historical chart
```

Example:

```text
Date          Price
--------------------
01-09-2026    ₹79,999
05-09-2026    ₹77,999
10-09-2026    ₹74,999
15-09-2026    ₹72,999
```

### Background Workers

Scraping could eventually be moved into:

```text
FastAPI
   │
   ├── API requests
   │
   └── Background workers
          │
          ├── Amazon scraper
          ├── Flipkart scraper
          └── Price alerts
```

### Docker Deployment

The complete system could be containerized:

```text
Docker Compose
│
├── FastAPI
├── PostgreSQL
└── Redis
```

---

# 📌 Project Status

```text
Status: Beta / Development
```

The project currently demonstrates a complete backend workflow involving:

```text
Authentication
      +
Rate Limiting
      +
Caching
      +
Database
      +
Web Scraping
      +
Data Processing
      +
REST APIs
```

---

# 🎯 Learning Objectives

This project was built to explore practical backend engineering concepts including:

* REST API development
* FastAPI
* Dependency injection
* Async programming
* PostgreSQL
* SQLAlchemy
* SQLModel
* Redis
* Redis Lua scripting
* Token bucket algorithms
* JWT authentication
* API-key authentication
* Web scraping
* HTML parsing
* HTTP clients
* Data serialization
* Service-layer architecture
* Caching
* Database persistence
* External API integration

---



---

# ⭐ Future Vision

The long-term goal of this project is to evolve it from a basic price-tracking API into a more complete **e-commerce intelligence platform** capable of:

```text
Product Discovery
       ↓
Price Tracking
       ↓
Price Comparison
       ↓
Historical Analysis
       ↓
Target Price Monitoring
       ↓
Automated Notifications
```

The project is primarily focused on learning and implementing **real-world backend engineering concepts** using Python.
