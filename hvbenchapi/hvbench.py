import etcd
import hvbenchapi.conf as conf
import hvbenchapi.tenant
import logging

log = logging.getLogger(__name__)


class NoSuchInstance(Exception):
    pass


class WrongAPIVersion(Exception):
    pass


class HVBench:
    def __init__(self, host="127.0.0.1", port=2379):

        self._host = host

        self._etcd = etcd.Client(host=host, port=port)

        # Populate config tree if it doesn't exist yet
        self._populate()

        # Make sure API version is correct
        etcd_api = self._etcd.read("%s/api_version" % conf.GLOBAL_CONF_DIR).value

        if etcd_api != conf.API_VERSION:
            raise WrongAPIVersion(
                "Configuration data belongs to a different API version! (%s vs. %s). Call reset-config." %
                (etcd_api, conf.API_VERSION))

        self._tenants = {}

    def __getitem__(self, index):
        return self.instance(index)

    def instance(self, name):
        return _HVBenchInstance(self, name)

    def tenant(self, name):
        return hvbenchapi.tenant.TenantFactory.from_etcd(self, name)

    def etcd(self):
        return self._etcd

    def set_experiment_id(self, study_id, run_id):
        """
        Set a unique identifier for this run.
        This is used by the hvbench instances to organize the log output.

        :param study_id: The name of the study (str)
        :param run_id: The numeric id of the study (int)
        :return:
        """

        self._etcd.write("%s/study_id" % conf.GLOBAL_CONF_DIR, study_id)
        self._etcd.write("%s/run_id" % conf.GLOBAL_CONF_DIR, run_id)

    def _populate(self):

        try:
            self._etcd.write(conf.INSTANCES_DIR, None, dir=True)
            self._etcd.write(conf.TENANT_DIR, None, dir=True)

        except etcd.EtcdNotFile:
            return

        for key, value in conf.DEFAULTS.items():
            self._etcd.write(key, value)

    def reset_config(self):
        """
        Delete the configuration in etcd and populate it with default values.

        :return:
        """

        self._etcd.delete(conf.BASE_DIR, recursive=True)
        self._populate()

    def instances(self):
        """
        Returns the registered hvbench instances.

        :return:
        """

        instances = self._etcd.get(conf.INSTANCES_DIR)

        it = lambda x: [i.key.split('/')[-1] for i in x]

        # Workaround for empty directory
        for i in instances.children:
            if i.key == conf.INSTANCES_DIR:
                return []

        return [_HVBenchInstance(self, i) for i in it(instances.children)]


class _HVBenchInstance:
    def __init__(self, parent, id):

        self._parent = parent
        self._name = id
        self._etcd = self._parent.etcd()
        self._confp = "{}/{}".format(conf.INSTANCES_DIR, self._name)

        # Check if instance exists
        try:
            self._etcd.read(self._confp)
        except etcd.EtcdKeyNotFound:
            raise NoSuchInstance("Instance %s does not exist!" % id)

    def __repr__(self):

        return self._name

    def add(self, item):
        """
        Add a tenant or node to the hvbench instance.

        :param item:
        :return:
        """

        log.debug("Adding %s to instance %s." % (item, self))

        path = "{}/{}".format(self._confp, item.name())

        if isinstance(item, hvbenchapi.tenant._AbstractTenant):
            self._etcd.write(path, "tenant")
        else:
            raise NotImplementedError("Item of type '%s' can not be added to a hvbench instance!")

    def __getitem__(self, index):

        T = True
        N = True

        try:
            nconf = "{}/{}".format(conf.NODE_CONF, index)
            self._etcd.read(nconf)
        except etcd.EtcdKeyNotFound:
            N = False

        try:
            tconf = "{}/{}".format(conf.TENANT_CONF, index)
            self._etcd.read(tconf)
        except etcd.EtcdKeyNotFound:
            T = False

        if T:
            return tenant(self, index)
        elif N:
            return node(self, index)
        else:
            raise Exception("Tenant/Node not found!")

    def tenants(self):
        """
        Get a list of all configured tenants.

        :return: list of tenants
        """

        p = "{}/{}".format(conf.HVBENCH_DIR, self._name)

        tenants = self._parent._etcd.get(p)

        it = lambda x: [i.key.split('/')[-1] for i in x]

        for i in tenants.children:
            print(i)

        #        return [tenant(self, i) for i in it(tenants.children)]

    def nodes(self):
        pass

    def shutdown(self):

        self._etcd.write("{}/{}/shutdown".format(conf.HVBENCH_DIR, self._name),
                         "shutdown", ttl=5)
