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


@app_views.route('/places_search', methods=['POST'])
def places_search():
    """
    Search for places based on states, cities, and amenities.
    """
    all_places = [p for p in storage.all('Place').values()]
    req_json = request.get_json(silent=True)

    if req_json is None:
        abort(400, 'Not a JSON')

    states = req_json.get('states', [])
    cities = req_json.get('cities', [])
    amenities = req_json.get('amenities', [])

    state_cities = set()
    if states:
        all_cities = storage.all('City')
        state_cities = {
            city.id for city in all_cities.values()
            if city.state_id in states
        }

    if cities:
        valid_cities = {
            c_id for c_id in cities if storage.get('City', c_id)
        }
        state_cities.update(valid_cities)

    if state_cities:
        all_places = [
            p for p in all_places if p.city_id in state_cities
        ]

    if not amenities:
        return jsonify([
            place.to_json() for place in all_places
        ])

    valid_amenities = {
        a_id for a_id in amenities if storage.get('Amenity', a_id)
    }
    places_amenities = []

    for place in all_places:
        p_amenities = set(a.id for a in place.amenities) \
            if place.amenities else set()

        if valid_amenities.issubset(p_amenities):
            places_amenities.append(place)

    return jsonify([
        place.to_json() for place in places_amenities
    ])

