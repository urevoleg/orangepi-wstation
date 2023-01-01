import datetime as dt


from flask import Flask, jsonify


app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({
	"dt": dt.datetime.now()
})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
