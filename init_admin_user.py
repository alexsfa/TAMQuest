from dotenv import load_dotenv
from supabase_auth import SyncGoTrueAdminAPI
from supabase import create_client, Client
import os
import sys

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SERVICE_ROLE_KEY")
ADMIN_EMAIL = os.getenv("APP_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("APP_ADMIN_PASSWORD")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
admin = supabase.auth.admin

def ensure_admin_exists(admin):

    response = admin.list_users()
    for u in response:
        print(u)

    admin_exists = any(u.get("email") == ADMIN_EMAIL for u in response if isinstance(u, dict))

    if admin_exists:
        print(f"Admin user '{ADMIN_EMAIL}' already exists.")
        return

    print(f"Creating admin user '{ADMIN_EMAIL}'...")
    response = admin.create_user(
        {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "email_confirm": True,
            "app_metadata": {"role": "admin"},
        }
    )

    if response:
        print(f"Admin user created: {response.user.email}")
        sys.exit(0)
    else:
        print(f"⚠️ Failed to create admin user: {response}")
        sys.exit(1)

if __name__ == "__main__":
    ensure_admin_exists(admin)