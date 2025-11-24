import os
import sys
from supabase_auth import SyncGoTrueAdminAPI

GOTRUE_URL = os.getenv("GOTRUE_URL", "http://auth:8081")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SERVICE_ROLE_KEY")
ADMIN_EMAIL = os.getenv("APP_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("APP_ADMIN_PASSWORD")

if not GOTRUE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Missing GOTRUE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables.")

def ensure_admin_exists():
    admin = SyncGoTrueAdminAPI(url=GOTRUE_URL, headers={"Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"})

    users = admin.list_users()
    admin_exists = any(u["email"] == ADMIN_EMAIL for u in users)

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

def create_admin(user_id: str):
    response = admin.update_user_by_id(
        user_id,
        {"app_metadata": {"role": "admin"}}
    )
    return response

if __name__ == "__main__":
    ensure_admin_exists()