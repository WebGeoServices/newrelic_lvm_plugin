#!/usr/bin/env python
# coding=utf-8
import json
import requests
import os
import logging
import argparse
import daemonize
import signal
import socket
import subprocess
from time import sleep

from assets.lvs_commands_datas import lvs_asset

logger = logging.getLogger('newrelic_lvm')
pid = "/tmp/nr_lvm_thinpool.pid"
newrelic_guid = "com.webgeoservices.lvm_thinpool"


def parse_config_file(config_file):
    config_values = {}
    try:
        config = open(config_file, 'r')
    except IOError:
        logger.error("newrelic sysmond config file is unreachable")
        return False
    else:
        for line in config.readlines():
            if line[0] != "#" and len(line.strip()) != 0:
                config_var = line.split("=")
                config_values[config_var[0].strip()] = config_var[1].strip()
        config.close()
    return config_values


def set_environment_variables(config_values):
    if "NEWRELIC_LICENCE_KEY" not in os.environ:
        os.environ["NEWRELIC_LICENCE_KEY"] = config_values.get("license_key", "")
    if "NEWRELIC_HOSTNAME" not in os.environ:
        if "hostname" in config_values:
            os.environ["NEWRELIC_HOSTNAME"] = config_values["hostname"]
        else:
            hostname = socket.gethostname()
            os.environ["NEWRELIC_HOSTNAME"] = hostname


def setup_arg_parser():
    parser = argparse.ArgumentParser(description='LVM thinpool plugin for Newrelic')
    parser.add_argument("state", help="start/stop daemon")
    parser.add_argument('-f', dest='foreground', default=False, action='store_true',
                        help='Launch process in foreground')
    parser.add_argument('--log', dest='loglevel', default="ERROR",
                        help='Define LogLevel')
    parser.add_argument('--config', dest='config', default=None,
                        help='Path to the config file')
    return parser


def setup_logger(loglevel):
    logger.setLevel(loglevel)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)


def set_headers():
    headers = {
        'X-License-Key': os.environ.get("NEWRELIC_LICENCE_KEY", None),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    return headers


def set_datas():
    def add_volume(line):
        meta_percent = 0
        try:
            lvs_values = line.decode('utf8').split(',')
            volume_name = lvs_values[0].strip()
            volume_space = float(lvs_values[1].strip()[:-1])
            data_percent = float(lvs_values[2].strip())
            if lvs_values[3].strip() != "":
                meta_percent = float(lvs_values[3].strip())
        except Exception as e:
            logger.info(e)
            return None
        else:
            return {
                'name': volume_name,
                'space': volume_space,
                'data': data_percent,
                'meta': meta_percent
            }

    lvm_datas = []
    volumes = []
    process_id = os.getpid()
    try:
        lvs_result = subprocess.check_output(["lvs","--noheadings","-o","lv_name,lv_size,data_percent,metadata_percent", "--separator",","])
        lvs_lines = lvs_result.splitlines()
        for line in lvs_lines:
            volume_data = add_volume(line)
            if volume_data:
                volumes.append(volume_data)

    except subprocess.CalledProcessError as e:
        logger.error(e)
        raise e
    except IndexError:
        logger.error("lvs command return unknown values")
        logger.error("lvs --noheadings -o lv_name,data_percent,metadata_percent")
        return None
    except Exception as e:
        logger.error(e)
        raise e
    else:
        for volume in volumes:
            lvm_datas.append({
                  "agent": {
                    "host": os.environ["NEWRELIC_HOSTNAME"]+" / "+volume['name'],
                    "pid": process_id,
                    "version": "0.0.2"
                  },
                  "components": [
                    {
                      "name": os.environ["NEWRELIC_HOSTNAME"]+" / "+volume['name'],
                      "guid": newrelic_guid,
                      "duration": 60,
                      "metrics": {
                        "Component/lvm/space/Total[gigaBytes|read]": int(volume['space']),
                        "Component/lvm/usage/Data/Used[percent]": volume['data'],
                        "Component/lvm/usage/Metadata/Used[percent]": volume['meta']
                      }
                    }
                  ]
                })
        return lvm_datas


def post_response(headers, datas):
    response = requests.post(
        "https://platform-api.newrelic.com/platform/v1/metrics",
        json.dumps(datas),
        headers=headers
    )

    if response.status_code != 200:
        try:
            json_response = json.loads(response.content)
            logger.error(json_response["error"])
        except:
            logger.critical(response.content)
    else:
        resp = response.json()
        logger.info(json.dumps(datas))
        logger.info("""Send datas to Newrelic : %s"""%resp["status"])


def launch_daemon():
    while True:
        try:
            headers = set_headers()
            datas = set_datas()
            for data in datas:
                post_response(headers, data)
            sleep(60)
        except KeyboardInterrupt:
            exit()


def main():
    parser = setup_arg_parser()
    args = parser.parse_args()
    loglevel = args.loglevel
    setup_logger(getattr(logging, loglevel.upper(), None))
    config_file = "/etc/newrelic/nrsysmond.cfg"

    if args.state == "start":
        if args.config:
            config_file=args.config

        config_values = parse_config_file(config_file)
        if config_values:
            set_environment_variables(config_values)
            daemon = daemonize.Daemonize(
                app="nr_lvm_daemon",
                pid=pid,
                action=launch_daemon,
                logger=logger,
                foreground=args.foreground
            )
            daemon.start()
        else:
            exit()

    elif args.state == "stop":
        try:
            process_id=open(pid, 'r').read()
            os.kill(int(process_id), signal.SIGTERM)
        except:
            logger.error("Daemon process id is unreachable")

if __name__ == "__main__":
    exit(main())
