#!/usr/bin/env python

'''
Basic IPv4 router (static routing) in Python, stage 1.
'''

import sys
import os
import os.path
sys.path.append(os.path.join(os.environ['HOME'],'pox'))
sys.path.append(os.path.join(os.getcwd(),'pox'))
import pox.lib.packet as pktlib
from pox.lib.packet import ethernet,ETHER_BROADCAST,IP_ANY
from pox.lib.packet import arp
from pox.lib.addresses import EthAddr,IPAddr
from srpy_common import log_info, log_debug, log_warn, SrpyShutdown, SrpyNoPackets, debugger

class Router(object):
    def __init__(self, net):
        self.net = net

    def router_main(self):    
        while True:
            try:
                dev,ts,pkt = self.net.recv_packet(timeout=1.0)
            except SrpyNoPackets:
                # log_debug("Timeout waiting for packets")
                continue
            except SrpyShutdown:
                return
            if pkt.type == pkt.ARP_TYPE:
                arp_request = pkt.payload
                for intf in self.net.interfaces():
                    if (intf.ipaddr==arp_request.protodst):
                        arp_reply = pktlib.arp()
                        arp_reply.protodst = arp_request.protosrc
                        arp_reply.protosrc = intf.ipaddr
                        arp_reply.hwsrc = intf.ethaddr
                        arp_reply.hwdst = arp_request.hwsrc
                        arp_reply.opcode = pktlib.arp.REPLY
                        ether = pktlib.ethernet()
                        ether.type = ether.ARP_TYPE
                        ether.src = intf.ethaddr
                        ether.dst = arp_request.hwsrc
                        ether.set_payload(arp_reply)
                        self.net.send_packet(dev, ether)
                        #self.net.send_packet(dev, arp_reply)
                        break

def srpy_main(net):
    '''
    Main entry point for router.  Just create Router
    object and get it going.
    '''
    r = Router(net)
    r.router_main()
    net.shutdown()
    
