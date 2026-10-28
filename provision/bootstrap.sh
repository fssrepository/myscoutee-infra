#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
if ! command -v ansible-playbook >/dev/null ||
   ! command -v puppet >/dev/null ||
   ! command -v curl >/dev/null; then
  apt-get update
  apt-get install -y --no-install-recommends ansible-core puppet curl
fi

# This lab uses puppet apply on demand; no background agent should run.
if [[ -d /run/systemd/system ]]; then
  systemctl disable --now puppet.service
fi
