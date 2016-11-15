# This plugin records some useful system metrics in an alert friendly manner.
#
# It requires the psutil python library or the python-psutil package. You can install it with
#
# pip install psutil
# or
# apt-get install python-psutil
#
# This has been tested on ubuntu 14.04
# Example collectd config
#<LoadPlugin python>
#  Globals true
#</LoadPlugin>

#<Plugin python>
#    ModulePath "/opt/collectd/plugin"
#    LogTraces true
#    Interactive false
#    Import "system_metrics"

#    <Module system_metrics>
#        metric_list "loadavg-per-cpu" "disk-usage-percent" "memory-usage-percent"
#    </Module>
#</Plugin>

import collectd
import multiprocessing
import os
import psutil

METRICS_CONFIGURED = []
PLUGIN_NAME = "system-metrics"
INTERVAL = 30 # the interval with which the plugin should be run by collectd.

def configure(conf):
  """Receive configuration block. Sets up the global system metrics list to export.
  Arguments: Takes the collectd Config object (https://collectd.org/documentation/manpages/collectd-python.5.shtml#config).
  Returns: None.
  """
  
  for node in conf.children:
    key = node.key.lower()
    val = node.values
    if key == 'metric_list':
      global METRICS_CONFIGURED
      METRICS_CONFIGURED = val
      collectd.debug('Exporting the following metrics ' + ' '.join(METRICS_CONFIGURED))
    else:
      collectd.warning('Metric list not set.')

def func_loadavg_per_cpu():
  """Returns the load average per cpu metric."""
  
  load_avg = os.getloadavg()[1] # we get the midterm loadavg
  cpu_count = None
  # The psutil pip module seems to have the cpu_count() method while the python-psutil deb package (at least in ubuntu 14.04) does not.
  if hasattr(psutil, 'cpu_count'):
    cpu_count = psutil.cpu_count()
  else:
    cpu_count = multiprocessing.cpu_count()
  return {'loadavg-per-cpu': load_avg/float(cpu_count)}

def func_memory_usage_percent():
  """Returns the memory usage by percenatge."""

  return {'memory-usage-percent': psutil.virtual_memory().percent}

def func_disk_usage_percent():
  """Returns the disk usage percentage for all partitions (mounted disk partitions)."""

  partition_usage = {}
  for partition in psutil.disk_partitions():
    mount = None
    if partition.mountpoint == '/':
      mount = 'df-root'
    else:
      mount = 'df' + partition.mountpoint.replace('/', '-') 
    partition_usage['disk-usage-percent.' + mount] = psutil.disk_usage(partition.mountpoint).percent
  return partition_usage

METRICS_ENABLED = {'loadavg-per-cpu': func_loadavg_per_cpu, 'disk-usage-percent': func_disk_usage_percent, 'memory-usage-percent': func_memory_usage_percent}

def dispatch_value(metric_name, value, type):
  """Dispatches a value for the key
  Argumets (key: metric name
            value:  value of the metric)
  Returns: None.
  """

  val = collectd.Values(plugin=PLUGIN_NAME)
  val.type = type
  val.type_instance = metric_name
  val.values = [value]
  val.dispatch()

def read_callback():
  
  collectd.debug('Metrics to be exported ' + ' '.join(METRICS_CONFIGURED))
  collect_metric = {}
  for metric in METRICS_CONFIGURED:
    if metric in METRICS_ENABLED:
      collect_metric.update(METRICS_ENABLED[metric]())

  for k, v in collect_metric.iteritems():
    dispatch_value(k, v, 'gauge')

# register callbacks
collectd.register_config(configure)
collectd.register_read(read_callback, INTERVAL)
