# Ansible Playbook

Personal Ansible playbook for system provisioning and management.

## Prerequisites

Ensure `git` and `ansible` are installed:

```bash
sudo apt update && sudo apt install -y git ansible
```

## Usage

### Update Workstation

To update the local workstation with the `workstation` tag:

```bash
ansible-playbook --tags workstation site.yml --ask-become-pass
```