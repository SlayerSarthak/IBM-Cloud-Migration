variable "security_groups" {
  description = "Security groups with rules from JSON"
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

# Create Security Groups
resource "ibm_is_security_group" "sg" {
  count = length(var.security_groups)

  name = var.security_groups[count.index].name
}

# Flatten rules for iteration
locals {
  all_rules = flatten([
    for sg_index, sg in var.security_groups : [
      for rule in sg.rules : {
        sg_index  = sg_index
        direction = rule.direction
        port      = rule.port
        protocol  = rule.protocol
        source    = rule.source
      }
    ]
  ])
}

# Create Rules Dynamically
resource "ibm_is_security_group_rule" "rules" {
  count = length(local.all_rules)

  group     = ibm_is_security_group.sg[local.all_rules[count.index].sg_index].id
  direction = local.all_rules[count.index].direction
  remote    = local.all_rules[count.index].source

  dynamic "tcp" {
    for_each = local.all_rules[count.index].protocol == "tcp" ? [1] : []
    content {
      port_min = local.all_rules[count.index].port
      port_max = local.all_rules[count.index].port
    }
  }

  dynamic "udp" {
    for_each = local.all_rules[count.index].protocol == "udp" ? [1] : []
    content {
      port_min = local.all_rules[count.index].port
      port_max = local.all_rules[count.index].port
    }
  }

  dynamic "icmp" {
    for_each = local.all_rules[count.index].protocol == "icmp" ? [1] : []
    content {}
  }
}

output "security_group_ids" {
  value = ibm_is_security_group.sg[*].id
}
