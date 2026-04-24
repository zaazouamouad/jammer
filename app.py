from flask import Flask, request, jsonify
import json
import os
import secrets

app = Flask(__name__)

# معلومات الدخول
USERNAME = "nexu_oi"
PASSWORD = "nethunter2010kali"

# تخزين التوكنات
tokens = []

# ملف التخزين
DATA_FILE = "data.json"

# إنشاء الملف إذا ما كانش
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# تحميل البيانات
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# حفظ البيانات
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# تسجيل الدخول
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get("username") == USERNAME and data.get("password") == PASSWORD:
        token = secrets.token_hex(16)
        tokens.append(token)
        return jsonify({"status": "success", "token": token})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# التحقق من التوكن
def is_auth(req):
    token = req.headers.get("Authorization")
    return token in tokens

# إضافة بيانات
@app.route('/add', methods=['POST'])
def add_data():
    if not is_auth(request):
        return jsonify({"error": "Unauthorized"}), 403

    data = load_data()
    new_item = request.json
    data.append(new_item)
    save_data(data)
    return jsonify({"status": "saved", "data": new_item})

# جلب البيانات
@app.route('/data', methods=['GET'])
def get_data():
    if not is_auth(request):
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(load_data())

# حذف البيانات
@app.route('/delete', methods=['POST'])
def delete_data():
    if not is_auth(request):
        return jsonify({"error": "Unauthorized"}), 403

    index = request.json.get("index")
    data = load_data()

    if 0 <= index < len(data):
        removed = data.pop(index)
        save_data(data)
        return jsonify({"deleted": removed})

    return jsonify({"error": "Invalid index"}), 400

app.run(host='0.0.0.0', port=5000)
