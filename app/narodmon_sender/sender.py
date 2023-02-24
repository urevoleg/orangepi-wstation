import os

import requests
import socket

from typing import Dict

from dotenv import load_dotenv
load_dotenv()


class Sender:
    def __init__(self, host, port, post_uri):
        self.host = host
        self.port = port
        self.post_uri = post_uri

    def send(self, data:Dict={}):
        headers = {
            'Content-Length': str(len(data)),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'narodmon.ru'
        }
        response = requests.post(url=self.post_uri, data=data, headers=headers)
        response.raise_for_status()
        return response

    @staticmethod
    def _name_sensor_mappings(name):
        return {
            't_out': f"{os.getenv('NARODMON_DEVICE_MAC')}01",
            'h': f"{os.getenv('NARODMON_DEVICE_MAC')}02",
            'p': f"{os.getenv('NARODMON_DEVICE_MAC')}03",
            'l': f"{os.getenv('NARODMON_DEVICE_MAC')}04",
            't_in': f"{os.getenv('NARODMON_DEVICE_MAC')}05",
            'gas': f"{os.getenv('NARODMON_DEVICE_MAC')}09"
        }.get(name)