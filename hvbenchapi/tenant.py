import etcd
import hvbenchapi.conf as conf
import logging


log = logging.getLogger(__name__)


class TenantExistsAlready(Exception):
    pass


class NoSuchTenant(Exception):
    pass


class InvalidWeights(Exception):
    pass


class _AbstractTenant(object):

    def __init__(self, hvbench, name, init=True,
                 rate=conf.DEFAULT_TENANT["generator_conf/avg_rate"],
                 port=conf.DEFAULT_TENANT["setup/port"]):

        self._name = name
        self._hvbench = hvbench
        self._etcd = self._hvbench.etcd()

        # Check if we want to create a new tenant
        if init:
            self._populate()

            if rate is not conf.DEFAULT_TENANT["generator_conf/avg_rate"]:
                self.set_rate(rate)
            if port is not conf.DEFAULT_TENANT["setup/port"]:
                self.set_port(port)
        else:
            # Otherwise the tenant has to exist already
            try:
                based = "%s/%s" % (conf.TENANT_DIR, self._name)
                self._etcd.read(based)
            except etcd.EtcdNotFile:
                raise NoSuchTenant("Tenant %s does not exist!" % self._name)

    def __repr__(self):
        return "Tenant({})".format(self._name)

    def _populate(self):

        based = "%s/%s" % (conf.TENANT_DIR, self._name)

        log.debug("Populating tenant %s." % based)

        tconf = conf.DEFAULT_TENANT.copy()
        tconf.update(conf.DEFAULT_TENANT_CONF[self.TYPE])

        try:
            self._etcd.write(based, None, dir=True)
        except etcd.EtcdNotFile:
            errstr = "A tenant with this name (%s) already exists!" % based
            log.error(errstr)
            raise TenantExistsAlready(errstr)

        for key, value in tconf.items():
            self._etcd.write("%s/%s" % (based, key), value)

    def name(self):
        return self._name

    def set_rate(self, rate):

        based = "%s/%s" % (conf.TENANT_DIR, self._name)
        p = "{}/generator_conf/avg_rate".format(based)
        self._etcd.write(p, rate)

    def set_port(self, port):

        based = "%s/%s" % (conf.TENANT_DIR, self._name)
        p = "{}/setup/port".format(based)
        self._etcd.write(p, str(port))


class DynamicTenant(_AbstractTenant):

    TYPE = "dynamic"

    def __init__(self, parent, name, weights=conf.DEFAULT_DYNAMIC_WEIGHTS, **kwargs):

        super().__init__(parent, name, **kwargs)

        if 'init' in kwargs and kwargs['init']:
            self.set_weights(weights)

    def set_weights(self, weights):

        based = "%s/%s" % (conf.TENANT_DIR, self._name)

        for k, v in weights.items():
            assert(k in conf.SUPPORTED_MSG)
            p = "{}/weights/{}".format(based, k)
            self._etcd.write(p, str(v))


class ConstantTenant(_AbstractTenant):

    TYPE = "constant"

    def __init__(self, hvbench, name, msg_t="ECHO_REQUEST", **kwargs):

        super().__init__(hvbench, name, **kwargs)

        if msg_t not in conf.SUPPORTED_MSG:
            raise Exception("Message type %s not supported ! (Types: %s)" % (msg_t, conf.SUPPORTED_MSG))


class TenantFactory(object):

    @staticmethod
    def from_etcd(bench, name):

        # Get the type of the tenant
        try:
            based = "%s/%s/generator" % (conf.TENANT_DIR, name)
            generator = bench.etcd().read(based).value
        except etcd.EtcdNotFile:
            raise NoSuchTenant("Tenant %s does not exist!" % name)

        return TenantFactory.new(bench, name, generator, init=False)

    @staticmethod
    def new(bench, name, generator, init=True, **kwargs):

        if generator == "constant":
            return ConstantTenant(bench, name, init=init, **kwargs)
        elif generator == "dynamic":
            return DynamicTenant(bench, name, init=init, **kwargs)
        else:
            raise RuntimeError("Could not determine type of tenant %s! (%s is not known)" % (name, generator))