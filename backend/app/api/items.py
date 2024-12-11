from flask import Blueprint, request, jsonify
from app.utils import upload_image
from app.db import supabase  # Assuming this initializes the Supabase client
from datetime import datetime, timezone
from app.middlewares import restrict_banned_users

items_api = Blueprint("items_api", __name__)

@items_api.route("/items", methods=["POST"])
@restrict_banned_users
def create_item():
    try:
        # Parse form data
        user_id = request.form.get("user_id")
        name = request.form.get("name")
        description = request.form.get("description")
        starting_price = request.form.get("starting_price")
        deadline = request.form.get("deadline")

        # Validate required fields
        if not user_id or not name or not starting_price or not deadline:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Handle image upload if an image is provided
        image_url = None
        if "image" in request.files:
            file = request.files["image"]
            upload_response = upload_image(file)
            if upload_response["success"]:
                image_url = upload_response["url"]
            else:
                return jsonify({"success": False, "error": upload_response["error"]}), 400

        # Create the item in the database
        response = supabase.table("items").insert({
            "user_id": user_id,
            "name": name,
            "description": description,
            "starting_price": starting_price,
            "current_price": starting_price,  # Set current_price to starting_price
            "deadline": deadline,
            "image_url": image_url
        }).execute()

        # Check if the item was successfully created
        if not response.data:
            return jsonify({"success": False, "error": "Failed to create item"}), 500

        return jsonify({"success": True, "item": response.data[0]}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@items_api.route("/available-items", methods=["GET"])
def fetch_available_items():
    """
    Fetch all items that are not sold (is_sold is false).
    """
    try:
        # Fetch all items where is_sold is false
        response = supabase.table("items").select("*").eq("is_sold", False).execute()
        if not response.data:
            return jsonify({"success": True, "items": [], "message": "No available items found"}), 200

        return jsonify({"success": True, "items": response.data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@items_api.route("/bids", methods=["POST"])
@restrict_banned_users
def place_bid():
    try:
        # Parse JSON data from the request body
        item_id = request.json.get("item_id")
        user_id = request.json.get("user_id")
        bid_amount = request.json.get("bid_amount")

        # Validate input
        if not item_id or not user_id or not bid_amount:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Check if the item exists
        item_response = supabase.table("items").select("*").eq("id", item_id).execute()
        if not item_response.data:
            return jsonify({"success": False, "error": "Item not found"}), 404

        item = item_response.data[0]

        # Check if the bidding deadline has passed
        current_time = datetime.utcnow()
        if current_time > datetime.fromisoformat(item["deadline"]):
            return jsonify({"success": False, "error": "Bidding period has ended"}), 400

        # Fetch the current highest bid for the item
        highest_bid_response = supabase.table("bids").select("bid_amount").eq("item_id", item_id).order("bid_amount", desc=True).limit(1).execute()

        # Determine the minimum acceptable bid amount
        highest_bid_amount = item["starting_price"]  # Default to starting price
        if highest_bid_response.data:
            highest_bid_amount = highest_bid_response.data[0]["bid_amount"]

        # Validate the bid amount
        if bid_amount <= highest_bid_amount:
            return jsonify({"success": False, "error": "Bid amount must be higher than the current highest bid"}), 400

        # Insert the bid into the database
        bid_response = supabase.table("bids").insert({
            "item_id": item_id,
            "user_id": user_id,
            "bid_amount": bid_amount
        }).execute()

        # Update the item's current price with the new bid amount
        supabase.table("items").update({"current_price": bid_amount}).eq("id", item_id).execute()

        return jsonify({"success": True, "bid": bid_response.data[0]}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@items_api.route("/transactions", methods=["POST"])
@restrict_banned_users
def process_transaction():
    """
    Handles the transaction between a buyer and a seller.
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400

    try:
        data = request.get_json()
        buyer_id = data.get("buyer_id")
        item_id = data.get("item_id")

        if not buyer_id or not item_id:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Fetch item details
        item_response = supabase.table("items").select("*").eq("id", item_id).execute()
        if not item_response.data:
            return jsonify({"success": False, "error": "Item not found"}), 404

        item = item_response.data[0]
        seller_id = item["user_id"]  # Assuming 'user_id' in items references the seller
        agreed_amount = item["current_price"]

        # Check if the item is already sold
        if item["is_sold"]:
            return jsonify({"success": False, "error": "Item is already sold"}), 400

        # Fetch buyer details
        buyer_response = supabase.table("users").select("balance, account_type, id").eq("id", buyer_id).execute()
        if not buyer_response.data:
            return jsonify({"success": False, "error": "Buyer not found"}), 404

        buyer = buyer_response.data[0]
        buyer_balance = buyer["balance"]

        # Apply VIP discount if applicable
        if buyer["account_type"] == "VIP":
            agreed_amount *= 0.9  # 10% discount

        # Check if the buyer has sufficient funds
        if buyer_balance < agreed_amount:
            return jsonify({"success": False, "error": "Insufficient funds"}), 400

        # Fetch seller details
        seller_response = supabase.table("users").select("balance").eq("id", seller_id).execute()
        if not seller_response.data:
            return jsonify({"success": False, "error": "Seller not found"}), 404

        seller_balance = seller_response.data[0]["balance"]

        # Deduct from buyer and credit to seller
        supabase.table("users").update({"balance": buyer_balance - agreed_amount}).eq("id", buyer_id).execute()
        supabase.table("users").update({"balance": seller_balance + agreed_amount}).eq("id", seller_id).execute()

        # Mark item as sold
        supabase.table("items").update({"is_sold": True}).eq("id", item_id).execute()

        # Record transaction
        transaction = {
            "item_id": item_id,
            "seller_id": seller_id,
            "buyer_id": buyer_id,
            "amount": agreed_amount,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("transactions").insert(transaction).execute()

        return jsonify({
            "success": True,
            "message": "Transaction completed successfully",
            "transaction": transaction
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


