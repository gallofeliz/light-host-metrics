#!/usr/bin/env python

import psutil
import pprint
import socketserver
import http.server
import urllib.parse
import json
import time
import os

port = int(os.environ['METRICS_PORT']) if "METRICS_PORT" in os.environ else 8080
disks_path = {}
net_devices = {}

for k, v in os.environ.items():
    if k[0:13] == 'METRICS_DISK_':
        disks_path[k[13:].lower()] = v
    if k[0:12] == 'METRICS_NET_':
        net_devices[k[12:].lower()] = v

if not disks_path:
    disks_path['root'] = '/'

if not net_devices:
    device = next(x for x in psutil.net_if_stats().keys() if x[0:3] == 'eth')
    net_devices[device] = device

def get_stats():

    load = psutil.getloadavg()
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    net0 = psutil.net_io_counters(pernic=True)
    time.sleep(5)
    net1 = psutil.net_io_counters(pernic=True)

    #disk_io = psutil.disk_io_counters()

    stats = {
      'load_1': load[0],
      'load_5': load[1],
      'load_15': load[2],

      'mem_used': mem.used,
      'mem_free': mem.free,
      'mem_used_pct': mem.percent,

      'swap_used': swap.used,
      'swap_free': swap.free,
      'swap_used_pct': swap.percent
    }

    for disk_name, disk_path in disks_path.items():
        disk = psutil.disk_usage(disk_path)
        stats['disk_' + disk_name + '_used'] = disk.used
        stats['disk_' + disk_name + '_free'] = disk.free
        stats['disk_' + disk_name + '_used_pct'] = disk.percent

    for net_name, net_device in net_devices.items():
        stats['net_' + net_name + '_bytes_sent_s'] = round((net1[net_device].bytes_sent - net0[net_device].bytes_sent) / 5)
        stats['net_' + net_name + '_bytes_recv_s'] = round((net1[net_device].bytes_recv - net0[net_device].bytes_recv) / 5)

    return stats

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        sMac = urllib.parse.urlparse(self.path).path[1:]
        print('Requested ' + sMac)

        if (sMac == 'favicon.ico'):
            print('Skipped')
            return

        try:
            data = get_stats()

            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(data), 'utf8'))
            print('Done ' + str(data))
        except Exception as inst:
            self.send_response(500)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(bytes(str(inst), 'utf8'))
            print('ERROR ' + str(inst))

httpd = socketserver.TCPServer(('', port), Handler)
try:
   print('Listening on ' + str(port))
   httpd.serve_forever()
except KeyboardInterrupt:
   pass
httpd.server_close()
print('Ended')
