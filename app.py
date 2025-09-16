from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
import urllib.parse

app = Flask(__name__)

# Read mongo connection pieces from environment
MONGO_USER = os.environ.get("MONGO_USER", "")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "")
MONGO_HOST = os.environ.get("MONGO_HOST", "mongo")
MONGO_PORT = os.environ.get("MONGO_PORT", "27017")
MONGO_DB = os.environ.get("MONGO_DB", "flask_db")
MONGO_AUTH_SOURCE = os.environ.get("MONGO_AUTH_SOURCE", "admin")

# Build a proper MongoDB URI with URL-encoding for username/password
if MONGO_USER and MONGO_PASSWORD:
    user_enc = urllib.parse.quote_plus(MONGO_USER)
    pwd_enc = urllib.parse.quote_plus(MONGO_PASSWORD)
    MONGODB_URI = f"mongodb://{user_enc}:{pwd_enc}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource={MONGO_AUTH_SOURCE}"
else:
    # fallback to unauthenticated (local development)
    MONGODB_URI = os.environ.get("MONGODB_URI", f"mongodb://{MONGO_HOST}:{MONGO_PORT}/")

client = MongoClient(MONGODB_URI)
db = client[MONGO_DB]
collection = db.data

@app.route('/')
def index():
    return f"Welcome to the Flask app! The current time is: {datetime.now()}"

@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        payload = request.get_json(force=True, silent=True)
        if not payload:
            return jsonify({"error": "JSON body required"}), 400
        collection.insert_one(payload)
        return jsonify({"status": "Data inserted"}), 201
    else:  # GET
        items = list(collection.find({}, {"_id": 0}))
        return jsonify(items), 200

if __name__ == '__main__':
    # Use 0.0.0.0 to be reachable from container/pod network
    app.run(host='0.0.0.0', port=5000)
