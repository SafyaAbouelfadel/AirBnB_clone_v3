#!/usr/bin/python3
"""
Create Flask app, app_views
"""

from flask import jsonify, request
from api.v1.views import app_views
from models import storage


@app_views.route("/status")
def api_status():
    """
    function that returns 'OK' status.
    """
    respond = {"status": "OK"}
    if request.method == "GET":
        return jsonify(respond)


@app_views.route("/stats")
def api_stats():
    """
    function that returns global status.
    """
    if request.method == "GET":
        return jsonify(
                {
                    "amenities": storage.count("Amenity"),
                    "cities": storage.count("City"),
                    "places": storage.count("Place"),
                    "reviews": storage.count("Review"),
                    "states": storage.count("State"),
                    "users": storage.count("User"),
                }
            )
