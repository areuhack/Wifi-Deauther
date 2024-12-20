# WiFi Deauther

WiFi Deauther is a Python-based tool designed for ethical hacking and penetration testing. It allows users to scan for WiFi networks in real-time, select a target network, and perform deauthentication attacks on connected devices. The tool is built with a focus on educational use and is intended to test the security of authorized networks only.

## Features

- **Live WiFi Network Scanning**: Continuously scans for available WiFi networks and updates the list in real-time.
- **Network Selection**: Users can select a target network by index after scanning.
- **Deauthentication Attack**: Perform deauth attacks on specific networks or devices to test network security.
- **Graceful Interrupt Handling**: `Ctrl+C` stops scanning but keeps the script running for further operations. A second `Ctrl+C` exits the script.

## Requirements

Before running the script, ensure the following requirements are met:

1. **Operating System**: Linux-based system with support for wireless interfaces (e.g., Kali Linux, Ubuntu).
2. **Python Version**: Python 3.6 or later.
3. **Aircrack-ng Suite**: Includes `airmon-ng`, `airodump-ng`, and `aireplay-ng`.
   - Install with:
     ```bash
     sudo apt install aircrack-ng
     ```
4. **Wireless Adapter**: 
   - Must support monitor mode and packet injection.
   - Use the following command to verify:
     ```bash
     sudo aireplay-ng --test <interface>
     ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/areuhack/Wifi-Deauther.git
   cd wifi-deauther
2. Make the script executable:
   ```bash
   chmod +x live_deauth.py
3. Ensure dependencies are installed:
   ```bash
   sudo apt install python3
## Usage
```bash
sudo python3 wifi_deauther.py
