# HVBench API - Control & Logs

  * *hvbench-ctrl* allows to create/remove tenants, adjust message rates and weights. 
  * *hvbench-log* receives the logs from the distributed hvbench and hvmonitor instances.

## Dependencies

  * etcd (only for hvbench-ctrl)
  * argh (only for hvbench-ctrl)
  * kafka-python (only for hvbench-log)

## Quickstart (hvbench-ctrl)

Install the package from source with

```bash
python3 setup.py install
```

You can use **reset-config** or **populate** to create an initial configuration:

```bash
hvbench-ctrl reset-config
```

Note: If you etcd is not localhost, use **--address** to specify the etcd host:

```bash
hvbench-ctrl --address 10.0.0.2 reset-config
```

Now start at least one hvbench instance. Afterwards you can add a tenant to this instance with:

```bash
hvbench-ctrl add-tenant test
```

The command **add-tenant** will by default add a constant tenant to instance 1 using port 6633. If you want to add an existing tenant to an instance, you can pass the **--existok** option.

To set the rate for this tenant, use **set-rate**:

```bash
hvbench-ctrl set-rate test 70
```

## Quickstart (hvbench-log)

To receive the logs from the distributed hvbench instances, use *hvbench-log*:

```bash
hvbench-log
```

### Usage

```
usage: hvbench-log [-h] [-v] [-k KAFKA] [-o OUTPUT]

Retrieve the hvbench and hvmonitor logs from kafka.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable debug log.
  -k KAFKA, --kafka KAFKA
                        Address of the kafka host.
  -o OUTPUT, --output OUTPUT
                        Output directory.
```

## Development

### etcd-viewer

In order to debug the etcd content, we recommend [[etcd-viewer]](https://github.com/nikfoundas/etcd-viewer). You can start it with:

```bash
docker run -d -p 8080:8080 nikfoundas/etcd-viewer
```

Afterwards you can reach the interface via http://127.0.0.1:8080. 

To add the etcd registry in etcd-viewer, use the internal IP of your host. In the default configuration you can get the internal IP of your host via **sudo ip addr show docker0**. For example **http://172.17.0.1:2379/**.


## References

[etcd-viewer] https://github.com/nikfoundas/etcd-viewer
