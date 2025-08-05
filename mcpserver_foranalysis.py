from flask import Flask, request, jsonify
from tika import parser
from flask_cors import CORS
import os
import tempfile

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({'error': 'No file uploaded'}), 400

    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        uploaded_file.save(temp.name)
        parsed = parser.from_file(temp.name)
        os.unlink(temp.name)

    content = parsed.get("content", "")
    metadata = parsed.get("metadata", {})

    # Simulate initial analysis questions
    response = {
        "status": "analysis_started",
        "text_preview": content[:300],
        "metadata": metadata,
        "questions": [
            "Do you want a summary or a table?",
            "Would you like to extract amounts, dates, or names?",
            "Is this document an invoice, contract, or something else?"
        ]
    }

    return jsonify(response)


@app.route('/followup', methods=['POST'])
def followup():
    data = request.json
    user_choice = data.get("user_choice", "").lower()

    # Simulated intelligent response
    if "summary" in user_choice:
        return jsonify({
            "result_type": "summary",
            "summary": "This document seems to contain financial data and invoice references. Summary complete."
        })

    elif "table" in user_choice:
        return jsonify({
            "result_type": "table",
            "headers": ["Item", "Amount", "Date"],
            "rows": [
                ["Consulting Fee", "$1,500", "2025-08-01"],
                ["Hosting", "$200", "2025-08-02"]
            ]
        })

    else:
        return jsonify({
            "result_type": "note",
            "message": "Sorry, I couldn't understand your input. Please be specific."
        })


if __name__ == '__main__':
    app.run(port=5001)
