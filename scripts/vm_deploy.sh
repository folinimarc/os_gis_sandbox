#!/bin/bash
# Idempotent server bootstrap: UFW, swap, Docker, repo sync, and compose deployment

set -euo pipefail

REPO_URL="https://github.com/folinimarc/os_gis_sandbox.git"
REPO_BRANCH="test/reverse_proxy"
REPO_DIR="/opt/os_gis_sandbox"
SWAPFILE="/swapfile"
SWAPSIZE="6G"
SWAPPINESS="10"
ENV_FILE=".env"

require_root() {
  if [[ $(id -u) -ne 0 ]]; then
    echo "This script must be run as root."
    exit 1
  fi
}

parse_args() {
  if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <hostname> <username> <password>"
    exit 1
  fi

  HOSTNAME="$1"
  USERNAME="$2"
  PASSWORD="$3"
}

set_kv() {
  local file="$1" key="$2" val="$3"
  if grep -qE "^${key}=" "$file"; then
    sed -i "s|^${key}=.*|${key}=${val}|" "$file"
  else
    echo "${key}=${val}" >> "$file"
  fi
}

ensure_line() {
  local file="$1" line="$2"
  grep -Fqx "$line" "$file" 2>/dev/null || echo "$line" >> "$file"
}

configure_ufw() {
  apt-get install -y ufw
  ufw default deny incoming
  ufw default allow outgoing

  for port in 22 80 443 5432; do
    ufw allow "${port}/tcp"
  done

  if ! ufw status | grep -q "^Status: active"; then
    ufw --force enable
  fi
}

configure_swap() {
  if [[ ! -f "$SWAPFILE" ]]; then
    if ! fallocate -l "$SWAPSIZE" "$SWAPFILE" 2>/dev/null; then
      truncate -s "$SWAPSIZE" "$SWAPFILE"
    fi
    chmod 600 "$SWAPFILE"
    mkswap "$SWAPFILE" >/dev/null
  fi

  ensure_line /etc/fstab "$SWAPFILE none swap sw 0 0"

  if ! swapon --show=NAME --noheadings --raw 2>/dev/null | grep -qx "$SWAPFILE"; then
    swapon "$SWAPFILE"
  fi

  printf "vm.swappiness=%s\n" "$SWAPPINESS" > /etc/sysctl.d/99-swappiness.conf
  sysctl -w "vm.swappiness=${SWAPPINESS}" >/dev/null
}

install_docker() {
  if command -v docker >/dev/null 2>&1; then
    return
  fi

  apt-get install -y ca-certificates curl
  install -m 0755 -d /etc/apt/keyrings

  if [[ ! -f /etc/apt/keyrings/docker.asc ]]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
  fi

  if [[ ! -f /etc/apt/sources.list.d/docker.list ]]; then
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
      > /etc/apt/sources.list.d/docker.list
  fi

  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
}

sync_repo() {
  if [[ -d "$REPO_DIR/.git" ]]; then
    git -C "$REPO_DIR" fetch --all --prune
    git -C "$REPO_DIR" checkout "$REPO_BRANCH"
    git -C "$REPO_DIR" pull --ff-only
  else
    mkdir -p "$(dirname "$REPO_DIR")"
    git clone -b "$REPO_BRANCH" "$REPO_URL" "$REPO_DIR"
  fi
}

deploy_stack() {
  cd "$REPO_DIR"

  cat sandbox.conf sandbox.deploy.conf > "$ENV_FILE"
  chmod 600 "$ENV_FILE"

  set_kv "$ENV_FILE" "OSGS_HOSTNAME" "$HOSTNAME"
  set_kv "$ENV_FILE" "OSGS_USERNAME" "$USERNAME"
  set_kv "$ENV_FILE" "OSGS_PASSWORD" "$PASSWORD"

  docker compose -f compose.yml -f compose.deploy.yml -f compose.build.yml \
    --env-file "$ENV_FILE" up -d
}

main() {
  require_root
  parse_args "$@"

  apt-get update
  configure_ufw
  configure_swap
  install_docker
  sync_repo
  deploy_stack
}

main "$@"