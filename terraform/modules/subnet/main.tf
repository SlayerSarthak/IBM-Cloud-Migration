variable "vpc_id" {}
variable "cidr" {}

resource "ibm_is_subnet" "subnet" {
  name            = "migration-subnet"
  vpc             = var.vpc_id
  zone            = "us-south-1"
  ipv4_cidr_block = var.cidr
}

output "subnet_id" {
  value = ibm_is_subnet.subnet.id
}
