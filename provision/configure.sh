#!/usr/bin/env bash
set -euo pipefail

if [[ $(id -u) != 0 ]]; then
  echo 'Run this guest provisioner as root (Vagrant shell does this).' >&2
  exit 1
fi

case "${MSC_CONFIG_TOOL:-}" in
  ansible)
    ansible-playbook -i 'localhost,' -c local /vagrant/ansible/site.yml
    ;;
  puppet)
    puppet apply /vagrant/puppet/site.pp
    ;;
  *)
    echo 'MSC_CONFIG_TOOL must be ansible or puppet' >&2
    exit 2
    ;;
esac
