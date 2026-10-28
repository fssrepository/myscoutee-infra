#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

usage() {
  cat <<'EOF'
Usage:
  ./lab.sh up kvm|kvm-local|libvirt|vmware ansible|puppet
  ./lab.sh apply ansible|puppet
  ./lab.sh ssh [-c command]
  ./lab.sh verify|status|halt|destroy
EOF
  exit 2
}

require_vagrant() {
  local local_bin="$HOME/.local/opt/vagrant/2.4.9/vagrant"
  if [[ -x "$local_bin" ]]; then
    VAGRANT_BIN="$local_bin"
    export VAGRANT_HOME="$HOME/.local/share/myscoutee-infra/vagrant-home"
  elif command -v vagrant >/dev/null; then
    VAGRANT_BIN="$(command -v vagrant)"
  else
    echo 'Vagrant is required; run ./setup-vagrant.sh.' >&2
    exit 1
  fi
  if [[ -f tmp/vagrant-active-local-box ]]; then
    export MSC_LOCAL_UBUNTU24=1
  else
    export MSC_LOCAL_UBUNTU24=0
  fi
}

validate_tool() {
  case "$1" in ansible|puppet) ;; *) usage ;; esac
}

require_kvm() {
  for command_name in qemu-system-x86_64 qemu-img rsync; do
    command -v "$command_name" >/dev/null || {
      echo "Missing host command for KVM: $command_name" >&2
      exit 1
    }
  done
  [[ -r /dev/kvm && -w /dev/kvm ]] || {
    echo 'KVM access is required: check /dev/kvm permissions.' >&2
    exit 1
  }
}

case "${1:-}" in
  up)
    [[ $# == 3 ]] || usage
    validate_tool "$3"
    require_vagrant
    if [[ -f tmp/vagrant-active-local-box && $2 != kvm-local ]]; then
      echo 'This lab has a local-image VM; use kvm-local or destroy it before switching.' >&2
      exit 1
    fi
    if [[ ! -f tmp/vagrant-active-local-box && $2 == kvm-local &&
          -d .vagrant/machines/default/qemu ]]; then
      echo 'This lab already has a standard QEMU VM; destroy it before switching.' >&2
      exit 1
    fi
    case "$2" in
      kvm) require_kvm; provider=qemu; export MSC_LOCAL_UBUNTU24=0 ;;
      kvm-local)
        require_kvm
        [[ -f tmp/vagrant-local-box-ready ]] || {
          echo 'Local box is missing; run ./setup-local-box.sh first.' >&2
          exit 1
        }
        provider=qemu
        export MSC_LOCAL_UBUNTU24=1
        ;;
      libvirt) provider=libvirt; export MSC_LOCAL_UBUNTU24=0 ;;
      vmware) provider=vmware_desktop; export MSC_LOCAL_UBUNTU24=0 ;;
      *) usage ;;
    esac
    if [[ $MSC_LOCAL_UBUNTU24 == 1 ]]; then
      touch tmp/vagrant-active-local-box
    else
      rm -f tmp/vagrant-active-local-box
    fi
    MSC_CONFIG_TOOL="$3" "$VAGRANT_BIN" up --provider="$provider"
    ;;
  apply)
    [[ $# == 2 ]] || usage
    validate_tool "$2"
    require_vagrant
    "$VAGRANT_BIN" rsync
    MSC_CONFIG_TOOL="$2" "$VAGRANT_BIN" provision --provision-with configure
    ;;
  verify)
    [[ $# == 1 ]] || usage
    require_vagrant
    "$VAGRANT_BIN" ssh -c 'curl -fsS http://127.0.0.1:8080/nginx-health | grep -qx UP && curl -fsS http://127.0.0.1:8080/lab/status.json | grep -q "\"status\":\"ready\"" && grep -qxE "ansible|puppet" /etc/myscoutee-lab/tool'
    curl -fsS http://127.0.0.1:18080/ | grep -q 'MyScoutee configuration lab'
    echo 'Guest and forwarded-port checks passed.'
    ;;
  ssh)
    require_vagrant
    shift
    "$VAGRANT_BIN" ssh "$@"
    ;;
  status|halt|destroy)
    [[ $# == 1 ]] || usage
    require_vagrant
    "$VAGRANT_BIN" "$1"
    if [[ $1 == destroy ]]; then rm -f tmp/vagrant-active-local-box; fi
    ;;
  *) usage ;;
esac
