from flaskr import create_app

# Create the application instance using the factory function
app = create_app()

if __name__ == "__main__":
    # Run the development server
    # debug=True enables auto-reloading and debugger
    # Use a proper WSGI server for production!
    app.run(debug=True, host="0.0.0.0", port=5000)
