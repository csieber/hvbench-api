import etcd
import hvbenchapi.conf as conf





class node:

    def __init__(self, parent, name):

        self._parent = parent
        self._name = name
        self._etcd = parent._parent._etcd

        self._confp = "{}/{}".format(conf.NODE_CONF, self._name)

    def __repr__(self):

        return "Node: {}/{}".format(self._parent._name, self._name)

    def write_conf(self, key, value):

        p = "{}/{}".format(self._confp, key)

        print("{}: {}".format(p, value))

        self._etcd.write(p, value)

    def run(self):

        p = "{}/{}".format(self._parent._confp, self._name)

        self._etcd.write(p, "node")


if __name__ == "__main__":

    bench = hvbench("192.168.33.15")

    print(bench.get_instances())
    print(bench['1'].get_tenants())

    #bench['1']['tenantA'].run()
    bench['1']['tenantA'].set_rate(5)
    bench['1']['tenantA'].set_const_msg_T("ECHO_REQUEST")
    #bench['1'].new_tenant("TestTenant")

