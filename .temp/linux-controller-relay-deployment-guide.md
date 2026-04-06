# IDN Controller / Relay Linux Deployment Guide

## 1. Purpose

This guide explains how to package, deploy, install, run, update, and troubleshoot the IDN controller and relay on another Linux environment.

The goal of this change is simple:

- The server address is not hardcoded in the binary.
- The operator configures the server in a separate auth file.
- The end user starts the service with only the ID.

Controller:

```bash
sudo idn-controller <controller_id>
```

Relay:

```bash
sudo idn-relay <relay_id>
```

## 2. What Changed

- `idn-controllerd` now supports `idn-controllerd <controller_id>`.
- `idn-edged` now supports `idn-edged <relay_id>`.
- The controller reads the auth server from `/etc/default/idn-controller.auth`.
- The relay reads the auth server from `/etc/default/idn-edge.auth`.
- If `netif` is omitted from the auth file, the default route interface is detected automatically.
- Linux deployment assets were added:
  - install script
  - uninstall script
  - wrapper command
  - systemd service
  - example config

## 3. Package Build

Build packages on a Linux build machine where the source tree can be compiled.

### 3.1 Controller package

```bash
cd /path/to/IDNclient_wg
./scripts/package-controller.sh
```

Output:

- `dist/idn-controller-<YYYYMMDD>.tar.gz`

### 3.2 Relay package

```bash
cd /path/to/IDNclient_wg
./scripts/package-relay.sh
```

Output:

- `dist/idn-relay-<YYYYMMDD>.tar.gz`

### 3.3 Build both

```bash
cd /path/to/IDNclient_wg
./scripts/package-linux-appliances.sh all
```

## 4. Target Host Requirements

This packaging flow is written for Linux systems that use:

- `systemd`
- `bash`
- `sudo`
- `apt-get` for automatic dependency installation

If the target host does not use `apt-get`, installation can still work, but runtime dependencies must be installed manually.

### 4.1 Controller runtime dependencies

- libevent
- libssl
- jansson
- glib2
- libblkid

### 4.2 Relay runtime dependencies

- libevent
- libgtop
- libssl
- jansson
- glib2
- libblkid
- wireguard-tools
- iproute2

## 5. Install Procedure

### 5.1 Controller install

Copy the controller package to the target host and run:

```bash
mkdir -p /tmp/idn-controller-package
tar xzf idn-controller-<YYYYMMDD>.tar.gz -C /tmp/idn-controller-package
cd /tmp/idn-controller-package
sudo ./install.sh --auth-ip <orchestrator-ip> --auth-port <auth-port>
```

Example:

```bash
sudo ./install.sh --auth-ip 61.109.220.75 --auth-port 15004
```

Installed paths:

- binary: `/opt/idn/controller/bin/idn-controllerd`
- wrapper: `/usr/local/bin/idn-controller`
- service: `/etc/systemd/system/idn-controller.service`
- auth config: `/etc/default/idn-controller.auth`
- ID env file: `/etc/default/idn-controller`

### 5.2 Relay install

Copy the relay package to the target host and run:

```bash
mkdir -p /tmp/idn-relay-package
tar xzf idn-relay-<YYYYMMDD>.tar.gz -C /tmp/idn-relay-package
cd /tmp/idn-relay-package
sudo ./install.sh --auth-ip <orchestrator-ip> --auth-port <auth-port>
```

Example:

```bash
sudo ./install.sh --auth-ip 61.109.220.75 --auth-port 15004
```

Installed paths:

- binary: `/opt/idn/relay/bin/idn-edged`
- wrapper: `/usr/local/bin/idn-relay`
- service: `/etc/systemd/system/idn-relay.service`
- auth config: `/etc/default/idn-edge.auth`
- ID env file: `/etc/default/idn-relay`

The relay installer also creates the runtime directories used by the edge process:

- `/var/opt/n2os/backup`
- `/var/opt/n2os/memory`
- `/var/opt/n2os/pid`
- `/var/opt/n2os/sock`
- `/var/opt/n2os/log/var/log/idn.log`

## 6. Auth Server Configuration

The auth server is configured outside the binary.

Controller auth file:

- `/etc/default/idn-controller.auth`

Relay auth file:

- `/etc/default/idn-edge.auth`

Format:

```txt
<orchestrator-ip> <auth-port> [netif]
```

Examples:

```txt
61.109.220.75 15004
```

```txt
61.109.220.75 15004 enp1s0
```

Rules:

- If `netif` is omitted, the program detects the default route interface automatically.
- The first non-empty, non-comment line must contain the auth server.
- The wrapper does not start the service if the auth file is still empty or only contains comments.

## 7. End User Operation

### 7.1 Controller

Register the controller ID and start the service:

```bash
sudo idn-controller test03
```

Other commands:

```bash
idn-controller status
sudo idn-controller stop
sudo idn-controller restart
idn-controller logs
```

### 7.2 Relay

Register the relay ID and start the service:

```bash
sudo idn-relay test03_relay
```

Other commands:

```bash
idn-relay status
sudo idn-relay stop
sudo idn-relay restart
idn-relay logs
```

## 8. Update Procedure

### 8.1 Controller update

```bash
tar xzf idn-controller-<NEW_VERSION>.tar.gz -C /tmp/idn-controller-package
cd /tmp/idn-controller-package
sudo ./install.sh --skip-deps
sudo idn-controller restart
```

### 8.2 Relay update

```bash
tar xzf idn-relay-<NEW_VERSION>.tar.gz -C /tmp/idn-relay-package
cd /tmp/idn-relay-package
sudo ./install.sh --skip-deps
sudo idn-relay restart
```

The install script overwrites binaries and keeps existing auth and ID files unless they do not exist yet.

## 9. Uninstall

### 9.1 Controller

```bash
cd /tmp/idn-controller-package
sudo ./uninstall.sh
```

If config files must also be removed:

```bash
sudo KEEP_CONFIG=0 ./uninstall.sh
```

### 9.2 Relay

```bash
cd /tmp/idn-relay-package
sudo ./uninstall.sh
```

If config files must also be removed:

```bash
sudo KEEP_CONFIG=0 ./uninstall.sh
```

## 10. Troubleshooting

### 10.1 The wrapper says the auth file is not configured

Check the auth file contents:

```bash
cat /etc/default/idn-controller.auth
cat /etc/default/idn-edge.auth
```

The first valid line must look like this:

```txt
61.109.220.75 15004
```

### 10.2 The service does not start

Check systemd status:

```bash
systemctl status idn-controller.service
systemctl status idn-relay.service
```

Check logs:

```bash
journalctl -u idn-controller.service -n 200 --no-pager
journalctl -u idn-relay.service -n 200 --no-pager
```

### 10.3 Relay started but no WireGuard interface or relay port appears

Check:

```bash
ip link show idn-tni
ss -lunp | egrep '30001|51820'
journalctl -u idn-relay.service -n 200 --no-pager
```

If the relay is registered and approved but `idn-tni`, `30001`, or `51820` still do not appear, the cause is no longer the package install path. At that point the issue is in the relay runtime path after registration.

### 10.4 Need to change only the server address

Edit the auth file and restart the service:

```bash
sudo vi /etc/default/idn-controller.auth
sudo vi /etc/default/idn-edge.auth

sudo idn-controller restart
sudo idn-relay restart
```

## 11. Recommended Operational Flow

1. Build controller and relay packages on a Linux build machine.
2. Copy the tarballs to the target hosts.
3. Install each package with `./install.sh --auth-ip ... --auth-port ...`.
4. Start the controller with `sudo idn-controller <controller_id>`.
5. Start the relay with `sudo idn-relay <relay_id>`.
6. Verify registration and approval in the orchestrator.
7. Verify service status and logs on the target host.

This is the intended split:

- installer/operator configures the auth server once
- end user enters only the ID
