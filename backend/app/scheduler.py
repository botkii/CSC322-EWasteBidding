# scheduler.py
from flask_apscheduler import APScheduler
import logging
from app.api.users import check_user_suspensions
from app.db import supabase

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def init_scheduler(app):
    """
    Initialize scheduler with the Flask app
    """
    scheduler = APScheduler()
    scheduler.init_app(app)
    
    # Explicitly define jobs
    scheduler.add_job(
        id='suspend_check',
        func=check_and_suspend_users,
        trigger='interval',
        minutes=10
    )
    
    scheduler.add_job(
        id='ban_check', 
        func=automatic_ban_users,
        trigger='interval', 
        minutes=10
    )
    
    scheduler.start()

def check_and_suspend_users():
    """
    Run the user suspension check with application context.
    """
    from flask import current_app
    logging.debug("Starting the check_and_suspend_users job.")
    try:
        # Call the suspension function
        response = check_user_suspensions()
        logging.info(f"Suspension check completed successfully: {response.get_json()}")
    except Exception as e:
        logging.error(f"Error in check_and_suspend_users: {e}")

def automatic_ban_users():
    """
    Automatically ban users with a suspension count of 3 or more.
    """
    logging.debug("Starting the automatic_ban_users job.")
    try:
        # Fetch users with suspension_count >= 3 and not already banned
        users_response = supabase.table("users").select("id, suspension_count, banned").execute()
        logging.info(f"Fetched {len(users_response.data)} users for evaluation.")
        
        if not users_response.data:
            logging.info("No users to evaluate for banning.")
            return

        for user in users_response.data:
            if user["suspension_count"] >= 3 and not user.get("banned", False):
                # Ban the user
                supabase.table("users").update({"banned": True}).eq("id", user["id"]).execute()
                logging.info(f"User with ID {user['id']} has been automatically banned.")

    except Exception as e:
        logging.error(f"Error during automatic ban process: {e}")