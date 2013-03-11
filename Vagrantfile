# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "debian"
  # FIXME Upload box to a public host
  # config.vm.box_url = "http://domain.com/path/to/above.box"

  config.vm.network :bridged

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "manifests"
    puppet.manifest_file  = "debian.pp"
  end
end
