import datetime as dt


from flask import Flask, jsonify


from w1thermsensor import W1ThermSensor
from libs.pressure import PressureSensor


sensor = W1ThermSensor()

def get_temperature():
    return sensor.get_temperature() 


def get_pressure():
    return PressureSensor(0x77).get_pressure()


app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({
	"dt": dt.datetime.now(),
	"sensors": {
		"t": [{"value": get_temperature(), "type": "ds18b20", "place": "out"}],
		"p": [{"value": get_pressure(), "type": "bmp180"}]
	}
})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
