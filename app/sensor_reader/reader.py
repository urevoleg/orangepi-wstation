from pprint import pprint
import requests
import logging

logging.basicConfig(level=logging.DEBUG,
                format="⏰ %(asctime)s - 💎 %(levelname)s - %(filename)s - %(funcName)s:%(lineno)s - 🧾 %(message)s")
logger = logging.getLogger(__name__)


class SensorReader:
    def __init__(self, host, port, path, **kwargs):
        self.host = host
        self.port = port
        self.path = path
        logger.info('SensorReader successfully init!')

    def _create_url(self):
        return f"http://{self.host}:{self.port}/{self.path}"

    def read(self):
        url = self._create_url()
        logger.info(f'Start read sensor with url: {url}')
        response = requests.get(url=url)
        response.raise_for_status()
        return response.json()


if __name__ == '__main__':
    response = SensorReader(**{'host': '192.168.55.27', 'port': 80, 'path': 'sensors'}).read()
    pprint(response)

