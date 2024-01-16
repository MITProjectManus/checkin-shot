#/usr/local/bin/python3

from flask import Flask, json, jsonify
app = Flask(__name__)

@app.route('/', methods=['GET'])
def lost_world():
	response = jsonify('Lost? This is not a public API. Contact make-admin@mit.edu.')
	response.status_code = 200
	return response

if __name__ == "__main__":
	app.run(debug=True)
