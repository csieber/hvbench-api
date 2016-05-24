import logging
import argparse
from kafka import KafkaConsumer
from hvbenchapi.conf import logconf
import json
import os
import csv

ARGS = {'kafka': "127.0.0.1"}

log = logging.getLogger(__name__)

class LogCSV(object):

    def __init__(self, path):

        self._path = path

        if os.path.isfile(path):

            with open(path, 'r') as f:
                header = f.readline().strip()

            self._f = open(path, 'a')
            self._csv = csv.DictWriter(self._f, fieldnames=header.split(','))
        else:
            self._csv = None

    def writerow(self, row):

        if self._csv is None:
            self._f = open(self._path, 'a')
            self._csv = csv.DictWriter(self._f, fieldnames=sorted(list(row.keys())))
            self._csv.writeheader()

        self._csv.writerow(row)
        self._f.flush()


class Study(object):

    def __init__(self, basep):

        self._basep = basep

        os.makedirs(ldir, exist_ok=True)

        self._fbench = LogCSV(os.path.join(self._basep, "hvbench.csv"))
        self._fcpu = LogCSV(os.path.join(self._basep, "hvmonitor.csv"))

    def writerow(self, topic, jmsg):

        if topic == "hvbench":
            self._fbench.writerow(jmsg)
        elif topic == "hvmonitor":
            self._fcpu.writerow(clean_hvmonitor(jmsg))
        else:
            log.warn("Unknown kafka topic %s!. Ignoring." % topic)


# http://stackoverflow.com/a/11668135
def flatten(d, parent_key=''):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s_' % (parent_key, k)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)


def clean_hvmonitor(jmsg):

    # Tasks are dangerous (csv keys change if there is a new thread!)
    del jmsg['proc_tasks']

    # Flatten the dictionary for csv write out
    jmsg = flatten(jmsg)

    # We do not need to store differences in the logs
    jmsg = {k: v for k, v in jmsg.items() if not k.endswith("_diff")}

    return jmsg


def main():

    parser = argparse.ArgumentParser(description="Retrieve the hvbench and hvmonitor logs from kafka.")

    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')
    parser.add_argument('-k', '--kafka', help="Address of the kafka host.", default=ARGS['kafka'])
    parser.add_argument('-o', '--output', help="Output directory.", default="out")

    cmdargs = parser.parse_args()

    if cmdargs.verbose:
        logging.basicConfig(level=logging.DEBUG, **logconf)
    else:
        logging.basicConfig(level=logging.INFO, **logconf)

    consumer = KafkaConsumer('hvbench', 'hvmonitor',
                             bootstrap_servers="%s:9092" % cmdargs.kafka)

    studies = {}

    for msg in consumer:

        jmsg = json.loads(str(msg.value, 'ASCII'))

        if jmsg['study_id'] not in studies:

            ldir = os.path.join(cmdargs.output, jmsg['study_id'])

            os.makedirs(ldir, exist_ok=True)

            studies[jmsg['study_id']] = Study(ldir)

        try:
            studies[jmsg['study_id']].writerow(str(msg.topic), jmsg)
        except ValueError:
            log.error("Error writing row! This may mean the CSV headers changed! Use a fresh log file.")
            break

    log.info("Quitting..")
