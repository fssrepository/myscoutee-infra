# frozen_string_literal: true

tool = ENV.fetch('MSC_CONFIG_TOOL', 'ansible')
abort "MSC_CONFIG_TOOL must be ansible or puppet" unless %w[ansible puppet].include?(tool)
local_box = ENV['MSC_LOCAL_UBUNTU24'] == '1'

Vagrant.configure('2') do |config|
  if local_box
    config.vm.box = 'myscoutee/local-ubuntu24'
    config.ssh.username = 'lab'
    config.ssh.private_key_path = 'tmp/kvm-demo/id_ed25519'
    config.ssh.insert_key = false
  else
    config.vm.box = 'bento/ubuntu-22.04'
    config.vm.box_version = '202502.21.0'
  end
  config.vm.hostname = 'myscoutee-config-lab'
  sync_target = local_box ? '/home/lab/infra' : '/vagrant'
  config.vm.synced_folder '.', sync_target, type: 'rsync',
                          rsync__exclude: ['.git/', '.vagrant/', 'tmp/']
  config.vm.network 'forwarded_port', guest: 8080, host: 18080,
                    host_ip: '127.0.0.1', auto_correct: false

  config.vm.provider 'libvirt' do |provider|
    provider.memory = 1536
    provider.cpus = 2
  end
  config.vm.provider 'qemu' do |provider|
    provider.memory = '1536M'
    provider.smp = '2'
  end
  config.vm.provider 'vmware_desktop' do |provider|
    provider.vmx['memsize'] = '1536'
    provider.vmx['numvcpus'] = '2'
  end

  config.vm.provision 'shell', name: 'bootstrap', path: 'provision/bootstrap.sh'
  config.vm.provision 'shell', name: 'configure', path: 'provision/configure.sh',
                      env: { 'MSC_CONFIG_TOOL' => tool }
end
