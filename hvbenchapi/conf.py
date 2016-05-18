
API_VERSION = "0.1"
BASE_DIR = "/hvbench"
INSTANCES_DIR = BASE_DIR + "/instances"
GLOBAL_CONF_DIR = BASE_DIR + "/globals"
TENANT_DIR = BASE_DIR + "/tenants"
NODE_CONF = BASE_DIR + "/nodes/conf"

logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s',
          'datefmt': "%H:%M:%S"}

DEFAULTS = {"%s/study_id" % GLOBAL_CONF_DIR: "default",
            "%s/run_id" % GLOBAL_CONF_DIR: 1,
            "%s/api_version" % GLOBAL_CONF_DIR: API_VERSION}

DEFAULT_TENANT = {"generator_conf/avg_rate": 10,
                  "setup/port": 6633,
                  "setup/listen": "0.0.0.0"}

DEFAULT_TENANT_CONF = {'constant': {
                            "generator_conf/msg_t": "ECHO_REQUEST",
                            "generator": "constant"},
                       'dynamic': {
                            "generator": "dynamic"}}

DEFAULT_DYNAMIC_WEIGHTS = {"FEATURE_REQUEST": 10,
                           "ECHO_REQUEST": 10,
                           "STATS_REQUEST_PORT": 20,
                           "STATS_REQUEST_FLOW": 20,
                           "PACKET_OUT_UDP": 20,
                           "FLOW_MOD": 20}

DEFAULT_NODE = {"setup/hv_ip": "127.0.0.1",
                "setup/hv_port": 6633,
                "setup/datapath_id": 0}

SUPPORTED_MSG = ["FEATURE_REQUEST", "ECHO_REQUEST",
                 "STATS_REQUEST_PORT", "STATS_REQUEST_FLOW",
                 "PACKET_OUT_UDP", "FLOW_MOD"]

