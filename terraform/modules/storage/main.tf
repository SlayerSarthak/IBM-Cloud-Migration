variable "instance_id" {
  description = "VSI instance ID for volume attachment"
  type        = string
  default     = null
}

variable "disk_sizes" {
  description = "List of disk sizes for volume attachment"
  type        = list(number)
  default     = []
}

variable "iscsi_servers" {
  description = "iSCSI server configurations"
  type = list(object({
    name           = string
    zone           = string
    profile        = string
    volume_size    = number
    volume_iops    = number
    initiator_iqns = list(string)
  }))
  default = []
}

variable "vpc_id" {
  type = string
}

variable "subnet_id" {
  type = string
}

# Standard volume attachment (your existing code)
resource "ibm_is_volume" "volume" {
  count = length(var.disk_sizes)

  name     = "volume-${count.index}"
  capacity = var.disk_sizes[count.index]
  profile  = "general-purpose"
  zone     = "us-south-1"
}

resource "ibm_is_volume_attachment" "attach" {
  count = length(var.disk_sizes)

  instance = var.instance_id
  volume   = ibm_is_volume.volume[count.index].id
}

# iSCSI storage provisioning
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

  name    = each.value.name
  profile = each.value.profile
  zone    = each.value.zone
  vpc     = var.vpc_id
  image   = "r006-14140f94-fcc4-11e9-96e7-a72723715315" # Ubuntu 20.04

  primary_network_interface {
    subnet = var.subnet_id
  }

  volumes = [ibm_is_volume.iscsi_volume[each.key].id]

  user_data = templatefile("${path.module}/iscsi-init.sh", {
    initiator_iqns = each.value.initiator_iqns
    target_name    = each.value.name
  })
}

output "iscsi_endpoints" {
  value = {
    for k, v in ibm_is_instance.iscsi_target : k => {
      ip  = v.primary_network_interface[0].primary_ipv4_address
      iqn = "iqn.2020-01.com.ibm:${v.name}"
    }
  }
}
