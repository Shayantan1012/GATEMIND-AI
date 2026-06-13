output "backend_url" {
  value = "http://${aws_eip.backend.public_ip}"
}

output "backend_instance_id" {
  value = aws_instance.backend.id
}

output "backend_public_ip" {
  value = aws_eip.backend.public_ip
}

output "aws_region" {
  value = var.aws_region
}

output "ecr_repository" {
  value = aws_ecr_repository.backend.name
}

output "github_deploy_role_arn" {
  value = aws_iam_role.github_deploy.arn
}

output "secret_key_secret_arn" {
  value = aws_secretsmanager_secret.secret_key.arn
}

output "mongo_uri_secret_arn" {
  value = aws_secretsmanager_secret.mongo_uri.arn
}
