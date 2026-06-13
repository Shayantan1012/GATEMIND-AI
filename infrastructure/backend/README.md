# GATEMIND Backend AWS Deployment

This stack deploys only the Flask backend.

## Architecture

- Amazon ECR stores backend container images.
- Amazon ECS Fargate runs Flask through Gunicorn.
- Application Load Balancer exposes `/api/*`.
- Amazon EFS persists `backend/uploads` across deployments.
- CloudWatch stores container stdout/stderr logs.
- Secrets Manager supplies `SECRET_KEY` and `MONGO_URI`.
- GitHub Actions authenticates through OIDC and deploys `main`.

## Prerequisites

- AWS CLI authenticated to the target AWS account.
- Terraform 1.6 or newer.
- A GitHub repository containing this project.
- A reachable MongoDB deployment, such as MongoDB Atlas.
- Docker for local image testing.

## 1. Configure Terraform

```powershell
cd infrastructure/backend
Copy-Item terraform.tfvars.example terraform.tfvars
```

Update:

- `github_repository`
- `allowed_origins`
- `aws_region`
- optional secret ARNs

Do not commit `terraform.tfvars`.

## 2. Create AWS Infrastructure

The initial ECS desired count is zero so Terraform can finish before the first image and secret values exist.

```powershell
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
```

## 3. Set Required Secret Values

Get the secret ARNs:

```powershell
terraform output secret_key_secret_arn
terraform output mongo_uri_secret_arn
```

Create secret values:

```powershell
aws secretsmanager put-secret-value --secret-id <SECRET_KEY_ARN> --secret-string "<LONG_RANDOM_SECRET>"
aws secretsmanager put-secret-value --secret-id <MONGO_URI_ARN> --secret-string "<MONGODB_CONNECTION_URI>"
```

Optional LLM, SMTP, and Twilio secrets can be created in Secrets Manager and supplied through `additional_secret_arns`.

## 4. Configure GitHub Repository

Create this GitHub Actions secret:

- `AWS_DEPLOY_ROLE_ARN`: value from `terraform output github_deploy_role_arn`

Create these GitHub Actions variables:

- `AWS_REGION`: value from `terraform output` or your configured region
- `ECR_REPOSITORY`: value from `terraform output ecr_repository`
- `ECS_CLUSTER`: value from `terraform output ecs_cluster`
- `ECS_SERVICE`: value from `terraform output ecs_service`

Push to `main` or manually run **Deploy Backend to AWS**. The workflow builds the backend image, pushes it to ECR, and starts the ECS service.

Docker Desktop does not need to be running on your computer for GitHub Actions deployment.

## 5. Verify

```powershell
terraform output backend_url
```

Open:

```text
http://<load-balancer-host>/api/health
```

## MongoDB Network Access

The ECS tasks need outbound access to MongoDB. Configure MongoDB Atlas Network Access appropriately for the AWS environment. Avoid permanently allowing every IP in production; VPC peering or private connectivity is preferred.

## HTTPS

The baseline listener uses HTTP so it can deploy without a domain. Before production traffic:

1. Request an ACM certificate.
2. Add an HTTPS listener to the load balancer.
3. Redirect HTTP to HTTPS.
4. Point Route 53 or your DNS provider to the load balancer.

## Costs

This stack creates paid AWS resources, including Fargate, an Application Load Balancer, EFS, CloudWatch, and Secrets Manager. Run `terraform destroy` when the environment is no longer needed.
