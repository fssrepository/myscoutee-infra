#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

version=2.4.9
install_dir="$HOME/.local/opt/vagrant/$version"
vagrant_bin="$install_dir/vagrant"
vagrant_home="$HOME/.local/share/myscoutee-infra/vagrant-home"
cache_dir=tmp/vagrant-install
archive="vagrant_${version}_linux_amd64.zip"
sums="vagrant_${version}_SHA256SUMS"
release_url="https://releases.hashicorp.com/vagrant/$version"

for command_name in curl sha256sum unzip; do
  command -v "$command_name" >/dev/null || {
    echo "Missing host command: $command_name" >&2
    exit 1
  }
done

mkdir -p "$cache_dir" "$install_dir" "$vagrant_home"
if [[ ! -x "$vagrant_bin" ]]; then
  [[ -f "$cache_dir/$archive" ]] || curl -fL --retry 3 \
    -o "$cache_dir/$archive" "$release_url/$archive"
  curl -fL --retry 3 -o "$cache_dir/$sums" "$release_url/$sums"
  (cd "$cache_dir" && awk -v name="$archive" '$2 == name { print }' "$sums" | sha256sum -c -)
  unzip -oq "$cache_dir/$archive" -d "$install_dir"
  chmod +x "$vagrant_bin"
fi

export VAGRANT_HOME="$vagrant_home"
"$vagrant_bin" --version
if ! "$vagrant_bin" plugin list | grep -q '^vagrant-qemu (0.7.0,'; then
  "$vagrant_bin" plugin install vagrant-qemu --plugin-version 0.7.0
fi
"$vagrant_bin" plugin list
echo 'Ready: ./lab.sh up kvm ansible'
