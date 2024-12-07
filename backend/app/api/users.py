#user-related routes
from flask import Blueprint, request, jsonify
from app.db import supabase  # Assumes you have initialized Supabase client
from werkzeug.security import generate_password_hash, check_password_hash
import random

users_api = Blueprint("users_api", __name__)

# Store the math question and answer in memory
math_question_answer = {}

# Function to generate random arithmetic questions
def generate_math_question():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operation = random.choice(["+", "-", "*"])
    question = f"What is {num1} {operation} {num2}?"
    answer = eval(f"{num1} {operation} {num2}")
    return question, answer

# Route to fetch a math question
@users_api.route("/auth/math-question", methods=["GET"])
def get_math_question():
    try:
        question, answer = generate_math_question()
        math_question_answer["answer"] = answer
        return jsonify({"success": True, "question": question}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Route to register a new user
@users_api.route("/auth/register", methods=["POST"])
def register_user():
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be in JSON format"}), 400
    
    try:
        # Parse request data
        request_data = request.get_json()
        email = request_data.get("email")
        password = request_data.get("password")
        name = request_data.get("name")
        answer = request_data.get("answer")

        # Validate input
        if not email or not password or not name or not answer:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Verify math question answer
        if math_question_answer.get("answer") != int(answer):
            return jsonify({"success": False, "error": "Incorrect arithmetic answer"}), 400

        # Check if email already exists
        existing_user = supabase.table("users").select("id").eq("email", email).execute()
        if existing_user.data:
            return jsonify({"success": False, "error": "Email already exists"}), 400

        new_user = {
            "email": email,
            "password": password,
            "name": name,
            "account_type": "User"
        }

        response = supabase.table("users").insert(new_user).execute()
        if response.data:
            return jsonify({"success": True, "message": "User successfully registered", "user": response.data[0]}), 201
        else:
            return jsonify({"success": False, "error": "Registration unsuccessful"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@users_api.route("/auth/login", methods=["POST"])
def login_user():
    """
    Handle user login.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        # Parse the JSON request
        request_data = request.get_json()
        email = request_data.get("email")
        password = request_data.get("password")

        # Validate input
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400

        # Query the database for the user
        response = supabase.table("users").select("*").eq("email", email).execute()

        if not response.data:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401

        user = response.data[0]  # Assuming the email is unique and we get a single result

        # Validate the password
        if user["password"] != password:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401

        # If login is successful
        return jsonify({
            "success": True,
            "message": "User logged in successfully",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "account_type": user["account_type"],
                "balance": user["balance"],
            },
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@users_api.route("/deposit", methods=["POST"])
def deposit():
    """
    Allows a user to deposit money into their account.
    """
    try:
        request_data = request.get_json()
        user_id = request_data.get("user_id")
        amount = request_data.get("amount")

        # Validate user_id
        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400

        # Validate amount
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Amount must be a valid number"}), 400

        if amount <= 0:
            return jsonify({"success": False, "error": "Deposit amount must be positive"}), 400

        # Fetch the user's current balance
        user_response = supabase.table("users").select("balance").eq("id", user_id).execute()
        if not user_response.data:
            return jsonify({"success": False, "error": "User not found"}), 404

        current_balance = user_response.data[0]["balance"]
        new_balance = current_balance + amount
        supabase.table("users").update({"balance": new_balance}).eq("id", user_id).execute()

        return jsonify({"success": True, "message": "Deposit successful", "balance": new_balance}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@users_api.route("/withdraw", methods=["POST"])
def withdraw():
    """
    Allows a user to withdraw money from their account.
    """
    try:
        request_data = request.get_json()
        user_id = request_data.get("user_id")
        amount = request_data.get("amount")

        # Validate user_id
        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400

        # Validate amount
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Amount must be a valid number"}), 400

        if amount <= 0:
            return jsonify({"success": False, "error": "Withdraw amount must be positive"}), 400

        # Fetch the user's current balance
        user_response = supabase.table("users").select("balance").eq("id", user_id).execute()
        if not user_response.data:
            return jsonify({"success": False, "error": "User not found"}), 404

        current_balance = user_response.data[0]["balance"]
        if amount > current_balance:
            return jsonify({"success": False, "error": "Insufficient funds"}), 400

        new_balance = current_balance - amount
        supabase.table("users").update({"balance": new_balance}).eq("id", user_id).execute()

        return jsonify({"success": True, "message": "Withdrawal successful", "balance": new_balance}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
