#!/usr/bin/python

"""
Create a network with 5 hosts, numbered 1-4 and 9. 
Validate that the port numbers match to the interface name,
and that the ovs ports match the mininet ports.
"""
import os
import sys
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.node import Controller
from mininet.log import setLogLevel, info, warn
from mininet.node import Node
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.link import Link

class CustomTopo(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)

    def create_spine_leaf(self, s, l):
        # spine
        s_arr = []
        for i in range(s):
            s_arr.append(self.addSwitch('s' + str(i + 1)))
        # leaf
        l_arr = []
        for i in range(l):
            l_arr.append(self.addSwitch('s' + str(s + i + 1)))
        # hosts
        h_arr = []
        for i in range(l):
            h_arr.append(self.addHost('h' + str(i + 1)))
        # leaf spine links
        for i in range(s):
            for j in range(l):
                self.addLink(s_arr[i], l_arr[j])
        # host leaf links
        for i in range(l):
            self.addLink(l_arr[i], h_arr[i])


    def create_from_file(self, topo_file):
        global switch_to_root_eth0_name
        config_dict = {}
        print "creating topo from file: {}".format(topo_file)
        fh = open(topo_file, 'r')
        for line in fh:
            if line and line.strip().startswith('#'):
                pass
            else:
                config_args = line.split()
                if len(config_args) == 0:
                    pass
                elif config_args[0] == '1':
                    if len(config_args) < 3:
                        print "error: wrong config for a host {}".format(line)
                        exit(1)
                    # config_args[1]: hostname
                    # config_args[2]: ip address
                    opts = {}
                    if len(config_args) > 2:
                        for opt in config_args[2:]:
                            opts[opt.split('=')[0]] = opt.split('=')[1]
                    config_dict[config_args[1]] = self.addHost(config_args[1], **opts)
                    arguments = ', '.join(config_args[1:])
                    print "host {} added".format(arguments)
                elif config_args[0] == '2':
                    # config_args[1]: switchname
                    opts = {}
                    if len(config_args) > 2:
                        for opt in config_args[2:]:
                            opts[opt.split('=')[0]] = opt.split('=')[1]
                    config_dict[config_args[1]] = self.addSwitch(config_args[1], **opts)
                    arguments = ', '.join(config_args[1:])
                    print "switch {} added".format(arguments)
                elif config_args[0] == '3':
                    if len(config_args) < 3:
                        print "error: wrong config for a link {}".format(line)
                        exit(1)
                    # config_args[1]: host1
                    # config_args[2]: ip address
                    opts = {}
                    if len(config_args) > 3:
                        for opt in config_args[3:]:
                            if opt.split('=')[0] == 'bw':
                                opts[opt.split('=')[0]] = int(opt.split('=')[1])
                            else:
                                opts[opt.split('=')[0]] = opt.split('=')[1]
                    arguments = ', '.join(config_args[1:])
                    self.addLink(config_dict[config_args[1]], config_dict[config_args[2]], **opts)
                    print "link {} added".format(arguments)
                elif config_args[0] == '4':
                    if len(config_args) < 2:
                        print "error: wrong config for switch to root-eth0"
                        exit(1)
                    switch_to_root_eth0_name = config_args[1]
                else: 
                    print "error: invalid config - {}".format(line)
                    exit(1)
       
def connectToRootNS( network, switch, ip, routes ):
    """Connect hosts to root namespace via switch. Starts network.
      network: Mininet() network object
      switch: switch to connect to root namespace
      ip: IP address for root namespace node
      routes: host networks to route to"""
    # Create a node in root namespace and link to switch 0
    root = Node( 'root', inNamespace=False)
    intf = Link( root, switch, port2=20).intf1
    root.setIP( ip, intf=intf)
    # Start network that now includes link to root namespace
    network.start()
    # Add routes from root ns to hosts
    for route in routes:
        root.cmd( 'route add -net ' + route + ' dev ' + str( intf ))
    return root

def net(s, l):
    global switch_to_root_eth0_name
    "Create a network with custom topo"
    topo = CustomTopo()
    topo.create_spine_leaf(s, l)

    info( '*** Starting network ***\n' )
    #if not flowpaths_file:
    #    print "No flows file. Creating a network with default controller"
    #    net = Mininet(topo=topo, controller=None, host=CPULimitedHost, link=TCLink)
    #else: 
    net = Mininet(topo=topo)
    
    # create a node in root namespace and link to switch 0
    routes = ['10.0.0.0/8']
    ip = '10.123.123.1/32'
    print switch_to_root_eth0_name
    rootnode = connectToRootNS(net, net[switch_to_root_eth0_name], ip, routes)

    # Generate and add flows
    #generate_flows(flowpaths_file, topo)
 
    # now run sshd on each host
    cmd = '/usr/sbin/sshd'
    opts = '-D -o UseDNS=no -u0' 
    for host in net.hosts:
        print 'at host:', host
        host.cmd(cmd + ' ' + opts + '&')
    #add_root_eth0_flows(rootnode, switch_to_root_eth0_name, ip)
    #os.system("./flows-tmp")
    # print interface - port number mappings
    print_port_numbers(net)

    print
    print "*** Hosts are running sshd at the following addresses:"
    for host in net.hosts:
        print host.name, host.IP()
    print
    print "*** Type 'exit' or control-D to shut down network"
    CLI(net)
    info( '*** Stopping network ***' )
    net.stop()
    from cleanup import cleanup
    cleanup()

def add_root_eth0_flows(root, switch, ip):
    fh = open('flows-tmp', 'a')
    port_on_root = 20
    fh.write("sudo ovs-ofctl add-flow {} arp,nw_dst=10.123.123.1/32,actions=output:{}\n".format(switch, str(port_on_root)))
    fh.write("sudo ovs-ofctl add-flow {} ip,nw_dst=10.123.123.1/32,actions=output:{}\n".format(switch, str(port_on_root)))
    fh.close()
    os.system("./flows-tmp") 

def install_path(topo, node1, node2, ip, fh):
    print 'Portinfo:', node1, topo.port(node1,node2),  topo.port(node2,node1), node2, ip
    print 'NodeInfo:', topo.nodeInfo(node1)
    if 'isSwitch' in topo.nodeInfo(node1) and topo.nodeInfo (node1)['isSwitch']:
        fh.write("sudo ovs-ofctl add-flow {} priority=500,ip,nw_src={}/32,actions=output:{}\n".format(node1, ip, topo.port(node1, node2)[0]))
        fh.write("sudo ovs-ofctl add-flow {} priority=500,arp,nw_src={}/32,actions=output:{}\n".format(node1, ip, topo.port(node1, node2)[0]))
        
    if 'isSwitch' in topo.nodeInfo(node2) and topo.nodeInfo (node2)['isSwitch']:
        fh.write("sudo ovs-ofctl add-flow {} priority=500,ip,nw_dst={}/32,actions=output:{}\n".format(node2, ip, topo.port(node2,node1)[0]))
        fh.write("sudo ovs-ofctl add-flow {} priority=500,arp,nw_dst={}/32,actions=output:{}\n".format(node2, ip, topo.port(node2,node1)[0]))

def generate_flows(filepath, topo):
    fh = open(filepath)
    fhout = open('flows-tmp', 'w')
    fhout.write("#!/bin/bash\n")
    for line in fh:
        if line and line.strip().startswith('#'):
            continue
        else:
            nodes = line.split()
            if len(nodes) == 0:
                continue
            host = nodes[0]
            switches = nodes[1:]
            print topo.nodeInfo(host)
            host_ip = topo.nodeInfo(host)['ip'][1:-1]
            i = 0
            while i < len(nodes) -1:
                install_path(topo, nodes[i], nodes[i+1], host_ip, fhout)
                i += 1
    fhout.close()
    fh.close()
    print topo.ports

def print_port_numbers(network):
    info("*** Switch interface port number mappings\n")
    for switch in network.switches:
        info(switch, "\n")
        for intfs in switch.intfList():
            info(intfs, ": ", switch.ports[intfs], '\n')

if __name__ == '__main__':
    switch_to_root_eth0_name = 's1'
    setLogLevel('info')
    try:
        s = int(sys.argv[1])
        l = int(sys.argv[2])
        assert l >= s, "Error: Spine < Leaf "
    except:
        print "\tError!!! \nUsage: ./gen_leaf_spine.py <spine> <leaf>\n leaf >= spine"
        exit(0)
    net(s, l)

