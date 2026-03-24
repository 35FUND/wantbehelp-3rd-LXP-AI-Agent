#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script with sudo." >&2
  exit 1
fi

dnf update -y || yum update -y
dnf install -y git nginx || yum install -y git nginx

if ! command -v uv >/dev/null 2>&1; then
  su - ec2-user -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
fi

systemctl enable nginx
systemctl start nginx

echo "Base EC2 bootstrap completed."
