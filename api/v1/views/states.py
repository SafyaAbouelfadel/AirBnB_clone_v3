#!/usr/bin/python3
"""States hanlders."""

from flask import abort, jsonify, request, make_response
from api.v1.views import app_views
from models import storage
from models.state import State


@app_views.route("/states", methods=["GET"], strict_slashes=False)
def get_states():
    """Retrieves the list of all State objects."""
    states = []
    for state in storage.all(State).values():
        states.append(state.to_dict())
    return jsonify(states)


@app_views.route(
    "/states/<string:state_id>", methods=["GET"], strict_slashes=False
)
def get_state(state_id):
    """Retrieves a State object."""
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    return jsonify(state.to_dict())


@app_views.route(
    "/states/<string:state_id>", methods=["DELETE"], strict_slashes=False
)
def delete_state(state_id):
    """Delete a specific state by state id."""
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    storage.delete(state)
    storage.save()
    return jsonify({})


@app_views.route("/states", methods=["POST"], strict_slashes=False)
def create_state():
    """Create a new state."""
    r = request.get_json(silent=True)
    if not r:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if "name" not in r:
        return make_response(jsonify({"error": "Missing name"}), 400)
    state = State(**r)
    state.save()
    return make_response(jsonify(state.to_dict()), 201)


@app_views.route(
    "/states/<string:state_id>", methods=["PUT"], strict_slashes=False
)
def update_state(state_id):
    """Update a specific state."""
    r = request.get_json(silent=True)
    if not r:
        abort(400, "Not a JSON")
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    for key, value in r.items():
        if key not in ["id", "created_at", "updated_at"]:
            setattr(state, key, value)
    state.save()
    return jsonify(state.to_dict())
