from app import create_app
from app.scheduler import init_scheduler

app = create_app()

# Print all available routes
print("Available routes:")
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == "__main__":
    # Initialize the scheduler
    init_scheduler(app)
    
    # Run the app
    app.run(debug=True)