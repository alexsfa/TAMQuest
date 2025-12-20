class Likert_scales:
    def __init__(self, client):
        self.supabase_client = client

    def create_likert_scale(self, questionnaire_id:str):
        try:
            return (
                self.supabase_client.table("likert_scales").insert({
                    "questionnaire_id": questionnaire_id
                }).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to insert the questionnaire's likert scales: {e}")