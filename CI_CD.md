# CIE CI/CD Pipeline Documentation

## Overview

This document describes the comprehensive CI/CD pipeline for the CIE (Optimization & Evaluation) project. The pipeline includes code quality checks, testing, security scanning, building, documentation generation, and deployment using both Dagger and traditional GitHub Actions.

## Pipeline Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Code Quality   │    │     Testing     │    │  Security Scan  │
│  (Lint/Format)  │───▶│  (Unit/Integ)   │───▶│  (Bandit/Safety)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Build       │    │   Documentation │    │   Deployment    │
│  (Package/Img)  │───▶│   (pdoc/API)    │───▶│ (Dev/Prod/Doc)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Components

### 1. Dagger CI/CD (`ci/main.py`)

A modern, containerized CI/CD pipeline using Dagger for reproducible builds.

#### Features:
- **Containerized**: All steps run in isolated containers
- **Reproducible**: Consistent environment across runs
- **Parallel**: Optimized for parallel execution
- **Extensible**: Easy to add new pipeline stages

#### Pipeline Stages:

1. **Quality Gate** (`quality_gate()`)
   - Code linting with ruff
   - Code formatting with black
   - Type checking with mypy

2. **Testing** (`test()`)
   - Unit tests with pytest
   - Integration tests
   - Coverage reporting

3. **Security Scanning** (`security_scan()`)
   - Bandit for security vulnerabilities
   - Safety for dependency vulnerabilities

4. **Building** (`build()`)
   - Python package building
   - Docker image creation

5. **Documentation** (`docs()`)
   - API documentation generation
   - Code documentation

6. **Deployment** (`deploy_dev()`, `deploy_prod()`)
   - Development environment deployment
   - Production container deployment

#### Usage:

```bash
# Install Dagger
curl -L https://dl.dagger.io/dagger/install.sh | sh

# Run complete CI pipeline
dagger call ci --source=.

# Run specific stages
dagger call quality-gate --source=.
dagger call test --coverage=true --source=.
dagger call build --source=.
```

### 2. GitHub Actions Workflows

#### Simple CI (`.github/workflows/simple-ci.yml`)
Traditional GitHub Actions workflow for basic CI needs.

**Jobs:**
- **Quality Checks**: Linting, formatting, type checking
- **Tests**: Unit and integration tests with coverage
- **Build**: Package building and testing
- **Security**: Vulnerability scanning
- **Documentation**: API docs generation
- **Integration**: CLI functionality testing

#### Advanced CI with Dagger (`.github/workflows/ci.yml`)
Full-featured workflow using Dagger for complex CI/CD needs.

**Jobs:**
- **Quality Checks**: Comprehensive code quality validation
- **Tests**: Multi-environment testing
- **Security**: Advanced security scanning
- **Build**: Multi-platform builds
- **Documentation**: Rich documentation generation
- **Deployment**: Multi-environment deployment
- **Monitoring**: Integration with monitoring systems

### 3. Docker Support

#### Multi-stage Dockerfile

**Stages:**
1. **Builder**: Compilation and package building
2. **Runtime**: Minimal production image
3. **Development**: Full development environment
4. **Production**: Optimized production image

#### Docker Compose

**Services:**
- `cie-dev`: Development environment
- `cie-prod`: Production deployment
- `cie-test`: Testing environment
- `cie-docs`: Documentation server
- `postgres`: Database (optional)
- `redis`: Cache (optional)
- `prometheus`: Metrics collection
- `grafana`: Visualization

## Environment Configuration

### Required Environment Variables

```bash
# AI Model API Keys
KIMI_API_KEY=your-kimi-api-key
OPENAI_API_KEY=your-openai-api-key

# Database (optional)
POSTGRES_PASSWORD=secure-password

# Monitoring (optional)
GRAFANA_PASSWORD=admin-password
```

### Optional Configuration

```bash
# Container Registry
REGISTRY=ghcr.io
IMAGE_TAG=latest

# CI/CD Settings
DAGGER_VERSION=0.9.3
PYTHON_VERSION=3.13
```

## Monitoring and Observability

### Metrics Collection

**Prometheus Metrics:**
- Application performance metrics
- Optimization progress tracking
- Error rates and success rates
- Resource utilization

**Custom Metrics:**
```python
# Example metric collection
cie_iterations_total  # Total optimization iterations
cie_best_score        # Current best score
cie_error_rate        # Error rate percentage
cie_latency_p95       # 95th percentile latency
cie_memory_usage      # Memory utilization
cie_cpu_usage         # CPU utilization
```

### Alerting

**Alert Rules:**
- High error rate (> 5%)
- Low success rate (< 80%)
- High latency (> 5000ms)
- High resource usage (> 90%)
- Stagnant optimization (no progress for 1 hour)

### Dashboards

**Grafana Dashboards:**
- System performance overview
- Optimization progress tracking
- Error analysis and trends
- Resource utilization monitoring

## Deployment Strategies

### Development Deployment

```bash
# Using Docker Compose
docker-compose up cie-dev

# Using Dagger
dagger call deploy-dev --source=.
```

### Production Deployment

```bash
# Using Docker Compose
docker-compose up cie-prod

# Using Dagger with registry
dagger call deploy-prod --source=. --registry=ghcr.io --image-tag=v1.0.0
```

### Documentation Deployment

```bash
# Start documentation server
docker-compose up cie-docs

# Access at http://localhost:8082
```

## Security Considerations

### Code Security
- **Bandit**: Python security vulnerability scanning
- **Safety**: Dependency vulnerability checking
- **Secret Scanning**: Prevent credential leaks

### Container Security
- **Non-root user**: Containers run as unprivileged user
- **Minimal base images**: Slim Python images
- **Security updates**: Regular base image updates

### Access Control
- **API Keys**: Secure storage and rotation
- **Container Registry**: Private registry with access control
- **Environment Isolation**: Separate dev/staging/prod environments

## Performance Optimization

### Build Performance
- **Layer Caching**: Optimized Docker layer ordering
- **Parallel Execution**: Parallel test and build stages
- **Incremental Builds**: Only rebuild changed components

### Runtime Performance
- **Resource Limits**: CPU and memory limits
- **Health Checks**: Container health monitoring
- **Auto-scaling**: Horizontal scaling support

## Troubleshooting

### Common Issues

1. **Dagger Installation**
   ```bash
   # Install Dagger
   curl -L https://dl.dagger.io/dagger/install.sh | sh
   sudo mv dagger /usr/local/bin/
   ```

2. **Container Build Failures**
   ```bash
   # Check Docker daemon
   docker info
   
   # Clean build cache
   docker system prune -a
   ```

3. **Test Failures**
   ```bash
   # Run tests locally
   pytest tests/ -v
   
   # Check test coverage
   pytest --cov=cie --cov-report=html
   ```

4. **API Key Issues**
   ```bash
   # Verify API keys
   echo $KIMI_API_KEY | wc -c  # Should show length > 0
   echo $OPENAI_API_KEY | wc -c  # Should show length > 0
   ```

### Debug Mode

```bash
# Enable debug logging
export DAGGER_LOG_LEVEL=debug

# Run with verbose output
dagger call ci --source=. --log-level=debug
```

## Maintenance

### Regular Tasks
- **Dependency Updates**: Monthly dependency scanning and updates
- **Security Patches**: Apply security patches promptly
- **Performance Review**: Quarterly performance analysis
- **Documentation Updates**: Keep documentation current

### Monitoring
- **Pipeline Health**: Monitor CI/CD pipeline success rates
- **Build Times**: Track and optimize build performance
- **Resource Usage**: Monitor container resource consumption
- **Error Rates**: Track application error rates

## Future Enhancements

### Planned Features
- **Web Interface**: REST API and web dashboard
- **Advanced Analytics**: Machine learning for optimization insights
- **Distributed Optimization**: Multi-node optimization support
- **Advanced Monitoring**: APM integration and distributed tracing

### Scaling Considerations
- **Multi-region Deployment**: Geographic distribution
- **Load Balancing**: High availability setup
- **Database Scaling**: Read replicas and sharding
- **Cache Optimization**: Redis clustering and optimization

This CI/CD pipeline provides a robust, scalable, and maintainable foundation for the CIE project with comprehensive testing, security, monitoring, and deployment capabilities.