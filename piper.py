from flask import Flask, request, jsonify, send_file
import subprocess
import os
from datetime import datetime

app = Flask(__name__)

def log(message):
    """Helper function to print messages with timestamps."""
    print(f"{datetime.now()}: {message}")

@app.route('/api/piper', methods=['POST'])
def piper_tts():
    """
    API endpoint to receive text and convert it to speech using Piper.
    """
    try:
        # Get JSON data from the request
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Invalid request, 'text' field is required."}), 400
        
        text = data['text']
        log(f"Text to convert: {text}")

        # Define Piper parameters
        model = os.getenv("PIPER_MODEL", "ne_NP-google-medium")
        speaker = os.getenv("PIPER_SPEAKER", "6")
        output_file = os.getenv("PIPER_OUTPUT", "welcome.wav")

        # Construct the Piper command
        command = [
            "piper",
            "--model", model,
            "--speaker", speaker,
            "--output_file", output_file
        ]

        log(f"Running Piper command with model: {model}, speaker: {speaker}, output file: {output_file}")

        # Execute the Piper command
        process = subprocess.run(
            command, input=text, text=True, capture_output=True
        )

        # Handle success or failure
        if process.returncode == 0:
            log("Command executed successfully.")
            if os.path.exists(output_file):
                log(f"Audio file generated successfully: {output_file}")
                
                # Send the audio file as a response
                return send_file(
                    output_file,
                    as_attachment=True,
                    download_name="speech.wav",
                    mimetype="audio/wav"
                )
            else:
                log("Error: Audio file was not created.")
                return jsonify({"error": "Audio file was not created."}), 500
        else:
            log(f"Error executing command. Return code: {process.returncode}")
            log(f"stderr: {process.stderr}")
            return jsonify({"error": "Error executing Piper command.", "details": process.stderr}), 500

    except Exception as e:
        log(f"An error occurred: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
