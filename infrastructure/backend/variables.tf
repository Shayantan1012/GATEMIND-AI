variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "project_name" {
  type    = string
  default = "gatemind-backend"
}

variable "github_repository" {
  description = "GitHub repository in owner/name format."
  type        = string
}

variable "allowed_origins" {
  description = "Comma-separated frontend origins allowed by Flask CORS."
  type        = string
  default     = "http://localhost:5173"
}

variable "mongo_db_name" {
  type    = string
  default = "gatemind"
}

variable "desired_count" {
  type    = number
  default = 0
}

variable "cpu" {
  type    = number
  default = 1024
}

variable "memory" {
  type    = number
  default = 4096
}

variable "additional_secret_arns" {
  description = "Optional ECS environment secret names mapped to existing Secrets Manager ARNs."
  type        = map(string)
  default     = {}
}
