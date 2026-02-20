#!/bin/bash
# =============================================================================
# Salon Flow API - Upstash Redis Setup Script
# =============================================================================
# This script helps set up Upstash Redis for serverless caching
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

echo "========================================"
echo "  Upstash Redis Setup for Salon Flow"
echo "========================================"
echo ""
echo "This script will guide you through setting up Upstash Redis"
echo "for serverless caching on Cloud Run."
echo ""

# Check if upstash CLI is installed
if ! command -v upstash &> /dev/null; then
    log_info "Upstash CLI not found. You can install it with:"
    echo "  npm install -g upstash-cli"
    echo ""
    echo "Alternatively, use the Upstash web console:"
    echo "  https://console.upstash.io"
fi

echo ""
echo "Step 1: Create Upstash Account"
echo "-------------------------------"
echo "1. Go to https://upstash.com"
echo "2. Sign up for a free account"
echo "3. Free tier includes: 10,000 commands/day, 256MB storage"
echo ""

echo "Step 2: Create Redis Database"
echo "------------------------------"
echo "1. In Upstash Console, click 'Create Database'"
echo "2. Configure as follows:"
echo "   - Name: salon-flow-cache"
echo "   - Region: ap-south-1 (Mumbai - closest to GCP asia-south1)"
eecho "   - Type: Regional"
echo "   - Enable TLS: Yes (required for Cloud Run)"
echo "3. Click 'Create'"
echo ""

echo "Step 3: Get Connection URL"
echo "--------------------------"
echo "1. In your database dashboard, click 'Details'"
echo "2. Copy the 'UPSTASH_REDIS_REST_URL' or connection string"
echo "   Format: rediss://default:PASSWORD@HOST.upstash.io:6379"
echo ""

read -p "Enter your Upstash Redis URL (rediss://...): " UPSTASH_URL

if [[ -z "$UPSTASH_URL" ]]; then
    echo "No URL provided. Exiting."
    exit 1
fi

# Save to GCP Secret Manager
if command -v gcloud &> /dev/null; then
    read -p "Save to GCP Secret Manager? (y/n): " SAVE_SECRET
    if [[ "$SAVE_SECRET" =~ ^[Yy]$ ]]; then
        echo "$UPSTASH_URL" | gcloud secrets create upstash-redis-url \
            --data-file=- \
            --project=salon-saas-487508 2>/dev/null || \
        echo "$UPSTASH_URL" | gcloud secrets versions add upstash-redis-url \
            --data-file=- \
            --project=salon-saas-487508
        log_success "Secret saved to GCP Secret Manager"
    fi
fi

# Save to .env file
read -p "Save to local .env file? (y/n): " SAVE_ENV
if [[ "$SAVE_ENV" =~ ^[Yy]$ ]]; then
    ENV_FILE="$(dirname "$0")/../services/api/.env"
    if grep -q "UPSTASH_REDIS_URL" "$ENV_FILE" 2>/dev/null; then
        # Update existing
        sed -i "s|^UPSTASH_REDIS_URL=.*|UPSTASH_REDIS_URL=$UPSTASH_URL|" "$ENV_FILE"
    else
        # Add new
        echo "UPSTASH_REDIS_URL=$UPSTASH_URL" >> "$ENV_FILE"
    fi
    log_success "URL saved to $ENV_FILE"
fi

echo ""
log_success "Upstash Redis setup complete!"
echo ""
echo "Next steps:"
echo "1. Run './deploy/deploy.sh --deploy' to deploy to Cloud Run"
echo "2. The service will automatically use Upstash Redis for caching"
