# light-host-metrics-server

NEED HOST NETWORK FOR DOCKER

`env METRICS_NET_DEVICE_ETH=wlp3s0 METRICS_DISK_ROOT=/ METRICS_DISK_EXTERNAL_DD=/media/drive METRICS_PORT=8888 python3 main.py`

`sudo docker run --net=host -v /media/drive:/media/drive:ro -e METRICS_NET_DEVICE_ETH=wlp3s0 -e METRICS_DISK_ROOT=/ -e METRICS_DISK_EXTERNAL_DD=/media/drive -e METRICS_PORT=8888 light-host-metrics-server` after build

Then, you can call http://localhost:8888 and use metric. For example with node-red, I call each 5 minutes this endpoint and push to influxdb. And then I can see in my grafana :)

## Output

`env METRICS_NET_DEVICE_wifi=wlp3s0 METRICS_NET_DEVICE_lo=lo METRICS_PORT=8080 METRICS_DISK_root=/ METRICS_NET_INTERVALS=1,5 python3 main.py`

http://localhost:8080 :

```
{
  "swap": {
    "free": 33751560192,
    "used": 0,
    "usedPct": 0
  },
  "load": {
    "1": 2.65,
    "5": 3.54,
    "15": 3.53
  },
  "net": {
    "wifi": {
      "1": {
        "sentSpeed": 488,
        "receivedSpeed": 770
      },
      "5": {
        "sentSpeed": 1801,
        "receivedSpeed": 21411
      }
    },
    "lo": {
      "1": {
        "sentSpeed": 41,
        "receivedSpeed": 41
      },
      "5": {
        "sentSpeed": 65,
        "receivedSpeed": 65
      }
    }
  },
  "disk": {
    "root": {
      "free": 120939520000,
      "used": 86611247104,
      "usedPct": 41.7
    }
  },
  "mem": {
    "free": 20786286592,
    "used": 5835284480,
    "usedPct": 21.1
  }
}
```

http://localhost:8080/flat :

```
{
  "disk_root_used_pct": 41.7,
  "mem_free": 20843929600,
  "net_wifi_5_sent_speed": 2179,
  "net_wifi_1_sent_speed": 2563,
  "net_lo_1_received_speed": 88,
  "disk_root_used": 86611058688,
  "load_1": 3.09,
  "net_lo_5_received_speed": 70,
  "disk_root_free": 120939708416,
  "load_5": 3.54,
  "mem_used_pct": 20.9,
  "net_lo_5_sent_speed": 70,
  "net_lo_1_sent_speed": 88,
  "net_wifi_5_received_speed": 23795,
  "swap_used_pct": 0,
  "net_wifi_1_received_speed": 22674,
  "load_15": 3.53,
  "mem_used": 5770801152,
  "swap_free": 33751560192,
  "swap_used": 0
}
```