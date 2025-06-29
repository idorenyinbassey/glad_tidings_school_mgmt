#!/bin/bash

# Docker Deployment Script for Glad Tidings School Management System
# This script helps deploy the application using Docker

set -e

echo "🐳 Docker Deployment Script for Glad Tidings School Management System"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Function to display menu
show_menu() {
    echo -e "${BLUE}Please select an option:${NC}"
    echo "1. 🔧 Development mode (SQLite)"
    echo "2. 🚀 Production mode (PostgreSQL + Redis + Nginx)"
    echo "3. 🏗️  Build only"
    echo "4. 🛑 Stop all services"
    echo "5. 🗑️  Clean up (remove containers and volumes)"
    echo "6. 📋 View logs"
    echo "7. ❓ Help"
    echo "8. 🚪 Exit"
}

# Function for development deployment
deploy_dev() {
    echo -e "${YELLOW}🔧 Starting development environment...${NC}"
    docker-compose -f docker-compose.dev.yml up --build -d
    echo -e "${GREEN}✅ Development environment started!${NC}"
    echo -e "${BLUE}🌐 Access your application at: http://localhost:8000${NC}"
}

# Function for production deployment
deploy_prod() {
    echo -e "${YELLOW}🚀 Starting production environment...${NC}"
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
        cp .env.docker .env
        echo -e "${RED}⚠️  Please edit the .env file with your production values before continuing!${NC}"
        echo -e "${BLUE}📝 Required: SECRET_KEY, DB_PASSWORD, EMAIL settings, ALLOWED_HOSTS${NC}"
        read -p "Press Enter after editing .env file..."
    fi
    
    docker-compose up --build -d
    echo -e "${GREEN}✅ Production environment started!${NC}"
    echo -e "${BLUE}🌐 Access your application at: http://localhost${NC}"
    echo -e "${BLUE}🌐 Admin interface at: http://localhost/admin${NC}"
}

# Function to build only
build_only() {
    echo -e "${YELLOW}🏗️  Building Docker images...${NC}"
    docker-compose build
    echo -e "${GREEN}✅ Build completed!${NC}"
}

# Function to stop services
stop_services() {
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    echo -e "${GREEN}✅ All services stopped!${NC}"
}

# Function to clean up
cleanup() {
    echo -e "${RED}🗑️  This will remove all containers, images, and volumes. Are you sure? (y/N)${NC}"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🧹 Cleaning up...${NC}"
        docker-compose down -v --rmi all
        docker-compose -f docker-compose.dev.yml down -v --rmi all
        docker system prune -f
        echo -e "${GREEN}✅ Cleanup completed!${NC}"
    else
        echo -e "${BLUE}ℹ️  Cleanup cancelled.${NC}"
    fi
}

# Function to view logs
view_logs() {
    echo -e "${BLUE}📋 Select which logs to view:${NC}"
    echo "1. All services"
    echo "2. Web application only"
    echo "3. Database only"
    echo "4. Nginx only"
    read -p "Enter your choice (1-4): " log_choice
    
    case $log_choice in
        1) docker-compose logs -f ;;
        2) docker-compose logs -f web ;;
        3) docker-compose logs -f db ;;
        4) docker-compose logs -f nginx ;;
        *) echo -e "${RED}❌ Invalid choice${NC}" ;;
    esac
}

# Function to show help
show_help() {
    echo -e "${BLUE}📖 Help Information:${NC}"
    echo
    echo -e "${YELLOW}Development Mode:${NC}"
    echo "  • Uses SQLite database"
    echo "  • Debug mode enabled"
    echo "  • Hot reloading"
    echo "  • Access: http://localhost:8000"
    echo
    echo -e "${YELLOW}Production Mode:${NC}"
    echo "  • Uses PostgreSQL database"
    echo "  • Redis for caching"
    echo "  • Nginx reverse proxy"
    echo "  • Production optimizations"
    echo "  • Access: http://localhost"
    echo
    echo -e "${YELLOW}Requirements:${NC}"
    echo "  • Docker installed"
    echo "  • Docker Compose installed"
    echo "  • .env file configured (for production)"
    echo
    echo -e "${YELLOW}Useful Docker Commands:${NC}"
    echo "  • docker-compose ps          - Show running containers"
    echo "  • docker-compose exec web bash - Access web container shell"
    echo "  • docker-compose restart web - Restart web service"
    echo
}

# Main script logic
while true; do
    echo
    show_menu
    echo
    read -p "Enter your choice (1-8): " choice
    echo
    
    case $choice in
        1) deploy_dev ;;
        2) deploy_prod ;;
        3) build_only ;;
        4) stop_services ;;
        5) cleanup ;;
        6) view_logs ;;
        7) show_help ;;
        8) 
            echo -e "${GREEN}👋 Goodbye!${NC}"
            exit 0 
            ;;
        *)
            echo -e "${RED}❌ Invalid choice. Please select 1-8.${NC}"
            ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
done
