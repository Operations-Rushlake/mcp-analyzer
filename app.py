# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    """
    This function handles requests to the root URL (/).
    It's a simple test to confirm your server is running.
    """
    return 'Hello, this is your MCP server! It is running correctly.'

if __name__ == '__main__':
    # This block runs the server only when you execute this file directly.
    # debug=True allows for automatic reloading when you make changes.
    app.run(debug=True, port=8000)