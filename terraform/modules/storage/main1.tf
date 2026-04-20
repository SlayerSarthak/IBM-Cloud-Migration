resource "ibm_is_volume" "iscsi_volume" {
  for_each = { for s in var.iscsi_servers : s.name => s }
  name     = "${each.value.name}-volume"
  profile  = "custom"
  zone     = each.value.zone
  capacity = each.value.volume_size
  iops     = each.value.volume_iops
}

resource "ibm_is_instance" "iscsi_target" {
  for_each = { for s in var.iscsi_servers : s.name => s }
  name     = each.value.name
  profile  = each.value.profile
  zone     = each.value.zone
  vpc      = var.vpc_id

  primary_network_interface {
    subnet = var.subnet_id
  }

  volumes = [ibm_is_volume.iscsi_volume[each.key].id]
}
