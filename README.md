# MyScoutee infrastructure configuration lab

This repository contains a disposable Ubuntu VM lab for comparing **Ansible**
and **Puppet** on one MyScoutee-shaped task: configure a small nginx edge with
the same `/nginx-health` response used by the application gateway. The page and
JSON status are synthetic; this lab does not install or contact the backend.

## Requirements

- For the default KVM path: QEMU, accessible `/dev/kvm`, `curl`, `unzip` and
  `sha256sum` on the host. Run `./setup-vagrant.sh` to install pinned Vagrant
  2.4.9 and `vagrant-qemu` in your user directory without sudo.
- Optional: `vagrant-libvirt` with working system libvirt, or
  `vagrant-vmware-desktop` with VMware Workstation/Fusion and its Vagrant
  utility. These providers require separate host setup.
- An x86-64 host with about 2 GiB free RAM and around 15 GiB free disk for
  the VM, box and packages. Without the local image described below, the first
  start downloads roughly 2 GiB for the pinned `bento/ubuntu-22.04` box
  (202502.21.0), plus Ubuntu packages. Later starts reuse the cached box.
- `rsync` and `curl` on the host. Port `127.0.0.1:18080` must be free.

No backend or application service is changed. Vagrant creates its own VM and
`./lab.sh destroy` removes that VM. The optional local-box route stops and
copies the earlier demo VM's disk; it leaves that source disk intact.

The setup script downloads Vagrant from
[HashiCorp releases](https://releases.hashicorp.com/vagrant/2.4.9/), checks the
published SHA-256 digest, and installs the QEMU provider plugin in an isolated
Vagrant home. The QEMU plugin imports a `libvirt` disk-format box while
running the VM directly with QEMU/KVM. The VMware path requires its utility before its provider plugin;
the [libvirt](https://vagrant-libvirt.github.io/vagrant-libvirt/installation.html)
and [VMware](https://developer.hashicorp.com/vagrant/docs/providers/vmware/installation)
instructions cover those optional paths.

## VM tool and configuration tool

Vagrant owns the disposable VM in this repository; Ansible or Puppet manages
packages, files and the nginx service inside it. The existing integration is
`./lab.sh up kvm ansible` -> Vagrant QEMU/KVM -> shell provisioning ->
`provision/configure.sh` -> `ansible-playbook`. Selecting `puppet` runs
`puppet apply` through the same provisioner.

Terraform could own this lab's VM, disk and network instead of Vagrant. It
would still need an explicit step to transfer the lab files and run Ansible or
Puppet in the guest. This repo has no Terraform-managed lab VM. The Terraform
configuration in `../myscoutee-microservices/infra/terraform` is for a separate
k3s VM; this sandbox does not deploy or configure `myscoutee-backend`.

## Start and compare

On this host, the previous direct-QEMU demo left an Ubuntu 24.04 disk and SSH
key under `tmp/kvm-demo/`. To reuse that image without another box download,
stop the direct demo VM and register the disk as a local Vagrant box:

```sh
./setup-vagrant.sh
./setup-local-box.sh
```

`setup-local-box.sh` flattens the demo disk into a user-local box. It checks
that the direct VM is stopped and needs the existing disk and key. The local
box is kept outside Git. Start it explicitly with `./lab.sh up kvm-local
ansible`; the regular `kvm` path stays portable and uses the pinned Bento
Ubuntu 22.04 box on a fresh machine. The local image already has Ansible and
Puppet, so bootstrap skips package downloads on that path.

```sh
./setup-vagrant.sh            # needed once on each host
./lab.sh up kvm ansible       # portable QEMU/KVM path; downloads Bento box once
# or: ./lab.sh up kvm-local ansible  # this host's existing Ubuntu 24.04 disk
./lab.sh verify
./lab.sh apply puppet         # same VM; Puppet takes ownership
./lab.sh verify
./lab.sh apply ansible        # switch back
./lab.sh verify
./lab.sh halt
```

Open <http://127.0.0.1:18080/>. The checks expect `UP` at `/nginx-health`, a
synthetic status at `/lab/status.json`, and the MyScoutee lab page. Run
`./lab.sh apply ansible` (or `puppet`) twice: the second run should report no
managed changes. For a drift exercise, change the page inside the VM, then
reapply the selected tool:

```sh
./lab.sh ssh -c 'sudo sh -c "echo drift > /srv/myscoutee-lab/index.html"'
./lab.sh apply ansible       # use puppet if that is the selected tool
./lab.sh verify
```

The page at port 18080 is the **result** of configuration management, not an
Ansible or Puppet control panel. In this lab, the interfaces are the terminal
output of `ansible-playbook` and `puppet apply`, plus their source files under
`ansible/` and `puppet/`. For separate web consoles, Ansible has
[AWX](https://docs.ansible.com/ecosystem.html) and Puppet has the
[Puppet Enterprise console](https://help.puppet.com/pe/current/topics/complete_install_log_in.htm);
neither is installed by this lab.

In the terminal, Ansible names each task and prints `ok` when a resource is
already correct or `changed` when it modifies the guest. Its `PLAY RECAP`
summarizes the run. Puppet compiles a catalog and prints a resource `Notice`
when it changes something; a repeat run has no resource-change notice. The
[manual](guides/publication/manuals/MyScoutee_Infrastructure_Config_Lab_Guide_EN.pdf)
explains the terms, Vagrant/Terraform roles, components, seven-step comparison
method and annotated terminal excerpts before the command runbook.

`./lab.sh status` shows the VM; `./lab.sh destroy` removes this lab VM and its
guest data. A provider is selected only on first `up`; use the same provider
for that VM. `kvm` selects the rootless QEMU provider with KVM acceleration;
`libvirt` selects the system libvirt provider. `kvm-local` selects the optional
box made from the previous demo image; after `up`, apply/verify/status use
that selected VM. The wrapper rejects unknown tools/providers. Run `./lab.sh ssh` to open the guest without adding the
user-local Vagrant binary to your shell PATH.

## Layout and ownership

| Path | Purpose |
| --- | --- |
| `Vagrantfile`, `lab.sh` | Disposable VM and host-side commands |
| `setup-vagrant.sh` | Reproducible, user-local Vagrant and QEMU provider setup |
| `provision/bootstrap.sh` | Installs Ansible/Puppet in the guest and disables the Puppet agent daemon |
| `ansible/site.yml` | Ansible desired state |
| `puppet/site.pp` | Puppet desired state |
| `shared/` | The same nginx configuration and content used by both tools |
| `guides/publication/manuals/` | Versioned, branded PDF and its source |

The lab copies files from Vagrant's `/vagrant` rsync folder. `lab.sh apply`
syncs current sources before provisioning. Keep the repository checked out.
The two tools intentionally manage the same files for comparison; run one tool
at a time. The marker
`/etc/myscoutee-lab/tool` records which tool last applied.
