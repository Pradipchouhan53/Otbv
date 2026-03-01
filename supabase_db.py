import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def create_user(email, hashed_password):
    try:
        data, count = supabase.table("users").insert({
            "email": email,
            "password": hashed_password,
            "is_verified": False
        }).execute()
        return data[1][0] if data[1] else None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_user_by_email(email):
    try:
        data, count = supabase.table("users").select("*").eq("email", email).execute()
        return data[1][0] if data[1] else None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def update_user_verification(email, is_verified):
    try:
        data, count = supabase.table("users").update({
            "is_verified": is_verified
        }).eq("email", email).execute()
        return data[1][0] if data[1] else None
    except Exception as e:
        print(f"Error updating verification: {e}")
        return None

def update_user_password(email, hashed_password):
    try:
        data, count = supabase.table("users").update({
            "password": hashed_password
        }).eq("email", email).execute()
        return data[1][0] if data[1] else None
    except Exception as e:
        print(f"Error updating password: {e}")
        return None
