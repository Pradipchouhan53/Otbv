
import os
import bcrypt
import requests
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from dotenv import load_dotenv

# Import custom services
from supabase_db import create_user, get_user_by_email, update_user_verification, update_user_password
from email_service import send_otp_email
from otp_service import generate_otp, store_otp, verify_otp

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "supersecretkey")
jwt = JWTManager(app)

# Telegram Config
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_notification(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram configuration missing.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")

# --- Endpoints ---

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"success": True, "message": "Server is running"}), 200

@app.route('/send-otp', methods=['POST'])
def send_otp_endpoint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
            
        email = data.get('email')
        
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
        
        otp = generate_otp()
        store_otp(email, otp)
        
        # Send via email service
        success = send_otp_email(email, otp)
        
        if success:
            return jsonify({"success": True, "message": "OTP sent successfully"}), 200
        else:
            return jsonify({"success": True, "message": "OTP generated (check console if email failed)"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp_endpoint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
            
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return jsonify({"success": False, "error": "Email and OTP are required"}), 400
        
        is_valid, message = verify_otp(email, otp)
        
        if is_valid:
            # Mark user as verified in DB if they exist
            update_user_verification(email, True)
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400
        
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({"success": False, "error": "User already exists"}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user in Supabase
        user = create_user(email, hashed_password)
        
        if user:
            send_telegram_notification(f"🚀 New User Signup: {email}")
            return jsonify({"success": True, "message": "User created successfully. Please verify your email."}), 201
        else:
            return jsonify({"success": False, "error": "Failed to create user. Check server logs for details."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400
        
        user = get_user_by_email(email)
        
        if not user:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Check if verified
            if not user.get('is_verified', False):
                return jsonify({"success": False, "error": "Please verify your email first"}), 403
                
            access_token = create_access_token(identity=email)
            return jsonify({
                "success": True, 
                "message": "Login successful",
                "access_token": access_token
            }), 200
        else:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
            
        email = data.get('email')
        
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
        
        user = get_user_by_email(email)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        otp = generate_otp()
        store_otp(email, otp)
        
        success = send_otp_email(email, otp)
        
        if success:
            return jsonify({"success": True, "message": "Password reset OTP sent"}), 200
        else:
            return jsonify({"success": True, "message": "OTP generated (check console if email failed)"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
            
        email = data.get('email')
        otp = data.get('otp')
        new_password = data.get('new_password')
        
        if not email or not otp or not new_password:
            return jsonify({"success": False, "error": "Email, OTP, and new password are required"}), 400
        
        is_valid, message = verify_otp(email, otp)
        
        if is_valid:
            # Hash new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update in Supabase
            updated_user = update_user_password(email, hashed_password)
            
            if updated_user:
                send_telegram_notification(f"🔐 Password Reset: {email}")
                return jsonify({"success": True, "message": "Password reset successful"}), 200
            else:
                return jsonify({"success": False, "error": "Failed to update password"}), 500
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
