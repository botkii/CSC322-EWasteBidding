from werkzeug.utils import secure_filename  # To secure the filename
import os  # For environment variables
from supabase import create_client  # To interact with Supabase storage

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Retrieve Supabase URL from .env
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Retrieve Supabase Key from .env
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)  # Create Supabase client

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

        # Debug: Print the response to inspect its structure
        print(response)

        # Check if the upload was successful
        if hasattr(response, "error") and response.error:
            raise Exception(f"Error uploading image: {response.error['message']}")

        # Get the public URL of the uploaded image
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        return {"success": True, "url": public_url}
    except Exception as e:
        return {"success": False, "error": str(e)}