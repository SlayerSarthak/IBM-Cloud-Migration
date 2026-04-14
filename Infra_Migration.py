import json
import os
import subprocess
import time
import winrm
from ibm_vpc import VpcV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# ---------- LOAD JSON ----------
with open("input.json") as f:
    data = json.load(f)

# ---------- SOURCE DETAILS (YOU MUST UPDATE) ----------
SOURCE = {
    "ssh_user": "ubuntu",
    "ssh_key_path": "/path/to/key.pem",

    "windows_user": "Administrator",
    "windows_password": "YourPassword",

    "app_path_linux": "/var/www/html",
    "app_path_windows": "C:\\inetpub\\wwwroot"
}

# ---------- IBM CLOUD ----------
API_KEY = "your-api-key"
REGION = "eu-de"
RESOURCE_GROUP_ID = "your-resource-group"

UBUNTU_IMAGE = "r006-ubuntu-22-04-amd64"
WINDOWS_IMAGE = "r006-windows-server-2022-amd64"
PROFILE = "bx2-2x8"

# ---------- AUTH ----------
authenticator = IAMAuthenticator(API_KEY)
vpc = VpcV1(authenticator=authenticator)
vpc.set_service_url(f"https://{REGION}.iaas.cloud.ibm.com/v1")

# ---------- CREATE VPC ----------
vpc_id = vpc.create_vpc(
    address_prefix_management='auto',
    name='json-vpc',
    resource_group={'id': RESOURCE_GROUP_ID}
).get_result()['id']

# ---------- CREATE SUBNET ----------
subnet_id = vpc.create_subnet(
    vpc_id,
    name='json-subnet',
    zone=f"{REGION}-1",
    ipv4_cidr_block='10.0.0.0/24'
).get_result()['id']

# ---------- SECURITY GROUP ----------
sg_id = vpc.create_security_group(
    vpc_id,
    name='json-sg'
).get_result()['id']

for port in [80, 22, 3389, 5985]:
    vpc.create_security_group_rule(
        sg_id,
        direction='inbound',
        protocol='tcp',
        port_min=port,
        port_max=port
    )

# ---------- WAIT FUNCTION ----------
def wait_for_port(ip, port):
    for _ in range(20):
        if os.system(f"nc -z {ip} {port}") == 0:
            return True
        time.sleep(10)
    return False

# ---------- MIGRATION ----------
def migrate_linux(src_ip, target_ip):
    if not wait_for_port(target_ip, 22):
        print("Linux VM not ready")
        return

    subprocess.run(f"""
    scp -o StrictHostKeyChecking=no -i {SOURCE['ssh_key_path']} -r \
    {SOURCE['ssh_user']}@{src_ip}:{SOURCE['app_path_linux']} \
    {SOURCE['ssh_user']}@{target_ip}:/var/www/html
    """, shell=True)


def migrate_windows(src_ip, target_ip):
    if not wait_for_port(target_ip, 5985):
        print("Windows VM not ready")
        return

    session = winrm.Session(
        f'http://{src_ip}:5985/wsman',
        auth=(SOURCE['windows_user'], SOURCE['windows_password'])
    )

    ps_script = f"""
    robocopy {SOURCE['app_path_windows']} \\\\{target_ip}\\C$\\inetpub\\wwwroot /E
    """

    session.run_ps(ps_script)

# ---------- CREATE VMs FROM JSON ----------
created_vms = []

for vm in data["resources"]["compute"]:
    name = vm["device_name"]
    os_type = vm["operating_system"]

    if "Windows" in os_type:
        image = WINDOWS_IMAGE
        os_flag = "windows"
    else:
        image = UBUNTU_IMAGE
        os_flag = "linux"

    print(f"Creating VM: {name}")

    vm_id = vpc.create_instance(
        name=name,
        vpc={'id': vpc_id},
        zone={'name': f"{REGION}-1"},
        profile={'name': PROFILE},
        image={'id': image},
        primary_network_interface={
            'subnet': {'id': subnet_id},
            'security_groups': [{'id': sg_id}]
        },
        resource_group={'id': RESOURCE_GROUP_ID}
    ).get_result()['id']

    # Fetch IP
    vm_details = vpc.get_instance(vm_id).get_result()
    ip = vm_details['primary_network_interface']['primary_ip']['address']

    created_vms.append({
        "id": vm_id,
        "ip": ip,
        "os": os_flag
    })

# ---------- MIGRATION LOOP ----------
print("Starting Migration...")

for i, vm in enumerate(created_vms):
    target_ip = vm["ip"]

    # ⚠️ YOU MUST MAP SOURCE IPs MANUALLY HERE
    src_ip = "REPLACE_WITH_SOURCE_IP"

    if vm["os"] == "linux":
        migrate_linux(src_ip, target_ip)
    else:
        migrate_windows(src_ip, target_ip)

# ---------- LOAD BALANCER ----------
lb_id = vpc.create_load_balancer(
    is_public=True,
    name="json-lb",
    subnets=[{'id': subnet_id}],
    resource_group={'id': RESOURCE_GROUP_ID}
).get_result()['id']

pool_id = vpc.create_load_balancer_pool(
    lb_id,
    algorithm="round_robin",
    protocol="http",
    name="json-pool"
).get_result()['id']

for vm in created_vms:
    vpc.create_load_balancer_pool_member(
        lb_id,
        pool_id,
        port=80,
        target={'id': vm["id"]}
    )

vpc.create_load_balancer_listener(
    lb_id,
    port=80,
    protocol="http",
    default_pool={'id': pool_id}
)

print("\n✅ DONE: Infra + Migration Complete")
