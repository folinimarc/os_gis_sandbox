#!/bin/bash
# Idempotent server bootstrap: UFW, swap, Docker, repo config, and Docker Compose app

set -euo pipefail

# Check if the script is run as root
if [[ $(id -u) -ne 0 ]]; then
  echo "This script must be run as root."
  exit 1
fi

# Input validation
if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <hostname> <username> <password>"
  exit 1
fi

HOSTNAME="$1"
USERNAME="$2"
PASSWORD="$3"

REPO_URL="https://github.com/folinimarc/os_gis_sandbox.git"
REPO_BRANCH="test/reverse_proxy"
REPO_DIR="/opt/os_gis_sandbox"

SWAPFILE="/swapfile"
SWAPSIZE="6G"

# Helper: set KEY=VALUE in a file (replace if exists, append if missing)
set_kv() {
  local file="$1" key="$2" val="$3"
  if grep -qE "^${key}=" "$file"; then
    sed -i "s|^${key}=.*|${key}=${val}|" "$file"
  else
    echo "${key}=${val}" >> "$file"
  fi
}

# Update system packages
apt-get update

# Install and activate UFW to only allow incoming on ports 80, 443, 5432, 22
apt-get install -y ufw

# Configure UFW idempotently
ufw default deny incoming
ufw default allow outgoing
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 5432/tcp # PostgreSQL
ufw allow 22/tcp   # SSH

# Enable UFW only if not already enabled (avoids interactive prompt)
if ! ufw status | grep -q "^Status: active"; then
  ufw --force enable
fi

# Enable swap idempotently
if ! swapon --show | awk '{print $1}' | grep -qx "$SWAPFILE"; then
  if [[ ! -f "$SWAPFILE" ]]; then
    fallocate -l "$SWAPSIZE" "$SWAPFILE"
    chmod 600 "$SWAPFILE"
    mkswap "$SWAPFILE"
  fi
  swapon "$SWAPFILE"
fi
swapon --show

# Install docker (skip if already present)
if ! command -v docker >/dev/null 2>&1; then
  apt-get install -y ca-certificates curl

  install -m 0755 -d /etc/apt/keyrings

  # Only (re)download key if missing
  if [[ ! -f /etc/apt/keyrings/docker.asc ]]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
  fi

  # Only write docker repo file if missing
  if [[ ! -f /etc/apt/sources.list.d/docker.list ]]; then
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
      | tee /etc/apt/sources.list.d/docker.list > /dev/null
  fi

  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# Clone or update the repository idempotently
if [[ -d "$REPO_DIR/.git" ]]; then
  git -C "$REPO_DIR" fetch --all --prune
  git -C "$REPO_DIR" checkout "$REPO_BRANCH"
  git -C "$REPO_DIR" pull --ff-only
else
  mkdir -p "$(dirname "$REPO_DIR")"
  git clone -b "$REPO_BRANCH" "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

# Update config files idempotently
# (Works whether keys exist or not; avoids fragile regex on "not spaces")
set_kv "sandbox.deploy.conf" "OSGS_HOSTNAME" "$HOSTNAME"
set_kv "sandbox.conf"        "OSGS_USERNAME" "$USERNAME"
set_kv "sandbox.conf"        "OSGS_PASSWORD" "$PASSWORD"

# Start Sandbox (idempotent by nature; re-running keeps it up-to-date)
docker compose -f compose.yml -f compose.deploy.yml -f compose.build.yml \
  --env-file sandbox.conf --env-file sandbox.deploy.conf up -d
