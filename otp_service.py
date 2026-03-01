import random
import time

# In-memory storage for OTPs: {email: {"otp": "123456", "expiry": timestamp}}
otp_store = {}

def generate_otp():
    return str(random.randint(100000, 999999))

def store_otp(email, otp):
    # Expiry set to 10 minutes (600 seconds)
    expiry = time.time() + 600
    otp_store[email] = {"otp": otp, "expiry": expiry}

def verify_otp(email, otp):
    if email not in otp_store:
        return False, "OTP not found for this email."
    
    stored_data = otp_store[email]
    if time.time() > stored_data["expiry"]:
        del otp_store[email]
        return False, "OTP has expired."
    
    if stored_data["otp"] == otp:
        del otp_store[email]
        return True, "OTP verified successfully."
    
    return False, "Invalid OTP."
