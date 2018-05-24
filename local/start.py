#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports
import os
import sys
import urllib.request
from shutil import copyfile
import ipaddress

ORIGINAL_EXECUTION_PATH_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Read the settings
def read_settings(key=None):
    import yaml
    with open(os.path.abspath("../settings.yml")) as file:
        settings = yaml.safe_load(file)

    if key:
        return settings[key]

    else:
        return settings


# Install requirements
def install_requirements(system_wide=False):
    if not system_wide:
        os.system("pip3 install -r requirements.txt --user")

    else:
        os.system("sudo pip3 install -r requirements.txt")


# iPXE
class iPXE():
    def __init__(self):
        self.settings = read_settings()
        self.git_repo_path = os.path.join(ORIGINAL_EXECUTION_PATH_DIRECTORY, "pxe-server")
        self.src_path = os.path.join(self.git_repo_path, "ipxe/src")

    def clone_repo(self):
        os.chdir(self.git_repo_path)
        clone_result = os.system("git clone https://github.com/ipxe/ipxe")

        if clone_result != 0:
            os.system("clear")
            print("Unable to clone the repository! Please, make sure you have internet connection, permissions to write and that the directory 'pxe-server/ipxe' does not exist")
            sys.exit(1)

        os.chdir(self.src_path)

    def generate_chainload_script(self):
        chainload_script = """#!ipxe

# Get an IP address
echo Getting an IP address...
dhcp

# Chainload to the API
echo Loading the menu...
chain {}://{}/boot""".format(self.settings["api"]["protocol"], self.settings["api"]["domain_name"])

        with open(os.path.join(self.src_path, "chainload.ipxe"), "w") as f:
            f.write(chainload_script)

    def create_ca_certificate(self, file=None):
        if file:
            try:
                copyfile(os.path.abspath(file), os.path.join(self.src_path, "ca.cer"))

            except FileNotFoundError:
                print("The file {} wasn't found!".format(file))
                sys.exit(1)

        else:
            urllib.request.urlretrieve("https://letsencrypt.org/certs/isrgrootx1.pem.txt", os.path.join(self.src_path, "ca.cer"))

    # TODO
    def modify_compilation_options(self):
        with open(os.path.join(self.src_path, "config/console.h"), "r") as f:
            console_config_file = f.readlines()

        with open(os.path.join(self.src_path, "config/general.h"), "r") as f:
            general_config_file = f.readlines()

        for line_num, line in enumerate(console_config_file):
            if line == "//#define\tCONSOLE_FRAMEBUFFER\t/* Graphical framebuffer console */\n":
                console_config_file[line_num] = "#define\tCONSOLE_FRAMEBUFFER\t/* Graphical framebuffer console */\n"

            elif line.startswith("#define\tKEYBOARD_MAP"):
                console_config_file[line_num] = "#define\tKEYBOARD_MAP\t{}\n".format(self.settings["ipxe"]["keymap"])

        for line_num, line in enumerate(general_config_file):
            if line == "#undef\tDOWNLOAD_PROTO_HTTPSt\t/* Secure Hypertext Transfer Protocol */\n":
                general_config_file[line_num] = "#define\tDOWNLOAD_PROTO_HTTPS\t/* Secure Hypertext Transfer Protocol */\n"
            if line == "//#define REBOOT_CMD\t\t/* Reboot command */\n":
                general_config_file[line_num] = "#define REBOOT_CMD\t\t/* Reboot command */\n"

            elif line == "//#define POWEROFF_CMD\t\t/* Power off command */\n":
                general_config_file[line_num] = "#define POWEROFF_CMD\t\t/* Power off command */\n"

            elif line == "//#define CONSOLE_CMD\t\t/* Console command */":
                general_config_file[line_num] = "#define CONSOLE_CMD\t\t/* Console command */\n"

        with open(os.path.join(self.src_path, "config/console.h"), "w") as f:
            f.writelines(console_config_file)

        with open(os.path.join(self.src_path, "config/general.h"), "w") as f:
            f.writelines(general_config_file)

    def compile_ipxe(self):
        os.chdir(self.src_path)
        os.system("make bin/undionly.kpxe EMBED=chainload.ipxe TRUST=ca.cer")
        copyfile(os.path.join(self.src_path, "bin/undionly.kpxe"), os.path.join(self.git_repo_path, "tftpboot/undionly.kpxe"))

def check_ip_in_network(address, network):
    for ip in list(network.hosts()):
        if ip == address:
            return True

    return False

# DHCP Configuration
def dhcp_setup():
    gateway_input = input("Which is the gateway address of the network? (ex: 192.168.1.1) ")
    netmask_input = input("Which is the netmask address of the network? (ex: 24) ")

    gateway_ip = ipaddress.IPv4Address(gateway_input)

    network = ipaddress.IPv4Network(str(gateway_ip) + "/" + netmask_input, strict=False)
    network_ip = network.network_address
    broadcast_ip = network.broadcast_address
    netmask = network.netmask

    dns_input = input("Please, specify the DNS servers (separating them with a comma and a space) (ex: 1.1.1.1, 1.0.0.1) ")

    server_address_input = input("Which is the ip address of this machine where the clients are going to connect? (ex: 192.168.1.5) ")
    server_address = ipaddress.IPv4Address(server_address_input)

    if not check_ip_in_network(server_address, network):
        print("The address you entered was outside the network!")
        sys.exit(1)

    range_start_input = input("What's the first ip address that the DNS is going to lease? (ex: 192.168.1.10) ")
    range_start_ip = ipaddress.IPv4Address(range_start_input)

    if not check_ip_in_network(range_start_ip, network):
        print("The address you entered was outside the network!")
        sys.exit(1)

    range_end_input = input("And the last one? (ex: 192.168.1.25) ")
    range_end_ip = ipaddress.IPv4Address(range_end_input)

    if not check_ip_in_network(range_end_ip, network):
        print("The address you entered was outside the network!")
        sys.exit(1)

    with open(os.path.join(ORIGINAL_EXECUTION_PATH_DIRECTORY, "dhcp-server/conf/dhcpd.conf.example"), "r") as f:
        dhcp_config = f.readlines()

    for line_num, line in enumerate(dhcp_config):
        if line.startswith("option routers"):
            dhcp_config[line_num] = "option routers {};\n".format(str(gateway_ip))

        elif line.startswith("option subnet-mask"):
            dhcp_config[line_num] = "option subnet-mask {};\n".format(str(netmask))

        elif line.startswith("option broadcast-address"):
            dhcp_config[line_num] = "option broadcast-address {};\n".format(str(broadcast_ip))

        elif line.startswith("option domain-name-servers"):
            dhcp_config[line_num] = "option domain-name-servers {};\n".format(str(dns_input))

        elif line.startswith("next-server"):
            dhcp_config[line_num] = "next-server {};\n".format(str(server_address))

        elif line.startswith("subnet"):
            dhcp_config[line_num] = "subnet {} netmask {} {{\n".format(str(network_ip), str(netmask))

        elif line.startswith("  range"):
            dhcp_config[line_num] = "  range {} {};".format(str(range_start_ip), str(range_end_ip))

    with open(os.path.join(ORIGINAL_EXECUTION_PATH_DIRECTORY, "dhcp-server/conf/dhcpd.conf"), "w") as f:
        f.writelines(dhcp_config)

def setup():
    install_input = input("Do you want to install the packages to all the users? [y/N]: ")
    if install_input.startswith("y") or install_input.startswith("Y"):
        install_requirements(True)

    else:
        install_requirements()

    ipxe = iPXE()
    ipxe.clone_repo()
    ipxe.generate_chainload_script()

    ca_input = input("Do you want to use a custom CA certificate? (If not, it's going to use the Let's Encrypt one) (if not sure, just hit enter) [y/N]: ")
    if ca_input.startswith("y") or ca_input.startswith("Y"):
        file_input = input("Please, introduce the path of the file: ")
        ipxe.create_ca_certificate(file_input)

    else:
        ipxe.create_ca_certificate()

    ipxe.modify_compilation_options()
    ipxe.compile_ipxe()

    dhcp_input = input("Do you want to configure the DHCP server? [Y/n]")
    if dhcp_input.startswith("y") or dhcp_input.startswith("Y") or dhcp_input == "":
        dhcp_setup()

    os.chdir(ORIGINAL_EXECUTION_PATH_DIRECTORY)
    os.system("touch .setup")


if __name__ == "__main__":
    if not os.path.isfile(".setup"):
        setup()

    else:
        recompile_input = input("Do you want to recompile the iPXE binary? [y/N]")
        if recompile_input.startswith("y") or recompile_input.startswith("Y"):
            ipxe = iPXE()
            ipxe.compile_ipxe()

    os.system("sudo docker-compose up -d")
