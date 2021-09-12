#!/usr/bin/env python

import psutil, socketserver, http.server, json, time, os, re, threading, datetime

port = int(os.environ['METRICS_PORT']) if "METRICS_PORT" in os.environ else 9386
disks_path = {}
net_devices = {}

net_collect=[]
net_collect_interval=30
net_intervals_minutes=[0, 1, 5, 15]
net_zero_interval = 1

for k, v in os.environ.items():
    if k[0:13] == 'METRICS_DISK_':
        disks_path[k[13:].lower()] = v
    if k[0:19] == 'METRICS_NET_DEVICE_':
        net_devices[k[19:].lower()] = v
    if k == 'METRICS_NET_INTERVALS':
        net_intervals_minutes=list(map(int, v.split(',')))
    if k == 'METRICS_NET_COLLECT_INTERVAL':
        net_collect_interval=int(v)
    if k == 'METRICS_NET_ZERO_INTERVAL':
        net_zero_interval=int(v)

if not disks_path:
    disks_path['root'] = '/'

if not net_devices:
    try:
        device = next(x for x in psutil.net_if_stats().keys() if x[0:3] == 'eth')
    except:
        raise BaseException('Unable to find device eth')
    net_devices[device] = device

max_net_interval_minutes=max(net_intervals_minutes)

def collect_network(sec):
    global net_collect
    threading.Timer(sec, lambda: collect_network(sec) ).start()
    max_net_interval_minutes_datetime = datetime.datetime.now() - datetime.timedelta(minutes=max_net_interval_minutes)
    # Can be optimized, no need to iterate on all the list and maybe no need to create new one
    net_collect = list(filter(lambda x: x['datetime'] >= max_net_interval_minutes_datetime, net_collect))
    net_collect.append({
        "datetime": datetime.datetime.now(),
        "network": psutil.net_io_counters(pernic=True)
    })

def get_net(interval_minutes):
    global net_collect
    datetime_wanted = datetime.datetime.now() - datetime.timedelta(minutes=interval_minutes)
    differences = list(map(lambda x: abs((x['datetime'] - datetime_wanted).total_seconds()), net_collect))
    min_difference=min(differences)
    return net_collect[differences.index(min_difference)]

def get_stats():

    load = psutil.getloadavg()
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    cpu = psutil.cpu_freq()
    temps = psutil.sensors_temperatures()

    #disk_io = psutil.disk_io_counters()
    stats = {
      'nbCpus': psutil.cpu_count(),
      #'nbProcesses': len(psutil.pids()),
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
      'temperatures': {
      },
      'cpufreq': {
         'current': round(cpu.current)
      },
      'disk': {
      },
      'net': {
        'global': {
            'nbConnections': len(psutil.net_connections())
        }
      }
    }

    for name, entries in temps.items():
        if name == 'cpu_thermal' or name == 'cpu-thermal':
            name = 'cpu' # thermal ? Yes, it's temperature sensor !
        for entry in entries:
            full_name = name + '_' + entry.label if entry.label else name
            stats['temperatures'][full_name] = entry.current

    for disk_name, disk_path in disks_path.items():
        disk = psutil.disk_usage(disk_path)
        stats['disk'][disk_name] = {
            'used': disk.used,
            'free': disk.free,
            'usedPct': disk.percent
        }

    if 0 in net_intervals_minutes:
        net0 = psutil.net_io_counters(pernic=True)
        time.sleep(net_zero_interval)
    net_now = psutil.net_io_counters(pernic=True)

    for net_name, net_device in net_devices.items():
        stats['net'][net_name] = {}
        for net_interval in net_intervals_minutes:
            if net_interval == 0:
                stats['net'][net_name][str(net_interval)] = {
                    'sentSpeed': round((net_now[net_device].bytes_sent - net0[net_device].bytes_sent) / net_zero_interval),
                    'receivedSpeed': round((net_now[net_device].bytes_recv - net0[net_device].bytes_recv) / net_zero_interval)
                }
            else:
                datetime_now=datetime.datetime.now()
                found_net=get_net(net_interval)
                real_interval=(datetime_now - found_net['datetime']).total_seconds()

                stats['net'][net_name][str(net_interval)] = {
                    'sentSpeed': round((net_now[net_device].bytes_sent - found_net['network'][net_device].bytes_sent) / real_interval),
                    'receivedSpeed': round((net_now[net_device].bytes_recv - found_net['network'][net_device].bytes_recv) / real_interval)
                }

    return stats

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path

        if (path == '/favicon.ico'):
            print('Skipped favicon')
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

if max_net_interval_minutes > 0:
    collect_network(net_collect_interval)

httpd = socketserver.TCPServer(('', port), Handler)
try:
   print('Listening on ' + str(port))
   httpd.serve_forever()
except KeyboardInterrupt:
   pass
httpd.server_close()
print('Ended')
