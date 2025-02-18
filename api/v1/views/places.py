#!/usr/bin/python3
"""Places hanlders."""

from api.v1.views import app_views
from flask import abort, jsonify, request, make_response
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.amenity import Amenity
from models.state import State
import requests
import json
from os import getenv


@app_views.route(
    "/cities/<string:city_id>/places", methods=["GET"], strict_slashes=False
)
def get_places(city_id):
    """Retrieve all the places of the a specific city."""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = []
    for place in city.places:
        places.append(place.to_dict())
    return jsonify(places)


@app_views.route(
    "/places/<string:place_id>",
    methods=["GET"],
    strict_slashes=False,
)
def get_place(place_id):
    """Get info about a specific place."""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route(
    "/places/<string:place_id>", methods=["DELETE"], strict_slashes=False
)
def delete_place(place_id):
    """Delete a specific place."""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({})


@app_views.route(
    "/cities/<string:city_id>/places", methods=["POST"], strict_slashes=False
)
def create_place(city_id):
    """Create a new city."""
    r = request.get_json(silent=True)
    if not r:
        abort(400, "Not a JSON")
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if "user_id" not in r:
        abort(400, "Missing user_id")
    user = storage.get(User, r["user_id"])
    if user is None:
        abort(404)
    if "name" not in r:
        abort(400, "Missing name")
    r["city_id"] = city_id
    place = Place(**r)
    place.save()
    return make_response(jsonify(place.to_dict()), 201)


@app_views.route(
    "/places/<string:place_id>", methods=["PUT"], strict_slashes=False
)
def update_place(place_id):
    """Update a specific place."""
    r = request.get_json(silent=True)
    if not r:
        abort(400, "Not a JSON")
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    for key, value in request.get_json().items():
        if key not in [
            "id",
            "created_at",
            "updated_at",
            "city_id",
            "user_id",
        ]:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict())


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """
    Retrieves all Place objects based on filters:
    - states: List of State IDs → Includes all places in those states.
    - cities: List of City IDs → Includes all places in those cities.
    - amenities: List of Amenity IDs → Filters results to places with them.
    """
    body_r = request.get_json(silent=True)
    if body_r is None:
        abort(400, "Not a JSON")

    if not any(body_r.get(k) for k in ["states", "cities", "amenities"]):
        return jsonify([p.to_dict() for p in storage.all(Place).values()])

    places = set()

    if body_r.get('states'):
        states = [storage.get(State, sid) for sid in body_r['states']]
        states = [s for s in states if s]
        for state in states:
            for city in state.cities:
                places.update(city.places)

    if body_r.get('cities'):
        cities = [storage.get(City, cid) for cid in body_r['cities']]
        cities = [c for c in cities if c]
        for city in cities:
            places.update(city.places)

    if not places:
        places = set(storage.all(Place).values())

    if body_r.get('amenities'):
        amenities = {storage.get(Amenity, aid) for aid in body_r['amenities']}
        amenities = {a for a in amenities if a}

        places = {
            p for p in places if all(a in p.amenities for a in amenities)
        }

    return jsonify([p.to_dict() for p in places])
