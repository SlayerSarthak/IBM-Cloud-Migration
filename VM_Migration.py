# ---------- SOURCE INFRA DETAILS ----------
SOURCE = {
    "ubuntu_vm_ip": "1.2.3.4",
    "windows_vm1_ip": "5.6.7.8",
    "windows_vm2_ip": "9.10.11.12",

    "ssh_user": "ubuntu",
    "ssh_key_path": "/path/to/key.pem",

    "windows_user": "Administrator",
    "windows_password": "YourPassword",

    "app_path_linux": "/var/www/html",
    "app_path_windows": "C:\\inetpub\\wwwroot"
}

# ---------- IMPORTS ----------
import os
import subprocess
import time
import winrm
from ibm_vpc import VpcV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# ---------- TARGET (IBM CLOUD) ----------
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
    name='my-vpc',
    resource_group={'id': RESOURCE_GROUP_ID}
).get_result()['id']

# ---------- CREATE SUBNET ----------
subnet_id = vpc.create_subnet(
    vpc_id,
    name='my-subnet',
    zone=f"{REGION}-1",
    ipv4_cidr_block='10.0.0.0/24'
).get_result()['id']

# ---------- SECURITY GROUP ----------
sg_id = vpc.create_security_group(
    vpc_id,
    name='my-sg'
).get_result()['id']

# Open ports
for port in [80, 22, 3389, 5985]:
    vpc.create_security_group_rule(
        sg_id,
        direction='inbound',
        protocol='tcp',
        port_min=port,
        port_max=port
    )

# ---------- CREATE VM ----------
def create_vm(name, image):
    return vpc.create_instance(
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

# Create instances
ubuntu_vm = create_vm("ubuntu-app", UBUNTU_IMAGE)
win_vm1 = create_vm("windows-app-1", WINDOWS_IMAGE)
win_vm2 = create_vm("windows-app-2", WINDOWS_IMAGE)

print("VMs Created:", ubuntu_vm, win_vm1, win_vm2)

# ---------- WAIT FUNCTIONS ----------
def wait_for_port(ip, port):
    print(f"Waiting for {ip}:{port} ...")
    for _ in range(20):
        if os.system(f"nc -z {ip} {port}") == 0:
            print(f"Port {port} ready!")
            return True
        time.sleep(15)
    return False

# ---------- LINUX MIGRATION ----------
def migrate_linux():
    vm_details = vpc.get_instance(ubuntu_vm).get_result()
    target_ip = vm_details['primary_network_interface']['primary_ip']['address']

    if not wait_for_port(target_ip, 22):
        print("Linux VM not ready")
        return

    subprocess.run(f"""
    scp -o StrictHostKeyChecking=no -i {SOURCE['ssh_key_path']} -r \
    {SOURCE['ssh_user']}@{SOURCE['ubuntu_vm_ip']}:{SOURCE['app_path_linux']} \
    {SOURCE['ssh_user']}@{target_ip}:/var/www/html
    """, shell=True)

    print("Linux migration done")

# ---------- WINDOWS MIGRATION ----------
def migrate_windows(source_ip, target_vm_id):
    vm_details = vpc.get_instance(target_vm_id).get_result()
    target_ip = vm_details['primary_network_interface']['primary_ip']['address']

    if not wait_for_port(target_ip, 5985):
        print("Windows VM not ready")
        return

    print(f"Migrating Windows from {source_ip} → {target_ip}")

    session = winrm.Session(
        f'http://{source_ip}:5985/wsman',
        auth=(SOURCE['windows_user'], SOURCE['windows_password'])
    )

    # PowerShell copy command (robocopy)
    ps_script = f"""
    robocopy {SOURCE['app_path_windows']} \\\\{target_ip}\\C$\\inetpub\\wwwroot /E
    """

    result = session.run_ps(ps_script)

    print(result.std_out.decode())
    print("Windows migration done")

# ---------- EXECUTE MIGRATION ----------
migrate_linux()
migrate_windows(SOURCE['windows_vm1_ip'], win_vm1)
migrate_windows(SOURCE['windows_vm2_ip'], win_vm2)

# ---------- LOAD BALANCER ----------
lb_id = vpc.create_load_balancer(
    is_public=True,
    name="my-load-balancer",
    subnets=[{'id': subnet_id}],
    resource_group={'id': RESOURCE_GROUP_ID}
).get_result()['id']

pool_id = vpc.create_load_balancer_pool(
    lb_id,
    algorithm="round_robin",
    protocol="http",
    name="my-pool"
).get_result()['id']

# Attach all VMs
for vm in [ubuntu_vm, win_vm1, win_vm2]:
    vpc.create_load_balancer_pool_member(
        lb_id,
        pool_id,
        port=80,
        target={'id': vm}
    )

vpc.create_load_balancer_listener(
    lb_id,
    port=80,
    protocol="http",
    default_pool={'id': pool_id}
)

print("\n===== DONE =====")
