class Profiles:
    def __init__(self, client):
        self.supabase_client = client

    """
    The get_all_profiles function returns all the profiles from database's profiles table 
    except the one that belongs to the user that calls it(for admins)
    """
    def get_all_profiles(self, user_id: str):
        try:
            return self.supabase_client.table("profiles").select("*").neq("id", user_id).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve profiles: {e}")

    """
    The get_profile_by_id function returns the profile that its user_id matches the parameter user_id (for user)
    """
    def get_profile_by_id(self, user_id: str):
        try:
            return self.supabase_client.table("profiles").select("*").eq("id", user_id).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve profile: {e}")

    def get_profile_by_user_name(self, username: str):
        try:
            return self.supabase_client.table("profiles").select("*").eq("name", username).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve profile: {e}")

    """
    The create_profile function inserts a new row on the database's profiles table (for users)
    """
    def create_profile(self, user_id: str, full_name: str, birth_date: str, city: str, country: str):
        try:
            return self.supabase_client.table("profiles").insert({
                                "id": user_id,
                                "full_name": full_name,
                                "birthdate": birth_date,
                                "city": city,
                                "country": country,
                            }).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to create profile: {e}")

    """
    The update_profile function updates the profile that its id matches the profile_id (for admins)
    """
    def update_profile_by_id(self, user_id: str, new_full_name: str, new_birth_date: str, new_city: str, new_country: str
        , old_full_name: str, old_birth_date: str, old_city: str, old_country: str):
        try:
            return self.supabase_client.table("profiles").update({
                            "id": user_id,
                            "full_name": new_full_name if new_full_name else old_full_name,
                            "birthdate": new_birth_date if new_birth_date else old_birth_date,
                            "city": new_city if new_city else old_city,
                            "country": new_country if new_country else old_country,
            }).eq("id", user_id).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to update profile: {e}")
    
    """
    The delete_profile_by_id function deletes the profile that its id matches the profile_id (for users)
    """
    def delete_profile_by_id(self, profile_id: str):
        try:
            return self.supabase_client.table("profiles").delete().eq("id", profile_id).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to delete profile: {e}")

