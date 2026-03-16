# 🚀 Getting Started with FreshHarvest Market

> **Quick setup and project understanding for the organic food marketplace**

---

## 📋 Documents in This Section

### 1. [Project Overview](PROJECT_OVERVIEW.md)
**Read Time:** 30 minutes  
**Purpose:** Complete project understanding - vision, goals, current status, features, metrics

**When to Read:**
- First time exploring the project
- Understanding the big picture
- Before contributing

---

### 2. [Tech Stack](TECH_STACK.md)
**Read Time:** 20 minutes  
**Purpose:** All technologies used, rationale, costs, alternatives

**When to Read:**
- Understanding technology choices
- Planning learning path
- Evaluating project complexity

---

## 🎯 Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Start everything
cd infra
docker-compose up --build -d

# Access
# Frontend: http://localhost:3000
# API Gateway: http://localhost:5000
# Swagger: http://localhost:5001-5005/swagger
```

### Option 2: Run Services Individually
```bash
# SQL Server
cd infra
docker-compose up -d mssql

# Each service
cd services/auth-service
dotnet run

# Frontend
cd frontend
npm install && npm start
```

---

## 🧭 Next Steps

**After Reading This Section:**

1. **For Learners** → Go to [`../2-learning-guide/`](../2-learning-guide/)
2. **For Product Owners** → Go to [`../3-product-owner/`](../3-product-owner/)
3. **To See User Flows** → Go to [`../5-user-flows/`](../5-user-flows/)
4. **To Understand Architecture** → Go to [`../6-architecture/`](../6-architecture/)

---

**Back to:** [Documentation Index](../DOCUMENTATION_INDEX.md) | [START HERE](../START_HERE.md)


















