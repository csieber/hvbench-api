import hvbenchapi
import logging

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, **hvbenchapi.logconf)

    # Put the IP of your etcd host here:
    etcdIP = "192.168.0.12"

    bench = hvbenchapi.HVBench(host=etcdIP)

    bench.reset_config()

    bench.set_experiment_id("basic_test", 1)

    print("Instances: %s" % bench.instances())

    tenant = hvbenchapi.ConstantTenant(bench, "first")

    bench["1"].add(tenant)

    #assert(len(bench.instances()) > 0)

