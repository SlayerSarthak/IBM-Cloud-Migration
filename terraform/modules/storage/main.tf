variable "instance_id" {}
variable "disk_sizes" {
  type = list(number)
}

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
