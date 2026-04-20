variable "ibmcloud_api_key" {
  description = "IBM Cloud API Key"
  type        = string
  sensitive   = true
}

variable "region" {
  type = string
}

variable "security_groups" {
  type = list(object({
    name  = string
    rules = list(object({
      direction = string
      port      = number
      protocol  = string
      source    = string
    }))
  }))
}

variable "input_json_path" {
  default = "../data/input.json"
}

locals {
  parsed_config = jsondecode(file(var.input_json_path))
}
