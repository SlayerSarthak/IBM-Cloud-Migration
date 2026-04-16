variable "vpc_name" {
  type        = string
  description = "Name of the VPC"
}

variable "zone" {
  type        = string
  description = "Zone for address prefix"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for VPC"
}
