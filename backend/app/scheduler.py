from flask_apscheduler import APScheduler
import logging
from app.db import supabase
from app.utils import perform_user_suspensions

# Configure logging to show only INFO and ERROR messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def init_scheduler(app):
    """
    Initialize scheduler with the Flask app
    """
    scheduler = APScheduler()
    scheduler.init_app(app)
    
    # Create wrapper functions that include app context
    def run_suspend_check():
        with app.app_context():
            check_and_suspend_users()
            
    def run_ban_check():
        with app.app_context():
            automatic_ban_users()
    
    scheduler.add_job(
        id='suspend_check',
        func=run_suspend_check,
        trigger='interval',
        minutes=5
    )
    
    scheduler.add_job(
        id='ban_check', 
        func=run_ban_check,
        trigger='interval',
        minutes=5
    )
    
    scheduler.start()

def check_and_suspend_users():
    """
    Run the user suspension check with application context.
    """
    try:
        if perform_user_suspensions():
            logging.info("Suspension check completed successfully")
        else:
            logging.info("No users to evaluate for suspension")
    except Exception as e:
        logging.error(f"Error in check_and_suspend_users: {e}")

def automatic_ban_users():
    """
    Automatically ban users with a suspension count of 3 or more.
    """
    try:
        users_response = supabase.table("users").select("id, suspension_count, banned").execute()
        
        if not users_response.data:
            return

        for user in users_response.data:
            if user["suspension_count"] >= 3 and not user.get("banned", False):
                supabase.table("users").update({"banned": True}).eq("id", user["id"]).execute()
                logging.info(f"User {user['id']} has been banned")

    except Exception as e:
        logging.error(f"Error during automatic ban process: {e}")