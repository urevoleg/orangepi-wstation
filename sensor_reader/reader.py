from pprint import pprint
import requests


class Sensor:
    def __init__(self, host, port, path):
        self.host = host
        self.port = port
        self.path = path

    def _create_url(self):
        return f"http://{self.host}:{self.port}/{self.path}"

    def read(self):
        host = '192.168.55.27'
        url = f"http://{host}/sensors"
        response = requests.get(url=url)
        response.raise_for_status()
        return response.json()


if __name__ == '__main__':
    host = '192.168.55.27'
    url = f"http://{host}/sensors"
    response = requests.get(url=url)

    pprint(response.json())

