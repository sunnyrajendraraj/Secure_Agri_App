from flask import Flask, request, jsonify, render_template
import sqlite3
from cryptography.fernet import Fernet
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Generate encryption key (Run this ONCE to generate a key)
def generate_key():
    key = Fernet.generate_key()
    with open("encryption_key.key", "wb") as key_file:
        key_file.write(key)

# Uncomment this and run ONCE, then comment it back
# generate_key()

# Load encryption key
def load_key():
    with open("encryption_key.key", "rb") as key_file:
        return key_file.read()

key = load_key()
fernet = Fernet(key)

# Setup SQLite database
def setup_database():
    conn = sqlite3.connect("agriculture_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encrypted_info BLOB
        )
    """)
    conn.commit()
    conn.close()

setup_database()

# Route for homepage
@app.route('/')
def home():
    return render_template('index.html')

# API to encrypt and store data
@app.route('/encrypt', methods=['POST'])
def encrypt_data():
    data = request.json.get('data')  # Get data from frontend
    if not data:
        return jsonify({"error": "No data provided"}), 400

    encrypted_data = fernet.encrypt(data.encode())

    conn = sqlite3.connect("agriculture_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO data (encrypted_info) VALUES (?)", (encrypted_data,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Data encrypted and stored successfully"})

# API to retrieve and decrypt data
@app.route('/decrypt', methods=['GET'])
def decrypt_data():
    conn = sqlite3.connect("agriculture_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT encrypted_info FROM data")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return jsonify({"decrypted_data": []})

    decrypted_data = [fernet.decrypt(row[0]).decode() for row in rows]
    return jsonify({"decrypted_data": decrypted_data})

if __name__ == '__main__':
    app.run(debug=True)
