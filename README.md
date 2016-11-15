# collectd_system_metrics

We collect system metrics via collectd. But how easy is it to use those for alerting. 

* For example we would like to get alerted on high load on systems. The collectd load plugin just exports the system load avg. For a multi core machine you would typically want to do

m = (load avg)/(number of cpu) 

and then do something like the following for alerting

if m > 1 for the past x minutes send an alert.

Now doing that dynamically via the /render api is not easy especially with complex graphite metric namespace.

* The collectd memory module exports the raw memory metrics. What we would be interested in is the real meory usage by percentage. And here you discount the cache/buffers and then derive the memory percentage used. Again with the collectd metrics it is hard to calculate that.

* Same goes with the df plugin although fortunately there is an option which is not turned on by default to export the metrics in percentage format.

All the above led me to write a simple python collectd plugin to export the following metrics which can be easily alerted upon

* load average per cpu.
* memory usage by percentage.
* disk usage (for all partitions) by percentage.

The only dependency is the psutil python which we use here.

Caveat
This has been tested only on ubuntu 14.04
