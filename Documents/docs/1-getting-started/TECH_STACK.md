# 🛠️ FreshHarvest Market - Complete Tech Stack

> **Last Updated:** January 2026  
> **Status:** MVP Complete + Testing + CI/CD (76% complete)  
> **Brand:** FreshHarvest Market - Organic Food E-Commerce Platform

---

## 📋 Table of Contents

- [Current Tech Stack (Implemented)](#current-tech-stack-implemented)
- [Planned Tech Stack (Roadmap)](#planned-tech-stack-roadmap)
- [Open Source & Free Tools](#open-source--free-tools)
- [Cost Analysis](#cost-analysis)
- [Technology Decisions & Rationale](#technology-decisions--rationale)

---

## 🎯 Current Tech Stack (Implemented)

### Frontend

| Technology       | Version | Purpose             | License      | Status         |
| ---------------- | ------- | ------------------- | ------------ | -------------- |
| **React**        | 18.x    | UI Framework        | MIT          | ✅ Implemented |
| **React Router** | 6.x     | Client-side routing | MIT          | ✅ Implemented |
| **Axios**        | 1.6.x   | HTTP client         | MIT          | ✅ Implemented |
| **CSS3**         | -       | Styling             | -            | ✅ Implemented |
| **Nginx**        | 1.25+   | Web server (Docker) | BSD-2-Clause | ✅ Implemented |

**Current Features:**

- ✅ Component-based architecture
- ✅ Custom hooks (`useAuth`, `useCart`, `useProducts`)
- ✅ Client-side routing with protected routes
- ✅ Responsive design
- ✅ localStorage for cart persistence
- ✅ JWT token management

---

### Backend

| Technology                | Version | Purpose                     | License | Status         |
| ------------------------- | ------- | --------------------------- | ------- | -------------- |
| **.NET**                  | 10.0    | Microservices framework     | MIT     | ✅ Implemented |
| **ASP.NET Core**          | 10.0    | Web API framework           | MIT     | ✅ Implemented |
| **Entity Framework Core** | 10.0    | ORM for database access     | MIT     | ✅ Implemented |
| **BCrypt.NET**            | 0.1.0   | Password hashing            | MIT     | ✅ Implemented |
| **JWT Bearer**            | 10.0    | Token authentication        | MIT     | ✅ Implemented |
| **Swashbuckle**           | 6.5.0   | API documentation (Swagger) | MIT     | ✅ Implemented |

**Architecture:**

- ✅ 5 independent microservices
- ✅ RESTful API design
- ✅ Database-per-service pattern
- ✅ Service-to-service HTTP communication
- ✅ Health check endpoints

---

### API Gateway

| Technology       | Version | Purpose           | License | Status         |
| ---------------- | ------- | ----------------- | ------- | -------------- |
| **YARP**         | 2.1.0   | Reverse proxy     | MIT     | ✅ Implemented |
| **ASP.NET Core** | 10.0    | Gateway framework | MIT     | ✅ Implemented |

**Features:**

- ✅ Request routing
- ✅ Load balancing (round-robin)
- ✅ Health checks with circuit breaker
- ✅ Environment-specific configuration
- ✅ Service discovery (manual)

---

### Database

| Technology                | Version | Purpose             | License                 | Status         |
| ------------------------- | ------- | ------------------- | ----------------------- | -------------- |
| **SQL Server**            | 2019    | Relational database | Commercial/Free Express | ✅ Implemented |
| **Entity Framework Core** | 10.0    | ORM                 | MIT                     | ✅ Implemented |

**Database Strategy:**

- ✅ Separate database per service (5 databases)
- ✅ Code-first migrations
- ✅ GUID primary keys
- ✅ Decimal precision for currency

**Databases:**

- ✅ `EP_Local_AuthDb` - Authentication service
- ✅ `EP_Local_UserDb` - User profiles and wallet (INR ₹)
- ✅ `EP_Local_ProductDb` - Organic product catalog (with certifications)
- ✅ `EP_Local_OrderDb` - Orders and order items
- ✅ `EP_Local_PaymentDb` - Payment transactions

---

### DevOps & Infrastructure

| Technology                    | Version | Purpose                       | License | Status         |
| ----------------------------- | ------- | ----------------------------- | ------- | -------------- |
| **Docker**                    | 20.x+   | Containerization              | Apache  | ✅ Implemented |
| **Docker Compose**            | 2.x     | Multi-container orchestration | Apache  | ✅ Implemented |
| **GitHub Actions**            | -       | CI/CD                         | Free    | ✅ Implemented |
| **GitHub Container Registry** | -       | Docker image registry         | Free    | ✅ Implemented |
| **Semantic Release**          | -       | Automated versioning          | MIT     | ✅ Implemented |

**Features:**

- ✅ Multi-stage Docker builds
- ✅ Docker Compose for local development
- ✅ Docker health checks
- ✅ Automated CI pipeline (build, test, coverage)
- ✅ Automated Docker image builds and pushes
- ✅ Semantic versioning with alpha/production tags
- ✅ Automated GitHub releases and CHANGELOG generation

---

### Testing

| Technology                | Version | Purpose                | License | Status         |
| ------------------------- | ------- | ---------------------- | ------- | -------------- |
| **xUnit**                 | 2.6.x   | .NET testing framework | Apache  | ✅ Implemented |
| **Moq**                   | 4.20.x  | Mocking framework      | MIT     | ✅ Implemented |
| **FluentAssertions**      | 6.12.x  | Assertion library      | Apache  | ✅ Implemented |
| **Coverlet**              | 6.0.x   | Code coverage          | MIT     | ✅ Implemented |
| **React Testing Library** | 14.x    | Component testing      | MIT     | ✅ Implemented |
| **Jest**                  | 27.x    | JavaScript testing     | MIT     | ✅ Implemented |
| **WebApplicationFactory** | 10.0    | Integration testing    | MIT     | ✅ Implemented |

**Test Coverage:**

- ✅ Unit tests for all 5 microservices (>80% coverage)
- ✅ Integration tests for all API endpoints
- ✅ Frontend component tests
- ✅ Custom hook tests
- ⏳ E2E tests with Playwright (planned)

---

### Code Quality & Security

| Technology     | Version | Purpose               | License | Status         |
| -------------- | ------- | --------------------- | ------- | -------------- |
| **SonarCloud** | -       | Code quality analysis | Free    | ✅ Implemented |
| **StyleCop**   | 1.2.0   | C# code style         | MIT     | ✅ Implemented |
| **ESLint**     | 8.x     | JavaScript linting    | MIT     | Planned        |
| **Prettier**   | 3.x     | Code formatting       | MIT     | Planned        |

**Features:**

- ✅ Automated code quality gates in CI
- ✅ Code coverage reporting to SonarCloud
- ✅ StyleCop analysis for C# code
- ✅ Quality gate enforcement
- ⏳ Dependency scanning (planned - PBI 6.5)

---

## 📋 Planned Tech Stack (Roadmap)

---

### DevOps (Current)

| Technology         | Version | Purpose                       | License    |
| ------------------ | ------- | ----------------------------- | ---------- |
| **Docker**         | 24.x    | Containerization              | Apache 2.0 |
| **Docker Compose** | 2.x     | Multi-container orchestration | Apache 2.0 |
| **Git**            | 2.x     | Version control               | GPL-2.0    |
| **GitHub**         | -       | Repository hosting            | -          |

**Current Setup:**

- Dockerized all services
- Docker Compose orchestration
- Health checks for all containers
- Multi-stage Docker builds
- Volume mounts for SQL Server data persistence

---

## 🚀 Planned Tech Stack (Roadmap)

### Frontend Enhancements

| Technology                | Purpose                 | Why                                               | License    | Epic   |
| ------------------------- | ----------------------- | ------------------------------------------------- | ---------- | ------ |
| **React Query**           | Server state management | Caching, automatic refetching, optimistic updates | MIT        | Epic 4 |
| **Zustand**               | Global state management | Lightweight, no boilerplate, TypeScript-first     | MIT        | Epic 4 |
| **React Hook Form**       | Form management         | Performance, less re-renders, better DX           | MIT        | Epic 4 |
| **Zod**                   | Schema validation       | Type-safe validation, inference                   | MIT        | Epic 4 |
| **Framer Motion**         | Animations              | Declarative animations, gestures                  | MIT        | Epic 4 |
| **Vitest**                | Unit testing            | Fast, Vite-native, Jest-compatible                | MIT        | Epic 5 |
| **React Testing Library** | Component testing       | User-centric testing                              | MIT        | Epic 5 |
| **Playwright**            | E2E testing             | Cross-browser, reliable, fast                     | Apache 2.0 | Epic 5 |
| **Storybook**             | Component documentation | Isolated component development                    | MIT        | Epic 4 |
| **Vite**                  | Build tool              | Fast HMR, optimized builds                        | MIT        | Epic 4 |
| **Workbox**               | PWA support             | Service worker, offline support                   | Apache 2.0 | Epic 4 |

**Rationale:**

- **React Query:** Eliminates 90% of state management boilerplate for server data
- **Zustand:** Simple, performant alternative to Redux/Context for client state
- **React Hook Form:** 10x performance improvement over traditional controlled forms
- **Framer Motion:** Industry-standard for React animations
- **Vitest:** 2-10x faster than Jest, better Vite integration

---

### Backend Enhancements

| Technology              | Purpose                 | Why                                       | License         | Epic    |
| ----------------------- | ----------------------- | ----------------------------------------- | --------------- | ------- |
| **Polly**               | Resilience patterns     | Retry, circuit breaker, timeout policies  | BSD-3-Clause    | Epic 3  |
| **FluentValidation**    | Input validation        | Strongly-typed, reusable validation rules | Apache 2.0      | Epic 10 |
| **Serilog**             | Structured logging      | Rich structured events, multiple sinks    | Apache 2.0      | Epic 8  |
| **OpenTelemetry**       | Observability           | Distributed tracing, metrics, logging     | Apache 2.0      | Epic 8  |
| **MediatR**             | CQRS                    | Mediator pattern, decoupled handlers      | Apache 2.0      | Future  |
| **AutoMapper**          | Object mapping          | DTO mapping automation                    | MIT             | Epic 1  |
| **Hangfire**            | Background jobs         | Task scheduling, retries                  | LGPL/Commercial | Epic 9  |
| **SignalR**             | Real-time communication | WebSocket abstraction                     | MIT             | Epic 9  |
| **StackExchange.Redis** | Caching                 | High-performance caching                  | MIT             | Epic 10 |
| **NEST**                | Elasticsearch client    | Full-text search                          | Apache 2.0      | Epic 9  |
| **QuestPDF**            | PDF generation          | Invoice generation                        | MIT             | Epic 2  |

**Rationale:**

- **Polly:** Industry-standard for fault tolerance in .NET
- **Serilog:** Best structured logging library for .NET
- **OpenTelemetry:** Cross-platform observability standard
- **Redis:** Essential for high-performance caching

---

### Testing (Backend)

| Technology                | Purpose              | Why                                        | License      | Epic   |
| ------------------------- | -------------------- | ------------------------------------------ | ------------ | ------ |
| **xUnit**                 | Unit testing         | Modern, extensible, parallel execution     | Apache 2.0   | Epic 5 |
| **Moq**                   | Mocking framework    | Fluent API, easy mocking                   | BSD-3-Clause | Epic 5 |
| **FluentAssertions**      | Assertion library    | Readable assertions, better error messages | Apache 2.0   | Epic 5 |
| **Testcontainers**        | Integration testing  | Real dependencies in Docker                | MIT          | Epic 5 |
| **WebApplicationFactory** | API testing          | In-memory API testing                      | MIT          | Epic 5 |
| **Bogus**                 | Test data generation | Realistic fake data                        | MIT          | Epic 5 |
| **Coverlet**              | Code coverage        | .NET code coverage                         | MIT          | Epic 5 |
| **ReportGenerator**       | Coverage reports     | HTML/XML coverage reports                  | Apache 2.0   | Epic 5 |

**Target:** >80% code coverage for business logic

---

### CI/CD Pipeline

| Technology                    | Purpose                | Why                                           | License/Cost | Epic   |
| ----------------------------- | ---------------------- | --------------------------------------------- | ------------ | ------ |
| **GitHub Actions**            | CI/CD automation       | Free for public repos, 2000 min/month private | Free tier    | Epic 6 |
| **Semantic Release**          | Automated versioning   | Conventional commits → versions               | MIT          | Epic 6 |
| **Docker Hub**                | Container registry     | 1 free private repo                           | Free tier    | Epic 6 |
| **GitHub Container Registry** | Container registry     | Free, integrated with GitHub                  | Free         | Epic 6 |
| **Trivy**                     | Vulnerability scanning | Container and dependency scanning             | Apache 2.0   | Epic 6 |
| **SonarQube**                 | Code quality           | Code smells, security, duplication            | LGPL/Free    | Epic 6 |
| **Codecov**                   | Coverage tracking      | Free for open source                          | Free tier    | Epic 6 |
| **Mend Bolt**                 | Dependency scanning    | Security vulnerabilities                      | Free tier    | Epic 6 |
| **Snyk**                      | Security scanning      | Alternative to Mend                           | Free tier    | Epic 6 |

**Pipeline Stages:**

1. **Build:** Compile all services
2. **Test:** Unit + integration tests
3. **Coverage:** Upload to Codecov
4. **Quality:** SonarQube analysis
5. **Security:** Trivy + Mend/Snyk scan
6. **Package:** Build Docker images
7. **Push:** Push to registry
8. **Deploy:** Deploy to staging (CD)

**Free Resources:**

- GitHub Actions: 2000 minutes/month (private), unlimited (public)
- SonarQube: Free community edition (self-hosted)
- Codecov: Free for open source
- Trivy: Completely free

---

### Kubernetes & Orchestration (📋 NEXT - Epic 3)

| Technology            | Purpose                 | Why                               | License/Cost | Status         |
| --------------------- | ----------------------- | --------------------------------- | ------------ | -------------- |
| **K3s**               | Kubernetes distribution | Lightweight, perfect for learning | Apache 2.0   | 📋 Next        |
| **Minikube**          | Local K8s cluster       | Development environment           | Apache 2.0   | 📋 Alternative |
| **kubectl**           | K8s CLI                 | Cluster management                | Apache 2.0   | 📋 Required    |
| **Helm**              | Package manager         | Templating, versioning, rollbacks | Apache 2.0   | 📋 Planned     |
| **NGINX Ingress**     | Ingress controller      | HTTP routing, load balancing      | Apache 2.0   | 📋 Planned     |
| **cert-manager**      | Certificate management  | Automatic TLS certificates        | Apache 2.0   | 📋 Planned     |
| **metrics-server**    | Resource metrics        | HPA, resource monitoring          | Apache 2.0   | 📋 Planned     |
| **Istio** (optional)  | Service mesh            | Advanced traffic management, mTLS | Apache 2.0   | 🧪 Optional    |
| **ArgoCD** (optional) | GitOps                  | Automated K8s deployments         | Apache 2.0   | 🧪 Optional    |

**Free K8s Options:**

- **Local:** K3s, Minikube, Kind (all free)
- **Cloud:**
  - Azure AKS: 1 free cluster (pay for VMs)
  - Google GKE Autopilot: $300 free credit
  - Oracle Cloud: Always free tier with K8s
  - Civo: $250 free credit

**Recommendation:** Start with K3s locally, then Oracle Cloud for production

---

### Observability & Monitoring

| Technology             | Purpose                    | Why                                  | License/Cost    | Epic   |
| ---------------------- | -------------------------- | ------------------------------------ | --------------- | ------ |
| **Prometheus**         | Metrics collection         | Industry standard, powerful queries  | Apache 2.0      | Epic 8 |
| **Grafana**            | Dashboards & visualization | Beautiful dashboards, alerting       | AGPL-3.0        | Epic 8 |
| **Loki**               | Log aggregation            | Prometheus-like logs, cost-effective | AGPL-3.0        | Epic 8 |
| **Promtail**           | Log shipping               | Collects logs for Loki               | AGPL-3.0        | Epic 8 |
| **Jaeger**             | Distributed tracing        | End-to-end request tracing           | Apache 2.0      | Epic 8 |
| **OpenTelemetry**      | Observability SDK          | Vendor-neutral instrumentation       | Apache 2.0      | Epic 8 |
| **Kiali** (with Istio) | Service mesh observability | Visualize service mesh               | Apache 2.0      | Epic 7 |
| **Seq** (alternative)  | Structured logging         | .NET-focused, free single-user       | Commercial/Free | Epic 8 |

**Stack Choice: PLG Stack (Prometheus + Loki + Grafana)**

- Completely free and open source
- Unified interface (Grafana)
- Scales from dev to production
- Industry standard

**Alternative: ELK Stack (Elasticsearch + Logstash + Kibana)**

- More heavy-weight
- Better for complex log queries
- Higher resource requirements

---

### Storage & Databases

| Technology                   | Purpose             | Why                         | License/Cost | Epic    |
| ---------------------------- | ------------------- | --------------------------- | ------------ | ------- |
| **SQL Server Express**       | Relational database | Current choice, free tier   | Free tier    | -       |
| **PostgreSQL** (alternative) | Relational database | More open, better for K8s   | PostgreSQL   | Future  |
| **Redis**                    | In-memory cache     | High-performance caching    | BSD-3-Clause | Epic 10 |
| **Elasticsearch**            | Search engine       | Full-text search, analytics | SSPL/Elastic | Epic 9  |
| **Azure Blob Storage**       | Object storage      | Image/file storage          | Pay-per-use  | Epic 1  |
| **MinIO** (alternative)      | Object storage      | S3-compatible, self-hosted  | AGPL-3.0     | Epic 1  |

**Database Strategy Evolution:**

- **Current:** SQL Server (separate DB per service)
- **Phase 2:** Add Redis for caching
- **Phase 3:** Add Elasticsearch for search
- **Phase 4:** Consider PostgreSQL migration for better K8s support

**Storage Strategy:**

- **Images:** MinIO (self-hosted) or Azure Blob (cloud)
- **Documents:** Same as images
- **Database Backups:** Volume snapshots + S3-compatible storage

---

### Security & Secrets Management

| Technology                        | Purpose                | Why                                | License/Cost | Epic    |
| --------------------------------- | ---------------------- | ---------------------------------- | ------------ | ------- |
| **HashiCorp Vault**               | Secrets management     | Industry standard, dynamic secrets | MPL-2.0      | Epic 10 |
| **Azure Key Vault** (alternative) | Secrets management     | Cloud-native, managed              | Pay-per-use  | Epic 10 |
| **Sealed Secrets**                | K8s secrets encryption | GitOps-friendly encrypted secrets  | Apache 2.0   | Epic 10 |
| **OWASP ZAP**                     | Security testing       | Automated security scanning        | Apache 2.0   | Epic 10 |
| **Trivy**                         | Vulnerability scanning | Container & dependency scanning    | Apache 2.0   | Epic 6  |

**Security Tools (All Free):**

- **OWASP Dependency-Check:** Dependency vulnerabilities
- **Trivy:** Multi-purpose security scanner
- **Mend Bolt:** Automated dependency updates
- **Snyk:** Alternative security scanner
- **SonarQube:** Security hotspots

---

## 💰 Cost Analysis

### Current Costs (MVP) = $0/month

- All technologies are free/open source
- Docker Desktop: Free for personal use
- GitHub: Free public repository
- SQL Server Express: Free (10GB limit per database)

### Future Costs (Full Roadmap)

#### Option 1: Completely Free (Self-Hosted)

**Total: $0/month**

- Local K3s cluster or Oracle Cloud Always Free
- Self-hosted SonarQube
- Self-hosted Grafana stack
- GitHub Actions (public repo)
- MinIO for object storage

**Requirements:**

- Own computer for K3s or Oracle Cloud account
- ~4GB RAM for local K8s
- ~20GB disk space

#### Option 2: Cloud-Enhanced (Minimal Cost)

**Total: ~$20-50/month**

- Azure AKS: $0 (cluster) + ~$30-50 (2 B2s VMs)
- Azure Blob Storage: ~$1-5/month
- GitHub Actions: Free (public) or $4/month (private)
- Everything else: Free/open source

#### Option 3: Fully Managed (Learning + Production)

**Total: ~$100-150/month**

- Managed K8s: ~$50-70/month
- Managed database: ~$20-30/month
- Object storage: ~$5-10/month
- Monitoring (Grafana Cloud): Free tier or $8/month
- CI/CD: Free tier
- Other tools: Free

### Cost Optimization Strategy

1. **Start:** Completely free (local development)
2. **Learn:** Use free cloud credits ($200-300 Azure/GCP)
3. **Deploy:** Oracle Cloud Always Free or minimal Azure
4. **Scale:** Gradually add paid services as needed

**Free Cloud Credits:**

- Azure: $200 for 30 days (new accounts)
- GCP: $300 for 90 days
- AWS: 12 months free tier
- Oracle: Always free tier (no expiry)

---

## 🎯 Technology Decisions & Rationale

### Why .NET 10?

✅ **Pros:**

- High performance (faster than Node.js, Java)
- Strong typing (C#)
- Excellent async/await support
- Built-in dependency injection
- Great tooling (Visual Studio, Rider)
- Cross-platform (Linux, Windows, macOS)
- Free and open source
- Strong community

❌ **Cons:**

- Larger learning curve than Node.js
- Heavier runtime than Node.js

**Decision:** Best for learning enterprise patterns and building scalable microservices.

---

### Why React 18?

✅ **Pros:**

- Most popular frontend framework (hiring market)
- Huge ecosystem
- Excellent documentation
- Great developer experience
- Concurrent rendering
- Strong community support

**Alternatives Considered:**

- **Vue 3:** Easier learning curve, but smaller job market
- **Angular:** More opinionated, steeper learning curve
- **Svelte:** Smaller bundle, but smaller ecosystem

**Decision:** React for maximum job market relevance and learning resources.

---

### Why YARP for API Gateway?

✅ **Pros:**

- Built by Microsoft for .NET
- High performance (uses Kestrel)
- Code-based configuration
- Built-in health checks
- Free and open source
- Load balancing support

**Alternatives Considered:**

- **Ocelot:** Older, less maintained
- **Kong:** More features, but heavier, complex setup
- **NGINX:** Lower level, requires Lua scripting
- **Traefik:** Good, but more K8s-focused

**Decision:** YARP for .NET-native solution with excellent performance.

---

### Why SQL Server?

✅ **Pros:**

- Familiar to many developers
- Excellent tooling (SSMS, Azure Data Studio)
- Strong .NET integration
- Free Express edition
- Good for learning SQL

**Alternatives Considered:**

- **PostgreSQL:** More open, better for K8s, no licensing concerns
- **MySQL:** Similar to PostgreSQL
- **MongoDB:** NoSQL, but not ideal for transactional data

**Decision:** SQL Server Express for now, consider PostgreSQL migration later for better cloud-native support.

---

### Why Kubernetes (K3s)?

✅ **Pros:**

- Industry standard for container orchestration
- Essential skill for DevOps
- Declarative configuration
- Self-healing
- Auto-scaling
- Service discovery
- Rolling updates

**Alternatives Considered:**

- **Docker Swarm:** Simpler, but less popular in industry
- **Nomad:** Good, but smaller ecosystem

**Decision:** K8s for maximum learning value and job market relevance. K3s for lightweight learning environment.

---

### Why Prometheus + Grafana + Loki?

✅ **Pros:**

- Industry standard observability stack
- Completely free and open source
- Unified interface (Grafana)
- Powerful query languages (PromQL, LogQL)
- Great K8s integration
- Active community

**Alternatives Considered:**

- **ELK Stack:** More complex, heavier
- **Datadog:** Excellent, but expensive
- **New Relic:** Good, but expensive

**Decision:** PLG stack for zero-cost, industry-standard observability.

---

## 📚 Learning Resources by Technology

### .NET & C#

- [Microsoft Learn - .NET](https://learn.microsoft.com/en-us/dotnet/)
- [.NET Microservices Architecture eBook](https://dotnet.microsoft.com/en-us/learn/aspnet/microservices-architecture)
- [Plural sight - .NET Courses](https://www.pluralsight.com/browse/software-development/dotnet)

### React

- [React Official Docs](https://react.dev/)
- [Frontend Masters - React Path](https://frontendmasters.com/learn/react/)
- [Epic React by Kent C. Dodds](https://epicreact.dev/)

### Kubernetes

- [Kubernetes Official Docs](https://kubernetes.io/docs/home/)
- [Kubernetes the Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way)
- [KodeKloud - Kubernetes Courses](https://kodekloud.com/)

### Observability

- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
- [Grafana Tutorials](https://grafana.com/tutorials/)
- [OpenTelemetry Docs](https://opentelemetry.io/docs/)

---

## 🔄 Migration Path

### Phase 1: MVP ✅ (Complete)

- Basic microservices
- Docker containerization
- Simple authentication
- Basic frontend

### Phase 2: Enhanced Features (Epics 1-3)

- Advanced product features
- Better order management
- Multiple payment methods

### Phase 3: Frontend Modernization (Epic 4)

- React Query, Zustand
- PWA support
- Accessibility
- Performance optimization

### Phase 4: Quality & Testing (Epic 5)

- Comprehensive testing
- > 80% code coverage
- E2E automation

### Phase 5: CI/CD (Epic 6)

- Automated pipelines
- Quality gates
- Automated versioning

### Phase 6: Cloud Native (Epic 7)

- Kubernetes deployment
- Helm charts
- Auto-scaling

### Phase 7: Observability (Epic 8)

- Prometheus + Grafana
- Distributed tracing
- Centralized logging

### Phase 8: Production Ready (Epics 9-10)

- Advanced features
- Security hardening
- Performance optimization

---

## 🎓 Skills You'll Master

By completing this tech stack implementation, you'll learn:

### Backend

- ✅ Microservices architecture
- ✅ RESTful API design
- ✅ Design patterns (10+ patterns)
- ✅ Entity Framework Core
- ✅ Authentication & Authorization (JWT)
- ✅ Service-to-service communication
- ✅ Database design (normalized schemas)
- ✅ Unit testing & integration testing
- ✅ Error handling & logging
- ✅ API documentation (Swagger)

### Frontend

- ✅ Modern React (hooks, context, custom hooks)
- ✅ State management (React Query, Zustand)
- ✅ Form management (React Hook Form)
- ✅ Routing (React Router)
- ✅ API integration (Axios, React Query)
- ✅ PWA development
- ✅ Accessibility (WCAG 2.1)
- ✅ Performance optimization
- ✅ Testing (Vitest, RTL, Playwright)
- ✅ Animation (Framer Motion)

### DevOps

- ✅ Docker & Docker Compose
- ✅ Kubernetes & Helm
- ✅ CI/CD (GitHub Actions)
- ✅ Infrastructure as Code
- ✅ GitOps (ArgoCD)
- ✅ Container security
- ✅ Automated testing in CI
- ✅ Semantic versioning

### Observability

- ✅ Prometheus (metrics)
- ✅ Grafana (dashboards)
- ✅ Loki (logging)
- ✅ Jaeger (tracing)
- ✅ OpenTelemetry
- ✅ Structured logging (Serilog)
- ✅ Alert management

### Security

- ✅ Authentication (JWT)
- ✅ Authorization (RBAC)
- ✅ Secrets management (Vault)
- ✅ Vulnerability scanning
- ✅ Security headers
- ✅ Input validation
- ✅ Penetration testing (OWASP ZAP)

---

## 📊 Technology Maturity Matrix

| Technology     | Maturity   | Learning Curve | Job Market | Free Option |
| -------------- | ---------- | -------------- | ---------- | ----------- |
| .NET 10        | ⭐⭐⭐⭐⭐ | Medium         | ⭐⭐⭐⭐⭐ | ✅ Yes      |
| React 18       | ⭐⭐⭐⭐⭐ | Medium         | ⭐⭐⭐⭐⭐ | ✅ Yes      |
| Docker         | ⭐⭐⭐⭐⭐ | Low-Medium     | ⭐⭐⭐⭐⭐ | ✅ Yes      |
| Kubernetes     | ⭐⭐⭐⭐⭐ | High           | ⭐⭐⭐⭐⭐ | ✅ Yes      |
| YARP           | ⭐⭐⭐⭐   | Low            | ⭐⭐⭐     | ✅ Yes      |
| SQL Server     | ⭐⭐⭐⭐⭐ | Medium         | ⭐⭐⭐⭐   | ⚠️ Express  |
| Redis          | ⭐⭐⭐⭐⭐ | Low            | ⭐⭐⭐⭐⭐ | ✅ Yes      |
| Prometheus     | ⭐⭐⭐⭐⭐ | Medium         | ⭐⭐⭐⭐   | ✅ Yes      |
| Grafana        | ⭐⭐⭐⭐⭐ | Low-Medium     | ⭐⭐⭐⭐   | ✅ Yes      |
| GitHub Actions | ⭐⭐⭐⭐⭐ | Low-Medium     | ⭐⭐⭐⭐⭐ | ✅ Yes      |
| Helm           | ⭐⭐⭐⭐   | Medium         | ⭐⭐⭐⭐   | ✅ Yes      |

---

**FreshHarvest Market's tech stack is designed to maximize learning while minimizing costs, using industry-standard, in-demand technologies!** 🌱🚀

**Total Investment:** $0 - $50/month depending on cloud choice  
**Job Market Value:** Very High (all in-demand technologies)  
**Learning Time:** 7-10 months for complete mastery  
**Domain:** Organic Food E-Commerce with Certification Tracking
