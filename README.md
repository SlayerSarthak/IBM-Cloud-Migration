# IBM-Cloud-Migration
This repo. is used Migration of the Classic Infra. to the VPC for the IBM Cloud.

🔧 Update These Values Before Running
1️⃣ Source Infrastructure Details
Replace all placeholder values:

SOURCE = {
    "ubuntu_vm_ip": "YOUR_LINUX_SOURCE_IP",
    "windows_vm1_ip": "YOUR_WINDOWS_VM1_IP",
    "windows_vm2_ip": "YOUR_WINDOWS_VM2_IP",

    "ssh_user": "ubuntu",
    "ssh_key_path": "/path/to/your/key.pem",

    "windows_user": "Administrator",
    "windows_password": "YOUR_WINDOWS_PASSWORD",

    "app_path_linux": "/var/www/html",
    "app_path_windows": "C:\\inetpub\\wwwroot"
}

2️⃣ IBM Cloud Credentials
Replace with your IBM Cloud account details:

API_KEY = "YOUR_IBM_CLOUD_API_KEY"
RESOURCE_GROUP_ID = "YOUR_RESOURCE_GROUP_ID"
REGION = "eu-de"   # change if needed (e.g., us-south)

3️⃣ SSH Key Path

/path/to/your/key.pem
✔ Must exist on your system
✔ Set correct permission:
chmod 400 key.pem

4️⃣ (Optional) OS Image / Profile
Update only if needed:

UBUNTU_IMAGE = "r006-ubuntu-22-04-amd64"
WINDOWS_IMAGE = "r006-windows-server-2022-amd64"
PROFILE = "bx2-2x8"
✅ Final Check

Before running, ensure:
- All IPs are correct
- API key is valid
- SSH key path is correct
- Windows password is correct
  
▶️ Run Script
python your_script_name.py
