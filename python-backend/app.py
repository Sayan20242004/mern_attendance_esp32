from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
import base64
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)


client = MongoClient(os.getenv("MONGO_URI"))
db = client["sample-db"]
users_col = db["users"]


def generate_vector(img):
    resized = cv2.resize(img, (100, 100))   
    vector = resized.flatten() / 255.0      
    return vector
def cosine_similarity(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0

    return np.dot(a, b) / (norm_a * norm_b)

@app.route("/register-face", methods=["POST"])
def register_face():
    data = request.json
    image = data.get("image")
    user_id = data.get("userId")

    if not image or not user_id:
        return jsonify({"message": "Missing data"}), 400

    try:
        img_data = base64.b64decode(image)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"message": "Invalid image"}), 400

        vector = generate_vector(img)

        return jsonify({
            "message": "Face registered",
            "vector": vector.tolist()
        })

    except Exception as e:
        print("REGISTER ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/recognize", methods=["POST"])
def recognize():
    try:
        
        img_data = request.data
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"message": "Invalid image"}), 400

        vector = generate_vector(img)

        print("Vector shape:", vector.shape)

        users = list(users_col.find({"vector": {"$exists": True}}))
        print("Users count:", len(users))

        best_match = None
        best_score = -1

        for user in users:
            
            if "vector" not in user or len(user["vector"]) == 0:
                continue

            db_vector = np.array(user["vector"])

            
            if db_vector.shape != vector.shape:
                print("Skipping user due to shape mismatch")
                continue

            score = cosine_similarity(db_vector, vector)

            if score > best_score:
                best_score = score
                best_match = user

        
        if best_match and best_score > 0.75:
            return jsonify({
                "userId": str(best_match["_id"]),
                "message": "Match found",
                "score": float(best_score)
            })

        return jsonify({
            "message": "No match",
            "score": float(best_score)
        })

    except Exception as e:
        print(" RECOGNIZE ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
