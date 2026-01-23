class Likert_scales:
    def __init__(self, client):
        self.supabase_client = client

    '''
    The get_likert_scale_by_questionnaire_id retrieves a likert scale
    by the id of the questionnaire that it belongs to.
    '''
    def get_likert_scale_by_questionnaire_id(self, questionnaire_id: str):
        try:
            return (
                self.supabase_client.
                table("likert_scales").
                select("id").
                eq("questionnaire_id", questionnaire_id)
                .execute()
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to retrieve the questionnaire's likert scale: {e}"
            )

    '''
    The create_likert_scale function creates a likert scale for a questionnaire
    '''
    def create_likert_scale(self, questionnaire_id: str):
        try:
            return (
                self.supabase_client.table("likert_scales").insert({
                    "questionnaire_id": questionnaire_id
                }).execute()
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to create the questionnaire's likert scale: {e}"
            )
