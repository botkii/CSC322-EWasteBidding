from flask import Blueprint, request, jsonify
from app.utils import upload_image
from app.db import supabase  # Assuming this initializes the Supabase client
from datetime import datetime

items_api = Blueprint("items_api", __name__)

@items_api.route("/items", methods=["POST"])
def create_item():
    try:
        # Parse form data
        user_id = request.form.get("user_id")
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        deadline = request.form.get("deadline")

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
            "starting_price": price,
            "deadline": deadline,
            "image_url": image_url
        }).execute()

        return jsonify({"success": True, "item": response.data[0]}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@items_api.route("/bids", methods=["POST"])
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
