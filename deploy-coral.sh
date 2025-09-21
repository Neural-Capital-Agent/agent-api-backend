#!/bin/bash

# Neural Capital Agents - Coral Protocol Build & Deploy Script
# This script automates the build and deployment process for Coral Protocol

set -e  # Exit on error

echo "🚀 Neural Capital Agents - Coral Protocol Deployment"
echo "=================================================="

# Configuration
REGISTRY_PREFIX="neural-capital"
VERSION="latest"
DOCKER_REGISTRY=""  # Add your registry URL here if using external registry

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if [ ! -f ".env.coral" ]; then
        print_warning ".env.coral file not found. Creating from template..."
        cp .env.coral.example .env.coral 2>/dev/null || true
        print_warning "Please edit .env.coral with your API keys before proceeding."
    fi
    
    print_success "Prerequisites check completed"
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Array of agents and their Dockerfiles
    declare -a agents=(
        "data-agent:Dockerfile.data-agent"
        "portfolio-agent:Dockerfile.portfolio-agent"
        "explainability-agent:Dockerfile.explainability-agent"
        "planner-agent:Dockerfile.planner-agent"
    )
    
    # Build each agent
    for agent_info in "${agents[@]}"; do
        IFS=':' read -r agent_name dockerfile <<< "$agent_info"
        image_name="${REGISTRY_PREFIX}/${agent_name}:${VERSION}"
        
        print_status "Building ${image_name}..."
        
        if docker build -f "${dockerfile}" -t "${image_name}" .; then
            print_success "Built ${image_name}"
        else
            print_error "Failed to build ${image_name}"
            exit 1
        fi
    done
    
    # Build coral server
    print_status "Building coral server..."
    if docker build -f Dockerfile -t "${REGISTRY_PREFIX}/coral-server:${VERSION}" .; then
        print_success "Built ${REGISTRY_PREFIX}/coral-server:${VERSION}"
    else
        print_error "Failed to build coral server"
        exit 1
    fi
}

# Test agents locally
test_agents() {
    print_status "Testing agents locally..."
    
    # Copy environment file
    cp .env.coral .env
    
    # Start services
    print_status "Starting services with Docker Compose..."
    docker-compose -f docker-compose.coral.yml up -d
    
    # Wait for services to start
    print_status "Waiting for services to start..."
    sleep 30
    
    # Test each agent
    declare -a test_endpoints=(
        "data-agent:8000"
        "portfolio-agent:8001"
        "explainability-agent:8002"
        "planner-agent:8003"
        "coral-server:5555"
    )
    
    all_healthy=true
    
    for endpoint_info in "${test_endpoints[@]}"; do
        IFS=':' read -r service_name port <<< "$endpoint_info"
        
        print_status "Testing ${service_name} on port ${port}..."
        
        if curl -s "http://localhost:${port}/health" > /dev/null; then
            print_success "${service_name} is healthy"
        else
            print_error "${service_name} health check failed"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        print_success "All agents are healthy!"
    else
        print_error "Some agents failed health checks. Check logs with: docker-compose -f docker-compose.coral.yml logs"
        exit 1
    fi
}

# Push images to registry
push_images() {
    if [ -z "$DOCKER_REGISTRY" ]; then
        print_warning "No Docker registry configured. Skipping push."
        return
    fi
    
    print_status "Pushing images to registry..."
    
    declare -a images=(
        "data-agent"
        "portfolio-agent"
        "explainability-agent"
        "planner-agent"
        "coral-server"
    )
    
    for image in "${images[@]}"; do
        local_image="${REGISTRY_PREFIX}/${image}:${VERSION}"
        remote_image="${DOCKER_REGISTRY}/${REGISTRY_PREFIX}/${image}:${VERSION}"
        
        print_status "Tagging ${local_image} as ${remote_image}..."
        docker tag "${local_image}" "${remote_image}"
        
        print_status "Pushing ${remote_image}..."
        if docker push "${remote_image}"; then
            print_success "Pushed ${remote_image}"
        else
            print_error "Failed to push ${remote_image}"
            exit 1
        fi
    done
}

# Generate submission package
generate_submission() {
    print_status "Generating marketplace submission package..."
    
    # Create submission directory
    SUBMISSION_DIR="coral-marketplace-submission"
    rm -rf "${SUBMISSION_DIR}"
    mkdir -p "${SUBMISSION_DIR}"
    
    # Copy configuration files
    cp coral-agent-*.toml "${SUBMISSION_DIR}/" 2>/dev/null || true
    cp coral-registry.toml "${SUBMISSION_DIR}/" 2>/dev/null || true
    cp docker-compose.coral.yml "${SUBMISSION_DIR}/" 2>/dev/null || true
    cp CORAL_DEPLOYMENT_GUIDE.md "${SUBMISSION_DIR}/" 2>/dev/null || true
    
    # Create submission info file
    cat > "${SUBMISSION_DIR}/submission-info.md" << EOF
# Neural Capital Agents - Coral Protocol Marketplace Submission

## Submission Date
$(date)

## Docker Images
- neural-capital/data-agent:${VERSION}
- neural-capital/portfolio-agent:${VERSION}
- neural-capital/explainability-agent:${VERSION}
- neural-capital/planner-agent:${VERSION}

## Configuration Files Included
- coral-agent-data.toml
- coral-agent-portfolio.toml
- coral-agent-explainability.toml
- coral-agent-planner.toml
- coral-registry.toml
- docker-compose.coral.yml

## Contact Information
- Publisher: Neural Capital
- Email: hello@neural-capital.com
- Website: https://neural-capital.com
- Support: support@neural-capital.com

## Next Steps
1. Send this package to hello@coralprotocol.org
2. Include wallet address and Crossmint email
3. Request wallet funding for testing
4. Await marketplace approval
EOF

    # Create archive
    tar -czf "${SUBMISSION_DIR}.tar.gz" "${SUBMISSION_DIR}"
    
    print_success "Submission package created: ${SUBMISSION_DIR}.tar.gz"
    print_status "Send this package to hello@coralprotocol.org along with your wallet information"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    docker-compose -f docker-compose.coral.yml down
}

# Main execution
main() {
    print_status "Starting Neural Capital Agents deployment process..."
    
    # Parse command line arguments
    case "${1:-}" in
        "build")
            check_prerequisites
            build_images
            ;;
        "test")
            test_agents
            ;;
        "push")
            push_images
            ;;
        "submit")
            generate_submission
            ;;
        "all")
            check_prerequisites
            build_images
            test_agents
            generate_submission
            cleanup
            ;;
        "clean")
            cleanup
            ;;
        *)
            echo "Usage: $0 {build|test|push|submit|all|clean}"
            echo ""
            echo "Commands:"
            echo "  build   - Build all Docker images"
            echo "  test    - Test agents locally"
            echo "  push    - Push images to registry"
            echo "  submit  - Generate submission package"
            echo "  all     - Run full deployment pipeline"
            echo "  clean   - Stop and remove containers"
            echo ""
            echo "Example: $0 all"
            exit 1
            ;;
    esac
    
    print_success "Deployment process completed!"
}

# Set trap for cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"