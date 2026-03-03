
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")
    supabase = None
else:
    supabase: Client = create_client(url, key)

def create_user(email, hashed_password):
    if not supabase:
        print("Supabase client not initialized.")
        return None
    try:
        response = supabase.table("users").insert({
            "email": email,
            "password": hashed_password,
            "is_verified": False
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_user_by_email(email):
    if not supabase:
        print("Supabase client not initialized.")
        return None
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def update_user_verification(email, is_verified):
    if not supabase:
        print("Supabase client not initialized.")
        return None
    try:
        response = supabase.table("users").update({
            "is_verified": is_verified
        }).eq("email", email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating verification: {e}")
        return None

def update_user_password(email, hashed_password):
    if not supabase:
        print("Supabase client not initialized.")
        return None
    try:
        response = supabase.table("users").update({
            "password": hashed_password
        }).eq("email", email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating password: {e}")
        return None
