#!/usr/bin/python3
"""Cities hanlders."""

from flask import abort, jsonify, request, make_response
from api.v1.views import app_views
from models import storage
from models.city import City
from models.state import State


@app_views.route(
    "/states/<string:state_id>/cities", methods=["GET"], strict_slashes=False
)
def get_cities(state_id):
    """Retrieve all the cities of the specified state."""
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    all_cities = []
    for city in state.all_cities:
        all_cities.append(city.to_dict())
    return jsonify(all_cities)


@app_views.route(
    "/cities/<string:city_id>",
    methods=["GET"],
    strict_slashes=False,
)
def get_city(city_id):
    """Get info about specified city."""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    return jsonify(city.to_dict())


@app_views.route(
    "/cities/<string:city_id>", methods=["DELETE"], strict_slashes=False
)
def delete_city(city_id):
    """Delete specified city."""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    storage.delete(city)
    storage.save()
    return jsonify({})


@app_views.route(
    "/states/<string:state_id>/cities", methods=["POST"], strict_slashes=False
)
def create_city(state_id):
    """Create a new city."""
    r = request.get_json(silent=True)
    if not r:
        abort(400, "Not a JSON")
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    if "name" not in request.get_json():
        abort(400, "Missing name")
    r["state_id"] = state_id
    city = City(**r)
    city.save()
    return make_response(jsonify(city.to_dict()), 201)


@app_views.route(
    "/cities/<string:city_id>", methods=["PUT"], strict_slashes=False
)
def update_city(city_id):
    """Update specified city."""
    r = request.get_json(silent=True)
    if not r:
        abort(400, "Not a JSON")
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    for key, value in request.get_json().items():
        if key not in ["id", "created_at", "updated_at", "state_id"]:
            setattr(city, key, value)
    city.save()
    return jsonify(city.to_dict())
