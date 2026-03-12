# 📅 Sprint-by-Sprint Guide - FreshHarvest Market Evolution

> **See exactly what happens in each sprint, what users will experience, and what you need to focus on as Product Owner**

---

## 🎯 How to Use This Guide

**Before each sprint:**
1. Read the sprint section below
2. Understand what users will experience
3. Review what you need to focus on
4. Prepare for sprint planning

**During the sprint:**
- Reference this guide when reviewing work
- Use the demo script to validate features
- Check the PO focus areas

**After the sprint:**
- Use the demo script in sprint review
- Validate against the success criteria
- Plan for the next sprint

---

## 📊 Current Status

**✅ MVP Complete (Sprint 0)**
- Basic e-commerce functionality working
- Users can: sign up, browse organic products, add to cart, checkout, view orders

**🚧 Next: Epic 1 - Enhanced Product Domain**
- Starting with Sprint 1
- Goal: Make catalog feel like a premium organic food marketplace

---

## 🗓️ Sprint Overview (All 35 Sprints)

### Q1: Enhanced Catalog (Sprints 1-6)
**Theme:** Make product browsing and selection feel like premium organic food commerce

| Sprint | Theme | What Users See |
|--------|-------|----------------|
| 1 | Categories | Products organized by type (Fresh Fruits, Vegetables, Grains, Dairy, Herbs) |
| 2 | Variants | Can select pack sizes (1kg, 5kg, 10kg), see different prices |
| 3 | Pricing + Attributes | See discounts clearly, view product attributes (certifications, origin, expiry) |
| 4 | Media + Search | Product galleries, search and filter by certification/origin |
| 5 | Inventory + Reviews | Stock/freshness alerts, customer reviews and ratings |
| 6 | Wishlist + Compare | Save items, compare products side-by-side |

### Q2: Trustworthy Orders (Sprints 7-11)
**Theme:** Make purchasing and post-purchase trustworthy and explicit

| Sprint | Theme | What Users See |
|--------|-------|----------------|
| 7 | Order Lifecycle | Clear order status with progression |
| 8 | Cancel/Modify | Can cancel orders, get refunds |
| 9 | Reliability + Invoice | Fewer errors, can download invoices |
| 10 | Multi-payments | Choose payment method (card, UPI, wallet) |
| 11 | Coupons + Retry | Apply promo codes, retry failed payments |

### Q3: Frontend & Testing (Sprints 12-18)
**Theme:** Modernize frontend and add comprehensive testing

| Sprint | Theme | What Users See |
|--------|-------|----------------|
| 12 | React Query | Faster page loads, less loading flicker |
| 13 | Global State + Forms | Better forms, fewer UI bugs |
| 14 | PWA + A11y | Can install as app, more accessible |
| 15 | Errors + Micro-UX | Better error messages, smoother interactions |
| 16 | Storybook + Perf | Consistent UI, faster performance |
| 17 | Backend Tests | Fewer bugs, more stable |
| 18 | Integration + E2E | More reliable, tested user journeys |

### Q4: DevOps & Operations (Sprints 19-27)
**Theme:** Automate deployment and add observability

| Sprint | Theme | What Users See |
|--------|-------|----------------|
| 19 | CI Basics | Faster deployments, visible build status |
| 20 | Versioning/Quality | Better release management |
| 21 | K8s Setup | Deployable to cloud |
| 22 | Helm + Ingress | Easier rollbacks, stable routing |
| 23 | Storage + Scaling | Handles more traffic |
| 24 | Mesh/GitOps | Advanced operations (optional) |
| 25 | Logging | Better error tracking |
| 26 | Metrics/Dashboards | System health visible |
| 27 | Tracing | Performance monitoring |

### Q5: Growth & Security (Sprints 28-35)
**Theme:** Add growth features and security hardening

| Sprint | Theme | What Users See |
|--------|-------|----------------|
| 28 | Notifications | Order updates, confirmations |
| 29 | Recommendations | "Customers also bought" suggestions |
| 30-31 | Admin | Admin dashboard for managing store |
| 32 | Advanced Search | Better search, real-time updates |
| 33 | Caching + Rate Limit | Faster responses, protection from abuse |
| 34 | Security Hardening | More secure, protected data |
| 35 | Security Testing | Security audits, compliance |

---

## 📝 Detailed Sprint Breakdowns

### Sprint 0: MVP Baseline ✅ COMPLETE

**What users can do:**
- Register and log in
- Browse organic products (basic list)
- Add items to cart
- Checkout using wallet payment (₹ INR)
- View order history
- Add money to wallet

**What's working:**
- 5 microservices (Auth, User, Product, Order, Payment)
- API Gateway
- Basic frontend with organic theme
- Docker setup

**Status:** ✅ Complete

---

### Sprint 1: Categories & Type System 🚧 NEXT

**Epic:** Epic 1 - Enhanced Product Domain  
**PBI:** PBI 1.1 - Product Categories & Types  
**Story Points:** 13

#### What Users Will Experience

**Before Sprint 1:**
- Products are just a flat list
- No organization by type
- Hard to find specific categories

**After Sprint 1:**
- Products organized into categories:
  - 🍎 Fresh Fruits
  - 🥬 Fresh Vegetables
  - 🌾 Grains & Pulses
  - 🥛 Dairy & Eggs
  - 🍃 Herbs & Spices
- Can browse by category
- Can filter by category
- Product detail pages show category and organic certifications

**User Journey:**
1. User visits homepage
2. Sees category navigation (like BigBasket's department menu)
3. Clicks "Fresh Fruits"
4. Sees only organic fruits
5. Can filter further within category (by certification, origin)

#### What You Need to Focus On (PO)

**Acceptance Criteria:**
- [ ] Products have categories assigned
- [ ] Categories are displayed in navigation
- [ ] Can filter products by category
- [ ] Product detail pages show category
- [ ] API endpoints support category filtering

**Questions to Ask:**
- How are categories structured? (hierarchy or flat?)
- Can a product be in multiple categories?
- What happens to existing products without categories?

**Demo Script:**
1. Show homepage with category navigation
2. Click "Fresh Fruits" category
3. Show filtered product list (organic mangoes, apples, etc.)
4. Click a product (e.g., Organic Alphonso Mangoes)
5. Show product detail with category displayed
6. Show category filter working

**Success Metrics:**
- Users can find products faster
- Category navigation is intuitive
- Filtering works correctly

**Related Documents:**
- [Epic 1](../4-epics-and-pbis/EPIC_1/EPIC_1.md)
- [PBI 1.1](../4-epics-and-pbis/EPIC_1/EPIC_1_PBI_1_1.md)

---

### Sprint 2: Variant Selection

**Epic:** Epic 1 - Enhanced Product Domain  
**PBI:** PBI 1.2 - Product Variants (SKUs)  
**Story Points:** 13

#### What Users Will Experience

**Before Sprint 2:**
- Products are single items
- No pack size options
- Can't see different configurations

**After Sprint 2:**
- Products have variants:
  - **Example:** Organic Basmati Rice
    - Pack Sizes: 1kg, 5kg, 10kg, 25kg
    - Total: 4 variants
  - **Example:** Organic Alphonso Mangoes
    - Pack Sizes: 1 dozen, 2 dozen, 5 dozen
    - Quality Grades: Premium, Standard
- Can select variant on product page
- Price changes based on variant (bulk discounts)
- Stock shown per variant
- SKU (Stock Keeping Unit) for each variant

**User Journey:**
1. User opens Organic Basmati Rice product page
2. Sees variant selector (Pack Size dropdown)
3. Selects "5kg"
4. Price updates: ₹250 → ₹1,150 (with bulk discount)
5. Stock shows: "In Stock" or "Only 5 packs left"
6. Adds to cart with selected variant

#### What You Need to Focus On (PO)

**Acceptance Criteria:**
- [ ] Products can have multiple variants
- [ ] Variant selector works on product page
- [ ] Price updates when variant changes
- [ ] Stock shown per variant
- [ ] Cart stores selected variant
- [ ] SKU generated for each variant

**Questions to Ask:**
- How are variants structured? (all combinations or specific ones?)
- What if a variant combination doesn't exist?
- How do we handle variant pricing?
- What about variant images?

**Demo Script:**
1. Open product with variants (e.g., Organic Basmati Rice)
2. Show variant selector (pack sizes)
3. Change pack size → price/stock updates
4. Show bulk discount applied
5. Add to cart
6. Show cart with variant selected
7. Show checkout with correct variant

**Success Metrics:**
- Users can select variants easily
- Price/stock updates correctly
- No confusion about which variant is selected

**Related Documents:**
- [Epic 1](../4-epics-and-pbis/EPIC_1/EPIC_1.md)
- [PBI 1.2](../4-epics-and-pbis/EPIC_1/EPIC_1_PBI_1_2.md)

---

### Sprint 3: Pricing + Product Attributes

**Epic:** Epic 1 - Enhanced Product Domain  
**PBI:** PBI 1.3 - Dynamic Pricing, PBI 1.4 - Product Attributes  
**Story Points:** 13 + 13 = 26

#### What Users Will Experience

**Pricing:**
- See original price and sale price
- See discount percentage (e.g., "20% OFF")
- Understand pricing strategies:
  - Regular price
  - Sale price
  - Bulk discounts (buy more, save more)
  - Seasonal pricing (mango season discounts)
- Transparent pricing display

**Product Attributes:**
- Product detail pages show detailed attributes:
  - **All Products:** Origin farm, Organic certification (India Organic, USDA, EU)
  - **Fresh Produce:** Harvest date, Expiry date, Freshness indicator
  - **Grains/Pulses:** Nutritional info, Cooking time, Storage instructions
  - **Dairy:** Fat content, Shelf life, Storage temperature
- Attributes organized by category
- Can filter products by certification, origin

**User Journey:**
1. User opens product page
2. Sees pricing: "Was ₹599, Now ₹449 (25% OFF - Mango Season)"
3. Scrolls to attributes section
4. Sees certifications: "🇮🇳 India Organic Certified"
5. Sees origin: "Ratnagiri, Maharashtra"
6. Can filter other products by certification

#### What You Need to Focus On (PO)

**Pricing Acceptance Criteria:**
- [ ] Multiple pricing strategies supported
- [ ] Discounts displayed clearly
- [ ] Price calculation is correct
- [ ] Pricing rules are testable

**Attributes Acceptance Criteria:**
- [ ] Products have attributes (certifications, origin, expiry)
- [ ] Attributes displayed on product page
- [ ] Can filter by certification and origin
- [ ] Attributes organized by category

**Questions to Ask:**
- What pricing strategies do we support?
- How are attributes stored? (flexible or fixed?)
- Can attributes vary by product type?
- How do we handle missing attributes?
- Which certifications do we support?

**Demo Script:**
1. Show product with seasonal sale price
2. Explain discount calculation
3. Show attributes section (certifications, origin, expiry)
4. Filter products by certification (e.g., "India Organic")
5. Show filtered results

**Success Metrics:**
- Users trust pricing
- Users can verify organic certifications
- Users can filter by origin/certification
- Pricing calculations are accurate

**Related Documents:**
- [PBI 1.3](../4-epics-and-pbis/EPIC_1/EPIC_1_PBI_1_3.md) - Dynamic Pricing
- [PBI 1.4](../4-epics-and-pbis/EPIC_1/EPIC_1_PBI_1_4.md) - Product Attributes

---

### Sprint 4: Media + Search/Filter

**Epic:** Epic 1 - Enhanced Product Domain  
**PBI:** PBI 1.5 - Product Images, PBI 1.6 - Search & Filtering  
**Story Points:** 13 + 21 = 34

#### What Users Will Experience

**Media:**
- Product pages have image galleries
- Multiple images per product (farm photos, product photos)
- Can zoom images
- Primary image displayed
- Image carousel/slider

**Search & Filter:**
- Search bar in header
- Can search by product name, farm, description
- Advanced filters:
  - Category (Fruits, Vegetables, Grains, Dairy, Herbs)
  - Price range
  - Certification (India Organic, USDA, EU Organic)
  - Origin (state/region)
- Sort options:
  - Price: Low to High
  - Price: High to Low
  - Freshness: Newest First
  - Best Rated
- Pagination (show 20 products per page)

**User Journey:**
1. User types "organic mangoes" in search
2. Sees search results
3. Applies filters: "Price: ₹200-₹500", "Certification: India Organic"
4. Sorts by "Price: Low to High"
5. Clicks product
6. Sees image gallery with zoom (farm and product photos)
7. Can browse through images

#### What You Need to Focus On (PO)

**Media Acceptance Criteria:**
- [ ] Products have multiple images
- [ ] Image gallery works
- [ ] Can zoom images
- [ ] Primary image displayed correctly
- [ ] Images load quickly

**Search Acceptance Criteria:**
- [ ] Search works by name, brand, description
- [ ] Filters work correctly
- [ ] Sort options work
- [ ] Pagination works
- [ ] Search is fast enough

**Questions to Ask:**
- How many images per product?
- Image storage location? (local or cloud?)
- Search performance requirements?
- What filters are most important for organic products?
- How many results per page?
- Do we show farm/origin photos?

**Demo Script:**
1. Search "organic mangoes"
2. Apply filters: certification, price range
3. Sort results by freshness
4. Click product
5. Show image gallery (product + farm photos)
6. Zoom an image
7. Navigate through images

**Success Metrics:**
- Users can find products quickly
- Search results are relevant
- Filters work correctly
- Images load fast

**Related Documents:**
- [PBI 1.5](../4-epics-and-pbis/EPIC_1/) - Product Images (when created)
- [PBI 1.6](../4-epics-and-pbis/EPIC_1/) - Search & Filtering (when created)

---

### Sprint 5: Inventory + Reviews

**Epic:** Epic 1 - Enhanced Product Domain  
**PBI:** PBI 1.7 - Inventory Management, PBI 1.8 - Reviews & Ratings  
**Story Points:** 13 + 13 = 26

#### What Users Will Experience

**Inventory:**
- Stock and freshness status displayed clearly:
  - "Fresh Stock Available"
  - "Only 5kg left - Order soon!"
  - "Out of Stock"
  - "Next Batch: Tomorrow"
- Low stock alerts
- Freshness indicators (harvested date, expiry)
- Stock updates in real-time

**Reviews & Ratings:**
- Product pages show:
  - Average rating (e.g., 4.5 stars)
  - Number of reviews
  - Review breakdown (5 stars, 4 stars, etc.)
- Can read reviews:
  - Review title
  - Rating
  - Review text (freshness, taste, packaging quality)
  - Reviewer name (or "Verified Buyer")
  - Date
- Can write reviews (if purchased)
- Can rate products

**User Journey:**
1. User opens product page
2. Sees stock status: "Only 5kg left - Order soon! Harvested 2 days ago"
3. Scrolls to reviews section
4. Sees average rating: 4.5/5 (127 reviews)
5. Reads reviews about freshness and quality
6. After purchase, can leave review

#### What You Need to Focus On (PO)

**Inventory Acceptance Criteria:**
- [ ] Stock status displayed
- [ ] Low stock alerts work
- [ ] Stock updates correctly
- [ ] Can't add out-of-stock to cart

**Reviews Acceptance Criteria:**
- [ ] Can view reviews
- [ ] Can write reviews (if purchased)
- [ ] Ratings displayed correctly
- [ ] Review moderation (if needed)
- [ ] Verified buyer badge

**Questions to Ask:**
- What stock thresholds trigger alerts?
- Who can write reviews? (all users or verified buyers only?)
- Review moderation process?
- How are ratings calculated?

**Demo Script:**
1. Show product with low stock alert and freshness indicator
2. Show reviews section
3. Read a review about freshness/quality
4. Show rating breakdown
5. (If purchased) Show review form
6. Submit review
7. Show review appears

**Success Metrics:**
- Users trust stock and freshness information
- Reviews help decision-making about quality
- Review submission works

**Related Documents:**
- [PBI 1.7](../4-epics-and-pbis/EPIC_1/) - Inventory Management (when created)
- [PBI 1.8](../4-epics-and-pbis/EPIC_1/) - Reviews & Ratings (when created)

---

### Sprint 6: Wishlist + Comparison

**Epic:** Epic 1 - Enhanced Product Domain  
**PBI:** PBI 1.9 - Wishlist, PBI 1.10 - Product Comparison  
**Story Points:** 13 + 8 = 21

#### What Users Will Experience

**Wishlist:**
- Can add products to wishlist
- Can view wishlist
- Can remove from wishlist
- Wishlist persists (saved to account)
- Can add wishlist items to cart
- Get notified if wishlist item price drops (future)

**Comparison:**
- Can select products to compare (up to 4)
- Comparison page shows:
  - Side-by-side product details
  - Certification comparison
  - Price per kg comparison
  - Origin comparison
  - Rating comparison
- Highlights differences
- Can only compare similar products (same category)

**User Journey:**
1. User browses products
2. Clicks "Add to Wishlist" on 3 products
3. Views wishlist page
4. Selects 2 products to compare
5. Sees comparison page
6. Sees differences highlighted
7. Makes decision based on comparison

#### What You Need to Focus On (PO)

**Wishlist Acceptance Criteria:**
- [ ] Can add/remove from wishlist
- [ ] Wishlist persists
- [ ] Can view wishlist
- [ ] Can add wishlist items to cart

**Comparison Acceptance Criteria:**
- [ ] Can select products to compare (max 4)
- [ ] Comparison page shows key details
- [ ] Differences highlighted
- [ ] Can only compare similar products
- [ ] Comparison works correctly

**Questions to Ask:**
- How many items in wishlist? (unlimited?)
- What products can be compared? (same category only?)
- What details shown in comparison?
- How are differences highlighted?

**Demo Script:**
1. Add products to wishlist
2. View wishlist
3. Select products to compare
4. Show comparison page
5. Highlight differences
6. Add one to cart from comparison

**Success Metrics:**
- Users use wishlist
- Comparison helps decisions
- Users return to wishlist

**Related Documents:**
- [PBI 1.9](../4-epics-and-pbis/EPIC_1/) - Wishlist (when created)
- [PBI 1.10](../4-epics-and-pbis/EPIC_1/) - Product Comparison (when created)

---

## 🎯 Epic 1 Complete!

**After Sprint 6, Epic 1 is complete!**

**What we've built:**
- ✅ Professional organic product catalog
- ✅ Categories (Fruits, Vegetables, Grains, Dairy, Herbs)
- ✅ Product variants (pack sizes)
- ✅ Dynamic pricing (bulk discounts, seasonal pricing)
- ✅ Product attributes (certifications, origin, freshness)
- ✅ Image galleries (product + farm photos)
- ✅ Search and filtering by certification/origin
- ✅ Inventory management with freshness tracking
- ✅ Reviews and ratings
- ✅ Wishlist
- ✅ Product comparison

**What users can do:**
- Find organic products easily
- Verify certifications (India Organic, USDA, EU)
- Compare products by price, certification, origin
- Make informed decisions about quality
- Save items for later
- Read reviews about freshness and quality
- Trust the pricing and authenticity

**Next:** Epic 2 - Advanced Order Management

---

## 📋 Sprint 7-11: Epic 2-3 (Trustworthy Orders)

### Sprint 7: Order Lifecycle

**What users see:**
- Clear order status:
  - Pending
  - Processing
  - Shipped
  - Delivered
  - Cancelled
- Order status updates
- Order history with status
- Status progression visible

**PO Focus:**
- State machine rules
- Status transitions
- History tracking

---

### Sprint 8: Cancel/Modify Orders

**What users see:**
- Can cancel orders (when allowed)
- Automatic refunds
- Clear cancellation rules
- Can modify orders (before shipping)

**PO Focus:**
- Cancellation rules
- Refund logic
- Modification constraints

---

### Sprint 9: Reliability + Invoice

**What users see:**
- Fewer errors
- Better error handling
- Can download invoices
- Invoices emailed automatically

**PO Focus:**
- Error handling
- Invoice format
- Email delivery

---

### Sprint 10: Multi-Payment Methods

**What users see:**
- Choose payment method:
  - Wallet (existing)
  - Credit/Debit Card
  - UPI
  - Net Banking
- Clear payment status
- Payment retry options

**PO Focus:**
- Payment adapter interfaces
- Payment method selection
- Error handling

---

### Sprint 11: Coupons + Payment Retry

**What users see:**
- Can apply coupon codes
- Discount shown clearly
- Payment retry if fails
- Clear error messages

**PO Focus:**
- Coupon validation
- Retry logic
- Error messaging

---

## 📚 How to Use This Guide

### Before Each Sprint

1. **Read the sprint section** - Understand what's coming
2. **Review related documents** - Read Epic and PBI docs
3. **Prepare questions** - List what's unclear
4. **Review acceptance criteria** - Know what "done" means
5. **Prepare demo script** - Know what to validate

### During Sprint

1. **Reference this guide** - Check what users should see
2. **Review work in progress** - Validate against criteria
3. **Test features** - Use the demo script
4. **Answer questions** - Help the team

### After Sprint

1. **Use demo script** - In sprint review
2. **Validate success** - Check metrics
3. **Plan next sprint** - Review next section

---

## 🔗 Related Documents

- [Product Roadmap](../3-product-owner/PRODUCT_ROADMAP_PM_PO.md) - High-level roadmap
- [Project Roadmap](../9-roadmap-and-tracking/PROJECT_ROADMAP.md) - Detailed roadmap
- [Iteration Checklist](../9-roadmap-and-tracking/ITERATION_CHECKLIST.md) - Progress tracking
- [Epic 1](../4-epics-and-pbis/EPIC_1/EPIC_1.md) - Epic details
- [Definition of Done](../3-product-owner/DEFINITION_OF_DONE.md) - What "done" means

---

**Remember:** This is a living document. As we progress, we'll add more detail to future sprints. Focus on the current and next sprint!

**Last Updated:** January 2026  
**Version:** 1.0
