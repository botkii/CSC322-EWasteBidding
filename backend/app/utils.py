#Utility/helper functions
import os
from supabase import create_client
from werkzeug.utils import secure_filename

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_image(file, bucket_name="item-images"):
    """
    Upload an image to the Supabase storage bucket and return its public URL.
    :param file: File object (from Flask's request.files)
    :param bucket_name: Name of the Supabase storage bucket
    :return: Public URL of the uploaded image
    """
    try:
        # Secure the file name
        filename = secure_filename(file.filename)

        # Path in the bucket where the image will be stored
        file_path = f"images/{filename}"

        # Upload file to Supabase Storage
        response = supabase.storage.from_(bucket_name).upload(file_path, file)

        if response.get("error"):
            raise Exception(f"Error uploading image: {response['error']}")

        # Get the public URL of the uploaded image
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        return {"success": True, "url": public_url}
    except Exception as e:
        return {"success": False, "error": str(e)}
