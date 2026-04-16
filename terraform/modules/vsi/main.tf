variable "vsi_instances" {}
variable "subnet_id" {}
variable "vpc_id" {}

resource "ibm_is_instance" "vsi" {
  count = length(var.vsi_instances)

  name    = var.vsi_instances[count.index].name
  vpc     = var.vpc_id
  zone    = "us-south-1"
  profile = "bx2-2x4"
  image   = var.vsi_instances[count.index].image

  primary_network_interface {
    subnet = var.subnet_id
    security_groups = var.security_group_ids
  }
}

module "storage" {
  source = "../storage"

  count        = length(var.vsi_instances)
  instance_id  = ibm_is_instance.vsi[count.index].id
  disk_sizes   = var.vsi_instances[count.index].disks
}
