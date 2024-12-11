#user-related routes
from flask import Blueprint, request, jsonify, session, current_app
from functools import wraps
from app.middlewares import restrict_banned_users
from app.db import supabase  # Assumes you have initialized Supabase client
#from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime, timezone
from app.utils import perform_user_suspensions


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


# Updated login route to include JWT
@users_api.route("/auth/login", methods=["POST"])
def login_user():
    """
    Handle user login.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        request_data = request.get_json()
        email = request_data.get("email")
        password = request_data.get("password")

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400

        response = supabase.table("users").select("*").eq("email", email).execute()

        if not response.data:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401

        user = response.data[0]

        if user["password"] != password:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401

        if user["banned"]:
            return jsonify({"success": False, "error": "Access restricted for banned users"}), 403

        # Set session or any other mechanism for tracking logged-in state
        session["user_id"] = user["id"]
        session["account_type"] = user["account_type"]

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

@users_api.route("/user-info", methods=["GET"])
def get_user_info():
    """
    Fetch a user's information based on their user_id.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        # Get the user_id from the request
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400

        # Fetch the user's information from the database
        user_response = supabase.table("users").select("id, name, email, balance, account_type, complaint_count, rating, transaction_count").eq("id", user_id).execute()

        if not user_response.data:
            return jsonify({"success": False, "error": "User not found"}), 404

        user = user_response.data[0]

        return jsonify({
            "success": True,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "balance": user["balance"],
                "account_type": user["account_type"],
                "complaint_count": user.get("complaint_count", 0),
                "rating": user.get("rating", 0),
                "transaction_count": user.get("transaction_count", 0),
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    
@users_api.route("/upgrade-to-vip", methods=["POST"])
def upgrade_to_vip():
    """
    Automatically upgrades users to VIP status if they meet the criteria:
    - Balance > $5,000
    - More than 5 transactions
    - 0 complaints
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400

        # Fetch user details
        user_response = supabase.table("users").select("balance, transaction_count, complaint_count, account_type").eq("id", user_id).execute()
        if not user_response.data:
            return jsonify({"success": False, "error": "User not found"}), 404

        user = user_response.data[0]

        # Check if user meets VIP criteria
        if (
            user["balance"] > 5000 and
            user["transaction_count"] > 5 and
            user["complaint_count"] == 0 and
            user["account_type"] != "VIP"
        ):
            # Upgrade to VIP
            supabase.table("users").update({"account_type": "VIP"}).eq("id", user_id).execute()
            return jsonify({"success": True, "message": "User upgraded to VIP successfully"}), 200

        return jsonify({"success": False, "message": "User does not meet VIP criteria"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



@users_api.route("/browse", methods=["GET"])
def browse():
    """
    Route accessible by all users, including visitors and logged-in users, to browse items.
    """
    try:
        # Example query to fetch items from the database
        items_response = supabase.table("items").select("*").execute()
        if not items_response.data:
            return jsonify({"success": True, "items": [], "message": "No items available"}), 200

        # Determine user role (Visitor by default)
        if "user_id" in session:
            user_role = session.get("account_type", "User")
        else:
            user_role = "Visitor"

        return jsonify({
            "success": True,
            "role": user_role,
            "items": items_response.data,
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@users_api.route("/rate-user", methods=["POST"])
@restrict_banned_users
def rate_user():
    """
    Allows users to rate another user (buyer/seller).
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        target_user_id = data.get("user_id")  # The user being rated
        rating = data.get("rating")

        # Validate inputs
        if not target_user_id or rating is None:
            return jsonify({"success": False, "error": "User ID and rating are required"}), 400
        if not (0 <= rating <= 5):
            return jsonify({"success": False, "error": "Rating must be between 0 and 5"}), 400

        # Fetch the user's current rating and rating count
        user_response = supabase.table("users").select("rating, rating_count").eq("id", target_user_id).execute()
        if not user_response.data:
            return jsonify({"success": False, "error": "User not found"}), 404

        user = user_response.data[0]
        current_rating = user.get("rating", 0)
        rating_count = user.get("rating_count", 0)

        # Calculate the new average rating
        new_rating = ((current_rating * rating_count) + rating) / (rating_count + 1)

        # Update the user's rating and rating count
        supabase.table("users").update({
            "rating": new_rating,
            "rating_count": rating_count + 1
        }).eq("id", target_user_id).execute()

        return jsonify({
            "success": True,
            "message": "User rated successfully",
            "new_rating": new_rating,
            "rating_count": rating_count + 1
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@users_api.route("/add-comment", methods=["POST"])
@restrict_banned_users
def add_comment():
    """
    Allows visitors or logged-in users to add comments.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        item_id = data.get("item_id")
        comment = data.get("comment")

        if not item_id or not comment:
            return jsonify({"success": False, "error": "Item ID and comment are required"}), 400

        # Check if the user is logged in
        user_id = session.get("user_id")
        user_name = "Anonymous"

        if user_id:
            # Fetch the user's name from the database
            user_response = supabase.table("users").select("name").eq("id", user_id).execute()
            if user_response.data:
                user_name = user_response.data[0]["name"]

        # Add the comment to the database
        supabase.table("comments").insert({
            "item_id": item_id,
            "comment": comment,
            "user_id": user_id,  # Null for visitors
            "user_name": user_name,  # 'Anonymous' for visitors
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()

        return jsonify({"success": True, "message": "Comment added successfully"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@users_api.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    """
    Allows a user to submit a complaint against another user.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        complainant_id = data.get("complainant_id")
        target_user_id = data.get("target_user_id")
        description = data.get("description")

        if not complainant_id or not target_user_id or not description:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Ensure the target user exists
        user_response = supabase.table("users").select("id, complaint_count").eq("id", target_user_id).execute()
        if not user_response.data:
            return jsonify({"success": False, "error": "Target user not found"}), 404

        # Fetch the current complaint count
        current_complaint_count = user_response.data[0].get("complaint_count", 0)

        # Insert the complaint into the complaints table
        supabase.table("complaints").insert({
            "complainant_id": complainant_id,
            "target_user_id": target_user_id,
            "description": description
        }).execute()

        # Increment the complaint count manually
        supabase.table("users").update({
            "complaint_count": current_complaint_count + 1
        }).eq("id", target_user_id).execute()

        return jsonify({"success": True, "message": "Complaint submitted successfully"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@users_api.route("/fetch-complaints", methods=["GET"])
def fetch_complaints():
    """
    Fetch complaints submitted against a specific user.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        # Parse the request data
        data = request.get_json()
        user_id = data.get("user_id")  # The user whose complaints are being fetched

        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400

        # Fetch complaints for the specified user
        response = supabase.table("complaints").select("*").eq("target_user_id", user_id).execute()

        if not response.data:
            return jsonify({"success": True, "complaints": [], "message": "No complaints found for this user"}), 200

        return jsonify({"success": True, "complaints": response.data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@users_api.route("/balance", methods=["GET"])
@restrict_banned_users
def get_user_balance():
    """
    Fetch a user's balance.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        # Get the user_id from the request body
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400

        # Query the user's balance from the database
        response = supabase.table("users").select("balance").eq("id", user_id).execute()

        if not response.data:
            return jsonify({"success": False, "error": "User not found"}), 404

        balance = response.data[0]["balance"]
        return jsonify({"success": True, "balance": balance}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@users_api.route("/deposit", methods=["POST"])
@restrict_banned_users
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
@restrict_banned_users
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

@users_api.route("/admin/tasks/pending", methods=["GET"])
def fetch_pending_tasks():
    """
    Fetch all pending tasks for Admin/SuperUser from the admin_tasks table.
    """
    try:
        # Parse query parameters
        admin_id = request.args.get("admin_id")  # ID of the Admin/SuperUser
        task_type = request.args.get("task_type", None)  # Optional filter by task type

        # Validate admin_id
        if not admin_id:
            return jsonify({"success": False, "error": "Admin ID is required"}), 400

        # Check if the requester is an Admin or SuperUser
        admin_response = supabase.table("users").select("account_type").eq("id", admin_id).execute()
        if not admin_response.data or admin_response.data[0]["account_type"] not in ["Admin", "SuperUser"]:
            return jsonify({"success": False, "error": "Unauthorized access"}), 403

        # Build the query
        query = supabase.table("admin_tasks").select("*").eq("status", "pending")
        if task_type:
            query = query.eq("task_type", task_type)

        # Execute the query
        response = query.execute()

        if response.data:
            return jsonify({"success": True, "tasks": response.data}), 200
        else:
            return jsonify({"success": True, "tasks": [], "message": "No pending tasks found."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


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

@users_api.route("/check-suspensions", methods=["POST"])
def check_user_suspensions():
    try:
        success = perform_user_suspensions()
        return jsonify({
            "success": success,
            "message": "Suspension checks completed" if success else "No users to evaluate"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@users_api.route("/admin/unsuspend-user", methods=["POST"])
def unsuspend_user():
    """
    Unsuspend a user based on admin approval or payment of fine, and reset ratings upon reactivation.
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

        # Fetch user details
        user_response = supabase.table("users").select("balance, suspension_status").eq("id", user_id).execute()
        if not user_response.data:
            return jsonify({"success": False, "error": "User not found"}), 404

        user = user_response.data[0]

        if not user["suspension_status"]:
            return jsonify({"success": False, "error": "User is not suspended"}), 400

        if payment_option == "pay_fine":
            # Check user balance
            balance = user["balance"]

            if balance < 50:
                return jsonify({"success": False, "error": "Insufficient balance to pay the suspension fine."}), 400

            # Deduct fine from user balance
            new_balance = balance - 50
            supabase.table("users").update({"balance": new_balance}).eq("id", user_id).execute()

        elif payment_option == "admin_approval":
            # Admin approval case
            pass  # No additional steps required for admin approval

        else:
            return jsonify({"success": False, "error": "Invalid payment option"}), 400

        # Reset ratings and unsuspend the user
        supabase.table("users").update({
            "suspension_status": False,
            "rating": 0,
            "rating_count": 0,
            "suspension_reason": None
        }).eq("id", user_id).execute()

        return jsonify({"success": True, "message": "User unsuspended successfully, and ratings reset."}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@users_api.route("/admin/approve-user", methods=["POST"])
def approve_user_request():
    """
    Admin/SuperUser approves a user's request to become a registered user.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        admin_id = data.get("admin_id")  # ID of the Admin/SuperUser
        task_id = data.get("task_id")  # ID of the approval task in admin_tasks

        if not admin_id or not task_id:
            return jsonify({"success": False, "error": "Admin ID and Task ID are required"}), 400

        # Check admin privileges
        admin_response = supabase.table("users").select("account_type").eq("id", admin_id).execute()
        if not admin_response.data or admin_response.data[0]["account_type"] not in ["Admin", "SuperUser"]:
            return jsonify({"success": False, "error": "Unauthorized access"}), 403

        # Fetch the task from admin_tasks
        task_response = supabase.table("admin_tasks").select("*").eq("id", task_id).execute()
        if not task_response.data or task_response.data[0]["task_type"] != "approve_user":
            return jsonify({"success": False, "error": "Invalid or non-existent approval task"}), 404

        task = task_response.data[0]
        user_id = task["user_id"]

        # Approve the user and update account_type to "User"
        supabase.table("users").update({
            "approval_status": "approved",
            "account_type": "User"  # Change the account type to User
        }).eq("id", user_id).execute()

        # Mark the task as completed
        supabase.table("admin_tasks").update({"status": "completed"}).eq("id", task_id).execute()

        return jsonify({"success": True, "message": "User request approved successfully."}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500





