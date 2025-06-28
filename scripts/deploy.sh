#!/bin/bash
"""
RealtyScanner Production Deployment Script
Epic 5.1: Automated deployment for production environments
"""

set -e  # Exit on any error

# Configuration
PROJECT_NAME="realtyscanner"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        warning ".env file not found. Creating from template..."
        cp .env.example .env
        warning "Please edit .env file with your configuration before continuing."
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Function to validate environment variables
validate_environment() {
    log "Validating environment variables..."
    
    # Load .env file
    source "$ENV_FILE"
    
    # Check critical environment variables
    REQUIRED_VARS=(
        "SECRET_KEY"
        "TELEGRAM_BOT_TOKEN"
        "MONGO_ROOT_PASSWORD"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    success "Environment validation passed"
}

# Function to build Docker images
build_images() {
    log "Building Docker images..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    success "Docker images built successfully"
}

# Function to start services
start_services() {
    log "Starting services..."
    
    # Start database services first
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d mongodb redis
    
    # Wait for databases to be ready
    log "Waiting for databases to be ready..."
    sleep 10
    
    # Start application services
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    success "All services started successfully"
}

# Function to check service health
check_health() {
    log "Checking service health..."
    
    # Wait for services to start
    sleep 30
    
    # Check web app health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Web application is healthy"
    else
        error "Web application health check failed"
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs web-app
    fi
    
    # Check database connection
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        success "MongoDB is healthy"
    else
        error "MongoDB health check failed"
    fi
}

# Function to show deployment status
show_status() {
    log "Deployment Status:"
    echo ""
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    echo ""
    log "Application URLs:"
    echo "  🌐 Web Dashboard: http://localhost:8000"
    echo "  📊 Grafana: http://localhost:3000 (admin/admin)"
    echo "  📈 Prometheus: http://localhost:9090"
    echo ""
    log "To view logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f [service-name]"
    log "To stop: docker-compose -f $DOCKER_COMPOSE_FILE down"
}

# Function to setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Create config directories if they don't exist
    mkdir -p config/{grafana,prometheus}
    
    # Create basic Prometheus config if it doesn't exist
    if [ ! -f "config/prometheus.yml" ]; then
        cat > config/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'realtyscanner-web'
    static_configs:
      - targets: ['web-app:8000']
  
  - job_name: 'realtyscanner-bot'
    static_configs:
      - targets: ['telegram-bot:8001']
EOF
    fi
    
    success "Monitoring setup complete"
}

# Function to create nginx config
setup_nginx() {
    log "Setting up Nginx configuration..."
    
    mkdir -p config
    
    if [ ! -f "config/nginx.conf" ]; then
        cat > config/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream web_app {
        server web-app:8000;
    }
    
    upstream telegram_bot {
        server telegram-bot:8001;
    }
    
    server {
        listen 80;
        server_name _;
        
        location / {
            proxy_pass http://web_app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        location /bot {
            proxy_pass http://telegram_bot;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        }
        
        location /health {
            proxy_pass http://web_app/health;
        }
    }
}
EOF
    fi
    
    success "Nginx configuration created"
}

# Main deployment function
deploy() {
    echo "🏠 RealtyScanner Agent - Production Deployment"
    echo "=============================================="
    echo ""
    
    check_prerequisites
    validate_environment
    setup_monitoring
    setup_nginx
    build_images
    start_services
    check_health
    show_status
    
    echo ""
    success "🎉 Deployment completed successfully!"
    echo ""
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "stop")
        log "Stopping services..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        success "Services stopped"
        ;;
    "restart")
        log "Restarting services..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        sleep 5
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
        success "Services restarted"
        ;;
    "logs")
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
        ;;
    "status")
        show_status
        ;;
    "clean")
        log "Cleaning up..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down -v
        docker system prune -f
        success "Cleanup completed"
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|clean}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Full deployment (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - Show logs from all services"
        echo "  status  - Show deployment status"
        echo "  clean   - Stop services and clean up volumes"
        ;;
esac
