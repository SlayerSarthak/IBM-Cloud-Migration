def map_os_to_image(os_name):
    os_name = os_name.lower()

    if "centos" in os_name:
        return "ibm-centos-stream-9-amd64"
    elif "debian" in os_name:
        return "ibm-debian-11-amd64"
    elif "windows" in os_name:
        return "ibm-windows-server-2019-full-standard-amd64"
    elif "rocky" in os_name:
        return "ibm-rocky-linux-8-amd64"
    else:
        return "ibm-centos-stream-9-amd64"
