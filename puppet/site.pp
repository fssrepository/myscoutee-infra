package { 'nginx':
  ensure => installed,
}

file { '/srv/myscoutee-lab':
  ensure => directory,
  owner  => 'root',
  group  => 'root',
  mode   => '0755',
}

file { '/etc/myscoutee-lab':
  ensure => directory,
  owner  => 'root',
  group  => 'root',
  mode   => '0755',
}

file { '/etc/nginx/conf.d/myscoutee-lab.conf':
  ensure  => file,
  content => file('/vagrant/shared/myscoutee-lab.conf'),
  owner   => 'root',
  group   => 'root',
  mode    => '0644',
  require => Package['nginx'],
}

file { '/srv/myscoutee-lab/index.html':
  ensure  => file,
  content => file('/vagrant/shared/index.html'),
  owner   => 'root',
  group   => 'root',
  mode    => '0644',
  require => File['/srv/myscoutee-lab'],
}

file { '/srv/myscoutee-lab/status.json':
  ensure  => file,
  content => file('/vagrant/shared/status.json'),
  owner   => 'root',
  group   => 'root',
  mode    => '0644',
  require => File['/srv/myscoutee-lab'],
}

file { '/etc/myscoutee-lab/tool':
  ensure  => file,
  content => "puppet\n",
  owner   => 'root',
  group   => 'root',
  mode    => '0644',
  require => File['/etc/myscoutee-lab'],
}

service { 'nginx':
  ensure    => running,
  enable    => true,
  require   => Package['nginx'],
  subscribe => File['/etc/nginx/conf.d/myscoutee-lab.conf'],
}
