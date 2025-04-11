# run.py
"""
Development server startup script.
Creates the Flask app using the factory and runs the development server.
Do NOT use this for production deployments. Use a WSGI server like Gunicorn or Waitress.
"""
from flaskr import create_app  # Import the factory function from our package

# Create the application instance by calling the factory function
app = create_app()

if __name__ == "__main__":
    # Run the Flask development server
    # debug=True: enables debugger and automatic reloading on code changes
    # host='0.0.0.0': makes the server accessible externally (e.g., within your local network)
    # port=5000: standard Flask development port
    app.run(debug=True, host="0.0.0.0", port=5000)
