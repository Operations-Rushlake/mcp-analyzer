from flask import Flask, request, jsonify
from tubi_checker import check_tubi_streaming

app = Flask(__name__)

@app.route("/check_tubi", methods=["POST"])
def mcp_check_tubi():
    data = request.json
    result = check_tubi_streaming(
        tubi_url=data['tubi_url'],
        territory=data.get('territory', 'United States')
    )
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=3333)
