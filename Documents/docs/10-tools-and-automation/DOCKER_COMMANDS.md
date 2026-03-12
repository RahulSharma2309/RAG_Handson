# Docker Quick Reference

> **Quick commands for local development with Docker Compose**

---

## 🚀 Recommended: VS Code Tasks

**Easiest way to run everything:**

1. Press `Ctrl+Shift+P` in VS Code
2. Type "Tasks: Run Task"
3. Select "Docker: Build & Start All Services"

This automatically:
1. Disables BuildKit (fixes ordering issues)
2. Cleans existing containers
3. Builds all services
4. Starts all services

---

## 🛠️ Manual Commands

### Build All Services
```powershell
cd infra
$env:DOCKER_BUILDKIT=0
docker-compose build
```

### Start All Services
```powershell
docker-compose up -d
```

### Check Service Status
```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service
```

### Stop All Services
```powershell
docker-compose down
```

### Clean Everything (Fresh Start)
```powershell
docker-compose down -v
docker system prune -af --volumes
```

---

## 🌐 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React UI |
| API Gateway | http://localhost:5000 | Main API entry |
| Auth Service | http://localhost:5001/swagger | Auth API docs |
| Product Service | http://localhost:5002/swagger | Product API docs |
| Payment Service | http://localhost:5003/swagger | Payment API docs |
| Order Service | http://localhost:5004/swagger | Order API docs |
| User Service | http://localhost:5005/swagger | User API docs |

---

## 🧪 Testing

### Health Check All Services
```powershell
curl http://localhost:5001/api/health
curl http://localhost:5002/api/health
curl http://localhost:5003/api/health
curl http://localhost:5004/api/health
curl http://localhost:5005/api/health
```

### Test Authentication Flow
1. Go to http://localhost:5001/swagger
2. Use POST `/api/auth/register` to create account
3. Use POST `/api/auth/login` to get JWT token
4. Copy token and use "Authorize" button at top

---

## ⚠️ Troubleshooting

### BuildKit "changes out of order" Error
**Solution:** Always set `$env:DOCKER_BUILDKIT=0` before building

### Port Already in Use
```powershell
# Find process using port
netstat -ano | findstr :5001

# Kill process
taskkill /PID <process_id> /F
```

### Service Unhealthy
```powershell
# Check logs
docker logs auth-service

# Restart service
docker-compose restart auth-service
```

### Database Issues
```powershell
# Check SQL Server
docker logs infra-mssql-1

# Restart SQL Server
docker-compose restart mssql
```

---

## 📝 Important Notes

- **BuildKit must be disabled** for builds to work correctly
- Wait 30-60 seconds after `docker-compose up -d` for services to be fully healthy
- First build takes 5-10 minutes, subsequent builds are faster (cached layers)
- All services use SQL Server running in Docker
- Platform library (`Ep.Platform`) is referenced directly via `ProjectReference`

---

## 🔗 Related Documentation

- [Dockerfile Explained](./DOCKERFILE_EXPLAINED.md) - Understanding Docker build process
- [Setup Guide](../../SETUP_GUIDE.md) - Complete setup instructions
- [CI/CD Documentation](../6-ci-cd/) - Automated builds and deployments

---

**For automated CI/CD builds, see:** [`docs/6-ci-cd/`](../6-ci-cd/)
