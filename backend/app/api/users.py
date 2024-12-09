#user-related routes
from flask import Blueprint, request, jsonify, session
from app.db import supabase  # Assumes you have initialized Supabase client
#from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime, timezone


users_api = Blueprint("users_api", __name__)

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
        session["math_answer"] = answer  # Store the answer in the session
        print("Generated Math Answer (Server):", session["math_answer"])  # Debugging
        return jsonify({"success": True, "question": question}), 200
    except Exception as e:
        print("Error generating math question:", str(e))
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
        role = request_data.get("role", "Visitor")  # Default to Visitor role

        # Validate input
        if not email or not password or not name or answer is None:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Verify math question answer for Visitors
        if role == "Visitor":
            stored_answer = session.get("math_answer")  # Fetch the answer from the session
            if stored_answer is None:
                return jsonify({"success": False, "error": "Math question not found. Please fetch a new question."}), 400

            try:
                if int(answer) != stored_answer:
                    return jsonify({"success": False, "error": "Incorrect arithmetic answer"}), 400
            except ValueError:
                return jsonify({"success": False, "error": "Answer must be a number"}), 400

        # Check if email already exists
        existing_user = supabase.table("users").select("id").eq("email", email).execute()
        if existing_user.data:
            return jsonify({"success": False, "error": "Email already exists"}), 400

        # Register user
        new_user = {
            "email": email,
            "password": password,
            "name": name,
            "account_type": role,
        }

        # Add approval_status only for Visitors
        if role == "Visitor":
            new_user["approval_status"] = "pending"

        response = supabase.table("users").insert(new_user).execute()
        if response.data:
            user_id = response.data[0]["id"]

            # Add an admin task for approval only for Visitors
            if role == "Visitor":
                try:
                    admin_task = {
                        "user_id": user_id,
                        "task_type": "approve_user",  # Matches the schema constraint
                        "status": "pending",         # Matches the schema constraint
                        "created_at": datetime.now(timezone.utc).isoformat()  # Use ISO format
                    }
                    supabase.table("admin_tasks").insert(admin_task).execute()
                except Exception:
                    pass

            return jsonify({
                "success": True,
                "message": "User registered successfully",
                "user": response.data[0]
            }), 201
        else:
            return jsonify({"success": False, "error": "Registration unsuccessful"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e) if str(e) else "Unknown error"}), 500


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

# Admin methods

# Approve Visitor Requests to become Users
@users_api.route("/admin/request/approve", methods=["POST"])
def request_approve_user():
    """
    Allow Admin/SuperUser to approve a visitor's request to become a user.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        requester_id = data.get("requester_id")  # ID of the Admin/SuperUser
        user_id = data.get("user_id")  # ID of the Visitor

        if not requester_id or not user_id:
            return jsonify({"success": False, "error": "Requester ID and User ID are required"}), 400

        # Check if the requester is a SuperUser or Admin
        requester_response = supabase.table("users").select("account_type").eq("id", requester_id).execute()
        if not requester_response.data:
            return jsonify({"success": False, "error": "Requester not found"}), 404

        requester = requester_response.data[0]
        if requester["account_type"] not in ["SuperUser", "Admin"]:
            return jsonify({"success": False, "error": "Unauthorized access"}), 403

        # Add an approval request task to admin_tasks
        task = {
            "user_id": user_id,
            "task_type": "approve_user",
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        response = supabase.table("admin_tasks").insert(task).execute()

        if response.data:
            return jsonify({"success": True, "message": "Approval request added to admin tasks."}), 201
        else:
            return jsonify({"success": False, "error": "Failed to add approval request"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@users_api.route("/admin/request/reactivate", methods=["POST"])
def request_reactivation():
    """
    Allow suspended users to request reactivation.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400

        # Add a reactivation request task to admin_tasks
        task = {
            "user_id": user_id,
            "task_type": "reactivate_user",
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        response = supabase.table("admin_tasks").insert(task).execute()

        if response.data:
            return jsonify({"success": True, "message": "Reactivation request added to admin tasks."}), 201
        else:
            return jsonify({"success": False, "error": "Failed to add reactivation request"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@users_api.route("/admin/request/quit", methods=["POST"])
def request_quit():
    """
    Allow users to request to quit the system.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400

        # Add a quit request task to admin_tasks
        task = {
            "user_id": user_id,
            "task_type": "quit_request",
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        response = supabase.table("admin_tasks").insert(task).execute()

        if response.data:
            return jsonify({"success": True, "message": "Quit request added to admin tasks."}), 201
        else:
            return jsonify({"success": False, "error": "Failed to add quit request"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@users_api.route("/admin/approve-quit", methods=["POST"])
def approve_quit():
    """
    Approve a user's quit request and remove them from the system.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        task_id = data.get("task_id")
        admin_id = data.get("admin_id")

        # Check admin privileges
        admin_response = supabase.table("users").select("account_type").eq("id", admin_id).execute()
        if not admin_response.data or admin_response.data[0]["account_type"] not in ["Admin", "SuperUser"]:
            return jsonify({"success": False, "error": "Unauthorized access"}), 403

        # Fetch the quit request from admin_tasks table
        task_response = supabase.table("admin_tasks").select("*").eq("id", task_id).execute()
        if not task_response.data or task_response.data[0]["task_type"] != "quit_request":
            return jsonify({"success": False, "error": "Invalid quit request"}), 404

        user_id = task_response.data[0]["user_id"]

        # Remove the user
        supabase.table("users").delete().eq("id", user_id).execute()

        # Update the task status
        supabase.table("admin_tasks").update({"status": "completed"}).eq("id", task_id).execute()

        return jsonify({"success": True, "message": "User quit request approved and user removed from system"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



@users_api.route("/admin/ban-user", methods=["POST"])
def ban_user():
    """
    Ban a user after exceeding suspension limits.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        user_id = data.get("user_id")
        admin_id = data.get("admin_id")

        # Check admin privileges
        admin_response = supabase.table("users").select("account_type").eq("id", admin_id).execute()
        if not admin_response.data or admin_response.data[0]["account_type"] not in ["Admin", "SuperUser"]:
            return jsonify({"success": False, "error": "Unauthorized access"}), 403

        # Fetch user details
        user_response = supabase.table("users").select("suspension_count").eq("id", user_id).execute()
        if not user_response.data:
            return jsonify({"success": False, "error": "User not found"}), 404

        suspension_count = user_response.data[0].get("suspension_count", 0)

        if suspension_count >= 3:
            # Mark user as banned
            supabase.table("users").update({"banned": True}).eq("id", user_id).execute()
            return jsonify({"success": True, "message": "User has been banned after exceeding suspension limits."}), 200

        return jsonify({"success": False, "error": "User has not exceeded suspension limits."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@users_api.route("/admin/unsuspend-user", methods=["POST"])
def unsuspend_user():
    """
    Unsuspend a user based on admin approval or payment of fine.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        user_id = data.get("user_id")
        admin_id = data.get("admin_id")
        payment_option = data.get("payment_option")  # "pay_fine" or "admin_approval"

        if not user_id or not admin_id or not payment_option:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Check admin privileges
        admin_response = supabase.table("users").select("account_type").eq("id", admin_id).execute()
        if not admin_response.data or admin_response.data[0]["account_type"] not in ["Admin", "SuperUser"]:
            return jsonify({"success": False, "error": "Unauthorized access"}), 403

        if payment_option == "pay_fine":
            # Fetch user balance
            user_response = supabase.table("users").select("balance").eq("id", user_id).execute()
            if not user_response.data:
                return jsonify({"success": False, "error": "User not found"}), 404

            balance = user_response.data[0]["balance"]

            # Check if user has enough balance to pay the fine
            if balance < 50:
                return jsonify({"success": False, "error": "Insufficient balance to pay the suspension fine."}), 400

            # Deduct fine from user balance and update suspension status
            new_balance = balance - 50
            supabase.table("users").update({"balance": new_balance, "suspension_status": False}).eq("id", user_id).execute()

        elif payment_option == "admin_approval":
            # Directly update suspension status with admin approval
            supabase.table("users").update({"suspension_status": False}).eq("id", user_id).execute()
        else:
            return jsonify({"success": False, "error": "Invalid payment option"}), 400

        return jsonify({"success": True, "message": "User unsuspended successfully."}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



