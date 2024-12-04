from app import create_app

app = create_app()

# Print all available routes
print("Available routes:")
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == "__main__":
    app.run(debug=True)

