module "vpc" {
  source   = "./modules/vpc"
  vpc_name = "migration-vpc"
  zone     = "us-south-1"
  vpc_cidr = "10.10.0.0/16"
}
module "subnet" {
  source = "./modules/subnet"
  vpc_id = module.vpc.vpc_id
  cidr   = var.subnet_cidr
}

module "security" {
  source = "./modules/security"
  security_groups = var.security_groups
}

module "vsi" {
  source        = "./modules/vsi"
  vsi_instances = var.vsi_instances
  subnet_id     = module.subnet.subnet_id
  vpc_id        = module.vpc.vpc_id

  security_group_ids = module.security.security_group_ids
}
