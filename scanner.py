#!/usr/bin/env python

import subprocess
import argparse

# Arguments Parser
parser = argparse.ArgumentParser()
parser.add_argument("-F", "--fullscan", metavar="[yes/no]", action='store_const', const=True, default=False, help="Do a full scan")
parser.add_argument("-ip", help="IP address")

args = parser.parse_args()

def bash(command, sudo=False):
    commands = ['bash', '-c', command]
    if(sudo):
        commands.insert(0, 'sudo')
    return subprocess.check_output(commands)

def nmap_scan(ip):
    print("Scanning TCP ports on %s" % ip)
    res = bash('nmap -T4 -p- %s | grep "open"' % ip)
    print(res)

    ports = []
    for port in res.splitlines():
        ports.append(port.split("/")[0])
    return ",".join(ports)
    

def nmap_scan_full(ip, port_list):
    file_name = 'nmap_output_%s.txt' % ip

    print("\nRunning intense scan on open ports...\n")
    bash('nmap -T4 -A -sV -p%s -oN %s %s' % (port_list, file_name, ip))
    print("NMap intense scan results logged in '%s'" % file_name)
    exit()

if __name__ == "__main__":
  ip_to_scan = ""
  if(args.ip):
          ip_to_scan = args.ip
  else:
    result = subprocess.check_output(['bash', '-c', 'ifconfig eth0'])

    ip_string = bash('ifconfig eth0 | grep "inet"')
    ip = ip_string.strip().split(" ")[1]
    print("Your IP address is: " + ip)

    octets = ".".join(ip.split(".")[:-1])
    subnet = octets + ".0/24"
    print("Running netdiscover on local subnet: %s " % subnet)

    discovered_ips = bash('netdiscover -P -r %s | grep "1" | cut -d " " -f2 ' % subnet, sudo=True).splitlines()
    ips = [x for x in discovered_ips if "Active" not in x]
    sorted_ips = sorted(ips, key = lambda ip: [int(ip) for ip in ip.split(".")] )

    for i in range(0, len(sorted_ips)):
      ip = sorted_ips[i]
      print("%s - %s" % (i + 1, ip))

      choice = input("Enter an option 1 - %s, or 0 to enter manually: " % len(ips))
      ip_to_scan = sorted_ips[choice - 1] if (choice != 0) else raw_input("Enter IP manually: ")
  ports = nmap_scan(ip_to_scan)

  if(args.fullscan):
    nmap_scan_full(ip_to_scan, ports)
  else:
    choice_full_scan = args.fullscan if (args.fullscan) else raw_input("Would you like to do an intense scan? [y/n]: ")

    if(choice_full_scan.lower() == 'yes' or choice_full_scan.lower() == 'y'):
        nmap_scan_full(ip_to_scan, ports)