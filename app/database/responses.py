class Responses:
    def __init__(self, client):
        self.supabase_client = client

    """
    The get_user_responses_by_id function gets all the responses that their user_id 
    matches the parameter user_id (for users)
    """
    def get_user_responses_by_id(self, user_id: str):
        try:
            return self.supabase_client.table("responses").select("questionnaires(*), id, submitted_at, is_submitted").
                        eq("user_id", user_id).order("is_submitted", desc=True).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve questionnaires: {e}")

    def get_user_drafts_by_questionnaire_id(self, user_id: str, questionnaire_id: str):
        
        