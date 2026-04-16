resource "ibm_is_vpc" "vpc" {
  name = var.vpc_name
}

# Address prefix (MANDATORY in IBM VPC)
resource "ibm_is_vpc_address_prefix" "prefix" {
  name = "${var.vpc_name}-prefix"
  zone = var.zone
  vpc  = ibm_is_vpc.vpc.id
  cidr = var.vpc_cidr
}
