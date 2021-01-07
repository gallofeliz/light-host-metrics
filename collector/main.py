#!/usr/bin/env python

import requests, threading, os, logging, re
from influxdb import InfluxDBClient
#from retrying import retry

def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + "_" + re.sub(r'(?<!^)(?=[A-Z])', '_', subkey).lower(), subvalue
            else:
                yield key, value

    return dict(items())

seconds_per_unit = {"s": 1, "m": 60}

def convert_to_seconds(duration):
    return int(duration[:-1]) * seconds_per_unit[duration[-1]]

# expected "host" (hostname(:ip)) of the agent. Maybe add options or configure 1 agent by ENV, for example PULL_AGENT_XXX_HOST=host etc
def describe_agent(agent_str):
    return {
        'hostname': agent_str.split(':')[0],
        'endpoint': 'http://' + agent_str + (':9386' if ':' not in agent_str else '')
    }

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
pull_agents=list(map(describe_agent, os.environ['PULL_AGENTS'].split(','))) if 'PULL_AGENTS' in os.environ else []
pull_frequency=os.environ['PULL_FREQUENCY'] if pull_agents else None
pull_frequency_s=convert_to_seconds(pull_frequency) if pull_frequency else None

logging.info('Having pull agents %s', pull_agents)
logging.info('Having pull freq %s', pull_frequency)

influxdb_client = InfluxDBClient(os.environ['INFLUXDB_HOST'], database=os.environ['INFLUXDB_DB'])
influxdb_measurement = os.environ['INFLUXDB_MEASUREMENT']

# Only handle pull for the moment ; push if needed
# No retry for the moment (no important)
def collect_agent(agent, pull_frequency_s):
    threading.Timer(pull_frequency_s, lambda: collect_agent(agent, pull_frequency_s) ).start()
    logging.info('Collecting agent %s', agent['hostname'])
    # Do we should put a metric for that ? NO_DATA will alert ;)
    response = requests.get(agent['endpoint']).json()
    metrics = flatten_dict(response)

    influxdb_client.write_points([{
      'measurement': influxdb_measurement,
      'fields': metrics,
      'tags': {
        'host': agent['hostname']
      }
    }])

    logging.info('Agent %s collected !', agent['hostname'])

for agent in pull_agents:
    threading.Thread(target=collect_agent, args=(agent, pull_frequency_s)).start()
