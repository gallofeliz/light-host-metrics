import threading, datetime, psutil, time

net=[]

net_collect_interval=30
net_intervals_minutes=[0, 1, 5]

max_net_interval_minutes=max(net_intervals_minutes)

if max_net_interval_minutes > 0:

    def collect_network(sec):
        global net
        threading.Timer(sec, lambda: collect_network(sec) ).start()
        max_net_interval_minutes_datetime = datetime.datetime.now() - datetime.timedelta(minutes=max_net_interval_minutes)
        # Can be optimized, no need to iterate on all the list and maybe no need to create new one
        net = list(filter(lambda x: x['datetime'] >= max_net_interval_minutes_datetime, net))
        net.append({
            "datetime": datetime.datetime.now(),
            "network": psutil.net_io_counters(pernic=True)
        })

    collect_network(net_collect_interval)

def get_nets(interval_minutes):
    global net
    print(datetime.datetime.now())
    if interval_minutes == 0:
        net0 = psutil.net_io_counters(pernic=True)
        time.sleep(1)
    else:
        datetime_wanted = datetime.datetime.now() - datetime.timedelta(minutes=interval_minutes)
        differences = list(map(lambda x: abs((x['datetime'] - datetime_wanted).total_seconds()), net))
        min_difference=min(differences)
        net0 = net[differences.index(min_difference)]['network']
    net1 = psutil.net_io_counters(pernic=True)
    return [net0, net1]

threading.Timer(100, lambda: print(get_nets(1)) ).start()
