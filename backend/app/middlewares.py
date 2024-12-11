# app/middlewares.py
from flask import jsonify, session
from functools import wraps
from app.db import supabase  # Access to the Supabase database

def restrict_banned_users(f):
    """
    Middleware to restrict access for banned users.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized access. Please log in."}), 401

        # Check if the user is banned
        user_response = supabase.table("users").select("banned").eq("id", user_id).execute()
        if user_response.data and user_response.data[0]["banned"]:
            return jsonify({
                "success": False,
                "error": "Access restricted. Your account is banned. Please contact support for assistance."
            }), 403

        return f(*args, **kwargs)
    return wrapper
