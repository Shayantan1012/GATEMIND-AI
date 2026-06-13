output "backend_url" {
  value = "http://${aws_lb.backend.dns_name}"
}

output "ecr_repository" {
  value = aws_ecr_repository.backend.name
}

output "ecs_cluster" {
  value = aws_ecs_cluster.backend.name
}

output "ecs_service" {
  value = aws_ecs_service.backend.name
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
