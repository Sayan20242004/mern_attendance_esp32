from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
import base64
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# ✅ MongoDB connection
client = MongoClient("mongodb+srv://sayankunndu2004:mbiSThCUwZfSHOxQ@cluster0.r1dbzex.mongodb.net/sample-db?retryWrites=true&w=majority&appName=Cluster0")
db = client["sample-db"]
users_col = db["users"]

# =========================
# ✅ VECTOR GENERATION
# =========================
def generate_vector(img):
    resized = cv2.resize(img, (100, 100))   # 100x100
    vector = resized.flatten() / 255.0      # normalize
    return vector

# =========================
# ✅ COSINE SIMILARITY (SAFE)
# =========================
def cosine_similarity(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0

    return np.dot(a, b) / (norm_a * norm_b)

# =========================
# ✅ REGISTER (FRONTEND)
# =========================
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


# =========================
# ✅ RECOGNIZE (ESP32)
# =========================
@app.route("/recognize", methods=["POST"])
def recognize():
    try:
        # 🔥 RAW image from ESP32
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
            # ✅ Skip invalid users
            if "vector" not in user or len(user["vector"]) == 0:
                continue

            db_vector = np.array(user["vector"])

            # ✅ Shape check
            if db_vector.shape != vector.shape:
                print("Skipping user due to shape mismatch")
                continue

            score = cosine_similarity(db_vector, vector)

            if score > best_score:
                best_score = score
                best_match = user

        # 🔴 THRESHOLD (tune this if needed)
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
        print("🔥 RECOGNIZE ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# =========================
# ✅ RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)