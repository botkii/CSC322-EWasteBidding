from flask import Blueprint, request, jsonify
from app.utils import upload_image
from app.db import supabase  # Assuming this initializes the Supabase client

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
