output "vpc_id" {
  value = module.vpc.vpc_id
}

output "subnet_id" {
  value = module.subnet.subnet_id
}

output "security_group_ids" {
  value = module.security.security_group_ids
}

output "vsi_names" {
  value = [for vm in var.vsi_instances : vm.name]
}
