# WiFi Deauther

WiFi Deauther is a Python-based tool designed for ethical hacking and penetration testing. It allows users to scan for WiFi networks in real-time, select a target network, and perform deauthentication attacks on connected devices. The tool is built with a focus on educational use and is intended to test the security of authorized networks only.

## Features

- **Live WiFi Network Scanning**: Continuously scans for available WiFi networks and updates the list in real-time.
- **Network Selection**: Users can select a target network by index after scanning.
- **Deauthentication Attack**: Perform deauth attacks on specific networks or devices to test network security.
- **Graceful Interrupt Handling**: `Ctrl+C` stops scanning but keeps the script running for further operations. A second `Ctrl+C` exits the script.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/wifi-deauther.git
   cd wifi-deauther
