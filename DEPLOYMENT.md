# VirtualPackaging Deployment Guide

This document provides comprehensive instructions for deploying the VirtualPackaging system in various environments, from development to production.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Development Environment Setup](#development-environment-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Security Considerations](#security-considerations)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 8GB minimum (16GB+ recommended for production)
- **Storage**: 20GB available space (100GB+ for production with data storage)
- **GPU**: CUDA-compatible GPU recommended for 3D processing and reconstruction
- **Operating System**: Ubuntu 20.04+, Windows 10/11, macOS 12+
- **Database**: MongoDB 5.0+ or PostgreSQL 13+

### Software Dependencies

- Python 3.10+
- Node.js 18+
- Redis 6+ (for caching and queue management)
- CUDA 11.4+ (for GPU acceleration)

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/JJshome/VirtualPackaging.git
cd VirtualPackaging
```

### 2. Backend Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with appropriate settings

# Initialize the database
python -m core.scripts.init_db
```

### 3. Frontend Setup

```bash
cd web/frontend
npm install

# Create frontend environment file
cp .env.example .env.local
# Edit .env.local with appropriate settings, including API URL
```

### 4. Start Development Servers

```bash
# Terminal 1: Start backend server
cd /path/to/VirtualPackaging
source venv/bin/activate
python -m web.api.main

# Terminal 2: Start frontend development server
cd /path/to/VirtualPackaging/web/frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Production Deployment

### Preparing for Production

1. Update the `.env` file with production settings
2. Build the frontend for production

```bash
cd web/frontend
npm run build
```

### Option 1: Traditional Server Deployment

#### Backend Deployment

1. Set up a production-ready web server:

```bash
# Install Gunicorn
pip install gunicorn

# Start the backend with Gunicorn
gunicorn web.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. Configure Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name yourserver.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Set up a process manager like Supervisor:

```ini
[program:virtualpackaging]
command=/path/to/venv/bin/gunicorn web.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
directory=/path/to/VirtualPackaging
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```

### Option 2: Containerized Deployment

See the [Docker Deployment](#docker-deployment) section below.

## Docker Deployment

### Building Docker Images

The repository includes Dockerfiles for both backend and frontend components.

```bash
# Build backend image
docker build -t virtualpackaging-backend -f docker/backend.Dockerfile .

# Build frontend image
docker build -t virtualpackaging-frontend -f docker/frontend.Dockerfile .
```

### Running with Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  backend:
    image: virtualpackaging-backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - data-volume:/app/data
    depends_on:
      - mongodb
      - redis

  frontend:
    image: virtualpackaging-frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  mongodb:
    image: mongo:5.0
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"

  redis:
    image: redis:6.2
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"

volumes:
  data-volume:
  mongo-data:
  redis-data:
```

Start the services:

```bash
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment

1. Set up an AWS account if you don't have one
2. Create an EC2 instance (t3.large or better recommended)
3. Configure security groups to allow ports 80, 443, and 22
4. Install Docker and Docker Compose on the instance
5. Clone the repository and follow the Docker Deployment instructions

For more advanced setups:
- Use AWS ECS/EKS for container orchestration
- Use RDS for PostgreSQL or DocumentDB for MongoDB
- Use ElastiCache for Redis
- Configure S3 for model and file storage
- Set up CloudFront for content delivery

### Azure Deployment

1. Create an Azure Container Instances group
2. Deploy the backend, frontend, and database containers
3. Set up networking and environment variables

For more advanced setups:
- Use Azure Kubernetes Service (AKS)
- Use Azure Cosmos DB for MongoDB
- Use Azure Cache for Redis
- Set up Azure CDN for content delivery

## Security Considerations

### API Security

1. Implement proper authentication and authorization:
   - JWT-based authentication for API access
   - Role-based access control for different operations

2. Secure API endpoints:
   - Input validation on all endpoints
   - Rate limiting to prevent abuse
   - HTTPS enforcement for all traffic

### Data Security

1. Sensitive data handling:
   - Encrypt sensitive data at rest
   - Use proper access controls for uploaded files
   - Implement backup and recovery procedures

2. Database security:
   - Restrict database access
   - Use strong passwords and authentication
   - Regular security updates

## Monitoring and Maintenance

### Monitoring

1. Set up logging:
   - Configure structured logging in the application
   - Use a log aggregation service like ELK Stack or Datadog

2. Performance monitoring:
   - Track API response times
   - Monitor memory and CPU usage
   - Set up alerts for abnormal conditions

### Maintenance

1. Regular updates:
   - Schedule regular dependency updates
   - Plan for version migrations

2. Backup strategy:
   - Regular database backups
   - Store model data with versioning
   - Test restore procedures periodically

## Troubleshooting

### Common Issues

1. **3D Model Processing Issues**
   - Check GPU availability and CUDA configuration
   - Verify image quality and quantity are sufficient
   - Check available disk space for temporary processing files

2. **LLM Integration Problems**
   - Confirm API keys are correctly configured
   - Check network connectivity to LLM provider
   - Verify rate limits haven't been exceeded

3. **Performance Issues**
   - Monitor resource usage (CPU, memory, disk I/O)
   - Check database query performance
   - Review concurrent user limits

### Getting Help

If you encounter issues not covered in this guide:

- Check the [GitHub Issues](https://github.com/JJshome/VirtualPackaging/issues) for similar problems
- Join the community discussion on [Discord](https://discord.gg/virtualpackaging)
- Contact the development team at support@virtualpackaging.example.com

---

This deployment guide covers the basic and advanced deployment scenarios for VirtualPackaging. For specific customizations or enterprise deployments, please contact the development team for additional support.