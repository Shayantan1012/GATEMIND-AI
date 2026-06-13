# GATEMIND Backend: EC2 + Docker Deployment

This lower-cost stack deploys only the Flask backend on one EC2 instance.

## Architecture

- Amazon EC2 runs the backend Docker container.
- Amazon ECR stores backend container images.
- The EC2 encrypted EBS volume persists `/opt/gatemind/uploads`.
- Secrets Manager supplies `SECRET_KEY`, `MONGO_URI`, and optional API credentials.
- AWS Systems Manager deploys containers without opening SSH port 22.
- GitHub Actions authenticates through OIDC and deploys only after backend CI passes.

The stack does not create ECS, Fargate, a load balancer, EFS, or a NAT Gateway.

## Expected Cost

The primary costs are:

- One `t3.small` EC2 instance
- One 30 GiB gp3 EBS volume
- One Elastic IP while attached to the running instance
- Small ECR and Secrets Manager usage

For lighter workloads, change `instance_type` to `t3.micro`. RAG embedding dependencies may require more memory, so `t3.small` is the safer default.

## Prerequisites

- AWS CLI authenticated to the target account
- Terraform 1.6 or newer
- GitHub repository containing this project
- Reachable MongoDB deployment such as MongoDB Atlas

Docker Desktop is not required for GitHub Actions deployment.

## 1. Configure Terraform

```powershell
cd infrastructure/backend
Copy-Item terraform.tfvars.example terraform.tfvars
```

Update:

- `github_repository`
- `allowed_origins`
- `aws_region`
- optional `instance_type`
- optional secret ARNs

Do not commit `terraform.tfvars`.

## 2. Create AWS Infrastructure

```powershell
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

The instance installs Docker during startup. It will not run the backend until the first GitHub deployment because no image exists yet.

## 3. Set Required Secret Values

Get the generated secret ARNs:

```powershell
terraform output secret_key_secret_arn
terraform output mongo_uri_secret_arn
```

Set their values:

```powershell
aws secretsmanager put-secret-value --secret-id <SECRET_KEY_ARN> --secret-string "<LONG_RANDOM_SECRET>"
aws secretsmanager put-secret-value --secret-id <MONGO_URI_ARN> --secret-string "<MONGODB_CONNECTION_URI>"
```

For optional LLM, SMTP, and Twilio credentials:

1. Create individual Secrets Manager secrets.
2. Add their names and ARNs to `additional_secret_arns`.
3. Run `terraform apply` again.

Example:

```hcl
additional_secret_arns = {
  GROQ_API_KEY   = "arn:aws:secretsmanager:..."
  OPENAI_API_KEY = "arn:aws:secretsmanager:..."
}
```

## 4. Configure GitHub Actions

Create this GitHub Actions secret:

- `AWS_DEPLOY_ROLE_ARN`: `terraform output github_deploy_role_arn`

Create these GitHub Actions variables:

- `AWS_REGION`: `terraform output -raw aws_region`
- `ECR_REPOSITORY`: `terraform output -raw ecr_repository`
- `EC2_INSTANCE_ID`: `terraform output -raw backend_instance_id`

After backend CI passes on `main`, GitHub Actions:

1. Builds the backend Docker image.
2. Pushes it to ECR.
3. Sends an SSM deployment command to EC2.
4. Pulls and restarts the backend container.

## 5. Verify

```powershell
terraform output backend_url
```

Open:

```text
http://<elastic-ip>/api/health
```

## Useful Operations

Check the container without SSH:

```powershell
aws ssm send-command --instance-ids <INSTANCE_ID> --document-name AWS-RunShellScript --parameters 'commands=["sudo docker ps","sudo docker logs --tail 100 gatemind-backend"]'
```

Uploaded files persist at `/opt/gatemind/uploads` on the EC2 EBS disk across container deployments and instance reboots.

## MongoDB Network Access

Allow the EC2 Elastic IP in MongoDB Atlas Network Access. For stronger production isolation, use private connectivity later.

## HTTPS

This cost-focused baseline exposes HTTP directly from EC2. Before production traffic, add a domain and HTTPS using either:

- Nginx and Let’s Encrypt on the instance, or
- an Application Load Balancer with ACM, which costs more.

## Backups

The uploaded files live on the EC2 root EBS volume. Configure scheduled EBS snapshots before storing important production documents.

## Destroying the Environment

```powershell
terraform destroy
```
