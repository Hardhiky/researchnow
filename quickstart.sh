#!/bin/bash

# ResearchNow Quick Start Script
# This script helps you get ResearchNow up and running quickly

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  ${1}${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    local missing=0

    # Check Docker
    if command_exists docker; then
        print_success "Docker is installed ($(docker --version))"
    else
        print_error "Docker is not installed"
        print_info "Install from: https://docs.docker.com/get-docker/"
        missing=1
    fi

    # Check Docker Compose
    if command_exists docker-compose; then
        print_success "Docker Compose is installed ($(docker-compose --version))"
    else
        print_error "Docker Compose is not installed"
        print_info "Install from: https://docs.docker.com/compose/install/"
        missing=1
    fi

    # Check Git
    if command_exists git; then
        print_success "Git is installed ($(git --version))"
    else
        print_error "Git is not installed"
        missing=1
    fi

    if [ $missing -eq 1 ]; then
        print_error "Please install missing prerequisites and try again"
        exit 1
    fi

    print_success "All prerequisites are installed!"
}

# Create environment file
create_env_file() {
    print_header "Setting Up Environment"

    if [ -f .env ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
            return
        fi
    fi

    if [ ! -f .env.example ]; then
        print_error ".env.example not found!"
        exit 1
    fi

    print_info "Copying .env.example to .env..."
    cp .env.example .env

    # Generate secure passwords
    print_info "Generating secure passwords..."

    if command_exists openssl; then
        POSTGRES_PWD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        REDIS_PWD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        RABBITMQ_PWD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        MINIO_PWD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)

        # Update .env file
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PWD/" .env
            sed -i '' "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PWD/" .env
            sed -i '' "s/RABBITMQ_PASSWORD=.*/RABBITMQ_PASSWORD=$RABBITMQ_PWD/" .env
            sed -i '' "s/MINIO_ROOT_PASSWORD=.*/MINIO_ROOT_PASSWORD=$MINIO_PWD/" .env
            sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        else
            # Linux
            sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PWD/" .env
            sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PWD/" .env
            sed -i "s/RABBITMQ_PASSWORD=.*/RABBITMQ_PASSWORD=$RABBITMQ_PWD/" .env
            sed -i "s/MINIO_ROOT_PASSWORD=.*/MINIO_ROOT_PASSWORD=$MINIO_PWD/" .env
            sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        fi

        print_success "Secure passwords generated"
    else
        print_warning "OpenSSL not found, using default passwords"
        print_warning "Please update passwords in .env for production!"
    fi

    # Ask for API keys
    print_info ""
    print_info "Optional: Enter API keys (press Enter to skip)"
    print_info "You can add these later in the .env file"
    echo ""

    read -p "CORE API Key (from core.ac.uk): " CORE_KEY
    read -p "Your email (for PubMed/Crossref/OpenAlex): " USER_EMAIL

    if [ ! -z "$CORE_KEY" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/CORE_API_KEY=.*/CORE_API_KEY=$CORE_KEY/" .env
        else
            sed -i "s/CORE_API_KEY=.*/CORE_API_KEY=$CORE_KEY/" .env
        fi
    fi

    if [ ! -z "$USER_EMAIL" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/PUBMED_EMAIL=.*/PUBMED_EMAIL=$USER_EMAIL/" .env
            sed -i '' "s/CROSSREF_EMAIL=.*/CROSSREF_EMAIL=$USER_EMAIL/" .env
            sed -i '' "s/OPENALEX_EMAIL=.*/OPENALEX_EMAIL=$USER_EMAIL/" .env
        else
            sed -i "s/PUBMED_EMAIL=.*/PUBMED_EMAIL=$USER_EMAIL/" .env
            sed -i "s/CROSSREF_EMAIL=.*/CROSSREF_EMAIL=$USER_EMAIL/" .env
            sed -i "s/OPENALEX_EMAIL=.*/OPENALEX_EMAIL=$USER_EMAIL/" .env
        fi
    fi

    print_success ".env file created successfully"
}

# Start services
start_services() {
    print_header "Starting Services"

    print_info "Pulling Docker images (this may take a while)..."
    docker-compose pull

    print_info "Starting all services..."
    docker-compose up -d

    print_success "Services started!"

    # Wait for services to be ready
    print_info "Waiting for services to be ready..."
    sleep 10

    # Check service health
    print_info "Checking service health..."

    services=("postgres" "redis" "rabbitmq" "qdrant" "minio")
    for service in "${services[@]}"; do
        if docker-compose ps | grep -q "$service.*Up"; then
            print_success "$service is running"
        else
            print_warning "$service may not be ready yet"
        fi
    done
}

# Initialize database
init_database() {
    print_header "Initializing Database"

    print_info "Running database migrations..."
    docker-compose exec -T backend alembic upgrade head || {
        print_warning "Migrations failed, retrying in 10 seconds..."
        sleep 10
        docker-compose exec -T backend alembic upgrade head
    }

    print_success "Database initialized"
}

# Pull AI model
pull_ai_model() {
    print_header "Setting Up AI Model"

    print_info "Available models:"
    echo "  1. llama2:7b  (4GB RAM, Fast, Good quality)"
    echo "  2. llama2:13b (8GB RAM, Balanced)"
    echo "  3. llama2:70b (40GB RAM, Best quality, Requires GPU)"
    echo "  4. Skip for now"
    echo ""

    read -p "Choose a model (1-4): " model_choice

    case $model_choice in
        1)
            MODEL="llama2:7b"
            ;;
        2)
            MODEL="llama2:13b"
            ;;
        3)
            MODEL="llama2:70b"
            ;;
        4)
            print_info "Skipping AI model setup"
            print_warning "You'll need to set this up manually later"
            return
            ;;
        *)
            print_warning "Invalid choice, defaulting to llama2:7b"
            MODEL="llama2:7b"
            ;;
    esac

    print_info "Pulling $MODEL (this will take a while)..."
    docker-compose exec ollama ollama pull $MODEL

    print_success "AI model ready: $MODEL"
}

# Display access information
show_access_info() {
    print_header "🎉 Installation Complete!"

    echo ""
    print_success "ResearchNow is now running!"
    echo ""
    echo -e "${GREEN}Access the application:${NC}"
    echo "  🌐 Web App:           http://localhost:3000"
    echo "  📚 API Documentation: http://localhost:8000/api/docs"
    echo "  🔧 API Base URL:      http://localhost:8000/api/v1"
    echo ""
    echo -e "${BLUE}Service Management UIs:${NC}"
    echo "  🐰 RabbitMQ:          http://localhost:15672 (guest/guest)"
    echo "  📦 MinIO Console:     http://localhost:9001 (minioadmin/minioadmin123)"
    echo ""
    echo -e "${YELLOW}Useful Commands:${NC}"
    echo "  View logs:            docker-compose logs -f"
    echo "  Stop services:        docker-compose stop"
    echo "  Restart services:     docker-compose restart"
    echo "  Remove everything:    docker-compose down -v"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Open http://localhost:3000 in your browser"
    echo "  2. Try searching for papers"
    echo "  3. Generate AI summaries"
    echo "  4. Check the documentation in ./docs/"
    echo ""
    echo -e "${GREEN}For production deployment, see: docs/SETUP_GUIDE.md${NC}"
    echo ""
}

# Cleanup on error
cleanup_on_error() {
    print_error "Setup failed!"
    print_info "Cleaning up..."
    docker-compose down
    print_info "Check the error messages above and try again"
    exit 1
}

# Main setup function
main() {
    # Trap errors
    trap cleanup_on_error ERR

    clear
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                ║${NC}"
    echo -e "${BLUE}║         ${GREEN}ResearchNow Quick Start${BLUE}              ║${NC}"
    echo -e "${BLUE}║                                                ║${NC}"
    echo -e "${BLUE}║   AI-Powered Research Paper Summarization     ║${NC}"
    echo -e "${BLUE}║                                                ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check prerequisites
    check_prerequisites

    # Create environment file
    create_env_file

    # Start services
    start_services

    # Initialize database
    init_database

    # Pull AI model
    pull_ai_model

    # Show access information
    show_access_info
}

# Run main function
main

exit 0
