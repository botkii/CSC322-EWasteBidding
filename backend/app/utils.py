from werkzeug.utils import secure_filename   
from app.db import supabase  

def upload_image(file, bucket_name="item-images"):
    try:
        # Secure the file name
        filename = secure_filename(file.filename)
        file_path = f"images/{filename}"

        # Check if the file already exists and delete it
        existing_file = supabase.storage.from_(bucket_name).get_public_url(file_path)
        if existing_file:
            supabase.storage.from_(bucket_name).remove([file_path])

        # Read the file's binary content
        file_content = file.read()

        # Upload the file to Supabase Storage
        response = supabase.storage.from_(bucket_name).upload(file_path, file_content)

        # Check if the upload was successful
        if hasattr(response, "error") and response.error:
            raise Exception(f"Error uploading image: {response.error['message']}")

        # Get the public URL of the uploaded image
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        return {"success": True, "url": public_url}
    except Exception as e:
        return {"success": False, "error": str(e)}

def perform_user_suspensions():
    """
    Core suspension logic without Flask routing
    """
    try:
        users_response = supabase.table("users").select("id, rating, rating_count, suspension_status, suspension_count, account_type").execute()
        if not users_response.data:
            return False

        for user in users_response.data:
            user_id = user["id"]
            rating = user["rating"]
            rating_count = user["rating_count"]
            suspension_status = user["suspension_status"] 
            suspension_count = user.get("suspension_count", 0)  # Get current count, default to 0
            account_type = user["account_type"]

            if suspension_status:
                continue

            if rating_count >= 3 and (rating < 2 or rating > 4):
                if account_type == "VIP":
                    # VIP gets demoted to regular User instead of being suspended
                    supabase.table("users").update({
                        "account_type": "User"
                    }).eq("id", user_id).execute()
                else:
                    # Regular users get suspended and suspension count increased
                    supabase.table("users").update({
                        "suspension_status": True,
                        "suspension_count": suspension_count + 1
                    }).eq("id", user_id).execute()

        return True
    except Exception as e:
        print(f"Error in perform_user_suspensions: {e}")
        return False