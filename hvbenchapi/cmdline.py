import logging
import argh
import hvbenchapi
from hvbenchapi.conf import logconf

ARGS = {'address': "127.0.0.1"}

log = logging.getLogger(__name__)


def populate():

    log.info("Populating etcd.")

    # It is enough to create the object, this will automatically
    # populate the directory service.
    hvbenchapi.HVBench(host=ARGS['address'])


def reset_config():

    log.info("Deleting current configuration & repopulating etcd.")

    bench = hvbenchapi.HVBench(host=ARGS['address'])

    bench.reset_config()

    # It is enough to create a new object, this will automatically
    # populate the directory service.
    hvbenchapi.HVBench(host=ARGS['address'])


def add_tenant(name, tenant_type='constant', instance=1, port=6633, existok=False):
    """
    Add a new tenant to a hvbench instance.

    :param name:
    :param tenant_type: constant | dynamic
    :param instance:
    :param port: OpenFlow listening port on the instance.
    :param existok: Do not stop if tenant configuration already exists.
    :return:
    """

    log.info("Adding a new tenant %s of type %s to instance %d at port %d." % (name, tenant_type, instance, port))

    bench = hvbenchapi.HVBench(host=ARGS['address'])

    try:

        tenant = hvbenchapi.TenantFactory.new(bench, name, tenant_type, port=port)

    except hvbenchapi.tenant.TenantExistsAlready:
        if not existok:
            return 1
        else:
            log.warn("--existok=True. Just adding tenant to the instance.")
            tenant = bench.tenant(name)

    bench[str(instance)].add(tenant)


def set_study(study_id, run_id=1):
    """
    Set's the current study and run identifier. The parameters can be used later to identify parts in the log files.

    :param study_id: Study identifier (str). Used by hvbench-log to create the log folder.
    :param run_id: Run identifier (int). Added to the log files as column.
    :return:
    """

    run_id = int(run_id)

    log.info("Setting study id to '%s' and run id to %d." % (study_id, run_id))

    bench = hvbenchapi.HVBench(host=ARGS['address'])

    bench.set_experiment_id(study_id, run_id)


def set_rate(tenant, rate):
    """
    Set the average rate for a tenant.

    :param tenant: The tenant identifier (str)
    :param rate: The average rate in messages per second (int)
    :return:
    """

    rate = int(rate)

    log.info("Changing rate of tenant %s to %d." % (tenant, rate))

    bench = hvbenchapi.HVBench(host=ARGS['address'])

    bench.tenant(tenant).set_rate(rate)


def set_weights(tenant, fmod=None, feat=None, echo=None, statsPort=None, statsFlow=None, packOut=None):
    """
    Set the weight of each message type for a specific tenant.

    :param tenant: The tenant identifier (str)
    :param fmod:
    :param feat:
    :param echo:
    :param statsPort:
    :param statsFlow:
    :param packOut:
    :return:
    """

    if not fmod and not feat and not echo and not statsPort and not statsFlow and not packOut:
        log.error("At least one of the weights has to be set.")
        return

    bench = hvbenchapi.HVBench(host=ARGS['address'])

    if fmod is not None:
        bench.tenant(tenant).set_weights({'FLOW_MOD': int(fmod)})
    if feat is not None:
        bench.tenant(tenant).set_weights({'FEATURE_REQUEST': int(feat)})
    if echo is not None:
        bench.tenant(tenant).set_weights({'ECHO_REQUEST': int(echo)})
    if statsPort is not None:
        bench.tenant(tenant).set_weights({'STATS_REQUEST_PORT': int(statsPort)})
    if statsFlow is not None:
        bench.tenant(tenant).set_weights({'STATS_REQUEST_FLOW': int(statsFlow)})
    if packOut is not None:
        bench.tenant(tenant).set_weights({'PACKET_OUT_UDP': int(packOut)})


def main():

    parser = argh.ArghParser()
    parser.add_commands([populate, reset_config, add_tenant, set_study, set_rate, set_weights])

    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')
    parser.add_argument('-a', '--address', help="URL/Address of the etcd host.", default=ARGS['address'])

    cmdargs = parser.parse_args()

    if cmdargs.verbose:
        logging.basicConfig(level=logging.DEBUG, **logconf)
    else:
        logging.basicConfig(level=logging.INFO, **logconf)

    ARGS['address'] = cmdargs.address

    parser.dispatch()
