import json
from image_mapper import map_os_to_image

INPUT_FILE = "../data/input.json"
OUTPUT_FILE = "../terraform/terraform.tfvars"

with open(INPUT_FILE) as f:
    data = json.load(f)

vsi_instances = []

for vm in data["resources"]["compute"]:
    vsi_instances.append({
        "name": vm["device_name"],
        "cpu": vm["cpu"],
        "memory": vm["memory_gb"],
        "image": map_os_to_image(vm["operating_system"]),
        "disks": [d["capacity_gb"] for d in vm["storage"]],
        "security_groups": vm["network"]["security_groups"]
    })

tfvars_content = f"""
region = "us-south"

vsi_instances = {json.dumps(vsi_instances, indent=2)}

subnet_cidr = "10.10.0.0/24"
"""

with open(OUTPUT_FILE, "w") as f:
    f.write(tfvars_content)

print("✅ tfvars generated with image + network mapping")
