# Workstation provisioning

Provision a work or personal laptop running Debian or macOS. Run the main
playbook locally as the login account you want to configure. Ansible detects
the account, home directory, and OS; it does not create or rename that account.

## Setup and use

Install Ansible and mise first. macOS also needs Homebrew installed and available
on PATH. Your existing SSH identity must be able to access the private secrets
and dotfile repositories. On Debian, the login account needs working sudo.

```sh
mise run project-setup
mise run check
mise run provision-work
# Or, on your personal laptop:
mise run provision-personal
```

Both profiles install development tools, mise-managed Node LTS, Rust, Pulumi,
AI tools, shell/editor configuration, Docker (OrbStack on macOS), personal
secrets, and system/desktop preferences. The personal profile also enables
Syncthing and personal apps. Work leaves messaging/media apps out.
Debian keeps its existing APT sources and release; provisioning does not
switch the machine to testing or install third-party media repositories.

System tasks use sudo; user configuration stays under the login account.
The password prompt is for sudo, not account creation. On a work Mac without
sudo tasks enabled, you can run `ansible-playbook site.yml -e workstation_profile=work`
without `--ask-become-pass`.

## Optional Debian account bootstrap

If Debian's installer already created your account and granted sudo access,
skip this. Otherwise, as root on your personal Debian laptop with Ansible
installed, run:

```sh
ansible-playbook playbooks/bootstrap.yml
passwd gdario
```

The bootstrap installs sudo and creates `gdario` as a sudo-group member, using
ordinary password-based sudo. It neither sets a default password nor enables
passwordless sudo. Log in as `gdario` before running workstation provisioning.
`mise run bootstrap` is equivalent if mise is available to root.

## Configuration

Defaults are in `playbooks/group_vars/all.yml`; package lists have one owner
per OS in `playbooks/vars/`. Override feature switches with `-e`:

```sh
ansible-playbook site.yml -e workstation_profile=work \
  -e install_docker=false -e install_ai_tools=false --ask-become-pass
```

Other switches are `configure_secrets`, `configure_system`, `is_gui_enabled`,
`install_personal_apps`, and `configure_touchid_sudo` (off by default).
`node_version` defaults to `lts`. The main playbook rejects root execution and
profiles other than `work` and `personal`. It does not change the login shell.

`mise run check` validates syntax and the four OS/profile combinations without
installing anything. For a machine-specific preview, run
`ansible-playbook site.yml --check --diff --ask-become-pass`.
Installer scripts, Git clones, and service/login-item startup are skipped in
check mode; a preview cannot verify those steps or private repository access.
The read-only Git and login-item probes may still execute. Provisioning has
not been integration-tested on freshly installed laptops.

Existing local changes in dotfile repositories are preserved rather than
forcibly overwritten. Replacing fnm with mise does not uninstall an existing
fnm installation or rewrite configuration in your external dotfile repositories.
