#!/usr/bin/python3
"""Amenities hanlders."""

from api.v1.views import app_views
from flask import abort, jsonify, request, make_response
from models import storage
from models.amenity import Amenity


@app_views.route("/amenities", methods=["GET"], strict_slashes=False)
def get_amenities():
    """ Retrieves the list of all Amenity objects."""
    amenity_list = []
    for amenity in storage.all(Amenity).values():
        amenity_list.append(amenity.to_dict())
    return jsonify(amenity_list)


@app_views.route(
        "/amenities/<string:amenity_id>", methods=["GET"], strict_slashes=False
)
def get_amenity(amenity_id):
    """Retrieves a Amenity object"""
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)
    return jsonify(amenity.to_dict())


@app_views.route(
    "/amenities/<string:amenity_id>", methods=["DELETE"], strict_slashes=False
)
def delete_amenity(amenity_id):
    """Delete specified amenity."""
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)
    storage.delete(amenity)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route("/amenities", methods=["POST"], strict_slashes=False)
def create_amenity():
    """Create a new amenity."""
    r = request.get_json(silent=True)
    if not r:
        abort(400, "Not a JSON")
    if "name" not in r:
        abort(400, "Missing name")
    amenity = Amenity(**r)
    amenity.save()
    return make_response(jsonify(amenity.to_dict()), 201)


@app_views.route(
    "/amenities/<string:amenity_id>", methods=["PUT"], strict_slashes=False
)
def update_amenity(amenity_id):
    """Update specified amenity."""
    req = request.get_json(silent=True)
    if not req:
        abort(400, "Not a JSON")
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)
    for key, value in req.items():
        if key not in ["id", "created_at", "updated_at"]:
            setattr(amenity, key, value)
    amenity.save()
    return jsonify(amenity.to_dict())
