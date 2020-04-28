#!/usr/bin/env python

import psutil
import pprint
import socketserver
import http.server
import urllib.parse
import json
import time

def get_stats():
    disk_root=psutil.disk_usage('/')
    disk_external=psutil.disk_usage('/media/USB-DD')
    load = psutil.getloadavg()
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    net0 = psutil.net_io_counters(pernic=True)
    time.sleep(5)
    net1 = psutil.net_io_counters(pernic=True)

    #disk_io = psutil.disk_io_counters()

    stats = {
      'disk_root_used': disk_root.used,
      'disk_root_free': disk_root.free,
      'disk_root_used_pct': disk_root.percent,

      'disk_external_used': disk_external.used,
      'disk_external_free': disk_external.free,
      'disk_external_used_pct': disk_external.percent,

      'load_1': load[0],
      'load_5': load[1],
      'load_15': load[2],

      'mem_used': mem.used,
      'mem_free': mem.free,
      'mem_used_pct': mem.percent,

      'swap_used': swap.used,
      'swap_free': swap.free,
      'swap_used_pct': swap.percent,

      'net_eth0_bytes_sent_s': round((net1['eth0'].bytes_sent - net0['eth0'].bytes_sent) / 5),
      'net_eth0.bytes_recv_s': round((net1['eth0'].bytes_recv - net0['eth0'].bytes_recv) / 5)
    }

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

httpd = socketserver.TCPServer(('', 8734), Handler)
try:
   print('Listening')
   httpd.serve_forever()
except KeyboardInterrupt:
   pass
httpd.server_close()
print('Ended')
