# Terraform Infrastructure as Code Skill

## Overview
Define and manage GCP infrastructure using Terraform for reproducible, version-controlled deployments.

## Project Structure
```
infrastructure/
├── modules/
│   ├── cloud-run/
│   ├── firestore/
│   ├── pubsub/
│   └── storage/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── main.tf
├── variables.tf
└── outputs.tf
```

## Core Resources

### Cloud Run Service
```hcl
resource "google_cloud_run_service" "api" {
  name     = "salon-api"
  location = var.region

  template {
    spec {
      containers {
        image = var.image
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "10"
      }
    }
  }
}
```

## Commands
- terraform init - Initialize working directory
- terraform plan - Preview changes
- terraform apply - Apply changes
- terraform destroy - Remove resources

## Best Practices
- Use remote state in Cloud Storage
- Lock state file during operations
- Use workspaces for environments
- Tag all resources for cost tracking
