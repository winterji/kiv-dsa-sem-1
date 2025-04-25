#
# *** Obarvovani
# Create N backend nodes and 1 frontend node working as a load-balancer.
#

VAGRANTFILE_API_VERSION = "2"
# set docker as the default provider
ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'
# disable parallellism so that the containers come up in order
ENV['VAGRANT_NO_PARALLEL'] = "1"
ENV['FORWARD_DOCKER_PORTS'] = "1"
# minor hack enabling to run the image and configuration trigger just once
ENV['VAGRANT_EXPERIMENTAL']="typed_triggers"

unless Vagrant.has_plugin?("vagrant-docker-compose")
  system("vagrant plugin install vagrant-docker-compose")
  puts "Dependencies installed, please try the command again."
  exit
end

# Names of Docker images built:
NODE_IMAGE  = "dsa/sem-1/node:0.1"
MONITOR_IMAGE = "dsa/sem-1/monitor:0.1"

# Node definitions
MONITOR  = { :name => "monitor",  # name of the monitor node
              :ipaddr => "10.0.1.10",
              :image => MONITOR_IMAGE,
              # :lb_name => "node-lb",  # NGINX upstream load-balancing group
              # :lb_config_file => "monitor/config/backend-upstream.conf" # generated config.
            }
NODES  = { :nameprefix => "node-",  # backend nodes get names: backend-1, backend-2, etc.
              :subnet => "10.0.1.",
              :ip_offset => 100,  # backend nodes get IP addresses: 10.0.1.101, .102, .103, etc
              :image => NODE_IMAGE,
             }
# Number of backends to start:
NODES_COUNT = 6

# Common configuration
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Before the 'vagrant up' command is started, build docker images:
  config.trigger.before :up, type: :command do |trigger|
    trigger.name = "Build docker images and configuration files"
    trigger.ruby do |env, machine|
      # Build image for backend nodes:
      puts "Building node image:"
      `docker build node -t "#{NODE_IMAGE}"`
      # Build image for the frontend node:
      puts "Building monitor image:"
      `docker build monitor -t "#{MONITOR_IMAGE}"`
      # --- end of Ruby script ---
    end
  end

  # config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: [".*/"]
  config.vm.synced_folder ".", "/vagrant", type: "docker"
  config.ssh.insert_key = false

  # Definition of N nodes
  (1..NODES_COUNT).each do |i|
    node_ip_addr = "#{NODES[:subnet]}#{NODES[:ip_offset] + i}"
    node_name = "#{NODES[:nameprefix]}#{i}"
    # Definition of BACKEND
    config.vm.define node_name do |s|
      s.vm.network "private_network", ip: node_ip_addr
      s.vm.hostname = node_name
      s.vm.provider "docker" do |d|
        d.build_dir = "node"
        d.build_args = ["-t", "#{NODES[:image]}"]
        d.name = node_name
        d.has_ssh = true
      end
      s.vm.post_up_message = "Node #{node_name} up and running. You can access the node with 'vagrant ssh #{node_name}'"
    end
  end

  # Definition of MONITOR
  config.vm.define MONITOR[:name] do |s|
    s.vm.network "private_network", ip: MONITOR[:ipaddr]
    # Forward port 5000 in the container to port 5000 on the host machine. Listen on 0.0.0.0 (all interfaces)
    s.vm.network "forwarded_port", guest: 5000, host: 8080, host_ip: "0.0.0.0"
    s.vm.hostname = MONITOR[:name]
    s.vm.provider "docker" do |d|
      d.build_dir = "monitor"
      d.build_args = ["-t", "#{MONITOR[:image]}"]
      d.name = MONITOR[:name]
      d.has_ssh = true
      d.env = { "STARTUP_DELAY": "10" } # minor hack to ensure backend is already running when the frontend wakes up
    end
    s.vm.post_up_message = "Node #{MONITOR[:name]} up and running. You can access the service at http://localhost:8080/service-api/find/<service>"
  end

end

# EOF
