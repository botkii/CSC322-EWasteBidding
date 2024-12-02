from flask import Blueprint, jsonify
import os
from app.db import test_users_table

test_api = Blueprint("test_api", __name__)

# Route to test Supabase environment variables
# when running backend for testing Supabase use this link http://127.0.0.1:5000/api/v1/test/test-env
@test_api.route("/test-env", methods=["GET"])
def test_env():
    return {
        "supabase_url": os.getenv("SUPABASE_URL"),
        "supabase_key": os.getenv("SUPABASE_KEY")
    }

# Route to test the users table
# when running backend for testing users table use this link http://127.0.0.1:5000/api/v1/test/test-users
@test_api.route("/test-users", methods=["GET"])
def test_users():
    data = test_users_table()
    if data:
        return jsonify({"success": True, "users": data}), 200
    else:
        return jsonify({"success": True, "users": [], "message": "No users found"}), 200
