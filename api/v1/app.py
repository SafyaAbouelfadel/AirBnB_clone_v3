#!/usr/bin/python3
"""
Create Flask app, and register the blueprint app_views to Flask instance app.
"""
from os import getenv
from flask import Flask, jsonify
from models import storage
from api.v1.views import app_views
from flask_cors import CORS

app = Flask(__name__)

app.register_blueprint(app_views)

cors = CORS(app, resources={"/*": {"origins": "0.0.0.0"}})


@app.teardown_appcontext
def close_db(exception):
    """Close the database connection after each request."""
    storage.close()


@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    respond = {"error": "Not found"}
    return jsonify(respond), 404


if __name__ == "__main__":
    HOST = getenv("HBNB_API_HOST", "0.0.0.0")
    PORT = int(getenv("HBNB_API_PORT", 5000))
    app.run(host=HOST, port=PORT, threaded=True)
