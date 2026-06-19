# Ansible Playbook

Personal Ansible playbook for system provisioning and management.

# Design Choices

### Playbook-as-Composition
Instead of using a single "Fat Role" for system types (e.g., a "workstation" role), this project employs a **Composition** model at the playbook level. Each high-level configuration (Workstation, Server) is defined in its own playbook by composing small, atomic, and specialized roles.

**Rationale:**
- **Visibility:** Looking at a playbook like `provision_workstation.yml` provides an immediate, high-level "shopping list" of the environment without digging into role metadata.
- **Atomicity:** Roles like `terminal`, `editor`, and `docker` are kept generic and OS-agnostic where possible. This allows the same `terminal` configuration to be reused on a headless Linux server as easily as on a macOS laptop.
- **Granular Control:** By splitting concerns into atomic roles, we can use Ansible tags (e.g., `--tags terminal`) to update specific parts of the system without running the entire provisioning suite.
- **Lifecycle Management:** Servers and workstations have different update frequencies and risk profiles. Playbook-level separation acknowledges that a "Workstation" is a collection of user-centric tools, while a "Server" is a collection of service-centric runtimes.

## User Configuration

Variables that can be overridden are defined in `playbooks/group_vars/all.yml` and act as the "Public API" for this playbook.

### General Overrides
```bash
ansible-playbook site.yml --tags workstation -e "is_gui_enabled=false install_docker=false" --ask-become-pass
```

### Pre-Provisioned Systems & Custom User Configuration
To keep workstation provisioning safe, compliant, and friction-free on corporate-managed machines, this playbook runs completely in **user-space** by default on macOS:
*   **User Creation:** Bypassed entirely for workstations (as the login account already exists).
*   **Shell Changes:** Bypassed in the playbook. You can change your default shell manually (see below).
*   **Sudo Privilege Escalation:** Disabled by default on macOS, meaning you can run the playbook **without** `--ask-become-pass` or root access.

#### 1. (Optional) Change your default shell to Nushell:
Run this one-time command in your terminal:
```bash
chsh -s ~/.cargo/bin/nu
```

#### 2. Running the playbook:
*   `target_user`: The user account to configure (defaults to `gdario`).
*   `home_dir`: The path to the user's home directory. Resolved dynamically based on the OS (`/Users/{{ target_user }}` on macOS, `/home/{{ target_user }}` on Linux), but can be overridden.
*   `configure_touchid_sudo`: Set to `true` if you have sudo access and want to enable Touch ID for sudo on macOS (defaults to `false`).

**Example: Running on a work Mac (passwordless, user-space execution):**
```bash
ansible-playbook site.yml --tags workstation -e "target_user=your_username"
```

**Example: Running on a personal Mac (with Touch ID sudo configuration):**
```bash
ansible-playbook site.yml --tags workstation -e "target_user=your_username configure_touchid_sudo=true" --ask-become-pass
```

## Prerequisites

Ensure `git` and `ansible` are installed:

```bash
# Linux systems
sudo apt update && sudo apt install -y git ansible
```

### macOS App Store (MAS)

For Mac App Store apps to be installed via the `mas` CLI, you **must be signed into the App Store** on your machine. The `mas` tool cannot perform the initial sign-in for you. Additionally, any app you wish to install must have been previously "purchased" (associated with your Apple ID), even if it is a free app.

## Usage

### Update Workstation

To update the local workstation with the `workstation` tag. The `--ask-become-pass` argument is required for tasks that need administrative privileges.

```bash
# Default run. Assumes a fat laptop is being used (docker, GUIs...)
ansible-playbook site.yml --tags workstation --ask-become-pass
```

### Bare Metal Network Provisioning (PXE & Automated Install)

This project includes fully automated network installation support for provisioning new physical nodes (such as target cluster machines) over the local network via PXE boot and Debian preseeding.

#### 1. Hardware & BIOS Requirements
Before booting the target machine, make sure you configure its BIOS/UEFI settings as follows:
* **Boot Mode:** Select **Legacy Boot** (CSM/BIOS only; UEFI PXE Proxy DHCP is unsupported on some network cards).
* **Storage Mode:** Ensure the SATA/Storage controller is set to **AHCI** mode. *(Note: The Linux kernel will not detect the storage drives if the controller is in Intel RST / RAID / VMD mode).*
* **Boot Order:** Enable network boot (PXE) and set it as the primary boot interface.

#### 2. Start the PXE Boot & HTTP Server
Run the local PXE boot services (dnsmasq for DHCP Proxy/TFTP, and Nginx in Docker to host `preseed.cfg`):
```bash
mise run run:bare-metal-start
```
*(Alternatively: `ansible-playbook site.yml --tags bare-metal --ask-become-pass`)*

#### 3. Perform the Installation
1. Power on the target machine connected to the same local network.
2. It will boot from the network, request a DHCP IP, and download the installer files over TFTP (which takes ~2 minutes).
3. The installer will boot automatically, retrieve `preseed.cfg` via HTTP, automatically partition the primary drive, setup user `gdario` with your workstation's SSH key, and install the base OS completely hands-free.

#### 4. Stop the PXE Server & Clean Up
Once the installation finishes and the machine reboots into the new OS, stop the local PXE boot services to free up ports and system resources:
```bash
mise run run:bare-metal-stop
```
*(Alternatively: `ansible-playbook site.yml --tags bare-metal -e 'pxe_state=stopped' --ask-become-pass`)*

#### 5. Provision the Cluster Node
Once the machine is running Debian, you can configure it (Docker, runtimes, utilities) using the cluster tags:
```bash
ansible-playbook site.yml --limit cluster --tags cluster
```
