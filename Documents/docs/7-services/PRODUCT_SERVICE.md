# Product Service - Complete Documentation

**FreshHarvest Market - Organic Product Catalog & Inventory Management**

---

## Table of Contents

1. [Service Overview](#1-service-overview)
2. [Database Schema](#2-database-schema)
3. [Entity Relationships](#3-entity-relationships)
4. [Tables Deep Dive](#4-tables-deep-dive)
5. [Architecture & Layers](#5-architecture--layers)
6. [API Endpoints](#6-api-endpoints)
7. [Business Logic](#7-business-logic)
8. [Configuration](#8-configuration)
9. [Code Structure](#9-code-structure)

---

## 1. Service Overview

### Purpose

The **Product Service** is the central catalog management system for FreshHarvest Market, specifically designed for an organic food marketplace. It handles:

- **Product Catalog** - Store and manage all organic product information
- **Inventory Management** - Track stock levels and availability
- **Stock Reservation** - Reserve inventory during checkout
- **Category Taxonomy** - Organize products hierarchically (Fruits, Vegetables, etc.)
- **Organic Tracking** - Track certification, origin, farm source, and freshness
- **Product Discovery** - Tags and search optimization

### Key Design Decisions

The schema is **simplified and domain-specific** for an organic food marketplace:

| Decision | Rationale |
|----------|-----------|
| **Inline organic fields** | `IsOrganic`, `Origin`, `FarmName`, `HarvestDate`, `BestBefore` are core to every organic product |
| **Inline certification** | Organic certification is product-specific; a separate table adds unnecessary joins |
| **Inline SEO** | Simple `SeoTitle`/`SeoDescription` fields suffice; no need for complex JSON |
| **No EAV pattern** | Removed `ProductAttributes` table - organic food has consistent attributes |
| **JSON for nutrition** | `NutritionJson` allows flexible nutrition data without schema changes |

### Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | .NET 10 |
| ORM | Entity Framework Core |
| Database | SQL Server (LocalDB) |
| Pattern | Repository + Service Layer |
| API | RESTful with Swagger |

### Service Info

| Property | Value |
|----------|-------|
| Port | `5002` |
| Database | `EP_Local_ProductDb` (Local) / `EP_Staging_ProductDb` (Staging) |
| Health Check | `GET /api/health` |
| Swagger | `http://localhost:5002/swagger` |

---

## 2. Database Schema

### Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│               FRESHHARVEST MARKET - PRODUCT SERVICE DATABASE                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────┐                                                           │
│  │    Categories    │                                                           │
│  ├──────────────────┤                                                           │
│  │ Id (PK)          │◄───────────┐                                              │
│  │ Name             │            │                                              │
│  │ Slug (Unique)    │            │                                              │
│  │ Description      │            │                                              │
│  │ ParentId (FK)────┼──┐         │                                              │
│  │ IsActive         │  │         │                                              │
│  │ CreatedAt        │  │         │                                              │
│  │ UpdatedAt        │  │         │                                              │
│  └────────┬─────────┘  │         │                                              │
│           │            │         │                                              │
│           └────────────┘         │                                              │
│      (Self-referencing           │                                              │
│       for hierarchy)             │                                              │
│                                  │                                              │
│  ┌───────────────────────────────┴──────────────────────────────────────────┐   │
│  │                              Products                                     │   │
│  │                    (CORE TABLE - SIMPLIFIED SCHEMA)                       │   │
│  ├───────────────────────────────────────────────────────────────────────────┤   │
│  │ ┌─────────────────────────────────────────────────────────────────────┐   │   │
│  │ │ CORE IDENTITY                                                        │   │   │
│  │ │ • Id (PK)          • Name              • Slug (Unique)               │   │   │
│  │ │ • Description      • Price (paise)     • Stock                       │   │   │
│  │ │ • Unit             • Sku (Unique)      • Brand                       │   │   │
│  │ │ • CategoryId (FK)                                                    │   │   │
│  │ └─────────────────────────────────────────────────────────────────────┘   │   │
│  │ ┌─────────────────────────────────────────────────────────────────────┐   │   │
│  │ │ ORGANIC & FRESHNESS (Key differentiator)                             │   │   │
│  │ │ • IsOrganic        • Origin            • FarmName                    │   │   │
│  │ │ • HarvestDate      • BestBefore                                      │   │   │
│  │ └─────────────────────────────────────────────────────────────────────┘   │   │
│  │ ┌─────────────────────────────────────────────────────────────────────┐   │   │
│  │ │ CERTIFICATION (Inline - no separate table)                           │   │   │
│  │ │ • CertificationNumber    • CertificationType    • CertifyingAgency   │   │   │
│  │ └─────────────────────────────────────────────────────────────────────┘   │   │
│  │ ┌─────────────────────────────────────────────────────────────────────┐   │   │
│  │ │ NUTRITION & SEO                                                      │   │   │
│  │ │ • NutritionJson    • SeoTitle          • SeoDescription              │   │   │
│  │ └─────────────────────────────────────────────────────────────────────┘   │   │
│  │ ┌─────────────────────────────────────────────────────────────────────┐   │   │
│  │ │ STATUS & TIMESTAMPS                                                  │   │   │
│  │ │ • IsActive         • IsFeatured        • CreatedAt    • UpdatedAt    │   │   │
│  │ └─────────────────────────────────────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                              │                                                    │
│              ┌───────────────┼───────────────┐                                   │
│              │               │               │                                   │
│              ▼               │               ▼                                   │
│  ┌────────────────────┐      │   ┌───────────────────────────────────────────┐  │
│  │   ProductImages    │      │   │       MANY-TO-MANY: Products ↔ Tags       │  │
│  ├────────────────────┤      │   │                                           │  │
│  │ Id (PK)            │      │   │  ┌──────────────┐    ┌──────────────┐     │  │
│  │ ProductId (FK)─────┼──────┤   │  │    Tags      │    │  ProductTags │     │  │
│  │ Url                │      │   │  ├──────────────┤    ├──────────────┤     │  │
│  │ AltText            │      │   │  │ Id (PK)      │◄───┤ TagId (PK,FK)│     │  │
│  │ SortOrder          │      │   │  │ Name         │    │ ProductId(PK)├─────┤  │
│  │ IsPrimary          │      │   │  │ Slug (Unique)│    └──────────────┘     │  │
│  │ CreatedAt          │      │   │  └──────────────┘     (Composite PK)      │  │
│  └────────────────────┘      │   │                                           │  │
│                              │   └───────────────────────────────────────────┘  │
│                              │                                                   │
└──────────────────────────────┴───────────────────────────────────────────────────┘
```

### Tables Summary (5 Tables - Simplified)

| Table | Purpose | Relationship to Product |
|-------|---------|-------------------------|
| `Products` | Core product data with organic fields | - |
| `Categories` | Product taxonomy/hierarchy | Many Products → One Category |
| `ProductImages` | Product image gallery | One Product → Many Images |
| `Tags` | Reusable discovery labels | - |
| `ProductTags` | Product-Tag junction | Many-to-Many |

**Removed Tables (vs. old schema):**
- ~~ProductAttributes~~ - Organic food has consistent attributes; use inline fields
- ~~ProductCertification~~ - Moved inline to Product
- ~~ProductMetadata~~ - SEO fields moved inline to Product

---

## 3. Entity Relationships

### Relationship Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    RELATIONSHIP SUMMARY                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ONE-TO-MANY (1:N)                                              │
│  ────────────────                                               │
│  • Category → Products     (One category has many products)     │
│  • Product → Images        (One product has many images)        │
│  • Category → Categories   (Self-ref: parent → children)        │
│                                                                  │
│  MANY-TO-MANY (N:M)                                             │
│  ─────────────────                                              │
│  • Products ↔ Tags         (Via ProductTags junction table)     │
│                                                                  │
│  NO 1:1 RELATIONSHIPS                                           │
│  ─────────────────────                                          │
│  Certification & Metadata moved inline for simplicity           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Delete Behaviors

| Relationship | On Delete | Meaning |
|--------------|-----------|---------|
| Category → Products | SET NULL | Products keep existing, CategoryId becomes null |
| Category → Parent | RESTRICT | Cannot delete parent with children |
| Product → Images | CASCADE | Delete product = delete all its images |
| Product ↔ Tags | CASCADE | Delete product = remove from ProductTags |

---

## 4. Tables Deep Dive

### 4.1 Products (Core Table - Simplified)

**Purpose:** Stores all product information with organic-specific fields inline.

#### Core Identity Fields

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `Id` | GUID | PK, Default NewGuid | Unique identifier |
| `Name` | nvarchar(300) | Required | Product name (e.g., "Organic Bananas") |
| `Slug` | nvarchar(300) | Required, Unique | SEO-friendly URL slug |
| `Description` | nvarchar(4000) | Nullable | Detailed description |
| `Price` | int | Default 0 | Price in **paise** (₹1 = 100 paise) |
| `Stock` | int | Default 0 | Available inventory count |
| `Unit` | nvarchar(50) | Nullable | Unit of measure (kg, dozen, bunch) |
| `Sku` | nvarchar(100) | Unique, Nullable | Stock Keeping Unit code |
| `CategoryId` | GUID | FK, Nullable | Link to Categories table |
| `Brand` | nvarchar(150) | Nullable | Brand or farm name |

#### Organic & Freshness Fields (Key Differentiator)

| Column | Type | Description |
|--------|------|-------------|
| `IsOrganic` | bit | Whether certified organic |
| `Origin` | nvarchar(200) | Source location (e.g., "Karnataka, India") |
| `FarmName` | nvarchar(200) | Farm or producer name |
| `HarvestDate` | datetime2 | Harvest/production date |
| `BestBefore` | datetime2 | Expiry date for perishables |

#### Certification Fields (Inline)

| Column | Type | Description |
|--------|------|-------------|
| `CertificationNumber` | nvarchar(100) | Cert ID (e.g., "IN-ORG-123456") |
| `CertificationType` | nvarchar(100) | Type (e.g., "India Organic", "USDA Organic") |
| `CertifyingAgency` | nvarchar(200) | Issuing authority (e.g., "APEDA", "Ecocert") |

#### Nutrition & SEO Fields

| Column | Type | Description |
|--------|------|-------------|
| `NutritionJson` | nvarchar(4000) | JSON nutrition data |
| `SeoTitle` | nvarchar(200) | Meta title for SEO |
| `SeoDescription` | nvarchar(500) | Meta description for SEO |

#### Status Fields

| Column | Type | Description |
|--------|------|-------------|
| `IsActive` | bit | Visibility flag (default: true) |
| `IsFeatured` | bit | Featured product flag |
| `CreatedAt` | datetime2 | Creation timestamp |
| `UpdatedAt` | datetime2 | Last modification timestamp |

**Price Storage:** Prices are stored in **paise** (smallest currency unit) to avoid floating-point precision issues.

```
Database: 9900 paise → Display: ₹99.00
Database: 14999 paise → Display: ₹149.99
```

**NutritionJson Example:**
```json
{
  "calories": 89,
  "protein": 1.1,
  "carbs": 23,
  "fiber": 2.6,
  "sugar": 12,
  "fat": 0.3
}
```

---

### 4.2 Categories (Taxonomy)

**Purpose:** Hierarchical product categorization for organic food.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `Id` | GUID | PK | Unique identifier |
| `Name` | nvarchar(200) | Required | Display name |
| `Slug` | nvarchar(200) | Required, Unique | URL-friendly identifier |
| `Description` | nvarchar(1000) | Nullable | Category description |
| `ParentId` | GUID | FK (self), Nullable | Parent category for hierarchy |
| `IsActive` | bit | Default true | Visibility flag |
| `CreatedAt` | datetime2 | Default UtcNow | Creation timestamp |
| `UpdatedAt` | datetime2 | Nullable | Last modification timestamp |

**Hierarchy Example (Organic Food):**
```
Fruits (ParentId: null)
├── Citrus (ParentId: Fruits.Id)
│   ├── Oranges
│   └── Lemons
├── Berries
└── Tropical

Vegetables (ParentId: null)
├── Leafy Greens
├── Root Vegetables
└── Herbs
```

---

### 4.3 ProductImages (Gallery)

**Purpose:** Store multiple images per product with ordering and primary flag.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `Id` | GUID | PK | Unique identifier |
| `ProductId` | GUID | FK, Required | Link to product |
| `Url` | nvarchar(500) | Required | Image URL (CDN/storage) |
| `AltText` | nvarchar(250) | Nullable | Accessibility text |
| `SortOrder` | int | Default 0 | Display ordering |
| `IsPrimary` | bit | Default false | Primary/thumbnail flag |
| `CreatedAt` | datetime2 | Default UtcNow | Creation timestamp |

**Constraint:** Only one image per product can have `IsPrimary = true` (unique filtered index).

---

### 4.4 Tags & ProductTags (Discovery)

**Purpose:** Reusable labels for product discovery and filtering.

**Tags Table:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `Id` | GUID | PK | Unique identifier |
| `Name` | nvarchar(100) | Required | Display name |
| `Slug` | nvarchar(120) | Required, Unique | URL-friendly identifier |

**ProductTags Table (Junction):**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `ProductId` | GUID | PK, FK | Link to product |
| `TagId` | GUID | PK, FK | Link to tag |

**Example (Organic Food Tags):**
```
Tags: [organic, local, seasonal, farm-fresh, pesticide-free, non-gmo]

Product "Organic Bananas" → Tags: [organic, local, farm-fresh]
Product "Seasonal Mangoes" → Tags: [organic, seasonal]
```

---

## 5. Architecture & Layers

### Layer Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                        API LAYER                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              ProductsController.cs                        │  │
│  │  • HTTP endpoints (GET, POST)                            │  │
│  │  • Request validation                                     │  │
│  │  • Response formatting                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
├────────────────────────────────────────────────────────────────┤
│                      SERVICE LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              ProductServiceImpl.cs                        │  │
│  │  • Business logic                                         │  │
│  │  • Validation rules                                       │  │
│  │  • Orchestration                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
├────────────────────────────────────────────────────────────────┤
│                     REPOSITORY LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              ProductRepository.cs                         │  │
│  │  • Data access                                            │  │
│  │  • CRUD operations                                        │  │
│  │  • Stock management                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
├────────────────────────────────────────────────────────────────┤
│                       DATA LAYER                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              AppDbContext.cs                              │  │
│  │  • EF Core DbContext                                      │  │
│  │  • Entity configurations                                  │  │
│  │  • Migrations                                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│                    ┌──────────────────┐                         │
│                    │   SQL Server     │                         │
│                    │  EP_Local_*Db    │                         │
│                    └──────────────────┘                         │
└────────────────────────────────────────────────────────────────┘
```

### Design Patterns Used

| Pattern | Implementation | Purpose |
|---------|----------------|---------|
| **Repository** | `IProductRepository` / `ProductRepository` | Abstract data access |
| **Service Layer** | `IProductService` / `ProductServiceImpl` | Business logic encapsulation |
| **DTO** | Request/Response classes | API contracts, hide internals |
| **Mapper** | `IProductMapper` / `ProductMapper` | Entity ↔ DTO conversion |

---

## 6. API Endpoints

### Base URL: `/api/products`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List all products |
| GET | `/api/products/{id}` | Get product details |
| POST | `/api/products` | Create new product |
| POST | `/api/products/{id}/reserve` | Reserve stock |
| POST | `/api/products/{id}/release` | Release stock |

### GET /api/products - List Products

**Response (200 OK):**
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Organic Bananas",
    "slug": "organic-bananas-kerala",
    "description": "Fresh organic bananas from Kerala farms",
    "price": 9900,
    "stock": 50,
    "unit": "dozen",
    "category": "Fruits",
    "brand": "Green Valley Farms",
    "imageUrl": "https://cdn.freshharvest.com/bananas.jpg",
    "isOrganic": true,
    "origin": "Kerala, India",
    "farmName": "Green Valley Organics",
    "bestBefore": "2026-02-15T00:00:00Z",
    "certificationType": "India Organic",
    "isActive": true,
    "isFeatured": true,
    "createdAt": "2026-01-31T10:00:00Z"
  }
]
```

### GET /api/products/{id} - Product Details

**Response (200 OK):**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Organic Bananas",
  "slug": "organic-bananas-kerala",
  "description": "Fresh organic bananas from Kerala farms, grown without pesticides",
  "price": 9900,
  "stock": 50,
  "unit": "dozen",
  "sku": "FRU-BAN-ORG-001",
  "categoryId": "...",
  "category": "Fruits",
  "brand": "Green Valley Farms",
  
  "isOrganic": true,
  "origin": "Kerala, India",
  "farmName": "Green Valley Organics",
  "harvestDate": "2026-01-28T00:00:00Z",
  "bestBefore": "2026-02-15T00:00:00Z",
  
  "certificationNumber": "IN-ORG-123456",
  "certificationType": "India Organic",
  "certifyingAgency": "APEDA",
  
  "nutritionJson": "{\"calories\":89,\"protein\":1.1,\"carbs\":23,\"fiber\":2.6}",
  
  "seoTitle": "Buy Organic Bananas Online | Fresh from Kerala",
  "seoDescription": "Fresh organic bananas from certified Kerala farms...",
  
  "isActive": true,
  "isFeatured": true,
  "createdAt": "2026-01-31T10:00:00Z",
  "updatedAt": "2026-01-31T12:00:00Z",
  
  "imageUrl": "https://cdn.freshharvest.com/bananas.jpg",
  "images": [
    {
      "id": "...",
      "url": "https://cdn.freshharvest.com/bananas.jpg",
      "altText": "Fresh organic bananas",
      "sortOrder": 0,
      "isPrimary": true
    }
  ],
  "tags": ["organic", "local", "farm-fresh"]
}
```

### POST /api/products - Create Product

**Request:**
```json
{
  "name": "Organic Tomatoes",
  "slug": "organic-tomatoes-pune",
  "description": "Vine-ripened organic tomatoes",
  "price": 4500,
  "stock": 100,
  "unit": "kg",
  "categoryId": "vegetables-category-id",
  "brand": "Sharma Family Farm",
  
  "isOrganic": true,
  "origin": "Pune, Maharashtra",
  "farmName": "Sharma Family Farm",
  "harvestDate": "2026-01-30T00:00:00Z",
  "bestBefore": "2026-02-10T00:00:00Z",
  
  "certificationNumber": "IN-ORG-789012",
  "certificationType": "India Organic",
  "certifyingAgency": "Ecocert",
  
  "nutritionJson": "{\"calories\":18,\"protein\":0.9,\"carbs\":3.9,\"fiber\":1.2}",
  
  "seoTitle": "Buy Organic Tomatoes Online",
  "seoDescription": "Fresh vine-ripened organic tomatoes...",
  
  "isActive": true,
  "isFeatured": false,
  "imageUrl": "https://cdn.freshharvest.com/tomatoes.jpg",
  "tags": ["organic", "local", "seasonal"]
}
```

### POST /api/products/{id}/reserve - Reserve Stock

**Request:**
```json
{ "quantity": 2 }
```

**Response (200 OK):**
```json
{ "id": "...", "remaining": 48 }
```

**Error (409 Conflict):**
```json
{ "error": "Insufficient stock" }
```

---

## 7. Business Logic

### Stock Management Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    STOCK MANAGEMENT FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  USER ADDS TO CART                                              │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────┐                                            │
│  │ Check Stock > 0 │  (Frontend checks before add to cart)     │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  USER PROCEEDS TO CHECKOUT                                       │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Order Service calls: POST /api/products/{id}/reserve    │    │
│  │ Body: { "quantity": N }                                  │    │
│  └────────┬────────────────────────────────────────────────┘    │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐     ┌──────────────────────────────┐       │
│  │ Stock >= N ?    │─NO─►│ Return 409 Conflict          │       │
│  └────────┬────────┘     │ "Insufficient stock"         │       │
│           │YES           └──────────────────────────────┘       │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Stock = Stock - N                                        │    │
│  │ Save to database                                         │    │
│  │ Return 200 OK { remaining: Stock }                       │    │
│  └────────┬────────────────────────────────────────────────┘    │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │               PAYMENT PROCESSING                         │    │
│  └────────┬─────────────────────────┬──────────────────────┘    │
│           │                         │                            │
│      SUCCESS                      FAILURE                        │
│           │                         │                            │
│           ▼                         ▼                            │
│  ┌─────────────────┐     ┌─────────────────────────────────┐    │
│  │ Order Complete  │     │ POST /api/products/{id}/release │    │
│  │ Stock stays     │     │ Body: { "quantity": N }         │    │
│  │ reduced         │     │ Stock = Stock + N               │    │
│  └─────────────────┘     └─────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Validation Rules

| Field | Rule | Error |
|-------|------|-------|
| Name | Required, not empty | "Name is required" |
| Slug | Required, lowercase/hyphens only | "Slug is required" |
| Price | Must be >= 0 | "Price must be >= 0" |
| Stock | Must be >= 0 | "Stock must be >= 0" |
| Reserve Quantity | Must be > 0 | "Quantity must be > 0" |
| Reserve Quantity | Must be <= Stock | "Insufficient stock" |

---

## 8. Configuration

### Connection Strings

**Local Development** (`appsettings.Development.json`):
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=(localdb)\\MSSQLLocalDB;Database=EP_Local_ProductDb;Integrated Security=true;TrustServerCertificate=True;"
  }
}
```

**Staging** (`appsettings.Staging.json`):
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=(localdb)\\MSSQLLocalDB-Staging;Database=EP_Staging_ProductDb;Integrated Security=true;TrustServerCertificate=True;"
  }
}
```

### Running the Service

```powershell
# Local Development (EP_Local_ProductDb)
cd services/product-service/src/ProductService.API
dotnet run

# Staging (EP_Staging_ProductDb)
dotnet run --environment Staging
```

---

## 9. Code Structure

```
product-service/
├── src/
│   ├── ProductService.API/                    # API Layer
│   │   ├── Controllers/
│   │   │   ├── ProductsController.cs          # Main API endpoints
│   │   │   └── HealthController.cs            # Health check
│   │   ├── Program.cs                         # Entry point
│   │   ├── Startup.cs                         # DI configuration
│   │   ├── appsettings.json                   # Base config
│   │   ├── appsettings.Development.json       # Local DB config
│   │   └── appsettings.Staging.json           # Staging DB config
│   │
│   ├── ProductService.Core/                   # Business Layer
│   │   ├── Business/
│   │   │   ├── IProductService.cs             # Service interface
│   │   │   └── ProductServiceImpl.cs          # Service implementation
│   │   ├── Repository/
│   │   │   ├── IProductRepository.cs          # Repository interface
│   │   │   └── ProductRepository.cs           # Data access
│   │   ├── Mappers/
│   │   │   ├── IProductMapper.cs              # Mapper interface
│   │   │   └── ProductMapper.cs               # Entity ↔ DTO mapping
│   │   └── Data/
│   │       ├── AppDbContext.cs                # EF Core context
│   │       └── Migrations/                    # DB migrations
│   │
│   └── ProductService.Abstraction/            # Contracts Layer
│       ├── Models/                            # Entity classes
│       │   ├── Product.cs                     # Core entity (simplified)
│       │   ├── Category.cs                    # Taxonomy
│       │   ├── ProductImage.cs                # Images
│       │   ├── Tag.cs                         # Tags
│       │   └── ProductTag.cs                  # Junction table
│       └── DTOs/                              # Data Transfer Objects
│           ├── Requests/
│           │   ├── CreateProductRequest.cs
│           │   ├── UpdateProductRequest.cs
│           │   └── ReserveStockRequest.cs
│           └── Responses/
│               ├── ProductResponse.cs         # List view
│               └── ProductDetailResponse.cs   # Detail view
│
└── test/                                      # Tests
    ├── unit-test/
    │   ├── ProductService.API.Test/
    │   └── ProductService.Core.Test/
    └── integration-test/
        └── ProductService.Integration.Test/
```

---

## Summary

The Product Service is a **simplified, domain-specific** catalog management system for FreshHarvest Market:

- **5 database tables** (reduced from 8)
- **Inline organic fields** - No unnecessary joins for core organic attributes
- **Inline certification** - Product-specific, not a separate table
- **Stock management** with reserve/release operations
- **Hierarchical categories** for organic food taxonomy
- **Many-to-many tags** for product discovery
- **Clean architecture** with separation of concerns

### Schema Philosophy

> "Keep it simple. Organic food products have consistent attributes. 
> Don't over-engineer with EAV patterns or unnecessary 1:1 tables."

**Database:** `EP_Local_ProductDb` (Local) | `EP_Staging_ProductDb` (Staging)  
**Port:** 5002  
**Swagger:** http://localhost:5002/swagger

---

*Document Version: 3.0 (Simplified Schema)*  
*Last Updated: January 31, 2026*
