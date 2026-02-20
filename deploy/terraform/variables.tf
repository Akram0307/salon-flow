# =============================================================================
# Salon Flow API - Terraform Variables
# =============================================================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "salon-saas-487508"
}

variable "region" {
  description = "GCP Region for deployment"
  type        = string
  default     = "asia-south1"  # Mumbai - lowest latency for India
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "salon-flow-api"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

# Scaling Configuration
variable "min_instances" {
  description = "Minimum instances (0 = scale to zero)"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum instances"
  type        = number
  default     = 10
}

variable "memory" {
  description = "Memory per instance"
  type        = string
  default     = "512Mi"
}

variable "cpu" {
  description = "CPU per instance"
  type        = string
  default     = "1"
}

# Secrets (mark as sensitive)
variable "gcp_json_key" {
  description = "GCP Service Account JSON key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "upstash_redis_url" {
  description = "Upstash Redis connection URL (rediss://...)"
  type        = string
  sensitive   = true
}

variable "openrouter_api_key" {
  description = "OpenRouter API key"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT signing secret"
  type        = string
  sensitive   = true
}
