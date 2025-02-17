#!/usr/bin/python3
"""Users hanlders."""

from flask import abort, jsonify, request, make_response
from api.v1.views import app_views
from models import storage
from models.user import User


@app_views.route("/users", methods=["GET"], strict_slashes=False)
def get_users():
    """Retrieve all the users."""
    users = []
    for user in storage.all(User).values():
        users.append(user.to_dict())
    return jsonify(users)


@app_views.route(
    "/users/<string:user_id>", methods=["GET"], strict_slashes=False
)
def get_user(user_id):
    """Get info about a specific user."""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    return jsonify(user.to_dict())


@app_views.route(
    "/users/<string:user_id>", methods=["DELETE"], strict_slashes=False
)
def delete_user(user_id):
    """Delete a specific user."""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    storage.delete(user)
    storage.save()
    return jsonify({})


@app_views.route("/users", methods=["POST"], strict_slashes=False)
def create_user():
    """Create a new user."""
    r = request.get_json(silent=True)
    if not r:
        abort(400, "Not a JSON")
    if "email" not in r:
        abort(400, "Missing email")
    if "password" not in r:
        abort(400, "Missing passord")
    user = User(**r)
    user.save()
    return make_response(jsonify(user.to_dict()), 201)


@app_views.route(
    "/users/<string:user_id>", methods=["PUT"], strict_slashes=False
)
def update_user(user_id):
    """Update a specific user."""
    r = request.get_json(silent=True)
    if not r:
        abort(400, "Not a JSON")
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    for key, value in request.get_json().items():
        if key not in ["id", "created_at", "updated_at", "email"]:
            setattr(user, key, value)
    user.save()
    return jsonify(user.to_dict())
