# app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

# This route is for a simple GET request to verify the server is running.
@app.route('/')
def home():
    return 'Hello, this is your MCP server! It is running correctly.'

# This route is for a POST request from your check_tubi_sheet.py script.
@app.route('/check_tubi', methods=['POST'])
def check_tubi_availability():
    # The script should send a POST request to this URL.
    
    # Check if the request is a JSON object.
    if request.is_json:
        payload = request.get_json()
        tubi_url = payload.get("tubi_url")
        territory = payload.get("territory")
        
        # --- YOUR ANALYSIS LOGIC GOES HERE ---
        # For now, we'll return a placeholder success message.
        # This is where your code to check the Tubi link would go.
        # You would use the tubi_url and territory variables.
        
        # We will assume it's available for now to confirm the connection works.
        is_available = True

        return jsonify({
            "status": "success",
            "available": is_available,
            "message": f"Successfully processed request for {tubi_url} in {territory}"
        }), 200
    else:
        # If the request is not JSON, return an error.
        return jsonify({
            "status": "error",
            "message": "Invalid request: Expected JSON payload."
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=8000)