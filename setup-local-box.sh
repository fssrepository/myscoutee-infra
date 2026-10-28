#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

source_disk=tmp/kvm-demo/disk.qcow2
private_key=tmp/kvm-demo/id_ed25519
box_dir=tmp/vagrant-local-box
box_archive="$box_dir/myscoutee-local-ubuntu24.box"
vagrant_bin="$HOME/.local/opt/vagrant/2.4.9/vagrant"
vagrant_home="$HOME/.local/share/myscoutee-infra/vagrant-home"

for file in "$source_disk" "$private_key" "$vagrant_bin"; do
  [[ -f "$file" ]] || { echo "Missing local prerequisite: $file" >&2; exit 1; }
done
command -v qemu-img >/dev/null || { echo 'Missing qemu-img' >&2; exit 1; }

if [[ -f tmp/kvm-demo/qemu.pid ]] && kill -0 "$(cat tmp/kvm-demo/qemu.pid)" 2>/dev/null; then
  echo 'Stop the direct QEMU demo VM before packaging its disk.' >&2
  exit 1
fi

mkdir -p "$box_dir" "$vagrant_home"
export VAGRANT_HOME="$vagrant_home"
if ! "$vagrant_bin" box list | grep -q '^myscoutee/local-ubuntu24 (libvirt,'; then
  rm -f "$box_dir/box.img" "$box_archive"
  qemu-img convert -f qcow2 -O qcow2 -c "$source_disk" "$box_dir/box.img"
  cat > "$box_dir/metadata.json" <<'EOF'
{"provider":"libvirt","format":"qcow2","virtual_size":12}
EOF
  printf '%s\n' 'Vagrant.configure("2") do |config|' 'end' > "$box_dir/Vagrantfile"
  tar -C "$box_dir" -cf "$box_archive" box.img metadata.json Vagrantfile
  "$vagrant_bin" box add --name myscoutee/local-ubuntu24 "$box_archive" --provider libvirt --force
fi
rm -f "$box_dir/box.img" "$box_dir/metadata.json" "$box_dir/Vagrantfile" "$box_archive"
rmdir "$box_dir" 2>/dev/null || true
touch tmp/vagrant-local-box-ready
echo 'Ready: ./lab.sh up kvm-local ansible (local Ubuntu 24.04 image)'
