variable "vsi_instances" {
  description = "List of VSI instances to create"
  type = list(object({
    name            = string
    cpu             = number
    memory          = number
    image           = string
    disks           = list(number)
    security_groups = list(string)
  }))
}

variable "subnet_id" {
  description = "Subnet ID where VSI will be deployed"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "security_group_ids" {
  description = "Security group IDs to attach to VSI"
  type        = list(string)
}
