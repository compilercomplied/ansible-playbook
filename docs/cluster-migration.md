# Cluster Migration Guide

This document outlines the steps and prerequisites for provisioning and migrating cluster nodes.

## Longhorn Storage Support

Longhorn is used as the distributed block storage system for the cluster. It requires a Container Storage Interface (CSI) that relies on iSCSI on the host nodes.

### Prerequisites

All cluster nodes must have the `open-iscsi` package installed and the `iscsid` daemon running. Without this, Longhorn volume mounts will fail.

### Installation & Setup

Before provisioning the cluster, or if adding new nodes, log into each cluster node and run:

1. **Install the package:**
   ```bash
   sudo apt update && sudo apt install -y open-iscsi
   ```

2. **Enable and start the daemon:**
   ```bash
   sudo systemctl enable --now iscsid
   ```

3. **Verify the service status:**
   ```bash
   sudo systemctl status iscsid
   ```
