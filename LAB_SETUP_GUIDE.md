# 🌐 LAN Execution & Lab Setup Guide

This guide explains how to deploy **G.V's Exam Protocol** in a physical lab environment using a central switch (D-Link) and Ethernet cables.

## 1. Physical Infrastructure
*   **Central Node**: D-Link Network Switch or Router.
*   **Cabling**: Cat5e/Cat6 Ethernet cables for all devices.
*   **Server**: Your main laptop where the project is stored.
*   **Nodes**: All student desktop computers.

### Setup Flow:
1.  Connect all student PCs to the D-Link switch.
2.  Connect your Laptop to the same D-Link switch.
3.  Ensure all green lights are flashing on the switch ports.

---

## 2. Server Configuration (Your Laptop)
To ensure students can always find your laptop, you should set a **Static IP**.

### On Windows 11/10:
1.  Open **Settings** > **Network & Internet** > **Ethernet**.
2.  Click **Edit** next to "IP assignment".
3.  Select **Manual** and turn on **IPv4**.
4.  Enter the following values:
    *   **IP address**: `192.168.1.100`
    *   **Subnet mask**: `255.255.255.0`
    *   **Gateway**: `192.168.1.1` (or leave blank if no router is present)
    *   **DNS**: `8.8.8.8`
5.  Click **Save**.

---

## 3. Launching the Exam Server
Open your terminal (PowerShell/CMD) in the project folder and run:

```powershell
# This command makes the server visible to everyone on the LAN
python manage.py runserver 0.0.0.0:8000
```

---

## 4. Student Access
Instruct all students to open their browser (Chrome recommended) and enter your static IP:

> 🌐 **URL**: `http://192.168.1.100:8000`

---

## 5. Critical Troubleshooting
*   **Firewall Issue**: If students can't connect, temporarily disable **Windows Defender Firewall** or create an "Inbound Rule" for Port **8000**.
*   **Ping Test**: From a student PC, open CMD and type `ping 192.168.1.100`. If you get a reply, the connection is active.
*   **IP Mismatch**: Ensure all student PCs are on the same subnet (e.g., `192.168.1.X`).

---

> [!IMPORTANT]
> **Security Protocol**: Ensure that the server laptop is not connected to a public Wi-Fi during the exam to prevent unauthorized external access.
