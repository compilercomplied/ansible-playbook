# Agent Guidelines

For running project commands, the preferred method is to use the tasks defined in [mise.toml](file:///Users/gdario/code/ansible-playbook/mise.toml).

Using `mise` ensures scoped actions run natively with guaranteed toolchains and environments. Always refer to `mise.toml` for standard automation tasks rather than running raw commands.

## Privilege Escalation & User Space

Always prioritize user-space configurations and operations when implementing automation (especially for workstations). Avoid baking privilege escalation (`become: true`/`sudo`) into tasks or scripts unless it is absolutely necessary. 

Before introducing any tasks that require root/sudo access or escape user-space, **always ask the human** for confirmation and design alignment before committing it to the codebase.

