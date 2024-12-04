from werkzeug.utils import secure_filename  
import os  
from supabase import create_client  

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")  
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)  

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
