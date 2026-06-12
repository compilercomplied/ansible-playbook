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
If you are running the playbook on a system that is already provisioned with a user (such as a corporate-managed Mac or Linux machine), or if you want to run the playbook for a specific target user, you can configure these options:

*   `target_user`: The user account to configure (defaults to `gdario`).
*   `skip_user_creation`: Set to `true` to skip the OS-level user creation task (ideal for pre-provisioned corporate laptops).
*   `create_user_home`: Set to `false` to skip creating the home directory during user creation (defaults to `true`).
*   `home_dir`: The path to the user's home directory. By default, this is dynamically resolved based on the OS (`/Users/{{ target_user }}` on macOS/Darwin, `/home/{{ target_user }}` on Debian/Linux), but can be fully overridden.

**Example: Running on a corporate laptop with a pre-existing user**
```bash
ansible-playbook site.yml --tags workstation -e "target_user=your_username skip_user_creation=true" --ask-become-pass
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
