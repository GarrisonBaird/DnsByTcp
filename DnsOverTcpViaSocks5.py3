import os, sys
import socket
import struct
import threading
import socketserver
import random

import socks

# DNS Server List
DNS_SERVS = ['8.8.8.8',
         '8.8.4.4',
         '208.67.222.222',
         '208.67.220.220',
         ]

DNS_PORT = 53           # default dns port 53
TIMEOUT = 20            # set timeout 20 second

LISTEN_ADDRESS = '127.0.0.1'
LISTEN_PORT = 53

SOCKS5_SERVER = '127.0.0.1'
SOCKS5_PORT = 1080

def QueryDnsByTcp(dns_ip, dns_port, query_data):
    # make TCP DNS Frame
    tcp_frame = struct.pack('!h', len(query_data)) + query_data
    try:
        s = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        s.set_proxy(socks.SOCKS5, SOCKS5_SERVER, SOCKS5_PORT)
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT) # set socket timeout
        s.connect((dns_ip, dns_port))
        s.send(tcp_frame)
        data = s.recv(2048)
    except:
        if s: s.close()
        return
      
    if s: s.close()
    return data

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True
    # much faster rebinding
    allow_reuse_address = True
    
    def __init__(self, s, t):
        socketserver.UDPServer.__init__(self, s, t)

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        query_data = self.request[0]
        udp_sock = self.request[1]
        addr = self.client_address

        dns_ip = DNS_SERVS[random.randint(0, len(DNS_SERVS) - 1)]
        response = QueryDnsByTcp(dns_ip, DNS_PORT, query_data)
        if response:
            # udp dns packet no length
            udp_sock.sendto(response[2:], addr)
        
        
if __name__ == "__main__":
    print("---------------------------------------------------------------")
    print("| To Use this tool, you must set your dns server to 127.0.0.1 |")
    print("---------------------------------------------------------------")
    
    dns_server = ThreadedUDPServer((LISTEN_ADDRESS, LISTEN_PORT), ThreadedUDPRequestHandler)
    dns_server.serve_forever()
