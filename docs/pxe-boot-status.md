# PXE Network Boot Status & Next Steps

This file records the current state of the Debian preseeded network installation setup, the recent debug logs, and our analysis of the boot hang behavior.

---

## Current Status (as of 2026-06-17)

1. **PXE Server Services**:
   * **dnsmasq** is running natively as root on macOS (PID `19888`), binding to `en0` (UDP port 67) for DHCP proxy and serving files via TFTP from `/Users/gdario/pxe-server/tftp`.
   * **Nginx** is running in a Docker container (`pxe-http`) serving the `preseed.cfg` file on port `8080` from `/Users/gdario/pxe-server/http`.
   * **Verbose Logging** is enabled and logging directly to `/Users/gdario/pxe-server/dnsmasq.log`.

2. **Boot Files Deployed**:
   * **BIOS Config**: Simplified `/Users/gdario/pxe-server/tftp/pxelinux.cfg/default` to boot the preseed option immediately (`timeout 1`, `prompt 0`) without loading the VESA graphical menu helper modules (`vesamenu.c32`).
   * **UEFI Config**: GRUB config is at `/Users/gdario/pxe-server/tftp/debian-installer/amd64/grub/grub.cfg`.

3. **Client Machine Behavior**:
   * When booted in **UEFI Mode** (`Arch:00007`), the client's network card fails to communicate/request files. This is due to buggy or nonexistent support for DHCP Proxy (`proxyDHCP`) in the client's UEFI firmware.
   * When booted in **Legacy BIOS Mode** (`Arch:00000`), the client's network card successfully interacts with the proxy DHCP and TFTP server.
   * **The Hang**: Under Legacy BIOS mode, the bootloader starts, loads `pxelinux.0`, requests its configuration `default`, and then starts downloading the Linux kernel (`debian-installer/amd64/linux`).
   * **TFTP Transfer completes**: The 7.9MB `linux` kernel successfully finishes downloading (logged as `sent ... linux`).
   * **The Freeze**: The client screen displays `automatic boot in 1 second...` and hangs there. It does *not* request the initial ramdisk (`debian-installer/amd64/initrd.gz`) or progress to booting.

---

## Guesses & Analysis of the Hang

### Guess 1: Slow TFTP Transfer (High Probability)
* **Explanation**: The initial ramdisk `initrd.gz` is **39 MB**. Over a standard TFTP connection (using default 512-byte block size), transferring 39MB can take **2 to 5 minutes**. 
* During this download, PXELINUX's single-threaded network stack blocks all CPU time, meaning the screen redraw is frozen. The screen will stay frozen at `automatic boot in 1 second...` (or the menu screen) until the download is *entirely finished*.
* Because `dnsmasq` only logs a TFTP file transfer *after* it has successfully completed, there will be no logs for `initrd.gz` while it is in progress.
* **Next Steps**: Leave the machine running for 5–10 minutes at the frozen screen to see if `initrd.gz` completes downloading and boots the installer.

### Guess 2: TFTP Block Size Limitation
* **Explanation**: If the transfer is indeed stalling or timing out, it might be due to the default 512-byte block size causing packet drops or timeouts over Wi-Fi.
* **Next Steps**: We can optimize TFTP transfer speed in `/opt/homebrew/etc/dnsmasq.conf` by adding:
  ```ini
  # Set TFTP block size to 1468 (optimal for Ethernet MTU 1500) to speed up downloads
  tftp-max-blocksize=1468
  ```
  This reduces the number of packets required for `initrd.gz` from ~80,000 to ~27,000, speeding up the download by 3x.

### Guess 3: Memory Fragmentation / Real Mode Limit
* **Explanation**: In legacy BIOS (16-bit real mode), PXELINUX might fail to allocate a large contiguous chunk of memory for a 39MB initrd + 8MB kernel, causing a silent crash immediately after loading the kernel.
* **Next Steps**: If it continues to hang, we can chainload **iPXE** (`undionly.kpxe`), which has modern memory management and supports fetching the kernel/initrd over HTTP (`http://.../linux` and `http://.../initrd.gz`) instead of TFTP. HTTP is virtually instantaneous on a local network and avoids BIOS real-mode limitations.

---

## Commands to Resume/Manage

* **Check dnsmasq logs**:
  ```bash
  tail -f /Users/gdario/pxe-server/dnsmasq.log
  ```
* **Verify HTTP server**:
  ```bash
  curl http://localhost:8080/preseed.cfg
  ```
* **Clean Stop Services**:
  ```bash
  mise run run:bare-metal-stop
  ```
