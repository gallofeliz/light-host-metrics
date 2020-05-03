#!/usr/bin/env python

import psutil, socketserver, http.server, urllib.parse, json, time, os, re

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
    try:
        device = next(x for x in psutil.net_if_stats().keys() if x[0:3] == 'eth')
    except:
        raise BaseException('Unable to find device eth')
    net_devices[device] = device

def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + "_" + re.sub(r'(?<!^)(?=[A-Z])', '_', subkey).lower(), subvalue
            else:
                yield key, value

    return dict(items())

def get_stats():

    load = psutil.getloadavg()
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    net0 = psutil.net_io_counters(pernic=True)
    time.sleep(1)
    net1 = psutil.net_io_counters(pernic=True)

    #disk_io = psutil.disk_io_counters()

    stats = {
      'load': {
        '1': load[0],
        '5': load[1],
        '15': load[2]
      },
      'mem': {
        'used': mem.used,
        'free': mem.free,
        'usedPct': mem.percent,
      },
      'swap': {
        'used': swap.used,
        'free': swap.free,
        'usedPct': swap.percent
      },
      'disk': {
      },
      'net': {
      }

    }

    for disk_name, disk_path in disks_path.items():
        disk = psutil.disk_usage(disk_path)
        stats['disk'][disk_name] = {
            'used': disk.used,
            'free': disk.free,
            'usedPct': disk.percent
        }

    for net_name, net_device in net_devices.items():
        stats['net'][net_name] = {
            'sentSpeed': round((net1[net_device].bytes_sent - net0[net_device].bytes_sent) / 1),
            'receivedSpeed': round((net1[net_device].bytes_recv - net0[net_device].bytes_recv) / 1)
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
            data = flatten_dict(get_stats()) if sMac == 'flat' else get_stats()

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
