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

variable "allowed_http_cidrs" {
  description = "Networks allowed to access backend HTTP."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "mongo_db_name" {
  type    = string
  default = "gatemind"
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "root_volume_size" {
  description = "Encrypted EBS root volume size in GiB. Uploaded files persist here."
  type        = number
  default     = 30
}

variable "additional_secret_arns" {
  description = "Optional environment variable names mapped to existing Secrets Manager ARNs."
  type        = map(string)
  default     = {}
}
