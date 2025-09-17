import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from k8s_helper import ask_k8s_bot

# Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Flask app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(__name__)

@app.route("/")
def home():
    logger.debug("Serving index.html")
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/style.css")
def css():
    logger.debug("Serving style.css")
    return send_from_directory(FRONTEND_DIR, "style.css")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    logger.debug(f"Received request: {data}")
    question = data.get("question", "")
    if not question:
        return jsonify({"answer": "⚠️ No question provided"}), 400

    answer = ask_k8s_bot(question)
    logger.debug(f"Returning answer: {answer}")
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

