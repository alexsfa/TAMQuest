class Likert_scales:
    def __init__(self, client):
        self.supabase_client = client

    def get_likert_scale_by_questionnaire_id(self, questionnaire_id:str):
        try:
            return (
                self.supabase_client.table("likert_scales").select("id").eq("questionnaire_id", questionnaire_id).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve the questionnaire's likert scale: {e}")

    def create_likert_scale(self, questionnaire_id:str):
        try:
            return (
                self.supabase_client.table("likert_scales").insert({
                    "questionnaire_id": questionnaire_id
                }).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create the questionnaire's likert scale: {e}")