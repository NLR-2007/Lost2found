from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import re
from api.db import get_db_connection
import json
import random
import requests
import os

otp_store = {}

def send_telegram_message(message):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            res = requests.post(url, json={"chat_id": chat_id, "text": message})
            print(f"DEBUG: Telegram API response: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"DEBUG: Failed to send Telegram message: {str(e)}")
    elif token:
        print(f"DEBUG: Telegram token exists but TELEGRAM_CHAT_ID is missing in .env!")

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing request body"}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"message": "Name, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        return jsonify({"message": "Invalid email format"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"message": "Email is already taken"}), 400

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, 'user')
        )
        conn.commit()
        return jsonify({"message": "Registration successful"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing request body"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, name, password, role FROM users WHERE email = %s AND role = 'user'", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            import json
            access_token = create_access_token(identity=json.dumps({'id': user['id'], 'name': user['name'], 'role': user['role']}))
            return jsonify({
                "message": "Login successful",
                "token": access_token,
                "user": {"id": user['id'], "name": user['name'], "role": user['role']}
            }), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/request-otp', methods=['POST'])
def request_otp():
    from werkzeug.security import check_password_hash
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Allow ANY admin in the DB to request OTP (not just hardcoded email)
        cursor.execute("SELECT id, password FROM users WHERE LOWER(email) = LOWER(%s) AND role = 'admin'", (email,))
        admin = cursor.fetchone()
        
        if not admin or not check_password_hash(admin['password'], password):
            return jsonify({"message": "Invalid admin credentials"}), 401
            
        otp = str(random.randint(100000, 999999))
        otp_store[email.lower()] = otp
        
        # Send via telegram (same chat ID for all admins)
        otp_msg = f"Lost2Found Admin OTP\n\nEmail: {email}\nCode: {otp}\n\nBlack Panthers 2.o Powered by NLR GROUP OF COMPANY"
        send_telegram_message(otp_msg)
        
        # Also print it for debugging if Telegram fails
        print(f"DEBUG: Admin OTP for {email}: {otp} (in case Telegram fails)")
        
        return jsonify({"message": "OTP sent to your Telegram successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing request body"}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    otp = data.get('otp')
    if otp is not None:
        otp = str(otp).strip()
    
    # Check OTP matches (stored with lowercase key)
    stored_otp = otp_store.get(email.lower())
    
    if not stored_otp or str(stored_otp).strip() != otp:
        return jsonify({"message": "Invalid or expired OTP"}), 401

    # No hardcoded email check — ANY admin in DB can login after OTP validation
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, name, password, role FROM users WHERE LOWER(email) = LOWER(%s) AND role = 'admin'", (email,))
        admin = cursor.fetchone()

        if admin and check_password_hash(admin['password'], password):
            import json
            access_token = create_access_token(identity=json.dumps({'id': admin['id'], 'name': admin['name'], 'role': admin['role']}))
            # Clear the OTP only after SUCCESSFUL login
            otp_store.pop(email.lower(), None)
            return jsonify({
                "message": "Admin login successful",
                "token": access_token,
                "user": {"id": admin['id'], "name": admin['name'], "role": admin['role']}
            }), 200
        else:
            return jsonify({"message": "Invalid admin credentials"}), 401
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
