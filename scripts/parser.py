import json
from image_mapper import map_os_to_image

INPUT_FILE = "../data/input.json"
OUTPUT_FILE = "../terraform/terraform.tfvars"

with open(INPUT_FILE) as f:
    data = json.load(f)

# -----------------------------
# COMPUTE (VSI + Bare Metal)
# -----------------------------
vsi_instances = []

# Handle VSI
for vm in data["resources"].get("compute", []):
    vsi_instances.append({
        "name": vm["device_name"],
        "cpu": vm["cpu"],
        "memory": vm["memory_gb"],
        "image": map_os_to_image(vm["operating_system"]),
        "disks": [d["capacity_gb"] for d in vm.get("storage", [])],
        "security_groups": vm.get("security_groups", [])
    })

# Handle Bare Metal → convert to VSI
for bm in data["resources"].get("bare_metal", []):
    vsi_instances.append({
        "name": bm["device_name"],
        "cpu": bm["cpu"],
        "memory": bm["memory_gb"],
        "image": map_os_to_image(bm["operating_system"]),
        "disks": [d["capacity_gb"] for d in bm.get("storage", [])],
        "security_groups": []
    })

# -----------------------------
# SECURITY GROUPS (IMPORTANT)
# -----------------------------
security_groups = data["resources"].get("security", {}).get("security_groups", [])

# -----------------------------
# NETWORK (CIDR)
# -----------------------------
subnet_cidr = "10.10.0.0/24"

if data["resources"].get("network", {}).get("subnets"):
    subnet_cidr = data["resources"]["network"]["subnets"][0].get("cidr", subnet_cidr)

# -----------------------------
# FINAL TFVARS CONTENT
# -----------------------------
tfvars_content = f"""
region = "us-south"

subnet_cidr = "{subnet_cidr}"

vsi_instances = {json.dumps(vsi_instances, indent=2)}

security_groups = {json.dumps(security_groups, indent=2)}
"""

# -----------------------------
# WRITE FILE
# -----------------------------
with open(OUTPUT_FILE, "w") as f:
    f.write(tfvars_content)

print("✅ terraform.tfvars generated successfully (compute + security + network)")
