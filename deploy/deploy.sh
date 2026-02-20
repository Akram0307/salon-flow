#!/bin/bash
# =============================================================================
# Salon Flow API - Cloud Run Deployment Script
# =============================================================================
# Usage: ./deploy.sh [options]
# Options:
#   --setup      First-time setup (enable APIs, create resources)
#   --deploy     Deploy the service
#   --destroy    Remove all resources
#   --status     Check deployment status
#   --logs       View logs
#   --help       Show this help message
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="salon-saas-487508"
REGION="asia-south1"
SERVICE_NAME="salon-flow-api"
ARTIFACT_REPO="salon-flow-images"

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter="status:ACTIVE" --format="value(account)" | grep -q .; then
        log_error "Not authenticated with gcloud. Run 'gcloud auth login' first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# =============================================================================
# Setup Functions
# =============================================================================

enable_apis() {
    log_info "Enabling required GCP APIs..."
    
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        artifactregistry.googleapis.com \
        secretmanager.googleapis.com \
        firestore.googleapis.com \
        cloudresourcemanager.googleapis.com \
        iam.googleapis.com \
        --project="$PROJECT_ID"
    
    log_success "APIs enabled"
}

create_artifact_repo() {
    log_info "Creating Artifact Registry repository..."
    
    if gcloud artifacts repositories describe "$ARTIFACT_REPO" --location="$REGION" --project="$PROJECT_ID" &> /dev/null; then
        log_warning "Artifact repository already exists"
    else
        gcloud artifacts repositories create "$ARTIFACT_REPO" \
            --repository-format=docker \
            --location="$REGION" \
            --description="Salon Flow Docker images" \
            --project="$PROJECT_ID"
        log_success "Artifact repository created"
    fi
}

setup_secrets() {
    log_info "Setting up secrets in Secret Manager..."
    
    # GCP JSON Key
    if gcloud secrets describe gcp-json-key --project="$PROJECT_ID" &> /dev/null; then
        log_warning "Secret 'gcp-json-key' already exists"
    else
        echo "$GCP_JSON_KEY" | gcloud secrets create gcp-json-key \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID"
        log_success "Secret 'gcp-json-key' created"
    fi
    
    # OpenRouter API Key
    if gcloud secrets describe openrouter-api-key --project="$PROJECT_ID" &> /dev/null; then
        log_warning "Secret 'openrouter-api-key' already exists"
    else
        echo "$OPENROUTER_API_KEY" | gcloud secrets create openrouter-api-key \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID"
        log_success "Secret 'openrouter-api-key' created"
    fi
    
    # Upstash Redis URL
    if gcloud secrets describe upstash-redis-url --project="$PROJECT_ID" &> /dev/null; then
        log_warning "Secret 'upstash-redis-url' already exists"
    else
        echo "$UPSTASH_REDIS_URL" | gcloud secrets create upstash-redis-url \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID"
        log_success "Secret 'upstash-redis-url' created"
    fi
}

setup_service_account() {
    log_info "Configuring service account permissions..."
    
    # Get Cloud Run service account email
    SA_EMAIL="${PROJECT_ID}@appspot.gserviceaccount.com"
    
    # Grant Secret Manager accessor role
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/secretmanager.secretAccessor" \
        --condition=None
    
    # Grant Firestore user role
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/datastore.user" \
        --condition=None
    
    # Grant Cloud Run invoker role (for internal services)
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/run.invoker" \
        --condition=None
    
    log_success "Service account permissions configured"
}

setup_firestore() {
    log_info "Checking Firestore configuration..."
    
    # Firestore should already be created with Firebase
    # Just verify it exists
    if gcloud firestore databases describe --project="$PROJECT_ID" &> /dev/null; then
        log_success "Firestore database exists"
    else
        log_warning "Firestore database not found. Creating..."
        gcloud firestore databases create \
            --location="$REGION" \
            --project="$PROJECT_ID"
        log_success "Firestore database created"
    fi
}

# =============================================================================
# Deploy Functions
# =============================================================================

build_and_push() {
    log_info "Building and pushing Docker image..."
    
    cd "$(dirname "$0")/.."
    
    # Build image
    docker build \
        -t "${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/${SERVICE_NAME}:latest" \
        -f services/api/Dockerfile.cloudrun \
        services/api
    
    # Configure Docker for Artifact Registry
    gcloud auth configure-docker "${REGION}-docker.pkg.dev" --project="$PROJECT_ID"
    
    # Push image
    docker push "${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/${SERVICE_NAME}:latest"
    
    log_success "Image pushed to Artifact Registry"
}

deploy_service() {
    log_info "Deploying to Cloud Run..."
    
    gcloud run deploy "$SERVICE_NAME" \
        --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/${SERVICE_NAME}:latest" \
        --region="$REGION" \
        --platform=managed \
        --memory=512Mi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=10 \
        --timeout=300 \
        --set-env-vars="ENVIRONMENT=production,FIREBASE_PROJECT_ID=${PROJECT_ID}" \
        --set-secrets="GCP_JSON_KEY=gcp-json-key:latest,OPENROUTER_API_KEY=openrouter-api-key:latest,UPSTASH_REDIS_URL=upstash-redis-url:latest" \
        --no-allow-unauthenticated \
        --ingress=all \
        --project="$PROJECT_ID"
    
    log_success "Service deployed"
}

# =============================================================================
# Utility Functions
# =============================================================================

get_service_url() {
    gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(status.url)" \
        --project="$PROJECT_ID"
}

show_status() {
    log_info "Deployment Status:"
    echo ""
    gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format="yaml(status, spec.template.spec.containers)"
}

show_logs() {
    gcloud run logs read \
        --service="$SERVICE_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --limit=100
}

test_health() {
    log_info "Testing health endpoint..."
    
    SERVICE_URL=$(get_service_url)
    TOKEN=$(gcloud auth print-identity-token)
    
    if curl -s -f "${SERVICE_URL}/health" -H "Authorization: Bearer ${TOKEN}" | jq .; then
        log_success "Health check passed"
    else
        log_error "Health check failed"
    fi
}

# =============================================================================
# Destroy Functions
# =============================================================================

destroy_service() {
    log_warning "This will delete the Cloud Run service and all associated resources"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud run services delete "$SERVICE_NAME" \
            --region="$REGION" \
            --project="$PROJECT_ID" \
            --quiet
        log_success "Service deleted"
    fi
}

# =============================================================================
# Main
# =============================================================================

show_help() {
    echo "Salon Flow API - Cloud Run Deployment Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --setup      First-time setup (enable APIs, create resources)"
    echo "  --deploy     Deploy the service"
    echo "  --status     Check deployment status"
    echo "  --logs       View logs"
    echo "  --health     Test health endpoint"
    echo "  --destroy    Remove all resources"
    echo "  --help       Show this help message"
    echo ""
    echo "Environment Variables (required for --setup):"
    echo "  GCP_JSON_KEY        - GCP service account JSON key"
    echo "  OPENROUTER_API_KEY  - OpenRouter API key"
    echo "  UPSTASH_REDIS_URL   - Upstash Redis connection URL"
}

# Parse arguments
case "${1:-}" in
    --setup)
        check_prerequisites
        enable_apis
        create_artifact_repo
        setup_secrets
        setup_service_account
        setup_firestore
        log_success "Setup complete! Run './deploy.sh --deploy' to deploy the service."
        ;;
    --deploy)
        check_prerequisites
        build_and_push
        deploy_service
        show_status
        test_health
        ;;
    --status)
        show_status
        ;;
    --logs)
        show_logs
        ;;
    --health)
        test_health
        ;;
    --destroy)
        destroy_service
        ;;
    --help|*)
        show_help
        ;;
esac
