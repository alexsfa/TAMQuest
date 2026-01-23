
class Questionnaires:
    def __init__(self, client):
        self.supabase_client = client

    """
    The get_all_questionnaires function returns all the questionnaires
    from the admin's responses on those questionnaires (for admins)
    """
    def get_all_questionnaires(self):
        try:
            return (
                self.supabase_client
                .table("questionnaires")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve questionnaires: {e}")

    """
    The get_all_questionnaires_wit_admin_response function returns
    all the questionnaires from the admin's responses
    on those questionnaires (for admins)
    """
    def get_all_questionnaires_with_admin_response(self, user_id: str):
        try:
            return (
                self.supabase_client.table("questionnaires").select(
                    """
                    *,
                    responses!left(
                        id,
                        user_id,
                        questionnaire_id,
                        is_submitted
                    )
                    """
                ).eq("responses.user_id", user_id).
                eq("responses.is_submitted", True).
                order("created_at", desc=True).
                execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve questionnaires: {e}")

    """
    The get_questionnaire_by_id function returns a questionnaire
    by its own id (for users)
    """
    def get_questionnaire_by_id(self, questionnaire_id: str):
        try:
            return (
                self.supabase_client.
                table("questionnaires").
                select("id, title, details, created_at")
                .eq("id", questionnaire_id)
                .execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve questionnaire: {e}")

    """
    The questionnaire_without_user_response function returns
    the questionnaires that the logged in user has not responded (for users)
    """
    def get_questionnaires_without_user_response(self, user_id: str):
        # Calls the Postgres RPC function.
        try:
            return (
                self.supabase_client.
                rpc(
                    "questionnaires_without_user_response",
                    {"uid": user_id})
                .execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve questionnaires: {e}")

    """
    The create_questionnaire function inserts a new questionnaire
    in the database's questionnaire table (for admins)
    """
    def create_questionnaire(
        self,
        app_name: str,
        questionnaire_details: str,
        user_id: str
    ):
        try:
            return self.supabase_client.table("questionnaires").insert({
                        "title": f"{app_name} TAM Questionnaire",
                        "details": questionnaire_details,
                        "created_by": user_id
                    }).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to create questionnaire: {e}")

    """
    The delete_questionnaire_by_id function deletes a questionnaire
    from the database's questionnaire table (for admins)
    """
    def delete_questionnaire_by_id(self, questionnaire_id: str):
        try:
            return (
                self.supabase_client.
                table("questionnaires")
                .delete()
                .eq("id", questionnaire_id)
                .execute())
        except Exception as e:
            raise RuntimeError(f"Failed to delete questionnaire: {e}")
