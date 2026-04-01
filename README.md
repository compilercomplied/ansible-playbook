# Ansible Playbook

Personal Ansible playbook for system provisioning and management.

## Prerequisites

Ensure `git` and `ansible` are installed:

```bash
sudo apt update && sudo apt install -y git ansible
```

### macOS App Store (MAS)

For Mac App Store apps to be installed via the `mas` CLI, you **must be signed into the App Store** on your machine. The `mas` tool cannot perform the initial sign-in for you. Additionally, any app you wish to install must have been previously "purchased" (associated with your Apple ID), even if it is a free app.

## Usage

### Update Workstation

To update the local workstation with the `workstation` tag. The `--ask-become-pass` (or `-K`) argument is required for tasks that need administrative privileges.

Note that `is_gui_enabled` and `install_docker` both default to `true`.

```bash
# Run with GUI applications and Docker (default)
ansible-playbook site.yml --tags workstation --ask-become-pass

# Run without GUI applications
ansible-playbook site.yml --tags workstation -e "is_gui_enabled=false" --ask-become-pass

# Run without Docker
ansible-playbook site.yml --tags workstation -e "install_docker=false" --ask-become-pass
```