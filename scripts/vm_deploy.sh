#!/bin/bash

# This script sets up a server with a configured firewall, installs Docker,
# updates a .env file with user-provided inputs, and starts a Docker-based application.

# Exit when any command fails, unset variables are referenced, and capture errors in pipelines
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

# Assign command line arguments to variables
HOSTNAME="$1"
USERNAME="$2"
PASSWORD="$3"

# Update system packages
apt-get update

# Install and activate UFW to only allow incoming on ports 80, 443, 5432, 22
apt-get install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 5432/tcp # PostgreSQL
ufw allow 22/tcp   # SSH

# Non-interactive UFW enable
echo "y" | ufw enable

# Enable swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
swapon --show

# Install docker
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Clone the repository
git clone -b test/reverse_proxy https://github.com/folinimarc/os_gis_sandbox.git
cd os_gis_sandbox

# Create .env file and replace crucial parameters
sed -i "s/OSGS_HOSTNAME=localhost/OSGS_HOSTNAME=${HOSTNAME}/" sandbox.deploy.conf
sed -i "s/OSGS_USERNAME=os_gis_sandbox/OSGS_USERNAME=${USERNAME}/" sandbox.conf
sed -i "s/OSGS_PASSWORD=you_should_change_this/OSGS_PASSWORD=${PASSWORD}/" sandbox.conf

# Start Sandbox
docker compose -f compose.yml -f compose.deploy.yml --env-file sandbox.conf --env-file sandbox.deploy.conf up -d
