# light-host-metrics-server

NEED HOST NETWORK FOR DOCKER

`env METRICS_NET_ETH=wlp3s0 METRICS_DISK_ROOT=/ METRICS_DISK_EXTERNAL_DD=/media/drive METRICS_PORT=8888 python3 main.py`

`sudo docker run --net=host -v /media/drive:/media/drive:ro -e METRICS_NET_ETH=wlp3s0 -e METRICS_DISK_ROOT=/ -e METRICS_DISK_EXTERNAL_DD=/media/drive -e METRICS_PORT=8888 light-host-metrics-server` after build

Then, you can call http://localhost:8888 and use metric. For example with node-red, I call each 5 minutes this endpoint and push to influxdb. And then I can see in my grafana :)
